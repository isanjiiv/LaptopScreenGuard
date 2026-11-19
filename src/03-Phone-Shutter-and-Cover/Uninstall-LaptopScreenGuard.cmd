@echo off
setlocal
echo Exit LaptopScreenGuard from its tray menu, then press any key.
pause >nul
set "GUARD_START=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\LaptopScreenGuard.cmd"
if exist "%GUARD_START%" del "%GUARD_START%"
if exist "%GUARD_START%" goto failed
if exist "%USERPROFILE%\LaptopScreenGuard" rmdir /s /q "%USERPROFILE%\LaptopScreenGuard"
if exist "%USERPROFILE%\LaptopScreenGuard" goto failed
echo LaptopScreenGuard removed.
pause
exit /b 0
:failed
echo Removal incomplete. Close the app and try again.
pause
exit /b 1
