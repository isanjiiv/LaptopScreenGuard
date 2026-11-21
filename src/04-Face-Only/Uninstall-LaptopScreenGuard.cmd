@echo off
setlocal
echo Exit LaptopScreenGuard from its tray menu, then press any key.
pause >nul
set "GUARD_START=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LaptopScreenGuard-Face-Only.cmd"
if exist "%GUARD_START%" del "%GUARD_START%"
if exist "%GUARD_START%" goto failed
if exist "%USERPROFILE%\LaptopScreenGuard-Face-Only" rmdir /s /q "%USERPROFILE%\LaptopScreenGuard-Face-Only"
if exist "%USERPROFILE%\LaptopScreenGuard-Face-Only" goto failed
echo LaptopScreenGuard removed.
pause
exit /b 0
:failed
echo Removal incomplete. Close the app and try again.
pause
exit /b 1

