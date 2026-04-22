"""Extract OCR text from each page, focusing on page 2+ where readable text appears."""
from pathlib import Path
from src.ingestion.document_loader import load_document

claim_dir = Path(r"extract_1\Claims\SB039A\CMJAY_TR_CMJAY_2025_R3_1021740400")

targets = ["DIS", "OT_NOTE"]
for f in sorted(claim_dir.iterdir()):
    label = f.stem.split("__")[-1] if "__" in f.stem else f.stem
    if any(t in label for t in targets):
        pages = load_document(f, "TEST", "SB039A")
        print(f"\n{'='*70}")
        print(f"FILE: {f.name}  ({len(pages)} pages)")
        for pg in pages:
            if pg.ocr_confidence > 0.55 or len(pg.text) > 100:
                print(f"\n  --- Page {pg.page_number} (conf={pg.ocr_confidence:.2f}) ---")
                print(pg.text[:1200])
