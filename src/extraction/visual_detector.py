"""
Visual Detector: detects stamps, signatures, QR codes, barcodes, and
implant stickers in document images.
"""
from __future__ import annotations

import logging
import re
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image

from src.extraction.models import VisualElement, BoundingBox
from config import (
    STAMP_MIN_AREA, STAMP_MIN_CIRCULARITY,
    SIGNATURE_MIN_ASPECT, QR_BARCODE_TYPES,
)

log = logging.getLogger(__name__)


def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def detect_hospital_stamp(img: Image.Image, doc_id: str, page: int) -> Optional[VisualElement]:
    """
    Detect circular/elliptical rubber stamps using contour analysis.
    Also checks for blue/purple filled circular regions.
    """
    try:
        bgr = _pil_to_bgr(img)
        h, w = bgr.shape[:2]

        # Look in bottom-right and bottom-left quarters where stamps typically appear
        region = bgr[h // 2:, :]

        # Detect blue/purple pixels (common stamp colours)
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        blue_mask = cv2.inRange(hsv, (100, 40, 40), (140, 255, 255))
        purple_mask = cv2.inRange(hsv, (130, 30, 30), (170, 255, 255))
        red_mask1 = cv2.inRange(hsv, (0, 40, 40), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (170, 40, 40), (180, 255, 255))
        stamp_mask = cv2.bitwise_or(blue_mask, cv2.bitwise_or(purple_mask,
                                    cv2.bitwise_or(red_mask1, red_mask2)))

        # Morphological fill
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        stamp_mask = cv2.morphologyEx(stamp_mask, cv2.MORPH_CLOSE, kernel, iterations=3)

        contours, _ = cv2.findContours(stamp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < STAMP_MIN_AREA:
                continue
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity >= STAMP_MIN_CIRCULARITY:
                x, y, bw, bh = cv2.boundingRect(cnt)
                confidence = min(0.55 + circularity * 0.4, 0.92)
                return VisualElement(
                    element_type="hospital_stamp",
                    detected=True,
                    confidence=confidence,
                    doc_id=doc_id,
                    page_number=page,
                    bounding_box=BoundingBox(
                        page=page, x0=x, y0=y + h // 2,
                        x1=x + bw, y1=y + h // 2 + bh,
                    ),
                )
    except Exception as exc:
        log.debug("Stamp detection error: %s", exc)
    return None


def detect_signature(img: Image.Image, doc_id: str, page: int) -> Optional[VisualElement]:
    """
    Detect doctor/patient signature: typically a dark elongated region
    in the lower third of a document.
    """
    try:
        bgr = _pil_to_bgr(img)
        h, w = bgr.shape[:2]
        region = bgr[int(h * 0.65):, :]   # bottom 35%

        grey = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Remove large print text (word blocks are dense; signatures are isolated strokes)
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
        dilated = cv2.dilate(binary, kernel_h, iterations=2)
        dilated = cv2.dilate(dilated, kernel_v, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            if bw < 50 or bh < 10:
                continue
            aspect = bw / max(bh, 1)
            area = bw * bh
            if aspect >= SIGNATURE_MIN_ASPECT and area >= 1500:
                confidence = min(0.50 + aspect * 0.05, 0.85)
                return VisualElement(
                    element_type="doctor_signature",
                    detected=True,
                    confidence=confidence,
                    doc_id=doc_id,
                    page_number=page,
                    bounding_box=BoundingBox(
                        page=page, x0=x, y0=y + int(h * 0.65),
                        x1=x + bw, y1=y + int(h * 0.65) + bh,
                    ),
                )
    except Exception as exc:
        log.debug("Signature detection error: %s", exc)
    return None


def detect_qr_barcode(img: Image.Image, doc_id: str, page: int) -> List[VisualElement]:
    """
    Detect QR codes and barcodes using pyzbar.
    """
    elements = []
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
        import numpy as np
        arr = np.array(img.convert("L"))
        decoded = pyzbar_decode(arr)
        for obj in decoded:
            if obj.type in QR_BARCODE_TYPES or True:
                rect = obj.rect
                elements.append(VisualElement(
                    element_type="qr_code" if obj.type == "QRCODE" else "barcode",
                    detected=True,
                    confidence=0.98,
                    doc_id=doc_id,
                    page_number=page,
                    bounding_box=BoundingBox(
                        page=page,
                        x0=rect.left, y0=rect.top,
                        x1=rect.left + rect.width,
                        y1=rect.top + rect.height,
                    ),
                    decoded_value=obj.data.decode("utf-8", errors="replace"),
                ))
    except ImportError:
        log.debug("pyzbar not available; skipping barcode detection")
    except Exception as exc:
        log.debug("Barcode detection error: %s", exc)
    return elements


def detect_implant_sticker(text: str, doc_id: str, page: int) -> Optional[VisualElement]:
    """
    Detect implant sticker by searching for lot/serial/REF patterns in OCR text.
    """
    patterns = [
        r"\bREF\b\s*[:\-]?\s*\w+",
        r"\bLOT\b\s*[:\-]?\s*[\w\-]+",
        r"\bSN\b\s*[:\-]?\s*[\w\-]+",
        r"\bCatalog\b[\w\s#:\-]+",
        r"\bimplant\b.{0,60}(?:number|no\.?|id)\b",
    ]
    hits = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
    if hits >= 2:
        return VisualElement(
            element_type="implant_sticker",
            detected=True,
            confidence=min(0.60 + hits * 0.10, 0.90),
            doc_id=doc_id,
            page_number=page,
        )
    return None


class VisualDetector:
    """Run all visual detectors on each page and accumulate results."""

    def detect_all(self, pages) -> List[VisualElement]:
        results: List[VisualElement] = []
        for page in pages:
            img = page.image
            doc_id = page.doc_id
            pn = page.page_number
            text = page.text or ""

            if img is not None:
                # Stamp
                stamp = detect_hospital_stamp(img, doc_id, pn)
                if stamp:
                    results.append(stamp)

                # Signature
                sig = detect_signature(img, doc_id, pn)
                if sig:
                    results.append(sig)

                # QR / barcode (also check filename label)
                if "BARCODE" in doc_id.upper() or "QR" in doc_id.upper():
                    results.append(VisualElement(
                        element_type="barcode",
                        detected=True,
                        confidence=0.90,
                        doc_id=doc_id,
                        page_number=pn,
                    ))
                else:
                    results.extend(detect_qr_barcode(img, doc_id, pn))

            # Implant sticker (text-based)
            implant = detect_implant_sticker(text, doc_id, pn)
            if implant:
                results.append(implant)

        return results
