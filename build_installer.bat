@echo off
title Build SAR Redaction Tool Installer
setlocal EnableDelayedExpansion

echo.
echo  ==========================================
echo   SAR Redaction Tool  --  Build Installer
echo  ==========================================
echo.

:: ── Find Inno Setup compiler ──────────────────────────────
set "ISCC="
for %%P in (
    "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles%\Inno Setup 6\ISCC.exe"
    "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
    "%ProgramFiles%\Inno Setup 5\ISCC.exe"
) do (
    if exist %%P (
        if not defined ISCC set "ISCC=%%~P"
    )
)

if not defined ISCC (
    echo  ERROR: Inno Setup not found.
    echo.
    echo  Please install it from:
    echo    https://jrsoftware.org/isdl.php
    echo.
    echo  Then re-run this script.
    pause
    exit /b 1
)

echo  Using: %ISCC%
echo.
echo  Compiling installer...
echo.

"%ISCC%" "%~dp0installer.iss"

if errorlevel 1 (
    echo.
    echo  ERROR: Build failed.  Check the output above for details.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Build complete!
echo  ==========================================
echo.
echo   Output: %~dp0SAR_Redaction_Tool_Setup.exe
echo.
echo   Distribute this single .exe file.
echo   Recipients double-click it and follow the wizard.
echo.
pause
