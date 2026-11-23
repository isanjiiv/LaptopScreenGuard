<div align="center">

# 🛡️ LaptopScreenGuard

### Your screen. Your space.

**Webcam-triggered screen privacy for Windows.**

Automatically hide your workspace when your selected privacy trigger is detected.

[![Windows](https://img.shields.io/badge/Windows_10_/_11-0078D4?style=for-the-badge&logo=windows&logoColor=white)](#-requirements)
[![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](#-installation-on-a-new-laptop)
[![PIN Protection](https://img.shields.io/badge/PIN_Protected_Controls-092647?style=for-the-badge)](#-pin-protected-controls)
[![Status](https://img.shields.io/badge/Preview_Release-F47621?style=for-the-badge)](#-testing-before-regular-use)

<br>

<a href="https://laptopscreenguard.vercel.app/">
  <img
    src="assets/laptopscreenguard-infographic.png"
    alt="LaptopScreenGuard infographic showing four webcam-triggered privacy editions"
    width="100%"
  />
</a>

[![Visit Website](https://img.shields.io/badge/Visit_Website-092647?style=for-the-badge&logo=googlechrome&logoColor=white)](https://laptopscreenguard.vercel.app/)
[![Downloads](https://img.shields.io/badge/Download-F47621?style=for-the-badge&logo=github&logoColor=white)](#-choose-your-edition)
[![Report an Issue](https://img.shields.io/badge/Report_an_Issue-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/isanjiiv/LaptopScreenGuard/issues)

</div>

---

## 📖 About

LaptopScreenGuard is a Python-based Windows application that monitors a selected webcam trigger and places a black overlay over the display when that trigger becomes active.

The app also attempts to suppress keyboard and mouse input while the overlay is visible. When the triggering condition clears, the overlay disappears and normal input resumes.

Four standalone editions let you choose the behavior that fits your workspace.

The latest packages include PIN-protected Pause and Exit controls, LaptopScreenGuard branding, and a compact live enrollment preview in Face Only.

**Created by [Sanjeev Kumar](https://isanjiiv.github.io/) — IT Engineer.**

> **Important:** LaptopScreenGuard provides an additional layer of visual privacy. It does not replace Windows account locking or prevent screenshots, screen recording, or all photography. PIN protection applies to application controls; it does not prevent termination through Task Manager or administrator actions.

## 🖼️ How it works

1. The app reads frames from your webcam.
2. Your selected edition checks its privacy trigger.
3. An active trigger displays a black overlay.
4. The app attempts to block keyboard and mouse input while the overlay is active.
5. When the condition clears, the workspace becomes visible again.

**Try the visual demonstration:**  
https://laptopscreenguard.vercel.app/

## ✨ Features

- 📱 Phone detection in three phone-based editions.
- 🔒 Shutter-like camera-feed checks in editions 2 and 3.
- 🖐️ Additional lens-cover checks in edition 3.
- 👤 Enrolled-face monitoring in Face Only.
- 🎥 Live face-enrollment preview with positioning guidance.
- 🖥️ Compact horizontal enrollment window.
- 🛡️ LaptopScreenGuard application and system-tray branding.
- 🔑 PIN verification before pausing or exiting.
- ⌨️ PIN verification when pausing through the keyboard shortcut.
- ⏱️ A 30-second retry delay after five incorrect control-PIN attempts.
- ⚙️ Background monitoring and per-account automatic startup.
- 📴 Offline monitoring after initial setup.
- 📦 Separate installation packages for each edition.

## 📦 Choose your edition

| Edition | What activates the overlay | Download |
| --- | --- | --- |
| **01 Phone Only** | A phone detected in the webcam’s view | [Download ZIP](downloads/LaptopScreenGuard-01-Phone-Only.zip?raw=true) |
| **02 Phone + Shutter** | Phone detection, or a dark, uniform or unavailable webcam feed | [Download ZIP](downloads/LaptopScreenGuard-02-Phone-and-Shutter.zip?raw=true) |
| **03 Phone + Shutter + Cover** | Phone and shutter checks, plus blurred or low-detail lens-cover checks | [Download ZIP](downloads/LaptopScreenGuard-03-Phone-Shutter-and-Cover.zip?raw=true) |
| **04 Face Only** | No match to the enrolled face for about two seconds | [Download ZIP](downloads/LaptopScreenGuard-04-Face-Only.zip?raw=true) |

### Which edition should I choose?

- **Phone Only:** You only want phone detection.
- **Phone + Shutter:** You also want checks for shutter-like changes in the webcam feed.
- **Phone + Shutter + Cover:** You want additional checks for a covered lens.
- **Face Only:** You want the display hidden when your enrolled face is absent.

> Run only one edition at a time for a Windows account.

### Understanding Face Only

Face Only does not run separate phone, shutter or lens-cover detection rules.

However, closing or covering the camera can hide your enrolled face and activate its face-absence rule.

### Understanding shutter and cover detection

These editions infer shutter closure or obstruction from the camera feed. Lighting, camera quality and the type of obstruction can affect results.

## 💻 Requirements

| Requirement | Details |
| --- | --- |
| Operating system | Windows 10 or Windows 11 |
| Architecture | Intel/AMD x64 |
| Python | Python 3.12, 64-bit |
| Camera | Working webcam with desktop-app access enabled |
| Internet | Required during initial dependency and model downloads |
| Lighting | Adequate front lighting for enrollment and face matching |

Monitoring works offline after the required packages and models are installed.

## 🚀 Installation on a new laptop

### Step 1 — Install Python 3.12 x64

Download Python from:

https://www.python.org/downloads/windows/

Choose **Python 3.12, 64-bit**.

During installation, enable:

```text
Add python.exe to PATH
```

After installation, open a **new Command Prompt**.

Check:

```cmd
py -3.12 --version
```

Expected output:

```text
Python 3.12.x
```

You can also run:

```cmd
python --version
```

If another Python version appears, ensure Python 3.12 x64 is installed. The installer checks for the supported version.

### Step 2 — Download one edition

Use the download table above.

Right-click the ZIP and choose:

```text
Extract All
```

Open the extracted folder.

Keep all these files together:

```text
LaptopScreenGuard.pyw
LaptopScreenGuard.png
control_security.py
Install-LaptopScreenGuard.cmd
Uninstall-LaptopScreenGuard.cmd
START-HERE.txt
```

**Do not delete `control_security.py`. The PIN-protected application requires it.**

**Do not run the installer directly from inside the ZIP.**

### Step 3 — Close older instances

Exit any running LaptopScreenGuard or PhoneScreenGuard instance from its tray menu.

If the existing version has PIN-protected controls, enter its PIN to exit.

Close other webcam privacy applications before proceeding.

### Step 4 — Run the installer

Double-click:

```cmd
Install-LaptopScreenGuard.cmd
```

Run it under the **Windows account that will use the app**.

You can also open Command Prompt in the extracted folder and run:

```cmd
Install-LaptopScreenGuard.cmd
```

The installer will:

1. Check for Python 3.12 x64.
2. Create or reuse the application’s virtual environment.
3. Install required packages.
4. Download the edition’s detection models.
5. Copy the application, PIN-control module and logo.
6. Create a startup entry for the current Windows account.
7. Start LaptopScreenGuard in the background.

Keep the internet connected and wait for:

```text
Setup complete
```

### Step 5 — Complete PIN setup

**Phone editions — modes 1, 2 and 3:**

1. On the first launch, choose a control PIN containing at least six digits.
2. Enter it again to confirm.
3. Keep the PIN safe. It is required for Pause and Exit.

Canceling first-time PIN setup closes the application. Launch it again to complete setup.

**Face Only:**

Enroll your face using the instructions below. The enrollment PIN also protects Pause and Exit.

If a Face Only enrollment already exists, its existing PIN is reused.

### Step 6 — Find the tray icon

Open the hidden-icons arrow near the Windows clock.

Look for the **LaptopScreenGuard laptop-and-shield logo**.

Hover over the icon to see the edition and status. Right-click it to open the available controls.

### Step 7 — Confirm startup

Sign out and sign back in.

Confirm that LaptopScreenGuard starts and appears in the system tray.

> Startup is configured for the installing Windows account. Installing it as an administrator does not automatically configure every standard user account.

## 🔑 PIN-protected controls

| Action | PIN required? |
| --- | --- |
| Pause monitoring from the tray | Yes |
| Pause using `Ctrl + Shift + F12` | Yes |
| Resume monitoring | No |
| Exit LaptopScreenGuard from the tray | Yes |
| Open Face Only enrollment after a face is already enrolled | Yes |
| Replace an enrolled face | Existing enrollment PIN required |
| End task through Windows Task Manager | Not protected by the app PIN |

### Which PIN is used?

- **Phone editions:** The control PIN created on first launch.
- **Face Only:** The PIN created during face enrollment.

This is an application PIN, not necessarily your Windows sign-in PIN.

### Incorrect PIN attempts

- An incorrect PIN cancels the requested action.
- Canceling the prompt does not authorize Pause or Exit.
- Five incorrect control-PIN attempts trigger a 30-second retry delay.

The retry delay applies to the control-PIN prompts.

### PIN prompt during an active overlay

Input hooks are temporarily released so you can type into the PIN prompt. An active black overlay remains visible while the trigger remains active.

Monitoring continues. After the prompt closes, normal input suppression can resume if the overlay is still active.

### PIN recovery

This build does not include a PIN-change or PIN-reset interface.

Keep your PIN safe. The PIN hash cannot be used to display your original PIN.

Uninstalling removes installation data, including the saved control PIN or face enrollment. Reinstallation and enrollment may then be required.

> PIN protection is not tamper protection. Task Manager, administrator actions, source edits, uninstalling, or modification of local files can bypass it.

## 👤 Face Only enrollment

### Register your face

1. Open the webcam shutter.
2. Sit alone with good lighting in front of you.
3. Right-click the LaptopScreenGuard tray icon.
4. Select **Enroll My Face**.
5. The enrollment window opens.
6. Adjust your position using the preview guidance.
7. Choose and confirm an app PIN with at least **six digits**.
8. When the face is ready, click **Capture & Enroll**.
9. Wait for the success message.

Once a face is enrolled, opening the enrollment window requires the existing PIN.

### Compact enrollment layout

| Left side | Right side |
| --- | --- |
| Live mirrored camera preview | App PIN |
| Face bounding box | PIN confirmation for first enrollment |
| Camera and positioning guidance | Capture & Enroll and Cancel |

The preview reuses the app’s camera feed.

While the enrollment window is open, the privacy overlay and input blocking are temporarily suspended so you can complete enrollment.

For an existing enrollment, the control PIN is checked before opening this window.

### Preview guidance

| Condition | Action |
| --- | --- |
| No face detected | Open the shutter and look at the camera |
| Multiple faces detected | Sit alone in the camera’s view |
| Face too small | Move closer |
| Face partly outside the preview | Reposition so your whole face is visible |
| Face too dark | Add light in front of you |
| Face blurred | Hold still and check camera focus |
| Face ready | Enter your PIN and click Capture & Enroll |

### Replace the enrolled face

1. Right-click the tray icon.
2. Select **Replace Enrolled Face**.
3. Enter your existing PIN to authorize opening enrollment.
4. Position the new face in the preview.
5. Enter the existing PIN in the enrollment form.
6. Click **Capture & Enroll**.

This build checks the PIN before opening enrollment and again when saving the replacement.

Canceling preserves the existing enrollment.

### Test face monitoring

1. Stay in front of the camera and confirm your workspace remains visible.
2. Step away.
3. After about two seconds without an enrolled-face match, the display should be covered.
4. Return alone and face the camera.
5. Confirm that your workspace and normal input return.

Repeat enrollment separately on every laptop and Windows account.

## 🔁 Switch editions

1. Exit the current edition from its tray menu using its PIN.
2. Download and extract the edition you want.
3. Run its installer.
4. Ensure only one edition starts after sign-in.

Modes 1–3 share a folder, control-PIN file and startup entry. An existing phone-edition control PIN is reused when switching between them.

Face Only uses a separate folder and startup entry. When switching between Face Only and a phone edition, disable the unwanted startup entry to avoid launching both.

Press **Windows + R** and enter:

```text
shell:startup
```

Back up or remove only the obsolete startup entry.

## ⌨️ Controls and recovery

| Action | Shortcut or control |
| --- | --- |
| Pause monitoring | `Ctrl + Shift + F12`, then enter PIN |
| Resume monitoring | `Ctrl + Shift + F12` |
| Open Windows security options | `Ctrl + Alt + Delete` |
| Lock Windows | `Windows + L` |
| Exit the app | Tray → Exit LaptopScreenGuard → enter PIN |
| Enroll or replace a face | Face Only tray menu |

Use **Windows + L** when leaving your laptop unattended.

Windows security options remain available for recovery. Signing out can close unsaved work.

## 🧪 Testing before regular use

Test on the actual laptop:

- Selected trigger detection.
- Overlay appearance and removal.
- Keyboard and mouse restoration.
- Correct, incorrect and canceled PIN prompts.
- Pause through the tray and keyboard shortcut.
- Exit authorization.
- Face enrollment and matching.
- Camera disconnection or unavailability.
- Startup after signing in.
- Processor usage during normal work.

Python syntax and PIN-control logic have been checked. Live Windows UI, webcam, overlay and input recovery still require testing on the target laptop.

## 📂 Installation locations

| Edition | Folder |
| --- | --- |
| Modes 1–3 | `%USERPROFILE%\LaptopScreenGuard` |
| Face Only | `%USERPROFILE%\LaptopScreenGuard-Face-Only` |

### Open the installed folder

For modes 1–3:

```cmd
explorer "%USERPROFILE%\LaptopScreenGuard"
```

For Face Only:

```cmd
explorer "%USERPROFILE%\LaptopScreenGuard-Face-Only"
```

### Important files

| File | Purpose |
| --- | --- |
| `LaptopScreenGuard.pyw` | Application source |
| `control_security.py` | PIN verification and protected controls |
| `LaptopScreenGuard.png` | Application and tray logo |
| `LaptopScreenGuard.log` | Diagnostic log |
| `control-pin.json` | Phone editions’ salted control-PIN hash |
| `owner-face.npz` | Face Only’s local enrollment and PIN-hash data |
| `venv` | Installed Python environment |

Do not share your PIN, `control-pin.json`, or `owner-face.npz`.

## 🛠️ Diagnostic commands

Exit the running app using its PIN before starting another instance.

### Run a phone edition with visible errors

```cmd
"%USERPROFILE%\LaptopScreenGuard\venv\Scripts\python.exe" "%USERPROFILE%\LaptopScreenGuard\LaptopScreenGuard.pyw"
```

### Run Face Only with visible errors

```cmd
"%USERPROFILE%\LaptopScreenGuard-Face-Only\venv\Scripts\python.exe" "%USERPROFILE%\LaptopScreenGuard-Face-Only\LaptopScreenGuard.pyw"
```

Keep Command Prompt open during diagnosis.

### Start a phone edition in the background

```cmd
start "" "%USERPROFILE%\LaptopScreenGuard\venv\Scripts\pythonw.exe" "%USERPROFILE%\LaptopScreenGuard\LaptopScreenGuard.pyw"
```

### Start Face Only in the background

```cmd
start "" "%USERPROFILE%\LaptopScreenGuard-Face-Only\venv\Scripts\pythonw.exe" "%USERPROFILE%\LaptopScreenGuard-Face-Only\LaptopScreenGuard.pyw"
```

### Read the log

For modes 1–3:

```cmd
notepad "%USERPROFILE%\LaptopScreenGuard\LaptopScreenGuard.log"
```

For Face Only:

```cmd
notepad "%USERPROFILE%\LaptopScreenGuard-Face-Only\LaptopScreenGuard.log"
```

## ❓ Troubleshooting

### Python is not found

Open a new Command Prompt and run:

```cmd
py -3.12 --version
```

If unavailable, modify or reinstall Python 3.12 x64 and enable its PATH option.

### Installation fails while downloading packages or models

- Check your internet connection.
- Read the error displayed in the installer window.
- Confirm security software or network filtering is not blocking the required download.
- Run the installer again after correcting the error.

### An error mentions `control_security`

Keep `control_security.py` beside `LaptopScreenGuard.pyw` in the extracted edition folder.

Run the installer again after closing the app. The installer copies both files into the installation folder.

### Phone edition closes during first-time PIN setup

Canceling setup, entering an invalid PIN, or entering mismatched confirmation closes the app.

Launch the app again and choose and confirm a PIN containing at least six digits.

### Camera preview is unavailable

- Open the physical shutter.
- Check camera permissions for desktop applications in Windows Settings.
- Close other apps using the webcam.
- Confirm the webcam works in the Windows Camera app.
- Check `CAMERA_INDEX` if the laptop has multiple cameras.

### Capture & Enroll is disabled

The preview must contain one suitable, fresh face sample.

Follow the displayed guidance for lighting, distance, positioning or blur.

### Existing PIN is rejected

Use the app PIN for the installed edition:

- Phone editions use the first-launch control PIN.
- Face Only uses the enrollment PIN.

If the retry delay is active, wait 30 seconds before trying again.

### Old icon still appears

1. Exit the running app using its PIN.
2. Run `Install-LaptopScreenGuard.cmd` from the extracted edition folder again.
3. Confirm `LaptopScreenGuard.png` exists beside the installed Python file.
4. Restart the application if it is not already running.

### App does not start after sign-in

Open:

```text
shell:startup
```

Check that the correct startup entry exists for the current Windows account.

Remove obsolete or duplicate entries only after identifying them.

### Screen remains black

Press:

```text
Ctrl + Shift + F12
```

Enter your app PIN to authorize pausing.

If necessary, use:

```text
Ctrl + Alt + Delete
```

Then inspect the app log, webcam availability and face matching.

### Processor usage is high

Confirm only one privacy edition is running. Close duplicate instances and other webcam detection applications.

Check usage in Task Manager and include your laptop specifications when reporting a performance issue.

## 🗑️ Uninstall

1. Exit LaptopScreenGuard from the tray using its PIN.
2. Open the extracted edition folder.
3. Run:

```cmd
Uninstall-LaptopScreenGuard.cmd
```

The script removes the edition’s startup entry and installation folder.

**Uninstalling deletes that installation’s local PIN data. Uninstalling Face Only also deletes its face enrollment.**

The uninstall script itself is not protected by the application PIN.

## 🔐 Privacy and limitations

- Webcam processing runs locally after setup.
- The application does not save webcam photo files.
- PINs are stored as salted hashes, not plain text.
- Face Only stores a local face embedding and salted app PIN hash.
- Lighting, camera quality, positioning and processor performance affect results.
- Face matching may accept photos or videos.
- Phone detection cannot detect devices outside the webcam’s field of view.
- Shutter and cover detection can produce false positives or miss some obstructions.
- Input suppression is attempted and must be tested on each laptop.
- The overlay is not a Windows security boundary.
- It does not prevent screenshots or screen recording.
- The app PIN does not block Task Manager termination, uninstalling, administrator actions or changes to local program files.

Use normal Windows security controls alongside this tool.

## 🗂️ Repository structure

| Location | Contents |
| --- | --- |
| `downloads/` | Four PIN-protected installer ZIPs |
| `assets/` | Website and README images |
| `index.html` | Product website |
| `favicon.png` | Website icon |
| `README.md` | Installation and usage documentation |
| `src/` — optional | Unpacked source matching the downloadable packages |

A separate `src/` folder is not required to install the app from the ZIPs or host the static website.

Each installer ZIP already includes its Python source and setup files. If `src/` is maintained, keep it synchronized with the downloadable editions.

## 📜 Dependencies

Dependencies and detection models retain their own licenses and distribution terms.

- [Ultralytics licensing](https://www.ultralytics.com/license)
- [OpenCV Zoo](https://github.com/opencv/opencv_zoo)
- [Qt for Python licensing](https://doc.qt.io/qtforpython-6/licenses.html)

## 🐛 Report an issue

Include:

- Windows version.
- Python version.
- Edition installed.
- Laptop model and webcam.
- Steps to reproduce the problem.
- Relevant log messages.

Do not upload your PIN, control-PIN file or enrollment file.

[Open an issue](https://github.com/isanjiiv/LaptopScreenGuard/issues)

---

<div align="center">

## 🌐 Explore LaptopScreenGuard

[![Visit Website](https://img.shields.io/badge/Visit_Website-092647?style=for-the-badge&logo=googlechrome&logoColor=white)](https://laptopscreenguard.vercel.app/)
[![GitHub Repository](https://img.shields.io/badge/GitHub_Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/isanjiiv/LaptopScreenGuard)

## 👨‍💻 Meet the Creator

<a href="https://isanjiiv.github.io/">
  <img
    src="https://isanjiiv.github.io/assets/images/sanjeev-it-engineer.png"
    alt="Sanjeev Kumar — IT Engineer and creator of LaptopScreenGuard"
    width="180"
  />
</a>

### Sanjeev Kumar

**IT Engineer · System Administration · Networking · Cloud · Cybersecurity**

Building practical tools through Python, automation and computer vision.

[![Portfolio](https://img.shields.io/badge/Portfolio-092647?style=for-the-badge&logo=googlechrome&logoColor=white)](https://isanjiiv.github.io/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/isanjiiv/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/isanjiiv)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/isanjiiv/)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@isanjiiv)
[![X](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/isanjiiv)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:sanjeev753304@gmail.com)

<br>

💬 **Feedback, testing suggestions and contributions are welcome.**

⭐ **Found this useful? Give LaptopScreenGuard a star on GitHub!**

</div>
