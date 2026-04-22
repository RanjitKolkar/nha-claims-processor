"""
Document Loader: reads PDFs and images, returns a list of DocumentPage objects
with raw text and PIL images for further processing.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from PIL import Image

from config import PDF_DPI

log = logging.getLogger(__name__)


@dataclass
class DocumentPage:
    doc_id: str                  # e.g. "000522__CMJAY_...__INITIAL_ASSESSMENT"
    claim_id: str                # parent claim folder name
    package_code: str            # e.g. "SB039A"
    source_path: str             # absolute path to original file
    page_number: int             # 1-based
    text: str                    # extracted / OCR'd text
    ocr_confidence: float        # 0-1
    ocr_engine: str              # "pdf_direct" | "tesseract" | "easyocr"
    image: Optional[Image.Image] = field(default=None, repr=False)
    width_px: int = 0
    height_px: int = 0


def _parse_filename(path: Path):
    """Extract doc_id, claim_id, doc_label from the standardised filename."""
    stem = path.stem  # e.g. 000522__CMJAY_...__INITIAL_ASSESSMENT
    parts = stem.split("__")
    doc_label = parts[-1] if len(parts) >= 3 else "UNKNOWN"
    claim_part = parts[1] if len(parts) >= 2 else stem
    # claim_id is the parent directory name
    return stem, doc_label


def load_document(
    file_path: Path,
    claim_id: str,
    package_code: str,
) -> List[DocumentPage]:
    """
    Load a single file (PDF or image) and return one DocumentPage per page.
    Text extraction: PDF native → fall back to image OCR.
    """
    suffix = file_path.suffix.lower()
    doc_id, _ = _parse_filename(file_path)
    pages: List[DocumentPage] = []

    if suffix == ".pdf":
        pages = _load_pdf(file_path, doc_id, claim_id, package_code)
    elif suffix in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}:
        pages = _load_image(file_path, doc_id, claim_id, package_code)
    else:
        log.warning("Unsupported file type: %s", file_path)

    return pages


def _load_pdf(path: Path, doc_id: str, claim_id: str, pkg: str) -> List[DocumentPage]:
    pages = []
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(path))
        for i, page in enumerate(doc):
            text = page.get_text("text").strip()
            img = None
            confidence = 1.0
            engine = "pdf_direct"

            if len(text) < 20:
                # Scanned PDF – render and OCR
                mat = fitz.Matrix(PDF_DPI / 72, PDF_DPI / 72)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                from src.ingestion.ocr_engine import ocr_image
                text, confidence, engine = ocr_image(img, aggressive=(len(text) == 0))
            else:
                # Render image anyway for visual detection (lower resolution)
                mat = fitz.Matrix(1.5, 1.5)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                w, h = img.size
            
            if img:
                w, h = img.size
            else:
                rect = page.rect
                w, h = int(rect.width), int(rect.height)

            pages.append(DocumentPage(
                doc_id=doc_id,
                claim_id=claim_id,
                package_code=pkg,
                source_path=str(path),
                page_number=i + 1,
                text=text,
                ocr_confidence=confidence,
                ocr_engine=engine,
                image=img,
                width_px=w,
                height_px=h,
            ))
        doc.close()
    except Exception as exc:
        log.error("PDF load failed %s: %s", path, exc)
    return pages


def _load_image(path: Path, doc_id: str, claim_id: str, pkg: str) -> List[DocumentPage]:
    pages = []
    try:
        img = Image.open(path).convert("RGB")
        from src.ingestion.ocr_engine import ocr_image
        text, confidence, engine = ocr_image(img)
        w, h = img.size
        pages.append(DocumentPage(
            doc_id=doc_id,
            claim_id=claim_id,
            package_code=pkg,
            source_path=str(path),
            page_number=1,
            text=text,
            ocr_confidence=confidence,
            ocr_engine=engine,
            image=img,
            width_px=w,
            height_px=h,
        ))
    except Exception as exc:
        log.error("Image load failed %s: %s", path, exc)
    return pages


def load_claim(claim_dir: Path, package_code: str) -> List[DocumentPage]:
    """Load all documents in a claim directory."""
    all_pages: List[DocumentPage] = []
    supported = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
    files = sorted(
        [f for f in claim_dir.iterdir() if f.suffix.lower() in supported],
        key=lambda f: f.name,
    )
    claim_id = claim_dir.name
    log.info("Loading claim %s (%d files)", claim_id, len(files))
    for f in files:
        pages = load_document(f, claim_id=claim_id, package_code=package_code)
        all_pages.extend(pages)
    return all_pages
