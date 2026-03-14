@echo off
title SAR Redaction Tool
setlocal EnableDelayedExpansion

set "PORT=8501"
set "PYTHON=%~dp0venv\Scripts\python.exe"
set "APP=%~dp0app.py"
set "BROWSER=%~dp0open_browser.py"

echo.
echo  ==========================================
echo   SAR Redaction Tool
echo  ==========================================
echo.

:: ── Ensure Tesseract is on the PATH ──────────────────────────
:: Check both 64-bit and 32-bit install locations
where tesseract >nul 2>&1
if errorlevel 1 (
    if exist "%ProgramFiles%\Tesseract-OCR\tesseract.exe" (
        set "PATH=%PATH%;%ProgramFiles%\Tesseract-OCR"
    ) else (
        if exist "%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe" (
            set "PATH=%PATH%;%ProgramFiles(x86)%\Tesseract-OCR"
        )
    )
)

:: ── Verify the virtual environment exists ────────────────────
if not exist "%PYTHON%" (
    echo  Virtual environment not found.
    echo  Please run INSTALL.bat first, then try again.
    pause
    exit /b 1
)

:: ── Ensure base Python DLL is findable (needed when launched via shortcut) ───
for /f "tokens=1,2,*" %%A in ('findstr /i "^home" "%~dp0venv\pyvenv.cfg" 2^>nul') do set "PYTHON_HOME=%%C"
if defined PYTHON_HOME set "PATH=%PYTHON_HOME%;%PATH%"

:: ── Check venv is usable; self-repair if base Python is inaccessible ─────────
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo  Venv base Python is inaccessible -- searching for a system Python to repair...
    set "REPAIR_PYTHON="
    :: Prefer system-wide paths (Program Files) accessible to all Windows users
    for %%P in (
        "%ProgramFiles%\Python313\python.exe"
        "%ProgramFiles%\Python312\python.exe"
        "%ProgramFiles%\Python311\python.exe"
        "%ProgramFiles%\Python310\python.exe"
        "C:\Python313\python.exe"
        "C:\Python312\python.exe"
    ) do (
        if exist %%P (
            if not defined REPAIR_PYTHON set "REPAIR_PYTHON=%%~P"
        )
    )
    :: Try py launcher as fallback
    if not defined REPAIR_PYTHON (
        where py >nul 2>&1
        if not errorlevel 1 (
            for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
                if not defined REPAIR_PYTHON (
                    echo "%%P" | findstr /i "WindowsApps" >nul 2>&1
                    if errorlevel 1 (
                        if exist "%%P" set "REPAIR_PYTHON=%%P"
                    )
                )
            )
        )
    )
    if not defined REPAIR_PYTHON (
        echo.
        echo  =====================================================
        echo   ACTION REQUIRED: Python not installed for all users
        echo  =====================================================
        echo.
        echo  Step 1: Find INSTALL.bat in the app folder:
        echo    %~dp0
        echo.
        echo  Step 2: Right-click INSTALL.bat
        echo          Select "Run as administrator"
        echo.
        echo  Step 3: When setup finishes, use the desktop
        echo          shortcut to launch the app.
        echo.
        pause
        exit /b 1
    )
    echo  Rebuilding environment with: %REPAIR_PYTHON%
    if exist "%~dp0venv" rd /s /q "%~dp0venv" >nul 2>&1
    "%REPAIR_PYTHON%" -m venv "%~dp0venv"
    if errorlevel 1 (
        echo  ERROR: Could not rebuild venv. Please re-run INSTALL.bat.
        pause
        exit /b 1
    )
    set "PYTHON=%~dp0venv\Scripts\python.exe"
    echo  Installing packages...
    "%PYTHON%" -m pip install --upgrade pip --quiet
    "%PYTHON%" -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo  ERROR: Package installation failed. Please re-run INSTALL.bat.
        pause
        exit /b 1
    )
    echo  Environment repaired successfully.
    echo.
)

:: ── Install packages if streamlit is missing ─────────────────
"%PYTHON%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo  Installing packages into venv...
    "%PYTHON%" -m pip install --upgrade pip --quiet
    "%PYTHON%" -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo  ERROR: Package installation failed.
        pause
        exit /b 1
    )
    echo  Packages installed.
    echo.
)

:: ── Free port %PORT% if already in use ───────────────────────
:: Filter to LISTENING rows only to avoid killing unrelated processes
for /f "tokens=5" %%a in (
    'netstat -aon 2^>nul ^| findstr /r ":%PORT%.*LISTENING"'
) do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: ── Start Ollama if not already running ──────────────────────
tasklist 2>nul | findstr /i "ollama.exe" >nul
if errorlevel 1 (
    echo  Starting Ollama AI engine...
    start /min "Ollama" cmd /c "ollama serve"
    timeout /t 6 /nobreak >nul
) else (
    echo  Ollama already running.
)

:: ── Start browser opener in background ───────────────────────
:: Pass port as argument so open_browser.py stays in sync with run.bat
start /b "" "%PYTHON%" "%BROWSER%" %PORT%

:: ── Launch Streamlit (blocking) ──────────────────────────────
echo  Starting app -- browser will open automatically...
echo  If the browser doesn't open, go to:  http://127.0.0.1:%PORT%
echo  To stop: press Ctrl+C or close this window
echo.
"%PYTHON%" -m streamlit run "%APP%" ^
    --server.port %PORT% ^
    --server.address 127.0.0.1 ^
    --server.headless true

:: ── Cleanup after Streamlit exits ────────────────────────────
echo.
echo  App stopped.
for /f "tokens=5" %%a in (
    'netstat -aon 2^>nul ^| findstr /r ":%PORT%.*LISTENING"'
) do (
    taskkill /f /pid %%a >nul 2>&1
)
pause
