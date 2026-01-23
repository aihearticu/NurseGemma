"""
Agentic Workflows for NurseGemma
Multi-step clinical reasoning workflows that chain MedGemma calls autonomously.

Built BY a nurse, FOR nurses - reducing documentation burden one workflow at a time.

Research shows:
- 79% of nurses lose time to unproductive charting (KLAS)
- 40% of shift spent on documentation (U.S. Surgeon General)
- 32 minutes saved per nurse per day is achievable (Mercy Health)

These workflows turn 15-minute tasks into 30-second automations.
"""

import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class WorkflowType(Enum):
    """Types of agentic workflows available"""
    ADMISSION = "admission"
    CRITICAL_LAB = "critical_lab"
    SHIFT_HANDOFF = "shift_handoff"
    MEDICATION_SAFETY = "medication_safety"
    MD_COMMUNICATION = "md_communication"


class Priority(Enum):
    """Clinical priority levels"""
    ROUTINE = "routine"
    ATTENTION = "attention"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class WorkflowStep:
    """A single step in an agentic workflow"""
    name: str
    description: str
    prompt_template: str
    depends_on: List[str] = field(default_factory=list)
    required: bool = True


@dataclass
class WorkflowResult:
    """Result from executing a workflow"""
    workflow_type: str
    success: bool
    steps_completed: List[str]
    step_results: Dict[str, str]
    final_output: str
    priority: Priority
    execution_time_seconds: float
    estimated_manual_time_seconds: float
    time_saved_seconds: float
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# High-alert medications (ISMP list)
HIGH_ALERT_MEDICATIONS = [
    "heparin", "enoxaparin", "warfarin", "apixaban", "rivaroxaban", "dabigatran",  # Anticoagulants
    "insulin", "lispro", "aspart", "glargine", "regular insulin", "nph",  # Insulin
    "morphine", "hydromorphone", "fentanyl", "oxycodone", "methadone",  # Opioids
    "potassium chloride", "kcl", "magnesium sulfate",  # Electrolytes IV
    "digoxin", "amiodarone", "lidocaine",  # Cardiac
    "epinephrine", "norepinephrine", "dopamine", "dobutamine", "vasopressin",  # Vasopressors
    "propofol", "midazolam", "lorazepam", "ketamine",  # Sedatives
    "rocuronium", "vecuronium", "succinylcholine",  # Paralytics
    "methotrexate", "vincristine", "doxorubicin",  # Chemotherapy
]

# Critical lab value thresholds
CRITICAL_VALUES = {
    "potassium": {"low": 2.5, "high": 6.5, "unit": "mEq/L"},
    "sodium": {"low": 120, "high": 160, "unit": "mEq/L"},
    "glucose": {"low": 50, "high": 500, "unit": "mg/dL"},
    "hemoglobin": {"low": 7.0, "high": None, "unit": "g/dL"},
    "platelets": {"low": 50000, "high": None, "unit": "/uL"},
    "wbc": {"low": 2000, "high": 30000, "unit": "/uL"},
    "creatinine": {"low": None, "high": 4.0, "unit": "mg/dL"},
    "troponin": {"low": None, "high": 0.04, "unit": "ng/mL"},
    "lactate": {"low": None, "high": 4.0, "unit": "mmol/L"},
}


class AgenticNurse:
    """
    Agentic AI that chains clinical reasoning steps autonomously.

    Transforms complex nursing tasks into one-click workflows:
    - Analyzes patient data across multiple dimensions
    - Flags safety concerns proactively
    - Generates complete documentation
    - Saves 30+ minutes per shift
    """

    def __init__(self, companion=None):
        """
        Initialize Agentic Nurse

        Args:
            companion: NurseCompanion instance with loaded model
        """
        self.companion = companion
        self._define_workflows()

    def _define_workflows(self):
        """Define all available agentic workflows"""
        self.workflows = {
            WorkflowType.ADMISSION: self._get_admission_workflow(),
            WorkflowType.CRITICAL_LAB: self._get_critical_lab_workflow(),
            WorkflowType.SHIFT_HANDOFF: self._get_shift_handoff_workflow(),
            WorkflowType.MEDICATION_SAFETY: self._get_medication_safety_workflow(),
            WorkflowType.MD_COMMUNICATION: self._get_md_communication_workflow(),
        }

        # Estimated manual times in seconds (based on nursing research)
        self.manual_times = {
            WorkflowType.ADMISSION: 900,  # 15 minutes
            WorkflowType.CRITICAL_LAB: 600,  # 10 minutes
            WorkflowType.SHIFT_HANDOFF: 720,  # 12 minutes
            WorkflowType.MEDICATION_SAFETY: 480,  # 8 minutes
            WorkflowType.MD_COMMUNICATION: 300,  # 5 minutes
        }

    def _get_admission_workflow(self) -> List[WorkflowStep]:
        """Define Smart Admission Workflow steps"""
        return [
            WorkflowStep(
                name="parse_patient_data",
                description="Parse and organize admission data",
                prompt_template="""Analyze this admission data and extract key information:

{input_data}

Extract and organize:
1. Demographics (age, sex, allergies)
2. Chief complaint and diagnosis
3. Vital signs
4. Current medications
5. Relevant history
6. Any immediate concerns

Format as structured summary."""
            ),
            WorkflowStep(
                name="medication_analysis",
                description="Analyze medications for safety concerns",
                prompt_template="""Based on this patient data:
{parse_patient_data}

Analyze the medication list for:
1. High-alert medications that require extra vigilance
2. Potential drug-drug interactions
3. Dose appropriateness (considering age, weight, renal function if known)
4. Any medications that need special monitoring

List any SAFETY CONCERNS prominently at the top.""",
                depends_on=["parse_patient_data"]
            ),
            WorkflowStep(
                name="assessment_priorities",
                description="Generate assessment priorities for this patient",
                prompt_template="""Based on the patient summary:
{parse_patient_data}

And medication analysis:
{medication_analysis}

Generate nursing assessment priorities:
1. What systems/areas need closest monitoring?
2. Key assessments to perform immediately
3. Baseline data to establish
4. Anticipated complications to watch for
5. Fall risk and safety considerations

Prioritize by clinical urgency.""",
                depends_on=["parse_patient_data", "medication_analysis"]
            ),
            WorkflowStep(
                name="family_education",
                description="Generate family-friendly explanation",
                prompt_template="""Using the patient information:
{parse_patient_data}

Create a family-friendly explanation (8th grade reading level) that covers:
1. What brought the patient to the hospital (in simple terms)
2. What the care team is doing to help
3. What family members might see (monitors, IV, etc.)
4. How they can help the patient
5. Questions they might want to ask the doctor

Use compassionate language and helpful analogies.""",
                depends_on=["parse_patient_data"]
            ),
            WorkflowStep(
                name="sbar_handoff",
                description="Generate SBAR for initial handoff",
                prompt_template="""Using all gathered information:

Patient Data: {parse_patient_data}
Medication Analysis: {medication_analysis}
Assessment Priorities: {assessment_priorities}

Generate a complete SBAR handoff report:

**SITUATION**
Current patient status and reason for admission

**BACKGROUND**
Relevant history and context

**ASSESSMENT**
Key concerns and nursing assessment

**RECOMMENDATION**
Immediate priorities and monitoring plan

Include:
- Critical tasks pending
- Key medications and timing
- What to watch for""",
                depends_on=["parse_patient_data", "medication_analysis", "assessment_priorities"]
            ),
        ]

    def _get_critical_lab_workflow(self) -> List[WorkflowStep]:
        """Define Critical Lab Response Workflow steps"""
        return [
            WorkflowStep(
                name="parse_labs",
                description="Parse and categorize lab values",
                prompt_template="""Parse these lab values and categorize each:

{input_data}

For each lab value:
1. Value and unit
2. Normal range
3. Status: CRITICAL / HIGH / LOW / NORMAL
4. Clinical significance

Sort by severity with CRITICAL values first."""
            ),
            WorkflowStep(
                name="prioritize_concerns",
                description="Prioritize by clinical severity",
                prompt_template="""Based on these lab results:
{parse_labs}

Prioritize the abnormal values:
1. CRITICAL - Requires immediate action/notification
2. URGENT - Needs attention within the hour
3. MONITOR - Track and reassess
4. NOTE - Mildly abnormal, document and observe

For each, explain WHY this priority level.""",
                depends_on=["parse_labs"]
            ),
            WorkflowStep(
                name="check_combinations",
                description="Check for dangerous combinations",
                prompt_template="""Given these lab priorities:
{prioritize_concerns}

And patient context (if available): {patient_context}

Check for dangerous combinations:
1. Low K+ with Digoxin = arrhythmia risk
2. High K+ with renal failure = cardiac risk
3. Low Na+ with diuretics = electrolyte emergency
4. Elevated lactate with low BP = sepsis concern
5. Rising creatinine with nephrotoxic drugs

Flag any dangerous combinations found.""",
                depends_on=["prioritize_concerns"]
            ),
            WorkflowStep(
                name="nursing_interventions",
                description="Suggest nursing interventions",
                prompt_template="""Based on lab analysis:
{prioritize_concerns}

And combinations checked:
{check_combinations}

Suggest nursing interventions for each concern:
1. Assessment actions (what to evaluate)
2. Monitoring frequency
3. Potential treatments to anticipate
4. Documentation requirements
5. Safety measures

Be specific and actionable.""",
                depends_on=["prioritize_concerns", "check_combinations"]
            ),
            WorkflowStep(
                name="md_notification",
                description="Generate MD notification if needed",
                prompt_template="""Based on lab analysis:
{prioritize_concerns}
{check_combinations}

If any CRITICAL or URGENT values exist, draft an MD notification:

Format for SBAR page/secure chat:
SITUATION: [Lab concern with value]
BACKGROUND: [Relevant patient context]
ASSESSMENT: [What you think is happening]
REQUEST: [What you need from the provider]

Suggest urgency level: ROUTINE / URGENT / STAT

If no notification needed, state "No immediate notification required" and explain why.""",
                depends_on=["prioritize_concerns", "check_combinations"]
            ),
        ]

    def _get_shift_handoff_workflow(self) -> List[WorkflowStep]:
        """Define Shift Handoff Generator Workflow steps"""
        return [
            WorkflowStep(
                name="extract_events",
                description="Extract key events from shift notes",
                prompt_template="""Extract key events from these shift notes:

{input_data}

Identify:
1. Significant events (changes, procedures, incidents)
2. Medication changes or new orders
3. Patient/family interactions
4. Provider communications
5. Any concerns or near-misses

List chronologically with times if available."""
            ),
            WorkflowStep(
                name="identify_trends",
                description="Identify trending concerns",
                prompt_template="""Based on shift events:
{extract_events}

Identify any trends:
1. Vital sign patterns (stable, improving, concerning)
2. Lab value trajectories
3. Pain/comfort trends
4. Mental status changes
5. Overall clinical trajectory

Mark trends as: IMPROVING / STABLE / CONCERNING""",
                depends_on=["extract_events"]
            ),
            WorkflowStep(
                name="pending_tasks",
                description="Compile pending tasks",
                prompt_template="""From the shift events:
{extract_events}

Compile outstanding tasks:
1. Medications due (with times)
2. Assessments needed
3. Consults pending
4. Tests/procedures scheduled
5. Follow-ups required
6. Patient education not yet completed

Mark each with priority: CRITICAL / IMPORTANT / ROUTINE""",
                depends_on=["extract_events"]
            ),
            WorkflowStep(
                name="generate_sbar",
                description="Generate complete SBAR handoff",
                prompt_template="""Using all gathered information:

Events: {extract_events}
Trends: {identify_trends}
Pending: {pending_tasks}

Generate a complete SBAR handoff:

**SITUATION**
Current patient status and any acute issues

**BACKGROUND**
Admission reason, relevant history, and this shift's context

**ASSESSMENT**
Nursing assessment, concerns, and trend analysis

**RECOMMENDATION**
What the next shift should prioritize

Format clearly for quick handoff.""",
                depends_on=["extract_events", "identify_trends", "pending_tasks"]
            ),
            WorkflowStep(
                name="what_to_watch",
                description="Generate what to watch summary",
                prompt_template="""Based on the shift summary:
{generate_sbar}

Create a "WHAT TO WATCH" quick reference:

1. Top 3 concerns for next shift
2. Specific parameters to monitor (values, thresholds)
3. Signs of improvement to look for
4. Red flags that need escalation
5. Time-sensitive tasks (with deadlines)

Keep it scannable - bullet points only.""",
                depends_on=["generate_sbar"]
            ),
        ]

    def _get_medication_safety_workflow(self) -> List[WorkflowStep]:
        """Define Medication Safety Check Workflow steps"""
        return [
            WorkflowStep(
                name="parse_mar",
                description="Parse Medication Administration Record",
                prompt_template="""Parse this medication list/MAR:

{input_data}

For each medication extract:
1. Medication name (generic and brand if given)
2. Dose and route
3. Frequency
4. Last given time (if available)
5. Next due time (if available)

Flag any that appear on the high-alert medication list."""
            ),
            WorkflowStep(
                name="identify_high_alert",
                description="Identify high-alert medications",
                prompt_template="""From this medication list:
{parse_mar}

Identify HIGH-ALERT medications (ISMP list):
- Anticoagulants (heparin, warfarin, enoxaparin, DOACs)
- Insulin (all types)
- Opioids (morphine, fentanyl, hydromorphone)
- IV electrolytes (potassium chloride, magnesium)
- Vasopressors/inotropes
- Chemotherapy agents
- Sedatives/paralytics

For each high-alert med found, list:
1. Why it's high-alert
2. Special monitoring required
3. Safety checks before administration""",
                depends_on=["parse_mar"]
            ),
            WorkflowStep(
                name="check_interactions",
                description="Check drug-drug interactions",
                prompt_template="""Check for interactions between these medications:
{parse_mar}

Identify:
1. Significant drug-drug interactions
2. Severity: MAJOR / MODERATE / MINOR
3. Clinical effect of interaction
4. Monitoring required
5. Nursing actions to take

Also check for therapeutic duplications.""",
                depends_on=["parse_mar"]
            ),
            WorkflowStep(
                name="verify_doses",
                description="Verify dose appropriateness",
                prompt_template="""Verify dose appropriateness for:
{parse_mar}

Patient context: {patient_context}

Check:
1. Standard dose ranges for each medication
2. Renal/hepatic adjustments if applicable
3. Age-related considerations
4. Weight-based dosing (if applicable)
5. Max daily dose limits

Flag any doses that seem:
- Too high
- Too low
- Need adjustment""",
                depends_on=["parse_mar"]
            ),
            WorkflowStep(
                name="nursing_considerations",
                description="Generate nursing considerations",
                prompt_template="""Based on medication analysis:

High-Alert: {identify_high_alert}
Interactions: {check_interactions}
Dose Verification: {verify_doses}

Generate nursing considerations:

For each medication category:
1. Key monitoring parameters
2. Timing considerations
3. Administration tips
4. Patient teaching points
5. What to document

Highlight any SAFETY ALERTS prominently.""",
                depends_on=["identify_high_alert", "check_interactions", "verify_doses"]
            ),
        ]

    def _get_md_communication_workflow(self) -> List[WorkflowStep]:
        """Define MD Communication Helper Workflow steps"""
        return [
            WorkflowStep(
                name="identify_request",
                description="Clarify what you need from the MD",
                prompt_template="""The nurse needs to communicate with the MD about:

{input_data}

Clarify the communication:
1. What is the specific request/question?
2. What decision is needed from the MD?
3. What is the urgency level? (ROUTINE/URGENT/STAT)
4. What response format is needed? (order, answer, consult)"""
            ),
            WorkflowStep(
                name="gather_relevant_data",
                description="Gather clinically relevant data",
                prompt_template="""For this MD communication:
{identify_request}

With patient context: {patient_context}

Gather relevant data to include:
1. Current vital signs
2. Relevant lab values
3. Pertinent medications
4. Recent changes/events
5. Current interventions

Include PERTINENT NEGATIVES (what's NOT present that might be expected).""",
                depends_on=["identify_request"]
            ),
            WorkflowStep(
                name="structure_sbar",
                description="Structure message in SBAR format",
                prompt_template="""Using:
Request: {identify_request}
Data: {gather_relevant_data}

Structure the communication in SBAR format:

**SITUATION** (2-3 sentences max)
What is happening right now that prompted this call

**BACKGROUND** (brief, relevant only)
Pertinent history and current context

**ASSESSMENT** (your clinical thinking)
What you think is happening

**REQUEST** (clear and specific)
What you need from the MD

Keep it concise - MDs appreciate brevity.""",
                depends_on=["identify_request", "gather_relevant_data"]
            ),
            WorkflowStep(
                name="suggest_urgency",
                description="Recommend urgency and channel",
                prompt_template="""Based on this communication:
{structure_sbar}

Recommend:
1. Urgency Level: ROUTINE / URGENT / STAT
2. Communication Channel: Secure Chat / Page / Phone Call
3. Response needed within: [timeframe]
4. Escalation plan if no response

Explain your urgency recommendation briefly.""",
                depends_on=["structure_sbar"]
            ),
            WorkflowStep(
                name="format_message",
                description="Format final message ready to send",
                prompt_template="""Create the final message based on:

SBAR Content:
{structure_sbar}

Urgency Assessment:
{suggest_urgency}

Format as a copy-paste ready message:
---
[URGENCY LEVEL] - [CHANNEL]
TO: Dr. [Name] ([Specialty])
RE: [Patient Name], Room [X] - [Brief Topic]

SITUATION: [1-2 sentences]
BACKGROUND: [Key history]
ASSESSMENT: [Your clinical thinking]
REQUEST: [What you need]

Please advise. Thank you!
— RN, [Unit]
---

Make it professional and ready to send.""",
                depends_on=["structure_sbar", "suggest_urgency"]
            ),
        ]

    def run_workflow(
        self,
        workflow_type: WorkflowType,
        input_data: str,
        patient_context: Optional[Dict] = None
    ) -> WorkflowResult:
        """
        Execute a multi-step agentic workflow

        Args:
            workflow_type: Type of workflow to run
            input_data: Initial input data for the workflow
            patient_context: Optional patient context dictionary

        Returns:
            WorkflowResult with all step outputs and final result
        """
        start_time = time.time()

        # Get workflow steps
        steps = self.workflows.get(workflow_type, [])
        if not steps:
            return WorkflowResult(
                workflow_type=workflow_type.value,
                success=False,
                steps_completed=[],
                step_results={},
                final_output="Unknown workflow type",
                priority=Priority.ROUTINE,
                execution_time_seconds=0,
                estimated_manual_time_seconds=0,
                time_saved_seconds=0,
                errors=["Unknown workflow type"]
            )

        # Execute steps
        step_results = {"input_data": input_data}
        if patient_context:
            step_results["patient_context"] = str(patient_context)
        else:
            step_results["patient_context"] = "No additional patient context provided."

        steps_completed = []
        warnings = []
        errors = []

        for step in steps:
            try:
                # Check dependencies
                for dep in step.depends_on:
                    if dep not in step_results:
                        raise ValueError(f"Missing dependency: {dep}")

                # Build prompt with context
                prompt = step.prompt_template.format(**step_results)

                # Generate response
                if self.companion:
                    result = self.companion._generate_response(
                        system_prompt=self._get_workflow_system_prompt(workflow_type),
                        user_message=prompt,
                        max_new_tokens=800,
                        temperature=0.7
                    )
                else:
                    # Mock response for testing without model
                    result = f"[Step: {step.name}] Analysis complete. (Mock response - model not loaded)"

                step_results[step.name] = result
                steps_completed.append(step.name)

                # Check for safety concerns
                safety_check = self._check_safety_flags(result)
                if safety_check:
                    warnings.extend(safety_check)

            except Exception as e:
                error_msg = f"Step {step.name} failed: {str(e)}"
                errors.append(error_msg)
                if step.required:
                    break

        # Calculate timing
        execution_time = time.time() - start_time
        manual_time = self.manual_times.get(workflow_type, 600)
        time_saved = manual_time - execution_time

        # Determine priority from warnings
        priority = self._determine_priority(warnings, step_results)

        # Get final output (last step result)
        final_output = step_results.get(steps[-1].name, "Workflow incomplete")

        # Add time savings footer
        final_output += f"\n\n---\n"
        final_output += f"Completed in {execution_time:.1f} seconds\n"
        final_output += f"Estimated manual time: {manual_time/60:.0f} minutes\n"
        final_output += f"TIME SAVED: {time_saved/60:.1f} minutes"

        return WorkflowResult(
            workflow_type=workflow_type.value,
            success=len(errors) == 0,
            steps_completed=steps_completed,
            step_results=step_results,
            final_output=final_output,
            priority=priority,
            execution_time_seconds=execution_time,
            estimated_manual_time_seconds=manual_time,
            time_saved_seconds=time_saved,
            warnings=warnings,
            errors=errors
        )

    def _get_workflow_system_prompt(self, workflow_type: WorkflowType) -> str:
        """Get system prompt for workflow type"""
        base_prompt = """You are NurseGemma, an AI nursing assistant built BY a nurse, FOR nurses.

Your role is to help reduce documentation burden and support clinical decision-making.
You are part of a multi-step workflow that chains reasoning together.

Guidelines:
- Be accurate and evidence-based
- Flag safety concerns prominently
- Use nursing-focused language
- Be concise but thorough
- Always recommend verifying with facility protocols

IMPORTANT: This is for educational purposes only. Do not substitute for professional clinical judgment."""

        workflow_additions = {
            WorkflowType.ADMISSION: "\n\nYou are processing a new admission. Focus on identifying key concerns and establishing baseline.",
            WorkflowType.CRITICAL_LAB: "\n\nYou are analyzing lab values. Prioritize by clinical urgency and flag critical values.",
            WorkflowType.SHIFT_HANDOFF: "\n\nYou are generating a shift handoff. Be thorough but concise - this needs to be scannable.",
            WorkflowType.MEDICATION_SAFETY: "\n\nYou are performing a medication safety check. Flag all high-alert medications and interactions.",
            WorkflowType.MD_COMMUNICATION: "\n\nYou are helping compose an MD communication. Be professional, concise, and SBAR-formatted.",
        }

        return base_prompt + workflow_additions.get(workflow_type, "")

    def _check_safety_flags(self, text: str) -> List[str]:
        """Check text for safety-related keywords and return warnings"""
        warnings = []
        text_lower = text.lower()

        # Check for high-alert medications
        for med in HIGH_ALERT_MEDICATIONS:
            if med.lower() in text_lower:
                warnings.append(f"HIGH-ALERT MEDICATION: {med}")

        # Check for critical keywords
        critical_keywords = ["critical", "emergency", "stat", "urgent", "immediately", "life-threatening"]
        for keyword in critical_keywords:
            if keyword in text_lower:
                warnings.append(f"CRITICAL FLAG: '{keyword}' mentioned")
                break  # Only flag once

        return warnings

    def _determine_priority(self, warnings: List[str], step_results: Dict) -> Priority:
        """Determine overall priority based on warnings and results"""
        # Check for critical indicators
        all_text = " ".join(str(v) for v in step_results.values()).lower()

        if "critical" in all_text or "stat" in all_text or "immediately" in all_text:
            return Priority.CRITICAL
        elif len([w for w in warnings if "HIGH-ALERT" in w]) > 0:
            return Priority.URGENT
        elif "urgent" in all_text or len(warnings) > 2:
            return Priority.ATTENTION
        else:
            return Priority.ROUTINE


# ==================== QUICK ACCESS FUNCTIONS ====================

def quick_admission(companion, admission_data: str, patient_context: Optional[Dict] = None) -> WorkflowResult:
    """One-click admission workflow"""
    agent = AgenticNurse(companion)
    return agent.run_workflow(WorkflowType.ADMISSION, admission_data, patient_context)


def quick_lab_response(companion, lab_values: str, patient_context: Optional[Dict] = None) -> WorkflowResult:
    """One-click critical lab response workflow"""
    agent = AgenticNurse(companion)
    return agent.run_workflow(WorkflowType.CRITICAL_LAB, lab_values, patient_context)


def quick_handoff(companion, shift_notes: str, patient_context: Optional[Dict] = None) -> WorkflowResult:
    """One-click shift handoff workflow"""
    agent = AgenticNurse(companion)
    return agent.run_workflow(WorkflowType.SHIFT_HANDOFF, shift_notes, patient_context)


def quick_med_safety(companion, medications: str, patient_context: Optional[Dict] = None) -> WorkflowResult:
    """One-click medication safety workflow"""
    agent = AgenticNurse(companion)
    return agent.run_workflow(WorkflowType.MEDICATION_SAFETY, medications, patient_context)


def quick_md_message(companion, request: str, patient_context: Optional[Dict] = None) -> WorkflowResult:
    """One-click MD communication workflow"""
    agent = AgenticNurse(companion)
    return agent.run_workflow(WorkflowType.MD_COMMUNICATION, request, patient_context)


# ==================== DEMO DATA ====================

DEMO_ADMISSION_DATA = """
68 y/o female, Mary Johnson
Chief complaint: Shortness of breath, worsening over 3 days
History: CHF (EF 35%), HTN, Type 2 DM, CKD Stage 3
Allergies: Penicillin (rash)

Vitals on admission:
- BP: 168/92
- HR: 102
- RR: 24
- O2 Sat: 89% on RA (92% on 2L NC)
- Temp: 98.6F

Current Medications:
- Metoprolol 25mg PO BID
- Lisinopril 10mg PO daily
- Furosemide 40mg PO BID
- Digoxin 0.125mg PO daily
- Metformin 500mg PO BID
- Aspirin 81mg PO daily

Labs pending. CXR shows pulmonary edema.
Cardiology consult ordered.
"""

DEMO_LAB_VALUES = """
BMP Results (collected 0600):
- Sodium: 138 mEq/L
- Potassium: 3.2 mEq/L
- Chloride: 102 mEq/L
- CO2: 24 mEq/L
- BUN: 28 mg/dL
- Creatinine: 1.8 mg/dL
- Glucose: 186 mg/dL

CBC:
- WBC: 11.2
- Hemoglobin: 10.2
- Platelets: 198

Patient is on Digoxin and Lasix.
"""


if __name__ == "__main__":
    print("=" * 60)
    print("NurseGemma Agentic Workflows")
    print("Built BY a nurse, FOR nurses")
    print("=" * 60)
    print()
    print("Available workflows:")
    for wf in WorkflowType:
        print(f"  - {wf.value}")
    print()
    print("Usage:")
    print("  from agentic_workflows import AgenticNurse, WorkflowType")
    print("  agent = AgenticNurse(companion)")
    print("  result = agent.run_workflow(WorkflowType.ADMISSION, admission_data)")
    print()
    print("Or use quick functions:")
    print("  result = quick_admission(companion, admission_data)")
    print("  result = quick_lab_response(companion, lab_values)")
    print("  result = quick_handoff(companion, shift_notes)")
    print("  result = quick_med_safety(companion, medications)")
    print("  result = quick_md_message(companion, request)")
