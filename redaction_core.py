"""
redaction_core.py
=================
Pure-logic SAR redaction functions extracted from app.py.
No Streamlit dependencies — safe to import from tests, CLI scripts, or batch runners.
"""

import re
import json
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import ollama


# =============================================================================
# NHS SAR Redaction Ontology
# =============================================================================

REDACTION_TAGS = {
    # ── Auto-redact ───────────────────────────────────────────────────────────
    "THIRD_PARTY_IDENTIFIER": {
        "label":  "Third-party identifier",
        "desc":   "Name or identifying detail of a private individual (family, carer, neighbour, friend)",
        "action": "redact",
    },
    "CONFIDENTIAL_DISCLOSURE": {
        "label":  "Confidential third-party disclosure",
        "desc":   "Information given in confidence by a third party; anonymous or pseudonymous reports",
        "action": "redact",
    },
    "OTHER_PATIENT_DATA": {
        "label":  "Other patient's data",
        "desc":   "Data belonging to a different patient (misfiled notes, clinic list error, wrong results)",
        "action": "redact",
    },
    "AGENCY_CONFIDENTIAL_INFO": {
        "label":  "Agency / social care report",
        "desc":   "Social worker, school, police or probation report that identifies a third party",
        "action": "redact",
    },
    "INDIRECT_IDENTIFIER": {
        "label":  "Indirect identifier",
        "desc":   "Text that would identify a third party without naming them explicitly",
        "action": "redact",
    },
    # ── Escalate for qualified human decision ─────────────────────────────────
    "CLINICIAN_CONTEXT_AMBIGUOUS": {
        "label":  "Clinician — context ambiguous",
        "desc":   (
            "A clinician name that appears in a non-professional context: named as a patient, "
            "as a complainant, as the subject of an internal complaint or investigation, or "
            "where their role is unclear (e.g. locum/agency staff). "
            "Clinicians named in their ordinary professional capacity are NOT redacted."
        ),
        "action": "escalate",
    },
    "SAFEGUARDING_RISK": {
        "label":  "Safeguarding concern",
        "desc":   "Safeguarding referral, MARAC, CP concern, LAC, MASH referral — requires clinical/IG review",
        "action": "escalate",
    },
    "DOMESTIC_ABUSE_CONTEXT": {
        "label":  "Domestic abuse disclosure",
        "desc":   "Domestic abuse, coercive control, DASH assessment, MARAC referral — escalate",
        "action": "escalate",
    },
    "CHILD_PROTECTION": {
        "label":  "Child protection information",
        "desc":   "CP plan, S47/S17 enquiry, CP conference, LADO — escalate",
        "action": "escalate",
    },
    "SERIOUS_HARM_RISK": {
        "label":  "Serious harm risk",
        "desc":   (
            "Information whose disclosure could cause serious physical or mental harm to the "
            "patient or a third party (DPA 2018 Sch.3 para.5 / s.15). "
            "Includes acute active suicide/self-harm risk, credible violence risk, acute psychotic "
            "risk. Routine historical mental health notes are NOT covered by this exemption."
        ),
        "action": "escalate",
    },
    "SENSITIVE_CLINICAL_OPINION": {
        "label":  "Harmful clinical opinion",
        "desc":   (
            "Clinical opinion that, if disclosed, could cause serious harm or engages a specific "
            "exemption — NOT routine clinical opinion, which is the patient's own data and must "
            "be disclosed. Covers: explicit notes on symptom fabrication / factitious disorder, "
            "notes recording a credible and current risk of violence by the patient, or opinion "
            "that would directly identify and potentially harm a named third party."
        ),
        "action": "escalate",
    },
    "LEGAL_PRIVILEGE": {
        "label":  "Legal / investigation material",
        "desc":   (
            "Material that may attract an exemption under DPA 2018 Sch.3: legal advice, court "
            "reports, expert witness reports, internal disciplinary or complaints investigations "
            "(Sch.3 para.19), management forecasting / planning information (Sch.3 para.6), or "
            "formal negotiation records (Sch.3 para.7). Requires IG / legal review."
        ),
        "action": "escalate",
    },
    "DPA_SCHEDULE3_EXEMPTION": {
        "label":  "DPA 2018 Sch.3 — other exemption",
        "desc":   (
            "Content that may engage a Schedule 3 DPA 2018 exemption not captured elsewhere: "
            "research, statistics or history data (Sch.3 para.8); exam scripts before publication "
            "(Sch.3 para.9); regulatory / supervisory body material (Sch.3 para.10); or data "
            "from a separate data controller whose provenance is unclear in a shared-care or "
            "ICB-held record. Requires IG review to identify the applicable head of exemption."
        ),
        "action": "escalate",
    },
}


# =============================================================================
# LLM prompts
# =============================================================================

_SAR_SYSTEM = (
    "You are an NHS Information Governance SAR redaction specialist. "
    "You respond with valid JSON only. No preamble, no explanation, no markdown."
)

_SAR_PROMPT_TMPL = """\
You are an NHS Information Governance officer processing a Subject Access Request (SAR).
Analyse ONLY the text between the --- markers below.
Apply UK GDPR / DPA 2018 / ICO guidance and the BMA guidance on access to health records.

━━━ DO NOT FLAG FOR REDACTION ━━━
{patient_line}\
• The patient's own name, DOB, NHS number, address, clinical findings, diagnoses,
  medications and test results — this is their own personal data and MUST be disclosed.
  NOTE: only the patient's OWN DOB is protected. Any date of birth that differs from
  the patient's DOB and belongs to a third party (e.g. a perpetrator, next of kin,
  or misfiled patient) MUST be flagged as THIRD_PARTY_IDENTIFIER or OTHER_PATIENT_DATA.
• Routine clinical opinion — clinical opinions, assessments and judgements recorded about
  the patient are the patient's own data. Do NOT escalate them unless they meet the
  specific "SENSITIVE_CLINICAL_OPINION" criteria below.
• Clinician names (GP, nurse, consultant, pharmacist, AHP) appearing in their ORDINARY
  PROFESSIONAL CAPACITY — e.g. signing a letter, recording a consultation, ordering a test.
  Exception: escalate as CLINICIAN_CONTEXT_AMBIGUOUS if the clinician is named as a
  patient, as the complainant/subject of a complaint, or in a context where their personal
  data (not their professional act) is being recorded.
• NHS Trust, hospital, GP practice, clinic or department names.
• Standard appointment dates, referral acknowledgements, administrative notices.
• Job titles and role descriptions alone (e.g. "SEN coordinator", "class teacher",
  "key worker", "social worker", "named nurse", "care coordinator") — these are NOT
  personal data. Only redact the individual's personal name, not their job title.
• In a paediatric record (patient described as "child"), the named parent or guardian
  listed in the record header (e.g. "Parent/Guardian: Mrs Chloe Green") is the SAR
  requestor acting on the child's behalf — do NOT redact their name ANYWHERE in the
  document, even when it appears again in the body or in correspondence.
• Clinician and healthcare professional names (including abbreviated forms such as
  "Dr M. Robertson", "Dr J. Cole", "Nurse Ward") when appearing in their professional
  capacity — do NOT redact. This applies to ALL registered health professionals:
  GPs, hospital consultants, nurses, pharmacists, physiotherapists, occupational
  therapists, optometrists, dentists, radiographers, and any other AHP or clinical
  specialist — regardless of whether they work at this practice or an external clinic.
  This overrides the abbreviated-name rule below.

━━━ PROPOSE FOR AUTO-REDACTION ━━━
Copy the EXACT tag name. Redact the minimum span — a name or phrase, not a whole sentence.

THIRD_PARTY_IDENTIFIER   — name or identifying detail of any private individual:
                           family member, partner, carer, neighbour, friend, employer,
                           teacher, school contact, or any unnamed member of the public.
                           This INCLUDES their date of birth, phone number, NHS number,
                           address, and any other personal data appearing in structured
                           blocks (e.g. "Perpetrator details:", "Emergency contact:",
                           "Next of kin:") — redact ALL fields in such blocks, not just
                           the name. Create a separate entry for EACH field (name, DOB,
                           phone, address) so each is individually redacted.
                           Device serial numbers for the patient's personal medical devices
                           (insulin pumps, implants, CGM sensors, home monitors) are personal
                           data — flag as THIRD_PARTY_IDENTIFIER.
                           When you flag a PERSONAL email address (firstname.lastname@,
                           initial.surname@, or similar personal format) belonging to a
                           named private individual, ALSO create a separate THIRD_PARTY_IDENTIFIER
                           entry for that person's name (e.g. if you flag
                           "anita.lobo@company.co.uk", also flag "Anita Lobo"; if you flag
                           "s.allen@sleep-centre-personal.com", also flag "Sophie Allen").
                           Do NOT apply this rule to generic role/dept addresses (support@,
                           info@, admin@, victim.support@) — and NEVER use it to flag
                           clinicians in their professional capacity.
                           Abbreviated names (e.g. "C. Murray", "Anna S.", "P. Hall") ARE
                           third-party identifiers when they refer to a NON-CLINICIAN private
                           individual — redact them exactly as written. Do NOT apply this to
                           clinicians or healthcare professionals acting in their professional
                           capacity (e.g. "Dr M. Robertson", "Dr J. Cole" are NOT redacted).
                           Police incident reference numbers, crime reference numbers, and
                           Motor Insurers' Bureau (MIB) claim references (e.g. "MV/2024/B1/04471",
                           "URN 01AZ/12345/23") are THIRD_PARTY_IDENTIFIER — they are linked
                           to a named third party in the police or insurance system and must
                           be redacted.
CONFIDENTIAL_DISCLOSURE  — information given in confidence or anonymously by a third party
                           (ICO guidance: the identity of the third party may be withheld).
                           Specific descriptions of a named or identifiable third party's
                           threatening or abusive behaviour (e.g. "sending threatening
                           messages", "verbal abuse", "threatening text messages") are
                           CONFIDENTIAL_DISCLOSURE — they characterise that private individual
                           and should not be disclosed without review.
OTHER_PATIENT_DATA       — data clearly belonging to a different patient: misfiled notes,
                           wrong-patient test results, clinic lists showing other patients.
                           Redact ALL identifying fields for the other patient including their
                           name, date of birth, NHS number, address, and any other personal
                           identifiers — create a SEPARATE entry for each field.
AGENCY_CONFIDENTIAL_INFO — (a) the name and direct contact details of any social worker,
                           police officer, prison officer, custody officer, housing officer,
                           probation officer, school staff member, university counsellor,
                           external therapist (including NHS therapists in specialist services
                           such as eating disorder, IAPT, psychological therapy, or substance
                           misuse services), support group coordinator, interpreter, solicitor
                           or legal representative, or private/employer-commissioned
                           physiotherapist or occupational health adviser
                           named individually in their professional capacity in a referral,
                           report, or correspondence — they work for a DIFFERENT data
                           controller and their personal work details are not the patient's
                           data to receive;
                           (b) the substantive content of any social work, police, probation,
                           school, or agency report that names or identifies a third party.
                           Do NOT redact the agency or organisation name itself (e.g.
                           'Kent Adult Social Care', 'Warwickshire Children's Services',
                           'Women's Refuge') — only the personal names and direct contact
                           details of named individuals working for those organisations.
                           Always create SEPARATE entries for the name and the phone
                           number — never bundle them. If you find a phone number for an
                           agency professional, you MUST also create a separate entry for
                           their name, and vice versa.
INDIRECT_IDENTIFIER      — text that would identify a private third party without naming
                           them (e.g. "your son at St Peter's Primary", "the neighbour at
                           No. 14", "your partner who works at the council").

━━━ ESCALATE FOR QUALIFIED HUMAN REVIEW — do NOT auto-redact ━━━
These require a clinical or IG professional to make an active decision before any action.

CLINICIAN_CONTEXT_AMBIGUOUS — a clinician name appearing in an ambiguous or non-professional
                              context: named as a patient in this record, named as the subject
                              of or complainant in a formal complaint or investigation, or
                              where their role is unclear (locum/agency with no stated role).
                              IMPORTANT: Documents headed 'Formal Complaint', 'Record of
                              Complaint Received', 'Patient Complaint' or similar MUST have
                              any clinician named as the SUBJECT of the complaint escalated
                              under this tag — even if their name also appears elsewhere in
                              the document in a professional capacity.
SAFEGUARDING_RISK           — safeguarding referrals, MARAC discussions, CP concerns,
                              LAC / MASH referrals. Releasing or withholding requires
                              a qualified decision; neither is automatic.
DOMESTIC_ABUSE_CONTEXT      — domestic abuse or coercive control disclosures, DASH risk
                              assessment results, MARAC referral details.
CHILD_PROTECTION            — the SUBSTANCE of CP referrals: CP plans, Section 47 or
                              Section 17 enquiry details, CP conferences, LADO referral
                              content. Do NOT use this tag for the child's name or DOB —
                              those are THIRD_PARTY_IDENTIFIER (auto-redact). Only the
                              risk assessment content and referral narrative is escalated.
SERIOUS_HARM_RISK           — content that could cause SERIOUS physical or mental harm if
                              disclosed (DPA 2018 Sch.3 para.5). Applies to ACUTE, ACTIVE
                              risk only: credible imminent suicide or self-harm risk,
                              credible current violence risk, acute psychotic risk. Routine
                              or historical mental health notes do NOT qualify.
SENSITIVE_CLINICAL_OPINION  — clinical opinion that, if disclosed, could cause serious harm
                              or identifies a third party harmfully. Specifically:
                              (a) explicit notes on factitious disorder / symptom fabrication;
                              (b) opinion recording a credible and current risk of violence
                              BY the patient; (c) opinion that would directly identify and
                              harm a named third party. Routine clinical opinion, including
                              personality disorder diagnoses, is the patient's own data and
                              must NOT be escalated under this tag.
LEGAL_PRIVILEGE             — legal advice, court reports, expert witness reports, internal
                              disciplinary or complaints investigation records (Sch.3 para.19),
                              management forecasting / planning information (Sch.3 para.6),
                              or formal negotiation records (Sch.3 para.7).
DPA_SCHEDULE3_EXEMPTION     — content that may engage a Sch.3 DPA 2018 exemption not listed
                              above: research/statistics/history data (Sch.3 para.8); exam
                              scripts before publication (Sch.3 para.9); regulatory body
                              material (Sch.3 para.10); or data whose originating data
                              controller is unclear (e.g. shared-care record, ICB-held data).

━━━ OUTPUT RULES ━━━
• "text": copy EXACTLY as it appears — character for character, minimum span only.
• "replacement": for auto-redactions only; use the format [REDACTED - reason].
  Use a plain hyphen (-), not an em-dash or any other character.
• Never include the patient's own name in any "text" field.
• For THIRD_PARTY_IDENTIFIER: if a third party's name appears in MORE THAN ONE FORM in this
  document (e.g. full name "Jane Smith" at first mention, then "Jane" alone in quoted speech),
  create a SEPARATE entry for EACH verbatim form so every occurrence is captured.
  Example: one entry with text "Jane Smith", a second with text "Jane" (if "Jane" appears alone).
• A first name used alone (e.g. "Sandra", "Brian", "Karen") IS a THIRD_PARTY_IDENTIFIER
  if it refers to a private individual — do not skip it just because a surname is absent.
• Named children appearing in safeguarding or CP referrals are THIRD_PARTY_IDENTIFIER —
  auto-redact their name and DOB as separate entries. The CP referral substance is what
  requires CHILD_PROTECTION escalation, not the child's name itself.
  Always capture just the child's name as the minimum span (e.g. text: "Lily"), and
  their approximate DOB as a second separate entry (e.g. text: "2019" or "approximately
  2019") — never bundle the name and description into one long text string.
• Escalation and auto-redaction are MUTUALLY EXCLUSIVE for the SAME span of text.
  However, a SHORTER span within an escalated passage CAN still be proposed for
  auto-redaction — e.g. if you escalate the full sentence "He mentioned his
  brother-in-law David Holmes has continued to send threatening messages" under
  DOMESTIC_ABUSE_CONTEXT, you should ALSO add a CONFIDENTIAL_DISCLOSURE entry for
  the specific phrase "threatening messages" (or similar behavioural description)
  so it is redacted automatically regardless of the human decision on the escalation.

Output this JSON and nothing else:
{{
  "proposed_redactions": [
    {{
      "text": "exact verbatim text from the document",
      "tag": "THIRD_PARTY_IDENTIFIER",
      "reason": "Brief explanation (one sentence)",
      "replacement": "[REDACTED - third-party personal data]",
      "context": "Up to 30 words of surrounding context"
    }}
  ],
  "escalations": [
    {{
      "text": "exact verbatim text",
      "tag": "SAFEGUARDING_RISK",
      "reason": "Brief explanation (one sentence)",
      "context": "Up to 30 words of surrounding context"
    }}
  ]
}}

If nothing requires redaction or escalation return exactly:
{{"proposed_redactions": [], "escalations": []}}

Document excerpt:
---
{chunk}
---"""


_CHUNK_TIMEOUT = 120   # seconds to wait for a single LLM chunk response


# =============================================================================
# Internal helpers
# =============================================================================

def _extract_json(raw: str):
    if not raw:
        return None

    # Strategy 1: JSON inside a ```json ... ``` fence (greedy to capture full nested object)
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 2: first { ... last }
    if "{" in raw and "}" in raw:
        start = raw.index("{")
        end   = raw.rindex("}") + 1
        candidate = raw[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Strategy 3: auto-fix common LLM JSON mistakes then retry
            fixed = candidate
            fixed = re.sub(r",\s*([}\]])",    r"\1",      fixed)  # trailing commas
            fixed = re.sub(r'(?<!")None(?!")',  '"null"',  fixed)  # Python None
            fixed = re.sub(r'(?<!")True(?!")',  '"true"',  fixed)  # Python True
            fixed = re.sub(r'(?<!")False(?!")', '"false"', fixed)  # Python False
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

    return None


# =============================================================================
# Public API
# =============================================================================

def _detect_patient_name(filename: str, text: str = "") -> str:
    """
    Try to detect the patient's full name from:
      1. NHS EPR filename convention: '…SURNAME, Firstname (Title) NHSnum date.ext'
      2. Common document header patterns: 'Patient: Ms Firstname SURNAME'

    Returns 'Firstname Surname' (title-cased) or empty string if not found.
    Used as a fallback when the operator has not typed the patient name in the sidebar.
    """
    # ── 1. Filename pattern ──────────────────────────────────────────────────
    # Typical: '2022-09-14_hash_Description SURNAME, Firstname (Ms) 1000 …'
    m = re.search(
        r'\b([A-Z]{2,}),\s+([A-Za-z][a-z]+)\s+\((?:Mr|Mrs|Ms|Miss|Dr|Prof)',
        filename,
    )
    if m:
        return f"{m.group(2)} {m.group(1).title()}"

    # ── 2. Document text header ──────────────────────────────────────────────
    if text:
        sample = text[:2000]
        for pat in (
            r'Patient:\s+(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+([A-Za-z][a-z]+)\s+([A-Z][A-Za-z]+)',
            r'Patient:\s+([A-Za-z][a-z]+)\s+([A-Z]{2,})',
            r'Name:\s+(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+([A-Za-z][a-z]+)\s+([A-Z][A-Za-z]+)',
        ):
            m = re.search(pat, sample)
            if m:
                return f"{m.group(1)} {m.group(2).title()}"

    return ""


def _detect_guardian_name(text: str) -> str:
    """
    Extract the named parent/guardian from a paediatric record header.
    Returns the full name string (including title such as 'Mrs') as it
    appears before any parenthetical annotation, or '' if not found.
    """
    sample = text[:1500]
    for pat in (
        r'(?:Parent/Guardian|Registered Parent):\s+'
        r'((?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+[A-Za-z][a-z]+\s+[A-Z][A-Za-z]+)',
        r'(?:Parent/Guardian|Registered Parent):\s+'
        r'([A-Za-z][a-z]+\s+[A-Z][A-Za-z]+)',
    ):
        m = re.search(pat, sample)
        if m:
            return m.group(1).strip()
    return ""


def _detect_patient_dob(text: str) -> str:
    """
    Extract the patient's own DOB from the record header (first 1500 chars).
    Returns the date string as it appears (e.g. '27/06/1978') or '' if not found.
    Used to prevent the LLM from accidentally flagging the patient's own DOB
    as third-party data.
    """
    sample = text[:1500]
    for pat in (
        r'DOB:\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'Date of Birth:\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'DOB:\s+(\d{2}\.\d{2}\.\d{4})',
        r'D\.O\.B\.?:\s+(\d{1,2}/\d{1,2}/\d{4})',
    ):
        m = re.search(pat, sample)
        if m:
            return m.group(1).strip()
    return ""


def _analyse_chunk(chunk: str, model: str, patient_line: str, extra_instructions: str = "") -> tuple:
    """Send one chunk to the LLM. Returns (result_dict, raw_string)."""
    user_msg = _SAR_PROMPT_TMPL.format(patient_line=patient_line, chunk=chunk)
    if extra_instructions:
        user_msg += f"\n\nADDITIONAL INSTRUCTIONS FOR THIS SESSION ONLY:\n{extra_instructions}"

    def _call():
        return ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SAR_SYSTEM},
                {"role": "user",   "content": user_msg},
            ],
            format="json",                              # forces valid JSON output for any model
            options={"temperature": 0,
                     "num_predict": 1024},              # cap output — SAR JSON rarely exceeds ~800 tokens
        )

    try:
        ex     = ThreadPoolExecutor(max_workers=1)
        future = ex.submit(_call)
        try:
            resp = future.result(timeout=_CHUNK_TIMEOUT)
        except FuturesTimeoutError:
            ex.shutdown(wait=False)   # don't block — let the stalled thread die on its own
            return (
                {"proposed_redactions": [], "escalations": [], "parse_ok": False},
                f"[TIMEOUT] LLM did not respond within {_CHUNK_TIMEOUT}s",
            )
        finally:
            ex.shutdown(wait=False)
        raw = resp["message"]["content"].strip()
    except Exception as exc:
        return {"proposed_redactions": [], "escalations": [], "parse_ok": False}, f"[LLM ERROR] {exc}"

    parsed = _extract_json(raw)
    if parsed is None:
        return {"proposed_redactions": [], "escalations": [], "parse_ok": False}, raw

    return {
        "proposed_redactions": parsed.get("proposed_redactions", []) or [],
        "escalations":         parsed.get("escalations", [])         or [],
        "parse_ok":            True,
    }, raw


def _expand_name_redactions(proposed: list, text: str, patient_name: str = "") -> list:
    """
    For each THIRD_PARTY_IDENTIFIER redaction that looks like a full name
    (two or more words), extract each component word and add a separate
    redaction entry for any that appear STANDALONE elsewhere in the document
    (i.e. outside the immediate context of the full name).

    This catches cases like: LLM flags "Michelle Granger" but the document
    later refers to her as just "Michelle" in quoted speech.

    patient_name: the subject of the SAR — name parts matching the patient's
    own name are never added as new redaction targets.
    """
    if not text:
        return proposed

    # Build a set of the patient's own name tokens to protect from over-redaction.
    # This prevents e.g. "Sampledata" (shared surname with a family member)
    # being expanded into a redaction that would erase the patient's own header lines.
    _pn_tokens: set = set()
    if patient_name.strip():
        for tok in patient_name.strip().lower().split():
            clean_tok = tok.strip(".,;:()[]'\"–—-")
            if len(clean_tok) >= 3:
                _pn_tokens.add(clean_tok)

    existing_lower = {(r.get("text") or "").strip().lower() for r in proposed}
    extra = []

    _STOPWORDS = {
        "the", "a", "an", "of", "at", "on", "in", "to", "for", "from", "with",
        "who", "what", "where", "when", "how", "that", "this", "and", "or",
        "but", "not", "no", "is", "was", "are", "were", "be", "been", "has",
        "have", "had", "do", "does", "did", "will", "would", "can", "could",
        "may", "might", "she", "he", "her", "his", "their", "they", "our",
        "runs", "post", "lives", "works", "near", "next", "door", "road",
        "street", "lane", "avenue", "close", "drive", "house", "flat", "office",
        "woman", "man", "lady", "person", "child", "boy", "girl", "family",
        "local", "nearby", "down",
        # Role / occupation words — prevent expanding role titles into name tokens
        "social", "worker", "coordinator", "senior", "care", "staff", "health",
        "support", "key", "lead", "head", "deputy", "assistant", "registered",
        "qualified", "community", "liaison", "service", "services", "team",
        "manager", "director", "officer", "nurse", "doctor", "consultant",
        "specialist", "therapist", "counsellor", "advisor", "adviser",
        # Salutation / correspondence words
        "dear", "tel", "ref", "re", "via", "attn",
        # Honorifics / titles — prevent "(Mrs" being extracted as a name token
        "mrs", "miss", "prof", "sir", "rev", "lord", "dame",
    }

    for item in proposed:
        tag = item.get("tag", "")
        raw = (item.get("text") or "").strip()

        # For AGENCY_CONFIDENTIAL_INFO items like
        # "Claire Hughes (Warwickshire Children's Services, Tel: 01926 000055)"
        # extract the name portion before the first '(' or ',' and add it
        # as a standalone redaction if it appears elsewhere in the document.
        if tag == "AGENCY_CONFIDENTIAL_INFO":
            name_part = re.split(r'[,(]', raw)[0].strip()
            np_parts = name_part.split()
            if (2 <= len(np_parts) <= 3
                    and all(p[0].isupper() for p in np_parts if p)
                    and name_part.lower() not in existing_lower):
                pattern = r'(?<!\w)' + re.escape(name_part) + r'(?!\w)'
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    window_start = max(0, m.start() - len(raw) - 5)
                    window_end   = min(len(text), m.end() + len(raw) + 5)
                    window       = text[window_start:window_end]
                    if raw.lower() not in window.lower():
                        extra.append({
                            "text":        name_part,
                            "tag":         tag,
                            "reason":      f"Standalone name from agency contact (propagated from \"{raw}\")",
                            "replacement": item.get("replacement", "[REDACTED - agency confidential information]"),
                            "context":     item.get("context", ""),
                            "approved":    True,
                        })
                        existing_lower.add(name_part.lower())
                        if len(np_parts) == 2:
                            surname = np_parts[1]
                            if (surname.lower() not in existing_lower
                                    and surname.lower() not in _STOPWORDS
                                    and len(surname) >= 3):
                                pat2 = r'(?<!\w)' + re.escape(surname) + r'(?!\w)'
                                for m2 in re.finditer(pat2, text, re.IGNORECASE):
                                    w2_start = max(0, m2.start() - len(raw) - 5)
                                    w2_end   = min(len(text), m2.end() + len(raw) + 5)
                                    w2       = text[w2_start:w2_end]
                                    if raw.lower() not in w2.lower() and name_part.lower() not in w2.lower():
                                        extra.append({
                                            "text":        surname,
                                            "tag":         tag,
                                            "reason":      f"Surname of agency contact (propagated from \"{raw}\")",
                                            "replacement": item.get("replacement", "[REDACTED - agency confidential information]"),
                                            "context":     item.get("context", ""),
                                            "approved":    True,
                                        })
                                        existing_lower.add(surname.lower())
                                        break
                        break
            continue

        if tag != "THIRD_PARTY_IDENTIFIER":
            continue
        parts = raw.split()
        if len(parts) < 2:
            continue   # already a single word — nothing to expand

        # Do NOT expand email salutation strings ("Dear Dr X", "To Whom", etc.)
        # These are not names — expanding them causes clinician names to be redacted.
        _SALUTATIONS = {"dear", "to", "re", "attn", "attention"}
        if parts[0].lower().strip(".,;:") in _SALUTATIONS:
            continue

        # Do NOT expand address strings — they contain place names that occur
        # legitimately in institution names like "Bradford Royal Infirmary".
        _ADDRESS_KEYWORDS = {
            "road", "street", "avenue", "lane", "close", "drive", "court", "place",
            "way", "grove", "gardens", "crescent", "terrace", "walk", "parade",
        }
        if any(kw in raw.lower() for kw in _ADDRESS_KEYWORDS):
            continue

        for part in parts:
            # Strip common punctuation that can attach to a name in free text
            clean = part.strip(".,;:()[]'\"–—-")
            if len(clean) < 3:
                continue   # skip initials / very short tokens
            if clean.lower() in existing_lower:
                continue   # already being redacted
            if clean.lower() in _pn_tokens:
                continue   # part of patient's own name — never redact

            # Only expand parts that look like proper name tokens:
            # must start with uppercase and not be a generic English word
            if not (len(clean) >= 3 and clean[0].isupper() and clean.lower() not in _STOPWORDS):
                continue   # not a proper name token — skip this part

            # Word-boundary search for standalone occurrence
            pattern = r'(?<!\w)' + re.escape(clean) + r'(?!\w)'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if not matches:
                continue

            # At least one occurrence must be OUTSIDE the span of the full name
            # AND not embedded in an organisation/company name.
            _ORG_SUFFIXES_RE = re.compile(
                r'\s*(?:&|and)\s+[A-Z]|\b(?:LLP|Ltd|PLC|plc|Inc|Trust|NHS|LTD)\b',
                re.IGNORECASE,
            )
            standalone = False
            for m in matches:
                # Build the surrounding window and check full name isn't there
                window_start = max(0, m.start() - len(raw) - 5)
                window_end   = min(len(text), m.end() + len(raw) + 5)
                window       = text[window_start:window_end]
                if raw.lower() in window.lower():
                    continue  # full name also present — not a standalone occurrence
                # Check that the immediate right-hand context doesn't suggest this
                # token is the first word of an org name ("Thompson & Reed LLP")
                right_ctx = text[m.end(): m.end() + 20]
                if _ORG_SUFFIXES_RE.match(right_ctx):
                    continue  # looks like org name — skip
                standalone = True
                break

            if standalone:
                extra.append({
                    "text":        clean,
                    "tag":         "THIRD_PARTY_IDENTIFIER",
                    "reason":      f"Standalone name-part of third party (expanded from \"{raw}\")",
                    "replacement": "[REDACTED - third-party personal data]",
                    "context":     item.get("context", ""),
                    "approved":    True,
                })
                existing_lower.add(clean.lower())

    return proposed + extra


# =============================================================================
# Post-processing: expand agency contacts to catch paired name/phone
# =============================================================================

def _expand_agency_contacts(proposed: list, text: str, patient_name: str = "") -> list:
    """
    When an AGENCY_CONFIDENTIAL_INFO or THIRD_PARTY_IDENTIFIER proposed redaction
    contains a phone number but the adjacent name was missed (or vice versa), try to
    locate the missing counterpart in the surrounding text and add it.

    Handles structured blocks like:
        Social worker: Diane Okafor
        Direct line: 01925 000055
    where the LLM may catch one field but not the other.
    """
    import re as _re

    _PHONE_PAT = _re.compile(
        r'\b(\d{5}\s\d{6}|\d{4}\s\d{3}\s\d{4}|\d{11}|\+44[\s\d]{10,13})\b'
    )
    _EMAIL_PAT = _re.compile(
        r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b'
    )
    _NAME_PAT = _re.compile(
        r'\b([A-Z][a-z]{1,}(?:\s+[A-Z][a-z]{1,}){1,2})\b'
    )
    _AGENCY_TAGS = {"AGENCY_CONFIDENTIAL_INFO", "THIRD_PARTY_IDENTIFIER"}

    _INSTITUTIONAL_WORDS = {
        "hospital", "infirmary", "royal", "nhs", "trust", "refuge", "liaison",
        "services", "service", "clinic", "surgery", "centre", "center", "council",
        "authority", "department", "office", "association", "police", "court",
        "school", "college", "university", "academy", "foundation", "unit",
        "ward", "team", "group", "limited", "ltd", "plc", "inc", "officer",
        # Social/care sector words — prevent 'Kent Adult Social' matching as a person
        "social", "adult", "care", "health", "mental", "children", "young",
        "community", "housing", "probation", "welfare", "voluntary",
    }

    def _is_institutional(name: str) -> bool:
        return any(w in _INSTITUTIONAL_WORDS for w in name.lower().split())

    def _is_plausible_person(name: str) -> bool:
        words = name.split()
        if not (1 < len(words) <= 3):
            return False
        return not _is_institutional(name)

    # Build patient name token set
    _pn_tokens_agency: set = set()
    for tok in patient_name.strip().lower().split():
        clean = tok.strip(".,;:()[]'\"")
        if len(clean) >= 3:
            _pn_tokens_agency.add(clean)

    existing_lower = {(r.get("text") or "").strip().lower() for r in proposed}
    lines = text.splitlines()
    extra = []

    for item in proposed:
        if item.get("tag") not in _AGENCY_TAGS:
            continue
        item_text = (item.get("text") or "").strip()

        # Case A: item is a phone number → look for adjacent personal name (±1 line)
        if _PHONE_PAT.fullmatch(item_text.replace(" ", "")):
            for li, line in enumerate(lines):
                if item_text in line:
                    window = lines[max(0, li - 1): li + 2]
                    for wline in window:
                        for m in _NAME_PAT.finditer(wline):
                            candidate = m.group(1)
                            if (candidate.lower() not in existing_lower
                                    and _is_plausible_person(candidate)):
                                extra.append({
                                    "text":        candidate,
                                    "tag":         item.get("tag"),
                                    "reason":      f"Name associated with agency contact (paired with {item_text})",
                                    "replacement": "[REDACTED - agency contact]",
                                    "context":     wline.strip(),
                                    "approved":    True,
                                })
                                existing_lower.add(candidate.lower())
                    break

        # Case B: item is a name → look for adjacent phone numbers (±1 line)
        elif _NAME_PAT.fullmatch(item_text) and _is_plausible_person(item_text):
            for li, line in enumerate(lines):
                if item_text in line:
                    window = lines[max(0, li - 1): li + 2]
                    for wline in window:
                        for m in _PHONE_PAT.finditer(wline):
                            candidate = m.group(0)
                            if candidate.lower() not in existing_lower:
                                extra.append({
                                    "text":        candidate,
                                    "tag":         item.get("tag"),
                                    "reason":      f"Phone associated with agency contact (paired with {item_text})",
                                    "replacement": "[REDACTED - agency contact]",
                                    "context":     wline.strip(),
                                    "approved":    True,
                                })
                                existing_lower.add(candidate.lower())
                    break

        # Case C: item is an email address → look for the owner's name on the same line
        elif _EMAIL_PAT.fullmatch(item_text):
            for li, line in enumerate(lines):
                if item_text in line:
                    window = lines[max(0, li - 1): li + 2]
                    for wline in window:
                        for m in _NAME_PAT.finditer(wline):
                            candidate = m.group(1)
                            candidate_toks = {w.lower() for w in candidate.split()}
                            if candidate_toks & _pn_tokens_agency:
                                continue
                            if (candidate.lower() not in existing_lower
                                    and _is_plausible_person(candidate)):
                                extra.append({
                                    "text":        candidate,
                                    "tag":         "THIRD_PARTY_IDENTIFIER",
                                    "reason":      f"Named owner of email address {item_text}",
                                    "replacement": "[REDACTED - third-party personal data]",
                                    "context":     wline.strip(),
                                    "approved":    True,
                                })
                                existing_lower.add(candidate.lower())
                    break

    return proposed + extra


def _expand_agency_professionals(proposed: list, text: str, patient_name: str = "") -> list:
    """
    Code-level fallback to catch named agency professionals that the LLM misses
    even when prompted.  Targets three high-miss patterns:

      1. "by [Name] (private/independent/employer-commissioned [role])"
         e.g. "by Lisa Torn (private physiotherapist, commissioned by employer's insurer)"

      2. "[Role] [Name] ([org/service]...)"
         e.g. "Therapist Claire Inder (NHS Eating Disorder Service, Peterborough)"

      3. "solicitor [Name] (" — solicitors named in correspondence
         e.g. "solicitor James Hazeldine (Hazeldine & Partners LLP)"

    Adds new AGENCY_CONFIDENTIAL_INFO entries for matched names not already proposed.
    """
    _NAME = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'

    _PATTERNS = [
        # "by [Name] (private / independent / employer-commissioned [clinical role])"
        re.compile(
            r'\bby\s+' + _NAME +
            r'\s*\((?:private|independent|employer[- ]commissioned)\s*'
            r'(?:physiotherapist|physio|therapist|counsellor|psychologist|'
            r'occupational health)',
            re.IGNORECASE,
        ),
        # "[Clinical role title] [Name] ([org"
        re.compile(
            r'\b(?:Therapist|Physiotherapist|Counsellor|Psychologist|'
            r'Occupational Health Adviser|Occupational Health Advisor)\s+' +
            _NAME + r'\s*[\(,]',
            re.IGNORECASE,
        ),
        # "solicitor [Name]" or "from solicitor [Name]"
        re.compile(
            r'\bsolicitor\s+' + _NAME + r'\b',
            re.IGNORECASE,
        ),
    ]

    _pn_lower = (patient_name or "").strip().lower()
    _existing = {(p.get("text") or "").strip().lower() for p in proposed}

    additions = []
    for pat in _PATTERNS:
        for m in pat.finditer(text):
            name = m.group(1).strip()
            if not name:
                continue
            if name.lower() in _existing:
                continue
            if _pn_lower and name.lower() == _pn_lower:
                continue
            additions.append({
                "text":        name,
                "tag":         "AGENCY_CONFIDENTIAL_INFO",
                "reason":      "Named agency professional (pattern-based extraction).",
                "replacement": "[REDACTED - agency confidential information]",
            })
            _existing.add(name.lower())

    return proposed + additions


def llm_analyse_document(
    text: str,
    model: str,
    patient_name: str = "",
    status_cb=None,
    extra_redactions: str = "",
    custom_instructions: str = "",
) -> tuple:
    """
    Analyse document text for SAR redactions.
    Splits long documents into overlapping chunks so the whole document is covered.
    Returns (result_dict, raw_llm_string).

    status_cb:           optional callable(message: str) for live progress updates.
    extra_redactions:    newline/comma-separated extra terms to always redact this session.
    custom_instructions: free-text extra prompt instructions appended this session.
    """
    patient_line = ""
    if patient_name.strip():
        patient_line = (
            f"- The patient is {patient_name.strip()} — "
            "NEVER flag this person's own name or identifiers for redaction\n"
        )

    # Build session-specific addendum
    extra_parts = []
    if extra_redactions.strip():
        terms = [t.strip() for t in re.split(r"[,\n]+", extra_redactions) if t.strip()]
        if terms:
            quoted = ", ".join(f'"{t}"' for t in terms)
            extra_parts.append(
                f"EXTRA TERMS TO REDACT (always flag these regardless of other rules): {quoted}\n"
                "Tag each as THIRD_PARTY_IDENTIFIER unless a more specific tag clearly applies."
            )
    if custom_instructions.strip():
        extra_parts.append(custom_instructions.strip())
    extra_str = "\n\n".join(extra_parts)

    CHUNK      = 6000   # characters per chunk (~1500 words, ~2-3 GP pages)
    STRIDE     = 5500   # overlap of 500 chars catches phrases that straddle a boundary
    MAX_CHUNKS = 8      # analyse up to ~48 000 chars (≈ 12–15 pages)

    chunks = []
    pos = 0
    while pos < len(text) and len(chunks) < MAX_CHUNKS:
        chunks.append(text[pos: pos + CHUNK])
        pos += STRIDE

    all_proposed, all_escalations, all_raw = [], [], []
    parse_ok = True

    for idx, chunk in enumerate(chunks, 1):
        if status_cb:
            status_cb(
                f"Analysing chunk {idx}/{len(chunks)} "
                f"(~{len(chunk):,} chars, up to {_CHUNK_TIMEOUT}s each)..."
            )
        result, raw = _analyse_chunk(chunk, model, patient_line, extra_str)
        all_raw.append(raw)
        if not result.get("parse_ok"):
            parse_ok = False
        all_proposed.extend(result.get("proposed_redactions", []))
        all_escalations.extend(result.get("escalations", []))

    # ── Post-processing: mutual exclusivity of escalation and auto-redaction ──
    _escalate_tags = {tag for tag, info in REDACTION_TAGS.items()
                      if info.get("action") == "escalate"}
    _esc_texts = {(e.get("text") or "").strip().lower() for e in all_escalations}
    all_proposed = [
        p for p in all_proposed
        if p.get("tag", "") not in _escalate_tags
        and (p.get("text") or "").strip().lower() not in _esc_texts
    ]

    # ── Post-processing: fix empty replacements ──────────────────────────────
    _DEFAULT_REPLACEMENTS = {
        "THIRD_PARTY_IDENTIFIER":  "[REDACTED - third-party personal data]",
        "CONFIDENTIAL_DISCLOSURE": "[REDACTED - confidential third-party information]",
        "OTHER_PATIENT_DATA":      "[REDACTED - other patient's data]",
        "AGENCY_CONFIDENTIAL_INFO":"[REDACTED - agency confidential information]",
        "INDIRECT_IDENTIFIER":     "[REDACTED - indirect identifier]",
    }
    for item in all_proposed:
        if not (item.get("replacement") or "").strip():
            tag = item.get("tag", "")
            item["replacement"] = _DEFAULT_REPLACEMENTS.get(tag, "[REDACTED]")

    # ── Post-processing: extract concrete identifiers from escalated passages ──
    _existing_proposed_lower = {(p.get("text") or "").strip().lower() for p in all_proposed}
    _EMAIL_RE   = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')
    _PHONE_RE   = re.compile(r'\b(\d{5}\s\d{6}|\d{4}\s\d{3}\s\d{4}|\d{11}|\+44[\s\d]{10,13})\b')
    _REF_RE     = re.compile(r'\b[A-Z]{2,}[/\-]\d{4}[/\-][A-Z0-9]+[/\-]\d+\b')
    _ABBR_NAME_RE = re.compile(r'\b([A-Z]\.?\s+[A-Z][a-z]{2,})\b')
    for esc in all_escalations:
        esc_text = (esc.get("text") or "").strip()
        for pat, tag, repl in (
            (_EMAIL_RE,     "THIRD_PARTY_IDENTIFIER",  "[REDACTED - third-party personal data]"),
            (_PHONE_RE,     "THIRD_PARTY_IDENTIFIER",  "[REDACTED - third-party personal data]"),
            (_REF_RE,       "THIRD_PARTY_IDENTIFIER",  "[REDACTED - third-party personal data]"),
            (_ABBR_NAME_RE, "AGENCY_CONFIDENTIAL_INFO","[REDACTED - agency confidential information]"),
        ):
            for m in pat.finditer(esc_text):
                candidate = m.group(0).strip() if pat is not _ABBR_NAME_RE else m.group(1).strip()
                if tag == "AGENCY_CONFIDENTIAL_INFO":
                    _header = text[:600].lower()
                    if candidate.split()[-1].lower() in _header:
                        continue
                if candidate.lower() not in _existing_proposed_lower:
                    all_proposed.append({
                        "text":        candidate,
                        "tag":         tag,
                        "reason":      "Identifier/name extracted from escalated passage",
                        "replacement": repl,
                        "context":     esc_text[:80],
                        "approved":    True,
                    })
                    _existing_proposed_lower.add(candidate.lower())

    # ── Post-processing: family-member name extraction ────────────────────────
    _FAMILY_PATTERN = re.compile(
        r'\b(?:daughter|son|sister|brother|mother|father|wife|husband|partner|'
        r'fianc[eé]e?|sibling|niece|nephew|granddaughter|grandson)\s+'
        r'(?:named\s+)?([A-Z][a-z]{1,})\b'
    )
    _pn_toks_fam = {t.lower() for t in patient_name.split() if len(t) >= 3}
    for fm in _FAMILY_PATTERN.finditer(text):
        name = fm.group(1)
        if name.lower() in _pn_toks_fam:
            continue
        if name.lower() not in _existing_proposed_lower:
            all_proposed.append({
                "text":        name,
                "tag":         "THIRD_PARTY_IDENTIFIER",
                "reason":      "Family member's first name (deterministic extraction)",
                "replacement": "[REDACTED - third-party personal data]",
                "context":     text[max(0, fm.start()-20):fm.end()+20],
                "approved":    True,
            })
            _existing_proposed_lower.add(name.lower())

    # ── Post-processing: remove clinician-only names ──────────────────────────
    # Suppress THIRD_PARTY_IDENTIFIER redactions for registered health
    # professionals appearing in their professional capacity.
    # Three guards — any ONE matching all occurrences is sufficient to suppress:
    #   (a) Name itself starts with "Dr" or "Prof" (e.g. "Dr M. Robertson").
    #   (b) Leading "Dr"/"Prof" prefix within 8 chars BEFORE each occurrence.
    #   (c) Trailing ", Consultant [Specialty]" or similar title within 60
    #       chars AFTER each occurrence (e.g. "Frank Miller, Consultant Optometrist").
    _CLINICIAN_TITLE_RE = re.compile(r'\b(?:Dr|Prof(?:essor)?)\s+', re.IGNORECASE)
    _CLINICIAN_NAME_START_RE = re.compile(r'^(?:Dr|Prof(?:essor)?)\b', re.IGNORECASE)
    _CLINICIAN_TRAILING_RE = re.compile(
        r',?\s*(?:Consultant|Senior\s+Consultant|Lead\s+Consultant|'
        r'Specialist|Principal|Registrar|Optometrist|Ophthalmologist|'
        r'Dentist|Radiographer)\b',
        re.IGNORECASE,
    )
    filtered_proposed = []
    for item in all_proposed:
        if item.get("tag") == "THIRD_PARTY_IDENTIFIER":
            name = (item.get("text") or "").strip()
            if " " in name:
                # Guard (a): name itself begins with Dr/Prof
                if _CLINICIAN_NAME_START_RE.match(name):
                    continue
                occurrences = list(re.finditer(
                    r'(?<!\w)' + re.escape(name) + r'(?!\w)', text, re.IGNORECASE
                ))
                # Guards (b) & (c): context around every occurrence
                if occurrences and all(
                    _CLINICIAN_TITLE_RE.search(text[max(0, m.start() - 8): m.start()])
                    or _CLINICIAN_TRAILING_RE.match(text[m.end(): m.end() + 60])
                    for m in occurrences
                ):
                    continue
        filtered_proposed.append(item)
    all_proposed = filtered_proposed

    # ── Role-title filter ─────────────────────────────────────────────────────
    # Remove THIRD_PARTY_IDENTIFIER items that look like role/job titles rather
    # than person names (e.g. "SEN coordinator", "care manager"). The DO NOT FLAG
    # section of the prompt instructs the LLM not to flag these, but it
    # occasionally does so — this filter is the code-level safety net.
    _ROLE_WORDS = {
        "coordinator", "worker", "officer", "manager", "director", "advisor",
        "adviser", "therapist", "counsellor", "nurse", "doctor", "consultant",
        "specialist", "assistant", "support", "teacher", "carer", "warden",
        "liaison", "lead", "head", "deputy", "supervisor", "practitioner",
    }
    all_proposed = [
        p for p in all_proposed
        if not (
            p.get("tag") == "THIRD_PARTY_IDENTIFIER"
            and any(
                word.lower().strip(".,;:") in _ROLE_WORDS
                for word in (p.get("text") or "").split()
                if word[:1].islower()   # only consider lowercase-starting words
            )
        )
    ]

    # ── Institutional-text filter ────────────────────────────────────────────
    # Remove proposed redactions whose text is clearly an organisation/agency
    # name rather than a person name. This catches cases where the LLM ignores
    # the DO NOT REDACT instruction for agency names (e.g. "Kent Adult Social",
    # "Suffolk County Council", "Bluebird Care Ltd").
    _INST_FILTER_WORDS = {
        "adult", "social", "care", "health", "mental", "children", "young",
        "services", "service", "authority", "council", "trust", "nhs",
        "royal", "hospital", "infirmary", "refuge", "centre", "center",
        "community", "primary", "secondary", "support", "unit",
        "foundation", "association", "police", "probation", "housing",
        # Local government / geographic body words
        "county", "borough", "district", "city", "parish", "metropolitan",
        # Org-type suffixes (even 1 institutional word + suffix = org)
        "limited", "ltd", "llp", "plc", "inc",
    }
    _ORG_SUFFIX_WORDS = {"limited", "ltd", "llp", "plc", "inc"}

    def _looks_institutional(t: str) -> bool:
        words = [w.rstrip('.,') for w in t.lower().split()]
        # Org suffix alone lowers the threshold: 1 other institutional word suffices
        if any(w in _ORG_SUFFIX_WORDS for w in words):
            return any(w in _INST_FILTER_WORDS for w in words)
        return sum(1 for w in words if w in _INST_FILTER_WORDS) >= 2

    all_proposed = [
        p for p in all_proposed
        if not _looks_institutional(p.get("text", ""))
    ]

    # ── Guardian name filter ─────────────────────────────────────────────────
    # In paediatric records the registered parent/guardian must not be redacted.
    # The prompt instructs the LLM to leave them alone, but as a safety net we
    # detect the guardian name from the record header and strip any proposed
    # redactions that target it.
    # Bidirectional check:
    #   • guardian substring of proposed text (e.g. proposed "Mrs Laura Sanders")
    #   • proposed text is substring of guardian (e.g. proposed "Laura Sanders"
    #     when guardian is "Mrs Laura Sanders") — the LLM may omit the title
    _guardian_name = _detect_guardian_name(text)
    if _guardian_name:
        _gn_lower = _guardian_name.strip().lower()
        all_proposed = [
            p for p in all_proposed
            if not (
                _gn_lower in (p.get("text") or "").strip().lower()
                or (p.get("text") or "").strip().lower() in _gn_lower
            )
        ]

    # ── Patient DOB filter ───────────────────────────────────────────────────
    # The LLM occasionally misidentifies the patient's own DOB as a third-party
    # date (e.g. "neighbour's DOB", "mother's DOB"). Since the patient is
    # entitled to their own DOB, remove any proposed redaction that exactly
    # matches the DOB from the record header.
    _patient_dob = _detect_patient_dob(text)
    if _patient_dob:
        all_proposed = [
            p for p in all_proposed
            if (p.get("text") or "").strip() != _patient_dob
        ]

    # ── Police / incident reference post-processor ───────────────────────────
    # The LLM sometimes misses police incident reference numbers even when
    # explicitly prompted. This regex scans the text for reference-number
    # patterns that appear near police/legal context keywords and adds them
    # as THIRD_PARTY_IDENTIFIER if not already proposed.
    _POLICE_REF_RE = re.compile(
        r'\b([A-Z]{1,4}/\d{4}/[A-Z0-9]{1,5}/\d{3,6})\b'
    )
    _POLICE_CONTEXT_RE = re.compile(
        r'(?i)(?:police|incident|crime|MIB|motor insur|reference|URN|log\s*number)',
    )
    _existing_texts = {(p.get("text") or "").strip() for p in all_proposed}
    for m in _POLICE_REF_RE.finditer(text):
        ref = m.group(1)
        if ref in _existing_texts:
            continue
        # Check surrounding context (200 chars window) for police/legal keywords
        window_start = max(0, m.start() - 100)
        window_end   = min(len(text), m.end() + 100)
        window = text[window_start:window_end]
        if _POLICE_CONTEXT_RE.search(window):
            all_proposed.append({
                "text":        ref,
                "tag":         "THIRD_PARTY_IDENTIFIER",
                "reason":      "Police/incident reference number linked to a third party.",
                "replacement": "[REDACTED - third-party personal data]",
            })
            _existing_texts.add(ref)

    # Pass patient_name so the expander never creates a redaction target that
    # matches the patient's own name parts (e.g. a shared family surname).
    all_proposed = _expand_name_redactions(all_proposed, text, patient_name)
    all_proposed = _expand_agency_contacts(all_proposed, text, patient_name)
    all_proposed = _expand_agency_professionals(all_proposed, text, patient_name)

    return {
        "proposed_redactions": all_proposed,
        "escalations":         all_escalations,
        "parse_ok":            parse_ok,
        "chunks_analysed":     len(chunks),
        "chars_total":         len(text),
    }, f"\n\n--- CHUNK BREAK ---\n\n".join(all_raw)


def apply_text_redactions(text: str, proposed_redactions: list) -> str:
    """
    Apply proposed redactions to plain text (not PDF). Returns redacted string.

    Only processes items that are approved (approved=True or key absent, treating
    absence as approved for backwards-compat) and have a non-empty 'text' field.

    Items are sorted by text length descending so longer phrases are replaced
    before their component words, avoiding partial-match corruption.
    """
    if not text or not proposed_redactions:
        return text

    # Filter to approved items with both text and replacement fields
    approved = [
        item for item in proposed_redactions
        if item.get("approved", True)
        and (item.get("text") or "").strip()
        and (item.get("replacement") or "").strip()
    ]

    # Sort longest-first to prevent partial-match corruption
    approved.sort(key=lambda x: len(x["text"]), reverse=True)

    result = text
    for item in approved:
        needle      = item["text"].strip()
        replacement = item["replacement"].strip()
        # Use word-boundary-aware regex where possible (word chars on both sides)
        pattern = r'(?<!\w)' + re.escape(needle) + r'(?!\w)'
        try:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        except re.error:
            # Fall back to plain string replacement if regex fails
            result = result.replace(needle, replacement)

    return result
