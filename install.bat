@echo off
title SAR Redaction Tool - Setup
setlocal EnableDelayedExpansion

:: =============================================================
::  Self-elevate to Administrator if not already running as one
:: =============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  Requesting administrator privileges...
    powershell -NoProfile -Command "Start-Process -FilePath \"%~f0\" -Verb RunAs -WorkingDirectory \"%~dp0\""
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

:: =============================================================
::  Step 1: Python  (bypass Windows App Execution Alias)
:: =============================================================
echo  [1/6] Checking Python...

:: Try Windows Python Launcher first -- handles any installed version
set "PYTHON_EXE="
where py >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
        if not defined PYTHON_EXE (
            echo "%%P" | findstr /i "WindowsApps" >nul 2>&1
            if errorlevel 1 set "PYTHON_EXE=%%P"
        )
    )
)

:: Fall back to known install locations
:: Check system-wide paths FIRST -- these are accessible to all Windows users.
:: User-scoped paths (LOCALAPPDATA) are checked last because they are only
:: accessible to the specific user who installed them.
if not defined PYTHON_EXE (
    for %%P in (
        "%ProgramFiles%\Python313\python.exe"
        "%ProgramFiles%\Python312\python.exe"
        "%ProgramFiles%\Python311\python.exe"
        "%ProgramFiles%\Python310\python.exe"
        "C:\Python313\python.exe"
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
        "C:\Python310\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    ) do (
        if exist %%P (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%~P"
        )
    )
)

if not defined PYTHON_EXE (
    echo        Not found.  Checking for winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  ERROR: Python not found and winget is not available on this PC.
        echo  Please install Python 3.10 or later from https://python.org
        echo  Tick "Add Python to PATH" during installation, then re-run this script.
        echo.
        pause
        exit /b 1
    )
    echo        Installing Python 3.12 for all users via winget...
    :: --scope machine  = installs to C:\Program Files\Python312 (all users)
    :: --force          = installs even if a per-user version already exists
    winget install --id Python.Python.3.12 -e --silent --scope machine --force --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo  ERROR: Could not install Python automatically.
        echo  Please install Python 3.12 from https://python.org
        echo  On the installer, tick "Install for all users" and "Add Python to PATH",
        echo  then re-run this script.
        pause
        exit /b 1
    )
    :: Add both machine-scope and user-scope paths for this session
    set "PATH=%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    :: Re-detect -- prefer machine-scope (Program Files) over user-scope
    where py >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
            if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
        )
    )
    if not defined PYTHON_EXE (
        for %%P in (
            "%ProgramFiles%\Python312\python.exe"
            "%ProgramFiles%\Python313\python.exe"
            "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
            "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        ) do (
            if exist %%P (
                if not defined PYTHON_EXE set "PYTHON_EXE=%%~P"
            )
        )
    )
    if not defined PYTHON_EXE (
        echo.
        echo  ERROR: Python was installed but could not be located.
        echo  Please restart this script, or install Python manually from https://python.org
        pause
        exit /b 1
    )
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
    echo        Not found.  Checking for winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo.
        echo  ERROR: Ollama not found and winget is not available on this PC.
        echo  Please install Ollama from https://ollama.com then re-run this script.
        echo.
        pause
        exit /b 1
    )
    echo        Installing Ollama via winget...
    winget install --id Ollama.Ollama -e --silent --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo.
        echo  ERROR: Could not install Ollama automatically.
        echo  Please install from https://ollama.com then re-run this script.
        pause
        exit /b 1
    )
    :: Ollama installer adds itself to PATH but current session won't see it yet
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    :: Ollama installer is async -- wait for the binary to appear on disk
    echo        Waiting for Ollama to finish installing...
    timeout /t 10 /nobreak >nul
    where ollama >nul 2>&1
    if errorlevel 1 (
        echo  WARNING: Ollama may not have finished installing yet.
        echo  If the next steps fail, close this window and re-run INSTALL.bat.
        echo.
    )
)
ollama --version
echo.

:: =============================================================
::  Step 3: Tesseract OCR  (for image / scanned-PDF support)
:: =============================================================
echo  [3/6] Checking Tesseract OCR...
set "TESS_DEFAULT=%ProgramFiles%\Tesseract-OCR"
set "TESS_X86=%ProgramFiles(x86)%\Tesseract-OCR"
where tesseract >nul 2>&1
if errorlevel 1 (
    if exist "%TESS_DEFAULT%\tesseract.exe" (
        echo        Found at default path -- adding to PATH...
        :: Use PowerShell to append to Machine PATH safely (avoids setx 1024-char limit)
        powershell -NoProfile -Command "$p=[Environment]::GetEnvironmentVariable('PATH','Machine'); if ($p -notlike '*Tesseract-OCR*') { [Environment]::SetEnvironmentVariable('PATH',$p+';%TESS_DEFAULT%','Machine') }" >nul 2>&1
        set "PATH=%PATH%;%TESS_DEFAULT%"
    ) else (
        if exist "%TESS_X86%\tesseract.exe" (
            echo        Found at 32-bit path -- adding to PATH...
            powershell -NoProfile -Command "$p=[Environment]::GetEnvironmentVariable('PATH','Machine'); if ($p -notlike '*Tesseract-OCR*') { [Environment]::SetEnvironmentVariable('PATH',$p+';%TESS_X86%','Machine') }" >nul 2>&1
            set "PATH=%PATH%;%TESS_X86%"
        ) else (
            echo        Not found.  Installing Tesseract OCR via winget...
            where winget >nul 2>&1
            if errorlevel 1 (
                echo  WARNING: winget not available.  Tesseract OCR could not be installed automatically.
                echo  Download manually from:
                echo    https://github.com/UB-Mannheim/tesseract/wiki
                echo  Install to: %TESS_DEFAULT%
                echo  Then re-run this script.
                echo.
            ) else (
                winget install -e --id UB-Mannheim.TesseractOCR --silent --accept-source-agreements --accept-package-agreements
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
                        powershell -NoProfile -Command "$p=[Environment]::GetEnvironmentVariable('PATH','Machine'); if ($p -notlike '*Tesseract-OCR*') { [Environment]::SetEnvironmentVariable('PATH',$p+';%TESS_DEFAULT%','Machine') }" >nul 2>&1
                        set "PATH=%PATH%;%TESS_DEFAULT%"
                        echo        Tesseract installed and added to PATH.
                    )
                )
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
:: If the venv exists but its base Python is inaccessible (e.g. installed for
:: a different Windows user), delete it so we can rebuild with the correct Python.
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo        Existing venv is broken (base Python not accessible^) -- rebuilding...
        rd /s /q "%~dp0venv" >nul 2>&1
    )
)
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
echo.

:: Start Ollama serve in background so we can pull/check
tasklist 2>nul | findstr /i "ollama.exe" >nul
if errorlevel 1 (
    start /min "Ollama" cmd /c "ollama serve"
    timeout /t 6 /nobreak >nul
)

:: Check if model is already present before downloading
:: Use trailing space to avoid substring matches (e.g. qwen2.5:7b vs qwen2.5:72b)
ollama list 2>nul | findstr /i /c:"%LLM_MODEL% " >nul
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
if errorlevel 1 (
    echo  WARNING: Could not create desktop shortcut automatically.
    echo  To launch manually: right-click run.bat ^> Send to ^> Desktop (create shortcut^)
) else (
    echo        Shortcut created on Desktop.
)
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
