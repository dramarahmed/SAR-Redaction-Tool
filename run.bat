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
if defined PYTHON_HOME if exist "%PYTHON_HOME%\python.exe" set "PATH=%PYTHON_HOME%;%PATH%"

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
