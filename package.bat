@echo off
title SAR Redaction Tool - Create Distribution Package
setlocal EnableDelayedExpansion

set "OUTZIP=%~dp0SAR_Redaction_Setup.zip"
set "TMPDIR=%TEMP%\SAR_Package_%RANDOM%"

echo.
echo  ==========================================
echo   Building distribution package...
echo  ==========================================
echo.

:: Create temp staging folder
mkdir "%TMPDIR%" >nul 2>&1

:: Copy all distributable files (no venv, no __pycache__, no output folders)
echo  Copying files...
copy "%~dp0app.py"            "%TMPDIR%\" >nul
copy "%~dp0install.bat"       "%TMPDIR%\" >nul
copy "%~dp0run.bat"           "%TMPDIR%\" >nul
copy "%~dp0open_browser.py"   "%TMPDIR%\" >nul
copy "%~dp0requirements.txt"  "%TMPDIR%\" >nul
copy "%~dp0README.txt"        "%TMPDIR%\" >nul 2>&1
if exist "%~dp0logo.jpg"  copy "%~dp0logo.jpg"  "%TMPDIR%\" >nul

:: Remove old zip if it exists
if exist "%OUTZIP%" del /f "%OUTZIP%" >nul

:: Create zip using PowerShell
echo  Compressing...
powershell -NoProfile -Command ^
    "Compress-Archive -Path '%TMPDIR%\*' -DestinationPath '%OUTZIP%' -CompressionLevel Optimal"

if errorlevel 1 (
    echo.
    echo  ERROR: Failed to create zip file.
    rd /s /q "%TMPDIR%" >nul 2>&1
    pause
    exit /b 1
)

:: Cleanup staging folder
rd /s /q "%TMPDIR%" >nul 2>&1

:: Report size
for %%F in ("%OUTZIP%") do set "FSIZE=%%~zF"
set /a "FSIZE_KB=%FSIZE% / 1024"

echo.
echo  ==========================================
echo   Package ready!
echo  ==========================================
echo.
echo   File : SAR_Redaction_Setup.zip
echo   Size : %FSIZE_KB% KB
echo.
echo   Send this ZIP to the recipient.
echo   They should:
echo     1. Extract the ZIP to any folder (e.g. C:\SAR_Redaction)
echo     2. Right-click INSTALL.bat  ^>  Run as administrator
echo     3. Double-click the desktop shortcut when setup finishes
echo.
pause
