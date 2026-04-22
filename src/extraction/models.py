"""
Pydantic data models for structured claim data.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    page: int
    x0: float = 0
    y0: float = 0
    x1: float = 0
    y1: float = 0


class ProvenanceRef(BaseModel):
    doc_id: str
    source_path: str
    page_number: int
    field_name: str
    extracted_value: str
    confidence: float
    bounding_box: Optional[BoundingBox] = None


class VisualElement(BaseModel):
    element_type: str          # "hospital_stamp" | "doctor_signature" | "qr_code" | "barcode" | "implant_sticker"
    detected: bool
    confidence: float
    doc_id: str
    page_number: int
    bounding_box: Optional[BoundingBox] = None
    decoded_value: Optional[str] = None   # for QR / barcode


class ExtractedFields(BaseModel):
    """Structured fields extracted from a claim's documents."""
    claim_id: str
    package_code: str

    # Patient demographics
    patient_name: Optional[str] = None
    patient_name_provenance: Optional[ProvenanceRef] = None

    patient_id: Optional[str] = None
    patient_id_provenance: Optional[ProvenanceRef] = None

    age: Optional[int] = None
    gender: Optional[str] = None

    # Dates
    admission_date: Optional[date] = None
    admission_date_provenance: Optional[ProvenanceRef] = None

    discharge_date: Optional[date] = None
    discharge_date_provenance: Optional[ProvenanceRef] = None

    procedure_date: Optional[date] = None
    procedure_date_provenance: Optional[ProvenanceRef] = None

    # Clinical
    diagnosis: List[str] = Field(default_factory=list)
    procedures: List[str] = Field(default_factory=list)
    icd_codes: List[str] = Field(default_factory=list)

    # Financial
    billed_amount: Optional[float] = None
    package_amount: Optional[float] = None

    # Hospital / Doctor
    hospital_name: Optional[str] = None
    doctor_name: Optional[str] = None

    # Visual elements found across all documents
    visual_elements: List[VisualElement] = Field(default_factory=list)

    # All provenance references
    all_provenance: List[ProvenanceRef] = Field(default_factory=list)

    # Length of stay (computed)
    @property
    def length_of_stay(self) -> Optional[int]:
        if self.admission_date and self.discharge_date:
            return (self.discharge_date - self.admission_date).days
        return None
