"""
Batch Processor: iterates over all Claims/<PackageCode>/<ClaimID>/ directories
and processes each claim, then writes a master summary CSV.
"""
from __future__ import annotations

import argparse
import csv
import io
import logging
import sys
from pathlib import Path

# Force UTF-8 stdout so logging/prints don't crash on Windows cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from config import CLAIMS_ROOTS, OUTPUT_DIR
from pipeline import ClaimProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def discover_claims(roots=CLAIMS_ROOTS):
    """
    Yields (claim_dir, package_code) for every claim found.
    Expected structure: <root>/<PackageCode>/<ClaimID>/
    """
    for root in roots:
        if not Path(root).exists():
            log.warning("Claims root not found: %s", root)
            continue
        for pkg_dir in sorted(Path(root).iterdir()):
            if not pkg_dir.is_dir():
                continue
            package_code = pkg_dir.name
            if package_code.startswith("."):
                continue
            for claim_dir in sorted(pkg_dir.iterdir()):
                if not claim_dir.is_dir():
                    continue
                if claim_dir.name.startswith("."):
                    continue
                yield claim_dir, package_code


def run_batch(limit: int = 0, package_filter: str = None):
    processor = ClaimProcessor(output_dir=OUTPUT_DIR)
    summary_rows = []
    count = 0

    for claim_dir, package_code in discover_claims():
        if package_filter and package_code != package_filter:
            continue
        if limit and count >= limit:
            break

        try:
            decision = processor.process(claim_dir, package_code)
            summary_rows.append({
                "claim_id": decision.claim_id,
                "package_code": decision.package_code,
                "verdict": decision.verdict,
                "score": round(decision.overall_score, 4),
                "confidence": round(decision.confidence, 4),
                "critical_failures": len(decision.critical_failures),
                "major_failures": len(decision.major_failures),
                "minor_failures": len(decision.minor_failures),
            })
        except Exception as exc:
            log.error("Failed to process claim %s: %s", claim_dir.name, exc, exc_info=True)
            summary_rows.append({
                "claim_id": claim_dir.name,
                "package_code": package_code,
                "verdict": "ERROR",
                "score": 0,
                "confidence": 0,
                "critical_failures": -1,
                "major_failures": -1,
                "minor_failures": -1,
            })
        count += 1

    # Write summary CSV
    summary_path = OUTPUT_DIR / "batch_summary.csv"
    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_rows)
        log.info("Batch summary written: %s", summary_path)

    # Print stats
    total = len(summary_rows)
    passed = sum(1 for r in summary_rows if r["verdict"] == "PASS")
    conditional = sum(1 for r in summary_rows if r["verdict"] == "CONDITIONAL")
    failed = sum(1 for r in summary_rows if r["verdict"] == "FAIL")
    errors = sum(1 for r in summary_rows if r["verdict"] == "ERROR")

    print(f"\n{'='*55}")
    print(f"  BATCH COMPLETE: {total} claims processed")
    print(f"  [PASS]        : {passed}")
    print(f"  [CONDITIONAL] : {conditional}")
    print(f"  [FAIL]        : {failed}")
    print(f"  [ERROR]       : {errors}")
    print(f"{'='*55}\n")

    return summary_rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch process medical claims")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max number of claims to process (0 = all)")
    parser.add_argument("--package", type=str, default=None,
                        help="Process only claims with this package code")
    args = parser.parse_args()
    run_batch(limit=args.limit, package_filter=args.package)
