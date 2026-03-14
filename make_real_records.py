"""
make_real_records.py
====================
Creates 10 realistic NHS patient record ZIPs for the SAR redaction test harness.
Each ZIP contains one .txt record and a _manifest.json.
"""

import json
import os
import zipfile

DOWNLOADS = r"C:\Users\Amar Ahmed\Downloads"

RECORDS = [
    {
        "zip_name": "Test-Real-Matthews-v1.zip",
        "txt_name": "2023-07-02_rec1_GP_consultation_MATTHEWS_John_1000.txt",
        "manifest": {
            "patient_name": "John Matthews",
            "patient_dob": "14/02/1984",
            "not_in_redacted": ["Mr David Holmes", "David Holmes", "threatening messages"],
            "must_stay": ["John Matthews", "14/02/1984", "Dr S. Patel", "Frimley Park Hospital", "Atorvastatin"],
            "escalation_expected": [],
        },
        "text": r"""GP CONSULTATION AND CORRESPONDENCE RECORD
Farnham Health Centre, 1 Church Lane, Farnham, GU9 3AB
Tel: 01252 000001

Patient:    Mr John MATTHEWS
DOB:        14/02/1984
NHS Number: 654 991 2857
Address:    9 Meadow View, Farnham, GU9 4JL
Date:       02 July 2023
Clinician:  Dr S. Patel, GP

PRESENTING COMPLAINT
Intermittent chest discomfort and shortness of breath for two weeks. Patient states he is worried after a close friend was recently diagnosed with angina.

CONSULTATION NOTES
BP 135/82. Pulse 82 regular. Chest examination clear. ECG normal sinus rhythm.
Smoking: 10 cigarettes per day. Patient reports significant stress relating to an ongoing dispute with his brother-in-law, Mr David Holmes (residing at a separate address), who has allegedly been sending threatening text messages. Patient was advised to contact the police regarding this matter.
Referred for cardiac risk assessment.

MEDICATION SUMMARY
- Atorvastatin 10 mg once daily
- Salbutamol 100 mcg inhaler PRN
- Nicotine replacement patch (trial)

CORRESPONDENCE — 10 August 2023
From: Frimley Park Hospital, Cardiology Department
"Dear Dr Patel, Thank you for referring Mr Matthews. Stress ECG was negative. We recommend smoking cessation support and ongoing lipid management. No further cardiac investigation required at this time."

HEALTH VISITOR NOTE — 22 September 2023
Patient appears under considerable stress due to the ongoing family dispute referenced above. He mentioned that his brother-in-law Mr David Holmes has continued to send threatening messages. Patient was advised to report this to Surrey Police and to retain copies of all communications for evidence.

OUTSTANDING ACTIONS
- Review lipid profile in 6 months.
- Smoking cessation referral to be arranged.

Dr S. Patel, GP
""",
    },
    {
        "zip_name": "Test-Real-Rahman-v1.zip",
        "txt_name": "2024-04-15_rec2_diabetes_review_RAHMAN_Fatima_1000.txt",
        "manifest": {
            "patient_name": "Fatima Rahman",
            "patient_dob": "05/10/1991",
            "not_in_redacted": ["Tariq Hussain", "MDP-2024-778821", "support@medra-co.com"],
            "must_stay": ["Fatima Rahman", "05/10/1991", "Dr A. King", "Dr Elena Morris", "HbA1c", "MedraCo"],
            "escalation_expected": [],
        },
        "text": r"""DIABETES MANAGEMENT REVIEW
Telford Medical Group, 45 Wellington Road, Telford, TF1 6JG
Tel: 01952 000002

Patient:    Ms Fatima RAHMAN
DOB:        05/10/1991
NHS Number: 945 113 7720
Address:    23 King Street, Telford, TF1 6JG
Date:       15 April 2024
Clinician:  Dr A. King, GP

BACKGROUND
Type 1 diabetes mellitus diagnosed 2007. Under follow-up with diabetes clinic and ophthalmology.

CONSULTATION
HbA1c: 61 mmol/mol (measured April 2024).
Patient reports insulin pump malfunction during recent holiday in Turkey. Device serial number: MDP-2024-778821. Contacted MedraCo support (support@medra-co.com) who are arranging replacement.

Patient disclosed ongoing emotional stress following the breakdown of her engagement to her fianc\u00e9 Tariq Hussain. She found the relationship difficult; counselling was recommended and a referral placed.

CORRESPONDENCE
Letter from Dr Elena Morris, Endocrinologist, Royal Shrewsbury Hospital:
"Ms Rahman is progressing well on continuous subcutaneous insulin infusion. I noted emotional distress relating to a recent personal relationship ending; I have recommended supportive counselling. Continue current pump settings."

OUTSTANDING ACTIONS
- MedraCo pump replacement to be confirmed.
- Counselling referral placed.
- Annual retinal screening due October 2024.

Dr A. King, GP
""",
    },
    {
        "zip_name": "Test-Real-ONeill-v1.zip",
        "txt_name": "2024-03-15_rec3_mental_health_review_ONEILL_Stephen_1000.txt",
        "manifest": {
            "patient_name": "Stephen O'Neill",
            "patient_dob": "18/09/1965",
            "not_in_redacted": ["Mike B.", "Margaret O'Neill", "07700 900789"],
            "must_stay": ["Stephen O'Neill", "18/09/1965", "Dr T. Hughes", "AA"],
            "escalation_expected": [],
        },
        "text": r"""MENTAL HEALTH AND ADDICTION REVIEW
Edgeley Medical Centre, 12 Shaw Heath, Stockport, SK4 2NW
Tel: 0161 000003

Patient:    Mr Stephen O'NEILL
DOB:        18/09/1965
NHS Number: 871 330 4921
Address:    Flat 4, Greenfields Court, Stockport, SK4 2NW
Date:       15 March 2024
Clinician:  Dr T. Hughes, GP

BACKGROUND
Long-standing depression and alcohol use disorder. Currently stable.

CONSULTATION
Mr O'Neill reports significant improvement following regular attendance at AA meetings. He credits his AA sponsor Mike B. with keeping him motivated and attending. Discussed referral to community addiction team for ongoing structured support.

COMMUNITY PSYCHIATRIC NURSE NOTE — 15 March 2024
Patient expressed that he had experienced suicidal thoughts in the past but states he is now stable and has not had ideation for eight months. Patient's address was verified with his sister Margaret O'Neill (Tel: 07700 900789) who confirmed he is living alone and engaging well with support.

HISTORIC INFORMATION
Note on file: Patient was arrested for a public order offence in 1989. Offence is unspent due to age of record but is of historical nature only and has no current clinical relevance.

OUTSTANDING ACTIONS
- Community addiction team referral submitted.
- Next GP review in 6 weeks.

Dr T. Hughes, GP
""",
    },
    {
        "zip_name": "Test-Real-Green-v1.zip",
        "txt_name": "2024-05-10_rec4_child_asthma_GREEN_Lucy_1000.txt",
        "manifest": {
            "patient_name": "Lucy Green",
            "patient_dob": "22/12/2016",
            "not_in_redacted": ["Mrs R. Harris", "Claire Hughes", "01926 000055", "court order terms"],
            "must_stay": ["Lucy Green", "22/12/2016", "Chloe Green", "Dr S. Lo", "Salbutamol"],
            "escalation_expected": [],
        },
        "text": r"""CHILD HEALTH RECORD — ASTHMA MANAGEMENT
Child Health Clinic, Rugby Community Health Centre, CV22 6QT
Tel: 01788 000004

Patient:    Lucy GREEN (child)
DOB:        22/12/2016
NHS Number: 734 118 2390
Address:    41 Overdale Road, Rugby, CV22 6QT
Parent/Guardian: Mrs Chloe Green (mother)
Date:       10 May 2024
Clinician:  Dr S. Lo, GP (Child Health)

SUMMARY
Asthma diagnosed 2019. Well-controlled on current regime.

SCHOOL NURSE NOTE
Received note from Lucy's class teacher Mrs R. Harris reporting that Lucy experienced a wheeze episode during a sports class on 08 May 2024. Salbutamol inhaler was administered by the school nurse with good effect.

SAFEGUARDING NOTE
Social worker Claire Hughes (Warwickshire Children's Services, Tel: 01926 000055) is involved due to ongoing concerns regarding the father's access arrangements under an existing family court order. The specific terms of the court order are recorded in a separate legal document held by the practice IG lead. Claire Hughes is the allocated key worker.

MEDICATION
- Salbutamol 100 mcg inhaler PRN
- Seretide Evohaler 50/25 mcg BD

OUTSTANDING ACTIONS
- Review in 3 months.
- Liaison with Claire Hughes re. safeguarding plan.

Dr S. Lo, GP
""",
    },
    {
        "zip_name": "Test-Real-Han-v1.zip",
        "txt_name": "2024-02-20_rec5_migraine_review_HAN_William_1000.txt",
        "manifest": {
            "patient_name": "William Han",
            "patient_dob": "02/05/1977",
            "not_in_redacted": ["Fred Kwan"],
            "must_stay": ["William Han", "02/05/1977", "Dr Lea Chand", "University of Oxford", "Propranolol", "Dr F. Ng"],
            "escalation_expected": [],
        },
        "text": r"""GP CONSULTATION — MIGRAINE MANAGEMENT
Headington Practice, 20 Old Road, Oxford, OX3 8BP
Tel: 01865 000005

Patient:    Mr William HAN
DOB:        02/05/1977
NHS Number: 205 774 1192
Address:    1 Hazel Walk, Oxford, OX3 8BP
Date:       20 February 2024
Clinician:  Dr Lea Chand, GP

BACKGROUND
Migraines managed long-term on Propranolol 20 mg BD. Recently relocated from Hong Kong following appointment at the University of Oxford.

CORRESPONDENCE — OCCUPATIONAL HEALTH
Email received from Dr F. Ng, University Medical Service, University of Oxford: "Mr Han has been assessed and is fit for his current post. No workplace adjustments are required at this time."

CONSULTATION
Patient reports occasional use of CBD oil obtained from a friend named Fred Kwan ("brought it back from California as a gift"). He was advised that while CBD oil is legal, its interaction with Propranolol is uncertain and he should discontinue use until further review.

OUTSTANDING ACTIONS
- Advise patient on CBD-Propranolol interaction.
- Review migraine frequency at next appointment.

Dr Lea Chand, GP
""",
    },
    {
        "zip_name": "Test-Real-Donnelly-v1.zip",
        "txt_name": "2024-03-05_rec6_fertility_referral_DONNELLY_Sarah_1000.txt",
        "manifest": {
            "patient_name": "Sarah Donnelly",
            "patient_dob": "29/07/1982",
            "not_in_redacted": ["Tom Eccleston"],
            "must_stay": ["Sarah Donnelly", "29/07/1982", "Dr G. Kerr", "PCOS", "Liverpool Women's Hospital"],
            "escalation_expected": [],
        },
        "text": r"""FERTILITY ASSESSMENT REFERRAL
Lancaster Surgery, 15 Castle Hill, Lancaster, LA1 1TD
Tel: 01524 000006

Patient:    Ms Sarah DONNELLY
DOB:        29/07/1982
NHS Number: 512 333 0804
Address:    77 Castle Hill, Lancaster, LA1 1TD
Date:       05 March 2024
Clinician:  Dr G. Kerr, GP

BACKGROUND
Polycystic ovary syndrome (PCOS) diagnosed 2018. Referred for fertility assessment.

CONSULTATION
Patient attended with her partner Tom Eccleston. Semen analysis for Mr Eccleston: result normal (reported by patient; formal report attached). Discussed IVF referral to Liverpool Women's Hospital.

Previous obstetric history: termination of pregnancy 2003 (recorded in historical notes; details held separately).

CORRESPONDENCE
Letter from Liverpool Women's Hospital (Fertility Unit): "Ms Donnelly has been assessed. PCOS confirmed with polycystic ovarian morphology on USS. AMH 2.1 pmol/L. IVF recommended. Partner results satisfactory."

OUTSTANDING ACTIONS
- IVF referral confirmed.
- Folic acid 5 mg OD commenced.

Dr G. Kerr, GP
""",
    },
    {
        "zip_name": "Test-Real-Page-v1.zip",
        "txt_name": "2024-06-03_rec7_COPD_review_PAGE_Richard_1000.txt",
        "manifest": {
            "patient_name": "Richard Page",
            "patient_dob": "10/09/1958",
            "not_in_redacted": [],
            "must_stay": ["Richard Page", "10/09/1958", "Dr E. Lawson", "Lynne Ward", "St James's"],
            "escalation_expected": [],
        },
        "text": r"""COPD MANAGEMENT AND HOME VISIT RECORD
Dr E. Lawson, Highcroft Surgery, Leeds, LS9 7FR
Tel: 0113 000007

Patient:    Mr Richard PAGE
DOB:        10/09/1958
NHS Number: 640 917 6533
Address:    Flat 12, Highcroft Court, Leeds, LS9 7FR
Date:       03 June 2024
Clinician:  District Nurse Lynne Ward / Dr E. Lawson, GP

BACKGROUND
COPD, ex-smoker (40 pack years). On home oxygen 2 L/min via concentrator.

HOME VISIT — 3 June 2024 (District Nurse Lynne Ward)
Patient found in moderate respiratory distress. His neighbour in the flat below — a retired gentleman who has known Richard for many years and who wishes to remain anonymous in any records — had called 999 after hearing him collapse. Ambulance attended; patient transferred to St James's University Hospital, Respiratory Ward.

AMBULANCE CALL LOG
Caller: anonymous (neighbour). Address: Highcroft Court. Caller asked not to be named.

HOSPITAL DISCHARGE SUMMARY — St James's University Hospital
Patient admitted 3 June 2024. Exacerbation of COPD secondary to viral infection. Treated with nebulised Salbutamol, Ipratropium, IV hydrocortisone and a 5-day course of Doxycycline. O2 sats improved to 94% on 2 L/min. Discharged home 8 June 2024.

OUTSTANDING ACTIONS
- GP review 2 weeks post-discharge.
- Pulmonary rehabilitation referral.

Lynne Ward, District Nurse / Dr E. Lawson, GP
""",
    },
    {
        "zip_name": "Test-Real-Begum-v1.zip",
        "txt_name": "2024-04-22_rec8_DA_safeguarding_BEGUM_Aisha_1000.txt",
        "manifest": {
            "patient_name": "Aisha Begum",
            "patient_dob": "19/11/1994",
            "not_in_redacted": ["Karim Begum", "03/07/1991", "88 Barkerend Road", "PC/2024/BR/004421", "victim.support@bradford.gov.uk", "P. Hall", "01274 000099"],
            "must_stay": ["Aisha Begum", "19/11/1994", "Dr H. Wood", "Women's Refuge", "Bradford Royal Infirmary"],
            "escalation_expected": ["Karim Begum"],
        },
        "text": r"""GYNAECOLOGY REFERRAL AND SAFEGUARDING RECORD
Dr H. Wood, Parkview Surgery, Bradford, BD2 7DY
Tel: 01274 000008

Patient:    Ms Aisha BEGUM
DOB:        19/11/1994
NHS Number: 880 662 1447
Address:    12 Crown Place, Bradford, BD2 7DY
Date:       22 April 2024
Clinician:  Dr H. Wood, GP

BACKGROUND
Referred for gynaecology assessment for suspected endometriosis.

SAFEGUARDING — DOMESTIC ABUSE DISCLOSURE
Patient disclosed a history of domestic abuse perpetrated by her ex-partner Karim Begum (DOB: 03/07/1991, last known address: 88 Barkerend Road, Bradford BD3 9LS). The relationship ended six months ago following police involvement.

Police reference number: PC/2024/BR/004421. Victim support email thread: victim.support@bradford.gov.uk. These documents are filed separately.

Risk assessment completed by Dr Wood using DA risk tool. Patient assessed as MEDIUM risk. Safety planning completed; patient has emergency contacts in place.

Women's Refuge Liaison Officer P. Hall (Tel: 01274 000099) has been contacted. A safe housing referral has been made.

CORRESPONDENCE
Letter from Bradford Royal Infirmary, Gynaecology: "Ms Begum has been assessed. Laparoscopic findings consistent with stage II endometriosis. Hormonal treatment commenced."

OUTSTANDING ACTIONS
- DA safeguarding plan to be reviewed in 4 weeks.
- Gynaecology follow-up: 3 months.

Dr H. Wood, GP
""",
    },
    {
        "zip_name": "Test-Real-Addison-v1.zip",
        "txt_name": "2024-05-20_rec9_ADHD_review_ADDISON_Michael_1000.txt",
        "manifest": {
            "patient_name": "Michael Addison",
            "patient_dob": "11/04/2004",
            "not_in_redacted": ["Kyle P.", "Jane Walters"],
            "must_stay": ["Michael Addison", "11/04/2004", "Dr R. Lamb", "methylphenidate", "ADHD"],
            "escalation_expected": [],
        },
        "text": r"""ADHD MANAGEMENT REVIEW
Dr R. Lamb, Carlisle Health Centre, CA3 9HR
Tel: 01228 000009

Patient:    Mr Michael ADDISON
DOB:        11/04/2004
NHS Number: 300 553 8821
Address:    5 Elm Close, Carlisle, CA3 9HR
Date:       20 May 2024
Clinician:  Dr R. Lamb, GP

BACKGROUND
ADHD diagnosed 2013. On methylphenidate 36 mg modified-release daily and accessing CBT support.

SCHOOL CORRESPONDENCE
Letter received from Jane Walters (SENCO, Carlisle Academy) regarding special examination arrangements for Michael. Ms Walters requests confirmation of diagnosis for submission to the exam board. Response sent confirming diagnosis.

CONFIDENTIAL NOTE — FROM MOTHER
Patient's mother attended separately and expressed concern that Michael has been associating with a peer named Kyle P. who she believes is encouraging him to try recreational substances including cannabis. She has asked that this be noted confidentially and that Michael is not made aware that she raised this.

OUTSTANDING ACTIONS
- GP to discuss substance avoidance sensitively at next appointment.
- SENCO letter response filed.

Dr R. Lamb, GP
""",
    },
    {
        "zip_name": "Test-Real-Armstrong-v1.zip",
        "txt_name": "2024-05-03_rec10_oncology_review_ARMSTRONG_Helen_1000.txt",
        "manifest": {
            "patient_name": "Helen Armstrong",
            "patient_dob": "25/01/1973",
            "not_in_redacted": ["Emily", "Anita Lobo", "anita.lobo@company.co.uk"],
            "must_stay": ["Helen Armstrong", "25/01/1973", "Dr P. Bryant", "Northwick Park", "BrightProtect", "Dr N. Foster"],
            "escalation_expected": [],
        },
        "text": r"""ONCOLOGY FOLLOW-UP AND CORRESPONDENCE RECORD
Dr P. Bryant, Harrow Health Centre, HA2 8HG
Tel: 020 0000 0010

Patient:    Ms Helen ARMSTRONG
DOB:        25/01/1973
NHS Number: 119 847 9003
Address:    22 Lakeside Drive, Harrow, HA2 8HG
Date:       03 May 2024
Clinician:  Dr P. Bryant, GP

BACKGROUND
Breast cancer diagnosed 2018. Currently in clinical remission following surgery and adjuvant chemotherapy.

FOLLOW-UP CONSULTATION — 3 May 2024
Review at Northwick Park Hospital, Oncology. Patient remains in remission. No new symptoms. Next review 12 months.

Patient raised the subject of an insurance medical report requested by BrightProtect Ltd. (policy reference BP-2024-HA-00391). Explained the SAR process and patient's right to see any report sent on her behalf.

OCCUPATIONAL HEALTH CORRESPONDENCE
Email from Dr N. Foster, Occupational Health Consultant:
"Ms Armstrong is fit to return to full duties. No adjustments required."
Copy sent to HR manager Anita Lobo (anita.lobo@company.co.uk).

MACMILLAN COUNSELLOR SESSION SUMMARY
Patient discussed concerns about her daughter Emily (aged 16) being aware of her prognosis. Patient does not yet wish Emily to be fully informed. The counsellor noted that Emily has been presenting as anxious at school, as reported by the school. No further third-party disclosure was made.

OUTSTANDING ACTIONS
- Annual mammogram arranged.
- Insurance report request acknowledged.

Dr P. Bryant, GP
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
            zf.writestr(txt_name, rec["text"].lstrip("\n"))
            zf.writestr(manifest_name, json.dumps(rec["manifest"], indent=2))

        print(f"Created: {zip_path}")

    print(f"\nAll {len(RECORDS)} ZIPs created in {DOWNLOADS}")


if __name__ == "__main__":
    main()
