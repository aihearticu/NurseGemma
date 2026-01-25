# NurseGemma

**Your Nursing AI Assistant - Built by a nurse, for nurses and families.**

A simple AI assistant powered by Google MedGemma that helps:
- **Families** understand medical information in plain English
- **Nurses** document wounds and interpret scans efficiently

## Features

### 1. Ask Questions
Get medical explanations anyone can understand. No jargon.

```python
ask_nursegemma("What is CHF? My dad was just diagnosed.")
```

### 2. Analyze Images
Upload wound photos or scans for professional documentation.

```python
# Wound charting
analyze_wound(image_url, patient_context="elderly patient, sacral area")

# Scan interpretation
analyze_scan(image_url, scan_type="chest X-ray")
```

## Quick Start

Run on [Kaggle](https://www.kaggle.com/) with GPU enabled:

1. Open `nursegemma.ipynb` on Kaggle
2. Add your HuggingFace token to Kaggle Secrets as `HF_TOKEN`
3. Enable GPU (Settings → Accelerator → GPU)
4. Run All

## Requirements

- GPU with 16GB+ VRAM (T4, P100, or better)
- HuggingFace account with MedGemma access

## Disclaimer

NurseGemma is an educational tool. All outputs should be verified by qualified healthcare professionals. Not for diagnostic or treatment decisions.

---

*MedGemma Impact Challenge 2026*
