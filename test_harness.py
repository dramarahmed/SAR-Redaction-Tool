"""
test_harness.py
===============
Standalone automated test harness that processes all 5 test ZIPs through
the SAR redaction engine and produces a detailed JSON report.
"""

import argparse
import json
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# ---------------------------------------------------------------------------
# Import redaction_core from the project
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from redaction_core import (
    llm_analyse_document,
    _expand_name_redactions,
    apply_text_redactions,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ZIP_DIR = r"C:\Users\Amar Ahmed\Downloads"
ZIP_PATTERN = "Test-*-v2.zip"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.json")
DOC_TIMEOUT = 180  # seconds per document

# Try qwen2.5:14b first, fall back to qwen2.5
MODEL_PRIMARY = "qwen2.5:14b"
MODEL_FALLBACK = "qwen2.5"


def _select_model() -> str:
    """Pick the best available model."""
    import ollama
    try:
        models = ollama.list()
        available = {m.model for m in models.models} if hasattr(models, 'models') else set()
        # Also check without tag
        available_base = set()
        for name in available:
            available_base.add(name)
            if ":" in name:
                available_base.add(name.split(":")[0])
        if MODEL_PRIMARY in available_base:
            print(f"[MODEL] Using {MODEL_PRIMARY}")
            return MODEL_PRIMARY
        if MODEL_FALLBACK in available_base:
            print(f"[MODEL] {MODEL_PRIMARY} not found, falling back to {MODEL_FALLBACK}")
            return MODEL_FALLBACK
        # If neither exact match, check partial
        for name in available:
            if "qwen2.5" in name and "14b" in name:
                print(f"[MODEL] Using {name}")
                return name
        for name in available:
            if "qwen2.5" in name:
                print(f"[MODEL] Falling back to {name}")
                return name
        print(f"[MODEL] No qwen2.5 variant found in {available}, trying {MODEL_PRIMARY} anyway")
        return MODEL_PRIMARY
    except Exception as e:
        print(f"[MODEL] Could not list models ({e}), defaulting to {MODEL_PRIMARY}")
        return MODEL_PRIMARY


def _patient_name_filter(proposed: list, patient_name: str) -> list:
    """
    Remove proposed redactions whose text matches the patient name or any
    token of it. Mirrors the logic in app.py.
    """
    if not patient_name.strip():
        return proposed
    pn_lower = patient_name.strip().lower()
    pn_tokens = {tok.lower() for tok in pn_lower.split() if len(tok) >= 3}
    return [
        p for p in proposed
        if pn_lower not in p["text"].lower()
        and p["text"].lower() not in pn_lower
        and p["text"].lower() not in pn_tokens
    ]


def _process_document(text: str, model: str, patient_name: str, filename: str) -> dict:
    """Process a single document through the redaction engine. Returns a result dict."""
    print(f"    Processing: {filename} ({len(text)} chars) ...", flush=True)
    t0 = time.time()

    try:
        # Run LLM analysis with timeout via ThreadPoolExecutor
        def _run():
            return llm_analyse_document(text, model, patient_name)

        with ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(_run)
            try:
                result, raw = future.result(timeout=DOC_TIMEOUT)
            except FuturesTimeoutError:
                elapsed = time.time() - t0
                print(f"      TIMEOUT after {elapsed:.1f}s", flush=True)
                return {
                    "filename": filename,
                    "proposed_redactions": [],
                    "escalations": [],
                    "redacted_text": text,
                    "original_text": text,
                    "error": f"Timeout after {elapsed:.1f}s",
                }

        proposed = result.get("proposed_redactions", [])
        escalations = result.get("escalations", [])

        # Expand name redactions
        proposed = _expand_name_redactions(proposed, text, patient_name)

        # Patient name token filter
        proposed = _patient_name_filter(proposed, patient_name)

        # Mark all as approved for apply_text_redactions
        for p in proposed:
            p["approved"] = True

        # Apply redactions
        redacted_text = apply_text_redactions(text, proposed)

        elapsed = time.time() - t0
        print(f"      Done in {elapsed:.1f}s — {len(proposed)} redactions, {len(escalations)} escalations", flush=True)

        # Serialise redactions (strip non-serialisable fields)
        serialisable_proposed = []
        for p in proposed:
            serialisable_proposed.append({
                "text": p.get("text", ""),
                "tag": p.get("tag", ""),
                "reason": p.get("reason", ""),
                "replacement": p.get("replacement", ""),
            })

        serialisable_escalations = []
        for e in escalations:
            serialisable_escalations.append({
                "text": e.get("text", ""),
                "tag": e.get("tag", ""),
                "reason": e.get("reason", ""),
            })

        return {
            "filename": filename,
            "proposed_redactions": serialisable_proposed,
            "escalations": serialisable_escalations,
            "redacted_text": redacted_text,
            "original_text": text,
            "error": "",
        }

    except Exception as e:
        elapsed = time.time() - t0
        print(f"      ERROR after {elapsed:.1f}s: {e}", flush=True)
        return {
            "filename": filename,
            "proposed_redactions": [],
            "escalations": [],
            "redacted_text": text,
            "original_text": text,
            "error": str(e),
        }


def _find_test_zips(zip_pattern: str = None) -> list:
    """Find test ZIP files matching the given pattern (default: Test-*-v2.zip)."""
    import glob
    if zip_pattern is None:
        zip_pattern = ZIP_PATTERN
    pattern = os.path.join(ZIP_DIR, zip_pattern)
    zips = sorted(glob.glob(pattern))
    return zips


def _process_zip(zip_path: str, model: str) -> dict:
    """Process a single test ZIP and return the patient result dict."""
    zip_name = os.path.basename(zip_path)
    print(f"\n{'='*60}", flush=True)
    print(f"Processing: {zip_name}", flush=True)
    print(f"{'='*60}", flush=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Read manifest
        manifest_names = [n for n in zf.namelist() if n.endswith("_manifest.json")]
        if not manifest_names:
            print(f"  ERROR: No _manifest.json found in {zip_name}", flush=True)
            return {
                "zip": zip_name,
                "patient_name": "",
                "documents": [],
                "missed_redactions": [],
                "over_redactions": [],
                "escalation_hits": [],
                "escalation_misses": [],
                "pass": False,
                "error": "No _manifest.json found",
            }

        manifest_data = json.loads(zf.read(manifest_names[0]).decode("utf-8"))
        patient_name = manifest_data.get("patient_name", "")
        patient_dob = manifest_data.get("patient_dob", "")
        not_in_redacted = manifest_data.get("not_in_redacted", [])
        must_stay = manifest_data.get("must_stay", [])
        escalation_expected = manifest_data.get("escalation_expected", [])

        print(f"  Patient: {patient_name}", flush=True)
        print(f"  DOB: {patient_dob}", flush=True)
        print(f"  Expected redactions (not_in_redacted): {len(not_in_redacted)}", flush=True)
        print(f"  Must stay: {len(must_stay)}", flush=True)
        print(f"  Expected escalations: {len(escalation_expected)}", flush=True)

        # Process each .txt file
        txt_files = [
            n for n in zf.namelist()
            if n.endswith(".txt") and not n.endswith("_manifest.json")
        ]
        txt_files.sort()

        documents = []
        for txt_name in txt_files:
            text = zf.read(txt_name).decode("utf-8")
            doc_result = _process_document(text, model, patient_name, txt_name)
            documents.append(doc_result)

    # ---- Evaluate against manifest ----
    # MISSED REDACTIONS: strings in not_in_redacted that still appear in any redacted_text
    missed_redactions = []
    for term in not_in_redacted:
        term_lower = term.lower()
        found_in_redacted = False
        for doc in documents:
            if term_lower in doc["redacted_text"].lower():
                found_in_redacted = True
                break
        if found_in_redacted:
            missed_redactions.append(term)

    # OVER-REDACTIONS: strings in must_stay that exist in original but not in redacted
    over_redactions = []
    for term in must_stay:
        term_lower = term.lower()
        for doc in documents:
            in_original = term_lower in doc["original_text"].lower()
            in_redacted = term_lower in doc["redacted_text"].lower()
            if in_original and not in_redacted:
                over_redactions.append(term)
                break

    # ESCALATIONS: strings in escalation_expected that appear in any escalations list
    all_escalation_texts = []
    for doc in documents:
        for esc in doc.get("escalations", []):
            all_escalation_texts.append((esc.get("text", "")).lower())

    escalation_hits = []
    escalation_misses = []
    for term in escalation_expected:
        term_lower = term.lower()
        found = any(term_lower in et for et in all_escalation_texts)
        if found:
            escalation_hits.append(term)
        else:
            escalation_misses.append(term)

    passed = len(missed_redactions) == 0 and len(over_redactions) == 0 and len(escalation_misses) == 0

    # Print summary for this ZIP
    print(f"\n  --- Results for {zip_name} ---", flush=True)
    print(f"  Missed redactions: {len(missed_redactions)}", flush=True)
    for m in missed_redactions:
        print(f"    MISS: '{m}'", flush=True)
    print(f"  Over-redactions:   {len(over_redactions)}", flush=True)
    for o in over_redactions:
        print(f"    OVER: '{o}'", flush=True)
    print(f"  Escalation hits:   {len(escalation_hits)}/{len(escalation_expected)}", flush=True)
    for em in escalation_misses:
        print(f"    ESC MISS: '{em}'", flush=True)
    print(f"  PASS: {passed}", flush=True)

    return {
        "zip": zip_name,
        "patient_name": patient_name,
        "documents": documents,
        "missed_redactions": missed_redactions,
        "over_redactions": over_redactions,
        "escalation_hits": escalation_hits,
        "escalation_misses": escalation_misses,
        "pass": passed,
    }


def main():
    parser = argparse.ArgumentParser(description="SAR Redaction Test Harness")
    parser.add_argument("--pattern", default=None,
                        help="Glob pattern for test ZIPs (default: Test-*-v2.zip)")
    args = parser.parse_args()

    print("=" * 60, flush=True)
    print("SAR Redaction Test Harness", flush=True)
    print("=" * 60, flush=True)

    # Select model
    model = _select_model()

    # Find test ZIPs
    zip_pattern = args.pattern
    zips = _find_test_zips(zip_pattern)
    if not zips:
        used_pattern = zip_pattern or ZIP_PATTERN
        print(f"ERROR: No {used_pattern} files found in {ZIP_DIR}", flush=True)
        sys.exit(1)

    print(f"\nFound {len(zips)} test ZIP(s):", flush=True)
    for z in zips:
        print(f"  {os.path.basename(z)}", flush=True)

    run_timestamp = datetime.now(timezone.utc).isoformat()
    patients = []

    for zip_path in zips:
        patient_result = _process_zip(zip_path, model)
        patients.append(patient_result)

    # Summary
    total_missed = sum(len(p["missed_redactions"]) for p in patients)
    total_over = sum(len(p["over_redactions"]) for p in patients)
    total_esc_misses = sum(len(p["escalation_misses"]) for p in patients)
    passes = sum(1 for p in patients if p["pass"])

    report = {
        "run_timestamp": run_timestamp,
        "model": model,
        "patients": patients,
        "summary": {
            "total_missed": total_missed,
            "total_over_redacted": total_over,
            "total_escalation_misses": total_esc_misses,
            "pass_rate": f"{passes}/{len(patients)}",
        },
    }

    # Write results
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}", flush=True)
    print("FINAL SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"Model:              {model}", flush=True)
    print(f"Total missed:       {total_missed}", flush=True)
    print(f"Total over-redacted:{total_over}", flush=True)
    print(f"Total esc misses:   {total_esc_misses}", flush=True)
    print(f"Pass rate:          {passes}/{len(patients)}", flush=True)
    print(f"\nResults written to: {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
