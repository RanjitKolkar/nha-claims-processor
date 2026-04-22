"""
Extract and show raw OCR text from claim documents for debugging.
"""
from pathlib import Path
from src.ingestion.document_loader import load_document

claim_dir = Path(r"extract_1\Claims\SB039A\CMJAY_TR_CMJAY_2025_R3_1021740400")

# Just look at the discharge summary and OT note
targets = ["DIS", "OT_NOTE", "INITIAL_ASSESSMENT"]
for f in sorted(claim_dir.iterdir()):
    label = f.stem.split("__")[-1] if "__" in f.stem else f.stem
    if any(t in label for t in targets):
        print(f"\n{'='*70}")
        print(f"FILE: {f.name}")
        print(f"{'='*70}")
        pages = load_document(f, "CMJAY_TR_CMJAY_2025_R3_1021740400", "SB039A")
        for pg in pages[:2]:
            print(f"  --- Page {pg.page_number} (ocr_conf={pg.ocr_confidence:.2f}, engine={pg.ocr_engine}) ---")
            print(pg.text[:1000] if pg.text else "[NO TEXT]")
            print()
