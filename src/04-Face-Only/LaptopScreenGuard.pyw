"""Local webcam phone detection for the signed-in Windows desktop."""
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
                pin = self.request
                if pin is not None:
                    try:
                        if profile and not hmac.compare_digest(self.digest(pin, profile[1]), profile[2]):
                            self.message = "Incorrect enrollment PIN."
                        elif feature is None:
                            self.message = "Show exactly one clear face and try again."
                        else:
                            salt = os.urandom(16)
                            digest = self.digest(pin, salt)
                            temporary = self.path.with_suffix(".tmp")
                            with temporary.open("wb") as stream:
                                np.savez(stream, feature=feature, salt=salt, digest=digest)
                            temporary.replace(self.path)
                            profile = feature, salt, digest
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
            self.message = "Owner face unavailable. Check models and LaptopScreenGuard.log."
            self.request = None


class Guard:
    def __init__(self, app):
        self.app = app
        self.paused = False
        self.hotkey_down = False
        self.input_guard = InputGuard()
        self.input_unavailable = False
        self.overlays = []
        self.detector = Detector()
        self.owner = OwnerFace(self.detector)
        self.owner_thread = None
        self.tray = QtWidgets.QSystemTrayIcon(
            app.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon), app
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
        if self.owner.request is not None:
            return
        label = "Enter your existing enrollment PIN." if self.owner.enabled else "Choose an enrollment PIN (at least six digits)."
        pin, ok = QtWidgets.QInputDialog.getText(None, "LaptopScreenGuard", label, QtWidgets.QLineEdit.EchoMode.Password)
        if not ok:
            return
        if len(pin) < 6 or not pin.isascii() or not pin.isdecimal():
            self.tray.showMessage("LaptopScreenGuard", "Use at least six digits.")
            return
        if not self.owner.enabled:
            confirmation, ok = QtWidgets.QInputDialog.getText(None, "LaptopScreenGuard", "Confirm enrollment PIN.", QtWidgets.QLineEdit.EchoMode.Password)
            if not ok or pin != confirmation:
                return
        if self.detector.latest_frame is None:
            self.tray.showMessage("LaptopScreenGuard", "Open the shutter and face the webcam.")
            return
        self.owner.request = pin
        self.start_owner()

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
        if message is not None:
            self.owner.message = None
            self.tray.showMessage("LaptopScreenGuard", message)
        owner_away = self.owner.enabled and now - self.owner.last_seen >= 2.0
        cover = owner_away and not self.paused
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

        status = "Paused" if self.paused else self.detector.status
        if self.input_unavailable:
            status = "Input blocking unavailable. See LaptopScreenGuard.log."
        self.tray.setToolTip(f"LaptopScreenGuard | Face Only | {status}")


def main():
    app = QtWidgets.QApplication([])
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
