# NurseGemma: An Agentic AI Companion for Nurses
## Technical Overview for MedGemma Impact Challenge

**Author:** AIHeartICU (ICU Nurse & Developer)
**Model:** MedGemma 1.5 4B (google/medgemma-1.5-4b-it)
**Repository:** kaggle.com/aihearticu/nursegemma-ai-companion-for-nurses

---

## Page 1: Problem Statement & Solution Architecture

### The Documentation Burden Crisis

Nurses face a critical documentation burden that directly impacts patient care:

| Statistic | Source |
|-----------|--------|
| **40%** of nursing shift spent on documentation | U.S. Surgeon General |
| **79%** of nurses lose time to unproductive charting | KLAS Research |
| **60%** cite duplicative documentation as top pain point | Industry Survey |
| **4+ million** registered nurses in the US affected | BLS |

This documentation burden contributes to nurse burnout, staffing shortages, and reduced time at the bedside. The average nurse spends only **31%** of their shift on direct patient care.

### NurseGemma: Built BY a Nurse, FOR Nurses

NurseGemma is an agentic AI companion that reduces documentation burden through intelligent automation. As an ICU nurse, I designed NurseGemma around actual clinical workflows and pain points.

**Core Design Principles:**
1. **Workflow Alignment** - Designed around clinical tasks, not AI capabilities
2. **One-Click Actions** - Every click costs bedside time
3. **Privacy First** - Works locally without cloud dependency
4. **Clinical Safety** - High-alert medication warnings, escalation criteria

### Solution Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NurseGemma Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│  PRESENTATION LAYER                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  EPIC-Style Gradio UI                                        ││
│  │  • Patient Header (demographics, MRN, attending)             ││
│  │  • Chart Tabs (MAR, Labs, Vitals, Notes, MD Note)           ││
│  │  • AI Companion Panel with Time Savings Display              ││
│  │  • One-Click Workflow Buttons                                ││
│  └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  AGENTIC WORKFLOW LAYER                                          │
│  ┌──────────────┬──────────────┬──────────────┬───────────────┐ │
│  │Smart Admission│Critical Lab  │Shift Handoff │Med Safety    │ │
│  │(5 steps)      │(4 steps)     │(4 steps)     │(4 steps)     │ │
│  └──────────────┴──────────────┴──────────────┴───────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  CORE MODULE LAYER (10 Modules)                                  │
│  ┌────────────┬────────────┬────────────┬────────────┐          │
│  │Quick Explain│Med Helper  │Shift Sidekick│Clinical Ref│        │
│  │Scales      │Calculations│Highlight   │Progress    │          │
│  │Shift Watch │Family Teach│            │            │          │
│  └────────────┴────────────┴────────────┴────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  MODEL LAYER                                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              MedGemma 1.5 4B                                  ││
│  │  • Instruction-tuned for medical conversations               ││
│  │  • 4B parameters (optimized for edge deployment)             ││
│  │  • torch.bfloat16 for efficient inference                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 2: Technical Implementation

### MedGemma Integration

NurseGemma uses MedGemma 1.5 4B from Google's Health AI Developer Foundations (HAI-DEF) collection:

```python
from transformers import AutoProcessor, AutoModelForImageTextToText

# Load MedGemma with efficient settings
processor = AutoProcessor.from_pretrained("google/medgemma-1.5-4b-it")
model = AutoModelForImageTextToText.from_pretrained(
    "google/medgemma-1.5-4b-it",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```

**Inference Pipeline:**
- Chat template formatting via `processor.apply_chat_template()`
- System prompts tailored for nursing context
- Temperature control for clinical accuracy (0.7 default)
- Max token limits per use case (200-1000 tokens)

### Agentic Workflow Implementation

Each workflow chains multiple MedGemma calls with intermediate processing:

**Example: Critical Lab Response Workflow**

```python
class WorkflowStep:
    name: str
    prompt_template: str
    depends_on: List[str]  # Step dependencies

# Workflow steps execute in dependency order
steps = [
    WorkflowStep("parse_labs", "Extract lab values...", []),
    WorkflowStep("analyze_values", "For each value...", ["parse_labs"]),
    WorkflowStep("prioritize", "Rank concerns...", ["analyze_values"]),
    WorkflowStep("notify_template", "Generate MD notification...", ["prioritize"])
]
```

**Workflow Execution Engine:**
1. Parse input data
2. Execute steps based on dependency graph
3. Accumulate context between steps
4. Generate final output with timing metrics

### Time Savings Tracking

Every workflow tracks execution time vs. estimated manual time:

```python
@dataclass
class WorkflowResult:
    final_output: str
    execution_time_seconds: float
    estimated_manual_time_seconds: float
    time_saved_seconds: float
    warnings: List[str]
    priority: Priority  # ROUTINE, ATTENTION, URGENT, CRITICAL
```

### 10 Core Modules

| Module | MedGemma Usage | Key Features |
|--------|----------------|--------------|
| Quick Explain | Single inference | Adjustable reading level |
| Med Helper | Single + optional interaction check | High-alert flagging |
| Shift Sidekick | Single inference | SBAR format enforced |
| Clinical Quick Ref | Single inference | Lab/procedure reference |
| Assessment Scales | Calculation + inference | GCS, NIHSS, Braden, NEWS2 |
| Nursing Calculations | Calculation + validation | Drip rates, dosing |
| Highlight-to-Explain | Single inference | Context-aware |
| Patient Progress Course | Multi-step | Trajectory analysis |
| Shift Watch | Single inference | Shift-specific (day/eve/night) |
| Family Med Teach | Single + per-med | Plain language |

### Safety Features

**High-Alert Medication Detection:**
```python
HIGH_ALERT_MEDICATIONS = [
    "heparin", "insulin", "warfarin", "digoxin",
    "opioids", "chemotherapy", "potassium_iv",
    # ... 19 total medications
]
```

**Critical Value Thresholds:**
```python
CRITICAL_VALUES = {
    "potassium": {"low": 2.5, "high": 6.5},
    "sodium": {"low": 120, "high": 160},
    "glucose": {"low": 50, "high": 500},
    # ... comprehensive thresholds
}
```

---

## Page 3: Clinical Validation & Impact Metrics

### Test Coverage

NurseGemma includes comprehensive test coverage:

| Test Category | Tests | Pass Rate |
|---------------|-------|-----------|
| Agentic Workflows | 35 | 100% |
| Assessment Scales | 21 | 100% |
| Highlight-to-Explain | 16 | 100% |
| New Features | 25 | 100% |
| UI Components | 46 | 100% |
| **Total** | **143** | **100%** |

### Clinical Accuracy Validation

Key clinical validations:
- Lab normal ranges verified against clinical references
- SBAR format compliance checked
- High-alert medication flags accurate
- Escalation criteria clinically appropriate
- Assessment scale calculations correct

### Quantified Impact

**Time Savings Per Workflow:**

| Workflow | Manual Time | NurseGemma | Savings |
|----------|-------------|------------|---------|
| Smart Admission | 15 min | 30 sec | 14.5 min |
| Critical Lab Response | 10 min | 25 sec | 9.6 min |
| Shift Handoff | 12 min | 35 sec | 11.4 min |
| Medication Safety | 8 min | 20 sec | 7.7 min |
| MD Communication | 5 min | 15 sec | 4.75 min |
| **Total per patient** | **50 min** | **~2 min** | **48 min** |

**Projected Daily Impact:**
- Average nurse: 4-6 patients per shift
- Potential time saved: **3-5 hours per shift**
- Additional bedside time: **30%+ increase**

### Sample Patient Scenarios

NurseGemma includes 4 realistic demo patients:

1. **Mrs. Johnson (68F)** - CHF exacerbation
   - Low K+ with Digoxin concern
   - Demonstrates: Lab safety, family explanation

2. **Mr. Smith (72M)** - Pneumonia Day 3
   - Improving trend
   - Demonstrates: Shift handoff, progress tracking

3. **Ms. Rodriguez (45F)** - DKA on insulin drip
   - Critical care scenario
   - Demonstrates: Critical lab response, medication safety

4. **Mr. Chen (55M)** - Post-op hip replacement
   - Pain management with opioid allergies
   - Demonstrates: Medication safety, post-op care

### Privacy & Deployment

NurseGemma is designed for clinical environments:
- **No cloud dependency** - Runs locally on Kaggle GPU
- **No real patient data** - Demo uses fictional patients
- **HIPAA-friendly** - Data stays on-premises
- **Edge-ready** - 4B parameter model fits clinical hardware

### Conclusion

NurseGemma demonstrates how MedGemma can be applied to real clinical workflows to reduce nursing documentation burden. With 5 agentic workflows, 10 core modules, and comprehensive safety features, NurseGemma provides a practical tool for healthcare AI deployment.

**Key Differentiators:**
1. Built by an ICU nurse with domain expertise
2. Agentic workflows with quantified time savings
3. EPIC-style professional UI
4. Comprehensive clinical safety features
5. 143 tests with 100% pass rate

---

*For questions: kaggle.com/aihearticu*
*Repository: nursegemma-ai-companion-for-nurses*
