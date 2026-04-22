"""
Evaluation Script: computes F1 scores for:
  1. Document Classification (vs. ground truth = filename labels)
  2. Rule / Decision evaluation (vs. ground truth = claim-level verdicts if available)

Usage:
  python evaluate.py --mode classification
  python evaluate.py --mode decision --gt ground_truth.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


def _canonical_from_filename(doc_id: str) -> str:
    """Derive ground-truth type from the filename label (same logic as classifier)."""
    from src.classification.doc_types import FILENAME_LABEL_MAP, OTHER
    parts = doc_id.split("__")
    if len(parts) >= 3:
        label = parts[-1].upper().strip()
        if label in FILENAME_LABEL_MAP:
            return FILENAME_LABEL_MAP[label]
    return OTHER


def eval_classification(output_dir: Path) -> None:
    """
    For each report JSON, compare predicted doc type vs. ground truth (from filename).
    Reports per-class precision, recall, F1 and macro-F1.
    """
    from sklearn.metrics import classification_report

    y_true, y_pred = [], []
    report_files = list(output_dir.glob("*_report.json"))
    if not report_files:
        print("No report JSON files found in", output_dir)
        return

    for rp in report_files:
        with open(rp, encoding="utf-8") as f:
            data = json.load(f)
        for doc in data.get("document_classification", []):
            doc_id = doc["doc_id"]
            pred = doc["predicted_type"]
            gt = _canonical_from_filename(doc_id)
            y_true.append(gt)
            y_pred.append(pred)

    if not y_true:
        print("No classification data found.")
        return

    print("\n── Document Classification Metrics ──────────────────────────")
    print(classification_report(y_true, y_pred, zero_division=0))

    # Macro F1
    from sklearn.metrics import f1_score
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    print(f"  Macro F1: {macro_f1:.4f}")

    # Mapping to competition rank
    if macro_f1 >= 0.95:
        print("  → Rank 1 eligible (F1 ≥ 0.95)")
    elif macro_f1 >= 0.90:
        print("  → Rank 2 eligible (F1 ≥ 0.90)")
    elif macro_f1 >= 0.85:
        print("  → Rank 3 eligible (F1 ≥ 0.85)")
    else:
        print("  → Below qualification threshold")


def eval_decision(output_dir: Path, gt_csv: Path) -> None:
    """
    Compare predicted verdicts vs. ground truth from a CSV file.
    GT CSV format: claim_id, verdict (PASS / CONDITIONAL / FAIL)
    """
    from sklearn.metrics import classification_report, f1_score

    gt_map: Dict[str, str] = {}
    with open(gt_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gt_map[row["claim_id"]] = row["verdict"].upper()

    y_true, y_pred = [], []
    for rp in output_dir.glob("*_report.json"):
        with open(rp, encoding="utf-8") as f:
            data = json.load(f)
        claim_id = data["claim"]["claim_id"]
        pred_verdict = data["decision"]["verdict"]
        if claim_id in gt_map:
            y_true.append(gt_map[claim_id])
            y_pred.append(pred_verdict)

    if not y_true:
        print("No matching claims found for evaluation.")
        return

    print("\n── Decision / Verdict Metrics ───────────────────────────────")
    print(classification_report(y_true, y_pred, zero_division=0))
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    print(f"  Macro F1: {macro_f1:.4f}")
    if macro_f1 >= 0.96:
        print("  → Rank 1 eligible (F1 ≥ 0.96)")
    elif macro_f1 >= 0.90:
        print("  → Rank 2 eligible (F1 ≥ 0.90)")
    elif macro_f1 >= 0.85:
        print("  → Rank 3 eligible (F1 ≥ 0.85)")
    else:
        print("  → Below qualification threshold")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["classification", "decision", "both"],
                        default="classification")
    parser.add_argument("--output-dir", type=Path, default=Path("output_reports"))
    parser.add_argument("--gt", type=Path, default=None,
                        help="Ground truth CSV for decision evaluation")
    args = parser.parse_args()

    if args.mode in ("classification", "both"):
        eval_classification(args.output_dir)
    if args.mode in ("decision", "both"):
        if args.gt is None:
            print("--gt required for decision evaluation")
        else:
            eval_decision(args.output_dir, args.gt)
