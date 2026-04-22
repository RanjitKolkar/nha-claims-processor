"""
Test pipeline on MC011A claim with UUID filenames (harder case - content-based classification).
"""
from pipeline import ClaimProcessor
from pathlib import Path

claim_dir = Path(r"extract_2\Claims\MC011A\BOCW_GJ_R3_2026040310046613_ER")
package_code = "MC011A"

print(f"Processing: {claim_dir.name}")
print(f"Package:    {package_code}")
print("-" * 60)

proc = ClaimProcessor()
decision = proc.process(claim_dir, package_code)

print(f"\nFinal verdict: {decision.verdict}  (score={decision.overall_score:.1%}, conf={decision.confidence:.1%})")
