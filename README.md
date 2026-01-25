# Nurse Companion

**Your AI Shift Buddy - Built by a nurse, for nurses.**

An AI assistant powered by MedGemma that helps nurses with patient communication, medication information, shift handoffs, and clinical reference - so they can spend more time caring for patients.

## The Problem

| Crisis | Statistic |
|--------|-----------|
| EHR burden | 92% of nurses say it hurts job satisfaction |
| Documentation time | 40% of every shift spent charting |
| Patient understanding | 65% don't understand their treatment |
| Nursing exodus | 100,000 RNs left in past 2 years |

## The Solution

### Modules

1. **Quick Explain** - Medical jargon → plain English for patients & families
2. **Med Helper** - Conversational medication lookup with nursing focus
3. **Shift Sidekick** - SBAR handoff report generation
4. **Clinical Quick Ref** - Lab values, procedures, assessments

## Quick Start

### On Kaggle (Recommended)

1. Open `notebooks/nurse_companion_demo.ipynb` on Kaggle
2. Enable GPU accelerator (T4 x2)
3. Run all cells
4. Use the Gradio interface

### Local Development

```bash
# Clone and setup
cd "MedGemma Impact Challenge"
pip install -r requirements.txt

# Run the demo
python -c "from src.nurse_companion import NurseCompanion; c = NurseCompanion(); c.load_model()"
```

## Project Structure

```
MedGemma Impact Challenge/
├── notebooks/
│   └── nurse_companion_demo.ipynb  # Main submission notebook
├── src/
│   └── nurse_companion.py          # Core module code
├── prompts/
│   └── nursing_prompts.py          # Prompt templates
├── tests/
│   └── test_scenarios.py           # Validation scenarios
├── data/                           # Competition data
├── PROJECT_PLAN.md                 # Full project plan
├── CLAUDE.md                       # Project context
└── requirements.txt
```

## Usage Examples

### Quick Explain
```python
response = companion.quick_explain(
    term="atrial fibrillation",
    reading_level="8th grade",
    for_family=True,
    context="Patient just diagnosed"
)
```

### Med Helper
```python
# Single medication
info = companion.med_info("metoprolol")

# Check interactions
interactions = companion.check_interactions(["warfarin", "aspirin", "ibuprofen"])
```

### Shift Sidekick
```python
sbar = companion.generate_sbar(
    patient_info="72 y/o male, pneumonia, day 3 of antibiotics...",
    format_style="standard"
)
```

### Clinical Quick Ref
```python
# Lab interpretation
result = companion.interpret_lab("Potassium", 6.2, "mEq/L")

# Condition monitoring
guide = companion.what_to_watch("new onset atrial fibrillation")
```

## Competition

**MedGemma Impact Challenge**
- Prize: $100,000
- Deadline: February 24, 2026
- Goal: Human-centered AI applications using MedGemma

## Why This Will Win

1. **Human-centered** - Built from real nursing pain points
2. **Domain expertise** - Created BY a nurse, FOR nurses
3. **Underserved market** - Most AI targets physicians
4. **High impact** - Addresses 4M+ nurse workforce
5. **Multi-module** - Comprehensive solution, not single feature

## Safety & Disclaimers

- For educational and reference purposes only
- Always verify with facility protocols
- Not a substitute for professional judgment
- Medication info should be confirmed with pharmacy
- Clinical decisions require licensed professional oversight

## Author

**AIHeartICU** - An ICU nurse who believes AI should help us care for patients, not create more paperwork.

---

*Built with MedGemma for the MedGemma Impact Challenge*
