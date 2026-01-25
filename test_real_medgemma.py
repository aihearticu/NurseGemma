#!/usr/bin/env python3
"""
NurseGemma Comprehensive Test with REAL MedGemma Responses
Tests all features with the actual MedGemma 1.5 4B model
"""

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from datetime import datetime
import time
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL_ID = "google/medgemma-1.5-4b-it"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.bfloat16 if DEVICE == "cuda" else torch.float32

print("=" * 70)
print("NURSEGEMMA COMPREHENSIVE TEST - REAL MEDGEMMA RESPONSES")
print("=" * 70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Device: {DEVICE}")
print(f"Dtype: {DTYPE}")
print(f"Model: {MODEL_ID}")
print("=" * 70)

# =============================================================================
# LOAD MODEL
# =============================================================================

print("\n[1/9] Loading MedGemma 1.5 4B model...")
start_load = time.time()

try:
    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
    print(f"  - Processor loaded")

    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        device_map="auto" if DEVICE == "cuda" else None,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )

    if DEVICE == "cpu":
        model = model.to(DEVICE)

    load_time = time.time() - start_load
    print(f"  - Model loaded in {load_time:.1f} seconds")
    print(f"  - Model device: {next(model.parameters()).device}")
    MODEL_LOADED = True
except Exception as e:
    print(f"  - ERROR loading model: {e}")
    MODEL_LOADED = False

if not MODEL_LOADED:
    print("\nCannot proceed without model. Exiting.")
    exit(1)

# =============================================================================
# CORE INFERENCE FUNCTION
# =============================================================================

def ask_medgemma(system_prompt: str, user_query: str, max_tokens: int = 500) -> str:
    """Query MedGemma with system and user prompts"""
    messages = [
        {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
        {"role": "user", "content": [{"type": "text", "text": user_query}]},
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        output = output[0][input_len:]

    return processor.decode(output, skip_special_tokens=True)

# =============================================================================
# HIGH-ALERT MEDICATIONS
# =============================================================================

HIGH_ALERT_MEDS = [
    "heparin", "warfarin", "enoxaparin", "rivaroxaban", "apixaban",
    "insulin", "lispro", "aspart", "glargine", "NPH",
    "morphine", "hydromorphone", "fentanyl", "oxycodone", "methadone",
    "potassium chloride", "magnesium sulfate", "sodium chloride 3%",
    "epinephrine", "norepinephrine", "vasopressin", "dopamine", "dobutamine",
    "propofol", "midazolam", "ketamine", "digoxin", "amiodarone",
]

def is_high_alert(med_name: str) -> bool:
    return any(ha in med_name.lower() for ha in HIGH_ALERT_MEDS)

# =============================================================================
# TEST RESULTS STORAGE
# =============================================================================

test_results = {
    "timestamp": datetime.now().isoformat(),
    "model": MODEL_ID,
    "device": DEVICE,
    "tests": []
}

def record_test(name, category, input_data, output, duration):
    """Record test result"""
    test_results["tests"].append({
        "name": name,
        "category": category,
        "input": input_data,
        "output": output,
        "duration_seconds": duration,
        "output_length": len(output),
        "passed": len(output) > 50  # Basic validation
    })

# =============================================================================
# TEST 1: QUICK EXPLAIN (Family Explainer)
# =============================================================================

print("\n" + "=" * 70)
print("[2/9] TEST: QUICK EXPLAIN MODULE")
print("=" * 70)

EXPLAINER_SYSTEM = """You are a compassionate nursing communication assistant.

Your explanations should:
- Use plain language (8th grade reading level)
- Be warm and reassuring (when appropriate)
- Use analogies to everyday things
- Acknowledge emotions
- Be honest about serious conditions
- Suggest questions for the doctor
- NEVER give false reassurance

Format:
1. Simple explanation
2. Why this is happening
3. What to expect
4. Questions to ask the doctor"""

explain_tests = [
    ("Atrial Fibrillation", "diagnosis", "Newly diagnosed, patient anxious"),
    ("Pneumothorax", "scan_finding", "Found on chest X-ray, chest tube being placed"),
    ("Troponin elevation", "test_result", "Came to ER with chest pain"),
]

for topic, topic_type, context in explain_tests:
    print(f"\n--- Explaining: {topic} ({topic_type}) ---")
    query = f"""Explain this {topic_type}: {topic}

Audience: a worried family member
Context: {context}

Provide:
1. **In simple terms:** What this means
2. **Think of it like:** An everyday analogy
3. **What to expect:** Next steps and timeline
4. **Questions to ask:** 3-4 good questions for the doctor"""

    start = time.time()
    result = ask_medgemma(EXPLAINER_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"Explain_{topic}", "Quick Explain",
                {"topic": topic, "type": topic_type, "context": context},
                result, duration)

# =============================================================================
# TEST 2: MED HELPER MODULE
# =============================================================================

print("\n" + "=" * 70)
print("[3/9] TEST: MED HELPER MODULE")
print("=" * 70)

MED_SYSTEM = """You are a medication information assistant for bedside nurses.

Focus on PRACTICAL nursing information:
- What it's for (simple terms)
- What to check BEFORE giving
- What to MONITOR after
- Side effects patients notice
- Key interactions
- Patient teaching points

Keep it concise - nurses need quick answers, not textbook chapters.

For HIGH-ALERT medications, always include:
⚠️ HIGH-ALERT warning
- Required double-checks
- Critical monitoring parameters
- Signs of toxicity/overdose"""

med_tests = [
    ("Heparin drip", True),
    ("Metoprolol 25mg PO", False),
    ("Insulin Lispro (Humalog)", True),
    ("Vancomycin 1g IV", False),
]

for med, is_high in med_tests:
    print(f"\n--- Medication: {med} {'(HIGH-ALERT)' if is_high else ''} ---")

    query = f"""Medication: {med}
{'⚠️ HIGH-ALERT MEDICATION - include safety checks' if is_high else ''}

Provide:
1. **What it's for:** (plain language)
2. **Before giving:** What to check
3. **How to give:** Route, timing, special instructions
4. **Monitor for:** Key things to watch
5. **Side effects:** What patient might notice
6. **Tell patient:** Teaching points
{'7. **⚠️ Safety:** Double-check requirements, toxicity signs' if is_high else ''}"""

    start = time.time()
    result = ask_medgemma(MED_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"Med_{med.split()[0]}", "Med Helper",
                {"medication": med, "high_alert": is_high},
                result, duration)

# =============================================================================
# TEST 3: SHIFT SIDEKICK (SBAR HANDOFF)
# =============================================================================

print("\n" + "=" * 70)
print("[4/9] TEST: SHIFT SIDEKICK (SBAR HANDOFF)")
print("=" * 70)

HANDOFF_SYSTEM = """You are a nursing handoff assistant. Generate clear, organized shift reports.

Your handoffs should:
- Be concise but complete
- Highlight CRITICAL items prominently with ⚠️
- Include pending tasks as checkboxes □
- Note changes from previous shift
- Flag concerning trends
- Use nursing-appropriate language"""

sbar_test = """72 y/o male, Room 412, Dr. Smith
Admitted 3 days ago for community-acquired pneumonia
PMH: HTN, DM2, COPD, former smoker (30 pack-years)
Allergies: PCN (rash), Sulfa (hives)

Current:
- Day 3 of Ceftriaxone 1g IV q24h and Azithromycin 500mg IV daily
- 2L NC, sats 94% at rest, drops to 89% with ambulation
- Vitals stable: T 99.2, HR 88, BP 138/82, RR 20

This shift:
- WBC improved 14.6 → 11.2
- Eating 50% of meals
- PT/OT eval still pending
- Wife asking about discharge timeline
- Blood cultures pending final (prelim negative)
- PIV right forearm, good, flushes well"""

print("\n--- SBAR Handoff Generation ---")

query = f"""Generate an SBAR handoff:

**SITUATION**
- Patient ID, room, attending
- Why they're here
- Current status in one sentence

**BACKGROUND**
- Relevant PMH
- Current treatment plan
- Key events this admission

**ASSESSMENT**
- Current nursing assessment
- Trends (improving/stable/declining)
- Concerns

**RECOMMENDATION**
- Priority tasks for next shift
- Pending orders/results
- When to notify MD

End with:
⚠️ CRITICAL ALERTS: [any urgent items]
□ PENDING TASKS: [checklist]

Patient Information:
{sbar_test}"""

start = time.time()
result = ask_medgemma(HANDOFF_SYSTEM, query, max_tokens=800)
duration = time.time() - start

print(f"\nRESPONSE ({duration:.1f}s):")
print("-" * 50)
print(result)
print("-" * 50)

record_test("SBAR_Handoff", "Shift Sidekick", {"patient_info": sbar_test}, result, duration)

# =============================================================================
# TEST 4: CLINICAL QUICK REF (LAB INTERPRETATION)
# =============================================================================

print("\n" + "=" * 70)
print("[5/9] TEST: CLINICAL QUICK REF (LAB INTERPRETATION)")
print("=" * 70)

CLINICAL_SYSTEM = """You are a clinical reference assistant for bedside nurses.

Provide:
- Accurate clinical information
- Context for when values are concerning
- Practical nursing actions
- When to escalate to the provider

Be concise and bedside-friendly."""

lab_tests = [
    ("Potassium", "3.1", "mEq/L", "Patient on Lasix, has history of arrhythmias"),
    ("Troponin", "0.15", "ng/mL", "Came to ER with chest pain, first troponin"),
    ("INR", "4.8", "ratio", "On warfarin for AFib, target 2-3"),
    ("Hemoglobin", "7.2", "g/dL", "GI bleed, getting blood transfusion"),
]

for lab, value, unit, context in lab_tests:
    print(f"\n--- Lab: {lab} = {value} {unit} ---")

    query = f"""Interpret this lab result for a bedside nurse:

Lab: {lab}
Value: {value} {unit}
Patient context: {context}

Provide:
1. **Normal range:** What's normal
2. **Interpretation:** What this value means
3. **Clinical significance:** Why it matters for this patient
4. **Nursing actions:** What to do/monitor
5. **When to call MD:** Specific triggers for escalation"""

    start = time.time()
    result = ask_medgemma(CLINICAL_SYSTEM, query, max_tokens=500)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"Lab_{lab}", "Clinical Quick Ref",
                {"lab": lab, "value": value, "unit": unit, "context": context},
                result, duration)

# =============================================================================
# TEST 5: ABG INTERPRETATION
# =============================================================================

print("\n" + "=" * 70)
print("[6/9] TEST: ABG INTERPRETATION")
print("=" * 70)

ABG_SYSTEM = """You are an ABG interpretation assistant for nurses.

Use the systematic approach:
1. Look at pH (acidotic/alkalotic/normal)
2. Look at pCO2 (respiratory component)
3. Look at HCO3 (metabolic component)
4. Determine primary disorder
5. Check for compensation
6. Assess oxygenation

Provide practical nursing implications."""

abg_tests = [
    ("pH 7.28, pCO2 58, HCO3 26, PaO2 62", "COPD patient, increasing SOB"),
    ("pH 7.52, pCO2 28, HCO3 22, PaO2 98", "Anxious patient, hyperventilating"),
    ("pH 7.18, pCO2 22, HCO3 8, PaO2 95", "DKA patient, Kussmaul breathing"),
]

for abg, context in abg_tests:
    print(f"\n--- ABG: {abg} ---")

    query = f"""Interpret this ABG for a bedside nurse:

ABG Values: {abg}
Clinical context: {context}

Provide:
1. **Step-by-step interpretation:** Walk through the analysis
2. **Primary disorder:** What's the main problem
3. **Compensation:** Is the body compensating?
4. **Oxygenation status:** How is the patient oxygenating?
5. **Nursing implications:** What to monitor and do"""

    start = time.time()
    result = ask_medgemma(ABG_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"ABG_{abg[:10]}", "ABG Interpretation",
                {"abg": abg, "context": context},
                result, duration)

# =============================================================================
# TEST 6: WHAT TO WATCH (CONDITION MONITORING)
# =============================================================================

print("\n" + "=" * 70)
print("[7/9] TEST: WHAT TO WATCH (CONDITION MONITORING)")
print("=" * 70)

WATCH_SYSTEM = """You are a clinical monitoring guide for nurses.

Help nurses know what to watch for with specific conditions.
Focus on:
- Assessment priorities
- Warning signs of deterioration
- When to escalate
- Key interventions"""

conditions = [
    "New onset atrial fibrillation with RVR",
    "Post-tPA for acute ischemic stroke",
    "Acute GI bleed with melena",
]

for condition in conditions:
    print(f"\n--- Condition: {condition} ---")

    query = f"""What should a bedside nurse watch for with: {condition}

Provide:
1. **Assessment priorities:** What to check frequently
2. **Warning signs:** Red flags for deterioration
3. **Vital sign parameters:** Specific numbers to watch
4. **When to call rapid response:** Clear triggers
5. **Key nursing interventions:** What to do proactively"""

    start = time.time()
    result = ask_medgemma(WATCH_SYSTEM, query, max_tokens=500)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"Watch_{condition[:20]}", "What to Watch",
                {"condition": condition},
                result, duration)

# =============================================================================
# TEST 7: DRUG INTERACTION CHECK
# =============================================================================

print("\n" + "=" * 70)
print("[8/9] TEST: DRUG INTERACTION CHECK")
print("=" * 70)

INTERACTION_SYSTEM = """You are a drug interaction checker for nurses.

Identify potential interactions and provide:
- Severity (major/moderate/minor)
- Clinical significance
- What to monitor
- Whether to hold and call pharmacy/MD"""

interactions = [
    ["Warfarin", "Aspirin", "Ibuprofen"],
    ["Metformin", "IV Contrast"],
    ["Digoxin", "Amiodarone", "Furosemide"],
]

for meds in interactions:
    print(f"\n--- Checking: {' + '.join(meds)} ---")

    query = f"""Check for drug interactions between: {', '.join(meds)}

For each interaction found:
1. **Interaction:** Which drugs interact
2. **Severity:** Major/Moderate/Minor
3. **Mechanism:** Why they interact
4. **Clinical effect:** What could happen
5. **Nursing action:** What to do"""

    start = time.time()
    result = ask_medgemma(INTERACTION_SYSTEM, query, max_tokens=500)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"Interaction_{meds[0]}", "Drug Interactions",
                {"medications": meds},
                result, duration)

# =============================================================================
# TEST 8: PATIENT EDUCATION
# =============================================================================

print("\n" + "=" * 70)
print("[9/9] TEST: PATIENT EDUCATION")
print("=" * 70)

EDUCATION_SYSTEM = """You are a patient education assistant for nurses.

Create teaching materials that:
- Use plain language (8th grade level)
- Are culturally sensitive
- Include practical tips
- Address common questions
- Emphasize safety"""

education_topics = [
    ("New diabetes diagnosis", "Type 2 diabetes, starting metformin"),
    ("Heart failure discharge", "CHF, going home on Lasix and low-sodium diet"),
]

for topic, context in education_topics:
    print(f"\n--- Patient Education: {topic} ---")

    query = f"""Create patient education for: {topic}
Context: {context}

Include:
1. **What you need to know:** Simple explanation of condition
2. **Your medications:** What they do and how to take them
3. **Warning signs:** When to call the doctor or go to ER
4. **Lifestyle tips:** Practical daily management
5. **Common questions:** Answer 3 things patients often ask"""

    start = time.time()
    result = ask_medgemma(EDUCATION_SYSTEM, query, max_tokens=600)
    duration = time.time() - start

    print(f"\nRESPONSE ({duration:.1f}s):")
    print("-" * 50)
    print(result)
    print("-" * 50)

    record_test(f"Education_{topic[:15]}", "Patient Education",
                {"topic": topic, "context": context},
                result, duration)

# =============================================================================
# GENERATE FINAL REPORT
# =============================================================================

print("\n" + "=" * 70)
print("COMPREHENSIVE TEST REPORT")
print("=" * 70)

total_tests = len(test_results["tests"])
passed_tests = sum(1 for t in test_results["tests"] if t["passed"])
total_duration = sum(t["duration_seconds"] for t in test_results["tests"])
avg_duration = total_duration / total_tests if total_tests > 0 else 0

print(f"""
Summary:
  Total Tests: {total_tests}
  Passed: {passed_tests}/{total_tests} ({100*passed_tests/total_tests:.0f}%)
  Total Duration: {total_duration:.1f} seconds
  Average Response Time: {avg_duration:.1f} seconds

Tests by Category:""")

from collections import Counter
categories = Counter(t["category"] for t in test_results["tests"])
for cat, count in categories.most_common():
    cat_passed = sum(1 for t in test_results["tests"] if t["category"] == cat and t["passed"])
    print(f"  - {cat}: {cat_passed}/{count} passed")

print(f"""
Device: {DEVICE}
Model: {MODEL_ID}
Timestamp: {test_results['timestamp']}
""")

# Save results to JSON
output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(test_results, f, indent=2)
print(f"Results saved to: {output_file}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
