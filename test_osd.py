"""Test Tesseract OSD on the real scanned images to see if rotation is detected."""
import fitz
from PIL import Image
import pytesseract
from pathlib import Path

claim_dir = Path(r"extract_1\Claims\SB039A\CMJAY_TR_CMJAY_2025_R3_1021740400")

for f in sorted(claim_dir.iterdir())[:5]:
    print(f"\n{f.name}")
    if f.suffix == ".pdf":
        doc = fitz.open(str(f))
        for i, page in enumerate(doc):
            mat = fitz.Matrix(200/72, 200/72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            print(f"  Page {i+1}: {img.size[0]}x{img.size[1]}")
            try:
                osd = pytesseract.image_to_osd(img, config="--psm 0 -c min_characters_to_try=5")
                for ln in osd.strip().split("\n"):
                    if any(k in ln for k in ["Rotate", "Orientation", "Script"]):
                        print(f"  OSD: {ln.strip()}")
            except Exception as e:
                print(f"  OSD error: {e}")
        doc.close()
    else:
        img = Image.open(f).convert("RGB")
        print(f"  {img.size[0]}x{img.size[1]}")
        try:
            osd = pytesseract.image_to_osd(img, config="--psm 0 -c min_characters_to_try=5")
            for ln in osd.strip().split("\n"):
                if any(k in ln for k in ["Rotate", "Orientation", "Script"]):
                    print(f"  OSD: {ln.strip()}")
        except Exception as e:
            print(f"  OSD error: {e}")
