# 🩺 NurseGemma

**Agentic Medical AI for Nursing Practice**

*Built by a nurse, for nurses and families.*

[![MedGemma Impact Challenge](https://img.shields.io/badge/MedGemma-Impact%20Challenge%202026-blue)](https://www.kaggle.com/competitions/med-gemma-impact-challenge)
[![Agentic AI](https://img.shields.io/badge/Category-Agentic%20AI-green)]()

---

## 🏗️ Architecture

NurseGemma uses a **multi-agent architecture** with:

```
┌─────────────────────────────────────────────────┐
│           GEMINI ORCHESTRATOR                   │
│     (Intent classification, routing, synthesis) │
└──────────────────┬──────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬───────────────┐
    ▼              ▼              ▼               ▼
┌────────┐  ┌────────────┐  ┌──────────┐  ┌────────────┐
│ IMAGE  │  │  CLINICAL  │  │ EVIDENCE │  │  SUMMARY   │
│ AGENT  │  │  QA AGENT  │  │  AGENT   │  │   AGENT    │
│        │  │            │  │          │  │            │
│MedGemma│  │ MedGemma   │  │ RAG+Lit  │  │ MedGemma   │
│ 1.5 4B │  │  1.5 4B    │  │          │  │            │
└────────┘  └────────────┘  └──────────┘  └────────────┘
```

### Agent Roles

| Agent | Model | Function |
|-------|-------|----------|
| **Orchestrator** | Gemini 1.5 Flash | Routes queries, classifies intent, synthesizes responses |
| **Image Agent** | MedGemma 1.5 4B | Analyzes X-rays, CT, MRI, wound images |
| **Clinical QA** | MedGemma 1.5 4B | Medications, lab values, procedures, protocols |
| **Evidence Agent** | RAG | Guidelines (SCCM, AACN), PubMed literature |
| **Summary Agent** | MedGemma 1.5 4B | SBAR handoffs, shift reports, documentation |

---

## 🎯 The Problem

As an ICU nurse, I face two challenges daily:

1. **40% of my shift is documentation** instead of patient care
2. **Families wait anxiously** with questions they're afraid to ask

NurseGemma bridges this gap with AI that understands nursing workflows.

---

## ✨ Features

### 1. 🖼️ Medical Image Analysis
Analyze X-rays, CT scans, MRI, and wounds with nursing-focused interpretations.

```python
# Example: Analyze chest X-ray
"Analyze this chest X-ray for my ICU patient. What should I report to the physician?"
```

### 2. 💊 Clinical Q&A
Get answers about medications, lab values, and procedures.

```python
# Example: Drug considerations
"What are the nursing considerations for Lasix?"
```

### 3. 📚 Evidence-Based Practice
Search guidelines and literature for best practices.

```python
# Example: Evidence query
"What does the evidence say about prone positioning in ARDS?"
```

### 4. 📋 Nurse Summaries
Generate SBAR-style handoffs and shift reports.

```python
# Example: Handoff summary
"Summarize this patient for night shift handoff"
```

---

## 🖼️ Sample Images

The demo includes clickable sample medical images:

| Category | Samples |
|----------|---------|
| **X-ray** | Normal chest, Pneumonia, Pleural effusion |
| **CT** | Normal brain, Ischemic stroke (MCA) |
| **MRI** | Knee (ACL/meniscus) |
| **Wound** | Stage IV pressure ulcer |

---

## 🚀 Quick Start

### Option 1: Hugging Face Spaces
Visit: [NurseGemma on HuggingFace](https://huggingface.co/spaces/AIHeartICU/NurseGemma)

### Option 2: Local/Kaggle

```bash
# Clone the repo
git clone https://github.com/AIHeartICU/NurseGemma.git
cd NurseGemma

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export HF_TOKEN="your-huggingface-token"

# Run the app
python app.py
```

### Option 3: Kaggle Notebook
Open `nursegemma.ipynb` on Kaggle with GPU enabled.

---

## 🔑 API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Gemini** | Orchestrator agent | [Google AI Studio](https://makersuite.google.com/app/apikey) (free) |
| **HuggingFace** | MedGemma access | [HuggingFace](https://huggingface.co/settings/tokens) |

---

## 🎬 Demo Video

[Watch the 3-minute demo](link-coming-soon)

---

## 📝 Technical Overview

**Why Agentic?**

Traditional medical AI is single-model, single-task. NurseGemma is different:

1. **Intent Classification**: Gemini analyzes what you're asking
2. **Smart Routing**: Queries go to specialized agents
3. **Multi-Agent Collaboration**: Complex queries use multiple agents
4. **Synthesis**: Orchestrator combines responses into cohesive answers

**Why Nursing-Focused?**

- Nurses are the largest healthcare workforce
- 40% of nursing time is documentation
- Families need information but nurses are stretched thin
- ICU/critical care has highest information needs

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

*Built with ❤️ by a nurse who codes | MedGemma Impact Challenge 2026*
