"""
Decision Engine: aggregates rule results into a Pass / Conditional / Fail verdict
with an overall confidence score and prioritised flag list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from config import PASS_THRESHOLD, CONDITIONAL_THRESHOLD, SEVERITY_WEIGHTS
from src.rules.provenance import RuleResult


@dataclass
class ClaimDecision:
    claim_id: str
    package_code: str
    verdict: str                        # "PASS" | "CONDITIONAL" | "FAIL"
    overall_score: float                # 0-1
    confidence: float                   # weighted average of rule confidences
    critical_failures: List[str] = field(default_factory=list)
    major_failures: List[str] = field(default_factory=list)
    minor_failures: List[str] = field(default_factory=list)
    passed_rules: List[str] = field(default_factory=list)
    all_results: List[RuleResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "package_code": self.package_code,
            "verdict": self.verdict,
            "overall_score": round(self.overall_score, 4),
            "confidence": round(self.confidence, 4),
            "critical_failures": self.critical_failures,
            "major_failures": self.major_failures,
            "minor_failures": self.minor_failures,
            "passed_rules": self.passed_rules,
            "rule_details": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "result": r.flag_label,
                    "message": r.message,
                    "confidence": round(r.confidence, 4),
                    "evidence": [
                        {
                            "doc_id": e.doc_id,
                            "page": e.page_number,
                            "field": e.field_name,
                            "value": e.value,
                            "confidence": round(e.confidence, 4),
                            "bounding_box": e.bounding_box,
                        }
                        for e in r.evidence
                    ],
                }
                for r in self.all_results
            ],
        }


class DecisionEngine:
    """
    Takes a list of RuleResult objects and produces a ClaimDecision.

    Scoring:
        weighted_score = Σ (passed_rule_weight) / Σ (all_rule_weights)
        where weight = SEVERITY_WEIGHTS[severity]

    Verdict thresholds (from config):
        score ≥ PASS_THRESHOLD         → PASS
        CONDITIONAL_THRESHOLD ≤ score < PASS_THRESHOLD → CONDITIONAL
        score < CONDITIONAL_THRESHOLD  → FAIL
    """

    def decide(
        self,
        claim_id: str,
        package_code: str,
        rule_results: List[RuleResult],
    ) -> ClaimDecision:

        if not rule_results:
            return ClaimDecision(
                claim_id=claim_id,
                package_code=package_code,
                verdict="CONDITIONAL",
                overall_score=0.0,
                confidence=0.0,
            )

        # ── Weighted score ────────────────────────────────────────────────────
        total_weight = sum(SEVERITY_WEIGHTS.get(r.severity, 0.2) for r in rule_results)
        passed_weight = sum(
            SEVERITY_WEIGHTS.get(r.severity, 0.2)
            for r in rule_results if r.passed
        )
        score = passed_weight / total_weight if total_weight > 0 else 0.0

        # ── Confidence (average of individual rule confidences) ───────────────
        avg_conf = sum(r.confidence for r in rule_results) / len(rule_results)

        # ── Any HIGH-CONFIDENCE critical failure → automatic FAIL ─────────────
        # Low-confidence (< 0.70) critical failures (e.g. dates unreadable from
        # landscape scans) are handled by weighted scoring only, not auto-FAIL.
        has_critical_fail = any(
            not r.passed and r.severity == "critical" and r.confidence >= 0.70
            for r in rule_results
        )

        # ── Verdict ───────────────────────────────────────────────────────────
        if has_critical_fail or score < CONDITIONAL_THRESHOLD:
            verdict = "FAIL"
        elif score < PASS_THRESHOLD:
            verdict = "CONDITIONAL"
        else:
            verdict = "PASS"

        # ── Categorise failures ───────────────────────────────────────────────
        critical_f, major_f, minor_f, passed_r = [], [], [], []
        for r in rule_results:
            if r.passed:
                passed_r.append(f"[{r.rule_id}] {r.rule_name}")
            elif r.severity == "critical":
                critical_f.append(f"[{r.rule_id}] {r.message}")
            elif r.severity == "major":
                major_f.append(f"[{r.rule_id}] {r.message}")
            else:
                minor_f.append(f"[{r.rule_id}] {r.message}")

        return ClaimDecision(
            claim_id=claim_id,
            package_code=package_code,
            verdict=verdict,
            overall_score=score,
            confidence=avg_conf,
            critical_failures=critical_f,
            major_failures=major_f,
            minor_failures=minor_f,
            passed_rules=passed_r,
            all_results=rule_results,
        )
