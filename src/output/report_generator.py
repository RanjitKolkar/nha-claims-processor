"""
Report Generator: serialises the full claim analysis to JSON and
generates a human-readable text summary.
"""
from __future__ import annotations

import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.decisioning.decision_engine import ClaimDecision
from src.extraction.models import ExtractedFields
from src.timeline.episode_builder import EpisodeTimeline

log = logging.getLogger(__name__)


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (date, datetime)):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


class ReportGenerator:

    def generate(
        self,
        decision: ClaimDecision,
        ef: ExtractedFields,
        timeline: EpisodeTimeline,
        doc_classification_summary: Dict[str, Any],
        extra_docs: List[str],
        output_dir: Path,
    ) -> Path:
        """
        Write the final JSON report and return its path.
        """
        report = self._assemble(
            decision, ef, timeline, doc_classification_summary, extra_docs
        )

        out_file = output_dir / f"{ef.claim_id}_{ef.package_code}_report.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=_json_default)

        log.info("Report written: %s", out_file)
        return out_file

    def _assemble(
        self,
        decision: ClaimDecision,
        ef: ExtractedFields,
        timeline: EpisodeTimeline,
        doc_classification_summary: Dict[str, Any],
        extra_docs: List[str],
    ) -> dict:
        return {
            "meta": {
                "generated_at": datetime.utcnow().isoformat(),
                "system": "Medical Claims Processor v1.0",
            },
            "claim": {
                "claim_id": ef.claim_id,
                "package_code": ef.package_code,
                "patient_name": ef.patient_name,
                "patient_id": ef.patient_id,
                "age": ef.age,
                "gender": ef.gender,
                "hospital_name": ef.hospital_name,
                "doctor_name": ef.doctor_name,
                "admission_date": ef.admission_date,
                "discharge_date": ef.discharge_date,
                "procedure_date": ef.procedure_date,
                "length_of_stay_days": ef.length_of_stay,
                "billed_amount": ef.billed_amount,
                "diagnosis": ef.diagnosis,
            },
            "decision": decision.to_dict(),
            "document_classification": [
                {
                    "doc_id": doc_id,
                    "predicted_type": info["predicted_type"],
                    "confidence": info["confidence"],
                    "signal": info["signal"],
                    "raw_label": info["raw_label"],
                    "source_path": info.get("source_path", ""),
                }
                for doc_id, info in doc_classification_summary.items()
            ],
            "extra_documents_flagged": extra_docs,
            "visual_elements": [
                {
                    "type": ve.element_type,
                    "detected": ve.detected,
                    "confidence": ve.confidence,
                    "doc_id": ve.doc_id,
                    "page": ve.page_number,
                    "decoded_value": ve.decoded_value,
                }
                for ve in ef.visual_elements
            ],
            "episode_timeline": timeline.to_dict(),
            "provenance_log": [
                {
                    "field": p.field_name,
                    "value": p.extracted_value,
                    "doc_id": p.doc_id,
                    "page": p.page_number,
                    "confidence": p.confidence,
                    "source_path": p.source_path,
                }
                for p in ef.all_provenance
            ],
        }

    def print_summary(self, decision: ClaimDecision, ef: ExtractedFields,
                      extra_docs: List[str]) -> None:
        """Print a concise text summary to stdout."""
        sep = "─" * 65
        verdict_icon = {"PASS": "✅", "CONDITIONAL": "⚠️", "FAIL": "❌"}.get(decision.verdict, "?")
        print(f"\n{sep}")
        print(f"  CLAIM  : {ef.claim_id}")
        print(f"  PACKAGE: {ef.package_code}")
        print(f"  VERDICT: {verdict_icon}  {decision.verdict}  "
              f"(score={decision.overall_score:.2%}, conf={decision.confidence:.2%})")
        print(sep)

        if decision.critical_failures:
            print("  CRITICAL FAILURES:")
            for f in decision.critical_failures:
                print(f"    ✗ {f}")

        if decision.major_failures:
            print("  MAJOR FAILURES:")
            for f in decision.major_failures:
                print(f"    ⚠ {f}")

        if decision.minor_failures:
            print("  MINOR FLAGS:")
            for f in decision.minor_failures:
                print(f"    ~ {f}")

        if extra_docs:
            print("  EXTRA / NON-REQUIRED DOCUMENTS:")
            for d in extra_docs:
                print(f"    📄 {d}")

        print(f"  Patient : {ef.patient_name or 'N/A'} | "
              f"Admit: {ef.admission_date or 'N/A'} | "
              f"Discharge: {ef.discharge_date or 'N/A'} | "
              f"LoS: {ef.length_of_stay or 'N/A'}d")
        print(sep)
