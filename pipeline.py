"""
Main Pipeline: orchestrates the end-to-end processing of a single claim.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import OUTPUT_DIR
from src.ingestion.document_loader import load_claim, DocumentPage
from src.classification.doc_classifier import DocumentClassifier, ClassificationResult
from src.extraction.field_extractor import FieldExtractor
from src.extraction.visual_detector import VisualDetector
from src.rules.rules_engine import RulesEngine
from src.timeline.episode_builder import EpisodeTimelineBuilder
from src.decisioning.decision_engine import DecisionEngine, ClaimDecision
from src.output.report_generator import ReportGenerator

log = logging.getLogger(__name__)


class ClaimProcessor:
    """
    Processes a single claim directory end-to-end.
    """

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.classifier  = DocumentClassifier()
        self.extractor   = FieldExtractor()
        self.detector    = VisualDetector()
        self.rules_eng   = RulesEngine()
        self.tl_builder  = EpisodeTimelineBuilder()
        self.decider     = DecisionEngine()
        self.reporter    = ReportGenerator()

    def process(self, claim_dir: Path, package_code: str) -> ClaimDecision:
        claim_id = claim_dir.name
        log.info("── Processing claim: %s  [%s] ──", claim_id, package_code)

        # ── Step 1: Load documents ─────────────────────────────────────────
        pages: List[DocumentPage] = load_claim(claim_dir, package_code)
        if not pages:
            log.warning("No pages loaded for claim %s", claim_id)

        # ── Step 2: Classify documents ────────────────────────────────────
        cls_results: List[ClassificationResult] = self.classifier.classify_claim(pages)
        cls_summary_by_doc = self.classifier.summarise_claim_docs(cls_results)

        # Build maps for downstream use
        doc_type_map: Dict[str, str] = {
            doc_id: res.predicted_type
            for doc_id, res in cls_summary_by_doc.items()
        }
        doc_source_map: Dict[str, str] = {
            doc_id: res.source_path
            for doc_id, res in cls_summary_by_doc.items()
        }
        doc_class_info: Dict[str, Any] = {
            doc_id: {
                "predicted_type": res.predicted_type,
                "confidence": res.confidence,
                "signal": res.signal,
                "raw_label": res.raw_label,
                "source_path": res.source_path,
            }
            for doc_id, res in cls_summary_by_doc.items()
        }

        # ── Step 3: Extract structured fields ─────────────────────────────
        ef = self.extractor.extract(pages, claim_id=claim_id, package_code=package_code)

        # ── Step 4: Detect visual elements ────────────────────────────────
        visual_elements = self.detector.detect_all(pages)
        ef.visual_elements = visual_elements

        # ── Step 5: Build episode timeline ────────────────────────────────
        timeline = self.tl_builder.build(ef, doc_type_map, doc_source_map)

        # ── Step 6: Evaluate STG rules ────────────────────────────────────
        rule_results = self.rules_eng.evaluate(ef, doc_type_map)

        # ── Step 7: Identify extra / non-required documents ───────────────
        extra_docs = self.rules_eng.identify_extra_documents(doc_type_map, package_code)

        # ── Step 8: Make decision ─────────────────────────────────────────
        decision = self.decider.decide(claim_id, package_code, rule_results)

        # ── Step 9: Generate report ───────────────────────────────────────
        report_path = self.reporter.generate(
            decision=decision,
            ef=ef,
            timeline=timeline,
            doc_classification_summary=doc_class_info,
            extra_docs=extra_docs,
            output_dir=self.output_dir,
        )

        # Print summary to console
        self.reporter.print_summary(decision, ef, extra_docs)
        log.info("Report saved: %s", report_path)

        return decision
