"""
OCR one JPEG from the MC011A UUID claim to see text quality.
"""
from PIL import Image
import pytesseract
from src.ingestion.preprocessor import enhance_image

img_path = r"extract_2\Claims\MC011A\BOCW_GJ_R3_2026040310046613_ER\000012__BOCW_GJ_R3_2026040310046613__4d079c0c-a8a0-417e-87aa-6f277f84fa5a.jpg"

img = Image.open(img_path).convert("RGB")
print(f"Size: {img.size}, mode: {img.mode}")

# Try raw OCR first
raw = pytesseract.image_to_string(img, lang="eng", config="--oem 3 --psm 6")
print(f"\n=== RAW TESSERACT ===")
print(raw[:1500])

# Try enhanced
enhanced = enhance_image(img)
enhanced_text = pytesseract.image_to_string(enhanced, lang="eng", config="--oem 3 --psm 6")
print(f"\n=== ENHANCED TESSERACT ===")
print(enhanced_text[:1500])
