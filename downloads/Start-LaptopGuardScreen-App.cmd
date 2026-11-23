@echo off
setlocal
title LaptopScreenGuard - Create Desktop Shortcut

echo.
echo Select your installed edition:
echo.
echo 1. Face Only
echo 2. Phone Only / Phone + Shutter / Phone + Cover
echo.

choice /c 12 /n /m "Choose 1 or 2: "

if errorlevel 2 (
    set "LSG_FOLDER=LaptopScreenGuard"
    set "LSG_NAME=LaptopScreenGuard"
) else (
    set "LSG_FOLDER=LaptopScreenGuard-Face-Only"
    set "LSG_NAME=LaptopScreenGuard - Face Only"
)

set "LSG_INSTALL=%USERPROFILE%\%LSG_FOLDER%"

if not exist "%LSG_INSTALL%\venv\Scripts\pythonw.exe" (
    echo.
    echo Installation not found:
    echo "%LSG_INSTALL%"
    echo.
    echo Install the selected edition first.
    pause
    exit /b 1
)

if not exist "%LSG_INSTALL%\LaptopScreenGuard.pyw" (
    echo.
    echo Application file not found. Run the installer again.
    pause
    exit /b 1
)

powershell.exe -NoProfile -Command ^
 "$ErrorActionPreference='Stop';" ^
 "$folder=$env:LSG_INSTALL;" ^
 "$shell=New-Object -ComObject WScript.Shell;" ^
 "$desktop=[Environment]::GetFolderPath('Desktop');" ^
 "$shortcut=$shell.CreateShortcut((Join-Path $desktop ($env:LSG_NAME+'.lnk')));" ^
 "$shortcut.TargetPath=Join-Path $folder 'venv\Scripts\pythonw.exe';" ^
 "$shortcut.Arguments=[char]34+(Join-Path $folder 'LaptopScreenGuard.pyw')+[char]34;" ^
 "$shortcut.WorkingDirectory=$folder;" ^
 "$shortcut.Description='Start LaptopScreenGuard background monitoring';" ^
 "$png=Join-Path $folder 'LaptopScreenGuard.png';" ^
 "$ico=Join-Path $folder 'LaptopScreenGuard.ico';" ^
 "if(Test-Path $png) {" ^
 "  $bytes=[IO.File]::ReadAllBytes($png);" ^
 "  if($bytes.Length -ge 24) {" ^
 "    $width=[int]$bytes[16]*16777216+[int]$bytes[17]*65536+[int]$bytes[18]*256+[int]$bytes[19];" ^
 "    $height=[int]$bytes[20]*16777216+[int]$bytes[21]*65536+[int]$bytes[22]*256+[int]$bytes[23];" ^
 "    if($width -le 256 -and $height -le 256) {" ^
 "      $stream=[IO.File]::Create($ico);" ^
 "      $writer=New-Object IO.BinaryWriter($stream);" ^
 "      try {" ^
 "        $writer.Write([uint16]0);$writer.Write([uint16]1);$writer.Write([uint16]1);" ^
 "        $writer.Write([byte]($width %% 256));$writer.Write([byte]($height %% 256));" ^
 "        $writer.Write([byte]0);$writer.Write([byte]0);" ^
 "        $writer.Write([uint16]1);$writer.Write([uint16]32);" ^
 "        $writer.Write([uint32]$bytes.Length);$writer.Write([uint32]22);$writer.Write($bytes);" ^
 "      } finally {$writer.Dispose()}" ^
 "    } else {" ^
 "      Add-Type -AssemblyName System.Drawing;" ^
 "      $image=[Drawing.Image]::FromFile($png);" ^
 "      $bitmap=New-Object Drawing.Bitmap(256,256);" ^
 "      $graphics=[Drawing.Graphics]::FromImage($bitmap);" ^
 "      try {" ^
 "        $graphics.Clear([Drawing.Color]::Transparent);" ^
 "        $graphics.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;" ^
 "        $scale=[Math]::Min(256.0/$image.Width,256.0/$image.Height);" ^
 "        $w=[int]($image.Width*$scale);$h=[int]($image.Height*$scale);" ^
 "        $graphics.DrawImage($image,[int]((256-$w)/2),[int]((256-$h)/2),$w,$h);" ^
 "        $memory=New-Object IO.MemoryStream;" ^
 "        try {" ^
 "          $bitmap.Save($memory,[Drawing.Imaging.ImageFormat]::Png);" ^
 "          $data=$memory.ToArray();" ^
 "          $stream=[IO.File]::Create($ico);" ^
 "          $writer=New-Object IO.BinaryWriter($stream);" ^
 "          try {" ^
 "            $writer.Write([uint16]0);$writer.Write([uint16]1);$writer.Write([uint16]1);" ^
 "            $writer.Write([byte]0);$writer.Write([byte]0);$writer.Write([byte]0);$writer.Write([byte]0);" ^
 "            $writer.Write([uint16]1);$writer.Write([uint16]32);" ^
 "            $writer.Write([uint32]$data.Length);$writer.Write([uint32]22);$writer.Write($data);" ^
 "          } finally {$writer.Dispose()}" ^
 "        } finally {$memory.Dispose()}" ^
 "      } finally {$graphics.Dispose();$bitmap.Dispose();$image.Dispose()}" ^
 "    }" ^
 "  }" ^
 "};" ^
 "if(Test-Path $ico){$shortcut.IconLocation=$ico+',0'};" ^
 "$shortcut.Save();"

if errorlevel 1 (
    echo.
    echo Shortcut could not be created. Check the error above.
    pause
    exit /b 1
)

echo.
echo Desktop shortcut created successfully!
echo Double-click it whenever you want to start LaptopScreenGuard.
echo.
pause