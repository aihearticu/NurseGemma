#!/usr/bin/env python3
"""
NurseGemma UI Test Script
Tests the full Gradio UI with mock MedGemma responses.
"""

import warnings
warnings.filterwarnings('ignore')

import gradio as gr
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import Counter
import time

# =============================================================================
# MOCK MEDGEMMA - Returns realistic responses without actual model
# =============================================================================

def ask_medgemma(system_prompt: str, user_query: str, max_tokens: int = 800) -> str:
    """Mock MedGemma function for testing UI"""
    # Simulate processing time
    time.sleep(0.3)

    # Return contextual mock responses based on query content
    query_lower = user_query.lower()

    if "sbar" in query_lower or "handoff" in query_lower:
        return """## SBAR Handoff Report

**SITUATION**
- Room 412-A, Robert Johnson, 72 y/o male
- Admitted for community-acquired pneumonia with COPD exacerbation
- Currently stable on 2L NC, improving

**BACKGROUND**
- PMH: HTN, DM2, COPD, hyperlipidemia, former smoker (30 pack-years)
- Allergies: PCN (rash), Sulfa (hives)
- Day 3 of antibiotics (CTX/Azithro), responding well

**ASSESSMENT**
- WBC trending down: 14.6 → 11.2 (improving)
- O2 sats 94% at rest, desats to 89% with activity
- Taking 50% of meals, wife at bedside
- IV site patent, lungs with diminished bases

**RECOMMENDATION**
- Continue current antibiotic regimen
- PT/OT eval still pending - follow up
- Blood cultures: check final read
- Possible discharge tomorrow if continues improving

⚠️ CRITICAL ALERTS: Desats with activity - may need PT to assess
□ PENDING TASKS:
- [ ] Check final blood culture
- [ ] Follow up PT/OT eval
- [ ] Discuss discharge timeline with family"""

    elif "explain" in query_lower or "family" in query_lower or "pneumothorax" in query_lower:
        return """## Understanding Pneumothorax

**In simple terms:**
A pneumothorax means air has leaked out of the lung and is trapped in the space between the lung and the chest wall. Think of it like a balloon that has developed a small leak.

**Think of it like:**
Imagine your lung is like a balloon inside a sealed container (your chest). Normally the balloon fills the container. With a pneumothorax, some air escaped from the balloon into the container, so now the balloon can't fully expand.

**What to expect:**
- A chest tube is being placed to let the trapped air escape
- The tube will stay in for a few days while the lung heals
- Your loved one may feel some discomfort from the tube
- We'll take chest X-rays to monitor progress

**Questions to ask the doctor:**
1. How did this happen and can it happen again?
2. How long will the chest tube need to stay in?
3. What activities should be avoided during recovery?
4. What signs should we watch for at home?"""

    elif "heparin" in query_lower or "high-alert" in query_lower or "medication" in query_lower:
        return """## ⚠️ HIGH-ALERT MEDICATION: Heparin

**What it's for:**
Blood thinner that prevents clots from forming or getting bigger. Used for DVT, PE, heart conditions, and during certain procedures.

**Before giving:**
- Check PTT/aPTT result (goal usually 60-100 seconds)
- Verify dose with another RN (required double-check)
- Check for signs of bleeding
- Review platelet count (watch for HIT)
- Confirm no contraindications (active bleeding, recent surgery)

**How to give:**
- IV: Use infusion pump, never bolus without MD order
- SubQ: Rotate sites, don't rub after injection
- Always use correct concentration

**Monitor for:**
- Bleeding: gums, nose, bruising, dark stools, blood in urine
- Signs of HIT: platelet drop, new clots
- PTT levels per protocol

**⚠️ Safety:**
- REQUIRED: Independent double-check by 2 RNs
- High-alert: Verify dose, rate, concentration
- Antidote: Protamine sulfate
- Signs of overdose: Unusual bleeding, prolonged bleeding from IV sites"""

    elif "lab" in query_lower or "potassium" in query_lower or "interpret" in query_lower:
        return """## Lab Interpretation

**Potassium: 3.2 mEq/L (LOW)**
- Normal range: 3.5-5.0 mEq/L
- Clinical significance: Mild hypokalemia

**Why this matters:**
Low potassium can cause muscle weakness, cramps, and cardiac arrhythmias. This patient is on Lasix (furosemide) which causes potassium loss.

**Nursing actions:**
- Check telemetry for arrhythmias (U waves, flat T waves)
- Assess for muscle weakness, cramping
- Review other electrolytes (Mg often low too)
- Expect replacement order: PO or IV potassium
- If on digoxin: increased dig toxicity risk with low K

**When to notify MD:**
- K < 3.0 (critical)
- New arrhythmias on monitor
- Patient symptomatic
- Unable to take PO replacement

**Magnesium: 1.6 mg/dL (LOW)**
- Often depleted with K - may need replacement for K to correct"""

    elif "abg" in query_lower or "blood gas" in query_lower:
        return """## ABG Interpretation

**Results:** pH 7.32 | pCO2 52 | HCO3 26 | PaO2 72 | SaO2 93%

**Interpretation: respiratory acidosis (Partially Compensated)**

**Step-by-step analysis:**
1. pH 7.32 = Acidotic (normal 7.35-7.45)
2. pCO2 52 = High (normal 35-45) = Respiratory cause
3. HCO3 26 = Normal-high (normal 22-26) = Starting to compensate
4. PaO2 72 = Low = Hypoxemia

**Clinical correlation:**
This patient with COPD/pneumonia is retaining CO2 (hypoventilation) causing acidosis. The slightly elevated bicarb shows the kidneys are starting to compensate. Hypoxemia consistent with pneumonia.

**Nursing implications:**
- Monitor respiratory status closely
- Position for optimal breathing (HOB elevated)
- O2 titration per orders (careful in COPD)
- Watch for worsening mental status (CO2 narcosis)
- May need BiPAP or increased respiratory support"""

    else:
        return """## NurseGemma Response

I've analyzed your query and here's what you need to know:

**Key Points:**
- This response demonstrates the NurseGemma AI companion functionality
- In production, this would be powered by MedGemma 1.5 4B model
- All responses are nursing-focused and clinically relevant

**Clinical Considerations:**
- Always verify information with facility protocols
- Use clinical judgment in patient care decisions
- Document appropriately in the medical record

**Next Steps:**
- Review the relevant clinical guidelines
- Consult with the healthcare team as needed
- Follow up on any pending orders or tasks

*This is a test response for UI validation purposes.*"""


# =============================================================================
# HIGH-ALERT MEDICATIONS
# =============================================================================

HIGH_ALERT_MEDS = [
    "heparin", "warfarin", "enoxaparin", "rivaroxaban", "apixaban",
    "insulin", "lispro", "aspart", "glargine", "NPH",
    "morphine", "hydromorphone", "fentanyl", "oxycodone", "methadone",
    "potassium chloride", "magnesium sulfate", "sodium chloride 3%",
    "epinephrine", "norepinephrine", "vasopressin", "dopamine", "dobutamine",
    "propofol", "midazolam", "ketamine",
    "digoxin", "amiodarone",
    "methotrexate", "vincristine",
]

def is_high_alert(med_name: str) -> bool:
    med_lower = med_name.lower()
    return any(ha in med_lower for ha in HIGH_ALERT_MEDS)


# =============================================================================
# DEMO DATA
# =============================================================================

DEMO_PATIENT = {
    "name": "Johnson, Robert M",
    "mrn": "MRN: 123456789",
    "dob": "DOB: 03/15/1952 (72 y/o)",
    "room": "Room: 412-A",
    "attending": "Dr. Sarah Smith, Hospitalist",
    "code_status": "Full Code",
    "allergies": "PCN (rash), Sulfa (hives)",
    "admit_date": "Admitted: 01/11/2026",
    "diagnosis": "Community-Acquired Pneumonia, COPD Exacerbation",
    "pmh": ["Hypertension", "Type 2 Diabetes", "COPD", "Hyperlipidemia", "Former smoker (30 pack-years)"]
}

DEMO_MAR = """Metoprolol Tartrate 25 mg Tab  PO BID  08:00, 20:00
pantoprazole (PROTONIX) 40 mg Tab  PO Daily  09:00
Lisinopril 10 mg Tab  PO Daily  09:00
Metformin 500 mg Tab  PO BID  08:00, 20:00
Ceftriaxone 1 g IVPB  IV Q24H  14:00
Azithromycin 500 mg IVPB  IV Daily  14:00
Albuterol 2.5 mg/3mL Neb  INH Q4H PRN
Heparin 5,000 Units  SubQ BID  08:00, 20:00
Insulin Lispro (HUMALOG)  SubQ AC per sliding scale
Furosemide (LASIX) 40 mg Tab  PO Daily  09:00"""

DEMO_LABS = """Sodium       138      136-145 mEq/L
Potassium    3.2 L    3.5-5.0 mEq/L
Chloride     102      98-106 mEq/L
CO2          24       22-29 mEq/L
BUN          28 H     7-20 mg/dL
Creatinine   1.4 H    0.7-1.3 mg/dL
Glucose      186 H    70-100 mg/dL
Magnesium    1.6 L    1.7-2.2 mg/dL
Phosphorus   2.3 L    2.5-4.5 mg/dL
WBC          11.2 H   4.5-11.0 K/uL
Hemoglobin   10.8 L   12.0-16.0 g/dL
Hematocrit   32.4 L   36-46 %
Platelets    245      150-400 K/uL"""

DEMO_ABG = "pH: 7.32 L  pCO2: 52 H  HCO3: 26  PaO2: 72 L  SaO2: 93%"


# =============================================================================
# PATIENT SCENARIOS
# =============================================================================

PATIENT_SCENARIOS = {
    "respiratory_failure": {
        "name": "Martinez, Maria T",
        "mrn": "MRN: 987654321",
        "dob": "DOB: 07/22/1956 (68 y/o)",
        "room": "Room: ICU-4 → 512-A (Stepdown)",
        "attending": "Dr. James Chen, Pulmonology/Critical Care",
        "code_status": "Full Code",
        "allergies": "NKDA",
        "admit_date": "01/12/2026",
        "diagnosis": "Acute Hypoxic Respiratory Failure, COPD Exacerbation, CAP",
        "pmh": ["COPD (on home O2 2L)", "HTN", "Type 2 DM", "OSA on CPAP"],
        "current_status": "Day 3: Extubated, on high-flow nasal cannula, improving",
        "progress_notes": {
            "day_1": "Admission day - intubated for respiratory failure",
            "day_2": "ICU day 2 - weaning ventilator, improving ABGs",
            "day_3": "Extubation successful, transfer to stepdown"
        }
    },
    "chf_exacerbation": {
        "name": "Williams, James R",
        "mrn": "MRN: 456789123",
        "dob": "DOB: 11/30/1948 (77 y/o)",
        "room": "Room: 318-B",
        "attending": "Dr. Lisa Park, Cardiology",
        "code_status": "DNR/DNI",
        "allergies": "Lisinopril (cough), Morphine (nausea)",
        "admit_date": "01/13/2026",
        "diagnosis": "Acute on Chronic CHF Exacerbation, EF 25%",
        "pmh": ["CHF EF 25%", "AFib on Eliquis", "CKD Stage 3", "DM2"],
        "current_status": "Day 2: Responding to IV diuresis, I/O negative 2L",
        "progress_notes": {
            "day_1": "Admission - acute CHF, started IV Lasix",
            "day_2": "Good diuresis response, BNP trending down",
            "day_3": "Converting to PO diuretics, cardiology follow-up arranged"
        }
    },
    "post_op_hip": {
        "name": "Thompson, Dorothy A",
        "mrn": "MRN: 789123456",
        "dob": "DOB: 02/14/1940 (85 y/o)",
        "room": "Room: 425-A → SNF",
        "attending": "Dr. Michael Brown, Orthopedics",
        "code_status": "Full Code",
        "allergies": "Codeine (confusion)",
        "admit_date": "01/10/2026",
        "diagnosis": "S/P Right Total Hip Arthroplasty (Fall)",
        "pmh": ["Osteoporosis", "HTN", "Hypothyroidism", "Mild dementia"],
        "current_status": "POD 3: Ambulating with PT, discharge to SNF today",
        "progress_notes": {
            "day_1": "POD 1 - pain controlled, started PT",
            "day_2": "POD 2 - walked 100 feet with walker",
            "day_3": "POD 3 - discharge to SNF, home health arranged"
        }
    }
}


# =============================================================================
# LEARNING SESSION TRACKING
# =============================================================================

@dataclass
class LearningEntry:
    timestamp: str
    category: str
    query: str
    response_summary: str
    key_points: List[str]

@dataclass
class NurseSession:
    session_id: str
    start_time: str
    entries: List[LearningEntry] = field(default_factory=list)

    def add_entry(self, category: str, query: str, response: str, key_points: List[str] = None):
        entry = LearningEntry(
            timestamp=datetime.now().strftime("%H:%M"),
            category=category,
            query=query[:200],
            response_summary=response[:500] if len(response) > 500 else response,
            key_points=key_points or []
        )
        self.entries.append(entry)
        return entry

    def get_topic_counts(self) -> Dict[str, int]:
        return dict(Counter(e.category for e in self.entries))

    def format_history(self) -> str:
        if not self.entries:
            return "*No queries yet this session*"

        output = f"## Session History ({len(self.entries)} queries)\n\n"
        output += f"**Started:** {self.start_time}\n\n"

        counts = self.get_topic_counts()
        if counts:
            output += "**Topics:** " + ", ".join(f"{k}: {v}" for k, v in counts.items()) + "\n\n"

        for i, entry in enumerate(self.entries, 1):
            icon = {"medication": "💊", "lab": "🧪", "condition": "🏥", "procedure": "📋",
                    "handoff": "📝", "abg": "🫁", "other": "❓"}.get(entry.category, "📌")
            output += f"### {icon} {entry.timestamp} - {entry.category.title()}\n"
            output += f"**Query:** {entry.query}\n\n"

        return output

# Global session
current_session = NurseSession(
    session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
    start_time=datetime.now().strftime("%Y-%m-%d %H:%M")
)


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def get_patient_header():
    p = DEMO_PATIENT
    return f"""
## {p['name']}
**{p['mrn']}** | **{p['dob']}** | **{p['room']}**

| Field | Value |
|-------|-------|
| **Attending** | {p['attending']} |
| **Diagnosis** | {p['diagnosis']} |
| **Code Status** | {p['code_status']} |
| **Allergies** | {p['allergies']} |
"""

def generate_handoff(patient_info: str, format_type: str = "SBAR") -> str:
    query = f"Generate {format_type} handoff for:\n{patient_info}"
    return ask_medgemma("Nursing handoff assistant", query)

def explain_to_family(topic: str, topic_type: str = "diagnosis", audience: str = "family", context: str = "") -> str:
    query = f"Explain {topic} ({topic_type}) to {audience}. Context: {context}"
    return ask_medgemma("Family explainer", query)

def med_lookup(medication: str, query_type: str = "full") -> str:
    high_alert = is_high_alert(medication)
    query = f"Medication lookup: {medication} ({'HIGH-ALERT' if high_alert else 'standard'}) - {query_type}"
    return ask_medgemma("Medication assistant", query)

def interpret_lab(lab_data: str, context: str = "") -> str:
    query = f"Interpret labs:\n{lab_data}\nContext: {context}"
    return ask_medgemma("Lab interpreter", query)

def interpret_abg(abg_data: str) -> str:
    query = f"Interpret ABG:\n{abg_data}"
    return ask_medgemma("ABG interpreter", query)

def what_to_watch(condition: str) -> str:
    query = f"What to watch for with: {condition}"
    return ask_medgemma("Clinical monitor", query)


# =============================================================================
# UI WRAPPER FUNCTIONS
# =============================================================================

def epic_med_lookup(mar_line):
    if not mar_line:
        return "Please select a medication"
    med_name = mar_line.split()[0] if mar_line else ""
    current_session.add_entry("medication", mar_line, "", [])
    return med_lookup(med_name, "full")

def interpret_labs_from_paste(labs, context):
    if not labs.strip():
        return "Please paste lab results"
    current_session.add_entry("lab", labs[:100], "", [])
    return interpret_lab(labs, context)

def epic_abg_lookup():
    current_session.add_entry("abg", DEMO_ABG, "", [])
    return interpret_abg(DEMO_ABG)

def epic_full_workflow():
    return """## Electrolyte Workflow Complete

**Abnormal Values Identified:**
- Potassium 3.2 (LOW) - Replacement recommended
- Magnesium 1.6 (LOW) - Replace before K for better correction
- Phosphorus 2.3 (LOW) - Monitor, may need replacement

**Recommended Actions:**
1. Check telemetry for arrhythmias
2. Oral K replacement: KCl 40 mEq PO x1 (if tolerating PO)
3. Mag replacement: MgSO4 2g IV over 2 hours
4. Recheck lytes in 4-6 hours post-replacement
5. Review diuretic dosing with MD

**MD Communication Template:**
```
Dr. Smith - Re: Johnson, Robert (412-A)
Labs back - K 3.2, Mg 1.6, Phos 2.3
On Lasix 40mg daily
Recommend electrolyte replacement
Please advise on orders
```"""

def epic_handoff():
    return generate_handoff(f"""
{DEMO_PATIENT['name']}, {DEMO_PATIENT['room']}
{DEMO_PATIENT['diagnosis']}
PMH: {', '.join(DEMO_PATIENT['pmh'])}
Allergies: {DEMO_PATIENT['allergies']}
Current: On 2L NC, sats 94%, taking PO, WBC improving
""", "SBAR")

def epic_md_chat_from_labs():
    return """## MD Secure Chat Message

**To:** Dr. Sarah Smith, Hospitalist
**Re:** Johnson, Robert M (412-A) - Lab Results

Good morning Dr. Smith,

Following up on morning labs for Mr. Johnson:

**Concerns:**
- K: 3.2 (low) - patient on Lasix
- Mg: 1.6 (low)
- BUN/Cr: 28/1.4 (elevated from baseline)

**Current status:**
- Tolerating PO well
- O2 sats stable on 2L NC
- No arrhythmias on tele

**Request:**
Would you like to order electrolyte replacement? Also, should we hold Lasix today given the elevated creatinine?

Please advise. Thank you!
- RN (NurseGemma)"""


# =============================================================================
# SCENARIO HELPERS
# =============================================================================

def get_scenario_header(scenario_key):
    if scenario_key not in PATIENT_SCENARIOS:
        return "Select a patient scenario"
    p = PATIENT_SCENARIOS[scenario_key]
    return f"""
## {p['name']}
**{p['mrn']}** | **{p['dob']}** | **{p['room']}**

| Field | Value |
|-------|-------|
| **Attending** | {p['attending']} |
| **Admission Date** | {p['admit_date']} |
| **Diagnosis** | {p['diagnosis']} |
| **Code Status** | {p['code_status']} |
| **Allergies** | {p['allergies']} |

**PMH:** {', '.join(p['pmh'])}

---
### Current Status
{p['current_status']}
"""

def get_day_notes(scenario_key, day):
    if scenario_key not in PATIENT_SCENARIOS:
        return "Select a patient scenario"
    p = PATIENT_SCENARIOS[scenario_key]
    day_key = f"day_{day}"
    if day_key not in p['progress_notes']:
        return f"No notes for day {day}"
    return f"```\n{p['progress_notes'][day_key]}\n```"

def run_course_summary(scenario_key):
    if scenario_key not in PATIENT_SCENARIOS:
        return "Please select a patient scenario first"
    p = PATIENT_SCENARIOS[scenario_key]
    return f"""## Patient Course Summary: {p['name']}

**Diagnosis:** {p['diagnosis']}

**3-Day Summary:**
- **Day 1:** {p['progress_notes']['day_1']}
- **Day 2:** {p['progress_notes']['day_2']}
- **Day 3:** {p['progress_notes']['day_3']}

**Current Status:** {p['current_status']}

**Key Events:**
- Successfully managed acute presentation
- Appropriate treatment response
- Planning for next level of care

**Nursing Priorities:**
- Continue monitoring for complications
- Ensure discharge planning in progress
- Patient/family education complete
"""

def run_comprehensive_handoff(scenario_key, format_type):
    if scenario_key not in PATIENT_SCENARIOS:
        return "Please select a patient scenario first"
    p = PATIENT_SCENARIOS[scenario_key]
    return generate_handoff(f"{p['name']}\n{p['diagnosis']}\nPMH: {', '.join(p['pmh'])}", format_type)


# =============================================================================
# LEARNING HUB FUNCTIONS
# =============================================================================

def get_session_history():
    return current_session.format_history()

def clear_session():
    global current_session
    current_session = NurseSession(
        session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
        start_time=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    return "Session cleared! Starting fresh."

def generate_study_summary():
    if not current_session.entries:
        return "*No queries yet - start using NurseGemma to build your study guide!*"

    return f"""## Study Summary - {datetime.now().strftime('%Y-%m-%d')}

**Session Duration:** Started {current_session.start_time}
**Total Queries:** {len(current_session.entries)}
**Topics Covered:** {', '.join(current_session.get_topic_counts().keys())}

### Key Learning Points:

Based on your queries today, here are the main topics to review:

1. **Medication Safety** - High-alert medications, double-checks
2. **Lab Interpretation** - Electrolyte management, critical values
3. **Clinical Assessment** - ABG interpretation, respiratory status

### Recommended Review:
- Review facility protocols for high-alert medications
- Practice ABG interpretation using the tic-tac-toe method
- Understand electrolyte replacement guidelines
"""

def generate_flash_cards():
    if not current_session.entries:
        return "*No queries yet - use NurseGemma to generate flashcards from your questions!*"

    return """## Flashcards from Today's Session

### Card 1: Hypokalemia
**Q:** What potassium level requires replacement?
**A:** Generally K < 3.5 mEq/L; critical if < 3.0 mEq/L

### Card 2: High-Alert Meds
**Q:** What's required before giving heparin?
**A:** Independent double-check by 2 RNs, verify PTT, check for bleeding signs

### Card 3: ABG Interpretation
**Q:** pH 7.32, pCO2 52 - What's the primary disorder?
**A:** Respiratory acidosis (low pH + high CO2)

### Card 4: SBAR
**Q:** What does SBAR stand for?
**A:** Situation, Background, Assessment, Recommendation
"""

def get_knowledge_gaps():
    counts = current_session.get_topic_counts()
    if not counts:
        return "*Build your learning profile by using NurseGemma throughout your shift!*"

    return f"""## Your Learning Profile

**Topics You've Explored:**
{chr(10).join(f'- {k}: {v} queries' for k, v in counts.items())}

**Suggested Areas to Explore:**
- Procedure guides (step-by-step clinical procedures)
- Patient education (teaching points for common conditions)
- Emergency protocols (rapid response, code documentation)

**Strength Areas:**
Based on your queries, you're building knowledge in: {', '.join(counts.keys())}

**Growth Opportunities:**
Consider exploring more about wound assessment and pain management protocols.
"""


# =============================================================================
# WORKFLOW FUNCTIONS
# =============================================================================

def run_admission_workflow_ui(patient_data):
    if not patient_data.strip():
        return "Please enter patient information"

    return f"""## Agentic Workflow Complete: New Admission

**Steps completed:** 4

---

### Monitoring Guide
{what_to_watch(patient_data[:100])}

---

### Medication Review
Review all medications for:
- Drug interactions
- High-alert medications
- Nursing considerations

---

### Family Explanation
{explain_to_family("new admission", "diagnosis", "family", patient_data[:100])}

---

### Shift Handoff
{generate_handoff(patient_data, "SBAR")}
"""

def run_electrolyte_workflow_ui(labs, context):
    if not labs.strip():
        return "Please paste lab results from EPIC"
    return epic_full_workflow()


# =============================================================================
# LOGGED FUNCTIONS (for Learning Hub)
# =============================================================================

def med_lookup_logged(med, query_type):
    current_session.add_entry("medication", med, "", [])
    return med_lookup(med, query_type)

def interpret_labs_logged(labs, context):
    current_session.add_entry("lab", labs[:100], "", [])
    return interpret_lab(labs, context)

def interpret_abg_logged(abg):
    current_session.add_entry("abg", abg, "", [])
    return interpret_abg(abg)

def generate_handoff_logged(info, fmt):
    current_session.add_entry("handoff", info[:100], "", [])
    return generate_handoff(info, fmt)

def explain_condition_logged(topic, topic_type, audience, context):
    current_session.add_entry("condition", topic, "", [])
    return explain_to_family(topic, topic_type, audience, context)

def generate_secure_chat(situation, data, request, patient_id):
    return f"""**MD Secure Chat Message**

**To:** Attending Physician
**Re:** {patient_id} - Clinical Update

**Situation:**
{situation}

**Data:**
{data}

**Request:**
{request}

Please advise. Thank you!
- RN"""


# =============================================================================
# BUILD GRADIO UI
# =============================================================================

def build_ui():
    with gr.Blocks(title="NurseGemma - AI Companion for Nurses", theme=gr.themes.Soft(), css="""
        .patient-header { background-color: #1e3a5f; color: white; padding: 10px; border-radius: 5px; }
        .learning-hub { background-color: #f0f7ff; padding: 15px; border-radius: 8px; }
    """) as demo:

        gr.Markdown("""# NurseGemma
        ### AI Companion for Nurses | Built by a nurse, for nurses
        *Powered by MedGemma 1.5 | Learn as you work*

        **TEST MODE:** Using mock responses for UI validation
        """)

        with gr.Tabs():
            # =================================================================
            # TAB 1: EPIC DEMO
            # =================================================================
            with gr.Tab("EPIC Demo"):
                gr.Markdown("""### Live Patient Chart Demo
                This simulates working with a real EPIC patient chart.
                """)

                gr.Markdown(get_patient_header())

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Patient Data (Simulated EPIC)")

                        with gr.Accordion("MAR", open=True):
                            gr.Markdown(f"```\n{DEMO_MAR}\n```")
                            mar_select = gr.Dropdown(
                                choices=DEMO_MAR.strip().split('\n'),
                                label="Select medication",
                                value=DEMO_MAR.strip().split('\n')[0]
                            )
                            mar_btn = gr.Button("Explain Med", variant="primary")

                        with gr.Accordion("Labs", open=True):
                            gr.Markdown(f"```\n{DEMO_LABS}\n```")
                            lab_btn = gr.Button("Interpret Labs", variant="primary")

                        with gr.Accordion("ABG", open=False):
                            gr.Markdown(f"```\n{DEMO_ABG}\n```")
                            abg_btn = gr.Button("Interpret ABG", variant="primary")

                    with gr.Column(scale=1):
                        gr.Markdown("### NurseGemma Response")
                        epic_output = gr.Markdown(value="*Click a button to analyze*")

                gr.Markdown("---")
                with gr.Row():
                    workflow_btn = gr.Button("Electrolyte Workflow", variant="primary", size="lg")
                    handoff_btn = gr.Button("SBAR Handoff", variant="secondary", size="lg")
                    md_btn = gr.Button("MD Chat", variant="secondary", size="lg")

                workflow_output = gr.Markdown(value="")

                mar_btn.click(epic_med_lookup, mar_select, epic_output)
                lab_btn.click(lambda: interpret_labs_from_paste(DEMO_LABS, "CHF, COPD, DM2"), None, epic_output)
                abg_btn.click(epic_abg_lookup, None, epic_output)
                workflow_btn.click(epic_full_workflow, None, workflow_output)
                handoff_btn.click(epic_handoff, None, workflow_output)
                md_btn.click(epic_md_chat_from_labs, None, workflow_output)

            # =================================================================
            # TAB 2: PATIENT COURSE
            # =================================================================
            with gr.Tab("Patient Course"):
                gr.Markdown("""### 3-Day Hospital Course Demo
                View full hospital courses and generate comprehensive handoffs.
                """)

                scenario_select = gr.Dropdown(
                    choices=[
                        ("Respiratory Failure - ICU Course", "respiratory_failure"),
                        ("CHF Exacerbation - Diuresis", "chf_exacerbation"),
                        ("Post-Op Hip - Rehab to SNF", "post_op_hip")
                    ],
                    label="Select Patient Scenario",
                    value="respiratory_failure"
                )

                scenario_header = gr.Markdown(value="")
                scenario_select.change(get_scenario_header, scenario_select, scenario_header)

                gr.Markdown("### Progress Notes")
                with gr.Row():
                    with gr.Column():
                        with gr.Accordion("Day 1 - Admission", open=True):
                            day1_btn = gr.Button("View Notes", variant="secondary")
                            day1_output = gr.Markdown()
                            day1_btn.click(lambda s: get_day_notes(s, 1), scenario_select, day1_output)

                        with gr.Accordion("Day 2 - Course", open=False):
                            day2_btn = gr.Button("View Notes", variant="secondary")
                            day2_output = gr.Markdown()
                            day2_btn.click(lambda s: get_day_notes(s, 2), scenario_select, day2_output)

                        with gr.Accordion("Day 3 - Transition", open=False):
                            day3_btn = gr.Button("View Notes", variant="secondary")
                            day3_output = gr.Markdown()
                            day3_btn.click(lambda s: get_day_notes(s, 3), scenario_select, day3_output)

                gr.Markdown("---")
                with gr.Row():
                    summary_btn = gr.Button("Course Summary", variant="primary", size="lg")
                    handoff_format = gr.Dropdown(choices=["SBAR", "I-PASS"], value="SBAR", label="Format")
                    course_handoff_btn = gr.Button("Full Handoff", variant="primary", size="lg")

                course_output = gr.Markdown()
                summary_btn.click(run_course_summary, scenario_select, course_output)
                course_handoff_btn.click(run_comprehensive_handoff, [scenario_select, handoff_format], course_output)

            # =================================================================
            # TAB 3: LEARNING HUB
            # =================================================================
            with gr.Tab("Learning Hub"):
                gr.Markdown("""### Your Learning Companion

                NurseGemma tracks your queries and helps you learn! Every question becomes a study opportunity.
                """)

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Session History")
                        refresh_history_btn = gr.Button("Refresh History", variant="secondary")
                        history_display = gr.Markdown(value="*Click refresh to see your session history*")
                        refresh_history_btn.click(get_session_history, None, history_display)

                        clear_btn = gr.Button("Clear Session", variant="secondary")
                        clear_output = gr.Markdown()
                        clear_btn.click(clear_session, None, clear_output)

                    with gr.Column(scale=1):
                        gr.Markdown("### Study Tools")

                        with gr.Accordion("What I Learned Today", open=True):
                            study_btn = gr.Button("Generate Study Summary", variant="primary")
                            study_output = gr.Markdown()
                            study_btn.click(generate_study_summary, None, study_output)

                        with gr.Accordion("Flashcards", open=False):
                            flash_btn = gr.Button("Generate Flashcards", variant="primary")
                            flash_output = gr.Markdown()
                            flash_btn.click(generate_flash_cards, None, flash_output)

                        with gr.Accordion("Knowledge Gaps", open=False):
                            gaps_btn = gr.Button("Analyze My Learning", variant="primary")
                            gaps_output = gr.Markdown()
                            gaps_btn.click(get_knowledge_gaps, None, gaps_output)

            # =================================================================
            # TAB 4: COPY/PASTE
            # =================================================================
            with gr.Tab("Copy/Paste"):
                gr.Markdown("### Copy from YOUR EPIC → Paste → Learn")

                with gr.Accordion("MAR", open=True):
                    mar_input = gr.Textbox(label="Paste from EPIC MAR", lines=4)
                    mar_paste_btn = gr.Button("Explain", variant="primary")
                    mar_paste_output = gr.Markdown()
                    mar_paste_btn.click(
                        lambda x: (med_lookup_logged(x, "full") if x.strip() else "Enter medication"),
                        mar_input, mar_paste_output
                    )

                with gr.Accordion("Labs", open=False):
                    lab_paste_input = gr.Textbox(label="Paste Labs", lines=6)
                    lab_paste_ctx = gr.Textbox(label="Context", placeholder="CHF, CKD...")
                    lab_paste_btn = gr.Button("Interpret", variant="primary")
                    lab_paste_output = gr.Markdown()
                    lab_paste_btn.click(interpret_labs_logged, [lab_paste_input, lab_paste_ctx], lab_paste_output)

                with gr.Accordion("ABG", open=False):
                    abg_paste_input = gr.Textbox(label="Paste ABG", lines=2)
                    abg_paste_btn = gr.Button("Interpret", variant="primary")
                    abg_paste_output = gr.Markdown()
                    abg_paste_btn.click(interpret_abg_logged, abg_paste_input, abg_paste_output)

                with gr.Accordion("MD Secure Chat", open=False):
                    chat_sit = gr.Textbox(label="Situation")
                    chat_data = gr.Textbox(label="Data")
                    chat_req = gr.Textbox(label="Request")
                    chat_pt = gr.Textbox(label="Patient ID")
                    chat_btn = gr.Button("Generate", variant="primary")
                    chat_out = gr.Textbox(label="Message", lines=6)
                    chat_btn.click(generate_secure_chat, [chat_sit, chat_data, chat_req, chat_pt], chat_out)

            # =================================================================
            # TAB 5: WORKFLOWS
            # =================================================================
            with gr.Tab("Workflows"):
                gr.Markdown("### Multi-Step Agentic Workflows")

                with gr.Accordion("Electrolyte Remediation", open=True):
                    elec_input = gr.Textbox(label="Paste Labs", lines=6)
                    elec_ctx = gr.Textbox(label="Context")
                    elec_btn = gr.Button("Run", variant="primary")
                    elec_out = gr.Markdown()
                    elec_btn.click(run_electrolyte_workflow_ui, [elec_input, elec_ctx], elec_out)

                with gr.Accordion("New Admission", open=False):
                    adm_in = gr.Textbox(label="Patient Info", lines=8)
                    adm_btn = gr.Button("Run", variant="primary")
                    adm_out = gr.Markdown()
                    adm_btn.click(run_admission_workflow_ui, adm_in, adm_out)

            # =================================================================
            # TAB 6: TOOLS
            # =================================================================
            with gr.Tab("Tools"):
                gr.Markdown("### Individual Tools")

                with gr.Tabs():
                    with gr.Tab("Handoff"):
                        ho_info = gr.Textbox(label="Patient Info", lines=10)
                        ho_fmt = gr.Dropdown(choices=["SBAR", "I-PASS", "Quick"], value="SBAR")
                        ho_btn = gr.Button("Generate", variant="primary")
                        ho_out = gr.Textbox(label="Handoff", lines=20)
                        ho_btn.click(generate_handoff_logged, [ho_info, ho_fmt], ho_out)

                    with gr.Tab("Family Explain"):
                        ex_topic = gr.Textbox(label="Topic")
                        ex_type = gr.Dropdown(choices=["diagnosis", "procedure", "medication"], value="diagnosis")
                        ex_aud = gr.Dropdown(choices=["family", "patient", "elderly_patient"], value="family")
                        ex_ctx = gr.Textbox(label="Context")
                        ex_btn = gr.Button("Explain", variant="primary")
                        ex_out = gr.Textbox(label="Explanation", lines=15)
                        ex_btn.click(explain_condition_logged, [ex_topic, ex_type, ex_aud, ex_ctx], ex_out)

                    with gr.Tab("Med Lookup"):
                        med_n = gr.Textbox(label="Medication")
                        med_t = gr.Dropdown(choices=["full", "quick", "teaching"], value="full")
                        med_b = gr.Button("Look Up", variant="primary")
                        med_o = gr.Textbox(label="Info", lines=15)
                        med_b.click(med_lookup_logged, [med_n, med_t], med_o)

        gr.Markdown("""---
        ### MedGemma Impact Challenge

        **NurseGemma** - Not just an AI tool, a **learning companion**:
        - EPIC-native copy/paste workflow
        - 10+ specialized nursing tools
        - Multi-step agentic workflows
        - **Learning Hub** - Every query becomes a study opportunity

        *Educational purposes only. Verify with facility protocols.*

        **Created by AIHeartICU | ICU Nurse**
        """)

    return demo


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("NurseGemma UI Test")
    print("="*60)
    print("\nStarting Gradio interface...")
    print("TEST MODE: Using mock MedGemma responses\n")

    demo = build_ui()
    demo.queue()

    # Find available port
    import socket
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    port = find_free_port()
    print(f"Using port: {port}")

    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True
    )
