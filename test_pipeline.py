"""
Quick smoke test: rules engine + decision engine + timeline builder
(no OCR required - uses mocked data)
"""
from datetime import date
from src.extraction.models import ExtractedFields, ProvenanceRef, VisualElement
from src.rules.rules_engine import RulesEngine
from src.decisioning.decision_engine import DecisionEngine
from src.timeline.episode_builder import EpisodeTimelineBuilder
from src.output.report_generator import ReportGenerator
from pathlib import Path

# ── Mock a SB039A (Knee Replacement) claim with all required docs ─────────────
ef = ExtractedFields(
    claim_id="TEST_SB039A_CLAIM_001",
    package_code="SB039A",
    patient_name="Ram Prasad",
    patient_id="PMJAY123456",
    age=62,
    gender="Male",
    admission_date=date(2026, 2, 2),
    procedure_date=date(2026, 2, 3),
    discharge_date=date(2026, 2, 10),
    diagnosis=["osteoarthritis knee", "total knee arthroplasty performed"],
    billed_amount=85000,
    hospital_name="City Ortho Hospital",
    doctor_name="Dr. Suresh Kumar",
)

# Provenance
ef.admission_date_provenance = ProvenanceRef(
    doc_id="001__TEST__DISCHARGE_SUMMARY", source_path="/test/DS.pdf",
    page_number=1, field_name="admission_date",
    extracted_value="2026-02-02", confidence=0.85
)
ef.discharge_date_provenance = ProvenanceRef(
    doc_id="001__TEST__DISCHARGE_SUMMARY", source_path="/test/DS.pdf",
    page_number=1, field_name="discharge_date",
    extracted_value="2026-02-10", confidence=0.85
)
ef.procedure_date_provenance = ProvenanceRef(
    doc_id="002__TEST__OT_NOTE", source_path="/test/OT.pdf",
    page_number=1, field_name="procedure_date",
    extracted_value="2026-02-03", confidence=0.78
)
ef.all_provenance = [ef.admission_date_provenance, ef.discharge_date_provenance, ef.procedure_date_provenance]
ef.all_provenance.append(ProvenanceRef(
    doc_id="001__TEST__DISCHARGE_SUMMARY", source_path="/test/DS.pdf",
    page_number=1, field_name="diagnosis",
    extracted_value="osteoarthritis knee", confidence=0.72
))

# Visual elements
ef.visual_elements = [
    VisualElement(element_type="hospital_stamp", detected=True, confidence=0.88,
                  doc_id="001__TEST__DISCHARGE_SUMMARY", page_number=1),
    VisualElement(element_type="doctor_signature", detected=True, confidence=0.82,
                  doc_id="002__TEST__OT_NOTE", page_number=1),
    VisualElement(element_type="barcode", detected=True, confidence=0.95,
                  doc_id="003__TEST__BARCODE", page_number=1),
]

# Document type map (all required docs present)
doc_type_map = {
    "001__TEST__DISCHARGE_SUMMARY": "discharge_summary",
    "002__TEST__OT_NOTE": "operative_notes",
    "003__TEST__BARCODE": "barcode_sticker",
    "004__TEST__XRAY": "xray_image",
    "005__TEST__ADHAR": "identity_document",
    "006__TEST__PRE_AUTHORIZATION": "preauthorization_form",
    "007__TEST__ANAESTH_SLIP": "anesthesia_notes",
    "008__TEST__CBC": "lab_investigation",
    "009__TEST__CASE_SHEET": "case_sheet",
    "010__TEST__FEEDBACK": "feedback_form",
    "011__TEST__BILL": "bill_invoice",
}

doc_source_map = {k: f"/test/{k}.pdf" for k in doc_type_map}

# ── Run pipeline components ────────────────────────────────────────────────────
eng = RulesEngine()
results = eng.evaluate(ef, doc_type_map)

print(f"\n{'='*60}")
print(f"Rules Evaluated: {len(results)}")
print(f"Passed: {sum(1 for r in results if r.passed)}")
print(f"Failed: {sum(1 for r in results if not r.passed)}")
print()

for r in results:
    icon = "✅" if r.passed else "❌"
    print(f"  {icon} [{r.rule_id}] {r.rule_name}")
    if not r.passed:
        print(f"       → {r.message}")
    if r.evidence:
        for e in r.evidence:
            print(f"         Evidence: doc={e.doc_id}, field={e.field_name}, value={e.value}, page={e.page_number}")

# ── Decision ──────────────────────────────────────────────────────────────────
decider = DecisionEngine()
decision = decider.decide("TEST_SB039A_CLAIM_001", "SB039A", results)
print(f"\n{'='*60}")
print(f"VERDICT: {decision.verdict}  (score={decision.overall_score:.2%}, conf={decision.confidence:.2%})")
print(f"LoS: {ef.length_of_stay} days")

# ── Timeline ─────────────────────────────────────────────────────────────────
tl_builder = EpisodeTimelineBuilder()
timeline = tl_builder.build(ef, doc_type_map, doc_source_map)
print(f"\n{'='*60}")
print("Episode Timeline:")
for ev in timeline.events[:8]:
    date_str = str(ev.event_date) if ev.event_date else "N/A"
    print(f"  [{ev.sequence}] {ev.event_type:35s} {date_str:12s} [{ev.temporal_validity}]")

# ── Extra docs check ──────────────────────────────────────────────────────────
extras = eng.identify_extra_documents(doc_type_map, "SB039A")
print(f"\nExtra/non-required documents: {extras or 'None'}")

# ── Full report ───────────────────────────────────────────────────────────────
reporter = ReportGenerator()
reporter.print_summary(decision, ef, extras)
print("Smoke test PASSED.")
