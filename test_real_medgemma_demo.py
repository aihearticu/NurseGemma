#!/usr/bin/env python3
"""
Real MedGemma Demo - Actual API calls to MedGemma 1.5 4B
This script loads the model and generates real responses for the Mrs. Johnson scenario.
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("=" * 70)
print("NurseGemma - REAL MedGemma Demo")
print("Loading MedGemma 1.5 4B...")
print("=" * 70)

# Check for HuggingFace token (needed for gated model)
HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    print("\n⚠️  No HuggingFace token found.")
    print("MedGemma is a gated model - you need to:")
    print("1. Go to https://huggingface.co/google/medgemma-1.5-4b-it")
    print("2. Accept the terms")
    print("3. Set HF_TOKEN environment variable")
    print("\nExport your token:")
    print("  export HF_TOKEN='your_token_here'")
    print("\nThen run this script again.")
    sys.exit(1)

try:
    import torch
    from transformers import AutoProcessor, AutoModelForImageTextToText

    print(f"\nPyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install torch transformers accelerate")
    sys.exit(1)

# Load model
print("\n" + "=" * 70)
print("Loading MedGemma 1.5 4B (this may take a minute)...")
print("=" * 70)

start_load = time.time()

try:
    processor = AutoProcessor.from_pretrained(
        "google/medgemma-1.5-4b-it",
        token=HF_TOKEN
    )

    model = AutoModelForImageTextToText.from_pretrained(
        "google/medgemma-1.5-4b-it",
        torch_dtype=torch.bfloat16,
        device_map="auto",
        token=HF_TOKEN
    )

    load_time = time.time() - start_load
    print(f"\n✓ Model loaded in {load_time:.1f} seconds")
    print(f"✓ Device: {next(model.parameters()).device}")

except Exception as e:
    print(f"\n❌ Failed to load model: {e}")
    print("\nMake sure you have:")
    print("1. Accepted the model terms on HuggingFace")
    print("2. Set HF_TOKEN correctly")
    print("3. Enough GPU memory (~8GB)")
    sys.exit(1)

# Helper function to generate responses
def generate_response(system_prompt: str, user_message: str, max_tokens: int = 500) -> str:
    """Generate a response from MedGemma"""
    messages = [
        {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
        {"role": "user", "content": [{"type": "text", "text": user_message}]},
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)

    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        generation = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.7,
        )
        generation = generation[0][input_len:]

    return processor.decode(generation, skip_special_tokens=True)

# System prompts
CLINICAL_REF_PROMPT = """You are a clinical reference assistant for nurses.
Your role is to provide quick, accurate clinical information including:
- Normal lab value ranges and interpretation
- Procedure steps and reminders
- Assessment findings and what they indicate
- Clinical pathways and protocols
- Emergency reference information

Guidelines:
- Be accurate and evidence-based
- Provide context for when values are concerning
- Give practical bedside tips
- Always recommend verifying with unit protocols
- Flag emergency situations clearly"""

SHIFT_SIDEKICK_PROMPT = """You are a nursing handoff assistant that helps generate SBAR reports.

SBAR Format:
- Situation: What is happening with the patient right now?
- Background: What is the clinical context/history?
- Assessment: What do you think the problem is?
- Recommendation: What needs to be done?

Guidelines:
- Be concise but thorough
- Highlight critical information prominently
- Include pending tasks and follow-ups
- Note any changes from previous shift
- Flag any concerning trends or findings"""

QUICK_EXPLAIN_PROMPT = """You are a helpful nursing assistant specialized in patient and family communication.
Your role is to explain medical terms, diagnoses, and procedures in simple, easy-to-understand language.

Guidelines:
- Use plain language appropriate for the specified reading level
- Avoid medical jargon unless explaining it
- Use analogies and comparisons to everyday things
- Be compassionate and reassuring while remaining accurate
- Keep explanations concise but complete
- If something is serious, be honest but gentle
- Suggest follow-up questions the patient might want to ask their doctor"""

# Mrs. Johnson's data
MRS_JOHNSON_CONTEXT = """
PATIENT: Mary Johnson (68F)
ROOM: 412-1 | MRN: 12345678
ATTENDING: Dr. Smith, James (Cardiology)
ADMITTED: 01/20/2026

CHIEF COMPLAINT: Shortness of breath x 3 days
DIAGNOSIS: Acute exacerbation of CHF

HISTORY: CHF (EF 35%), Hypertension, Type 2 Diabetes, CKD Stage 3, A-fib on anticoagulation
ALLERGIES: Penicillin (rash), Sulfa (hives)

CURRENT VITALS:
Time      BP         HR    RR   Temp   SpO2
0400      142/88     82    18   99.2   94% 2L NC
0800      138/84     78    18   98.8   95% 2L NC
1200      128/76     72    20   98.6   94% 2L NC
1600      92/58      52    18   98.4   96% 2L NC  <-- CONCERNING

MEDICATIONS:
* METOPROLOL 25mg PO BID - 0800 GIVEN
* LISINOPRIL 10mg PO Daily - 0800 GIVEN
* FUROSEMIDE 40mg IV Q12H - 0600 GIVEN (Monitor K+)
* DIGOXIN 0.125mg PO Daily - HIGH-ALERT (Hold if HR <60)
* HEPARIN 5000 units SC Q8H - HIGH-ALERT
* METFORMIN 500mg PO BID
* POTASSIUM CL 20mEq PO PRN - HIGH-ALERT (For K+ <3.5)

LABS (0600):
Sodium: 138 mEq/L (136-145)
Potassium: 3.2 mEq/L (3.5-5.0) LOW ⚠️
BUN: 28 mg/dL (7-20) HIGH
Creatinine: 1.4 mg/dL (0.6-1.2) HIGH
Glucose: 142 mg/dL (70-100) HIGH
BNP: 892 pg/mL (0-100) HIGH
Digoxin Level: 1.8 ng/mL (0.8-2.0) - high therapeutic

NURSING NOTES:
- 0700: Patient resting comfortably. Received report from night shift.
- 0800: AM meds given. Patient tolerated breakfast 50%.
- 1000: PT/OT evaluated. Ambulated 50 feet with walker, O2 sat dropped to 89%.
- 1200: Lunch tolerated 75%. Patient's daughter asking about diagnosis.
- 1400: Noted BP and HR dropping. Patient denies dizziness.
- 1600: BP 92/58, HR 52. Hold parameters for Metoprolol are HR <60. K+ 3.2 this AM.

PENDING: Echo (tomorrow), Daily weights
CONSULTS: Dietary, Social work for discharge planning
"""

# Run demos
print("\n" + "=" * 70)
print("DEMO 1: Critical Lab Analysis")
print("=" * 70)

lab_prompt = f"""Analyze these lab values for a patient on Digoxin and Lasix:

{MRS_JOHNSON_CONTEXT}

The nurse is concerned about the K+ of 3.2 with the patient on Digoxin.

Provide:
1. Priority level (Routine/Urgent/Critical)
2. Key findings and concerns
3. Clinical significance (especially Digoxin-hypokalemia interaction)
4. Recommended actions
5. SBAR format for MD notification

Be specific and actionable."""

start = time.time()
response1 = generate_response(CLINICAL_REF_PROMPT, lab_prompt, max_tokens=700)
time1 = time.time() - start

print(f"\n⏱️ Response time: {time1:.1f} seconds\n")
print(response1)

print("\n" + "=" * 70)
print("DEMO 2: Shift Watch (What to Watch This Shift)")
print("=" * 70)

shift_prompt = f"""Generate a "What to Watch This Shift" checklist for this patient:

{MRS_JOHNSON_CONTEXT}

Shift: DAY SHIFT
Context: Day shift - most tests, procedures, and rounding happen. Family often visits.

Provide a practical shift checklist including:
- RED FLAGS - Call MD Immediately If (with specific parameters)
- WATCH CLOSELY - Key things to monitor
- SHIFT PRIORITIES - Top 3-5 specific tasks
- MEDICATION ALERTS - Timing-critical meds, hold parameters
- ANTICIPATED NEEDS - Expected orders, family questions

Keep it actionable and specific to THIS patient."""

start = time.time()
response2 = generate_response(SHIFT_SIDEKICK_PROMPT, shift_prompt, max_tokens=800)
time2 = time.time() - start

print(f"\n⏱️ Response time: {time2:.1f} seconds\n")
print(response2)

print("\n" + "=" * 70)
print("DEMO 3: Explain CHF to Family")
print("=" * 70)

explain_prompt = """A patient's daughter asks: "What is CHF? The doctor keeps saying it but I don't understand."

Please explain CHF (Congestive Heart Failure) to a worried family member using:
- 8th grade reading level
- Simple analogies
- What to expect
- Reassuring but honest tone

The patient is a 68-year-old woman with CHF (EF 35%) admitted for acute exacerbation.

Include:
1. Simple explanation of what CHF means
2. Why it's happening
3. What the treatment is doing
4. What to expect going forward
5. Questions they might want to ask the doctor"""

start = time.time()
response3 = generate_response(QUICK_EXPLAIN_PROMPT, explain_prompt, max_tokens=600)
time3 = time.time() - start

print(f"\n⏱️ Response time: {time3:.1f} seconds\n")
print(response3)

print("\n" + "=" * 70)
print("DEMO 4: Family Medication Teaching")
print("=" * 70)

med_prompt = """Help me explain these medications to a patient's family member.
Use an 8th grade reading level - simple, everyday language.

Patient context: Mary Johnson, 68yo with CHF exacerbation

Medications to explain:
- METOPROLOL 25mg
- FUROSEMIDE (Lasix) 40mg
- DIGOXIN 0.125mg
- LISINOPRIL 10mg

For EACH medication, provide:
- What it's for (simple terms)
- What it does (everyday comparison)
- What to watch for
- Important tips

Use language like "This medicine helps..." not "This medication is indicated for..."

End with 2-3 questions the family might want to ask."""

start = time.time()
response4 = generate_response(QUICK_EXPLAIN_PROMPT, med_prompt, max_tokens=700)
time4 = time.time() - start

print(f"\n⏱️ Response time: {time4:.1f} seconds\n")
print(response4)

print("\n" + "=" * 70)
print("DEMO 5: SBAR Shift Handoff")
print("=" * 70)

handoff_prompt = f"""Generate a nursing shift handoff report in SBAR format from this information:

{MRS_JOHNSON_CONTEXT}

This is for Day Shift → Evening Shift handoff.

Format as:
**SITUATION**
[Current state - what's happening right now]

**BACKGROUND**
[Relevant history and context]

**ASSESSMENT**
[Nursing assessment and concerns]

**RECOMMENDATION**
[What needs to happen next shift]

Also include:
- Critical tasks pending
- Changes from earlier in shift
- What to watch for tonight
- Hold parameters for medications"""

start = time.time()
response5 = generate_response(SHIFT_SIDEKICK_PROMPT, handoff_prompt, max_tokens=800)
time5 = time.time() - start

print(f"\n⏱️ Response time: {time5:.1f} seconds\n")
print(response5)

# Summary
print("\n" + "=" * 70)
print("SUMMARY - Real MedGemma Performance")
print("=" * 70)

total_time = time1 + time2 + time3 + time4 + time5
manual_estimate = 10 + 5 + 5 + 8 + 12  # minutes

print(f"""
Demo                      AI Time    Manual Est.   Saved
─────────────────────────────────────────────────────────
1. Critical Lab Analysis  {time1:5.1f}s     10 min       ~10 min
2. Shift Watch            {time2:5.1f}s      5 min        ~5 min
3. Explain CHF            {time3:5.1f}s      5 min        ~5 min
4. Med Teaching           {time4:5.1f}s      8 min        ~8 min
5. SBAR Handoff           {time5:5.1f}s     12 min       ~12 min
─────────────────────────────────────────────────────────
TOTAL                     {total_time:5.1f}s     40 min       ~40 min
""")

print("✓ These are REAL MedGemma 1.5 4B responses!")
print("✓ Model: google/medgemma-1.5-4b-it")
print(f"✓ Device: {next(model.parameters()).device}")
print("=" * 70)
