@echo off
:: ============================================================
::  install_deps.bat  --  called by the Inno Setup installer
::  Usage:  install_deps.bat <tier>
::    tier 1 = Basic / no GPU       qwen2.5:7b
::    tier 2 = 6-8 GB VRAM GPU      qwen3.5:9b
::    tier 3 = 8-12 GB VRAM GPU     qwen2.5:14b
::    tier 4 = 20+ GB VRAM GPU      qwen2.5:32b
::
::  Assumes it is already running with Administrator rights
::  (the Inno Setup installer requires admin).
::  Does NOT self-elevate and does NOT pause at the end.
:: ============================================================
title SAR Redaction Tool - Installing Dependencies
setlocal EnableDelayedExpansion

:: ── Tier / model selection ────────────────────────────────
set "TIER=%~1"
if "%TIER%"=="" set "TIER=1"

set "LLM_MODEL=qwen2.5:7b"
if "%TIER%"=="2" set "LLM_MODEL=qwen3.5:9b"
if "%TIER%"=="3" set "LLM_MODEL=qwen2.5:14b"
if "%TIER%"=="4" set "LLM_MODEL=qwen2.5:32b"

echo.
echo  ==========================================
echo   SAR Redaction Tool  --  Dependency Setup
echo   AI model: %LLM_MODEL%
echo  ==========================================
echo.

:: ── Step 1: Python ────────────────────────────────────────
echo  [1/5] Checking Python...

set "PYTHON_EXE="

:: Prefer system-wide (Program Files) paths -- accessible to ALL Windows users
for %%P in (
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%P (
        if not defined PYTHON_EXE (
            %%P --version >nul 2>&1
            if not errorlevel 1 set "PYTHON_EXE=%%~P"
        )
    )
)

:: Fall back to py launcher (may find any installed version)
if not defined PYTHON_EXE (
    where py >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
            if not defined PYTHON_EXE (
                echo "%%P" | findstr /i "WindowsApps" >nul 2>&1
                if errorlevel 1 (
                    if exist "%%P" (
                        "%%P" --version >nul 2>&1
                        if not errorlevel 1 set "PYTHON_EXE=%%P"
                    )
                )
            )
        )
    )
)

if not defined PYTHON_EXE (
    echo        Not found.  Installing Python 3.12 for all users via winget...
    winget install --id Python.Python.3.12 -e --scope machine ^
        --override "/quiet InstallAllUsers=1 PrependPath=1 Include_launcher=1" ^
        --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo  ERROR: Could not install Python automatically.
        echo  Please install Python 3.12 from https://python.org
        echo  Tick "Install for all users" and "Add to PATH", then re-run setup.
        exit /b 1
    )
    set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
    if exist "%ProgramFiles%\Python312\python.exe" set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
    if not defined PYTHON_EXE (
        echo  ERROR: Python was installed but could not be located.
        exit /b 1
    )
)

echo        Found: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

:: ── Step 2: Ollama ────────────────────────────────────────
echo  [2/5] Checking Ollama...
where ollama >nul 2>&1
if errorlevel 1 (
    echo        Not found.  Installing Ollama via winget...
    winget install --id Ollama.Ollama -e --silent ^
        --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo  ERROR: Could not install Ollama automatically.
        echo  Please install from https://ollama.com then re-run setup.
        exit /b 1
    )
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    echo        Waiting for Ollama installer to finish...
    timeout /t 10 /nobreak >nul
) else (
    ollama --version
)
echo.

:: ── Step 3: Tesseract OCR ─────────────────────────────────
echo  [3/5] Checking Tesseract OCR...
set "TESS_DEFAULT=%ProgramFiles%\Tesseract-OCR"
set "TESS_X86=%ProgramFiles(x86)%\Tesseract-OCR"
where tesseract >nul 2>&1
if errorlevel 1 (
    if exist "%TESS_DEFAULT%\tesseract.exe" (
        echo        Found -- adding to Machine PATH...
        powershell -NoProfile -Command ^
            "$p=[Environment]::GetEnvironmentVariable('PATH','Machine'); if ($p -notlike '*Tesseract*') { [Environment]::SetEnvironmentVariable('PATH',$p+';%TESS_DEFAULT%','Machine') }" >nul 2>&1
        set "PATH=%PATH%;%TESS_DEFAULT%"
    ) else if exist "%TESS_X86%\tesseract.exe" (
        echo        Found (32-bit) -- adding to Machine PATH...
        powershell -NoProfile -Command ^
            "$p=[Environment]::GetEnvironmentVariable('PATH','Machine'); if ($p -notlike '*Tesseract*') { [Environment]::SetEnvironmentVariable('PATH',$p+';%TESS_X86%','Machine') }" >nul 2>&1
        set "PATH=%PATH%;%TESS_X86%"
    ) else (
        echo        Not found.  Installing via winget...
        winget install -e --id UB-Mannheim.TesseractOCR --silent ^
            --accept-source-agreements --accept-package-agreements
        if errorlevel 1 (
            echo  WARNING: Tesseract auto-install failed.
            echo  Download from https://github.com/UB-Mannheim/tesseract/wiki
            echo  Install to: %TESS_DEFAULT%  then re-run setup.
        ) else (
            if exist "%TESS_DEFAULT%\tesseract.exe" (
                powershell -NoProfile -Command ^
                    "$p=[Environment]::GetEnvironmentVariable('PATH','Machine'); if ($p -notlike '*Tesseract*') { [Environment]::SetEnvironmentVariable('PATH',$p+';%TESS_DEFAULT%','Machine') }" >nul 2>&1
                set "PATH=%PATH%;%TESS_DEFAULT%"
                echo        Tesseract installed.
            )
        )
    )
) else (
    echo        Already installed.
    tesseract --version 2>&1 | findstr /i "tesseract"
)
echo.

:: ── Step 4: Python virtual environment + packages ─────────
echo  [4/5] Setting up Python virtual environment...

:: If venv exists but its base Python is broken, delete and rebuild
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo        Existing venv is broken -- rebuilding...
        rd /s /q "%~dp0venv" >nul 2>&1
    )
)

if not exist "%~dp0venv\Scripts\python.exe" (
    "%PYTHON_EXE%" -m venv "%~dp0venv"
    if errorlevel 1 (
        echo  ERROR: Could not create virtual environment.
        echo  Python used: %PYTHON_EXE%
        exit /b 1
    )
    echo        Virtual environment created.
) else (
    echo        Virtual environment already exists.
)

echo        Installing packages (may take a few minutes)...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo  ERROR: Package installation failed.  Check internet connection.
    exit /b 1
)
echo.

:: ── Step 5: Download AI model ─────────────────────────────
echo  [5/5] Downloading AI model: %LLM_MODEL%
echo        This is a one-time download -- may take 10-30 minutes.
echo.

:: Start Ollama if not already running
tasklist 2>nul | findstr /i "ollama.exe" >nul
if errorlevel 1 (
    start /min "Ollama" cmd /c "ollama serve"
    timeout /t 6 /nobreak >nul
)

:: Only download if not already present
ollama list 2>nul | findstr /i /c:"%LLM_MODEL% " >nul
if errorlevel 1 (
    echo        Downloading now -- do not close this window...
    ollama pull %LLM_MODEL%
    if errorlevel 1 (
        echo.
        echo  WARNING: Model download failed.  Check internet connection.
        echo  You can pull it manually later:  ollama pull %LLM_MODEL%
        echo.
    )
) else (
    echo        Model already downloaded -- skipping.
)
echo.

echo  ==========================================
echo   Dependencies installed successfully!
echo  ==========================================
echo.
echo   Model : %LLM_MODEL%
echo   Use the desktop shortcut to launch the app.
echo.
