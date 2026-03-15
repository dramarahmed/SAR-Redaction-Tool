"""
make_real_records_v2.py
=======================
Creates 10 realistic NHS patient record ZIPs (Records 11-20) for the SAR
redaction test harness. Each covers a distinct redaction challenge:
  11 – Prison healthcare / officer as third party
  12 – Interpreter personal data
  13 – Student mental health / external counsellor
  14 – Child-to-adult transition / non-parent copied
  15 – Genetic data / family member third-party
  16 – Legal/insurance claims handler
  17 – Partner notification (STI)
  18 – Social care overlap / carer personal data
  19 – Child record / parent support coordinator
  20 – Research participant / coordinator email
"""

import json
import os
import zipfile

DOWNLOADS = r"C:\Users\Amar Ahmed\Downloads"

RECORDS = [
    # ------------------------------------------------------------------ 11
    {
        "zip_name": "Test-Real-White-v2.zip",
        "txt_name": "2024-06-11_rec11_prison_health_WHITE_Daniel_1000.txt",
        "manifest": {
            "patient_name": "Daniel White",
            "patient_dob": "19/08/1989",
            "not_in_redacted": ["C. Murray", "Officer C. Murray"],
            "must_stay": [
                "Daniel White", "19/08/1989", "Dr L. Barker",
                "Salbutamol", "Hydrocortisone",
            ],
            "escalation_expected": [],
        },
        "text": """\
PRISON HEALTHCARE RECORD
HMP Lancaster Farms — Healthcare Unit
Tel: 01524 000011

Patient:    Mr Daniel WHITE
DOB:        19/08/1989
NHS Number: 578 668 3320
Location:   Wing C, Cell 7
Date:       11 June 2024
Clinician:  Dr L. Barker, Prison Healthcare GP

BACKGROUND
Asthma diagnosed 2015. Mild eczema affecting both forearms.

CONSULTATION — 11 June 2024
Patient presented with a 3-day history of worsening cough, wheeze and mild shortness of breath.
During escort to the Healthcare Unit, officer C. Murray noted that the patient had not been using his Salbutamol inhaler as prescribed.
On examination: mild expiratory wheeze bilaterally. Peak flow 380 L/min (80% predicted). No fever.
Impression: mild acute asthma exacerbation.
Management: Salbutamol 100 mcg × 4 puffs via spacer administered in clinic. Stepped-up to regular Beclometasone 100 mcg BD. Advised to keep inhaler accessible at all times.

INCIDENT NOTE
A note was made by Healthcare staff that the patient's Hydrocortisone cream (prescribed for eczema) had been borrowed without permission by his cellmate (identity not recorded in this health record; referenced in the separate security file). The patient was advised to keep all medications secured.

MEDICATION SUMMARY
- Salbutamol 100 mcg inhaler PRN (via spacer)
- Beclometasone 100 mcg inhaler BD (new)
- Hydrocortisone 1% cream — apply to affected areas BD

OUTSTANDING ACTIONS
- Review at next weekly healthcare clinic.
- Liaise with wing staff regarding secure medication storage.

Dr L. Barker, Prison Healthcare GP
""",
    },
    # ------------------------------------------------------------------ 12
    {
        "zip_name": "Test-Real-Wu-v2.zip",
        "txt_name": "2024-07-03_rec12_diabetes_review_WU_MeiLing_1000.txt",
        "manifest": {
            "patient_name": "Mei Ling Wu",
            "patient_dob": "02/03/1970",
            "not_in_redacted": ["Anna S.", "07711 000212"],
            "must_stay": [
                "Mei Ling Wu", "02/03/1970", "Dr K. Farmer",
                "Lingua Services", "Type 2 diabetes", "metformin",
            ],
            "escalation_expected": [],
        },
        "text": """\
DIABETES ANNUAL REVIEW
Broad Street Surgery, 22 Broad Street, Reading, RG1 8UE
Tel: 0118 000012

Patient:    Ms Mei Ling WU
DOB:        02/03/1970
NHS Number: 684 440 2261
Address:    Flat 8, Willow Court, Reading, RG1 8UE
Date:       03 July 2024
Clinician:  Dr K. Farmer, GP

BACKGROUND
Type 2 diabetes mellitus, diagnosed 2016. Hypertension. English is not the patient's first language; interpreter support is required for all appointments.

CONSULTATION
An interpreter was provided by Lingua Services for today's appointment. The interpreter was Anna S. (Tel: 07711 000212), a telephone interpreter in Cantonese.
HbA1c: 54 mmol/mol (improved from 62 last year). Blood pressure: 138/86 mmHg.
Patient reports good adherence to metformin. Dietary advice discussed with interpreter support.

CORRESPONDENCE — Attached Documents
1. Clinic letter from Reading Diabetes Centre confirming satisfactory review.
2. Interpreter evaluation form: signed by Anna S., includes her mobile number 07711 000212 and staff reference code LG-5509.

OUTSTANDING ACTIONS
- Repeat HbA1c and renal function in 6 months.
- BP medication review — consider dose titration.
- Ensure interpreter booked for all future appointments via Lingua Services.

Dr K. Farmer, GP
""",
    },
    # ------------------------------------------------------------------ 13
    {
        "zip_name": "Test-Real-Dutta-v2.zip",
        "txt_name": "2024-09-17_rec13_student_mh_DUTTA_Oliver_1000.txt",
        "manifest": {
            "patient_name": "Oliver Dutta",
            "patient_dob": "11/05/2005",
            "not_in_redacted": ["Liz Manning", "liz.manning@uon.ac.uk"],
            "must_stay": [
                "Oliver Dutta", "11/05/2005", "Dr S. Holloway",
                "depression", "University of Nottingham",
            ],
            "escalation_expected": [],
        },
        "text": """\
MENTAL HEALTH CONSULTATION — STUDENT PATIENT
Park View Practice, 30 Castle Boulevard, Nottingham, NG5 5AA
Tel: 0115 000013

Patient:    Mr Oliver DUTTA
DOB:        11/05/2005
NHS Number: 442 559 3308
Address:    14 Park Terrace, Nottingham, NG5 5AA
Date:       17 September 2024
Clinician:  Dr S. Holloway, GP

BACKGROUND
Oliver is in his first year at the University of Nottingham. He has a history of depression since his A-level year; previously managed with brief CBT in his home area (Sheffield). Newly registered at this practice.

CONSULTATION
Patient reports low mood, significant homesickness and difficulty engaging with lectures. He disclosed a single episode of superficial self-harm (cutting) approximately six weeks ago, which has not recurred. No current suicidal ideation. Risk assessed as low.

EXTERNAL AGENCY CORRESPONDENCE
Email received from Liz Manning, Senior Counsellor, University of Nottingham Student Services (liz.manning@uon.ac.uk):
"Dear Dr Holloway, Oliver Dutta has been receiving weekly counselling sessions with our team since September. He has consented to us sharing this information with his GP. We would welcome a joint care planning conversation in due course."

MANAGEMENT
Fluoxetine 20 mg OD commenced. Referral to NHS Talking Therapies placed. Care coordination ongoing with University Counselling Service.

OUTSTANDING ACTIONS
- Review in 4 weeks (medication effect).
- Respond to University Counselling Service.

Dr S. Holloway, GP
""",
    },
    # ------------------------------------------------------------------ 14
    {
        "zip_name": "Test-Real-Sanders-v2.zip",
        "txt_name": "2024-10-01_rec14_transition_SANDERS_Noah_1000.txt",
        "manifest": {
            "patient_name": "Noah Sanders",
            "patient_dob": "05/04/2011",
            "not_in_redacted": ["James Walker", "Mrs D. Briggs"],
            "must_stay": [
                "Noah Sanders", "05/04/2011", "Dr J. Cole",
                "autism", "SEN coordinator", "Mrs Laura Sanders",
            ],
            "escalation_expected": [],
        },
        "text": """\
CHILD AND ADOLESCENT HEALTH — TRANSITION PLANNING RECORD
Rowbarton Surgery, 8 Rowbarton Close, Taunton, TA1 3LT
Tel: 01823 000014

Patient:    Noah SANDERS (child)
DOB:        05/04/2011
NHS Number: 915 332 7810
Address:    2 Ivy Close, Taunton, TA1 3LT
Registered Parent/Guardian: Mrs Laura Sanders (mother)
Date:       01 October 2024
Clinician:  Dr J. Cole, GP

BACKGROUND
Autism spectrum disorder (ASD) diagnosed 2017 by Child and Adolescent Mental Health Services (CAMHS). Noah is currently 13 and approaching the transition from paediatric to adult services.

TRANSITION PLANNING MEETING — 1 October 2024
Attended by: Noah (with assent), Mrs Laura Sanders (mother), Dr J. Cole (GP), and Mr James Walker (Mrs Sanders' partner).
Note: Mr James Walker attended in a supportive capacity for Mrs Sanders. He is not a registered parent or legal guardian and has no clinical role in Noah's care.

The transition plan was discussed in detail. Noah is to be referred to adult autism services within the next 12 months.

SCHOOL CORRESPONDENCE
Psychology letter from the CAMHS Clinical Psychologist was copied to:
- Mrs D. Briggs, SEN Coordinator, St Augustine's Academy, Taunton.
- Mrs Laura Sanders (mother).
- Mr James Walker (Mrs Sanders' partner, at her specific request).

Mrs D. Briggs has confirmed that additional support will be put in place for Noah ahead of his GCSEs.

SAFEGUARDING
No current safeguarding concerns. Routine checks completed.

OUTSTANDING ACTIONS
- Initiate adult autism services referral.
- Review in 6 months.

Dr J. Cole, GP
""",
    },
    # ------------------------------------------------------------------ 15
    {
        "zip_name": "Test-Real-Baker-v2.zip",
        "txt_name": "2024-08-14_rec15_genetics_BAKER_Eleanor_1000.txt",
        "manifest": {
            "patient_name": "Eleanor Baker",
            "patient_dob": "03/06/1980",
            "not_in_redacted": ["Emma Baker", "emma.baker@personalmail.com"],
            "must_stay": [
                "Eleanor Baker", "03/06/1980", "Dr L. Greaves",
                "BRCA1", "breast cancer",
            ],
            "escalation_expected": [],
        },
        "text": """\
GENETICS REFERRAL AND RESULTS RECORD
Durham City Health Centre, 27 North Street, Durham, DH1 4LH
Tel: 0191 000015

Patient:    Ms Eleanor BAKER
DOB:        03/06/1980
NHS Number: 380 441 0915
Address:    27 North Street, Durham, DH1 4LH
Date:       14 August 2024
Clinician:  Dr L. Greaves, GP

BACKGROUND
Strong family history of breast cancer — mother and maternal aunt both diagnosed before age 50. Referred to the Northern Regional Genetics Service for BRCA testing.

RESULTS — Received 10 August 2024
Pathogenic variant identified: BRCA1 (c.5266dupC, p.Gln1756Profs). This result significantly increases Eleanor's lifetime risk of breast and ovarian cancer.

Genetic counsellor recommendation: risk-reduction surveillance or prophylactic surgery to be discussed at the oncology MDT.

FAMILY MEMBER NOTIFICATION
The genetics team noted that Eleanor's sister, Emma Baker (DOB: 15/04/1978, personal email: emma.baker@personalmail.com), has also been contacted directly by the genetics service and has been offered testing in her own right. This is recorded here as contextual information; Emma Baker's medical details are held separately and do not form part of Eleanor's record.

MANAGEMENT
- Referral to high-risk breast surveillance clinic.
- Oncology MDT discussion regarding prophylactic options.
- Psychological support offered and accepted.

OUTSTANDING ACTIONS
- Confirmation of MDT appointment.
- Annual mammogram and MRI from age 30 (already commenced).

Dr L. Greaves, GP
""",
    },
    # ------------------------------------------------------------------ 16
    {
        "zip_name": "Test-Real-Nicholson-v2.zip",
        "txt_name": "2024-07-22_rec16_back_pain_NICHOLSON_Craig_1000.txt",
        "manifest": {
            "patient_name": "Craig Nicholson",
            "patient_dob": "25/12/1975",
            "not_in_redacted": ["Sarah Thompson", "sthompson@reedclaims.co.uk"],
            "must_stay": [
                "Craig Nicholson", "25/12/1975", "Dr M. Robertson",
                "Thompson & Reed LLP", "Kirkcaldy",
            ],
            "escalation_expected": [],
        },
        "text": """\
CHRONIC PAIN MANAGEMENT AND LEGAL CORRESPONDENCE RECORD
Kirkcaldy Medical Group, 13 Bridge Street, Kirkcaldy, KY1 2PA
Tel: 01592 000016

Patient:    Mr Craig NICHOLSON
DOB:        25/12/1975
NHS Number: 222 774 8864
Address:    13 Bridge Street, Kirkcaldy, KY1 2PA
Date:       22 July 2024
Clinician:  Dr M. Robertson, GP

BACKGROUND
Chronic lumbar back pain following a workplace accident in March 2022. Ongoing physiotherapy. Litigation in progress.

CONSULTATION
Craig reports persistent pain at 6/10. Current analgesic regime reviewed; Naproxen increased. Physiotherapy to continue.

LEGAL CORRESPONDENCE
A formal written request for a medical report was received from Thompson & Reed LLP (solicitors), acting on behalf of the patient's employer's insurers. The patient has provided written consent for release.

Accompanying email from claims handler Sarah Thompson (sthompson@reedclaims.co.uk):
"Dear Dr Robertson, I am handling the personal injury claim on behalf of our client. Please could you provide a medical report covering Mr Nicholson's prognosis and capacity for work. Our reference: TR/CR/2022/5571."

OUTSTANDING ACTIONS
- Medical report to be prepared and sent to Thompson & Reed LLP.
- Next pain review in 8 weeks.

Dr M. Robertson, GP
""",
    },
    # ------------------------------------------------------------------ 17
    {
        "zip_name": "Test-Real-Patel-v2.zip",
        "txt_name": "2024-05-29_rec17_sexual_health_PATEL_Priya_1000.txt",
        "manifest": {
            "patient_name": "Priya Patel",
            "patient_dob": "14/10/1998",
            "not_in_redacted": ["Rajan Mehta", "07712 000317"],
            "must_stay": [
                "Priya Patel", "14/10/1998", "Dr C. Foster",
                "Chlamydia", "Azithromycin",
            ],
            "escalation_expected": [],
        },
        "text": """\
SEXUAL HEALTH CONSULTATION AND PARTNER NOTIFICATION RECORD
Queen's Road Surgery, 45 Queen's Road, Birmingham, B12 8JJ
Tel: 0121 000017

Patient:    Ms Priya PATEL
DOB:        14/10/1998
NHS Number: 520 882 9111
Address:    45 Queen's Road, Birmingham, B12 8JJ
Date:       29 May 2024
Clinician:  Dr C. Foster, GP

BACKGROUND
Attendance following contact tracing notification from the NHS Sexual Health Contact Tracing Service.

CONSULTATION
Patient attended following a partner notification. She reports no symptoms. Testing performed.

RESULTS
NAAT: Chlamydia trachomatis — POSITIVE.
Patient was informed and treated with Azithromycin 1 g stat.

PARTNER NOTIFICATION
Public Health (Sexual Health Team) initiated contact tracing. The notified partner is recorded here for clinical completeness as Rajan Mehta (Tel: 07712 000317, a contact provided during contact tracing). Mr Mehta was contacted independently by the sexual health team and offered testing. His results do not form part of Ms Patel's record.

OUTSTANDING ACTIONS
- Test of cure at 6 weeks.
- Advise abstinence until treatment complete.
- Public Health to confirm partner notification outcome.

Dr C. Foster, GP
""",
    },
    # ------------------------------------------------------------------ 18
    {
        "zip_name": "Test-Real-Thompson-v2.zip",
        "txt_name": "2024-11-08_rec18_dementia_care_THOMPSON_Hannah_1000.txt",
        "manifest": {
            "patient_name": "Hannah Thompson",
            "patient_dob": "29/11/1963",
            "not_in_redacted": ["David Rees", "Fiona Booth", "07700 000518"],
            "must_stay": [
                "Hannah Thompson", "29/11/1963", "Dr I. West",
                "dementia", "Kent Adult Social Care",
            ],
            "escalation_expected": [],
        },
        "text": """\
DEMENTIA CARE RECORD — MULTIDISCIPLINARY CORRESPONDENCE
Canterbury Health Centre, 7 Orchard Lane, Canterbury, CT2 8LU
Tel: 01227 000018

Patient:    Mrs Hannah THOMPSON
DOB:        29/11/1963
NHS Number: 761 330 6609
Address:    7 Orchard Lane, Canterbury, CT2 8LU
Date:       08 November 2024
Clinician:  Dr I. West, GP

BACKGROUND
Early-onset dementia (probable Alzheimer's type) diagnosed 2022. Lives alone; social care package in place.

JOINT CARE PLAN — November 2024
A joint care plan has been prepared by Kent Adult Social Care and the GP. The plan is signed by:
- David Rees, Social Worker, Kent Adult Social Care.
- Fiona Booth (Tel: 07700 000518), informal carer and close friend of the patient.

The plan covers daily check-in visits by Fiona Booth, weekly professional carer visits, and monthly GP review.

COMMUNITY NURSE NOTE — 5 November 2024
Home visit conducted. Hannah appeared settled. Fiona Booth was present and reported no concerns. Memory aids in place (labelled drawers, calendar). Medication compliance satisfactory.

Carer emergency contact recorded: Fiona Booth — 07700 000518.

OUTSTANDING ACTIONS
- Memory clinic review in 3 months.
- Occupational therapy assessment for home safety.
- Carer's assessment offered to Fiona Booth.

Dr I. West, GP
""",
    },
    # ------------------------------------------------------------------ 19
    {
        "zip_name": "Test-Real-Khalid-v2.zip",
        "txt_name": "2024-12-04_rec19_child_asthma_KHALID_Zain_1000.txt",
        "manifest": {
            "patient_name": "Zain Khalid",
            "patient_dob": "22/01/2014",
            "not_in_redacted": ["Shelley James"],
            "must_stay": [
                "Zain Khalid", "22/01/2014", "Dr D. Nguyen",
                "asthma", "Croydon University Hospital",
            ],
            "escalation_expected": [],
        },
        "text": """\
CHILD HEALTH RECORD — ASTHMA REVIEW
New Road Surgery, 56 New Road, Croydon, CR0 1YT
Tel: 020 0000 0019

Patient:    Zain KHALID (child)
DOB:        22/01/2014
NHS Number: 881 400 7733
Address:    56 New Road, Croydon, CR0 1YT
Parent/Guardian: Mrs Fatima Khalid (mother)
Date:       04 December 2024
Clinician:  Dr D. Nguyen, GP (Child Health)

BACKGROUND
Asthma diagnosed 2018. Mild eczema. Under follow-up with Croydon University Hospital paediatric respiratory clinic.

CONSULTATION
Mrs Khalid reports Zain has had no hospital admissions in the past 12 months. He is managing well at school and engaging with an NHS-commissioned community asthma support group. The group's parent coordinator is Shelley James, who Mrs Khalid described as "very helpful." Zain's inhaler technique was observed and confirmed as correct.

CORRESPONDENCE — Croydon University Hospital
Outpatient review letter from Dr Y. Patel, Paediatric Respiratory Consultant:
"Zain continues to demonstrate excellent asthma control. Current regime is appropriate. Please continue community follow-up and advise Mrs Khalid to contact the hospital directly if any nocturnal symptoms develop."

MEDICATION
- Salbutamol 100 mcg inhaler PRN
- Clenil Modulite 100 mcg BD

OUTSTANDING ACTIONS
- GP review in 6 months.
- Eczema cream prescription renewed.

Dr D. Nguyen, GP
""",
    },
    # ------------------------------------------------------------------ 20
    {
        "zip_name": "Test-Real-King-v2.zip",
        "txt_name": "2024-10-15_rec20_research_KING_Robert_1000.txt",
        "manifest": {
            "patient_name": "Robert King",
            "patient_dob": "09/02/1985",
            "not_in_redacted": ["Sophie Allen", "s.allen@sleep-centre-personal.com"],
            "must_stay": [
                "Robert King", "09/02/1985", "Dr H. Grant",
                "Sleep Centre", "sleep apnoea",
            ],
            "escalation_expected": [],
        },
        "text": """\
RESEARCH PARTICIPANT RECORD — SLEEP APNOEA STUDY
Severn Avenue Practice, 89 Severn Avenue, Bristol, BS10 7DN
Tel: 0117 000020

Patient:    Mr Robert KING
DOB:        09/02/1985
NHS Number: 303 912 5702
Address:    89 Severn Avenue, Bristol, BS10 7DN
Date:       15 October 2024
Clinician:  Dr H. Grant, GP

BACKGROUND
Obstructive sleep apnoea diagnosed 2021. CPAP therapy in use. Patient enrolled as a participant in the Bristol Sleep Centre NHS Research Study (BSCR-2024-OSA) in January 2024.

RESEARCH FILE NOTE
Study coordinator Dr Sophie Allen (s.allen@sleep-centre-personal.com) emailed the patient on 14 October 2024 regarding completion of the 9-month follow-up survey. The email includes Dr Allen's personal academic email address rather than the institutional address, along with a direct dial number.

The patient's consent form (with handwritten signature) is stored in the research file. Participant ID code assigned: BSCR-2024-0087. This code is non-identifiable on its own and does not require redaction.

CORRESPONDENCE — Bristol Sleep Centre
Follow-up letter from Sleep Centre: "Mr King's CPAP adherence is excellent at 94% nights used. AHI has reduced from 28 to 6 events/hour. No changes to management required. Next annual review January 2025."

OUTSTANDING ACTIONS
- Complete and return 9-month follow-up survey.
- Annual CPAP review January 2025.

Dr H. Grant, GP
""",
    },
]


def main():
    os.makedirs(DOWNLOADS, exist_ok=True)
    for rec in RECORDS:
        zip_path = os.path.join(DOWNLOADS, rec["zip_name"])
        txt_name = rec["txt_name"]
        manifest_name = txt_name.replace(".txt", "") + "_manifest.json"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(txt_name, rec["text"])
            zf.writestr(manifest_name, json.dumps(rec["manifest"], indent=2))

        print(f"Created: {zip_path}")

    print(f"\nAll {len(RECORDS)} ZIPs created in {DOWNLOADS}")


if __name__ == "__main__":
    main()
