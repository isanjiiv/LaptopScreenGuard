@echo off
setlocal
cd /d "%~dp0"
set "GUARD_DIR=%USERPROFILE%\LaptopScreenGuard-Face-Only"
set "GUARD_START=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LaptopScreenGuard-Face-Only.cmd"
set "GUARD_PY=%GUARD_DIR%\venv\Scripts\python.exe"
set "GUARD_PYW=%GUARD_DIR%\venv\Scripts\pythonw.exe"

rem Use Python directly when the Windows launcher is missing.
set "CHECK_PY=import platform, struct, sys; sys.exit(not (sys.version_info[:2] == (3, 12) and struct.calcsize('P') == 8 and platform.machine().upper() == 'AMD64'))"
if exist "%GUARD_PY%" (
    "%GUARD_PY%" -c "%CHECK_PY%" >nul 2>&1
    if not errorlevel 1 goto install
)
python -c "%CHECK_PY%" >nul 2>&1
if not errorlevel 1 (
    python -m venv "%GUARD_DIR%\venv" || goto failed
    goto install
)
py -3.12 -c "%CHECK_PY%" >nul 2>&1
if not errorlevel 1 (
    py -3.12 -m venv "%GUARD_DIR%\venv" || goto failed
    goto install
)
echo Install Python 3.12 x64, then run this installer again.
pause
exit /b 1

:install
if not exist "%GUARD_PYW%" goto failed
"%GUARD_PY%" -m pip install "opencv-python==4.11.0.86" "PySide6==6.8.3" || goto failed
curl.exe --fail --location --retry 2 "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx" --output "%GUARD_DIR%\face_detection_yunet_2023mar.onnx.tmp" || goto failed
move /y "%GUARD_DIR%\face_detection_yunet_2023mar.onnx.tmp" "%GUARD_DIR%\face_detection_yunet_2023mar.onnx" >nul || goto failed
curl.exe --fail --location --retry 2 "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx" --output "%GUARD_DIR%\face_recognition_sface_2021dec.onnx.tmp" || goto failed
move /y "%GUARD_DIR%\face_recognition_sface_2021dec.onnx.tmp" "%GUARD_DIR%\face_recognition_sface_2021dec.onnx" >nul || goto failed
"%GUARD_PY%" -c "import cv2, sys; from pathlib import Path; from PySide6 import QtWidgets; p=Path(sys.argv[1]); cv2.FaceDetectorYN.create(str(p/'face_detection_yunet_2023mar.onnx'), '', (320,240)); cv2.FaceRecognizerSF.create(str(p/'face_recognition_sface_2021dec.onnx'), '')" "%GUARD_DIR%" || goto failed
copy /y "%~dp0LaptopScreenGuard.pyw" "%GUARD_DIR%\LaptopScreenGuard.pyw" >nul || goto failed
> "%GUARD_START%" echo @start "" "%%USERPROFILE%%\LaptopScreenGuard-Face-Only\venv\Scripts\pythonw.exe" "%%USERPROFILE%%\LaptopScreenGuard-Face-Only\LaptopScreenGuard.pyw"
if errorlevel 1 goto failed
start "" "%GUARD_PYW%" "%GUARD_DIR%\LaptopScreenGuard.pyw"
echo Setup complete. Look for LaptopScreenGuard under the system tray arrow.
pause
exit /b 0

:failed
echo Setup failed. Check the error above.
pause
exit /b 1
