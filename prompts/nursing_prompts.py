"""
Nursing-Specific Prompt Templates for Nurse Companion
These prompts are optimized for MedGemma to provide nursing-focused responses
"""

# ==================== QUICK EXPLAIN PROMPTS ====================

EXPLAIN_FOR_FAMILY = """You are explaining {condition} to a worried family member.

Guidelines:
- Use {reading_level} reading level language
- Be compassionate but accurate
- Use everyday analogies when helpful
- Avoid medical jargon or explain it immediately
- Keep it concise (3-4 paragraphs max)

Explain:
1. What {condition} means in simple terms
2. Why this is happening or what caused it
3. What the treatment involves
4. What to expect going forward
5. Reassuring points (if medically appropriate)

{additional_context}"""

EXPLAIN_FOR_PATIENT = """You are a nurse explaining {condition} directly to the patient.

Guidelines:
- Speak directly to the patient ("you" language)
- Be warm but professional
- Use {reading_level} reading level
- Acknowledge their feelings
- Empower them with knowledge

Include:
1. What is happening with your body
2. Why we're doing what we're doing
3. What you might feel or experience
4. What you can do to help your recovery
5. Questions you might want to ask your doctor

{additional_context}"""

EXPLAIN_PROCEDURE = """The patient/family needs to understand what will happen during: {procedure}

Use {reading_level} reading level and explain:
1. What this procedure is for
2. What will happen step by step (in simple terms)
3. What the patient will feel during it
4. How long it takes
5. What to expect after
6. Any prep they need to do
7. Reassuring information about safety

{additional_context}"""

# ==================== MED HELPER PROMPTS ====================

MED_INFO_NURSING = """Provide nursing-focused information about: {medication}

Format your response as:

## What is {medication}?
[Simple explanation of what it's for]

## How It's Given
[Route, timing, special considerations]

## What to Monitor
[Key assessments and vitals to watch]

## Side Effects to Watch For
[Common and serious side effects]

## Patient Teaching
[What to tell the patient in simple terms]

## Nursing Pearls
[Practical tips for administration]

{patient_context}"""

DRUG_INTERACTION_CHECK = """Check for interactions between these medications:
{medication_list}

For each interaction found, provide:
1. **Drugs involved**:
2. **What happens**:
3. **Severity**: (Minor/Moderate/Major)
4. **What to monitor**:
5. **Action needed**:

If no significant interactions found, state that clearly.

Always note: Verify with pharmacy for patient-specific concerns.

{patient_context}"""

IV_COMPATIBILITY = """Check IV compatibility for:
{medications}

Include:
1. Are these Y-site compatible?
2. Are they compatible in the same bag?
3. Any special considerations for mixing/timing?
4. Recommended flushing between medications

Note: Always verify with current compatibility references and pharmacy."""

# ==================== SHIFT SIDEKICK PROMPTS ====================

SBAR_TEMPLATE = """Generate a nursing SBAR handoff report from this information:

{patient_info}

Format as:

## SITUATION
- Patient identification
- Reason for admission
- Current status in one sentence

## BACKGROUND
- Relevant medical history
- Current treatment plan
- Recent changes/events

## ASSESSMENT
- Current nursing assessment
- Areas of concern
- Trends (improving/stable/declining)

## RECOMMENDATION
- Priority actions for next shift
- Pending orders/tasks
- Follow-up needed
- When to notify provider

---
**CRITICAL ALERTS:**
[Any red flags or urgent items]

**PENDING TASKS:**
[Checklist of outstanding items]"""

QUICK_HANDOFF = """Create a brief 2-minute handoff summary:

{patient_info}

Format:
**In a nutshell:** [One sentence summary]

**Key points:**
- Diagnosis:
- Current status:
- Critical meds/treatments:
- What to watch:
- Pending:"""

SHIFT_NOTES_SUMMARY = """Summarize these shift notes into key points:

{notes}

Provide:
1. **Events Summary**: What happened this shift
2. **Current Status**: Where the patient is now
3. **Changes**: Any changes from previous shift
4. **Action Items**: What needs follow-up
5. **Communication**: What was communicated to providers"""

# ==================== CLINICAL QUICK REF PROMPTS ====================

LAB_INTERPRETATION = """Interpret this lab result:

Lab: {lab_name}
Value: {value} {unit}
{patient_context}

Provide:
1. **Normal Range**:
2. **This Value**: (Normal/High/Low and by how much)
3. **Clinical Meaning**: What this could indicate
4. **Assessment Focus**: What to assess related to this
5. **Notify Provider If**: When this needs escalation
6. **Nursing Actions**: What to do about it"""

PROCEDURE_GUIDE = """Nursing guide for: {procedure}

## Supplies Needed
[List of supplies]

## Patient Preparation
[How to prepare patient and environment]

## Step-by-Step
1. [Steps with nursing tips]

## Common Issues
- Problem → Solution

## Documentation
- What to document

## Post-Procedure
- What to monitor after

**Note: Verify with facility-specific protocols**"""

CONDITION_MONITORING = """Monitoring guide for patient with: {condition}

## Key Assessments
[What to assess and how often]

## Vital Sign Considerations
[Specific VS to watch and target ranges]

## Signs of Improvement
[What getting better looks like]

## Warning Signs (Red Flags)
[When to be concerned]

## Escalation Criteria
[When to call provider/rapid response]

## Common Complications
[What might go wrong and early signs]

## Patient Teaching
[What to teach the patient]"""

# ==================== PATIENT EDUCATION PROMPTS ====================

PATIENT_EDUCATION_DISCHARGE = """Create discharge teaching for a patient with: {condition}

Use {reading_level} reading level.

Include:
1. What is your condition (simple terms)
2. Medications to take at home
3. Warning signs - when to call doctor
4. Warning signs - when to go to ER
5. Activity and diet guidelines
6. Follow-up appointments
7. Resources and support"""

MED_TEACHING = """Create patient medication teaching for: {medication}

Reading level: {reading_level}

Include:
1. What this medicine is for
2. How to take it
3. When to take it
4. Side effects to watch for
5. What to avoid while taking it
6. When to call the doctor
7. Tips to remember to take it"""

# ==================== EMERGENCY REFERENCE ====================

EMERGENCY_REF = """Provide quick reference for: {emergency_type}

Format for rapid bedside use:
- Recognition signs
- Immediate actions
- Who to call
- Key meds/doses (if applicable)
- Documentation needs

This is for reference only. Follow ACLS/facility protocols."""

# ==================== UTILITY FUNCTIONS ====================

def get_prompt(prompt_type: str, **kwargs) -> str:
    """Get a formatted prompt template"""
    prompts = {
        "explain_family": EXPLAIN_FOR_FAMILY,
        "explain_patient": EXPLAIN_FOR_PATIENT,
        "explain_procedure": EXPLAIN_PROCEDURE,
        "med_info": MED_INFO_NURSING,
        "drug_interaction": DRUG_INTERACTION_CHECK,
        "iv_compat": IV_COMPATIBILITY,
        "sbar": SBAR_TEMPLATE,
        "quick_handoff": QUICK_HANDOFF,
        "shift_summary": SHIFT_NOTES_SUMMARY,
        "lab_interp": LAB_INTERPRETATION,
        "procedure": PROCEDURE_GUIDE,
        "monitoring": CONDITION_MONITORING,
        "discharge": PATIENT_EDUCATION_DISCHARGE,
        "med_teaching": MED_TEACHING,
        "emergency": EMERGENCY_REF,
    }

    template = prompts.get(prompt_type)
    if template:
        return template.format(**kwargs)
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")


# Reading level adjustments
READING_LEVEL_GUIDANCE = {
    "child": "Use very simple words a 10-year-old would understand. Short sentences. No medical words without explanation.",
    "basic": "Use everyday language an 8th grader would understand. Explain medical terms when used.",
    "standard": "Use clear language a high school graduate would understand. Brief explanations of medical terms.",
    "advanced": "Use standard health literacy language. Can include common medical terms with context.",
}
