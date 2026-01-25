# =============================================================================
# COMPREHENSIVE NURSEGEMMA TEST - REAL MEDGEMMA RESPONSES
# Copy this cell into your Kaggle notebook and run with GPU enabled
# =============================================================================
# Prerequisites:
# 1. GPU accelerator enabled (T4 x2 recommended)
# 2. MedGemma model loaded (run setup cells first)
# 3. ask_medgemma() function defined
# =============================================================================

import time
from datetime import datetime
import json

print("=" * 70)
print("NURSEGEMMA COMPREHENSIVE TEST - REAL MEDGEMMA 1.5 RESPONSES")
print("=" * 70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# TEST RESULTS STORAGE
# =============================================================================

test_results = {
    "timestamp": datetime.now().isoformat(),
    "model": "MedGemma 1.5 4B",
    "tests": []
}

def record_test(name, category, query, output, duration):
    test_results["tests"].append({
        "name": name,
        "category": category,
        "query": query[:300],
        "output": output,
        "duration": round(duration, 2),
        "chars": len(output),
        "passed": len(output) > 50
    })
    print(f"✓ {name}: {duration:.1f}s, {len(output)} chars")

# =============================================================================
# TEST 1: QUICK EXPLAIN (Family Explainer)
# =============================================================================

print("\n" + "=" * 70)
print("[1/8] QUICK EXPLAIN MODULE")
print("=" * 70)

EXPLAIN_SYSTEM = """You are a compassionate nursing communication assistant.
Explain medical terms to worried family members using plain language (8th grade level).
Use analogies, be reassuring when appropriate, and suggest questions for the doctor."""

explain_tests = [
    ("Atrial Fibrillation", "newly diagnosed, patient anxious"),
    ("Pneumonia", "elderly parent admitted"),
    ("COPD Exacerbation", "family asking what this means"),
]

for topic, context in explain_tests:
    query = f"""Explain {topic} to a worried family member.
Context: {context}
Include: simple explanation, everyday analogy, what to expect, questions for doctor."""

    start = time.time()
    result = ask_medgemma(EXPLAIN_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\n--- {topic} ---")
    print(result[:600] + "..." if len(result) > 600 else result)
    record_test(f"Explain_{topic}", "Quick Explain", query, result, duration)

# =============================================================================
# TEST 2: MED HELPER (High-Alert Focus)
# =============================================================================

print("\n" + "=" * 70)
print("[2/8] MED HELPER MODULE")
print("=" * 70)

MED_SYSTEM = """You are a medication information assistant for bedside nurses.
Focus on practical nursing info: what to check before giving, what to monitor,
side effects, patient teaching. For HIGH-ALERT meds, include safety checks."""

med_tests = [
    ("Heparin drip 25,000u/500mL", True),
    ("Insulin Lispro per sliding scale", True),
    ("Metoprolol 25mg PO BID", False),
    ("Vancomycin 1g IV", False),
]

for med, high_alert in med_tests:
    ha_tag = "⚠️ HIGH-ALERT - " if high_alert else ""
    query = f"""{ha_tag}Medication: {med}
Provide: what it's for, pre-administration checks, monitoring parameters,
side effects, patient teaching{', required double-checks, toxicity signs' if high_alert else ''}."""

    start = time.time()
    result = ask_medgemma(MED_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\n--- {med} {'⚠️' if high_alert else ''} ---")
    print(result[:500] + "..." if len(result) > 500 else result)
    record_test(f"Med_{med.split()[0]}", "Med Helper", query, result, duration)

# =============================================================================
# TEST 3: SHIFT SIDEKICK (SBAR)
# =============================================================================

print("\n" + "=" * 70)
print("[3/8] SHIFT SIDEKICK - SBAR HANDOFF")
print("=" * 70)

HANDOFF_SYSTEM = """You are a nursing handoff assistant. Generate clear SBAR reports.
Highlight critical items with ⚠️, include pending tasks as □ checkboxes."""

patient_info = """72 y/o male, Room 412, Dr. Smith
Admitted 3 days ago: Community-acquired pneumonia
PMH: HTN, DM2, COPD, former smoker (30 pack-years)
Allergies: PCN (rash), Sulfa (hives)

Current:
- Day 3 Ceftriaxone/Azithromycin
- 2L NC, sats 94% rest, 89% activity
- T 99.2, HR 88, BP 138/82, RR 20
- WBC 14.6→11.2 (improving)
- Eating 50%, PT/OT pending
- Blood cultures: prelim negative
- Wife asking about discharge"""

query = f"""Generate SBAR handoff:
{patient_info}

Format: SITUATION, BACKGROUND, ASSESSMENT, RECOMMENDATION
End with ⚠️ CRITICAL ALERTS and □ PENDING TASKS"""

start = time.time()
result = ask_medgemma(HANDOFF_SYSTEM, query, max_tokens=800)
duration = time.time() - start

print(result)
record_test("SBAR_Handoff", "Shift Sidekick", query, result, duration)

# =============================================================================
# TEST 4: CLINICAL QUICK REF (Labs)
# =============================================================================

print("\n" + "=" * 70)
print("[4/8] CLINICAL QUICK REF - LAB INTERPRETATION")
print("=" * 70)

LAB_SYSTEM = """You are a clinical reference for nurses. Provide lab interpretation
with normal ranges, clinical significance, nursing actions, escalation criteria."""

lab_tests = [
    ("Potassium", "3.1 mEq/L", "On Lasix, history of arrhythmias"),
    ("Troponin I", "0.15 ng/mL", "Chest pain, first troponin"),
    ("INR", "4.8", "On warfarin for AFib, target 2-3"),
    ("Hemoglobin", "7.2 g/dL", "GI bleed with melena"),
]

for lab, value, context in lab_tests:
    query = f"""Lab: {lab} = {value}
Context: {context}
Provide: normal range, interpretation, clinical significance, nursing actions, when to notify MD."""

    start = time.time()
    result = ask_medgemma(LAB_SYSTEM, query, max_tokens=500)
    duration = time.time() - start

    print(f"\n--- {lab}: {value} ---")
    print(result[:400] + "..." if len(result) > 400 else result)
    record_test(f"Lab_{lab}", "Clinical Ref", query, result, duration)

# =============================================================================
# TEST 5: ABG INTERPRETATION
# =============================================================================

print("\n" + "=" * 70)
print("[5/8] ABG INTERPRETATION")
print("=" * 70)

ABG_SYSTEM = """You are an ABG interpretation assistant. Use systematic analysis:
pH, pCO2, HCO3, primary disorder, compensation, oxygenation. Nursing implications."""

abg_tests = [
    ("pH 7.28, pCO2 58, HCO3 26, PaO2 62", "COPD exacerbation, increasing SOB"),
    ("pH 7.52, pCO2 28, HCO3 22, PaO2 98", "Anxious patient hyperventilating"),
    ("pH 7.18, pCO2 22, HCO3 8, PaO2 95", "DKA, Kussmaul breathing"),
]

for abg, context in abg_tests:
    query = f"""ABG: {abg}
Context: {context}
Provide: step-by-step analysis, primary disorder, compensation, oxygenation, nursing actions."""

    start = time.time()
    result = ask_medgemma(ABG_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\n--- {abg[:30]}... ---")
    print(result[:500] + "..." if len(result) > 500 else result)
    record_test(f"ABG_{context[:15]}", "ABG", query, result, duration)

# =============================================================================
# TEST 6: WHAT TO WATCH
# =============================================================================

print("\n" + "=" * 70)
print("[6/8] WHAT TO WATCH - CONDITION MONITORING")
print("=" * 70)

WATCH_SYSTEM = """You are a clinical monitoring guide. Provide assessment priorities,
warning signs, vital parameters, escalation criteria, nursing interventions."""

conditions = [
    "New onset atrial fibrillation with RVR",
    "Post-tPA for acute ischemic stroke",
    "Acute GI bleed with melena",
    "DKA on insulin drip",
]

for condition in conditions:
    query = f"""What should a nurse watch for: {condition}
Include: assessment priorities, warning signs, vital parameters, when to escalate, interventions."""

    start = time.time()
    result = ask_medgemma(WATCH_SYSTEM, query, max_tokens=500)
    duration = time.time() - start

    print(f"\n--- {condition} ---")
    print(result[:400] + "..." if len(result) > 400 else result)
    record_test(f"Watch_{condition[:20]}", "What to Watch", query, result, duration)

# =============================================================================
# TEST 7: DRUG INTERACTIONS
# =============================================================================

print("\n" + "=" * 70)
print("[7/8] DRUG INTERACTION CHECK")
print("=" * 70)

INTERACTION_SYSTEM = """You are a drug interaction checker. Identify interactions,
severity (Major/Moderate/Minor), mechanism, clinical effects, nursing actions."""

interaction_checks = [
    ["Warfarin", "Aspirin", "Ibuprofen"],
    ["Metformin", "IV Contrast"],
    ["Digoxin", "Amiodarone", "Furosemide"],
]

for meds in interaction_checks:
    query = f"""Check interactions between: {', '.join(meds)}
For each: severity, mechanism, clinical effect, nursing action."""

    start = time.time()
    result = ask_medgemma(INTERACTION_SYSTEM, query, max_tokens=500)
    duration = time.time() - start

    print(f"\n--- {' + '.join(meds)} ---")
    print(result[:400] + "..." if len(result) > 400 else result)
    record_test(f"Interaction_{meds[0]}", "Drug Interactions", query, result, duration)

# =============================================================================
# TEST 8: PATIENT EDUCATION
# =============================================================================

print("\n" + "=" * 70)
print("[8/8] PATIENT EDUCATION")
print("=" * 70)

EDUCATION_SYSTEM = """You are a patient education assistant. Create teaching materials
in plain language (8th grade), culturally sensitive, with practical tips."""

education_topics = [
    ("New Type 2 Diabetes", "Starting metformin, lifestyle changes"),
    ("Heart Failure Discharge", "Low-sodium diet, daily weights, medications"),
]

for topic, context in education_topics:
    query = f"""Create patient education for: {topic}
Context: {context}
Include: simple explanation, medications, warning signs, lifestyle tips, when to call doctor."""

    start = time.time()
    result = ask_medgemma(EDUCATION_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\n--- {topic} ---")
    print(result[:500] + "..." if len(result) > 500 else result)
    record_test(f"Education_{topic[:15]}", "Patient Education", query, result, duration)

# =============================================================================
# FINAL REPORT
# =============================================================================

print("\n" + "=" * 70)
print("COMPREHENSIVE TEST REPORT - REAL MEDGEMMA RESPONSES")
print("=" * 70)

total = len(test_results["tests"])
passed = sum(1 for t in test_results["tests"] if t["passed"])
total_time = sum(t["duration"] for t in test_results["tests"])
total_chars = sum(t["chars"] for t in test_results["tests"])

print(f"""
SUMMARY
=======
Total Tests: {total}
Passed: {passed}/{total} ({100*passed/total:.0f}%)
Total Time: {total_time:.1f} seconds
Avg Response: {total_time/total:.1f}s per query
Total Output: {total_chars:,} characters

BY CATEGORY
===========""")

from collections import Counter
cats = Counter(t["category"] for t in test_results["tests"])
for cat, count in cats.most_common():
    cat_tests = [t for t in test_results["tests"] if t["category"] == cat]
    cat_time = sum(t["duration"] for t in cat_tests)
    cat_passed = sum(1 for t in cat_tests if t["passed"])
    print(f"  {cat}: {cat_passed}/{count} passed, {cat_time:.1f}s")

print(f"""
All tests used REAL MedGemma 1.5 4B responses.
Timestamp: {test_results['timestamp']}
""")

print("=" * 70)
print("COMPREHENSIVE TEST COMPLETE")
print("=" * 70)
