# 🩺 NurseGemma

**Agentic Medical AI for Nursing Practice**

*Built by a nurse, for nurses.*

[![MedGemma Impact Challenge](https://img.shields.io/badge/MedGemma-Impact%20Challenge%202026-blue)](https://www.kaggle.com/competitions/med-gemma-impact-challenge)
[![Agentic AI](https://img.shields.io/badge/Category-Agentic%20AI-green)]()
[![MedGemma 1.5](https://img.shields.io/badge/MedGemma-1.5%204B-orange)]()

---

## 🆕 New in MedGemma 1.5 Update!

| Feature | Description | Nursing Use Case |
|---------|-------------|------------------|
| 🎤 **MedASR Voice Input** | Medical speech-to-text (82% fewer errors vs Whisper) | Hands-free bedside dictation |
| 📊 **Longitudinal Comparison** | Compare X-rays over time | Track patient progression for handoffs |
| 🧊 **3D CT/MRI Analysis** | Full volumetric scan interpretation | Comprehensive imaging assessment |
| 🔬 **Lab Report Extraction** | Structured data from lab images (+18% accuracy) | Rapid lab interpretation |
| 🗺️ **Anatomical Localization** | CXR landmark identification (+35% IoU) | Verify tube/line positions |

---

## 🏗️ Architecture

NurseGemma uses a **multi-agent architecture** with Gemini as the orchestrator and MedGemma 1.5 as the medical specialist:

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INPUT                                 │
│     Text Query | Voice (MedASR) | Single/Multiple Images     │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                  GEMINI ORCHESTRATOR                          │
│        Intent Classification | Routing | Synthesis            │
└───────────────────────────┬──────────────────────────────────┘
                            │
    ┌───────────┬───────────┼───────────┬───────────┬──────────┐
    ▼           ▼           ▼           ▼           ▼          ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ IMAGE  │ │LONGIT- │ │VOLUMETRIC│ │  LAB   │ │ANATOMY │ │EVIDENCE│
│ AGENT  │ │UDINAL  │ │  AGENT   │ │ AGENT  │ │ AGENT  │ │ AGENT  │
│        │ │ AGENT  │ │          │ │        │ │        │ │        │
│MedGemma│ │MedGemma│ │ MedGemma │ │MedGemma│ │MedGemma│ │ Gemini │
│1.5 4B  │ │1.5 4B  │ │ 1.5 4B   │ │1.5 4B  │ │1.5 4B  │ │Grounded│
└────────┘ └────────┘ └──────────┘ └────────┘ └────────┘ └────────┘
    │           │           │           │           │          │
    └───────────┴───────────┴───────────┴───────────┴──────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │  NURSING-FOCUSED RESPONSE   │
              │  • Key Findings             │
              │  • Nursing Considerations   │
              │  • Safety Alerts            │
              │  • Escalation Criteria      │
              └─────────────────────────────┘
```

### Agent Roles

| Agent | Model | Function |
|-------|-------|----------|
| **Orchestrator** | Gemini 2.0 Flash | Routes queries, classifies intent, synthesizes responses |
| **Image Agent** | MedGemma 1.5 4B | Single image analysis (X-ray, CT, wound) |
| **Longitudinal Agent** | MedGemma 1.5 4B | 🆕 Compare images over time (trending) |
| **Volumetric Agent** | MedGemma 1.5 4B | 🆕 3D CT/MRI volume analysis |
| **Lab Agent** | MedGemma 1.5 4B | 🆕 Lab report extraction & interpretation |
| **Anatomy Agent** | MedGemma 1.5 4B | 🆕 CXR anatomical localization |
| **Evidence Agent** | Gemini + Grounding | Guidelines search (SCCM, AACN, PubMed) |
| **Clinical Agent** | MedGemma 1.5 4B | General clinical Q&A |

---

## 🎯 The Problem

As an ICU nurse, I face two challenges daily:

1. **40% of my shift is documentation** instead of patient care
2. **Families wait anxiously** with questions they're afraid to ask

NurseGemma bridges this gap with AI that understands nursing workflows.

---

## ✨ Features

### 🚨 Code Blue Agent - ACLS 2025 Compliant

Real-time voice-activated cardiac arrest documentation with automatic timestamping and ACLS algorithm guidance.

**Voice Commands:**
```
"Code called"          → Start documentation
"CPR started"          → Log CPR cycle
"V-fib"                → Identify shockable rhythm
"Shock delivered 200J" → Log defibrillation
"Epi given"            → Log epinephrine + timer
"ETCO2 25"             → Log capnography
"Check H's and T's"    → Reversible causes checklist
"ROSC"                 → Log outcome
```

**ACLS 2025 Compliance:**
| Protocol | Guidance |
|----------|----------|
| VF/pVT | Epi AFTER 2nd shock, Amio after 3rd |
| PEA/Asystole | Epi ASAP, treat H's and T's |
| Monitoring | ETCO2 alerts, Epi timing (q3-5min) |
| CPR Quality | Compressor switch reminders (q2min) |

---

### 1. 🎤 Voice Input (MedASR) - NEW!
Hands-free nursing mode. Dictate your questions while providing patient care.

```
"Patient in bed 4 has new onset confusion and left-sided weakness. Priority assessment?"
```

### 2. 📊 Longitudinal Comparison - NEW!
Upload multiple X-rays to track patient progression over time.

```
"Compare the admission CXR to today's follow-up. Is the pneumonia improving?"
```

### 3. 🧊 3D CT/MRI Volumes - NEW!
Upload multiple slices for comprehensive volumetric analysis.

```
"Analyze this CT scan - what are the key findings across all slices?"
```

### 4. 🔬 Lab Report Extraction - NEW!
Upload a photo of lab results for instant extraction and interpretation.

```
"Extract all values from this CBC and interpret for a post-op patient"
```

### 5. 🖼️ Medical Image Analysis
Analyze X-rays, CT scans, MRI, and wounds with nursing-focused interpretations.

```
"Analyze this chest X-ray for my ICU patient. What should I report to the physician?"
```

### 6. 💊 Clinical Q&A
Get answers about medications, lab values, and procedures.

```
"What are the nursing considerations for Lasix (furosemide)?"
```

### 7. 📚 Evidence-Based Practice
Search guidelines and literature for best practices.

```
"What does the evidence say about prone positioning in ARDS?"
```

---

## 🚀 Quick Start

### Option 1: Gradio Web UI (Local)

```bash
# Clone the repo
git clone https://github.com/AIHeartICU/NurseGemma.git
cd NurseGemma

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-gemini-api-key"  # Free from Google AI Studio

# Optional: Enable MedGemma (requires GPU + HuggingFace access)
export HF_TOKEN="your-huggingface-token"
export USE_MEDGEMMA="true"
export USE_MEDASR="true"

# Run the app
python app.py
```

### Option 2: HuggingFace Spaces

Visit: [https://huggingface.co/spaces/AIHeartICU/nursegemma](https://huggingface.co/spaces/AIHeartICU/nursegemma)

### Option 3: Kaggle Notebook

1. Open `nursegemma.ipynb` on [Kaggle](https://www.kaggle.com/)
2. Add your HuggingFace token to Kaggle Secrets as `HF_TOKEN`
3. Enable GPU (Settings → Accelerator → GPU T4 x2)
4. Run All

---

## 🔑 API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Gemini** | Orchestrator agent | [Google AI Studio](https://makersuite.google.com/app/apikey) (free) |
| **HuggingFace** | MedGemma/MedASR access | [HuggingFace](https://huggingface.co/settings/tokens) |

---

## 🖼️ Sample Images for Testing

Download from these Kaggle datasets to test image analysis:

| Type | Dataset |
|------|---------|
| **Chest X-rays** | [NIH Chest X-ray Dataset](https://www.kaggle.com/datasets/nih-chest-xrays/data) |
| **CT Scans** | [Chest CT-Scan Images](https://www.kaggle.com/datasets/mohamedhanyyy/chest-ctscan-images) |
| **Brain MRI** | [Brain MRI Dataset](https://www.kaggle.com/datasets/navoneel/brain-mri-images-for-brain-tumor-detection) |
| **Skin/Wound** | [Skin Cancer Dataset](https://www.kaggle.com/datasets/fanconic/skin-cancer-malignant-vs-benign) |

---

## 📝 Technical Overview

### Why Agentic?

Traditional medical AI is single-model, single-task. NurseGemma is different:

1. **Intent Classification**: Gemini analyzes what you're asking
2. **Smart Routing**: Queries go to specialized agents
3. **Multi-Agent Collaboration**: Complex queries use multiple agents
4. **Synthesis**: Orchestrator combines responses into cohesive answers

### Why Nursing-Focused?

- Nurses are the largest healthcare workforce (4M+ in US alone)
- 40% of nursing time is spent on documentation
- Families need information but nurses are stretched thin
- ICU/critical care has highest information needs

### MedGemma 1.5 Improvements Used

- **3D Volumetric**: First open LLM with true 3D CT/MRI support
- **Longitudinal Imaging**: Compare images over time (5% macro accuracy boost)
- **Lab Extraction**: 18% F1 improvement on structured extraction
- **Anatomical Localization**: 35% IoU improvement on CXR landmarks
- **MedASR**: 82% fewer errors than Whisper on medical dictation

---

## ⚠️ Disclaimer

NurseGemma is an **educational tool**. All outputs should be verified by qualified healthcare professionals. Not intended for diagnostic or treatment decisions.

---

## 📜 License

MIT License

---

## 🙏 Acknowledgments

- Google MedGemma team for the incredible open models
- The nursing community for inspiring this project
- MedGemma Impact Challenge organizers

---

*Built with ❤️ by a nurse who codes | MedGemma Impact Challenge 2026 - Agentic Category*
