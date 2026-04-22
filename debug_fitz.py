"""Check what PyMuPDF extracts natively from the PDFs (before OCR)."""
import fitz
from pathlib import Path

claim_dir = Path(r"extract_2\Claims\MC011A\BOCW_GJ_R3_2026040310046613_ER")

for f in sorted(claim_dir.iterdir()):
    if f.suffix != ".pdf":
        continue
    label = f.stem.split("__")[-1]
    doc = fitz.open(str(f))
    print(f"\n{'='*70}")
    print(f"FILE: {f.name} ({doc.page_count} pages)")
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        # Also try "words" extraction
        words = page.get_text("words")
        readable_words = [w[4] for w in words if len(w[4]) >= 3 and w[4].isalpha()]
        print(f"\n  Page {i+1}: native_text={len(text)} chars, readable_words={len(readable_words)}")
        if len(text) > 30:
            print(f"  TEXT[:600]: {text[:600]}")
        if readable_words[:20]:
            print(f"  Words: {readable_words[:20]}")
    doc.close()
