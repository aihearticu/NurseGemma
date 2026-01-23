"""
Demo Scenarios for NurseGemma Competition Presentation

Pre-built demo scripts that showcase NurseGemma's capabilities:
1. Busy Morning - Lab analysis and time savings
2. Worried Family - Plain language explanations
3. Critical Lab - Safety catches
4. Shift Handoff - Complete SBAR generation
5. Pain Management - Allergy awareness

Each scenario is designed to be impressive in 30 seconds or less.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DemoScenario:
    """A complete demo scenario for competition presentation"""
    name: str
    title: str
    setup_narration: str
    patient_key: str
    demo_action: str
    expected_highlight: str
    time_comparison: str
    clinical_value: str


# ==================== DEMO SCENARIOS ====================

DEMO_SCENARIOS = {
    "busy_morning": DemoScenario(
        name="busy_morning",
        title="Busy Morning - Lab Analysis",
        setup_narration="""
It's 7am. You have 4 patients. Mrs. Johnson's labs just came back.
You need to review them quickly before the MD rounds at 8am.
        """,
        patient_key="mrs_johnson",
        demo_action="Paste lab values and click 'Analyze Labs'",
        expected_highlight="""
NurseGemma immediately flags:
- Potassium 3.2 (LOW) with patient on Lasix + Digoxin
- BUN/Cr elevated suggesting renal involvement
- Suggests: "Monitor for arrhythmia risk, consider K+ replacement"
        """,
        time_comparison="Manual review: 10 minutes | NurseGemma: 12 seconds",
        clinical_value="Caught the dangerous K+/Digoxin combination that could cause arrhythmia",
    ),

    "worried_family": DemoScenario(
        name="worried_family",
        title="Worried Family - CHF Explanation",
        setup_narration="""
Mrs. Johnson's daughter arrives. She's anxious and asks:
"The doctor said CHF. What does that mean? Is mom going to be okay?"
You need to explain clearly without medical jargon.
        """,
        patient_key="mrs_johnson",
        demo_action="Ask NurseGemma to explain CHF at 8th grade reading level",
        expected_highlight="""
NurseGemma generates:
"CHF means your mom's heart isn't pumping as strongly as it should.
Think of the heart like a pump - right now it's working harder but
not moving fluid as efficiently. That's why she has extra fluid in
her lungs making it hard to breathe. The good news is we have
medicines that help the heart work better and reduce that extra fluid."
        """,
        time_comparison="Composing explanation: 3 minutes | NurseGemma: 8 seconds",
        clinical_value="Family understands diagnosis, reduces anxiety, builds trust",
    ),

    "critical_lab": DemoScenario(
        name="critical_lab",
        title="Critical Lab - DKA Management",
        setup_narration="""
Ms. Rodriguez is in the ICU with DKA. New labs just resulted.
Glucose is improving (428→298) but you need to watch potassium
as insulin drives K+ into cells.
        """,
        patient_key="ms_rodriguez",
        demo_action="Run Critical Lab Response workflow",
        expected_highlight="""
NurseGemma's multi-step analysis:
1. Parses all lab values
2. Identifies: K+ 5.8 (HIGH) - but will DROP as DKA resolves
3. Flags: "Anticipate K+ replacement needed when < 5.0"
4. Suggests: Continue insulin drip, monitor K+ Q2H
5. Generates MD update: "Gap closing, glucose improving, K+ trending"
        """,
        time_comparison="Full analysis: 8 minutes | NurseGemma: 15 seconds",
        clinical_value="Proactive K+ monitoring prevents dangerous hypokalemia",
    ),

    "shift_handoff": DemoScenario(
        name="shift_handoff",
        title="Shift Handoff - Complete SBAR",
        setup_narration="""
End of a 12-hour shift. Mr. Smith has been stable - pneumonia improving,
WBC trending down, ambulated with PT. You need to hand off to night shift
but you're exhausted and don't want to miss anything.
        """,
        patient_key="mr_smith",
        demo_action="Click 'Generate SBAR Handoff'",
        expected_highlight="""
NurseGemma generates complete SBAR:

**SITUATION**: 72M Day 3 pneumonia, stable, improving

**BACKGROUND**: CAP on Ceftriaxone/Azithro Day 3, COPD history

**ASSESSMENT**:
- WBC 11.2 (down from 14.6) - improving
- On 2L NC, sats 94-96%
- Tolerating diet, ambulated with PT

**RECOMMENDATION**:
- Continue antibiotics, may discuss step-down tomorrow
- PT/OT daily
- Watch: O2 needs if increased activity
- Pending: Blood cultures final read
        """,
        time_comparison="Writing handoff: 12 minutes | NurseGemma: 10 seconds",
        clinical_value="Nothing missed, next shift has complete picture",
    ),

    "pain_management": DemoScenario(
        name="pain_management",
        title="Pain Management - Allergy Awareness",
        setup_narration="""
Mr. Chen is POD#2 from hip surgery. Pain is 6/10 and he needs
something stronger. But wait - he has allergies to Morphine and Codeine.
What can you give safely?
        """,
        patient_key="mr_chen",
        demo_action="Run Medication Safety workflow with current MAR",
        expected_highlight="""
NurseGemma's safety analysis:
1. Flags: Morphine ALLERGY - cannot give
2. Flags: Codeine ALLERGY - cannot give
3. Notes: Hydromorphone ordered (0.5mg IV) - SAFE alternative
4. Notes: Oxycodone ordered (5mg PO) - SAFE alternative
5. Recommends: "Use hydromorphone for breakthrough, Oxycodone for oral transition"
6. Reminds: "Monitor for constipation - bowel regimen in place"
        """,
        time_comparison="Checking allergies + alternatives: 5 minutes | NurseGemma: 8 seconds",
        clinical_value="Prevents allergic reaction, identifies safe alternatives",
    ),

    "md_communication": DemoScenario(
        name="md_communication",
        title="MD Communication - SBAR Page",
        setup_narration="""
Mrs. Johnson's BP dropped to 92/58 and HR to 52. She's on Metoprolol
and Lisinopril. You need to page the cardiologist but want to sound
professional and include all relevant info.
        """,
        patient_key="mrs_johnson",
        demo_action="Enter 'BP dropped, should we hold meds?' and click Compose Message",
        expected_highlight="""
NurseGemma composes:

📱 URGENT - PAGE TO: Dr. Smith (Cardiology)
RE: Mrs. Johnson, Room 412 - Hypotension Concern

SITUATION: BP dropped to 92/58 (was 128/76 this AM), HR 52

PERTINENT DATA:
• Current meds: Lisinopril 10mg, Metoprolol 25mg
• AM Labs: K+ 3.2 (low), Cr 1.4
• I/O: -800mL this shift (on Lasix)
• No chest pain, no dizziness

REQUEST: Hold Lisinopril and Metoprolol for now?

Please advise. Thank you!
— RN, CCU
        """,
        time_comparison="Composing page: 4 minutes | NurseGemma: 6 seconds",
        clinical_value="Professional, complete SBAR gets faster MD response",
    ),
}


# ==================== DEMO SCRIPT ====================

COMPETITION_DEMO_SCRIPT = """
## NurseGemma Competition Demo Script

### Opening (30 seconds)
"As an ICU nurse, I spend 40% of my shift documenting instead of caring for patients.
In those precious moments at bedside, families ask me to explain what doctors said.
I built NurseGemma to change that."

### Problem Statement (45 seconds)
- Show stat: "79% of nurses lose time to unproductive charting"
- Show stat: "40% of shift on documentation"
- Show stat: "100,000 nurses left the profession in 2 years"
- Quote: "Documentation has ruined nursing" - AllNurses.com

### Demo 1: Busy Morning (60 seconds)
- Load Mrs. Johnson in EPIC-style UI
- Show her labs with low K+
- Click "Analyze Labs"
- NurseGemma flags K+/Digoxin concern
- "12 seconds instead of 10 minutes"

### Demo 2: Worried Family (45 seconds)
- Same patient, daughter arrives
- Ask: "Explain CHF at 8th grade level"
- NurseGemma generates compassionate explanation
- "Ready for the bedside in 8 seconds"

### Demo 3: Critical Lab (45 seconds)
- Switch to Ms. Rodriguez (DKA)
- Run Critical Lab workflow
- Show 5-step analysis completing
- "Caught the K+ trajectory before it became dangerous"

### Demo 4: Shift Handoff (45 seconds)
- Switch to Mr. Smith (improving pneumonia)
- Click "Generate SBAR"
- Complete handoff appears
- "Nothing missed, night shift has everything"

### Closing (30 seconds)
"30 seconds instead of 15 minutes. That's time back at the bedside.
That's better patient outcomes. That's why NurseGemma matters.
Built by a nurse, for nurses."

### Technical Highlight (20 seconds)
- MedGemma 1.5 4B - runs on free tier
- Agentic workflows chain 5 reasoning steps
- Safety-first: ISMP high-alert medication checks
- Works offline after model load

---
Total demo time: ~5 minutes
"""


def get_scenario(name: str) -> DemoScenario:
    """Get a demo scenario by name"""
    return DEMO_SCENARIOS.get(name)


def list_scenarios() -> List[str]:
    """List all available scenarios"""
    return [
        f"{s.name}: {s.title}"
        for s in DEMO_SCENARIOS.values()
    ]


def run_demo_scenario(scenario_name: str, companion=None, agent=None) -> Dict:
    """
    Run a complete demo scenario

    Args:
        scenario_name: Name of the scenario to run
        companion: NurseCompanion instance
        agent: AgenticNurse instance

    Returns:
        Dict with demo results
    """
    from sample_patients import SAMPLE_PATIENTS
    from agentic_workflows import WorkflowType

    scenario = DEMO_SCENARIOS.get(scenario_name)
    if not scenario:
        return {"error": f"Unknown scenario: {scenario_name}"}

    patient = SAMPLE_PATIENTS.get(scenario.patient_key)
    if not patient:
        return {"error": f"Unknown patient: {scenario.patient_key}"}

    result = {
        "scenario": scenario.title,
        "patient": patient.name,
        "setup": scenario.setup_narration.strip(),
        "action": scenario.demo_action,
        "time_comparison": scenario.time_comparison,
        "clinical_value": scenario.clinical_value,
    }

    # Run the appropriate workflow if agent is available
    if agent:
        if "lab" in scenario_name.lower():
            lab_text = "\n".join([f"{l.name}: {l.value}{l.unit}" for l in patient.labs])
            workflow_result = agent.run_workflow(WorkflowType.CRITICAL_LAB, lab_text)
            result["ai_output"] = workflow_result.final_output
            result["time_saved"] = workflow_result.time_saved_seconds

        elif "handoff" in scenario_name.lower():
            notes_text = "\n".join(patient.nursing_notes)
            workflow_result = agent.run_workflow(WorkflowType.SHIFT_HANDOFF, notes_text)
            result["ai_output"] = workflow_result.final_output
            result["time_saved"] = workflow_result.time_saved_seconds

        elif "medication" in scenario_name.lower() or "pain" in scenario_name.lower():
            med_text = "\n".join([f"{m.name} {m.dose}" for m in patient.medications])
            workflow_result = agent.run_workflow(
                WorkflowType.MEDICATION_SAFETY,
                med_text,
                {"allergies": patient.allergies}
            )
            result["ai_output"] = workflow_result.final_output
            result["time_saved"] = workflow_result.time_saved_seconds

        elif "md" in scenario_name.lower() or "communication" in scenario_name.lower():
            workflow_result = agent.run_workflow(
                WorkflowType.MD_COMMUNICATION,
                "BP dropped to 92/58, HR 52. Should we hold the beta blocker?",
                {"patient": patient.name}
            )
            result["ai_output"] = workflow_result.final_output
            result["time_saved"] = workflow_result.time_saved_seconds

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("NurseGemma Demo Scenarios")
    print("=" * 60)
    print()
    print("Available scenarios:")
    for name, scenario in DEMO_SCENARIOS.items():
        print(f"  {name}: {scenario.title}")
    print()
    print("Demo script:")
    print(COMPETITION_DEMO_SCRIPT[:500] + "...")
