; ============================================================
;  installer.iss  --  SAR Redaction Tool
;  Compile with Inno Setup 6.x  (https://jrsoftware.org/isinfo.php)
;
;  To build:  run build_installer.bat  (or open this file in
;             the Inno Setup Compiler and press F9)
; ============================================================

#define AppName    "SAR Redaction Tool"
#define AppVersion "1.0"
#define AppPublisher "NHS Surgery AI"
[Setup]
AppId={{8F3A1B2C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppVerName={#AppName} {#AppVersion}

; Install to "C:\Program Files\SAR Redaction Tool\" by default
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}

; Output
OutputDir=.
OutputBaseFilename=SAR_Redaction_Tool_Setup

; Always require admin  (needs to install Python / Ollama system-wide)
PrivilegesRequired=admin

; UI
WizardStyle=modern
DisableProgramGroupPage=yes
DisableDirPage=no

; Compression
Compression=lzma2
SolidCompression=yes

; Uninstall
UninstallDisplayName={#AppName}
UninstallDisplayIcon={sys}\shell32.dll,23

; Minimum Windows 10
MinVersion=10.0

; 64-bit only
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ── Files to install ─────────────────────────────────────────────────────────
[Files]
Source: "app.py";            DestDir: "{app}"; Flags: ignoreversion
Source: "run.bat";           DestDir: "{app}"; Flags: ignoreversion
Source: "open_browser.py";   DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt";  DestDir: "{app}"; Flags: ignoreversion
Source: "logo.jpg";          DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt";        DestDir: "{app}"; Flags: ignoreversion isreadme

; install_deps.bat is only needed during setup -- delete it afterwards
Source: "install_deps.bat";  DestDir: "{app}"; Flags: ignoreversion deleteafterinstall

; ── Shortcuts ────────────────────────────────────────────────────────────────
[Icons]
; Public desktop (visible to all users on this PC)
Name: "{commondesktop}\{#AppName}";         Filename: "{app}\run.bat";  WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 23; Comment: "Launch SAR Redaction Tool"
; Start Menu
Name: "{group}\{#AppName}";                 Filename: "{app}\run.bat";  WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 23
Name: "{group}\Uninstall {#AppName}";       Filename: "{uninstallexe}"

; ── Run dependency installer after files are copied ──────────────────────────
[Run]
Filename: "{app}\install_deps.bat"; \
    Parameters: "{code:GetSelectedTier}"; \
    Flags: waituntilterminated; \
    StatusMsg: "Installing Python, Ollama, Tesseract and AI model (may take 10-30 min)..."; \
    Description: "Install all dependencies and download AI model"

; ── Remove generated folders on uninstall ────────────────────────────────────
[UninstallDelete]
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\__pycache__"

; ── Pascal code: custom GPU tier selection wizard page ───────────────────────
[Code]

var
  TierPage:   TWizardPage;
  RBasic:     TRadioButton;
  RGood:      TRadioButton;
  RBetter:    TRadioButton;
  RBest:      TRadioButton;

procedure InitializeWizard;
var
  TopLbl, WarnLbl: TLabel;
begin
  // Insert the tier page just before the "Ready to install" page
  TierPage := CreateCustomPage(
    wpReady,
    'GPU / Performance Selection',
    'Choose the option that matches this computer''s graphics card.'
  );

  TopLbl := TLabel.Create(TierPage);
  with TopLbl do
  begin
    Parent  := TierPage.Surface;
    Left    := 0;
    Top     := 0;
    Width   := TierPage.SurfaceWidth;
    Height  := 30;
    AutoSize := False;
    WordWrap := True;
    Caption := 'This controls which AI model is downloaded. If unsure, choose option 1.';
  end;

  RBasic := TRadioButton.Create(TierPage);
  with RBasic do
  begin
    Parent  := TierPage.Surface;
    Left    := 8;
    Top     := 38;
    Width   := TierPage.SurfaceWidth - 8;
    Caption := '1  Basic / no dedicated GPU  —  qwen2.5:7b  (~5 GB,  slower)';
    Checked := True;
  end;

  RGood := TRadioButton.Create(TierPage);
  with RGood do
  begin
    Parent  := TierPage.Surface;
    Left    := 8;
    Top     := 66;
    Width   := TierPage.SurfaceWidth - 8;
    Caption := '2  Dedicated GPU 6–8 GB VRAM  —  qwen3.5:9b   (~6 GB,  good)';
  end;

  RBetter := TRadioButton.Create(TierPage);
  with RBetter do
  begin
    Parent  := TierPage.Surface;
    Left    := 8;
    Top     := 94;
    Width   := TierPage.SurfaceWidth - 8;
    Caption := '3  Dedicated GPU 8–12 GB VRAM  —  qwen2.5:14b  (~9 GB,  better)';
  end;

  RBest := TRadioButton.Create(TierPage);
  with RBest do
  begin
    Parent  := TierPage.Surface;
    Left    := 8;
    Top     := 122;
    Width   := TierPage.SurfaceWidth - 8;
    Caption := '4  High-end GPU 20+ GB VRAM  —  qwen2.5:32b  (~20 GB, best)';
  end;

  WarnLbl := TLabel.Create(TierPage);
  with WarnLbl do
  begin
    Parent   := TierPage.Surface;
    Left     := 0;
    Top      := 162;
    Width    := TierPage.SurfaceWidth;
    Height   := 52;
    AutoSize := False;
    WordWrap := True;
    Font.Style := [fsBold];
    Caption :=
      'The AI model download is 5-20 GB and may take 10-30 minutes.' + #13#10 +
      'Keep the computer connected to the internet and do not close' + #13#10 +
      'the console window that opens during installation.';
  end;
end;

// Returns the tier number as a string, passed to install_deps.bat
function GetSelectedTier(Param: String): String;
begin
  if RBest.Checked   then Result := '4'
  else if RBetter.Checked then Result := '3'
  else if RGood.Checked   then Result := '2'
  else                          Result := '1';
end;
