#!/usr/bin/env python3
"""
NurseGemma COMPREHENSIVE TEST - REAL MedGemma 1.5 4B Responses
Using Kaggle Hub model download
"""

import os
os.environ['KAGGLE_USERNAME'] = 'aihearticu'
os.environ['KAGGLE_KEY'] = '568f017fb62efc90e39c48848942a80f'
os.environ['KERAS_BACKEND'] = 'torch'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import warnings
warnings.filterwarnings('ignore')

import time
import json
from datetime import datetime

print("=" * 70)
print("NURSEGEMMA COMPREHENSIVE TEST - REAL MEDGEMMA 1.5 RESPONSES")
print("=" * 70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# LOAD MODEL
# =============================================================================
print("\n[LOADING] MedGemma 1.5 4B via Keras Hub...")
start_load = time.time()

import keras_hub
import torch

# Check GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Load model from Kaggle
model = keras_hub.models.Gemma3CausalLM.from_preset(
    'kaggle://keras/medgemma/keras/medgemma_1.5_instruct_4b'
)

load_time = time.time() - start_load
print(f"Model loaded in {load_time:.1f} seconds")

# =============================================================================
# INFERENCE FUNCTION
# =============================================================================

def ask_medgemma(system_prompt: str, user_query: str, max_tokens: int = 512) -> str:
    """Query MedGemma with formatted prompt"""
    # Format for Gemma 3 chat template
    prompt = f"""<start_of_turn>user
{system_prompt}

{user_query}<end_of_turn>
<start_of_turn>model
"""

    response = model.generate(prompt, max_length=max_tokens + len(prompt.split()))

    # Extract just the model response
    if "<start_of_turn>model" in response:
        response = response.split("<start_of_turn>model")[-1]
    if "<end_of_turn>" in response:
        response = response.split("<end_of_turn>")[0]

    return response.strip()

# =============================================================================
# TEST RESULTS STORAGE
# =============================================================================

test_results = {
    "timestamp": datetime.now().isoformat(),
    "model": "keras/medgemma/medgemma_1.5_instruct_4b",
    "device": device,
    "load_time_seconds": load_time,
    "tests": []
}

def record_test(name, category, input_data, output, duration):
    test_results["tests"].append({
        "name": name,
        "category": category,
        "input": str(input_data)[:500],
        "output": output,
        "duration_seconds": round(duration, 2),
        "output_length": len(output),
        "passed": len(output) > 50
    })
    return output

# =============================================================================
# TEST 1: QUICK EXPLAIN (Family Explainer)
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 1/7] QUICK EXPLAIN MODULE - Family Explainer")
print("=" * 70)

EXPLAINER_SYSTEM = """You are a compassionate nursing communication assistant. Explain medical terms to worried family members using plain language (8th grade level). Use analogies, be reassuring when appropriate, and suggest questions for the doctor."""

explain_tests = [
    ("Atrial Fibrillation", "newly diagnosed, patient anxious about the term"),
    ("Pneumonia", "elderly parent admitted, family wants to understand"),
    ("Type 2 Diabetes", "new diagnosis, patient overwhelmed"),
]

for topic, context in explain_tests:
    print(f"\n--- Explaining: {topic} ---")
    query = f"""Explain {topic} to a worried family member.
Context: {context}

Provide:
1. Simple explanation (what this means)
2. An everyday analogy
3. What to expect next
4. 2-3 questions to ask the doctor"""

    start = time.time()
    result = ask_medgemma(EXPLAINER_SYSTEM, query)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result[:1500] if len(result) > 1500 else result)
    print("-" * 50)

    record_test(f"Explain_{topic.replace(' ', '_')}", "Quick Explain",
                {"topic": topic, "context": context}, result, duration)

# =============================================================================
# TEST 2: MED HELPER MODULE
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 2/7] MED HELPER MODULE - Medication Information")
print("=" * 70)

MED_SYSTEM = """You are a medication information assistant for bedside nurses. Focus on practical nursing information: what to check before giving, what to monitor after, side effects, and patient teaching points. For HIGH-ALERT medications, include required double-checks and toxicity signs."""

HIGH_ALERT_MEDS = ["heparin", "insulin", "warfarin", "morphine", "potassium chloride"]

med_tests = [
    ("Heparin drip 25,000 units/500mL NS", True),
    ("Metoprolol 25mg PO BID", False),
    ("Furosemide (Lasix) 40mg IV push", False),
]

for med, is_high_alert in med_tests:
    print(f"\n--- Medication: {med} {'⚠️ HIGH-ALERT' if is_high_alert else ''} ---")

    query = f"""Medication: {med}
{'⚠️ This is a HIGH-ALERT medication - include safety requirements' if is_high_alert else ''}

Provide nursing-focused information:
1. What it's for (simple terms)
2. What to check BEFORE giving
3. What to MONITOR after
4. Common side effects
5. Patient teaching points
{'6. Required double-checks and signs of toxicity' if is_high_alert else ''}"""

    start = time.time()
    result = ask_medgemma(MED_SYSTEM, query)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result[:1500] if len(result) > 1500 else result)
    print("-" * 50)

    record_test(f"Med_{med.split()[0]}", "Med Helper",
                {"medication": med, "high_alert": is_high_alert}, result, duration)

# =============================================================================
# TEST 3: SHIFT SIDEKICK - SBAR HANDOFF
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 3/7] SHIFT SIDEKICK - SBAR Handoff Generation")
print("=" * 70)

HANDOFF_SYSTEM = """You are a nursing handoff assistant. Generate clear, organized SBAR shift reports. Highlight critical items with ⚠️, include pending tasks as checkboxes □, note concerning trends, and use nursing-appropriate language."""

sbar_patient = """72 y/o male, Room 412, Dr. Smith
Admitted 3 days ago for community-acquired pneumonia
PMH: HTN, DM2, COPD, former smoker
Allergies: PCN (rash), Sulfa (hives)

Current status:
- Day 3 of Ceftriaxone/Azithromycin
- 2L NC, sats 94% rest, 89% with activity
- Vitals: T 99.2, HR 88, BP 138/82, RR 20
- WBC improved 14.6 → 11.2
- Eating 50% of meals
- PT/OT eval pending
- Wife asking about discharge
- Blood cultures: prelim negative, final pending
- PIV RFA: patent, good"""

print("\n--- SBAR Handoff Generation ---")
query = f"""Generate a complete SBAR handoff report for this patient:

{sbar_patient}

Format as:
SITUATION: (who, what, current status)
BACKGROUND: (PMH, treatment, key events)
ASSESSMENT: (nursing assessment, trends, concerns)
RECOMMENDATION: (tasks, pending items, when to call MD)

End with:
⚠️ CRITICAL ALERTS
□ PENDING TASKS"""

start = time.time()
result = ask_medgemma(HANDOFF_SYSTEM, query)
duration = time.time() - start

print(f"\nRESPONSE ({duration:.1f}s):")
print("-" * 50)
print(result)
print("-" * 50)

record_test("SBAR_Handoff", "Shift Sidekick", {"patient": sbar_patient[:200]}, result, duration)

# =============================================================================
# TEST 4: CLINICAL QUICK REF - Lab Interpretation
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 4/7] CLINICAL QUICK REF - Lab Interpretation")
print("=" * 70)

CLINICAL_SYSTEM = """You are a clinical reference assistant for bedside nurses. Provide accurate lab interpretation with normal ranges, clinical significance, nursing actions, and when to escalate to the provider."""

lab_tests = [
    ("Potassium", "3.1 mEq/L", "Patient on Lasix 40mg daily, history of arrhythmias"),
    ("Troponin I", "0.15 ng/mL", "Chest pain patient, first troponin of admission"),
    ("Hemoglobin", "7.2 g/dL", "GI bleed patient, melena x2 days"),
]

for lab, value, context in lab_tests:
    print(f"\n--- Lab: {lab} = {value} ---")

    query = f"""Interpret this lab for a bedside nurse:

Lab: {lab}
Value: {value}
Context: {context}

Provide:
1. Normal range
2. Is this critical/abnormal/normal?
3. Clinical significance for this patient
4. Nursing actions to take
5. When to notify the MD"""

    start = time.time()
    result = ask_medgemma(CLINICAL_SYSTEM, query)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result[:1500] if len(result) > 1500 else result)
    print("-" * 50)

    record_test(f"Lab_{lab}", "Clinical Quick Ref",
                {"lab": lab, "value": value, "context": context}, result, duration)

# =============================================================================
# TEST 5: ABG INTERPRETATION
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 5/7] ABG INTERPRETATION")
print("=" * 70)

ABG_SYSTEM = """You are an ABG interpretation assistant. Use systematic analysis: check pH, pCO2, HCO3, determine primary disorder, check compensation, assess oxygenation. Provide practical nursing implications."""

abg_test = "pH 7.28, pCO2 58, HCO3 26, PaO2 62, SaO2 89%"
abg_context = "COPD patient with increasing shortness of breath over 2 days"

print(f"\n--- ABG: {abg_test} ---")
query = f"""Interpret this ABG:

Values: {abg_test}
Context: {abg_context}

Provide:
1. Step-by-step analysis (pH, pCO2, HCO3)
2. Primary acid-base disorder
3. Compensation status
4. Oxygenation assessment
5. Nursing implications and actions"""

start = time.time()
result = ask_medgemma(ABG_SYSTEM, query)
duration = time.time() - start

print(f"\nRESPONSE ({duration:.1f}s):")
print("-" * 50)
print(result)
print("-" * 50)

record_test("ABG_Interpretation", "ABG", {"abg": abg_test, "context": abg_context}, result, duration)

# =============================================================================
# TEST 6: WHAT TO WATCH - Condition Monitoring
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 6/7] WHAT TO WATCH - Condition Monitoring")
print("=" * 70)

WATCH_SYSTEM = """You are a clinical monitoring guide for nurses. Provide assessment priorities, warning signs of deterioration, vital sign parameters to watch, and when to escalate."""

conditions = [
    "New onset atrial fibrillation with rapid ventricular response",
    "Post-tPA administration for acute ischemic stroke",
]

for condition in conditions:
    print(f"\n--- Condition: {condition} ---")

    query = f"""What should a bedside nurse watch for with: {condition}

Provide:
1. Assessment priorities (what to check frequently)
2. Warning signs of deterioration
3. Specific vital sign parameters
4. When to call rapid response or MD
5. Key nursing interventions"""

    start = time.time()
    result = ask_medgemma(WATCH_SYSTEM, query)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result[:1500] if len(result) > 1500 else result)
    print("-" * 50)

    record_test(f"Watch_{condition[:20]}", "What to Watch", {"condition": condition}, result, duration)

# =============================================================================
# TEST 7: DRUG INTERACTIONS
# =============================================================================

print("\n" + "=" * 70)
print("[TEST 7/7] DRUG INTERACTION CHECK")
print("=" * 70)

INTERACTION_SYSTEM = """You are a drug interaction checker for nurses. Identify interactions, severity levels (major/moderate/minor), clinical effects, and nursing actions."""

meds_to_check = ["Warfarin", "Aspirin 81mg", "Ibuprofen 400mg"]

print(f"\n--- Checking: {' + '.join(meds_to_check)} ---")
query = f"""Check for drug interactions between: {', '.join(meds_to_check)}

For each interaction:
1. Which drugs interact
2. Severity (Major/Moderate/Minor)
3. Why they interact (mechanism)
4. What could happen clinically
5. What the nurse should do"""

start = time.time()
result = ask_medgemma(INTERACTION_SYSTEM, query)
duration = time.time() - start

print(f"\nRESPONSE ({duration:.1f}s):")
print("-" * 50)
print(result)
print("-" * 50)

record_test("Drug_Interactions", "Interactions", {"medications": meds_to_check}, result, duration)

# =============================================================================
# GENERATE FINAL REPORT
# =============================================================================

print("\n" + "=" * 70)
print("COMPREHENSIVE TEST REPORT - REAL MEDGEMMA RESPONSES")
print("=" * 70)

total_tests = len(test_results["tests"])
passed_tests = sum(1 for t in test_results["tests"] if t["passed"])
total_duration = sum(t["duration_seconds"] for t in test_results["tests"])
avg_duration = total_duration / total_tests if total_tests > 0 else 0
total_output = sum(t["output_length"] for t in test_results["tests"])

print(f"""
SUMMARY:
========
  Total Tests: {total_tests}
  Passed: {passed_tests}/{total_tests} ({100*passed_tests/total_tests:.0f}%)
  Total Response Time: {total_duration:.1f} seconds
  Average Response Time: {avg_duration:.1f} seconds/query
  Total Output Generated: {total_output:,} characters
  Model Load Time: {load_time:.1f} seconds

TESTS BY CATEGORY:
==================""")

from collections import Counter
categories = Counter(t["category"] for t in test_results["tests"])
for cat, count in categories.most_common():
    cat_tests = [t for t in test_results["tests"] if t["category"] == cat]
    cat_passed = sum(1 for t in cat_tests if t["passed"])
    cat_time = sum(t["duration_seconds"] for t in cat_tests)
    print(f"  {cat}: {cat_passed}/{count} passed, {cat_time:.1f}s total")

print(f"""
SYSTEM INFO:
============
  Device: {device}
  Model: {test_results['model']}
  Timestamp: {test_results['timestamp']}
""")

# Save results
output_file = f"real_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(test_results, f, indent=2)
print(f"Results saved to: {output_file}")

print("\n" + "=" * 70)
print("ALL COMPREHENSIVE TESTS COMPLETE - REAL MEDGEMMA RESPONSES")
print("=" * 70)
