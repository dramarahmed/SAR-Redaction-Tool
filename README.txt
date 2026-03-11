══════════════════════════════════════════════════════════════════
  SAR Redaction Tool  —  README & Setup Instructions
══════════════════════════════════════════════════════════════════

IMPORTANT — PLEASE READ BEFORE USE
────────────────────────────────────────────────────────────────
This tool is provided as a DECISION-SUPPORT AID only.

• All AI-generated redaction suggestions MUST be reviewed and
  approved by a human before any document is finalised.

• This software is NOT a medical device and has NOT been
  clinically validated or approved by any regulatory body.

• The AI model runs ENTIRELY on your local computer.  No patient
  data is sent to the internet, to Anthropic, to the NHS or to
  any third party at any point.

• The developers accept no liability for redaction errors,
  missed identifiers, or any consequences arising from the use
  of this tool.  The clinician or Information Governance officer
  reviewing the output bears sole responsibility for the
  accuracy and completeness of redaction.

• This tool is intended for use within NHS organisations that
  have appropriate Information Governance agreements in place
  for the use of local AI tools.

SYSTEM REQUIREMENTS
────────────────────────────────────────────────────────────────
  • Windows 10 or 11 (64-bit)
  • At least 8 GB RAM (16 GB recommended)
  • At least 15 GB free disk space for the AI model
  • Internet connection for first-time setup only
  • Administrator rights on the PC (needed for install only)

  GPU is optional but speeds up AI processing significantly:
    No GPU / integrated  →  choose option 1 at setup (qwen2.5:7b,  ~5 GB)
    6–8 GB VRAM GPU      →  choose option 2 at setup (qwen3.5:9b,  ~6 GB)
    8–12 GB VRAM GPU     →  choose option 3 at setup (qwen2.5:14b, ~9 GB)
    20+ GB VRAM GPU      →  choose option 4 at setup (qwen2.5:32b, ~20 GB)

SETUP — STEP BY STEP
────────────────────────────────────────────────────────────────
  1.  Extract this ZIP to a permanent folder, e.g.:
        C:\SAR_Redaction\

  2.  Right-click  INSTALL.bat  and choose
      "Run as administrator"

  3.  When asked about your computer type, enter 1, 2, 3 or 4
      and press Enter.  The installer handles everything else.

      ⚠  The AI model download is 5–20 GB.
         Leave the window open until it says "Setup complete!"

  4.  Double-click the  "SAR Redaction Tool"  shortcut on your
      Desktop.  The app opens in your web browser automatically.

  FIRST LAUNCH may take 30–60 seconds while Ollama loads the
  AI model into memory.  Subsequent launches are faster.

DAILY USE
────────────────────────────────────────────────────────────────
  • Double-click the desktop shortcut to start.
  • Upload PDFs, Word documents, TIFF or image scans.
  • Fill in the patient name and SAR received date in the sidebar.
  • Click "Analyse" and wait for the AI to suggest redactions.
  • Review EVERY suggested redaction before approving.
  • Click "Apply approved redactions & download" to get the
    redacted PDF.

  To stop the app: close the black console window that appears
  when you launch.

TROUBLESHOOTING
────────────────────────────────────────────────────────────────
  "Ollama not found" or app won't start:
    → Close and re-open the desktop shortcut.

  Browser doesn't open automatically:
    → Go to  http://127.0.0.1:8501  in your browser manually.

  Analysis seems stuck / frozen:
    → Each chunk of text allows up to 2 minutes for the AI.
      A large document may take several minutes.  Wait for it.

  Very slow analysis (no GPU):
    → This is normal.  The 7b model on CPU takes 2–5 min per
      document chunk.  Upgrade to a PC with a dedicated GPU
      for significantly faster processing.

  Re-run setup after a Windows reinstall:
    → Run  INSTALL.bat  again as administrator.
      Your AI model will NOT need to be re-downloaded if the
      user profile folder (%USERPROFILE%) is the same drive.

PRIVACY & DATA HANDLING
────────────────────────────────────────────────────────────────
  • The AI (Ollama + qwen2.5) runs 100% locally on this machine.
  • No document content, patient data or results are transmitted
    over the network at any point during normal use.
  • Uploaded files are held in browser memory only and are not
    written to disk by the app (except the final redacted output
    you explicitly download).
  • Redacted output files are saved to the location you choose
    when downloading.

VERSION
────────────────────────────────────────────────────────────────
  Tool version  : 1.0
  Requires      : Python 3.10+, Ollama 0.1.7+

══════════════════════════════════════════════════════════════════
