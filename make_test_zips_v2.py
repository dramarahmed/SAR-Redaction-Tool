"""
make_test_zips_v2.py
====================
Generates 5 test patient ZIP files for SAR redaction tool stress-testing.
Each ZIP contains 2-3 realistic NHS .txt documents plus a _manifest.json.

Run with:
  venv\\Scripts\\python.exe make_test_zips_v2.py
"""

import json
import zipfile
from pathlib import Path

OUTPUT_DIR = Path(r"C:\Users\Amar Ahmed\Downloads")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# PATIENT 1 — Alice SHARESURNAME
# Stress test: shared surname with perpetrator (husband Roger SHARESURNAME)
# =============================================================================

P1_MANIFEST = {
    "patient_name": "Alice SHARESURNAME",
    "patient_dob": "15/06/1962",
    "not_in_redacted": [
        "Roger SHARESURNAME",
        "03/11/1960",
        "07700 901234",
        "Sandra",
    ],
    "must_stay": [
        "Alice",
        "15/06/1962",
        "SHARESURNAME",
    ],
}

P1_DOC1 = """\
HARTFIELD ROAD MEDICAL CENTRE
GP CONSULTATION NOTE — CONFIDENTIAL

Date: 14 March 2024
Clinician: Dr Priya Mehta (GP)
Patient: Alice SHARESURNAME
DOB: 15/06/1962
NHS Number: 111 222 3333
Address: 47 Cartwright Avenue, Manchester M14 6PQ

Presenting complaint:
Mrs SHARESURNAME attended today accompanied by her husband Roger SHARESURNAME. The
consultation began as a routine review of her hypertension management. Mrs SHARESURNAME
appeared anxious and repeatedly looked towards her husband before answering questions. I
asked Roger SHARESURNAME to wait in reception so that I could complete a brief NICE
domestic violence routine enquiry with the patient.

Disclosure:
When seen alone, Alice disclosed that Roger has been controlling her access to finances
for approximately two years. She stated: "He checks my phone every night and I'm not
allowed to see anyone without him knowing." She described an incident last week in which
Roger pushed her against the kitchen wall following an argument about her attendance at
a church group. She said that her neighbour Sandra had witnessed shouting through the
wall on two separate occasions and had expressed concern, but Alice asked Sandra not to
call the police as she was afraid of what Roger might do.

Mental state: Distressed but coherent. No active suicidal ideation. Insight good.
Physical examination: No visible injuries today. Blood pressure 148/92 mmHg (elevated).

Clinical management:
- Blood pressure medication dose increased: Amlodipine 10mg OD
- Safety planning discussed and documented on EMIS under safeguarding flag
- DASH risk assessment completed — score 18 out of 24 = HIGH RISK
- Patient given domestic abuse helpline card concealed in medication information leaflet
- Referral to MARAC initiated (see separate referral note)
- Follow-up appointment booked for 4 weeks, coded as routine review

Alice declined referral to IDVA today but was given written information. She confirmed
she has a safe mobile phone Roger does not know about.

Signed: Dr Priya Mehta, MRCGP
"""

P1_DOC2 = """\
HARTFIELD ROAD MEDICAL CENTRE
MARAC REFERRAL — STRICTLY CONFIDENTIAL

Date: 14 March 2024
Referring clinician: Dr Priya Mehta (GP)
Completed by: Practice safeguarding lead

SUBJECT OF SAR (VICTIM):
Name: Alice SHARESURNAME
DOB: 15/06/1962
NHS Number: 111 222 3333
Address: 47 Cartwright Avenue, Manchester M14 6PQ

PERPETRATOR DETAILS:
Name: Roger SHARESURNAME
DOB: 03/11/1960
Relationship to victim: Husband (co-habiting)
Address: 47 Cartwright Avenue, Manchester M14 6PQ (same address as victim)
Telephone: 07700 901234
Occupation: Self-employed (exact occupation unknown)
Known to police: Unknown at time of referral

DASH RISK ASSESSMENT SUMMARY:
Total score: 18/24 — HIGH RISK
Risk factors identified include: financial control, physical assault, isolation from
support network, monitoring of communications, and escalating frequency of incidents
over a 6-month period.

NATURE OF RISK:
The perpetrator, Roger SHARESURNAME, has used a pattern of coercive and controlling
behaviour over an extended period. The most recent incident (approximately one week
prior to this referral) involved physical violence. The victim has reported that Roger
has threatened to harm himself if she leaves, which may be used as a further means of
control. There is a known third-party witness (a neighbour) but the victim has
requested this individual not be approached directly.

IMMEDIATE SAFETY MEASURES TAKEN:
- Safety plan recorded in patient record
- Emergency contact numbers provided
- EMIS safeguarding alert flag activated
- Patient aware of MARAC process and has consented to referral

REQUESTED ACTION:
Please convene MARAC panel with urgency given HIGH RISK designation.
All agencies attending must ensure the perpetrator is NOT made aware of this referral.

Referring practice: Hartfield Road Medical Centre, Manchester
Contact: Dr Priya Mehta via practice main line

Signed: Dr Priya Mehta, MRCGP   Date: 14/03/2024
"""

# =============================================================================
# PATIENT 2 — Peter FIRSTONLY
# Stress test: third parties referred to by first name only
# =============================================================================

P2_MANIFEST = {
    "patient_name": "Peter FIRSTONLY",
    "patient_dob": "28/02/1945",
    "not_in_redacted": [
        "Emma",
        "Janet",
        "Diane Okafor",
        "01925 000055",
    ],
    "must_stay": [
        "Peter",
        "28/02/1945",
    ],
}

P2_DOC1 = """\
MILLBROOK SURGERY
GP CONSULTATION NOTE — CONFIDENTIAL

Date: 07 February 2024
Clinician: Dr Samuel Okafor (GP)
Patient: Peter FIRSTONLY
DOB: 28/02/1945
NHS Number: 444 555 6666
Address: 12 Bluebell Close, Warrington WA4 2RR

Presenting complaint:
Mr FIRSTONLY attended for his quarterly medication review. He is known to the practice
with a background of type 2 diabetes mellitus, ischaemic heart disease, and moderate
cognitive impairment. He attended alone today.

Social history update:
Mr FIRSTONLY's daughter Emma visits regularly, usually twice a week. Emma has expressed
concern to the practice on previous occasions about her father's ability to manage his
medications independently. On 22 January 2024 Emma phoned the surgery to report that
she had found several unused insulin cartridges that should have been administered.
Emma was advised to contact the community diabetes nurse. There is no record that Emma
has been formally assessed as a carer.

Current carer:
Mr FIRSTONLY's wife Janet is his primary carer. Janet manages all medications on a
day-to-day basis, administers his morning and evening insulin, and accompanies him to
most clinical appointments. Janet has not been referred for a formal carer's assessment
but this was discussed with Mr FIRSTONLY today.

Clinical review:
HbA1c: 68 mmol/mol (slight improvement from 74 at last review — attributed to Janet's
improved medication administration routine). Blood pressure: 134/78 mmHg. Weight
stable. Foot check completed — no active ulceration.

Plan:
- Continue current medication regimen (Metformin 1g BD, Insulin Glargine 20 units ON,
  Aspirin 75mg OD, Atorvastatin 40mg OD, Ramipril 5mg OD)
- Refer Janet for formal carer's assessment via social care — consent obtained
- Request from Emma that she contacts surgery only via agreed communication pathway
- Repeat HbA1c in 3 months

Signed: Dr Samuel Okafor, MRCGP
"""

P2_DOC2 = """\
MILLBROOK SURGERY / CHESHIRE WEST SOCIAL CARE
CARER ASSESSMENT AND SUPPORT NOTE — CONFIDENTIAL

Date: 19 February 2024
Completed following referral from Dr Samuel Okafor, Millbrook Surgery

Patient: Peter FIRSTONLY
DOB: 28/02/1945
NHS Number: 444 555 6666
Address: 12 Bluebell Close, Warrington WA4 2RR

Social worker: Diane Okafor
Agency: Cheshire West and Chester Council, Adult Social Care
Direct contact: 01925 000055

Background:
This carer assessment was completed following a GP referral in respect of Mr Peter
FIRSTONLY. Mr FIRSTONLY has type 2 diabetes and moderate cognitive impairment. His wife
Janet is identified as his primary informal carer and has been managing all medications,
including insulin administration, since approximately September 2023.

Carer assessment (Janet):
Janet was interviewed at the family home on 19 February 2024. Janet reported feeling
overwhelmed by the responsibility of managing Peter's insulin regime and expressed
concern that she did not feel she had received adequate training. Janet indicated she
sometimes experiences anxiety about administering the wrong dose, particularly as Peter's
prescription was recently changed. Janet confirmed she is not currently in receipt of
any carer's support services and has not had a break from caring in over four months.

Janet demonstrated competence in the physical tasks of caring; however, her emotional
wellbeing is a concern. She was offered referral to the local carer's support group
and the Carers Trust helpline.

Risk assessment:
The arrangement is sustainable in the short term, provided Janet receives additional
training from the community diabetes nurse. A safety-netting plan has been agreed.
Emma (Mr FIRSTONLY's daughter) has also been noted as providing supplementary support;
however, Emma's role is informal and she is not available on a daily basis.

Recommendations:
1. Community diabetes nurse to visit and provide insulin administration refresher for Janet
2. Janet to be referred to the Carers Trust for emotional wellbeing support
3. Telecare pendant alarm for Mr FIRSTONLY to be arranged via equipment service
4. Review in six months or sooner if situation deteriorates

Signed: Diane Okafor, Social Worker
Cheshire West and Chester Council, Adult Social Care
Tel: 01925 000055
"""

# =============================================================================
# PATIENT 3 — Nuala MISFILED
# Stress test: misfiled letter with full demographics of another patient
# =============================================================================

P3_MANIFEST = {
    "patient_name": "Nuala MISFILED",
    "patient_dob": "12/09/1970",
    "not_in_redacted": [
        "Dorothy OTHERPATIENT",
        "07/04/1952",
        "222 333 4444",
        "15 Elm Road",
        "Dorothy",
    ],
    "must_stay": [
        "Nuala",
        "12/09/1970",
    ],
}

P3_DOC1 = """\
RIVERSIDE HEALTH CENTRE
ADMINISTRATIVE NOTE — FILING ERROR IDENTIFIED

Date: 22 January 2024
Completed by: Jade Thornton, Medical Records Administrator

Patient record: Nuala MISFILED
DOB: 12/09/1970
NHS Number: 777 888 9999
Address: 3 Sycamore Drive, Chester CH2 4LN

Nature of filing error:
During a routine audit of clinical correspondence, the following letter was identified
as incorrectly filed within the medical record of Nuala MISFILED. The letter below
appears to have been filed in error and belongs to a different patient entirely. The
demographics, NHS number, and clinical content do not match those of Nuala MISFILED
in any respect.

--- BEGIN MISFILED LETTER ---

Chester Royal Infirmary
Gynaecology Outpatient Department
Eastgate Street, Chester CH1 1RB

Date: 09 January 2024
Re: Mrs Dorothy OTHERPATIENT
DOB: 07/04/1952
NHS Number: 222 333 4444
Address: 15 Elm Road, Chester CH1 9QQ

Dear Dr Leighton,

Thank you for referring Mrs Dorothy OTHERPATIENT for investigation of postmenopausal
bleeding. Mrs OTHERPATIENT attended the colposcopy clinic on 08 January 2024.
Transvaginal ultrasound demonstrated an endometrial thickness of 6mm. Endometrial
biopsy was performed. We will write again when histology results are available.

Yours sincerely,
Mr Jonathan Fielding, Consultant Gynaecologist

--- END MISFILED LETTER ---

Action taken:
The misfiled letter has been flagged for removal from Nuala MISFILED's record pending
confirmation of correct patient. The relevant consultant's secretary has been notified.
A copy has been placed in a pending tray for filing to the correct patient record once
identity has been verified.

Signed: Jade Thornton, Medical Records Administrator
"""

P3_DOC2 = """\
RIVERSIDE HEALTH CENTRE
GP CONSULTATION NOTE — CONFIDENTIAL

Date: 15 March 2024
Clinician: Dr Helen Leighton (GP Principal)
Patient: Nuala MISFILED
DOB: 12/09/1970
NHS Number: 777 888 9999
Address: 3 Sycamore Drive, Chester CH2 4LN

Presenting complaint:
Ms MISFILED attended for a routine annual review. She has a background of well-controlled
hypothyroidism and mild anxiety disorder. She has no other significant medical history.

History:
Ms MISFILED reports feeling well overall. She has been taking Levothyroxine 75mcg OD
consistently and has experienced no side effects. She reports her mood has been stable
and she has continued attending monthly CBT sessions with a psychology service, which
she describes as helpful.

Examination:
General appearance: Well. Weight: 68kg. BMI: 24.1. Blood pressure: 118/74 mmHg.
Heart rate: 72 bpm, regular. Thyroid: not palpable. No lymphadenopathy.

Investigations:
Recent TFTs (01 March 2024): TSH 1.8 mU/L (within range), FT4 16.4 pmol/L (normal).
No further investigations required at this time.

Plan:
- Continue Levothyroxine 75mcg OD
- Continue psychological support — patient reports good progress
- Repeat TFTs in 12 months
- Patient to return sooner if symptomatic

No safeguarding concerns identified. No third-party information discussed or recorded
at this consultation.

Signed: Dr Helen Leighton, MRCGP
"""

# =============================================================================
# PATIENT 4 — Kwame COMPLAINT
# Stress test: CLINICIAN_CONTEXT_AMBIGUOUS — Dr Amara Osei as complaint subject
# =============================================================================

P4_MANIFEST = {
    "patient_name": "Kwame COMPLAINT",
    "patient_dob": "05/07/1978",
    "not_in_redacted": [],
    "must_stay": [
        "Kwame",
        "05/07/1978",
        "Dr Amara Osei",
    ],
    "escalation_expected": [
        "Dr Amara Osei",
    ],
}

P4_DOC1 = """\
NORTHGATE SURGERY
FORMAL PATIENT COMPLAINT — RECEIVED IN WRITING

Date received: 02 March 2024
Patient: Kwame COMPLAINT
DOB: 05/07/1978
NHS Number: 100 200 3000
Address: 88 Pennington Road, Birmingham B15 2TT

Letter of complaint (verbatim):

Dear Practice Manager,

I am writing to formally complain about my consultation with Dr Amara Osei at your
surgery on 14 February 2024. I attended because I have been experiencing persistent
chest pain over several weeks. During this appointment, Dr Amara Osei was dismissive
of my concerns and failed to conduct any physical examination despite my repeated
requests. When I explained that the pain was radiating to my left arm, Dr Amara Osei
told me it was "probably muscular" and ended the appointment after less than five minutes.

I was given no investigation, no referral, and no safety-netting advice. I subsequently
attended A&E the following day, where an ECG revealed ST-segment changes and I was
admitted to the cardiac care unit for three days. I was discharged with a diagnosis of
NSTEMI and a prescription for dual antiplatelet therapy.

I believe Dr Amara Osei's conduct during that consultation fell well below the standard
expected of a GP and may have placed my life at risk. I am requesting a full written
response, a copy of my medical records from that date, and an explanation of the steps
the practice will take to prevent a similar occurrence in the future.

I reserve the right to refer this matter to NHS England and the General Medical Council
if I am not satisfied with the practice's response.

Yours sincerely,
Kwame COMPLAINT
05/07/1978

---

PRACTICE MANAGER'S LOG NOTE:
Complaint received 02/03/2024. Acknowledged to patient 04/03/2024 (within 3 working
days per NHS Complaints Procedure). Complaint allocated to Dr Sarah Yates (Clinical
Lead) for clinical review. Dr Amara Osei informed and invited to provide a written
account of the 14 February consultation. EMIS record for that date requested. Target
response date: 02/04/2024.
"""

P4_DOC2 = """\
NORTHGATE SURGERY
GP CLINICAL CONSULTATION NOTE

Date: 19 March 2024
Clinician: Dr Amara Osei (GP)
Patient: Kwame COMPLAINT
DOB: 05/07/1978
NHS Number: 100 200 3000
Address: 88 Pennington Road, Birmingham B15 2TT

Presenting complaint:
Mr COMPLAINT attended for a post-discharge medication review following his recent
admission to Birmingham City Hospital Cardiac Care Unit (CCU), 15–17 February 2024.
Diagnosis on discharge: Non-ST-elevation myocardial infarction (NSTEMI).

History and current status:
Mr COMPLAINT is now on dual antiplatelet therapy (Aspirin 75mg OD and Ticagrelor
90mg BD), Atorvastatin 80mg OD, Bisoprolol 2.5mg OD, and Ramipril 2.5mg OD as per
the discharge letter from the cardiology team at Birmingham City Hospital.

He reports his chest pain has resolved. He is mobilising without symptoms and feels
significantly better than prior to admission. He has no current breathlessness, ankle
swelling, or palpitations.

Examination:
Pulse: 62 bpm, regular. Blood pressure: 126/80 mmHg. Auscultation: heart sounds
normal, no murmurs. Chest clear. No peripheral oedema.

ECG: Performed in clinic today — sinus rhythm, no acute changes. Prior ST-segment
changes have resolved.

Management plan:
- Prescriptions for all cardiac medications issued
- Patient referred to cardiac rehabilitation programme (letter sent today)
- Repeat ECG and blood tests (renal function, lipids) in 4 weeks
- Echocardiogram requested (community cardiology service)
- Patient advised regarding lifestyle: diet, smoking cessation (patient is a
  non-smoker), alcohol limits, and graduated return to physical activity
- Patient provided with BHF information booklet

Follow-up: In 4 weeks or sooner if symptomatic.

Signed: Dr Amara Osei, MRCGP
"""

# =============================================================================
# PATIENT 5 — Beatrice MULTITYPE
# Stress test: everything at once — DA perpetrator + first-name-only family +
#              misfiled DOB + social worker + indirect identifier
# =============================================================================

P5_MANIFEST = {
    "patient_name": "Beatrice MULTITYPE",
    "patient_dob": "19/11/1953",
    "not_in_redacted": [
        "Gerald MULTITYPE",
        "11/03/1950",
        "07700 902222",
        "Sophie",
        "Yvonne Bridges",
        "01244 000077",
        "Lily",
        "22/06/1948",
        "444 555 6666",
        "the woman who runs the post office on Acacia Street",
    ],
    "must_stay": [
        "Beatrice",
        "19/11/1953",
    ],
}

P5_DOC1 = """\
ACACIA STREET FAMILY PRACTICE
GP CONSULTATION NOTE — CONFIDENTIAL

Date: 05 February 2024
Clinician: Dr Fatima Al-Rashid (GP)
Patient: Beatrice MULTITYPE
DOB: 19/11/1953
NHS Number: 321 654 9870
Address: 22 Orchard Way, Chester CH4 8LQ

Presenting complaint:
Mrs MULTITYPE attended complaining of a painful bruise to her left forearm. She
initially stated she had knocked it on a door frame. When asked directly, and after
I confirmed the consultation was confidential, she disclosed that her husband Gerald
MULTITYPE had grabbed her arm during an argument four days ago.

Domestic abuse disclosure:
Mrs MULTITYPE stated that Gerald has become increasingly aggressive over the past
year, since his retirement. She describes him checking her whereabouts constantly,
demanding to know who she has spoken to, and criticising her in front of family
members. She mentioned their daughter Sophie has noticed a change in Gerald's
behaviour and is worried. Sophie has visited more frequently in recent months and
has on two occasions asked Gerald directly to stop shouting, which Gerald resented.
Sophie also confided in Beatrice that she witnessed her father throw a cup at the wall
last month, though Beatrice asked Sophie not to report this anywhere.

A neighbour, whom the patient described as "the woman who runs the post office on
Acacia Street," apparently commented to the patient that she looked frightened when
Beatrice came in to collect a parcel without Gerald last week. Beatrice found the
comment distressing, as she fears it means her situation is becoming visible in the
community.

Physical examination:
Left forearm: 4cm x 3cm bruise, consistent with a grip injury. No fracture suspected
clinically. Photographs taken with consent for safeguarding records.

DASH risk assessment: Score 14/24 — STANDARD RISK at present, but pattern suggests
escalation may occur. Will monitor and re-assess.

Plan:
- Domestic abuse safety plan discussed and documented
- Patient given concealed helpline card
- Referral to safeguarding team initiated — see separate safeguarding note
- Sophie not to be contacted without patient consent; however, Beatrice indicated she
  would speak with Sophie herself
- Bruise management: ice, elevation, no further intervention required

Signed: Dr Fatima Al-Rashid, MRCGP
"""

P5_DOC2 = """\
ACACIA STREET FAMILY PRACTICE / CHESHIRE WEST CHILDREN'S SAFEGUARDING
SAFEGUARDING REFERRAL NOTE — STRICTLY CONFIDENTIAL

Date: 06 February 2024
Referring clinician: Dr Fatima Al-Rashid, GP
Completed in conjunction with: Practice safeguarding lead

PATIENT (SUBJECT OF SAR):
Name: Beatrice MULTITYPE
DOB: 19/11/1953
NHS Number: 321 654 9870
Address: 22 Orchard Way, Chester CH4 8LQ

PERPETRATOR BLOCK:
Name: Gerald MULTITYPE
DOB: 11/03/1950
Relationship: Husband (co-habiting)
Address: 22 Orchard Way, Chester CH4 8LQ (same address)
Telephone: 07700 902222
Occupation: Retired (former site manager)
Previous domestic abuse history: Unknown to GP surgery — DVDS check requested

CHILD CONCERN:
During the disclosure, Beatrice mentioned that her granddaughter Lily (approximate
date of birth: 2019, making her approximately 5 years old) visits the family home
regularly, usually one weekend per fortnight. Beatrice expressed concern that Lily
should not be present during Gerald's episodes of anger. Beatrice confirmed that Lily
is the daughter of her son Marcus (Gerald's son), who is aware of the visits.

Given Lily's age and the pattern of domestic violence in the household, a referral
to Children's Social Care is required under Working Together 2023 guidance.

SOCIAL WORKER ALLOCATED:
Yvonne Bridges
Cheshire West and Chester Children's Safeguarding Team
Direct line: 01244 000077

DASH RISK SUMMARY:
Score 14/24 at time of referral — STANDARD RISK, however the household includes
a young child and the perpetrator's behaviour is escalating. Yvonne Bridges has
confirmed initial assessment will be completed within 10 working days.

MARAC:
Not referred at this stage given standard risk score. To be reviewed at 6-week
follow-up. If DASH score increases at next consultation, MARAC referral will be made.

ACTIONS:
1. Children's Social Care informed — Yvonne Bridges allocated
2. Police disclosure form completed
3. Safeguarding flag added to EMIS record of Beatrice MULTITYPE
4. Gerald MULTITYPE's identity shared with police under DVDS

Signed: Dr Fatima Al-Rashid, MRCGP   Date: 06/02/2024
"""

P5_DOC3 = """\
ACACIA STREET FAMILY PRACTICE
ADMINISTRATIVE NOTE — MISFILED CORRESPONDENCE IDENTIFIED

Date: 12 February 2024
Completed by: Chloe Finch, Senior Receptionist

Patient record: Beatrice MULTITYPE
DOB: 19/11/1953
NHS Number: 321 654 9870

Filing error:
The following hospital letter was discovered incorrectly filed within the above
patient's medical record during a routine scan-and-file audit. The demographics
and clinical content are entirely unrelated to Beatrice MULTITYPE.

--- BEGIN MISFILED DOCUMENT ---

Warrington Hospital NHS Foundation Trust
Trauma and Orthopaedics Outpatient Department
Lovely Lane, Warrington WA5 1QG

Date: 29 January 2024
Re: Mr Raymond WRONGPERSON
DOB: 22/06/1948
NHS Number: 444 555 6666
Address: 8 Park Lane, Warrington WA2 7HH

Dear GP,

Thank you for referring Mr Raymond WRONGPERSON with ongoing right hip pain. Mr
WRONGPERSON attended the orthopaedic clinic on 26 January 2024. Plain radiographs
demonstrate moderate osteoarthritis of the right hip with joint space narrowing.
We have placed Mr WRONGPERSON on the waiting list for a right total hip replacement.
He has been commenced on Naproxen 500mg BD with a proton pump inhibitor.

Yours sincerely,
Mr David Greenwood, Consultant Orthopaedic Surgeon

--- END MISFILED DOCUMENT ---

Action:
Document flagged for removal from Beatrice MULTITYPE's record and referred to
medical records manager for filing to the correct patient. Orthopaedic secretary
contacted by telephone.

Signed: Chloe Finch, Senior Receptionist
"""


# =============================================================================
# Helper: build a ZIP in memory and write it
# =============================================================================

def make_zip(zip_path: Path, files: dict):
    """
    files: dict of {filename_in_zip: content_string_or_bytes}
    Writes the ZIP to zip_path.
    """
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            zf.writestr(fname, content)
    print(f"  Created: {zip_path}")


# =============================================================================
# Main
# =============================================================================

def main():
    patients = [
        {
            "zip_name": "Test-Alice-SHARESURNAME-v2.zip",
            "files": {
                "01_GP_Consultation_Domestic_Disclosure.txt": P1_DOC1,
                "02_MARAC_Referral.txt": P1_DOC2,
                "_manifest.json": json.dumps(P1_MANIFEST, indent=2, ensure_ascii=False),
            },
        },
        {
            "zip_name": "Test-Peter-FIRSTONLY-v2.zip",
            "files": {
                "01_GP_Consultation_Note.txt": P2_DOC1,
                "02_Carer_Assessment_Note.txt": P2_DOC2,
                "_manifest.json": json.dumps(P2_MANIFEST, indent=2, ensure_ascii=False),
            },
        },
        {
            "zip_name": "Test-Nuala-MISFILED-v2.zip",
            "files": {
                "01_Admin_Misfiled_Letter.txt": P3_DOC1,
                "02_GP_Consultation_Note.txt": P3_DOC2,
                "_manifest.json": json.dumps(P3_MANIFEST, indent=2, ensure_ascii=False),
            },
        },
        {
            "zip_name": "Test-Kwame-COMPLAINT-v2.zip",
            "files": {
                "01_Formal_Complaint_Letter.txt": P4_DOC1,
                "02_GP_Clinical_Note_Post_Discharge.txt": P4_DOC2,
                "_manifest.json": json.dumps(P4_MANIFEST, indent=2, ensure_ascii=False),
            },
        },
        {
            "zip_name": "Test-Beatrice-MULTITYPE-v2.zip",
            "files": {
                "01_GP_Consultation_DA_Disclosure.txt": P5_DOC1,
                "02_Safeguarding_Referral.txt": P5_DOC2,
                "03_Admin_Misfiled_Letter.txt": P5_DOC3,
                "_manifest.json": json.dumps(P5_MANIFEST, indent=2, ensure_ascii=False),
            },
        },
    ]

    print(f"\nWriting test ZIPs to: {OUTPUT_DIR}\n")
    for p in patients:
        zip_path = OUTPUT_DIR / p["zip_name"]
        make_zip(zip_path, p["files"])

    print(f"\nAll {len(patients)} ZIPs created successfully.")


if __name__ == "__main__":
    main()
