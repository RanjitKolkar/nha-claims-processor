import json

d = json.load(open("output_reports/CMJAY_TR_CMJAY_2025_R3_1021740400_SB039A_report.json"))
cl = d["claim"]
dec = d["decision"]
dc = d["document_classification"]

print("=== CLAIM ===")
print(f"  claim:    {cl['claim_id']}")
print(f"  pkg:      {cl['package_code']}")
print(f"  patient:  {cl['patient_name']}")
print(f"  admit:    {cl['admission_date']}")
print(f"  discharge:{cl['discharge_date']}")
print(f"  LoS:      {cl['length_of_stay_days']} days")
print(f"  amount:   {cl['billed_amount']}")
print(f"  dx:       {cl['diagnosis']}")

print("\n=== DECISION ===")
print(f"  verdict:  {dec['verdict']}")
print(f"  score:    {dec['overall_score']:.1%}")
print(f"  conf:     {dec['confidence']:.1%}")
print(f"  critical: {dec['critical_failures']}")
print(f"  major:    {dec['major_failures']}")

print("\n=== RULE RESULTS ===")
for r in dec.get("rule_details", []):
    result_str = r.get("result", "")
    icon = "OK " if result_str == "PASS" else "FAIL"
    print(f"  [{icon}] {r['rule_id']} {r['rule_name']}")
    if result_str != "PASS":
        print(f"          -> {r.get('message','')}")
    for ev in r.get("evidence", []):
        print(f"          ev: doc={ev.get('doc_id','')[:40]}  field={ev.get('field',ev.get('field_name',''))}  val={str(ev.get('value',''))[:30]}")

print("\n=== DOCUMENT CLASSIFICATION ===")
for r in dc:
    dtype = r.get('predicted_type') or r.get('doc_type', 'unknown')
    print(f"  {r['doc_id'][:55]:55s} -> {dtype:25s} [sig={r.get('signal')}, conf={r.get('confidence')}]")

print("\n=== VISUAL ELEMENTS ===")
for v in d.get("visual_elements", []):
    print(f"  {v.get('type', v.get('element_type','?')):25s} detected={v['detected']}  conf={v['confidence']:.2f}  doc={v.get('doc_id','?')[:40]}")

print("\n=== EXTRA DOCUMENTS ===", d.get("extra_documents_flagged", []) or "None")

tl = d.get("episode_timeline", {}).get("events", [])
print("\n=== TIMELINE ===")
for ev in tl:
    print(f"  [{ev.get('sequence','?')}] {ev.get('event_type', ev.get('type','?')):35s} date={str(ev.get('event_date', ev.get('date','N/A'))):12s}  validity={ev.get('temporal_validity', ev.get('valid','?'))}")
