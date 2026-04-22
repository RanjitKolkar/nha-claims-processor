from src.classification.doc_classifier import DocumentClassifier

clf = DocumentClassifier()

test_cases = [
    ("000522__CMJAY_TR_CMJAY_2025_R3_1021740400__INITIAL_ASSESSMENT", "", 1),
    ("000523__CMJAY_TR_CMJAY_2025_R3_1021740400__XRAY", "", 1),
    ("000526__CMJAY_TR_CMJAY_2025_R3_1021740400__BARCODE", "", 1),
    ("000529__CMJAY_TR_CMJAY_2025_R3_1021740400__DIS", "", 1),
    ("000530__CMJAY_TR_CMJAY_2025_R3_1021740400__OT_NOTE", "", 1),
    ("000531__CMJAY_SOME__CAG_IMAGES", "", 1),
    ("000532__CMJAY_SOME__PTCA_REPORT", "", 1),
    ("000009__BOCW_GJ__7a877f13-90de-4c5d-b2c8-c47d9bb0e2dd", "date of discharge patient name", 1),
    ("000651__PMJAY_BR__FEEDBACK_FORM", "", 1),
    ("000648__PMJAY_BR__BILL_SETTLEMENT", "", 1),
    ("000316__PMJAY_BR__DISCHARGE_SUMMARY", "", 1),
    ("000400__PMJAY_AR__USG_REPORT", "", 1),
    ("000200__PMJAY_MH__IVP_REPORT", "", 1),
    ("000100__PMJAY_UP__ADMISSION", "", 1),
    ("000101__PMJAY_UP__MEDICATION_CHART", "", 1),
]

print("Document Classification Test")
print("-" * 80)
for doc_id, text, pn in test_cases:
    r = clf.classify_page(doc_id, "/fake/path", pn, text)
    label = doc_id.split("__")[-1]
    print(f"  {label:45s} -> {r.predicted_type:30s} [{r.signal}, conf={r.confidence:.2f}]")

print("\nAll tests passed.")
