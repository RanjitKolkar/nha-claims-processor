"""
Canonical document type taxonomy for the claims processing system.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

# ── Canonical type names ──────────────────────────────────────────────────────
ADMISSION_FORM          = "admission_form"
PREAUTH_FORM            = "preauthorization_form"
CONSENT_FORM            = "consent_form"
CASE_SHEET              = "case_sheet"
CLINICAL_NOTES          = "clinical_notes"
NURSING_NOTES           = "nursing_notes"
MEDICATION_CHART        = "medication_chart"
DISCHARGE_SUMMARY       = "discharge_summary"
OPERATIVE_NOTES         = "operative_notes"
ANESTHESIA_NOTES        = "anesthesia_notes"
LAB_INVESTIGATION       = "lab_investigation"
RADIOLOGY_REPORT        = "radiology_report"
XRAY_IMAGE              = "xray_image"
USG_REPORT              = "usg_report"
CT_MRI_REPORT           = "ct_mri_report"
ANGIOGRAPHY_REPORT      = "angiography_report"
PROCEDURE_REPORT        = "procedure_report"
ENDOSCOPY_REPORT        = "endoscopy_report"
IVP_REPORT              = "ivp_report"
BILL_INVOICE            = "bill_invoice"
FEEDBACK_FORM           = "feedback_form"
IDENTITY_DOCUMENT       = "identity_document"
BARCODE_STICKER         = "barcode_sticker"
IMPLANT_STICKER         = "implant_sticker"
GEOTAG_PHOTO            = "geotag_photo"
REFERRAL_LETTER         = "referral_letter"
PRESCRIPTION            = "prescription"
VITAL_CHART             = "vital_chart"
BEDSIDE_CHART           = "bedside_chart"
ENHANCEMENT_RECORD      = "enhancement_record"
BIRTH_PROOF             = "birth_proof"
OTHER                   = "other"

ALL_TYPES: Set[str] = {
    ADMISSION_FORM, PREAUTH_FORM, CONSENT_FORM, CASE_SHEET, CLINICAL_NOTES,
    NURSING_NOTES, MEDICATION_CHART, DISCHARGE_SUMMARY, OPERATIVE_NOTES,
    ANESTHESIA_NOTES, LAB_INVESTIGATION, RADIOLOGY_REPORT, XRAY_IMAGE,
    USG_REPORT, CT_MRI_REPORT, ANGIOGRAPHY_REPORT, PROCEDURE_REPORT,
    ENDOSCOPY_REPORT, IVP_REPORT, BILL_INVOICE, FEEDBACK_FORM,
    IDENTITY_DOCUMENT, BARCODE_STICKER, IMPLANT_STICKER, GEOTAG_PHOTO,
    REFERRAL_LETTER, PRESCRIPTION, VITAL_CHART, BEDSIDE_CHART,
    ENHANCEMENT_RECORD, BIRTH_PROOF, OTHER,
}

# ── Filename label → canonical type  (upper-cased partial match) ──────────────
FILENAME_LABEL_MAP: Dict[str, str] = {
    # Admission
    "ADMISSION": ADMISSION_FORM,
    "ADM": ADMISSION_FORM,
    "ADMIT": ADMISSION_FORM,
    "ADM1": ADMISSION_FORM,
    "ADDMIT": ADMISSION_FORM,

    # Pre-auth
    "PRE_AUTH": PREAUTH_FORM,
    "PREAUTH": PREAUTH_FORM,
    "AUTHORIZATION": PREAUTH_FORM,
    "AUTHORISATION": PREAUTH_FORM,
    "01_PRE_AUTHORIZATION_FORM": PREAUTH_FORM,
    "PRE_AUTHORIZATION": PREAUTH_FORM,
    "PAC_REPORT": ANESTHESIA_NOTES,

    # Consent
    "CONSENT": CONSENT_FORM,

    # Case sheet / clinical
    "CASE_SHEET": CASE_SHEET,
    "CASE_RECORD": CASE_SHEET,
    "CASESHEET": CASE_SHEET,
    "CASE": CASE_SHEET,
    "ALLCASE_SHEET": CASE_SHEET,
    "CASERECORD": CASE_SHEET,
    "CLINICAL_NOTE": CLINICAL_NOTES,
    "CLINICAL_NOTES": CLINICAL_NOTES,
    "CLINICAL": CLINICAL_NOTES,
    "ICU_NOTES": CLINICAL_NOTES,
    "ICP_NOTES": CLINICAL_NOTES,
    "ICP_CHART": CLINICAL_NOTES,
    "ICP": CLINICAL_NOTES,
    "PROGRESS_RECORD": CLINICAL_NOTES,
    "DOC": CLINICAL_NOTES,
    "NOTES": CLINICAL_NOTES,
    "OPD": CLINICAL_NOTES,
    "PRESCRIPTION": PRESCRIPTION,
    "TREATMENT": CLINICAL_NOTES,
    "TREATMENT_CHART": CLINICAL_NOTES,
    "INITIAL_ASSESSMENT": ADMISSION_FORM,

    # Nursing / bedside
    "NURSES_RECORD": NURSING_NOTES,
    "NURSING": NURSING_NOTES,
    "BEDSIDE": BEDSIDE_CHART,
    "BED": BEDSIDE_CHART,
    "TPR": VITAL_CHART,
    "VITALS": VITAL_CHART,
    "INTAKE_OUTPUT": VITAL_CHART,
    "CHART": VITAL_CHART,

    # Medication
    "MEDICATION_CHART": MEDICATION_CHART,
    "MEDICINE_BILL": MEDICATION_CHART,
    "DIS_MEDICINE": MEDICATION_CHART,
    "PHARMACY": PRESCRIPTION,

    # Discharge
    "DISCHARGE_SUMMARY": DISCHARGE_SUMMARY,
    "DISCHARGE": DISCHARGE_SUMMARY,
    "DIS": DISCHARGE_SUMMARY,
    "DISC": DISCHARGE_SUMMARY,
    "DISCHARGESUMMERRY": DISCHARGE_SUMMARY,
    "DETAILED_DISCHARGE_SUMMARY": DISCHARGE_SUMMARY,
    "SDS": DISCHARGE_SUMMARY,
    "SUM": DISCHARGE_SUMMARY,
    "SUMMARY": DISCHARGE_SUMMARY,
    "MS_DIS": DISCHARGE_SUMMARY,
    "MSDCL": DISCHARGE_SUMMARY,
    "SAV_DIS": DISCHARGE_SUMMARY,
    "DC": DISCHARGE_SUMMARY,
    "DDD": DISCHARGE_SUMMARY,
    "DISCHARGE_CARD": DISCHARGE_SUMMARY,

    # OT / Operative
    "OT_NOTE": OPERATIVE_NOTES,
    "OT_NOTES": OPERATIVE_NOTES,
    "OT": OPERATIVE_NOTES,
    "OTNOTE": OPERATIVE_NOTES,
    "OTNOTES": OPERATIVE_NOTES,
    "OPERATIVE_NOTE": OPERATIVE_NOTES,
    "OPERATIVE_NOTES": OPERATIVE_NOTES,
    "DETAILED_OPERATIVE_NOTES": OPERATIVE_NOTES,
    "POST_OP_PHOTO": OPERATIVE_NOTES,

    # Anesthesia
    "ANAESTH_SLIP": ANESTHESIA_NOTES,
    "ANAESTHESIA": ANESTHESIA_NOTES,
    "ANESTHESIA": ANESTHESIA_NOTES,

    # Lab / investigations
    "LAB_REPORTS": LAB_INVESTIGATION,
    "LAB": LAB_INVESTIGATION,
    "CBC": LAB_INVESTIGATION,
    "HB_REPORT": LAB_INVESTIGATION,
    "HBR": LAB_INVESTIGATION,
    "LFT": LAB_INVESTIGATION,
    "RFT": LAB_INVESTIGATION,
    "RFTLFT": LAB_INVESTIGATION,
    "PTINR": LAB_INVESTIGATION,
    "URINE": LAB_INVESTIGATION,
    "INVESTIGATION": LAB_INVESTIGATION,
    "INVES": LAB_INVESTIGATION,
    "INVEST": LAB_INVESTIGATION,
    "ALL_INVESTIGATIONS": LAB_INVESTIGATION,
    "ALL_REPORTS": LAB_INVESTIGATION,
    "INV": LAB_INVESTIGATION,
    "INVESTIGATIONS": LAB_INVESTIGATION,
    "NEW_CBC": LAB_INVESTIGATION,

    # Radiology / X-ray
    "XRAY": XRAY_IMAGE,
    "X_RAY": XRAY_IMAGE,
    "X-RAY": XRAY_IMAGE,
    "XRAY_FILM": XRAY_IMAGE,
    "FILMS": XRAY_IMAGE,
    "X_RAY_PLATE": XRAY_IMAGE,
    "XRAY_CT_REPORT": CT_MRI_REPORT,
    "CT": CT_MRI_REPORT,
    "MRI": CT_MRI_REPORT,
    "CXRAY": XRAY_IMAGE,
    "CXR": XRAY_IMAGE,
    "CHEST_XRAY": XRAY_IMAGE,
    "CHEST_XRAY_REPORT": RADIOLOGY_REPORT,
    "POST_XRAY": XRAY_IMAGE,
    "POST_XRAY_FILM": XRAY_IMAGE,
    "POST_XRAY_FILM01": XRAY_IMAGE,
    "POST_XRAY_FILM_WITH_REPORT": RADIOLOGY_REPORT,
    "POST_OP_X_RAY": XRAY_IMAGE,
    "PRE_XRAY": XRAY_IMAGE,
    "XRAY_AND_REPORT": XRAY_IMAGE,
    "X_RAY_REPORT": RADIOLOGY_REPORT,
    "X_RAY_CHEST": XRAY_IMAGE,
    "X_RAY_CHEST_REPORT_0001": RADIOLOGY_REPORT,
    "POSTKUB": XRAY_IMAGE,
    "XRAYFILMREPORT": RADIOLOGY_REPORT,
    "RAMBHEJ_XRAY_FILM": XRAY_IMAGE,
    "SCAN_0002": XRAY_IMAGE,
    "XRY": XRAY_IMAGE,

    # USG
    "USG": USG_REPORT,
    "USG_REPORT": USG_REPORT,
    "USG_REPORT1": USG_REPORT,
    "USGREPORT": USG_REPORT,
    "ULTRA_SOUND": USG_REPORT,
    "USGFILM": USG_REPORT,
    "USG_IVP": IVP_REPORT,
    "USG_LFT": USG_REPORT,
    "IVP_USG": IVP_REPORT,
    "USG_IVP_BLOOD_R": IVP_REPORT,

    # IVP / KUB (Urology)
    "IVP": IVP_REPORT,
    "IVP_II": IVP_REPORT,
    "IVP_REPORT": IVP_REPORT,
    "IVP_REPORT_": IVP_REPORT,
    "IVP_X_RAY": IVP_REPORT,
    "IVP_X_RAY_WITH_REPORT": IVP_REPORT,
    "IVPFILM": IVP_REPORT,
    "KUB": IVP_REPORT,
    "GOVIND_IVP": IVP_REPORT,
    "MALA_DEVIV_IVP": IVP_REPORT,
    "RAVINDRA_YADAV_IVP": IVP_REPORT,
    "PAC_REPORT_OT_NOTES_AND_XRAY_REPORT": ANESTHESIA_NOTES,

    # Angiography / CAG
    "CAG": ANGIOGRAPHY_REPORT,
    "CAG_01": ANGIOGRAPHY_REPORT,
    "CAG_02": ANGIOGRAPHY_REPORT,
    "CAG_REPORT": ANGIOGRAPHY_REPORT,
    "CAG_REPORT_001": ANGIOGRAPHY_REPORT,
    "CAG_IMAGE": ANGIOGRAPHY_REPORT,
    "CAG_IMAGES": ANGIOGRAPHY_REPORT,
    "CAG_IMAGES_COMPRESSED": ANGIOGRAPHY_REPORT,
    "CAG_DAIGARM": ANGIOGRAPHY_REPORT,
    "PRE_ANGIOGRAM": ANGIOGRAPHY_REPORT,
    "PRE_ANGIOGRAM_2": ANGIOGRAPHY_REPORT,
    "PRE_ANGIOGRAPHY_2": ANGIOGRAPHY_REPORT,
    "POST_ANGIOGRAM": ANGIOGRAPHY_REPORT,
    "POST_CAG_DAIGARM": ANGIOGRAPHY_REPORT,
    "POST_ANGI_REPORT": ANGIOGRAPHY_REPORT,
    "POST_STENT": PROCEDURE_REPORT,
    "CAG_STILL_IMAGE": ANGIOGRAPHY_REPORT,
    "CAG_STILL_IMAGE_": ANGIOGRAPHY_REPORT,

    # PTCA / Procedure
    "PTCA": PROCEDURE_REPORT,
    "PTCA_REPORT": PROCEDURE_REPORT,
    "PTCA_REPORT_001": PROCEDURE_REPORT,
    "PTCA_REPORT_DIAG": PROCEDURE_REPORT,
    "PTCA_IMAGE": PROCEDURE_REPORT,
    "PTCA_IMAGES": PROCEDURE_REPORT,
    "PTCA_STENT": PROCEDURE_REPORT,
    "POST_PTCA_STILL_IMAGE": PROCEDURE_REPORT,

    # Endoscopy
    "ENDOSCOPY": ENDOSCOPY_REPORT,

    # Billing
    "BILL": BILL_INVOICE,
    "HOSPITAL_BILL": BILL_INVOICE,
    "BILL_SETTLEMENT": BILL_INVOICE,
    "INVOICE": BILL_INVOICE,
    "MEDICINE_BILL": BILL_INVOICE,

    # Feedback
    "FEEDBACK": FEEDBACK_FORM,
    "FEEDBACK_FORM": FEEDBACK_FORM,
    "FEED_BACK_FORM": FEEDBACK_FORM,
    "FEED": FEEDBACK_FORM,
    "FEDD": FEEDBACK_FORM,
    "FB": FEEDBACK_FORM,

    # Identity
    "ADHAR": IDENTITY_DOCUMENT,
    "AADHAR": IDENTITY_DOCUMENT,
    "CARD": IDENTITY_DOCUMENT,
    "PMAM": IDENTITY_DOCUMENT,
    "ID": IDENTITY_DOCUMENT,

    # Barcode / sticker
    "BARCODE": BARCODE_STICKER,
    "IMPLANT": IMPLANT_STICKER,
    "STICKER": IMPLANT_STICKER,

    # Geotag
    "GEOTAG": GEOTAG_PHOTO,
    "PHOTO": GEOTAG_PHOTO,
    "PIC": GEOTAG_PHOTO,

    # Enhancement record
    "ENHANCEMENT_RECORD": ENHANCEMENT_RECORD,
    "ENC": ENHANCEMENT_RECORD,

    # Birth proof – treated as identity document for NHA claim purposes
    "BIRTH_PROOF": IDENTITY_DOCUMENT,
    "BIRTH_PROOF_BBY_OF_JESMINA_DARLONG": IDENTITY_DOCUMENT,
    "BABYOFJESMINADARLONG": IDENTITY_DOCUMENT,
    "BABYOFJESMINADARLONGDOCUMENT_11ZON": IDENTITY_DOCUMENT,

    # Discharge Summary – additional real-world label variants
    "DP": DISCHARGE_SUMMARY,         # Discharge Papers
    "DB": DISCHARGE_SUMMARY,         # Discharge Brief
    "MS": DISCHARGE_SUMMARY,         # Medical Summary
    "SUDHAN_DB": DISCHARGE_SUMMARY,
    "DIS_DAR_": DISCHARGE_SUMMARY,
    "DISCHARGE__SUMMARY": DISCHARGE_SUMMARY,
    "DISCHARGE_SUMMRY": DISCHARGE_SUMMARY,
    "DISCHARGE_SUMMARY_GENERAL": DISCHARGE_SUMMARY,
    "DISCHARGE-1": DISCHARGE_SUMMARY,
    "AVTAR_SINGH_DISCHARGE_DECLARATION": DISCHARGE_SUMMARY,
    "PT_AVTAR_SINGH_DISCHARGE_SUMMARY": DISCHARGE_SUMMARY,
    "DEVI_DAS_DISCHARGE_SUMMARY": DISCHARGE_SUMMARY,
    "PRAVAKAR_NAIK_DIS": DISCHARGE_SUMMARY,
    "PRAVAKAR_NAIK_DIS_SUM": DISCHARGE_SUMMARY,
    "PUSHPA_DISCHARGE_2_1": DISCHARGE_SUMMARY,
    "PUSHPA_DISCHARGE_2_11": DISCHARGE_SUMMARY,
    "PUSHPA_DISCHARGE_2_2": DISCHARGE_SUMMARY,
    "PUSHPA_DISCHARGE_2_6": DISCHARGE_SUMMARY,

    # Clinical Notes – additional real-world label variants
    "CN": CLINICAL_NOTES,
    "CL": CLINICAL_NOTES,
    "CLINIC": CLINICAL_NOTES,
    "DEVI_DAS_CLINICAL_NOTES": CLINICAL_NOTES,
    "PT_AVTAR_FEVER_PROFILE_UPDATE": CLINICAL_NOTES,
    "CHOI_TSERING_DOCS_COMPRESSED": CLINICAL_NOTES,
    "23RD_JAN_DOC_NOTES_ICU": CLINICAL_NOTES,
    "DEVI_DAS_MHIS_DECLARATION": CLINICAL_NOTES,
    "PRAVAKAR_NAIK_CLINICAL_11ZON": CLINICAL_NOTES,

    # Feedback – additional variants
    "FD": FEEDBACK_FORM,
    "FF": FEEDBACK_FORM,
    "F_IPD": FEEDBACK_FORM,
    "FEED_BAC_": FEEDBACK_FORM,
    "FEED_BACK__": FEEDBACK_FORM,
    "DEVI_DAS_FEEDBACK": FEEDBACK_FORM,
    "CHOI_TSERING_FEEDBACK": FEEDBACK_FORM,
    "PRAVAKAR_NAIK_FEEDBACK": FEEDBACK_FORM,
    "PT_AVTAR_SINGH_NEGI_FEEDBACK": FEEDBACK_FORM,

    # Identity document – patient photo / name-as-filename patterns
    "N": IDENTITY_DOCUMENT,
    "N3": IDENTITY_DOCUMENT,
    "N4": IDENTITY_DOCUMENT,
    "AANITA": IDENTITY_DOCUMENT,
    "ANNITA": IDENTITY_DOCUMENT,
    "ANITA_D": IDENTITY_DOCUMENT,
    "ANITA_DHJH": IDENTITY_DOCUMENT,
    "ANITA_FDGH": IDENTITY_DOCUMENT,
    "NASEEMA": IDENTITY_DOCUMENT,
    "AMBIGADEVI": IDENTITY_DOCUMENT,
    "ADIT": IDENTITY_DOCUMENT,
    "PRAVAKAR_NAIK_ID": IDENTITY_DOCUMENT,

    # Case sheet – additional variants
    "CS": CASE_SHEET,
    "CR": CASE_SHEET,
    "CR2": CASE_SHEET,
    "CR3": CASE_SHEET,
    "BHT": CASE_SHEET,              # Bed Head Ticket
    "CASERECORD1": CASE_SHEET,
    "CASE_": CASE_SHEET,

    # Nursing notes – additional variants
    "NN1": NURSING_NOTES,
    "SNT": NURSING_NOTES,

    # Lab investigations – name-prefixed variants
    "DEVI_DAS_CBC": LAB_INVESTIGATION,
    "DEVI_DAS_INVESTIGATION": LAB_INVESTIGATION,
    "PRINT_REPORT": LAB_INVESTIGATION,
    "PARBATI_MAHANANDA_REPORTS": LAB_INVESTIGATION,
    "PT_AVTAR_SINGH_BLOOD_INVESTIGATION_REPORT": LAB_INVESTIGATION,
    "PT_AVTAR_URINE_RE": LAB_INVESTIGATION,
    "REPORT": LAB_INVESTIGATION,

    # USG – name-prefixed variants
    "MALTI_USG": USG_REPORT,
    "PRIYA_MISHRA_USG": USG_REPORT,
    "SASMITA_USG": USG_REPORT,
    "ULTRA_SOUND_": USG_REPORT,

    # IVP / KUB – KUV suffix = KUB/IVP film
    "MALATIKUV": IVP_REPORT,
    "GOVINDKUV": IVP_REPORT,
    "MALA_DEVIKUV": IVP_REPORT,
    "RAVINDRA_YADAVKUV": IVP_REPORT,

    # X-Ray – name-prefixed variants
    "PRAVAKAR_NAIK_XRAY": XRAY_IMAGE,
    "PRAVAKAR_NAIK_X-RAY": XRAY_IMAGE,
    "PHOOLPATTIDEVIPREXRAY": XRAY_IMAGE,

    # Operative notes – name-prefixed variants
    "OP_SLIP_": OPERATIVE_NOTES,
    "OTN": OPERATIVE_NOTES,
    "PRAVAKAR_NAIK_OT_11ZON": OPERATIVE_NOTES,

    # Bill / invoice – name-prefixed
    "DEVI_DAS_BILL": BILL_INVOICE,
    "PRAVAKAR_NAIK_BILL": BILL_INVOICE,
    "PRAVAKAR_NAIK_INVOICE": BILL_INVOICE,

    # Admission
    "ADD": ADMISSION_FORM,
    "AVTAR_SINGH_NEGI_ADMISSION_FORM": ADMISSION_FORM,

    # Medication chart
    "DEVI_DAS_MEDICATION_CHART": MEDICATION_CHART,
    "DIS-MEDICINE": MEDICATION_CHART,

    # Enhancement record – date-suffixed variants
    "DEVI_DAS_ENHANCE": ENHANCEMENT_RECORD,
    "ENHANCEMENT_RECORD_11_12": ENHANCEMENT_RECORD,
    "ENHANCEMENT_RECORD_13": ENHANCEMENT_RECORD,
    "ENHANCEMENT_RECORD_14": ENHANCEMENT_RECORD,
    "ENHANCEMENT_RECORD_15_16": ENHANCEMENT_RECORD,
    "ENHANCEMENT_RECORD_17": ENHANCEMENT_RECORD,
    "ENHANCEMENT_RECORD_18": ENHANCEMENT_RECORD,

    # Justification
    "JUSTIFICATION": OTHER,
    "JUSTICATION": OTHER,
    "HISSSS": OTHER,
    "ISSS": OTHER,
    "HISS": OTHER,
}

# ── Keyword lists for content-based classification ────────────────────────────
CONTENT_KEYWORDS: Dict[str, List[str]] = {
    DISCHARGE_SUMMARY: [
        "discharge summary", "date of discharge", "final diagnosis",
        "condition at discharge", "discharged on", "date of admission",
        "discharge date", "follow up", "length of stay",
    ],
    ADMISSION_FORM: [
        "admission", "date of admission", "admitted on", "patient admitted",
        "pre operative", "pre-operative", "initial assessment", "triage",
    ],
    OPERATIVE_NOTES: [
        "operation theatre", "operative note", "surgery performed",
        "intraoperative", "anaesthesia given", "surgeon", "scrub nurse",
        "procedure performed", "incision", "post operative",
    ],
    CLINICAL_NOTES: [
        "patient complains", "on examination", "clinical notes",
        "progress note", "doctor notes", "day notes", "icу", "ward rounds",
        "bp:", "pulse:", "spo2", "temperature:",
    ],
    LAB_INVESTIGATION: [
        "haemoglobin", "wbc", "platelets", "creatinine", "bilirubin",
        "sgpt", "sgot", "blood urea", "serum", "hba1c", "urine report",
        "culture sensitivity", "complete blood count",
    ],
    XRAY_IMAGE: [
        "x-ray", "xray", "radiograph", "chest pa", "ap view",
        "bones appear", "no pneumothorax", "fracture",
    ],
    ANGIOGRAPHY_REPORT: [
        "coronary angiography", "cag", "lad", "lcx", "rca",
        "stenosis", "occlusion", "ejection fraction", "ptca",
        "stent deployed", "angiogram", "cath no", "catheterization",
        "cardiovascular", "diag", "cardiologist",
    ],
    PROCEDURE_REPORT: [
        "ptca", "percutaneous", "coronary intervention", "stent",
        "balloon", "guidewire", "catheter lab", "phacoemulsification",
        "cataract extraction", "iol implanted", "intraocular lens",
    ],
    BARCODE_STICKER: [
        "ref:", "lot:", "serial no", "serial number", "model no", "catalog",
        "manufactured by", "udi", "implant", "device", "batch no",
    ],
    USG_REPORT: [
        "ultrasonography", "usg", "ultrasound", "liver size",
        "gall bladder", "kidneys", "echogenicity", "no free fluid",
    ],
    IVP_REPORT: [
        "intravenous pyelogram", "ivp", "kub", "collecting system",
        "pelvi-calyceal", "ureter", "bladder outline",
    ],
    BILL_INVOICE: [
        "total amount", "room charges", "ot charges", "package amount",
        "hospital bill", "invoice", "balance due", "amount paid",
    ],
    IDENTITY_DOCUMENT: [
        "aadhaar", "aadhar", "beneficiary id", "pmjay id",
        "date of birth", "uid:", "enrolment",
    ],
    FEEDBACK_FORM: [
        "feedback", "patient satisfaction", "rate your experience",
        "grievance", "how was your stay",
    ],
    MEDICATION_CHART: [
        "drug name", "dosage", "route", "frequency", "medication",
        "tablets", "injection", "iv drip", "administered",
    ],
}
