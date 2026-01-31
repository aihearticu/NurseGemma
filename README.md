# 🩺 NurseGemma Code Blue

**Voice-activated ACLS 2025 cardiac arrest assistant for nurses**

[![Demo](https://img.shields.io/badge/Demo-Live-green)](https://34700187b6e2aee5a2.gradio.live)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)](https://gradio.app)

## 🎯 What It Does

NurseGemma is a **mobile-first Code Blue assistant** that helps nurses:

- 📱 **Document interventions in real-time** via voice or tap
- ⏱️ **Track timing** for CPR, meds, and rhythm checks
- 🎤 **Voice commands** during resuscitation (hands-busy scenarios)
- 📋 **Generate charting reports** automatically for documentation
- ✅ **ACLS 2025 compliant** prompts and guidance

## 🚀 Quick Start

### Live Demo
**[Try it on your phone →](https://34700187b6e2aee5a2.gradio.live)**

### Run Locally
```bash
# Clone
git clone https://github.com/AIHeartICU/NurseGemma.git
cd NurseGemma

# Install
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python app.py
```

## 📱 How to Use

### Button Interface (Fastest)
1. **Tap CODE BLUE** to start
2. **Identify rhythm**: V-Fib, V-Tach, Asystole, or PEA
3. **Log interventions**: Shock, Epi, Amio, CPR, IV Access
4. **Tap ROSC** when pulse returns
5. **Generate Report** for charting

### Voice Commands
1. Tap **🎤 Voice** button
2. Speak clearly: "V-fib", "Shock", "Epi given", "ROSC"
3. Command auto-submits when you stop speaking

## ⚡ ACLS 2025 Features

| Feature | Description |
|---------|-------------|
| **Shockable vs Non-shockable** | Color-coded rhythm buttons (⚡ vs ❌) |
| **Drug Timing** | Prompts for Epi q3-5min, Amio after 3rd shock |
| **H's & T's Checklist** | Reversible causes reminder |
| **Quality Metrics** | Time to first shock, time to first Epi |
| **Post-ROSC Care** | Checklist for post-arrest management |

## 📋 Documentation Report

After ROSC, NurseGemma generates a complete Code Blue record:

```
╔══════════════════════════════════════════════════════════════╗
║              CODE BLUE RECORD - ACLS 2025                    ║
╚══════════════════════════════════════════════════════════════╝

Date: 2026-01-31
Time Called: 00:15:30
Duration: 8 min 45 sec
Outcome: ROSC

MEDICATIONS:
Epinephrine 1mg x 3 doses
  Dose 1: 00:16:15
  Dose 2: 00:19:30
  Dose 3: 00:22:45

DEFIBRILLATION:
  Shock 1: 00:15:45 - 200J
  Shock 2: 00:17:50 - 200J

EVENT LOG:
| Time     | Run   | Event       | Details                    |
|----------|-------|-------------|----------------------------|
| 00:15:30 | 00:00 | CODE_CALLED | Code Blue initiated        |
| 00:15:35 | 00:05 | RHYTHM      | VF identified              |
...
```

## 🛠️ Tech Stack

- **Frontend**: Gradio (mobile-responsive)
- **Backend**: Python
- **Voice**: Web Speech API (browser-native)
- **Model**: Rule-based ACLS logic (no LLM required for core functionality)

## 📁 Project Structure

```
NurseGemma/
├── app.py                 # Main Gradio app
├── code_blue_agent.py     # ACLS logic & documentation
├── acls_protocol.py       # ACLS 2025 reference data
├── requirements.txt       # Dependencies
└── tests/                 # Unit tests
```

## 🎓 Educational Purpose

⚠️ **This is an educational tool for training purposes only.**

- Not FDA approved for clinical use
- Always follow your institution's protocols
- Real codes require real equipment and trained personnel

## 👨‍⚕️ Created By

**James Perlas** ([@AIHeartICU](https://github.com/AIHeartICU))  
ICU Nurse & AI Developer

Built with ❤️ for the nursing community.

---

*ACLS 2025 guidelines from American Heart Association*
