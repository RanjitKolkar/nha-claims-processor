"""
Preprocessor: enhance low-quality scanned images before OCR.
"""
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance


def pil_to_cv2(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def cv2_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


def enhance_image(img: Image.Image, aggressive: bool = False) -> Image.Image:
    """
    Apply a pipeline of enhancements designed for scanned medical documents.
    aggressive=True uses heavier denoising for very low-quality scans.
    """
    # 1. Convert to greyscale for OCR
    grey = img.convert("L")

    # 2. Resize if very small (upscale to help OCR)
    w, h = grey.size
    if max(w, h) < 1200:
        scale = 1200 / max(w, h)
        grey = grey.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # 3. Contrast enhancement
    grey = ImageEnhance.Contrast(grey).enhance(1.8)
    grey = ImageEnhance.Sharpness(grey).enhance(2.0)

    # 4. Convert to numpy for cv2 operations
    arr = np.array(grey)

    if aggressive:
        arr = cv2.fastNlMeansDenoising(arr, h=15, templateWindowSize=7, searchWindowSize=21)

    # 5. Adaptive thresholding (binarise)
    arr = cv2.adaptiveThreshold(
        arr, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=10,
    )

    # 6. Deskew
    arr = _deskew(arr)

    return Image.fromarray(arr)


def auto_orient(img: Image.Image) -> Image.Image:
    """
    Detect and correct page orientation using Tesseract OSD (single pass).
    Much faster than trying all 4 orientations with full OCR.
    Falls back to identity if OSD fails.
    """
    import pytesseract
    try:
        # OSD: orientation and script detection (very fast)
        osd = pytesseract.image_to_osd(img, config="--psm 0 -c min_characters_to_try=5")
        for line in osd.split("\n"):
            if "Rotate:" in line:
                angle = int(line.split(":")[-1].strip())
                if angle != 0:
                    return img.rotate(-angle, expand=True)
                break
    except Exception:
        pass
    return img


def _orient_score(img: Image.Image) -> float:
    """
    Quick proxy for OCR quality: count recognisable ASCII word characters
    in a Tesseract run with low timeout settings.
    """
    import pytesseract
    from config import TESSERACT_LANG
    try:
        enhanced = enhance_image(img)
        text = pytesseract.image_to_string(
            enhanced, lang="eng",
            config="--oem 3 --psm 3 --tessdata-dir . -c tessedit_char_whitelist="
                   "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
        )
        # Score = number of word-like tokens (3+ chars)
        return sum(1 for tok in text.split() if len(tok) >= 3)
    except Exception:
        return 0


def _deskew(binary_arr: np.ndarray) -> np.ndarray:
    """Correct skew of up to ±15 degrees."""
    coords = np.column_stack(np.where(binary_arr < 128))
    if len(coords) < 100:
        return binary_arr
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 0.5:
        return binary_arr
    h, w = binary_arr.shape
    centre = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(centre, angle, 1.0)
    rotated = cv2.warpAffine(binary_arr, M, (w, h), flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    return rotated
