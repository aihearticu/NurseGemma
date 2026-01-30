# 🩺 NurseGemma

**Your AI Nursing Companion** — Built by a nurse, for nurses and families.

NurseGemma bridges the gap between families and healthcare teams using Google MedGemma.

🌐 **Live Demo**: [mentius.ai/nursegemma](https://mentius.ai/nursegemma/)

## The Problem

As an ICU nurse, I spend 40% of my shift documenting instead of caring for patients. Meanwhile, families wait anxiously with questions — "What does this mean?" "Why is this beeping?" "Is my dad going to be okay?"

## The Solution

NurseGemma bridges this gap:

1. **Family at bedside** → Asks NurseGemma questions while waiting
2. **NurseGemma responds** → Provides clear, reassuring explanations  
3. **Nurse makes rounds** → Reviews the summary of what family asked
4. **Nurse follows up** → Clarifies, expands, or corrects as needed

*Families get immediate answers. Nurses save time on repetitive education. Everyone stays on the same page.*

## Features

### 👨‍👩‍👧 Family Mode
Get medical explanations in plain English. No jargon.

```python
ask_nursegemma("What is CHF? My dad was just diagnosed.")
```

### 👩‍⚕️ Nurse Mode  
Get professional clinical assessments with proper terminology.

```python
ask_nursegemma("68yo M, POD 2 hip replacement, new confusion and fever - assessment?")
```

### 🖼️ Image Analysis
Upload wound photos or medical scans for AI-assisted interpretation.

```python
analyze_wound(image, patient_context="elderly patient, sacral area")
analyze_scan(image, scan_type="chest X-ray")
```

### 📋 Nurse Summary
Generate handoff summaries of all family questions for the healthcare team.

```python
generate_nurse_summary(patient_name="Room 512 - Mr. Johnson")
```

## Quick Start

### Option 1: Kaggle (Recommended for Competition)

1. Open `nursegemma.ipynb` on [Kaggle](https://www.kaggle.com/)
2. Add your HuggingFace token to Kaggle Secrets as `HF_TOKEN`
3. Enable GPU (Settings → Accelerator → GPU T4 x2)
4. Run All

### Option 2: Local GPU Server

Requirements: NVIDIA GPU with 16GB+ VRAM (RTX 3090, 4090, A100)

```bash
# Clone repo
git clone https://github.com/AIHeartICU/NurseGemma.git
cd NurseGemma

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install torch transformers accelerate gradio huggingface_hub

# Login to HuggingFace (need MedGemma access)
huggingface-cli login

# Run server (creates public link)
python local_server.py
```

### Option 3: Web Demo

Try it now at [mentius.ai/nursegemma](https://mentius.ai/nursegemma/)

## Requirements

- **Kaggle/Local**: GPU with 16GB+ VRAM, HuggingFace account with MedGemma access
- **Web Demo**: Just a browser!

## Tech Stack

- **Model**: Google MedGemma 4B (medical fine-tuned Gemma)
- **Framework**: Gradio / Streamlit
- **Inference**: PyTorch + Transformers

## Disclaimer

⚠️ **NurseGemma is an educational tool.** All outputs should be verified by qualified healthcare professionals. Not for diagnostic or treatment decisions.

## Links

- 🌐 [Live Demo](https://mentius.ai/nursegemma/)
- 🏆 [MedGemma Impact Challenge](https://www.kaggle.com/competitions/med-gemma-impact-challenge)
- 🐦 [Twitter @AIHeartICU](https://x.com/AIHeartICU)

---

*Built for the MedGemma Impact Challenge 2026*
