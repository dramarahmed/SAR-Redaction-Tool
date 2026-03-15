#Requires -Version 5.1
<#
.SYNOPSIS
    SAR Redaction Tool — one-time setup script.

.DESCRIPTION
    Right-click this file and choose "Run with PowerShell".
    The script will:
      1. Install Python 3.11 (if not already installed)
      2. Install Ollama     (if not already installed)
      3. Create a Python virtual environment and install dependencies
      4. Download the qwen2.5:14b language model (~9 GB — only on first run)
      5. Create a "SAR Redaction Tool" shortcut on your Desktop

    After setup completes, use the Desktop shortcut to launch the app.
    The app opens automatically in your web browser.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Helpers ──────────────────────────────────────────────────────────────────

function Write-Header($msg) {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Write-Step($msg)    { Write-Host "  >> $msg" -ForegroundColor Yellow }
function Write-OK($msg)      { Write-Host "  OK  $msg" -ForegroundColor Green  }
function Write-Info($msg)    { Write-Host "      $msg" -ForegroundColor Gray   }
function Abort($msg) {
    Write-Host ""
    Write-Host "  ERROR: $msg" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# ── Script root ───────────────────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║      SAR Redaction Tool — Setup          ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  This will set up everything needed to run the tool." -ForegroundColor White
Write-Host "  The AI model download is ~9 GB — please be on a good" -ForegroundColor White
Write-Host "  connection and allow 10-30 minutes on first run." -ForegroundColor White

# ── 1. Python ─────────────────────────────────────────────────────────────────
Write-Header "Step 1/4 — Python"

$pythonCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]; $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 9) {
                $pythonCmd = $candidate
                Write-OK "Found $ver"
                break
            }
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Step "Python 3.9+ not found — installing Python 3.11 via winget..."
    try {
        winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path","User")
        $pythonCmd = "python"
        Write-OK "Python installed."
    } catch {
        Abort "Could not install Python automatically.`n      Please install Python 3.11 from https://www.python.org/downloads/ and re-run this script."
    }
}

# ── 2. Ollama ─────────────────────────────────────────────────────────────────
Write-Header "Step 2/4 — Ollama (local AI runtime)"

$ollamaInstalled = $false
try {
    $null = & ollama --version 2>&1
    $ollamaInstalled = $true
    Write-OK "Ollama is already installed."
} catch { }

if (-not $ollamaInstalled) {
    Write-Step "Ollama not found — installing via winget..."
    try {
        winget install --id Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-OK "Ollama installed."
    } catch {
        Abort "Could not install Ollama automatically.`n      Please install it from https://ollama.com/download and re-run this script."
    }
}

# ── 3. Python virtual environment + dependencies ──────────────────────────────
Write-Header "Step 3/4 — Python dependencies"

$venvDir = Join-Path $ScriptDir "venv"
$venvPy  = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"

if (-not (Test-Path $venvPy)) {
    Write-Step "Creating virtual environment..."
    & $pythonCmd -m venv $venvDir
    Write-OK "Virtual environment created."
} else {
    Write-OK "Virtual environment already exists."
}

Write-Step "Installing/updating dependencies (this may take a few minutes)..."
& $venvPip install --upgrade pip --quiet
& $venvPip install -r (Join-Path $ScriptDir "requirements.txt") --quiet
Write-OK "Dependencies installed."

# ── 4. AI model ───────────────────────────────────────────────────────────────
Write-Header "Step 4/4 — AI model (qwen2.5:14b, ~9 GB)"

# Check if model already exists
$modelExists = $false
try {
    $models = & ollama list 2>&1
    if ($models -match "qwen2\.5:14b") { $modelExists = $true }
} catch { }

if ($modelExists) {
    Write-OK "Model qwen2.5:14b already downloaded."
} else {
    Write-Step "Downloading qwen2.5:14b — this will take a while..."
    Write-Info "(You can see progress below. Do not close this window.)"
    Write-Host ""
    # Start Ollama service first (needed on Windows before pull)
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    & ollama pull qwen2.5:14b
    if ($LASTEXITCODE -ne 0) {
        Abort "Model download failed. Check your internet connection and re-run this script."
    }
    Write-OK "Model downloaded successfully."
}

# ── Create launch script ──────────────────────────────────────────────────────
$launchScript = Join-Path $ScriptDir "launch.bat"
@"
@echo off
cd /d "%~dp0"
start "" http://localhost:8501
call venv\Scripts\activate.bat
streamlit run app.py --server.headless true
"@ | Set-Content -Path $launchScript -Encoding ASCII

# ── Create Desktop shortcut ───────────────────────────────────────────────────
Write-Step "Creating Desktop shortcut..."
$desktopPath  = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "SAR Redaction Tool.lnk"
$iconPath     = Join-Path $ScriptDir "logo.ico"

$wsh      = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath       = $launchScript
$shortcut.WorkingDirectory = $ScriptDir
$shortcut.Description      = "SAR Redaction Tool"
if (Test-Path $iconPath) { $shortcut.IconLocation = $iconPath }
$shortcut.Save()

Write-OK "Shortcut created on Desktop."

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║         Setup complete!                  ║" -ForegroundColor Green
Write-Host "  ║                                          ║" -ForegroundColor Green
Write-Host "  ║  Double-click 'SAR Redaction Tool'       ║" -ForegroundColor Green
Write-Host "  ║  on your Desktop to launch the app.      ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
