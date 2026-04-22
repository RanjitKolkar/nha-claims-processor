"""
Run the full pipeline on a single real claim from the extracted data.
"""
from pipeline import ClaimProcessor
from pathlib import Path

# Single SB039A claim
claim_dir = Path(r"extract_1\Claims\SB039A\CMJAY_TR_CMJAY_2025_R3_1021740400")
package_code = "SB039A"

print(f"Processing: {claim_dir.name}")
print(f"Package:    {package_code}")
print("-" * 60)

proc = ClaimProcessor()
decision = proc.process(claim_dir, package_code)

print(f"\nFinal verdict: {decision.verdict}  (score={decision.overall_score:.1%}, conf={decision.confidence:.1%})")
