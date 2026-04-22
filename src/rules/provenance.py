"""
Provenance tracker: records evidence for every rule evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RuleEvidence:
    """Single piece of evidence supporting (or failing) a rule evaluation."""
    doc_id: str
    source_path: str
    page_number: int
    field_name: str
    value: str
    confidence: float
    bounding_box: Optional[dict] = None   # {x0,y0,x1,y1,page}


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    passed: bool
    severity: str                         # "critical" | "major" | "minor"
    message: str
    evidence: List[RuleEvidence] = field(default_factory=list)
    confidence: float = 1.0

    @property
    def flag_label(self) -> str:
        if self.passed:
            return "PASS"
        return f"FAIL-{self.severity.upper()}"
