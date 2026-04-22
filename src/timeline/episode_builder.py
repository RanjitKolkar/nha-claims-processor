"""
Episode Timeline Builder:
- Extracts all dates from each document
- Assigns event types based on document type
- Orders events chronologically
- Validates temporal plausibility
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

from src.extraction.models import ExtractedFields
from src.classification.doc_types import (
    ADMISSION_FORM, DISCHARGE_SUMMARY, OPERATIVE_NOTES,
    LAB_INVESTIGATION, XRAY_IMAGE, RADIOLOGY_REPORT, USG_REPORT,
    IVP_REPORT, ANGIOGRAPHY_REPORT, PROCEDURE_REPORT, CT_MRI_REPORT,
    CLINICAL_NOTES, BEDSIDE_CHART, VITAL_CHART, NURSING_NOTES,
    MEDICATION_CHART, FEEDBACK_FORM, BILL_INVOICE, ANESTHESIA_NOTES,
)

log = logging.getLogger(__name__)

# ── Event type taxonomy ───────────────────────────────────────────────────────
EVENT_ADMISSION              = "Admission"
EVENT_DIAGNOSTIC_INVESTIGATION = "Diagnostic Investigation"
EVENT_PROCEDURE              = "Procedure (Package)"
EVENT_POST_PROCEDURE         = "Post-Procedure Monitoring"
EVENT_DISCHARGE              = "Discharge"
EVENT_BILLING                = "Billing / Administrative"
EVENT_OTHER                  = "Other"

DOC_TYPE_TO_EVENT: Dict[str, str] = {
    ADMISSION_FORM:          EVENT_ADMISSION,
    DISCHARGE_SUMMARY:       EVENT_DISCHARGE,
    OPERATIVE_NOTES:         EVENT_PROCEDURE,
    ANESTHESIA_NOTES:        EVENT_PROCEDURE,
    ANGIOGRAPHY_REPORT:      EVENT_PROCEDURE,
    PROCEDURE_REPORT:        EVENT_PROCEDURE,
    LAB_INVESTIGATION:       EVENT_DIAGNOSTIC_INVESTIGATION,
    XRAY_IMAGE:              EVENT_DIAGNOSTIC_INVESTIGATION,
    RADIOLOGY_REPORT:        EVENT_DIAGNOSTIC_INVESTIGATION,
    USG_REPORT:              EVENT_DIAGNOSTIC_INVESTIGATION,
    IVP_REPORT:              EVENT_DIAGNOSTIC_INVESTIGATION,
    CT_MRI_REPORT:           EVENT_DIAGNOSTIC_INVESTIGATION,
    CLINICAL_NOTES:          EVENT_POST_PROCEDURE,
    BEDSIDE_CHART:           EVENT_POST_PROCEDURE,
    VITAL_CHART:             EVENT_POST_PROCEDURE,
    NURSING_NOTES:           EVENT_POST_PROCEDURE,
    MEDICATION_CHART:        EVENT_POST_PROCEDURE,
    BILL_INVOICE:            EVENT_BILLING,
    FEEDBACK_FORM:           EVENT_BILLING,
}


@dataclass
class TimelineEvent:
    sequence: int
    event_type: str
    event_date: Optional[date]
    source_doc_id: str
    source_doc_type: str
    source_path: str
    temporal_validity: str    # "Valid" | "Warning" | "Invalid" | "Unknown"
    validity_reason: str = ""


@dataclass
class EpisodeTimeline:
    claim_id: str
    events: List[TimelineEvent] = field(default_factory=list)
    is_plausible: bool = True
    plausibility_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "is_plausible": self.is_plausible,
            "plausibility_flags": self.plausibility_flags,
            "events": [
                {
                    "sequence": e.sequence,
                    "event_type": e.event_type,
                    "date": str(e.event_date) if e.event_date else None,
                    "source_document": e.source_doc_id,
                    "source_path": e.source_path,
                    "temporal_validity": e.temporal_validity,
                    "validity_reason": e.validity_reason,
                }
                for e in self.events
            ],
        }


class EpisodeTimelineBuilder:
    """
    Builds the episode timeline from extracted fields + document classifications.
    """

    def build(
        self,
        ef: ExtractedFields,
        doc_type_map: Dict[str, str],            # {doc_id → canonical_type}
        doc_source_map: Dict[str, str],          # {doc_id → source_path}
    ) -> EpisodeTimeline:

        tl = EpisodeTimeline(claim_id=ef.claim_id)
        raw_events: List[Tuple[Optional[date], str, str, str]] = []
        # (date, event_type, doc_id, source_path)

        # ── Seed from extracted structured fields ────────────────────────────
        if ef.admission_date:
            raw_events.append((
                ef.admission_date, EVENT_ADMISSION,
                ef.admission_date_provenance.doc_id if ef.admission_date_provenance else "",
                ef.admission_date_provenance.source_path if ef.admission_date_provenance else "",
            ))

        if ef.procedure_date:
            raw_events.append((
                ef.procedure_date, EVENT_PROCEDURE,
                ef.procedure_date_provenance.doc_id if ef.procedure_date_provenance else "",
                ef.procedure_date_provenance.source_path if ef.procedure_date_provenance else "",
            ))

        if ef.discharge_date:
            raw_events.append((
                ef.discharge_date, EVENT_DISCHARGE,
                ef.discharge_date_provenance.doc_id if ef.discharge_date_provenance else "",
                ef.discharge_date_provenance.source_path if ef.discharge_date_provenance else "",
            ))

        # ── Add one event per document type in claim ─────────────────────────
        seen_types: set = set()
        for doc_id, doc_type in doc_type_map.items():
            event_type = DOC_TYPE_TO_EVENT.get(doc_type, EVENT_OTHER)
            sp = doc_source_map.get(doc_id, "")

            # Only add doc-level events for investigation / procedure types
            # to avoid bloat; admission/discharge already seeded above
            if event_type in (EVENT_DIAGNOSTIC_INVESTIGATION, EVENT_BILLING, EVENT_OTHER):
                key = (event_type, doc_type)
                if key not in seen_types:
                    raw_events.append((None, event_type, doc_id, sp))
                    seen_types.add(key)

        # ── Sort: dated events first, then undated ────────────────────────────
        def sort_key(ev):
            d = ev[0]
            return (0 if d is None else 1, d or date.min, ev[1])

        # Sort dated events chronologically; undated go to estimated position
        dated = sorted(
            [(d, et, di, sp) for d, et, di, sp in raw_events if d is not None],
            key=lambda x: x[0],
        )
        undated = [(d, et, di, sp) for d, et, di, sp in raw_events if d is None]

        ordered = dated + undated

        # ── Assign sequences and validate ─────────────────────────────────────
        admission_date = ef.admission_date
        procedure_date = ef.procedure_date
        discharge_date = ef.discharge_date

        for seq, (evt_date, evt_type, doc_id, sp) in enumerate(ordered, start=1):
            validity = "Unknown"
            reason = ""

            if evt_date is None:
                validity = "Unknown"
                reason = "Date not extracted from document"
            else:
                validity = "Valid"
                # Check specific plausibility
                if evt_type == EVENT_DIAGNOSTIC_INVESTIGATION:
                    if admission_date and evt_date > admission_date:
                        from config import MAX_PRE_ADMIT_DAYS
                        # Post-admission investigations are fine
                        validity = "Valid"
                        reason = "Investigation during/after admission."
                    elif admission_date:
                        delta = (admission_date - evt_date).days
                        from config import MAX_PRE_ADMIT_DAYS
                        if delta <= MAX_PRE_ADMIT_DAYS:
                            validity = "Valid"
                            reason = f"Pre-admission investigation {delta}d before admit (≤{MAX_PRE_ADMIT_DAYS}d)."
                        else:
                            validity = "Warning"
                            reason = f"Investigation {delta}d before admission (>{MAX_PRE_ADMIT_DAYS}d)."
                            tl.plausibility_flags.append(
                                f"[{doc_id}] investigation date {evt_date} is {delta} days before admission."
                            )

                elif evt_type == EVENT_PROCEDURE:
                    if admission_date and evt_date < admission_date:
                        validity = "Invalid"
                        reason = "Procedure dated before admission."
                        tl.is_plausible = False
                        tl.plausibility_flags.append(
                            f"[{doc_id}] procedure date {evt_date} is before admission {admission_date}."
                        )
                    elif discharge_date and evt_date > discharge_date:
                        validity = "Invalid"
                        reason = "Procedure dated after discharge."
                        tl.is_plausible = False
                        tl.plausibility_flags.append(
                            f"[{doc_id}] procedure date {evt_date} is after discharge {discharge_date}."
                        )
                    else:
                        validity = "Valid"
                        reason = "Procedure within admission window."

                elif evt_type == EVENT_DISCHARGE:
                    if admission_date and evt_date < admission_date:
                        validity = "Invalid"
                        reason = "Discharge before admission."
                        tl.is_plausible = False
                        tl.plausibility_flags.append(
                            f"Discharge date {evt_date} is before admission {admission_date}."
                        )
                    else:
                        validity = "Valid"
                        reason = "After treatment."

            tl.events.append(TimelineEvent(
                sequence=seq,
                event_type=evt_type,
                event_date=evt_date,
                source_doc_id=doc_id,
                source_doc_type=doc_type_map.get(doc_id, "unknown"),
                source_path=sp,
                temporal_validity=validity,
                validity_reason=reason,
            ))

        return tl
