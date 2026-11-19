# LaptopScreenGuard

Webcam privacy for Windows with four selectable editions. The app shows a black overlay and attempts to block keyboard and mouse input while its trigger is active.

## How it works

![Four LaptopScreenGuard modes showing a normal display changing to a black overlay](assets/laptopscreenguard-infographic.png)

Each edition monitors its selected trigger through the webcam. When the trigger clears, the overlay clears and ordinary keyboard and mouse input is restored. Face Only requires a match with the enrolled face. Camera obstruction can also hide that face and activate its two-second absence rule.

## Download your edition

| Edition | Trigger | Download |
| --- | --- | --- |
| 01-Phone-Only | Phone detected | [Download](downloads/LaptopScreenGuard-01-Phone-Only.zip?raw=true) |
| 02-Phone-and-Shutter | Phone or dark, uniform or unavailable webcam feed | [Download](downloads/LaptopScreenGuard-02-Phone-and-Shutter.zip?raw=true) |
| 03-Phone-Shutter-and-Cover | Phone, shutter-like changes or blurred low-detail lens cover | [Download](downloads/LaptopScreenGuard-03-Phone-Shutter-and-Cover.zip?raw=true) |
| 04-Face-Only | Registered face unmatched for about two seconds | [Download](downloads/LaptopScreenGuard-04-Face-Only.zip?raw=true) |

## Install step by step

1. Install Python 3.12 x64 on Windows 10/11 x64. Enable Add python.exe to PATH if offered. Download from https://www.python.org/downloads/windows/.
2. Open a fresh CMD and check Python using either command below. Expected version is Python 3.12.x.

```cmd
python --version
py -3.12 --version
```

3. Download one edition ZIP above and select Extract All. Exit any existing webcam privacy app from its tray menu. To prevent it relaunching, open Win+R, type shell:startup and back up/remove the old startup entry.
4. In the extracted edition folder, double-click Install-LaptopScreenGuard.cmd under the Windows account that will use the app. Internet is required for initial package and model downloads. Wait for Setup complete.
5. Open the ^ tray menu near the clock. Hover over LaptopScreenGuard to confirm the edition and camera status. Sign out and sign back in to test automatic startup.
6. Run only one edition at a time. After initial setup, monitoring works offline.

## Face Only enrollment and replacement

1. Open the shutter and sit alone in good light.
2. Right-click the tray icon and select Enroll My Face.
3. Choose and confirm an app PIN of at least six digits. Look at the webcam until Owner face saved appears.
4. Step away or let another person take your seat. After about two seconds without an owner match, the screen should black out. Return alone to restore it.
5. Use Replace Enrolled Face and the existing app PIN to register a new face. Repeat enrollment on each laptop/account.

Face Only uses face matching as its trigger. A shutter or cover can hide the face and trigger the same absence rule. Modes 2 and 3 infer shutter closure from the feed, so an object producing a dark or missing feed can also trigger Mode 2.

## Test and recover

Test the selected trigger, input blocking during the overlay and input restoration afterwards. Ctrl+Shift+F12 pauses or resumes monitoring. Ctrl+Alt+Delete opens Windows security options if recovery is needed. Signing out may close unsaved work.

This preview still needs fresh installation, webcam matching and input recovery testing on the target Windows laptop. Webcam face matching may accept a photo or video. Use Win+L to secure the Windows session.

## Paths and diagnostic commands

Modes 1–3 install in %USERPROFILE%\LaptopScreenGuard. Face Only installs in %USERPROFILE%\LaptopScreenGuard-Face-Only. Each is installed for the signed-in Windows account.

For startup errors, open CMD and run the command for your edition. Keep that CMD open during the test.

```cmd
"%USERPROFILE%\LaptopScreenGuard\venv\Scripts\python.exe" "%USERPROFILE%\LaptopScreenGuard\LaptopScreenGuard.pyw"
```

```cmd
"%USERPROFILE%\LaptopScreenGuard-Face-Only\venv\Scripts\python.exe" "%USERPROFILE%\LaptopScreenGuard-Face-Only\LaptopScreenGuard.pyw"
```

For a background Face Only launch, run:

```cmd
start "" "%USERPROFILE%\LaptopScreenGuard-Face-Only\venv\Scripts\pythonw.exe" "%USERPROFILE%\LaptopScreenGuard-Face-Only\LaptopScreenGuard.pyw"
```

Check LaptopScreenGuard.log in the appropriate installation folder. Verify Windows camera privacy permissions, close other webcam apps and use adequate lighting. The Face Only edition stores a local face embedding and salted app PIN hash. Webcam photos are not saved.

## Switch, update or uninstall

Exit the app before running another edition's Install-LaptopScreenGuard.cmd. Carry forward a custom CAMERA_INDEX if you changed it. The renamed app uses new folders and startup entries. Disable the previous app's startup entry and enroll again in Face Only. To remove an edition, exit it and run its Uninstall-LaptopScreenGuard.cmd. Removal also deletes its local face enrollment.

## Repository files

| Folder | Contents |
| --- | --- |
| downloads/ | Four full installer ZIPs |
| src/ | Matching source and setup scripts |

See GITHUB-UPLOAD.md for repository publishing steps. Dependencies and models retain their own terms. Review https://www.ultralytics.com/license and https://github.com/opencv/opencv_zoo for your distribution requirements.
