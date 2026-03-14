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
set "TESS_DEFAULT=C:\Program Files\Tesseract-OCR"
where tesseract >nul 2>&1
if errorlevel 1 (
    if exist "%TESS_DEFAULT%\tesseract.exe" (
        set "PATH=%PATH%;%TESS_DEFAULT%"
    )
)

:: ── Verify the virtual environment exists ────────────────────
if not exist "%PYTHON%" (
    echo  Virtual environment not found.
    echo  Please run INSTALL.bat first, then try again.
    pause
    exit /b 1
)

:: ── Install packages if streamlit is missing ─────────────────
"%PYTHON%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo  Installing packages into venv...
    "%~dp0venv\Scripts\pip.exe" install --upgrade pip --quiet
    "%~dp0venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo  ERROR: Package installation failed.
        pause
        exit /b 1
    )
    echo  Packages installed.
    echo.
)

:: ── Free port %PORT% if already in use ───────────────────────
for /f "tokens=5" %%a in (
    'netstat -aon 2^>nul ^| findstr /r ":%PORT% "'
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
start /b "" "%PYTHON%" "%BROWSER%"

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
    'netstat -aon 2^>nul ^| findstr /r ":%PORT% "'
) do (
    taskkill /f /pid %%a >nul 2>&1
)
pause
