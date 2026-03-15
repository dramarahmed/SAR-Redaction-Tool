"""
make_real_records_v3.py
=======================
Creates 30 realistic NHS patient record ZIPs (Records 21-50) for the SAR
redaction test harness. Manifests derived from the accompanying Redaction Guide.
"""

import json
import os
import zipfile

DOWNLOADS = r"C:\Users\Amar Ahmed\Downloads"

RECORDS = [
    # ------------------------------------------------------------------ 21
    {
        "zip_name": "Test-Real-Ahmed-v3.zip",
        "txt_name": "2024-03-10_rec21_anaemia_AHMED_Leila_1000.txt",
        "manifest": {
            "patient_name": "Leila Ahmed",
            "patient_dob": "10/04/1987",
            "not_in_redacted": ["Sami Ahmed"],
            "must_stay": ["Leila Ahmed", "10/04/1987", "Dr E. Morley",
                          "coeliac", "ferritin", "Dr Patrick O'Callaghan",
                          "Luton and Dunstable"],
            "escalation_expected": [],
        },
        "text": """\
GYNAECOLOGY AND GASTROENTEROLOGY CORRESPONDENCE RECORD
Birch Road Surgery, 12 Birch Road, Luton, LU2 9DY
Tel: 01582 000021

Patient:    Ms Leila AHMED
DOB:        10/04/1987
NHS Number: 805 991 3342
Address:    12 Birch Road, Luton, LU2 9DY
Date:       10 March 2024
Clinician:  Dr E. Morley, GP

BACKGROUND
Chronic iron-deficiency anaemia and coeliac disease (diagnosed 2015). Maintains
a strict gluten-free diet. Presented with ongoing fatigue and irregular menses.

CONSULTATION — 10 March 2024
Patient shared that her husband Sami Ahmed was recently made redundant, causing
significant household financial stress. She reports this has adversely affected
dietary adherence, as gluten-free products are more expensive. Physical
examination revealed pallor; abdomen soft, non-tender.

PLAN
Ferritin, full blood count and coeliac serology requested. Dietitian referral
placed for gluten-free dietary support. Folic acid 400 mcg OD prescribed.

CORRESPONDENCE — Luton and Dunstable University Hospital
Letter from Dr Patrick O'Callaghan, Consultant Gastroenterologist:
"Ms Ahmed's coeliac serology shows mildly elevated anti-tTG. I recommend
B12 testing to rule out associated deficiency. Please note that the patient's
mother reports similar gastrointestinal symptoms; this family history has been
noted but her mother is not a patient of this service and no further action
is required on our part."

OUTSTANDING ACTIONS
- Repeat coeliac serology and B12 in 6 weeks.
- Dietitian appointment confirmed.

Dr E. Morley, GP
""",
    },
    # ------------------------------------------------------------------ 22
    {
        "zip_name": "Test-Real-Collins-v3.zip",
        "txt_name": "2024-08-15_rec22_assault_COLLINS_Marcus_1000.txt",
        "manifest": {
            "patient_name": "Marcus Collins",
            "patient_dob": "03/02/1993",
            "not_in_redacted": ["Jess Hughes", "Paul Norris"],
            "must_stay": ["Marcus Collins", "03/02/1993", "Dr N. Singh",
                          "Royal Manchester Hospital", "tetanus"],
            "escalation_expected": [],
        },
        "text": """\
EMERGENCY DEPARTMENT AND OCCUPATIONAL HEALTH RECORD
Deansgate Medical Practice, 22 York Street, Manchester, M3 2PX
Tel: 0161 000022

Patient:    Mr Marcus COLLINS
DOB:        03/02/1993
NHS Number: 290 882 6670
Address:    22 York Street, Manchester, M3 2PX
Date:       15 August 2024
Clinician:  Dr N. Singh, GP

BACKGROUND
Attended Royal Manchester Hospital Emergency Department following a night-time
assault at his workplace. The employer's security manager contacted police who
attended the scene. Mr Collins was subsequently reviewed by his GP.

EMERGENCY DEPARTMENT SUMMARY — 14 August 2024
Minor lacerations to the right forearm; wound cleaned and dressed. Tetanus
immunisation administered (up to date). Patient was shaken but alert.

During the consultation Mr Collins mentioned that his colleague Jess Hughes
was present at the time of the incident and witnessed the event. He expressed
concern about returning to night-shift work.

OCCUPATIONAL HEALTH REFERRAL
Occupational Health nurse Paul Norris (City OH Services) requested a medical
certificate to support a return-to-work assessment. A fitness-for-work note
has been issued; full duties suspended pending review.

OUTSTANDING ACTIONS
- OH nurse to review in 2 weeks.
- GP to follow up if psychological symptoms worsen.

Dr N. Singh, GP
""",
    },
    # ------------------------------------------------------------------ 23
    {
        "zip_name": "Test-Real-Gomes-v3.zip",
        "txt_name": "2024-06-20_rec23_hypertension_GOMES_Rita_1000.txt",
        "manifest": {
            "patient_name": "Rita Gomes",
            "patient_dob": "27/06/1978",
            "not_in_redacted": ["Maria Rodriguez"],
            "must_stay": ["Rita Gomes", "27/06/1978", "Dr Y. Falk",
                          "Amlodipine", "perindopril"],
            "escalation_expected": [],
        },
        "text": """\
HYPERTENSION AND COMMUNITY CARE RECORD
Clifton Parade Surgery, 8 Lansdown Avenue, Bristol, BS8 7QR
Tel: 0117 000023

Patient:    Ms Rita GOMES
DOB:        27/06/1978
NHS Number: 788 319 5544
Address:    8 Lansdown Avenue, Bristol, BS8 7QR
Date:       20 June 2024
Clinician:  Dr Y. Falk, GP

BACKGROUND
Hypertension and moderate learning disability. Resides in supported
accommodation with community care package in place.

COMMUNITY NOTE — 18 June 2024
Ms Gomes's carer Maria Rodriguez attended the surgery on the patient's behalf
to report that prescribed medications had been missed on three consecutive days.
A medication administration record was reviewed; the missed doses were confirmed.

MEDICATION SUMMARY
- Amlodipine 5 mg once daily (antihypertensive)
- Perindopril 5 mg once daily (ACE inhibitor)
Dosette box compliance support arranged.

DISTRICT NURSE NOTE — 20 June 2024
District nurse home visit completed. BP recorded as 148/92. Noted a noise
complaint from a neighbour regarding the property; this is a housing matter
and does not affect clinical care. An interaction issue between the carer and
the neighbour was documented by the district nurse for contextual information
only.

OUTSTANDING ACTIONS
- Blood pressure medication compliance review in 4 weeks.
- Liaise with supported accommodation provider re medication prompting.

Dr Y. Falk, GP
""",
    },
    # ------------------------------------------------------------------ 24
    {
        "zip_name": "Test-Real-MacKenzie-v3.zip",
        "txt_name": "2024-05-08_rec24_diabetes_foot_MACKENZIE_Ewan_1000.txt",
        "manifest": {
            "patient_name": "Ewan MacKenzie",
            "patient_dob": "18/01/1969",
            "not_in_redacted": ["Anne MacKenzie"],
            "must_stay": ["Ewan MacKenzie", "18/01/1969", "Dr A. McStay",
                          "Dr Dennis Foyle", "metformin", "Lauren Keir"],
            "escalation_expected": [],
        },
        "text": """\
DIABETES FOOT CARE AND VASCULAR ASSESSMENT RECORD
Church View Surgery, 34 Church View, Inverness, IV2 4PL
Tel: 01463 000024

Patient:    Mr Ewan MACKENZIE
DOB:        18/01/1969
NHS Number: 100 733 9266
Address:    34 Church View, Inverness, IV2 4PL
Date:       08 May 2024
Clinician:  Dr A. McStay, GP

BACKGROUND
Type 2 diabetes mellitus managed with metformin 1g BD. Presented for review
of a plantar foot ulcer (Wagner grade 1) noted at the previous annual review.

PODIATRY REVIEW — 8 May 2024
District Podiatrist Lauren Keir reviewed the lesion. Superficial ulcer with
clean margins; no cellulitis or osteomyelitis suspected. Regular debridement
to continue; foam dressing applied.

CORRESPONDENCE
Report copied to Dr Dennis Foyle, Consultant Vascular Surgeon, NHS Highland,
for assessment of peripheral arterial disease. Vascular imaging has been
recommended.

ADMINISTRATIVE NOTE — 8 May 2024
Receptionist note: "Dr McStay: wife Anne MacKenzie called to reschedule
today's appointment; rebooked for 22 May 2024."

OUTSTANDING ACTIONS
- Vascular assessment referral confirmed.
- Podiatry review in 4 weeks.
- Repeat HbA1c at 3-month review.

Dr A. McStay, GP
""",
    },
    # ------------------------------------------------------------------ 25
    {
        "zip_name": "Test-Real-Price-v3.zip",
        "txt_name": "2024-07-14_rec25_osteoporosis_PRICE_Georgina_1000.txt",
        "manifest": {
            "patient_name": "Georgina Price",
            "patient_dob": "11/07/1955",
            "not_in_redacted": ["Michelle Price", "Robert Price"],
            "must_stay": ["Georgina Price", "11/07/1955", "Dr O. Woods",
                          "osteoporosis", "DXA"],
            "escalation_expected": [],
        },
        "text": """\
OSTEOPOROSIS MANAGEMENT AND COMPLAINT CORRESPONDENCE RECORD
Hereford Hills Practice, Hilltop House, Hereford, HR4 8XY
Tel: 01432 000025

Patient:    Mrs Georgina PRICE
DOB:        11/07/1955
NHS Number: 912 440 1882
Address:    Hilltop House, Hereford, HR4 8XY
Date:       14 July 2024
Clinician:  Dr O. Woods, GP

BACKGROUND
Established osteoporosis; on alendronic acid 70 mg weekly and calcium/vitamin D
supplementation. Annual DXA scan due.

FAMILY INVOLVEMENT
Mrs Price's daughter Michelle Price assists with medication dispensing and
accompanies her to appointments. Her son Robert Price submitted a formal written
complaint to the practice regarding a delay in scheduling the DXA scan.

COMPLAINT SUMMARY
Robert Price's letter (dated 30 June 2024) stated that his mother had been
waiting over 10 months for a bone density scan. The practice manager has
prepared a formal written response outlining the reasons for the delay and
the action taken to expedite the appointment.

OUTSTANDING ACTIONS
- DXA scan appointment confirmed: 2 August 2024.
- Practice manager response to Robert Price to be sent by 16 July 2024.
- Annual review with Dr O. Woods in September 2024.

Dr O. Woods, GP
""",
    },
    # ------------------------------------------------------------------ 26
    {
        "zip_name": "Test-Real-Hassan-v3.zip",
        "txt_name": "2024-09-02_rec26_PTSD_HASSAN_Amir_1000.txt",
        "manifest": {
            "patient_name": "Amir Hassan",
            "patient_dob": "30/10/1971",
            "not_in_redacted": ["MV/2024/B1/04471"],
            "must_stay": ["Amir Hassan", "30/10/1971", "Dr D. Fraser",
                          "PTSD", "Dr Carla Evans"],
            "escalation_expected": [],
        },
        "text": """\
PSYCHOLOGICAL AND POST-COLLISION CARE RECORD
Canal Place Surgery, 3 Canal Place, Birmingham, B1 1RQ
Tel: 0121 000026

Patient:    Mr Amir HASSAN
DOB:        30/10/1971
NHS Number: 440 100 9930
Address:    3 Canal Place, Birmingham, B1 1RQ
Date:       02 September 2024
Clinician:  Dr D. Fraser, GP

BACKGROUND
Road-traffic collision (RTC) two months ago in which another vehicle crossed
into Mr Hassan's lane. Currently receiving counselling.

POLICE AND LEGAL INFORMATION
Police incident reference logged: MV/2024/B1/04471. A Motor Insurers' Bureau
(MIB) claim has been initiated; the other driver has been identified in the
MIB record. This information is held separately by the solicitor and is
referenced here for continuity of care.

CORRESPONDENCE
Letter from Dr Carla Evans, Consultant Neuropsychologist:
"Mr Hassan presents with symptoms consistent with PTSD following the RTC.
I recommend a structured trauma-focused CBT programme and suggest a period
of sick leave of 6 weeks. No evidence of acquired neurological injury."

OUTSTANDING ACTIONS
- Trauma-focused CBT referral placed.
- Fitness certificate issued for 6 weeks.
- Medication review in 4 weeks (to consider low-dose sertraline if symptoms
  do not improve with psychological therapy alone).

Dr D. Fraser, GP
""",
    },
    # ------------------------------------------------------------------ 27
    {
        "zip_name": "Test-Real-Watts-v3.zip",
        "txt_name": "2024-10-10_rec27_endometriosis_WATTS_Hollie_1000.txt",
        "manifest": {
            "patient_name": "Hollie Watts",
            "patient_dob": "12/03/1999",
            "not_in_redacted": ["Becky Farnsworth"],
            "must_stay": ["Hollie Watts", "12/03/1999", "Dr M. Henderson",
                          "endometriosis", "Dr Charlotte Myers"],
            "escalation_expected": [],
        },
        "text": """\
GYNAECOLOGY FOLLOW-UP AND OCCUPATIONAL CORRESPONDENCE RECORD
Ocean Road Surgery, 45 Ocean Road, Sunderland, SR6 0HB
Tel: 0191 000027

Patient:    Ms Hollie WATTS
DOB:        12/03/1999
NHS Number: 338 944 0075
Address:    45 Ocean Road, Sunderland, SR6 0HB
Date:       10 October 2024
Clinician:  Dr M. Henderson, GP

BACKGROUND
Endometriosis diagnosed 2021; laparoscopy performed July 2023 with good
short-term results. Currently using Mirena intrauterine system (IUS).

CONSULTATION — 10 October 2024
Recurrence of lower abdominal pain over the past 3 weeks (7/10 severity).
Patient shares a property with flatmate Becky Farnsworth, who has been
providing informal practical support during episodes of severe pain.
Sick note requested for employer Metro Telecom Ltd.

CORRESPONDENCE
Letter from Dr Charlotte Myers, Gynaecological Surgeon, Sunderland Royal
Hospital:
"Ms Watts has been reviewed in clinic. The Mirena IUS remains correctly
positioned. Given symptom recurrence, I recommend a 6-month trial of
combined oral contraceptive pill in addition to the IUS, with reassessment
in early 2025. A repeat laparoscopy may be required if symptoms persist."

OUTSTANDING ACTIONS
- Fit note issued for 4 weeks; to be reviewed.
- Gynaecology follow-up confirmed January 2025.

Dr M. Henderson, GP
""",
    },
    # ------------------------------------------------------------------ 28
    {
        "zip_name": "Test-Real-AlHariri-v3.zip",
        "txt_name": "2024-04-18_rec28_antenatal_ALHARIRI_Noor_1000.txt",
        "manifest": {
            "patient_name": "Noor Al-Hariri",
            "patient_dob": "22/03/1986",
            "not_in_redacted": ["Layla K."],
            "must_stay": ["Noor Al-Hariri", "22/03/1986", "Dr R. Jamieson",
                          "Glasgow Language Coop"],
            "escalation_expected": [],
        },
        "text": """\
ANTENATAL CARE RECORD
Pollokshields Health Centre, 27 Albert Drive, Glasgow, G41 5PJ
Tel: 0141 000028

Patient:    Ms Noor AL-HARIRI
DOB:        22/03/1986
NHS Number: 615 293 7004
Address:    27 Albert Drive, Glasgow, G41 5PJ
Date:       18 April 2024
Clinician:  Dr R. Jamieson, GP / Midwife Team

BACKGROUND
G2 P1. Currently 26 weeks gestation. Arabic speaker with limited English.
Interpreter service arranged via Glasgow Language Coop for all appointments.
Today's appointment interpreter: Layla K. (reference: GLC-2024-0088).

MIDWIFE NOTE — 18 April 2024
Blood pressure 130/80 mmHg. Urinalysis: no proteinuria. Fundal height
consistent with gestational age. FHR 142 bpm. Patient tolerating pregnancy
well; no current concerns.

ADMINISTRATIVE NOTE
A call was received from a male caller stating he was the patient's partner.
He asked to confirm the timing of the next ultrasound scan. In line with
Caldicott principles, no information was shared; the patient was advised
directly and asked to pass on the appointment details herself.

OUTSTANDING ACTIONS
- 28-week growth scan arranged.
- Repeat blood pressure monitoring at 30 weeks.
- Glucose tolerance test booked for 28 weeks.

Dr R. Jamieson, GP
""",
    },
    # ------------------------------------------------------------------ 29
    {
        "zip_name": "Test-Real-Jenkins-v3.zip",
        "txt_name": "2024-11-05_rec29_back_pain_JENKINS_Harvey_1000.txt",
        "manifest": {
            "patient_name": "Harvey Jenkins",
            "patient_dob": "06/08/1972",
            "not_in_redacted": ["Lisa Torn", "Mick Rowe"],
            "must_stay": ["Harvey Jenkins", "06/08/1972", "Dr S. Francis",
                          "Keane & Co Solicitors"],
            "escalation_expected": [],
        },
        "text": """\
CHRONIC PAIN AND LEGAL CORRESPONDENCE RECORD
Brook Rise Surgery, 9 Brook Rise, Newport, NP10 9YN
Tel: 01633 000029

Patient:    Mr Harvey JENKINS
DOB:        06/08/1972
NHS Number: 781 022 9115
Address:    9 Brook Rise, Newport, NP10 9YN
Date:       05 November 2024
Clinician:  Dr S. Francis, GP

BACKGROUND
Long-term lower-back pain following a workplace lifting injury (2019).
Currently on a pain self-management programme (PCA). Legal proceedings ongoing
via Keane & Co Solicitors.

PHYSIOTHERAPY REPORT — Attached
Physio assessment by Lisa Torn (private physiotherapist, commissioned by
employer's insurer). Report notes: "Significant deconditioning. Patient would
benefit from a structured exercise programme. Prognosis for full recovery
guarded."

LEGAL NOTE
Correspondence from Keane & Co Solicitors includes a signed witness statement
(affidavit) from Mr Harvey Jenkins's former line manager Mick Rowe, who
witnessed the original injury. The statement has been copied to this file
for completeness.

OUTSTANDING ACTIONS
- Pain clinic referral reviewed; appointment confirmed.
- Medical records to be provided to Keane & Co Solicitors as per patient
  consent.

Dr S. Francis, GP
""",
    },
    # ------------------------------------------------------------------ 30
    {
        "zip_name": "Test-Real-Moretti-v3.zip",
        "txt_name": "2024-09-23_rec30_migraine_MORETTI_Isabella_1000.txt",
        "manifest": {
            "patient_name": "Isabella Moretti",
            "patient_dob": "15/11/1990",
            "not_in_redacted": ["Paolo Moretti", "James Hazeldine"],
            "must_stay": ["Isabella Moretti", "15/11/1990", "Dr U. Patil",
                          "Dr Helen Reed", "topiramate"],
            "escalation_expected": [],
        },
        "text": """\
NEUROLOGY AND OCCUPATIONAL CORRESPONDENCE RECORD
Kingsgate Practice, Flat 5, Kingsgate Apartments, London, NW1 4RD
Tel: 020 0000 0030

Patient:    Ms Isabella MORETTI
DOB:        15/11/1990
NHS Number: 704 815 6320
Address:    Flat 5, Kingsgate Apartments, London, NW1 4RD
Date:       23 September 2024
Clinician:  Dr U. Patil, GP

BACKGROUND
Migraines with aura since 2018. Current episode frequency: 4 per month.
Patient reports a significant increase in stress linked to ongoing divorce
proceedings against her spouse Paolo Moretti.

CORRESPONDENCE — Neurology
Letter from Dr Helen Reed, Consultant Neurologist, University College
Hospital:
"MRI brain: normal. No structural cause identified. I recommend a topiramate
trial 25 mg OD increasing to 50 mg at 4 weeks as migraine prophylaxis.
Emotional stressors should be addressed in parallel; psychological support
is recommended."

LEGAL CORRESPONDENCE
Letter received from solicitor James Hazeldine (Hazeldine & Partners LLP)
requesting an occupational health report regarding Ms Moretti's fitness to
work during the divorce proceedings. Patient has provided written consent
for this report to be prepared.

OUTSTANDING ACTIONS
- Topiramate prescription issued.
- Occupational health report to be prepared for Hazeldine & Partners LLP.
- Psychological support referral placed.

Dr U. Patil, GP
""",
    },
    # ------------------------------------------------------------------ 31
    {
        "zip_name": "Test-Real-Ncube-v3.zip",
        "txt_name": "2024-07-30_rec31_HIV_NCUBE_Joseph_1000.txt",
        "manifest": {
            "patient_name": "Joseph Ncube",
            "patient_dob": "02/07/1983",
            "not_in_redacted": ["Adaeze Obi"],
            "must_stay": ["Joseph Ncube", "02/07/1983", "Dr C. Rigby",
                          "Hallamshire Hospital", "ART"],
            "escalation_expected": [],
        },
        "text": """\
HIV MANAGEMENT AND SEXUAL HEALTH RECORD
Park Lane Surgery, 16 Park Lane, Sheffield, S1 8PR
Tel: 0114 000031

Patient:    Mr Joseph NCUBE
DOB:        02/07/1983
NHS Number: 723 221 9051
Address:    16 Park Lane, Sheffield, S1 8PR
Date:       30 July 2024
Clinician:  Dr C. Rigby, GP

BACKGROUND
HIV positive (diagnosed 2016). Stable on antiretroviral therapy (ART);
undetectable viral load at last review. Attends Hallamshire Hospital
Sexual Health Clinic for 6-monthly monitoring.

PUBLIC HEALTH LOG — PARTNER NOTIFICATION
A previous partner, Adaeze Obi, was informed of Mr Ncube's HIV status by
consent following structured partner notification support through the sexual
health clinic. Ms Obi's name and contact details are recorded in the
public-health partner notification log held separately by the clinic.
No further disclosure was made beyond the consented notification.

OUTSTANDING ACTIONS
- Routine 6-month review at Hallamshire Sexual Health Clinic.
- Annual lipid profile and renal function.
- Continue current ART regime.

Dr C. Rigby, GP
""",
    },
    # ------------------------------------------------------------------ 32
    {
        "zip_name": "Test-Real-Hargreaves-v3.zip",
        "txt_name": "2024-08-25_rec32_COPD_HARGREAVES_Emma_1000.txt",
        "manifest": {
            "patient_name": "Emma Hargreaves",
            "patient_dob": "13/09/1960",
            "not_in_redacted": ["Patricia Lane", "Simon Hargreaves"],
            "must_stay": ["Emma Hargreaves", "13/09/1960", "Dr W. Nyoni",
                          "COPD", "Adult Social Care"],
            "escalation_expected": [],
        },
        "text": """\
COPD MANAGEMENT AND SAFEGUARDING RECORD
Downlands Surgery, 4 Downlands Crescent, Southampton, SO16 3LH
Tel: 023 0000 0032

Patient:    Ms Emma HARGREAVES
DOB:        13/09/1960
NHS Number: 822 559 4490
Address:    4 Downlands Crescent, Southampton, SO16 3LH
Date:       25 August 2024
Clinician:  Dr W. Nyoni, GP

BACKGROUND
Chronic obstructive pulmonary disease (COPD) — Global Initiative stage III.
Uses home oxygen 2 L/min via concentrator. Lives alone. Neighbour Patricia
Lane holds a spare key to the property for emergency access.

COMMUNITY NURSE NOTE — 23 August 2024
Community nurse arrived for a scheduled home visit and found the front door
unlocked and patient in mild respiratory distress. Patricia Lane was contacted
as keyholder. The community nurse then phoned the patient's son Simon
Hargreaves (Tel: 07709 000232) who attended within 20 minutes.

SAFEGUARDING NOTE
A fire hazard was identified: an electric heater was being used in proximity
to the oxygen concentrator. A safeguarding referral has been made to Adult
Social Care to arrange a fire safety assessment and review the home
environment.

OUTSTANDING ACTIONS
- Fire safety assessment via Adult Social Care.
- GP review in 2 weeks.
- Discuss home support package review with social worker.

Dr W. Nyoni, GP
""",
    },
    # ------------------------------------------------------------------ 33
    {
        "zip_name": "Test-Real-Grant-v3.zip",
        "txt_name": "2024-06-15_rec33_epilepsy_GRANT_Callum_1000.txt",
        "manifest": {
            "patient_name": "Callum Grant",
            "patient_dob": "08/05/2002",
            "not_in_redacted": ["Jacqueline Grant"],
            "must_stay": ["Callum Grant", "08/05/2002", "Dr A. Burns",
                          "epilepsy", "DVLA", "Crosshouse Hospital"],
            "escalation_expected": [],
        },
        "text": """\
EPILEPSY MANAGEMENT AND DVLA NOTIFICATION RECORD
Ash Mews Surgery, 2 Ash Mews, Ayr, KA7 3JU
Tel: 01292 000033

Patient:    Mr Callum GRANT
DOB:        08/05/2002
NHS Number: 662 103 3987
Address:    2 Ash Mews, Ayr, KA7 3JU
Date:       15 June 2024
Clinician:  Dr A. Burns, GP

BACKGROUND
Lifelong epilepsy (juvenile myoclonic epilepsy); seizure-free for 14 months
on sodium valproate. Recently passed his driving test.

DVLA NOTIFICATION
As Callum's condition and medication require formal notification to the DVLA,
a notification letter is to be prepared and filed with the practice.
His mother Jacqueline Grant attended the appointment with him and queried
the DVLA notification process, seeking clarification on the conditions under
which Callum may drive.

CORRESPONDENCE
Neurology letter from Crosshouse Hospital (Dr B. Aitken):
"Callum remains seizure-free on current medication. He is aware of the legal
requirement to notify the DVLA of his diagnosis. I support him continuing to
drive if the DVLA is notified and the group 1 licence criteria are met."

OUTSTANDING ACTIONS
- DVLA notification letter to be submitted.
- Routine neurology review in 12 months.

Dr A. Burns, GP
""",
    },
    # ------------------------------------------------------------------ 34
    {
        "zip_name": "Test-Real-Parker-v3.zip",
        "txt_name": "2024-07-19_rec34_macular_PARKER_Violet_1000.txt",
        "manifest": {
            "patient_name": "Violet Parker",
            "patient_dob": "21/01/1949",
            "not_in_redacted": ["Helena Watts"],
            "must_stay": ["Violet Parker", "21/01/1949", "Dr T. Clarke",
                          "macular degeneration", "Frank Miller", "RNIB"],
            "escalation_expected": [],
        },
        "text": """\
OPHTHALMOLOGY AND SOCIAL SUPPORT RECORD
Oak Cottage Surgery, Wells, BA5 2JW
Tel: 01749 000034

Patient:    Mrs Violet PARKER
DOB:        21/01/1949
NHS Number: 509 774 8211
Address:    Oak Cottage, Wells, BA5 2JW
Date:       19 July 2024
Clinician:  Dr T. Clarke, GP

BACKGROUND
Age-related macular degeneration (AMD); registered partially sighted.
Lives alone. A close friend Helena Watts assists with shopping and daily tasks.

CORRESPONDENCE
Letter from Frank Miller, Consultant Optometrist, Wells Eye Centre:
"Mrs Parker's AMD has progressed bilaterally. Current best corrected visual
acuity: right 6/36, left 6/60. I have referred her to the RNIB liaison
officer for assessment for low-vision aids and community support. Anti-VEGF
treatment is not currently indicated given the non-wet classification."

OUTSTANDING ACTIONS
- RNIB liaison officer contact to be followed up.
- Annual ophthalmology review.
- Social services review of home support package in view of deteriorating
  visual function.

Dr T. Clarke, GP
""",
    },
    # ------------------------------------------------------------------ 35
    {
        "zip_name": "Test-Real-Kerr-v3.zip",
        "txt_name": "2024-09-10_rec35_bipolar_KERR_Jonathan_1000.txt",
        "manifest": {
            "patient_name": "Jonathan Kerr",
            "patient_dob": "28/10/1976",
            "not_in_redacted": ["Tina Clark"],
            "must_stay": ["Jonathan Kerr", "28/10/1976", "Dr I. Mathews",
                          "bipolar", "Dr Anita Rao"],
            "escalation_expected": [],
        },
        "text": """\
MENTAL HEALTH AND OCCUPATIONAL CORRESPONDENCE RECORD
Valley View Surgery, 11 Valley View, York, YO24 3BN
Tel: 01904 000035

Patient:    Mr Jonathan KERR
DOB:        28/10/1976
NHS Number: 456 995 2307
Address:    11 Valley View, York, YO24 3BN
Date:       10 September 2024
Clinician:  Dr I. Mathews, GP

BACKGROUND
Bipolar disorder type I; under community psychiatry follow-up. Stable for
3 years on lithium 800 mg OD.

PSYCHIATRIC NOTE
Community Psychiatrist Dr Anita Rao notes an informal discussion with the
employer's HR business partner Ms Tina Clark regarding a phased return to
work following a period of extended sick leave. This discussion took place
with Mr Kerr's verbal consent, which was documented at the time.

OUTSTANDING ACTIONS
- Phased return-to-work plan to be formalised in writing.
- Lithium level check in 3 months.
- Mental health review in 6 weeks.

Dr I. Mathews, GP
""",
    },
    # ------------------------------------------------------------------ 36
    {
        "zip_name": "Test-Real-Rowe-v3.zip",
        "txt_name": "2024-05-22_rec36_eczema_ROWE_Amelia_1000.txt",
        "manifest": {
            "patient_name": "Amelia Rowe",
            "patient_dob": "17/04/1995",
            "not_in_redacted": ["Carla Mendez"],
            "must_stay": ["Amelia Rowe", "17/04/1995", "Dr K. Ashford",
                          "eczema", "emollient"],
            "escalation_expected": [],
        },
        "text": """\
DERMATOLOGY AND ALLERGY REFERRAL RECORD
Riverside Surgery, Flat 3, Riverside Court, Derby, DE1 2PG
Tel: 01332 000036

Patient:    Ms Amelia ROWE
DOB:        17/04/1995
NHS Number: 411 229 8806
Address:    Flat 3, Riverside Court, Derby, DE1 2PG
Date:       22 May 2024
Clinician:  Dr K. Ashford, GP

BACKGROUND
Persistent eczema affecting face and neck. Patient reports a significant
flare over the past 6 weeks following introduction of a new skincare product.

CONSULTATION — 22 May 2024
Ms Rowe states the product was purchased via social media from a friend
named Carla Mendez, who sells handmade cosmetics online. The product
contained undisclosed ingredients and is not licensed in the UK. Patient
was advised to discontinue use immediately.

Examination: erythematous, excoriated plaques on bilateral cheeks and neck.
No secondary infection.

MANAGEMENT
Prescribed emollient (Epaderm) to apply liberally TDS, and hydrocortisone
1% cream for acute flares. Referred to NHS allergy clinic for patch testing.
Patient advised to retain the product and its packaging for allergy
investigation.

OUTSTANDING ACTIONS
- Allergy clinic referral confirmed.
- Review in 4 weeks to assess treatment response.

Dr K. Ashford, GP
""",
    },
    # ------------------------------------------------------------------ 37
    {
        "zip_name": "Test-Real-Davies-v3.zip",
        "txt_name": "2024-08-06_rec37_knee_DAVIES_Owen_1000.txt",
        "manifest": {
            "patient_name": "Owen Davies",
            "patient_dob": "29/08/1982",
            "not_in_redacted": ["Sgt Ruth Collins"],
            "must_stay": ["Owen Davies", "29/08/1982", "Dr P. Nichols",
                          "South Wales Police", "knee"],
            "escalation_expected": [],
        },
        "text": """\
MUSCULOSKELETAL AND OCCUPATIONAL HEALTH RECORD
Bay Surgery, 45 Bay Avenue, Cardiff, CF10 5RQ
Tel: 029 0000 0037

Patient:    Mr Owen DAVIES
DOB:        29/08/1982
NHS Number: 310 557 6409
Address:    45 Bay Avenue, Cardiff, CF10 5RQ
Date:       06 August 2024
Clinician:  Dr P. Nichols, GP

BACKGROUND
Recovering from right knee arthroscopy (meniscus repair, June 2024).
Active physiotherapy programme in progress.

OCCUPATIONAL HEALTH
Owen is employed by South Wales Police. His employer requested a return-to-
work form. The form was submitted by Sgt Ruth Collins, who serves as the
occupational health liaison contact for Owen's unit.

PHYSIOTHERAPY NOTE
Physio log attached. Manager's contact details appear in the physio email
signature block. These are for administrative purposes only.

OUTSTANDING ACTIONS
- Return-to-work form completed and returned to South Wales Police.
- Physiotherapy to continue for 8 further weeks.
- GP review in 6 weeks.

Dr P. Nichols, GP
""",
    },
    # ------------------------------------------------------------------ 38
    {
        "zip_name": "Test-Real-Sandhu-v3.zip",
        "txt_name": "2024-10-28_rec38_eating_disorder_SANDHU_Ella_1000.txt",
        "manifest": {
            "patient_name": "Ella Sandhu",
            "patient_dob": "06/03/2000",
            "not_in_redacted": ["Claire Inder"],
            "must_stay": ["Ella Sandhu", "06/03/2000", "Dr J. Ahmed",
                          "bulimia"],
            "escalation_expected": [],
        },
        "text": """\
EATING DISORDER TREATMENT RECORD
Tallow Lane Practice, 29 Tallow Lane, Peterborough, PE1 4BG
Tel: 01733 000038

Patient:    Ms Ella SANDHU
DOB:        06/03/2000
NHS Number: 852 663 9922
Address:    29 Tallow Lane, Peterborough, PE1 4BG
Date:       28 October 2024
Clinician:  Dr J. Ahmed, GP

BACKGROUND
History of bulimia nervosa (diagnosed 2021). Currently under the
NHS Eating Disorder Service. Treatment plan includes CBT therapy.

THERAPIST NOTE — SESSION SUMMARY
Therapist Claire Inder (NHS Eating Disorder Service, Peterborough) emailed
a session summary to Dr J. Ahmed. The email was also copied to the patient's
mother, Dr Reena Sandhu, who is a GP at a different practice in Peterborough.
Dr Reena Sandhu's name appears in the email correspondence in her capacity
as a family member who has given consent to receive updates, not in her
professional clinical capacity. A boundaries discussion was recorded with
the patient's consent.

CLINICAL NOTE
Ella's current weight is stable; no purging behaviours reported in the past
6 weeks. Engaging well with therapy.

OUTSTANDING ACTIONS
- Continue eating disorder CBT programme.
- GP review in 4 weeks.

Dr J. Ahmed, GP
""",
    },
    # ------------------------------------------------------------------ 39
    {
        "zip_name": "Test-Real-Lewis-v3.zip",
        "txt_name": "2024-07-11_rec39_COPD_LEWIS_Gareth_1000.txt",
        "manifest": {
            "patient_name": "Gareth Lewis",
            "patient_dob": "14/02/1959",
            "not_in_redacted": ["Angela Lewis", "Brian Evans"],
            "must_stay": ["Gareth Lewis", "14/02/1959", "Dr E. Morris",
                          "COPD", "Dr Paula King"],
            "escalation_expected": [],
        },
        "text": """\
COPD EXACERBATION AND HOSPITAL DISCHARGE RECORD
Penarth Drive Surgery, 4 Penarth Drive, Swansea, SA2 9JA
Tel: 01792 000039

Patient:    Mr Gareth LEWIS
DOB:        14/02/1959
NHS Number: 266 440 7751
Address:    4 Penarth Drive, Swansea, SA2 9JA
Date:       11 July 2024
Clinician:  Dr E. Morris, GP

BACKGROUND
COPD (GOLD stage III). Moderate exacerbation requiring hospital admission.

EMERGENCY EVENT — 5 July 2024
Mr Lewis's spouse Angela Lewis called 999 following a rapid deterioration in
his breathing. Paramedics attended and transferred him to Morriston Hospital.
During the admission his neighbour Brian Evans looked after Mr Lewis's dog,
as noted for continuity planning purposes.

HOSPITAL DISCHARGE SUMMARY
Consultant Dr Paula King, Morriston Hospital:
"Mr Lewis was admitted with a COPD exacerbation secondary to a respiratory
tract infection. Managed with nebulised bronchodilators, systemic
corticosteroids, and a 5-day course of doxycycline. Discharged after
6 days with home oxygen and a written exacerbation action plan."

OUTSTANDING ACTIONS
- GP review 2 weeks post-discharge.
- Pulmonary rehabilitation referral placed.
- COPD self-management plan updated.

Dr E. Morris, GP
""",
    },
    # ------------------------------------------------------------------ 40
    {
        "zip_name": "Test-Real-Neal-v3.zip",
        "txt_name": "2024-09-04_rec40_rheumatoid_NEAL_Sophie_1000.txt",
        "manifest": {
            "patient_name": "Sophie Neal",
            "patient_dob": "21/11/1974",
            "not_in_redacted": ["Marcia Donovan"],
            "must_stay": ["Sophie Neal", "21/11/1974", "Dr T. Riley",
                          "methotrexate", "rheumatoid arthritis"],
            "escalation_expected": [],
        },
        "text": """\
RHEUMATOID ARTHRITIS MANAGEMENT RECORD
Long Trees Surgery, 8 Long Trees Close, Bexley, DA5 3BX
Tel: 020 0000 0040

Patient:    Ms Sophie NEAL
DOB:        21/11/1974
NHS Number: 834 772 2203
Address:    8 Long Trees Close, Bexley, DA5 3BX
Date:       04 September 2024
Clinician:  Dr T. Riley, GP

BACKGROUND
Established rheumatoid arthritis (diagnosed 2019). Currently on methotrexate
15 mg weekly with folic acid 5 mg the following day.

RHEUMATOLOGY CLINIC NOTE — 28 August 2024
Reviewed at Queen Mary's Hospital rheumatology clinic. The clinic letter
notes that Ms Neal attended with her friend Marcia Donovan, who provided
transport and personal support. Clinical review: disease activity low,
DAS28 score 2.1. Treatment to continue.

TEST RESULTS
LFTs slightly raised (ALT 52 IU/L; upper normal 45). Repeat blood test
requested in 4 weeks. If persistently elevated, methotrexate dose reduction
to be considered.

OUTSTANDING ACTIONS
- Repeat LFTs in 4 weeks.
- Rheumatology review in 3 months.

Dr T. Riley, GP
""",
    },
    # ------------------------------------------------------------------ 41
    {
        "zip_name": "Test-Real-Omar-v3.zip",
        "txt_name": "2024-06-24_rec41_hypertension_OMAR_Khaled_1000.txt",
        "manifest": {
            "patient_name": "Khaled Omar",
            "patient_dob": "12/12/1977",
            "not_in_redacted": ["Aziz Omar"],
            "must_stay": ["Khaled Omar", "12/12/1977", "Dr G. Paterson",
                          "Dr Melanie Reeves", "hypertension"],
            "escalation_expected": [],
        },
        "text": """\
HYPERTENSION AND CARDIOLOGY REFERRAL RECORD
Abbey Way Surgery, 16 Abbey Way, Leicester, LE4 1FB
Tel: 0116 000041

Patient:    Mr Khaled OMAR
DOB:        12/12/1977
NHS Number: 505 118 4467
Address:    16 Abbey Way, Leicester, LE4 1FB
Date:       24 June 2024
Clinician:  Dr G. Paterson, GP

BACKGROUND
Hypertension; on amlodipine 10 mg OD. Strong family history of cardiovascular
disease: father Aziz Omar died of a myocardial infarction at age 54. This
family history is clinically significant for risk stratification.

CARDIOLOGY CORRESPONDENCE
Letter from Dr Melanie Reeves, Consultant Cardiologist, Leicester Royal
Infirmary:
"Mr Omar's coronary artery calcium score is elevated (CAC 156). In view of
his family history and risk factors, I recommend a diagnostic coronary
angiogram. Please continue current antihypertensive therapy."

OCCUPATIONAL HEALTH
An occupational health report has been prepared to support renewal of Mr Omar's
taxi driver licence. The report confirms fitness to drive subject to annual
review.

OUTSTANDING ACTIONS
- Coronary angiogram referral placed.
- Taxi licence OH report submitted to DVLA.
- Blood pressure review in 6 weeks.

Dr G. Paterson, GP
""",
    },
    # ------------------------------------------------------------------ 42
    {
        "zip_name": "Test-Real-Newton-v3.zip",
        "txt_name": "2024-11-14_rec42_parkinsons_NEWTON_Frances_1000.txt",
        "manifest": {
            "patient_name": "Frances Newton",
            "patient_dob": "30/01/1940",
            "not_in_redacted": ["Susan King", "Janet Shaw"],
            "must_stay": ["Frances Newton", "30/01/1940", "Dr U. Chandra",
                          "Parkinson", "Sunny Meadows Care Home"],
            "escalation_expected": [],
        },
        "text": """\
PARKINSON'S DISEASE AND CARE HOME CORRESPONDENCE RECORD
Maple Crescent Practice, 11 Maple Crescent, Worcester, WR2 4JJ
Tel: 01905 000042

Patient:    Mrs Frances NEWTON
DOB:        30/01/1940
NHS Number: 901 229 7734
Address:    Sunny Meadows Care Home, Worcester, WR2 5LH
Date:       14 November 2024
Clinician:  Dr U. Chandra, GP

BACKGROUND
Parkinson's disease (stage 3); resident at Sunny Meadows Care Home since
2022. On co-careldopa 25/100 mg three times daily.

CARE HOME CORRESPONDENCE
An email from care home manager Susan King reports that Mrs Newton had an
unwitnessed fall in her room on 10 November 2024. No apparent injury was
sustained, but a GP assessment has been requested.

The notification was also copied to Mrs Newton's daughter Janet Shaw (next
of kin), who confirmed she has been informed and will visit at the weekend.

GP ASSESSMENT — 14 November 2024
Mrs Newton is alert and oriented. No focal neurological deficit. Minor
bruising to the left elbow. No evidence of fracture. Medication review:
current co-careldopa timing to be adjusted to reduce evening 'off' periods.

OUTSTANDING ACTIONS
- Falls referral to physiotherapy for balance assessment.
- Medication timing adjusted — carers to be briefed.
- Next GP review in 4 weeks.

Dr U. Chandra, GP
""",
    },
    # ------------------------------------------------------------------ 43
    {
        "zip_name": "Test-Real-Nishimura-v3.zip",
        "txt_name": "2024-04-05_rec43_travel_health_NISHIMURA_Tomoko_1000.txt",
        "manifest": {
            "patient_name": "Tomoko Nishimura",
            "patient_dob": "07/07/1969",
            "not_in_redacted": ["JN7432891"],
            "must_stay": ["Tomoko Nishimura", "07/07/1969", "Dr R. Wray",
                          "yellow fever", "University of Cambridge"],
            "escalation_expected": [],
        },
        "text": """\
TRAVEL HEALTH ASSESSMENT RECORD
Pear Street Practice, 89 Pear Street, Cambridge, CB2 1EE
Tel: 01223 000043

Patient:    Dr Tomoko NISHIMURA
DOB:        07/07/1969
NHS Number: 580 336 4408
Address:    89 Pear Street, Cambridge, CB2 1EE
Date:       05 April 2024
Clinician:  Dr R. Wray, GP

BACKGROUND
Academic researcher visiting from Japan. Attached to the Department of
Biochemistry, University of Cambridge for a 12-month fellowship.

VACCINATION RECORD — 5 April 2024
Yellow fever vaccine administered (Stamaril; batch ZP4421A). Yellow fever
vaccination certificate issued. Patient counselled on post-vaccination
observation period.

ADMINISTRATIVE NOTE
The standard vaccination record form completed by the patient includes her
passport number JN7432891. This was captured for identification purposes at
the time of travel-health registration.

CORRESPONDENCE
An email from the University of Cambridge HR department to Dr Wray's practice
confirms that Dr Nishimura is covered by an overseas institutional health
insurance arrangement for the duration of her fellowship and lists the
sponsoring institution and policy reference.

OUTSTANDING ACTIONS
- Vaccination record filed.
- Return travel health review if new destinations planned.

Dr R. Wray, GP
""",
    },
    # ------------------------------------------------------------------ 44
    {
        "zip_name": "Test-Real-Larkin-v3.zip",
        "txt_name": "2024-12-10_rec44_child_asthma_LARKIN_Jade_1000.txt",
        "manifest": {
            "patient_name": "Jade Larkin",
            "patient_dob": "03/09/2007",
            "not_in_redacted": ["Mr Luke Powell", "Darren Larkin"],
            "must_stay": ["Jade Larkin", "03/09/2007", "Dr S. Brown",
                          "asthma", "eczema"],
            "escalation_expected": [],
        },
        "text": """\
CHILD HEALTH AND SAFEGUARDING RECORD
Oakwood Surgery, 24 Oakwood Road, Huddersfield, HD3 3AL
Tel: 01484 000044

Patient:    Jade LARKIN (child)
DOB:        03/09/2007
NHS Number: 414 553 9326
Address:    24 Oakwood Road, Huddersfield, HD3 3AL
Parent/Guardian: Mrs Karen Larkin (mother)
Date:       10 December 2024
Clinician:  Dr S. Brown, GP

BACKGROUND
Asthma (well-controlled) and mild eczema. Annual school health review.

SCHOOL NURSE REPORT
A report was shared by class teacher Mr Luke Powell (Huddersfield Academy),
describing a wheeze episode during PE on 5 December 2024. Salbutamol
inhaler was administered by the school nurse with good effect. Mr Powell
has noted Jade's inhaler remains in the school medical room as agreed.

SAFEGUARDING NOTE
Mrs Karen Larkin has requested that all access to Jade's health information
be restricted to herself only, due to an ongoing family court case. The court
case involves former partner Darren Larkin, and a residency order is in place.
The specific terms of the order are held by the practice IG lead.

OUTSTANDING ACTIONS
- Safeguarding referral reviewed — no immediate concerns.
- Review asthma control in 3 months.

Dr S. Brown, GP
""",
    },
    # ------------------------------------------------------------------ 45
    {
        "zip_name": "Test-Real-Knight-v3.zip",
        "txt_name": "2024-10-22_rec45_renal_KNIGHT_Peter_1000.txt",
        "manifest": {
            "patient_name": "Peter Knight",
            "patient_dob": "15/12/1951",
            "not_in_redacted": ["Hannah Shaw"],
            "must_stay": ["Peter Knight", "15/12/1951", "Dr L. Murray",
                          "Dr Adriana Carver", "Bluebird Care", "haemodialysis"],
            "escalation_expected": [],
        },
        "text": """\
CHRONIC RENAL FAILURE AND DIALYSIS CARE RECORD
Cherwell Surgery, Cherwell House, Banbury, OX16 2BS
Tel: 01295 000045

Patient:    Mr Peter KNIGHT
DOB:        15/12/1951
NHS Number: 355 994 2083
Address:    Cherwell House, Banbury, OX16 2BS
Date:       22 October 2024
Clinician:  Dr L. Murray, GP

BACKGROUND
End-stage renal disease (ESRD) on haemodialysis three times per week at
Oxford University Hospitals Trust dialysis unit. Under nephrology care.

NEPHROLOGY CORRESPONDENCE
A copy of the clinic letter from Dr Adriana Carver, Consultant Nephrologist,
was sent to Dr L. Murray. The letter confirms continued stable dialysis
adequacy and recommends review for potential renal transplant listing.

DIALYSIS UNIT REPORT
The dialysis unit report was written by dialysis nurse Hannah Shaw, detailing
access site condition and fluid balance. Ms Shaw is an agency nurse contracted
to provide specialist dialysis care.

HOME SUPPORT
Transport to dialysis sessions is arranged by carer agency Bluebird Care Ltd.
A contact list of transport coordinators and emergency contacts has been
attached to this record.

OUTSTANDING ACTIONS
- Transplant assessment referral to be initiated.
- Next dialysis unit review in 4 weeks.

Dr L. Murray, GP
""",
    },
    # ------------------------------------------------------------------ 46
    {
        "zip_name": "Test-Real-Brooks-v3.zip",
        "txt_name": "2024-09-19_rec46_complaint_BROOKS_Natalie_1000.txt",
        "manifest": {
            "patient_name": "Natalie Brooks",
            "patient_dob": "25/06/1988",
            "not_in_redacted": ["Cathy Bates"],
            "must_stay": ["Natalie Brooks", "25/06/1988", "Dr V. Kennet",
                          "sumatriptan", "migraine"],
            "escalation_expected": [],
        },
        "text": """\
MIGRAINE MANAGEMENT AND PATIENT COMPLAINT RECORD
Highfield Surgery, 22 Highfield Close, Cheltenham, GL52 4PX
Tel: 01242 000046

Patient:    Ms Natalie BROOKS
DOB:        25/06/1988
NHS Number: 697 220 5541
Address:    22 Highfield Close, Cheltenham, GL52 4PX
Date:       19 September 2024
Clinician:  Dr V. Kennet, GP

CLINICAL BACKGROUND
Established migraines. Prescribed sumatriptan 50 mg PRN. Review indicates
good symptom control.

PATIENT COMPLAINT — PALS REFERENCE P/2024/CHL/00314
Ms Brooks submitted a formal complaint via email regarding an interaction
with a member of reception staff. She described the behaviour as dismissive
and unhelpful during an urgent appointment request.

An investigation was conducted by the practice manager. A staff statement
from the receptionist Cathy Bates was obtained as part of the internal review.
The practice manager's written response to Ms Brooks has been filed on record.

OUTSTANDING ACTIONS
- Complaint resolved; written apology issued.
- Clinical review of migraine management in 3 months.

Dr V. Kennet, GP
""",
    },
    # ------------------------------------------------------------------ 47
    {
        "zip_name": "Test-Real-Okafor-v3.zip",
        "txt_name": "2024-07-08_rec47_sickle_cell_OKAFOR_Darius_1000.txt",
        "manifest": {
            "patient_name": "Darius Okafor",
            "patient_dob": "05/05/1991",
            "not_in_redacted": [],
            "must_stay": ["Darius Okafor", "05/05/1991", "Dr E. Jones",
                          "sickle-cell", "Dr Nicholas Hart", "Dr Mona Khatib",
                          "Luton"],
            "escalation_expected": [],
        },
        "text": """\
SICKLE-CELL DISEASE MANAGEMENT AND CORRESPONDENCE RECORD
Ridge Lane Surgery, 19 Ridge Lane, Luton, LU1 4PE
Tel: 01582 000047

Patient:    Mr Darius OKAFOR
DOB:        05/05/1991
NHS Number: 588 119 7008
Address:    19 Ridge Lane, Luton, LU1 4PE
Date:       08 July 2024
Clinician:  Dr E. Jones, GP

BACKGROUND
Sickle-cell disease (HbSS genotype). Experiences frequent pain crises;
on hydroxyurea 1g OD and penicillin prophylaxis.

EMERGENCY DEPARTMENT SUMMARY
Attended Luton and Dunstable University Hospital ED on 4 July 2024 with
a vaso-occlusive pain crisis. Paramedic report attached. Managed with IV
analgesia (morphine), IV fluids and oxygen. Discharged after 48 hours.

HAEMATOLOGY CORRESPONDENCE
Letter from Dr Nicholas Hart, Consultant Haematologist:
"Mr Okafor has been reviewed post-admission. Hydroxyurea dose to be
increased to 1.5 g OD given frequency of crises. I have copied this letter
to Dr Mona Khatib, Consultant Rheumatologist, to rule out avascular
necrosis as a contributing factor."

OUTSTANDING ACTIONS
- Haematology review in 6 weeks.
- MRI hip requested.

Dr E. Jones, GP
""",
    },
    # ------------------------------------------------------------------ 48
    {
        "zip_name": "Test-Real-Myles-v3.zip",
        "txt_name": "2024-11-28_rec48_anxiety_MYLES_Bethany_1000.txt",
        "manifest": {
            "patient_name": "Bethany Myles",
            "patient_dob": "01/05/2004",
            "not_in_redacted": ["Mark Evans", "Sandra Myles"],
            "must_stay": ["Bethany Myles", "01/05/2004", "Dr A. Quinn",
                          "anxiety"],
            "escalation_expected": [],
        },
        "text": """\
ADOLESCENT MENTAL HEALTH RECORD
Elm Gardens Surgery, 39 Elm Gardens, Chichester, PO19 6AZ
Tel: 01243 000048

Patient:    Ms Bethany MYLES
DOB:        01/05/2004
NHS Number: 932 664 8805
Address:    39 Elm Gardens, Chichester, PO19 6AZ
Date:       28 November 2024
Clinician:  Dr A. Quinn, GP

BACKGROUND
Bethany is a sixth-form student presenting with anxiety and low mood ahead
of her A-level examinations.

CONSULTATION — 28 November 2024
Bethany disclosed significant academic pressure and social anxiety. Risk
assessment completed; no self-harm or suicidal ideation. A referral to the
school counsellor Mark Evans (Chichester Academy) was discussed and accepted.
Examination anxiety management techniques discussed.

PARENT COMMUNICATION
An email from Bethany's mother Sandra Myles (received 27 November 2024)
requested an update on her daughter's progress. In line with Gillick
competency guidance, a response was sent to Bethany only after discussion
with her and with her consent to share a general update.

SAFEGUARDING
No safeguarding concerns identified.

OUTSTANDING ACTIONS
- School counsellor referral confirmed.
- Review in 6 weeks.

Dr A. Quinn, GP
""",
    },
    # ------------------------------------------------------------------ 49
    {
        "zip_name": "Test-Real-Foster-v3.zip",
        "txt_name": "2024-06-30_rec49_prostate_cancer_FOSTER_Henry_1000.txt",
        "manifest": {
            "patient_name": "Henry Foster",
            "patient_dob": "04/06/1967",
            "not_in_redacted": ["Julie Parsons"],
            "must_stay": ["Henry Foster", "04/06/1967", "Dr J. Orton",
                          "prostate", "Royal Cornwall Hospital", "GiltEdge Life"],
            "escalation_expected": [],
        },
        "text": """\
ONCOLOGY FOLLOW-UP AND INSURANCE CORRESPONDENCE RECORD
Far End Surgery, 2 Far End Cottages, Truro, TR1 2AX
Tel: 01872 000049

Patient:    Mr Henry FOSTER
DOB:        04/06/1967
NHS Number: 440 773 1190
Address:    2 Far End Cottages, Truro, TR1 2AX
Date:       30 June 2024
Clinician:  Dr J. Orton, GP

BACKGROUND
Prostate cancer (Gleason 7); radical prostatectomy 2019. Currently in
remission. Follow-up under Royal Cornwall Hospital oncology.

CLINICAL UPDATE
Latest PSA result: <0.01 ng/mL (undetectable). Patient remains
asymptomatic. Royal Cornwall Hospital has confirmed annual review to
continue.

INSURANCE CORRESPONDENCE
GiltEdge Life insurance company submitted a request for a medical report
via their clerk Julie Parsons (reference: GEL/FH/2024/3389). The request
covers Mr Foster's current health status and prognosis.

NOTE
Mr Foster has also submitted a Subject Access Request (SAR) for a copy of
his own medical records held by this practice, in accordance with Article 15
of UK GDPR. This is being processed separately by the practice manager.

OUTSTANDING ACTIONS
- Medical report for GiltEdge Life to be completed.
- SAR response to be sent within the statutory 30-day period.

Dr J. Orton, GP
""",
    },
    # ------------------------------------------------------------------ 50
    {
        "zip_name": "Test-Real-Lawson-v3.zip",
        "txt_name": "2024-10-17_rec50_MS_LAWSON_Michelle_1000.txt",
        "manifest": {
            "patient_name": "Michelle Lawson",
            "patient_dob": "27/12/1970",
            "not_in_redacted": ["Linda Boyce", "Colin Firth"],
            "must_stay": ["Michelle Lawson", "27/12/1970", "Dr B. Andrews",
                          "multiple sclerosis", "Addenbrooke's",
                          "Suffolk County Council"],
            "escalation_expected": [],
        },
        "text": """\
MULTIPLE SCLEROSIS DIAGNOSIS AND MULTIDISCIPLINARY CARE RECORD
Hazelwood Surgery, 20 Hazelwood Way, Ipswich, IP3 0HT
Tel: 01473 000050

Patient:    Ms Michelle LAWSON
DOB:        27/12/1970
NHS Number: 912 509 4402
Address:    20 Hazelwood Way, Ipswich, IP3 0HT
Date:       17 October 2024
Clinician:  Dr B. Andrews, GP

BACKGROUND
Multiple sclerosis (relapsing-remitting) confirmed on MRI October 2024.
Neurology follow-up under Addenbrooke's Hospital, Cambridge.

OCCUPATIONAL HEALTH
Michelle is employed by Suffolk County Council. The occupational health
contact for her employer is Linda Boyce (Occupational Health Advisor,
Suffolk County Council). Ms Boyce has been in contact with the practice
to discuss reasonable adjustments.

SOCIAL CARE
A social worker Colin Firth (Suffolk Adult Social Care) is arranging an
assessment for a Disabled Facilities Grant to fund mobility adaptations
to the patient's home. The assessment is due in November 2024.

NEUROLOGY CORRESPONDENCE
Letter from Addenbrooke's Hospital Neurology Department:
"Ms Lawson has been assessed. Relapsing-remitting MS confirmed. I recommend
natalizumab infusions subject to JC virus antibody testing. Please refer
to the MS specialist nursing team for ongoing support."

OUTSTANDING ACTIONS
- JC virus antibody testing arranged.
- Home assessment by Colin Firth confirmed.
- Natalizumab infusion referral pending.

Dr B. Andrews, GP
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
