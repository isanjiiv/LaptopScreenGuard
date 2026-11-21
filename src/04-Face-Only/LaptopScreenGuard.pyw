"""Face-only screen privacy with live, local enrollment preview."""
import ctypes
import hashlib
import hmac
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import threading
import time

from PySide6 import QtCore, QtGui, QtWidgets

BASE = Path(__file__).resolve().parent
logging.basicConfig(
    handlers=[RotatingFileHandler(BASE / "LaptopScreenGuard.log", maxBytes=250_000, backupCount=1)],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
CAMERA_INDEX = 0
class Detector(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.stop = threading.Event()
        self.latest_frame = None
        self.status = "Opening webcam"

    def run(self):
        try:
            import cv2

            while not self.stop.is_set():
                capture = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
                try:
                    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    while capture.isOpened() and not self.stop.is_set():
                        ok, frame = capture.read()
                        if not ok or frame is None or not frame.size:
                            break
                        self.latest_frame = (time.monotonic(), frame)
                        self.status = "Webcam active"
                        self.stop.wait(0.03)
                finally:
                    self.latest_frame = None
                    capture.release()
                self.status = "Webcam unavailable; retrying"
                self.stop.wait(1)
        except Exception:
            self.latest_frame = None
            self.status = "Webcam error. See LaptopScreenGuard.log."
            logging.exception("Webcam capture stopped")


class InputGuard:
    """Suppress desktop input only while an overlay is visible."""

    def __init__(self):
        self.user = ctypes.WinDLL("user32", use_last_error=True)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        callback = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t, ctypes.c_int, ctypes.c_size_t, ctypes.c_void_p
        )
        self.user.SetWindowsHookExW.argtypes = (
            ctypes.c_int, callback, ctypes.c_void_p, ctypes.c_uint32
        )
        self.user.SetWindowsHookExW.restype = ctypes.c_void_p
        self.user.UnhookWindowsHookEx.argtypes = (ctypes.c_void_p,)
        self.user.UnhookWindowsHookEx.restype = ctypes.c_int
        self.user.CallNextHookEx.argtypes = (
            ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_void_p
        )
        self.user.CallNextHookEx.restype = ctypes.c_ssize_t
        kernel.GetModuleHandleW.argtypes = (ctypes.c_wchar_p,)
        kernel.GetModuleHandleW.restype = ctypes.c_void_p
        self.module = kernel.GetModuleHandleW(None)
        self.keyboard_callback = callback(self.keyboard_event)
        self.mouse_callback = callback(self.mouse_event)
        self.handles = []
        self.keys = set()
        self.pause_requested = False

    def keyboard_event(self, code, message, data):
        if code != 0:
            return self.user.CallNextHookEx(None, code, message, data)
        key = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint32)).contents.value
        if message in (0x100, 0x104):
            first_press = key not in self.keys
            self.keys.add(key)
            if (first_press and key == 0x7B
                    and self.keys.intersection((0x11, 0xA2, 0xA3))
                    and self.keys.intersection((0x10, 0xA0, 0xA1))):
                self.pause_requested = True
        elif message in (0x101, 0x105):
            self.keys.discard(key)
        return 1

    def mouse_event(self, code, message, data):
        if code != 0:
            return self.user.CallNextHookEx(None, code, message, data)
        return 1

    def start(self):
        self.keys.clear()
        self.pause_requested = False
        for hook_type, callback in ((13, self.keyboard_callback), (14, self.mouse_callback)):
            handle = self.user.SetWindowsHookExW(hook_type, callback, self.module, 0)
            if not handle:
                error = ctypes.get_last_error()
                self.stop()
                logging.error("Input blocking unavailable (Win32 error %s)", error)
                return False
            self.handles.append(handle)
        return True

    def stop(self):
        for handle in self.handles:
            self.user.UnhookWindowsHookEx(handle)
        self.handles.clear()
        self.keys.clear()
        self.pause_requested = False



class OwnerFace:
    def __init__(self, detector):
        self.detector = detector
        self.path = BASE / "owner-face.npz"
        self.enabled = self.path.exists()
        self.last_seen = float("-inf")
        self.request = None
        self.message = None
        self.preview = None
        self.error = None

    @staticmethod
    def digest(pin, salt):
        return hashlib.scrypt(pin.encode(), salt=salt, n=16384, r=8, p=1)

    def run(self):
        try:
            import cv2
            import numpy as np
            finder = cv2.FaceDetectorYN.create(str(BASE / "face_detection_yunet_2023mar.onnx"), "", (320, 240))
            matcher = cv2.FaceRecognizerSF.create(str(BASE / "face_recognition_sface_2021dec.onnx"), "")
            profile = None
            if self.enabled:
                with np.load(self.path, allow_pickle=False) as saved:
                    profile = saved["feature"], bytes(saved["salt"]), bytes(saved["digest"])
            previous = None
            while not self.detector.stop.wait(0.28):
                sample = self.detector.latest_frame
                if sample is None or sample[0] == previous:
                    continue
                previous, frame = sample
                small = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)
                _, faces = finder.detect(small)
                feature = None
                if faces is not None and len(faces) == 1:
                    feature = matcher.feature(matcher.alignCrop(small, faces[0])).copy()
                self.preview = (previous, small.copy(), None if faces is None else faces.copy(), feature)
                request = self.request
                if request is not None:
                    pin, captured_feature = request
                    try:
                        if profile and not hmac.compare_digest(self.digest(pin, profile[1]), profile[2]):
                            self.message = "Incorrect enrollment PIN."
                        elif captured_feature is None:
                            self.message = "Show exactly one clear face and try again."
                        else:
                            salt = os.urandom(16)
                            digest = self.digest(pin, salt)
                            temporary = self.path.with_suffix(".tmp")
                            with temporary.open("wb") as stream:
                                np.savez(stream, feature=captured_feature, salt=salt, digest=digest)
                            temporary.replace(self.path)
                            profile = captured_feature, salt, digest
                            self.last_seen = previous
                            self.enabled = True
                            self.message = "Owner face saved."
                    except Exception:
                        logging.exception("Owner enrollment failed")
                        self.message = "Enrollment failed. See LaptopScreenGuard.log."
                    finally:
                        self.request = None
                if profile and feature is not None and matcher.match(feature, profile[0], cv2.FaceRecognizerSF_FR_COSINE) >= 0.45:
                    self.last_seen = previous
        except Exception:
            logging.exception("Owner recognition stopped")
            self.error = "Face engine unavailable. Check models and LaptopScreenGuard.log."
            self.message = self.error
            self.request = None



class EnrollmentDialog(QtWidgets.QDialog):
    """Qt preview reuses the detector feed; it never opens a second camera."""

    def __init__(self, guard):
        super().__init__()
        self.guard = guard
        self.owner = guard.owner
        self.feature = None
        self.frame_time = 0
        self.pending = False
        self.setWindowTitle("LaptopScreenGuard | Face Enrollment")
        self.setWindowIcon(QtGui.QIcon(str(BASE / "LaptopScreenGuard.png")))
        self.resize(880, 440)
        self.setMinimumSize(680, 410)
        self.setStyleSheet("""
            QDialog {background:#f5f7fb; color:#14273e;}
            QLabel {color:#14273e; font-size:14px;}
            QLabel#heading {font-size:23px; font-weight:700;}
            QLabel#subtitle {color:#607087;}
            QLabel#preview {background:#102338; color:#dce6f1; border-radius:18px;}
            QLabel#status {background:#e8eef7; padding:12px; border-radius:10px;}
            QLineEdit {background:white; border:1px solid #cbd5e1;
                border-radius:9px; padding:11px; font-size:15px; color:#14273e;}
            QLineEdit:focus {border:1px solid #e87925;}
            QPushButton {background:white; color:#14273e; border:1px solid #cbd5e1;
                padding:12px 20px; border-radius:10px; font-size:14px;}
            QPushButton#capture {background:#12314f; color:white; border:none; font-weight:600;}
            QPushButton#capture:disabled {background:#cbd5e1; color:#64748b;}
        """)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)
        heading = QtWidgets.QLabel("Let’s register your face")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        subtitle = QtWidgets.QLabel("Sit alone in good light and look straight at the webcam.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        content = QtWidgets.QHBoxLayout()
        content.setSpacing(22)
        layout.addLayout(content, 1)
        camera_column = QtWidgets.QVBoxLayout()
        form_column = QtWidgets.QVBoxLayout()
        form_column.setSpacing(10)
        content.addLayout(camera_column, 3)
        content.addLayout(form_column, 2)
        self.image = QtWidgets.QLabel("Starting live preview…")
        self.image.setObjectName("preview")
        self.image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumSize(280, 210)
        self.image.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Expanding)
        camera_column.addWidget(self.image, 1)
        self.status = QtWidgets.QLabel("Waiting for camera…")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        camera_column.addWidget(self.status)
        label = "Existing app PIN" if self.owner.enabled else "Choose an app PIN (6 or more digits)"
        form_column.addWidget(QtWidgets.QLabel(label))
        self.pin = QtWidgets.QLineEdit()
        self.pin.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pin.setPlaceholderText(label)
        self.pin.setMaxLength(128)
        form_column.addWidget(self.pin)
        self.confirm = None
        if not self.owner.enabled:
            self.confirm = QtWidgets.QLineEdit()
            self.confirm.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.confirm.setPlaceholderText("Confirm your app PIN")
            self.confirm.setMaxLength(128)
            form_column.addWidget(self.confirm)
        note = QtWidgets.QLabel("Local processing • No webcam photos saved\nMonitoring resumes when you close this window.")
        note.setObjectName("subtitle")
        note.setWordWrap(True)
        form_column.addWidget(note)
        form_column.addStretch()
        buttons = QtWidgets.QHBoxLayout()
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        self.capture = QtWidgets.QPushButton("Capture & Enroll")
        self.capture.setObjectName("capture")
        self.capture.setEnabled(False)
        self.capture.setAutoDefault(False)
        self.capture.clicked.connect(self.submit)
        buttons.addWidget(cancel)

        buttons.addWidget(self.capture)
        form_column.addLayout(buttons)
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(100)

    def reject(self):
        if not self.pending:
            super().reject()

    def submit(self):
        pin = self.pin.text()
        if len(pin) < 6 or not pin.isascii() or not pin.isdecimal():
            self.status.setText("Enter an app PIN containing at least six digits.")
            return
        if self.confirm is not None and self.confirm.text() != pin:
            self.status.setText("The two PIN entries do not match.")
            return
        if self.feature is None or time.monotonic() - self.frame_time > 1:
            self.status.setText("Camera frame expired. Look at the camera and try again.")
            return
        self.owner.message = None
        self.pending = True
        self.capture.setEnabled(False)
        self.pin.setEnabled(False)
        if self.confirm is not None:
            self.confirm.setEnabled(False)
        # Save the embedding of the exact valid preview sample selected by the user.
        self.owner.request = (pin, self.feature.copy())
        self.status.setText("Saving your face securely…")

    def refresh(self):
        if self.pending:
            message = self.owner.message
            if message is not None and self.owner.request is None:
                self.owner.message = None
                self.pending = False
                self.pin.setEnabled(True)
                if self.confirm is not None:
                    self.confirm.setEnabled(True)
                if message == "Owner face saved.":
                    self.refresh_timer.stop()
                    QtWidgets.QMessageBox.information(self, "Face enrolled", "Your face was enrolled successfully. Monitoring will now resume.")
                    self.accept()
                else:
                    QtWidgets.QMessageBox.warning(self, "Enrollment", message)
            return
        sample = self.owner.preview
        self.feature = None
        self.capture.setEnabled(False)
        if self.owner.error:
            self.status.setText(self.owner.error)
            return
        if sample is None or time.monotonic() - sample[0] > 1:
            self.image.clear()
            self.image.setText("Camera unavailable — open the shutter and check camera permissions.")
            self.status.setText("Waiting for a fresh camera frame…")
            return
        import cv2
        timestamp, frame, faces, feature = sample
        view = cv2.resize(frame, (640, 480))
        count = 0 if faces is None else len(faces)
        ready = False
        text = "No face detected. Look at the camera and open the shutter."
        if count > 1:
            text = "More than one face detected. Please sit alone."
        elif count == 1:
            x, y, w, h = faces[0][:4]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            roi = gray[max(0,int(y)):min(240,int(y+h)), max(0,int(x)):min(320,int(x+w))]
            if w < 65 or h < 65:
                text = "Move a little closer to the camera."
            elif x < 3 or y < 3 or x+w > 317 or y+h > 237:
                text = "Keep your whole face inside the preview."
            elif roi.size == 0 or roi.mean() < 45:
                text = "Your face is too dark. Add light in front of you."
            elif cv2.Laplacian(roi, cv2.CV_64F).var() < 20:
                text = "Hold still and check your camera focus."
            else:
                ready = feature is not None
                text = "Face ready. Enter your PIN and click Capture & Enroll."
            color = (120, 210, 80) if ready else (40, 165, 245)
            cv2.rectangle(view, (int(x*2), int(y*2)), (int((x+w)*2), int((y+h)*2)), color, 3)
        rgb = cv2.cvtColor(cv2.flip(view, 1), cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QtGui.QImage.Format.Format_RGB888).copy()
        pixmap = QtGui.QPixmap.fromImage(image).scaled(self.image.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.image.setPixmap(pixmap)
        self.status.setText(text)
        self.frame_time = timestamp
        self.feature = feature if ready else None
        self.capture.setEnabled(ready)


class Guard:
    def __init__(self, app):
        self.app = app
        self.enrollment = None
        self.paused = False
        self.hotkey_down = False
        self.input_guard = InputGuard()
        self.input_unavailable = False
        self.overlays = []
        self.detector = Detector()
        self.owner = OwnerFace(self.detector)
        self.owner_thread = None
        self.tray = QtWidgets.QSystemTrayIcon(
            QtGui.QIcon(str(BASE / "LaptopScreenGuard.png")), app
        )
        self.menu = QtWidgets.QMenu()
        self.pause_action = self.menu.addAction("Pause monitoring")
        self.pause_action.setCheckable(True)
        self.pause_action.toggled.connect(self.set_paused)
        self.menu.addAction("Enroll My Face", self.enroll_face)
        self.menu.addAction("Replace Enrolled Face", self.enroll_face)
        self.menu.addAction("Exit LaptopScreenGuard", app.quit)
        self.tray.setContextMenu(self.menu)
        self.tray.show()
        app.screenAdded.connect(self.rebuild_overlays)
        app.screenRemoved.connect(self.rebuild_overlays)
        self.timer = QtCore.QTimer(app)
        self.timer.timeout.connect(self.update)
        self.timer.start(25)
        app.aboutToQuit.connect(self.input_guard.stop)
        app.aboutToQuit.connect(self.detector.stop.set)
        self.detector.start()
        if self.owner.enabled:
            self.start_owner()

    def start_owner(self):
        if self.owner_thread is None or not self.owner_thread.is_alive():
            self.owner_thread = threading.Thread(target=self.owner.run, daemon=True)
            self.owner_thread.start()

    def enroll_face(self):
        if self.enrollment is not None:
            self.enrollment.raise_()
            self.enrollment.activateWindow()
            return
        self.start_owner()
        self.enrollment = EnrollmentDialog(self)
        self.rebuild_overlays()
        self.enrollment.finished.connect(self.finish_enrollment)
        self.enrollment.show()
        self.enrollment.raise_()
        self.enrollment.activateWindow()

    def finish_enrollment(self, _result):
        dialog = self.enrollment
        self.enrollment = None
        if self.owner.enabled:
            self.owner.last_seen = time.monotonic()
        if dialog is not None:
            dialog.refresh_timer.stop()
            dialog.pin.clear()
            if dialog.confirm is not None:
                dialog.confirm.clear()
            dialog.deleteLater()

    def set_paused(self, paused):
        self.paused = paused
        self.pause_action.setChecked(paused)

    def rebuild_overlays(self, *_):
        for overlay in self.overlays:
            overlay.hide()
            overlay.deleteLater()
        self.overlays.clear()
        self.input_guard.stop()
        self.input_unavailable = False

    def update(self):
        key_down = ctypes.windll.user32.GetAsyncKeyState
        pressed = all(key_down(key) & 0x8000 for key in (0x11, 0x10, 0x7B))
        if self.input_guard.pause_requested or (pressed and not self.hotkey_down):
            self.input_guard.pause_requested = False
            self.set_paused(not self.paused)
        self.hotkey_down = pressed

        now = time.monotonic()
        message = self.owner.message
        if message is not None and self.enrollment is None:
            self.owner.message = None
            self.tray.showMessage("LaptopScreenGuard", message)
        owner_away = self.owner.enabled and now - self.owner.last_seen >= 2.0
        cover = owner_away and not self.paused and self.enrollment is None
        if cover and not self.overlays:
            for screen in self.app.screens():
                overlay = QtWidgets.QWidget()
                overlay.setWindowFlags(
                    QtCore.Qt.WindowType.FramelessWindowHint
                    | QtCore.Qt.WindowType.WindowStaysOnTopHint
                    | QtCore.Qt.WindowType.Tool
                    | QtCore.Qt.WindowType.WindowDoesNotAcceptFocus
                )
                overlay.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
                overlay.setStyleSheet("background-color: black;")
                overlay.setGeometry(screen.geometry())
                screen.geometryChanged.connect(overlay.setGeometry)
                overlay.show()
                self.overlays.append(overlay)
            if self.overlays:
                self.input_unavailable = not self.input_guard.start()
        elif not cover and self.overlays:
            self.rebuild_overlays()

        status = "Enrolling face" if self.enrollment is not None else ("Paused" if self.paused else self.detector.status)
        if self.input_unavailable:
            status = "Input blocking unavailable. See LaptopScreenGuard.log."
        self.tray.setToolTip(f"LaptopScreenGuard | Face Only | {status}")


def main():
    app = QtWidgets.QApplication([])
    # Windows uses an explicit application ID for taskbar branding.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sanjeev.LaptopScreenGuard.FaceOnly")
    app.setWindowIcon(QtGui.QIcon(str(BASE / "LaptopScreenGuard.png")))
    app.setApplicationName("LaptopScreenGuard")
    app.setApplicationDisplayName("LaptopScreenGuard")
    app.setQuitOnLastWindowClosed(False)
    lock = QtCore.QLockFile(str(BASE / "LaptopScreenGuard.lock"))
    if not lock.tryLock(0):
        return
    guard = Guard(app)
    app.exec()
    guard.detector.join(timeout=1)
    lock.unlock()


if __name__ == "__main__":
    main()

