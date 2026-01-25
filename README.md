# NurseGemma

**Your Nursing AI Companion - Built by a nurse, for nurses and families.**

NurseGemma bridges the gap between families and healthcare teams using Google MedGemma.

## The Problem

As an ICU nurse, I spend 40% of my shift documenting instead of caring for patients. Meanwhile, families wait anxiously with questions - "What does this mean?" "Why is this beeping?" "Is my dad going to be okay?"

## The Solution

**NurseGemma bridges this gap:**

1. **Family at bedside** → Asks NurseGemma questions while waiting
2. **NurseGemma responds** → Provides clear, reassuring explanations
3. **Nurse makes rounds** → Reviews the summary of what family asked
4. **Nurse follows up** → Clarifies, expands, or corrects as needed

*Families get immediate answers. Nurses save time on repetitive education. Everyone stays on the same page.*

## Features

### 1. Ask Questions
Families get medical explanations in plain English. No jargon.

```python
ask_nursegemma("What is CHF? My dad was just diagnosed.")
```

### 2. Analyze Images
Nurses get professional documentation for wounds and scans.

```python
# Wound charting
analyze_wound(image_url, patient_context="elderly patient, sacral area")

# Scan interpretation
analyze_scan(image_url, scan_type="chest X-ray")
```

### 3. Nurse Summary
Healthcare team gets a handoff summary of all family questions.

```python
# After family asks questions, generate summary for the nurse
generate_nurse_summary(patient_name="Room 512 - Mr. Johnson")
```

**Summary includes:**
- Key family concerns
- Topics already covered
- Knowledge gaps to address
- Suggested follow-up items

## Quick Start

Run on [Kaggle](https://www.kaggle.com/) with GPU enabled:

1. Open `nursegemma.ipynb` on Kaggle
2. Add your HuggingFace token to Kaggle Secrets as `HF_TOKEN`
3. Enable GPU (Settings → Accelerator → GPU T4 x2)
4. Run All

## Requirements

- GPU with 16GB+ VRAM (T4, P100, or better)
- HuggingFace account with MedGemma access

## Disclaimer

NurseGemma is an educational tool. All outputs should be verified by qualified healthcare professionals. Not for diagnostic or treatment decisions.

---

*MedGemma Impact Challenge 2026*
