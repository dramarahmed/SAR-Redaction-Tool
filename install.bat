@echo off
title SAR Redaction Tool - Setup
setlocal EnableDelayedExpansion

:: =============================================================
::  Self-elevate to Administrator if not already running as one
:: =============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  Requesting administrator privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo.
echo  ==========================================
echo   SAR Redaction Tool  --  Setup
echo  ==========================================
echo.
echo  This will install Python, Ollama, Tesseract and the AI model.
echo  Internet connection required.  Takes 10-30 minutes first time.
echo.

:: =============================================================
::  GPU / model tier selection
:: =============================================================
echo  -------------------------------------------------------
echo   What kind of computer is this?
echo.
echo    [1]  Basic / no dedicated GPU         (~5 GB,  slower)
echo    [2]  Dedicated GPU 6-8 GB VRAM        (~6 GB,  good)   qwen3.5:9b
echo    [3]  Dedicated GPU 8-12 GB VRAM       (~9 GB,  better) qwen2.5:14b
echo    [4]  High-end GPU 20+ GB VRAM         (~20 GB, best)   qwen2.5:32b
echo.
set "LLM_MODEL=qwen2.5:7b"
set /p "TIER=  Enter 1, 2, 3 or 4 (press Enter for 1): "
if "%TIER%"=="2" set "LLM_MODEL=qwen3.5:9b"
if "%TIER%"=="3" set "LLM_MODEL=qwen2.5:14b"
if "%TIER%"=="4" set "LLM_MODEL=qwen2.5:32b"
echo.
echo   Selected model: %LLM_MODEL%
echo  -------------------------------------------------------
echo.

:: Models go in Ollama's default location - no path to configure
set "OLLAMA_MODELS=%USERPROFILE%\.ollama\models"

:: =============================================================
::  Step 1: Python  (bypass Windows App Execution Alias)
:: =============================================================
echo  [1/6] Checking Python...

:: Search known install locations - ignore WindowsApps (Store alias)
set "PYTHON_EXE="
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
) do (
    if exist %%P (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%~P"
    )
)

if not defined PYTHON_EXE (
    echo        Not found.  Installing Python 3.12 via winget...
    winget install --id Python.Python.3.12 -e --silent ^
        --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo  ERROR: Could not install Python automatically.
        echo  Please install Python 3.10 or later from https://python.org
        echo  Tick "Add Python to PATH" during installation, then re-run this script.
        pause
        exit /b 1
    )
    :: winget installs to LOCALAPPDATA - set the path for this session
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

echo        Found: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

:: =============================================================
::  Step 2: Ollama
:: =============================================================
echo  [2/6] Checking Ollama...
where ollama >nul 2>&1
if errorlevel 1 (
    echo        Not found.  Installing Ollama via winget...
    winget install --id Ollama.Ollama -e --silent ^
        --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo  ERROR: Could not install Ollama automatically.
        echo  Please install from https://ollama.com then re-run this script.
        pause
        exit /b 1
    )
    timeout /t 5 /nobreak >nul
    :: Ollama installer adds itself to PATH but current session won't see it yet
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
)
ollama --version
echo.

:: =============================================================
::  Step 3: Tesseract OCR  (for image / scanned-PDF support)
:: =============================================================
echo  [3/6] Checking Tesseract OCR...
set "TESS_DEFAULT=C:\Program Files\Tesseract-OCR"
where tesseract >nul 2>&1
if errorlevel 1 (
    if exist "%TESS_DEFAULT%\tesseract.exe" (
        echo        Found at default path -- adding to PATH...
        setx PATH "%PATH%;%TESS_DEFAULT%" >nul 2>&1
        set "PATH=%PATH%;%TESS_DEFAULT%"
    ) else (
        echo        Not found.  Installing Tesseract OCR via winget...
        winget install -e --id UB-Mannheim.TesseractOCR --silent ^
            --accept-source-agreements --accept-package-agreements
        if errorlevel 1 (
            echo.
            echo  WARNING: Tesseract auto-install failed.
            echo  Download manually from:
            echo    https://github.com/UB-Mannheim/tesseract/wiki
            echo  Install to: %TESS_DEFAULT%
            echo  Then re-run this script.
            echo.
        ) else (
            if exist "%TESS_DEFAULT%\tesseract.exe" (
                setx PATH "%PATH%;%TESS_DEFAULT%" >nul 2>&1
                set "PATH=%PATH%;%TESS_DEFAULT%"
                echo        Tesseract installed and added to PATH.
            )
        )
    )
) else (
    echo        Tesseract already in PATH.
    tesseract --version 2>&1 | findstr /i "tesseract"
)
echo.

:: =============================================================
::  Step 4: Python virtual environment + packages
:: =============================================================
echo  [4/6] Setting up Python packages...
if not exist "%~dp0venv\Scripts\python.exe" (
    "%PYTHON_EXE%" -m venv "%~dp0venv"
    if errorlevel 1 (
        echo  ERROR: Could not create Python virtual environment.
        echo  Python used: %PYTHON_EXE%
        pause
        exit /b 1
    )
    echo        Created virtual environment.
) else (
    echo        Virtual environment already exists.
)
echo        Installing / updating packages (this may take a few minutes)...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo.
    echo  ERROR: Package installation failed.  Check your internet connection.
    pause
    exit /b 1
)
echo.

:: =============================================================
::  Step 5: Download AI model
:: =============================================================
echo  [5/6] Downloading AI model: %LLM_MODEL%
echo        This is a one-time download -- could take 10-30 minutes.
echo        Models stored in: %OLLAMA_MODELS%
echo.

:: Save chosen model so run.bat can use it
setx SAR_LLM_MODEL "%LLM_MODEL%" >nul 2>&1

:: Start Ollama serve in background so we can pull/check
tasklist 2>nul | findstr /i "ollama.exe" >nul
if errorlevel 1 (
    start /min "Ollama" cmd /c "ollama serve"
    timeout /t 6 /nobreak >nul
)

:: Check if model is already present before downloading
ollama list 2>nul | findstr /i "%LLM_MODEL%" >nul
if errorlevel 1 (
    echo        Model not found locally.  Downloading now...
    ollama pull %LLM_MODEL%
    if errorlevel 1 (
        echo.
        echo  WARNING: Model pull failed.  Check your internet connection.
        echo  You can pull it manually later with:
        echo    ollama pull %LLM_MODEL%
        echo.
    )
) else (
    echo        Model already downloaded -- skipping.
)
echo.

:: =============================================================
::  Step 6: Desktop shortcut
:: =============================================================
echo  [6/6] Creating desktop shortcut...
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\SAR Redaction Tool.lnk'); $lnk.TargetPath = '%~dp0run.bat'; $lnk.WorkingDirectory = '%~dp0'; $lnk.IconLocation = 'shell32.dll,23'; $lnk.Description = 'SAR Redaction Tool'; $lnk.Save()"
echo        Shortcut created on Desktop.
echo.

:: =============================================================
::  Done
:: =============================================================
echo  ==========================================
echo   Setup complete!
echo  ==========================================
echo.
echo   Model     : %LLM_MODEL%
echo   Shortcut  : Desktop  ^>  "SAR Redaction Tool"
echo.
echo   To launch the app, double-click the desktop shortcut.
echo   To stop the app,  close the black console window that appears.
echo.
pause
