"""
Nurse Companion - AI Assistant for Nurses
Built with MedGemma for the MedGemma Impact Challenge

Modules:
1. Quick Explain - Medical jargon to plain English
2. Med Helper - Medication information and interactions
3. Shift Sidekick - SBAR handoff report generation
4. Clinical Quick Ref - Lab values, procedures, assessments
5. Assessment Scales - GCS, NIHSS, Braden, NEWS2, Fall Risk, Pain
6. Nursing Calculations - Drip rates, dose calculations, clinical formulas
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Optional torch import for local testing
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None


class ReadingLevel(Enum):
    """Reading level for patient explanations"""
    CHILD = "5th grade"
    BASIC = "8th grade"
    STANDARD = "high school"
    ADVANCED = "college"


@dataclass
class PatientContext:
    """Context about the patient for personalized responses"""
    age: Optional[int] = None
    primary_diagnosis: Optional[str] = None
    current_medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    language_preference: str = "English"
    reading_level: ReadingLevel = ReadingLevel.BASIC


class NurseCompanion:
    """Main Nurse Companion AI Assistant"""

    def __init__(self, model=None, processor=None):
        """
        Initialize Nurse Companion

        Args:
            model: Pre-loaded MedGemma model (optional, will load if None)
            processor: Pre-loaded processor (optional, will load if None)
        """
        self.model = model
        self.processor = processor
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"

        # System prompts for each module
        self.system_prompts = {
            "quick_explain": self._get_quick_explain_prompt(),
            "med_helper": self._get_med_helper_prompt(),
            "shift_sidekick": self._get_shift_sidekick_prompt(),
            "clinical_ref": self._get_clinical_ref_prompt(),
        }

    def _get_quick_explain_prompt(self) -> str:
        return """You are a helpful nursing assistant specialized in patient and family communication.
Your role is to explain medical terms, diagnoses, and procedures in simple, easy-to-understand language.

Guidelines:
- Use plain language appropriate for the specified reading level
- Avoid medical jargon unless explaining it
- Use analogies and comparisons to everyday things
- Be compassionate and reassuring while remaining accurate
- Keep explanations concise but complete
- If something is serious, be honest but gentle
- Suggest follow-up questions the patient might want to ask their doctor"""

    def _get_med_helper_prompt(self) -> str:
        return """You are a medication information assistant for nurses.
Your role is to provide nursing-focused medication information including:
- What the medication is used for (in plain terms)
- Common side effects to monitor
- Key nursing considerations for administration
- Patient teaching points
- Drug interactions when asked

Guidelines:
- Focus on practical nursing information, not pharmacology textbook details
- Highlight what nurses need to watch for
- Provide patient teaching points in simple language
- Always recommend checking with pharmacy for specific patient questions
- Note any high-alert medication considerations"""

    def _get_shift_sidekick_prompt(self) -> str:
        return """You are a nursing handoff assistant that helps generate SBAR reports.

SBAR Format:
- Situation: What is happening with the patient right now?
- Background: What is the clinical context/history?
- Assessment: What do you think the problem is?
- Recommendation: What needs to be done?

Guidelines:
- Be concise but thorough
- Highlight critical information prominently
- Include pending tasks and follow-ups
- Note any changes from previous shift
- Flag any concerning trends or findings"""

    def _get_clinical_ref_prompt(self) -> str:
        return """You are a clinical reference assistant for nurses.
Your role is to provide quick, accurate clinical information including:
- Normal lab value ranges and interpretation
- Procedure steps and reminders
- Assessment findings and what they indicate
- Clinical pathways and protocols
- Emergency reference information

Guidelines:
- Be accurate and evidence-based
- Provide context for when values are concerning
- Give practical bedside tips
- Always recommend verifying with unit protocols
- Flag emergency situations clearly"""

    def load_model(self, model_id: str = "google/medgemma-1.5-4b-it"):
        """Load MedGemma model and processor"""
        from transformers import AutoProcessor, AutoModelForImageTextToText

        print(f"Loading {model_id}...")
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        print(f"Model loaded on {self.device}")
        return self

    def _generate_response(
        self,
        system_prompt: str,
        user_message: str,
        max_new_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Generate response from MedGemma"""

        messages = [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": user_message}]},
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.model.device, dtype=torch.bfloat16)

        input_len = inputs["input_ids"].shape[-1]

        with torch.inference_mode():
            generation = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
            )
            generation = generation[0][input_len:]

        return self.processor.decode(generation, skip_special_tokens=True)

    # ==================== MODULE 1: QUICK EXPLAIN ====================

    def quick_explain(
        self,
        term_or_condition: str,
        reading_level: ReadingLevel = ReadingLevel.BASIC,
        context: Optional[str] = None,
        for_family: bool = True,
    ) -> str:
        """
        Explain medical terms in plain language

        Args:
            term_or_condition: Medical term, diagnosis, or procedure to explain
            reading_level: Target reading level for explanation
            context: Additional context about the situation
            for_family: If True, frame for family; if False, for patient directly

        Returns:
            Plain language explanation
        """
        audience = "a worried family member" if for_family else "the patient directly"

        user_message = f"""Please explain the following medical term/condition to {audience}.
Use a {reading_level.value} reading level.

Term/Condition: {term_or_condition}

{"Additional context: " + context if context else ""}

Provide:
1. A simple explanation of what this means
2. Why this might be happening or why it's being done
3. What they can expect
4. Any reassuring points (if appropriate)
5. Questions they might want to ask the doctor"""

        return self._generate_response(
            self.system_prompts["quick_explain"],
            user_message,
            max_new_tokens=600
        )

    # ==================== MODULE 2: MED HELPER ====================

    def med_info(
        self,
        medication: str,
        include_interactions: bool = False,
        patient_context: Optional[PatientContext] = None,
    ) -> str:
        """
        Get nursing-focused medication information

        Args:
            medication: Medication name (generic or brand)
            include_interactions: Whether to include drug interaction info
            patient_context: Optional patient context for personalized info

        Returns:
            Medication information formatted for nurses
        """
        context_str = ""
        if patient_context and patient_context.current_medications:
            context_str = f"\nCurrent medications: {', '.join(patient_context.current_medications)}"
        if patient_context and patient_context.allergies:
            context_str += f"\nKnown allergies: {', '.join(patient_context.allergies)}"

        user_message = f"""Provide nursing-focused information about: {medication}
{context_str}

Please include:
1. What is this medication used for? (plain language)
2. Common side effects to monitor
3. Key nursing considerations for administration
4. Patient teaching points (in simple language for patient education)
{"5. Potential drug interactions to watch for" if include_interactions else ""}

Format clearly with sections."""

        return self._generate_response(
            self.system_prompts["med_helper"],
            user_message,
            max_new_tokens=700
        )

    def check_interactions(
        self,
        medications: List[str],
        patient_context: Optional[PatientContext] = None,
    ) -> str:
        """
        Check for drug-drug interactions

        Args:
            medications: List of medications to check
            patient_context: Optional patient context

        Returns:
            Interaction report
        """
        context_str = ""
        if patient_context and patient_context.allergies:
            context_str = f"\nKnown allergies: {', '.join(patient_context.allergies)}"

        user_message = f"""Please check for potential drug interactions between these medications:
{', '.join(medications)}
{context_str}

For each significant interaction found:
1. Which drugs interact
2. What is the interaction (what happens)
3. Clinical significance (mild/moderate/severe)
4. What to monitor
5. Nursing actions to take

If no significant interactions, state that clearly but remind to verify with pharmacy."""

        return self._generate_response(
            self.system_prompts["med_helper"],
            user_message,
            max_new_tokens=800
        )

    # ==================== MODULE 3: SHIFT SIDEKICK ====================

    def generate_sbar(
        self,
        patient_info: str,
        format_style: str = "standard",
    ) -> str:
        """
        Generate SBAR handoff report

        Args:
            patient_info: Raw patient information/notes
            format_style: "standard", "detailed", or "brief"

        Returns:
            Formatted SBAR report
        """
        format_instructions = {
            "standard": "Use standard SBAR format with complete sections",
            "detailed": "Use detailed SBAR with subsections and comprehensive information",
            "brief": "Use brief SBAR, highlight only critical points for quick handoff"
        }

        user_message = f"""Generate a nursing shift handoff report in SBAR format from this information:

{patient_info}

Instructions: {format_instructions.get(format_style, format_instructions['standard'])}

Format as:
**SITUATION**
[Current state]

**BACKGROUND**
[Relevant history and context]

**ASSESSMENT**
[Nursing assessment and concerns]

**RECOMMENDATION**
[What needs to happen next shift]

Also include:
- Critical tasks pending
- Changes from last shift
- Concerning trends to watch"""

        return self._generate_response(
            self.system_prompts["shift_sidekick"],
            user_message,
            max_new_tokens=1000
        )

    def shift_summary(
        self,
        notes: str,
        focus_areas: Optional[List[str]] = None,
    ) -> str:
        """
        Generate brief shift summary from notes

        Args:
            notes: Shift notes or events
            focus_areas: Specific areas to highlight

        Returns:
            Concise shift summary
        """
        focus_str = ""
        if focus_areas:
            focus_str = f"\nPay special attention to: {', '.join(focus_areas)}"

        user_message = f"""Create a concise shift summary from these notes:

{notes}
{focus_str}

Include:
1. Key events this shift
2. Current patient status
3. Changes in condition
4. Outstanding tasks
5. Critical follow-ups needed"""

        return self._generate_response(
            self.system_prompts["shift_sidekick"],
            user_message,
            max_new_tokens=500
        )

    # ==================== MODULE 4: CLINICAL QUICK REF ====================

    def interpret_lab(
        self,
        lab_name: str,
        value: float,
        unit: str,
        patient_context: Optional[PatientContext] = None,
    ) -> str:
        """
        Interpret lab value with clinical context

        Args:
            lab_name: Name of the lab test
            value: The lab value
            unit: Unit of measurement
            patient_context: Optional patient context

        Returns:
            Clinical interpretation
        """
        context_str = ""
        if patient_context:
            if patient_context.primary_diagnosis:
                context_str += f"\nDiagnosis: {patient_context.primary_diagnosis}"
            if patient_context.age:
                context_str += f"\nAge: {patient_context.age}"

        user_message = f"""Interpret this lab value for nursing assessment:

Lab: {lab_name}
Value: {value} {unit}
{context_str}

Please provide:
1. Normal range for this lab
2. Is this value normal, high, or low?
3. What this value might indicate clinically
4. What to assess/monitor related to this value
5. When to notify the provider
6. Any nursing interventions to consider"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=500
        )

    def procedure_reminder(
        self,
        procedure: str,
        detail_level: str = "standard",
    ) -> str:
        """
        Get procedure steps and reminders

        Args:
            procedure: Name of the procedure
            detail_level: "brief", "standard", or "detailed"

        Returns:
            Procedure guide
        """
        user_message = f"""Provide a {detail_level} nursing guide for: {procedure}

Include:
1. Supplies needed
2. Patient preparation
3. Step-by-step procedure
4. Documentation points
5. Common issues and troubleshooting
6. Post-procedure care/monitoring

Note: Always verify with your facility's specific protocols."""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=800
        )

    def what_to_watch(
        self,
        condition: str,
        patient_context: Optional[PatientContext] = None,
    ) -> str:
        """
        Get monitoring priorities for a condition

        Args:
            condition: Patient condition or diagnosis
            patient_context: Optional patient context

        Returns:
            Monitoring guide
        """
        user_message = f"""For a patient with {condition}, what should I watch for?

Provide:
1. Key assessment findings to monitor
2. Vital sign considerations
3. Signs of improvement
4. Warning signs/red flags
5. When to escalate care
6. Common complications to watch for
7. Patient education points"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=600
        )

    # ==================== ALIAS METHODS FOR COMPATIBILITY ====================

    def medication_lookup(
        self,
        medication: str,
        include_interactions: bool = False,
        patient_context: Optional[PatientContext] = None,
    ) -> str:
        """
        Alias for med_info - Get nursing-focused medication information

        Args:
            medication: Medication name (generic or brand)
            include_interactions: Whether to include drug interaction info
            patient_context: Optional patient context for personalized info

        Returns:
            Medication information formatted for nurses
        """
        return self.med_info(medication, include_interactions, patient_context)

    def clinical_reference(
        self,
        query: str,
        reference_type: str = "general",
    ) -> str:
        """
        General clinical reference lookup

        Args:
            query: Clinical question or topic
            reference_type: "lab", "procedure", "assessment", or "general"

        Returns:
            Clinical reference information
        """
        type_prompts = {
            "lab": "Provide information about this lab test, including normal ranges and clinical significance:",
            "procedure": "Provide nursing guidance for this procedure:",
            "assessment": "Explain this assessment finding and its clinical significance:",
            "general": "Provide clinical reference information about:",
        }

        prompt_intro = type_prompts.get(reference_type, type_prompts["general"])

        user_message = f"""{prompt_intro} {query}

Include:
1. Key clinical information
2. Normal/abnormal findings
3. Nursing considerations
4. When to notify provider
5. Documentation points"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=500
        )

    def analyze_abg(
        self,
        ph: float,
        pco2: float,
        hco3: float,
        pao2: Optional[float] = None,
        fio2: Optional[float] = None,
    ) -> str:
        """
        Analyze Arterial Blood Gas results

        Args:
            ph: pH value (normal 7.35-7.45)
            pco2: PaCO2 in mmHg (normal 35-45)
            hco3: HCO3 in mEq/L (normal 22-26)
            pao2: PaO2 in mmHg (optional, normal 80-100)
            fio2: FiO2 (optional, for A-a gradient)

        Returns:
            ABG interpretation with clinical implications
        """
        o2_info = ""
        if pao2 is not None:
            o2_info = f"\nPaO2: {pao2} mmHg"
            if fio2 is not None:
                o2_info += f"\nFiO2: {fio2}%"

        user_message = f"""Interpret this Arterial Blood Gas (ABG):

pH: {ph}
PaCO2: {pco2} mmHg
HCO3: {hco3} mEq/L{o2_info}

Please provide:
1. Is the pH acidotic, alkalotic, or normal?
2. What is the primary disorder (respiratory vs metabolic)?
3. Is there compensation? If so, partial or full?
4. Complete interpretation (e.g., "Partially compensated metabolic acidosis")
5. Common clinical causes for this pattern
6. Nursing priorities for this ABG result
7. When to escalate/notify provider
8. Relevant interventions to consider"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=600
        )

    # ==================== HIGHLIGHT-TO-EXPLAIN FEATURE ====================

    def explain_highlighted_text(
        self,
        highlighted_text: str,
        source_context: Optional[str] = None,
        reading_level: ReadingLevel = ReadingLevel.BASIC,
        audience: str = "nursing",
    ) -> str:
        """
        Explain selected/highlighted text from progress notes or clinical documentation.
        This enables nurses to highlight any medical term and get instant explanation.

        Args:
            highlighted_text: The text selected by the user (e.g., "A-fib with RVR")
            source_context: Surrounding text for better context (optional)
            reading_level: Target reading level for explanation
            audience: "nursing" for clinical, "patient" for family-friendly

        Returns:
            Plain language explanation of the highlighted text
        """
        audience_instruction = (
            "for a nurse who needs a quick clinical refresher"
            if audience == "nursing"
            else f"for a patient or family member at a {reading_level.value} reading level"
        )

        context_str = f"\n\nContext from the note:\n{source_context}" if source_context else ""

        user_message = f"""A nurse has highlighted this text from a clinical note and needs an explanation:

HIGHLIGHTED TEXT: "{highlighted_text}"
{context_str}

Please explain this {audience_instruction}. Include:

1. **What it means**: Simple definition/explanation
2. **Why it matters**: Clinical significance or why the doctor mentioned it
3. **Key points**: What a nurse should know or watch for related to this
4. **Common abbreviations**: If abbreviations are present, spell them out

Keep the explanation concise but thorough. Use bullet points where helpful."""

        return self._generate_response(
            self.system_prompts["quick_explain"],
            user_message,
            max_new_tokens=400
        )

    def explain_abbreviation(
        self,
        abbreviation: str,
    ) -> str:
        """
        Quick lookup for medical abbreviations.

        Args:
            abbreviation: Medical abbreviation (e.g., "CABG", "A-fib", "CHFrEF")

        Returns:
            Full meaning and brief explanation
        """
        user_message = f"""What does the medical abbreviation "{abbreviation}" stand for?

Please provide:
1. Full term/meaning
2. Brief definition (1-2 sentences)
3. Common clinical context where this is used"""

        return self._generate_response(
            self.system_prompts["quick_explain"],
            user_message,
            max_new_tokens=200
        )

    # ==================== MODULE 5: ASSESSMENT SCALES ====================

    def assess_gcs(
        self,
        eye_response: int,
        verbal_response: int,
        motor_response: int,
    ) -> str:
        """
        Calculate and interpret Glasgow Coma Scale

        Args:
            eye_response: 1-4 (1=none, 4=spontaneous)
            verbal_response: 1-5 (1=none, 5=oriented)
            motor_response: 1-6 (1=none, 6=obeys commands)

        Returns:
            GCS interpretation and nursing implications
        """
        total = eye_response + verbal_response + motor_response

        user_message = f"""Interpret this Glasgow Coma Scale (GCS) assessment:

Eye Response: {eye_response}/4
Verbal Response: {verbal_response}/5
Motor Response: {motor_response}/6
TOTAL GCS: {total}/15

Please provide:
1. What this GCS score means clinically
2. Severity classification (mild/moderate/severe)
3. Key nursing considerations for this GCS level
4. When to escalate/notify provider
5. Documentation tips
6. Common interventions for this level"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=500
        )

    def assess_nihss(
        self,
        components: Dict[str, int],
    ) -> str:
        """
        Interpret NIH Stroke Scale score

        Args:
            components: Dict with NIHSS component scores

        Returns:
            NIHSS interpretation and stroke severity
        """
        total = sum(components.values())

        user_message = f"""Interpret this NIH Stroke Scale (NIHSS) assessment:

Component Scores: {components}
TOTAL NIHSS: {total}

Please provide:
1. Stroke severity classification
2. What each abnormal component indicates
3. Expected deficits at this severity
4. Time-critical interventions
5. tPA/thrombectomy eligibility considerations
6. Nursing priorities for this score
7. What to monitor for improvement/deterioration"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=600
        )

    def assess_braden(
        self,
        sensory_perception: int,
        moisture: int,
        activity: int,
        mobility: int,
        nutrition: int,
        friction_shear: int,
    ) -> str:
        """
        Calculate and interpret Braden Scale for pressure injury risk

        Args:
            sensory_perception: 1-4
            moisture: 1-4
            activity: 1-4
            mobility: 1-4
            nutrition: 1-4
            friction_shear: 1-3

        Returns:
            Braden interpretation and prevention plan
        """
        total = (sensory_perception + moisture + activity +
                 mobility + nutrition + friction_shear)

        user_message = f"""Interpret this Braden Scale assessment for pressure injury risk:

Sensory Perception: {sensory_perception}/4
Moisture: {moisture}/4
Activity: {activity}/4
Mobility: {mobility}/4
Nutrition: {nutrition}/4
Friction/Shear: {friction_shear}/3
TOTAL BRADEN: {total}/23

Please provide:
1. Risk level classification (high/moderate/low)
2. Which subscales are most concerning
3. Specific interventions for each risk area
4. Turning/repositioning schedule recommendation
5. Skin care considerations
6. Documentation requirements
7. When to involve wound care team"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=600
        )

    def assess_pain(
        self,
        scale_type: str,
        score: int,
        location: Optional[str] = None,
        quality: Optional[str] = None,
    ) -> str:
        """
        Interpret pain assessment and suggest interventions

        Args:
            scale_type: "numeric" (0-10), "faces", "flacc", "cpot"
            score: Pain score
            location: Pain location if known
            quality: Pain quality (sharp, dull, burning, etc.)

        Returns:
            Pain interpretation and management suggestions
        """
        location_str = f"\nLocation: {location}" if location else ""
        quality_str = f"\nQuality: {quality}" if quality else ""

        user_message = f"""Interpret this pain assessment:

Scale: {scale_type.upper()}
Score: {score}
{location_str}{quality_str}

Please provide:
1. Pain severity classification
2. Expected patient presentation at this level
3. Non-pharmacological interventions
4. Pharmacological considerations
5. Reassessment timing
6. Documentation requirements
7. When to escalate/adjust pain management plan"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=500
        )

    def assess_fall_risk(
        self,
        age: int,
        fall_history: bool,
        secondary_diagnosis: bool,
        ambulatory_aid: bool,
        iv_access: bool,
        gait: str,
        mental_status: str,
    ) -> str:
        """
        Assess fall risk using Morse Fall Scale components

        Args:
            age: Patient age
            fall_history: History of falls
            secondary_diagnosis: Has secondary diagnosis
            ambulatory_aid: Uses ambulatory aid
            iv_access: Has IV/heplock
            gait: "normal", "weak", "impaired"
            mental_status: "oriented", "forgetful", "confused"

        Returns:
            Fall risk assessment and prevention plan
        """
        user_message = f"""Assess fall risk based on these factors:

Age: {age}
History of Falls: {"Yes" if fall_history else "No"}
Secondary Diagnosis: {"Yes" if secondary_diagnosis else "No"}
Ambulatory Aid: {"Yes" if ambulatory_aid else "No"}
IV/Heplock: {"Yes" if iv_access else "No"}
Gait: {gait}
Mental Status: {mental_status}

Please provide:
1. Estimated fall risk level (high/moderate/low)
2. Key risk factors identified
3. Recommended fall prevention interventions
4. Environmental modifications needed
5. Patient/family education points
6. Documentation requirements
7. When to reassess"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=500
        )

    def assess_news(
        self,
        resp_rate: int,
        o2_sat: int,
        supplemental_o2: bool,
        temp: float,
        systolic_bp: int,
        heart_rate: int,
        consciousness: str,
    ) -> str:
        """
        Calculate and interpret NEWS2 (National Early Warning Score)

        Args:
            resp_rate: Respiratory rate
            o2_sat: Oxygen saturation %
            supplemental_o2: On supplemental oxygen
            temp: Temperature in Celsius
            systolic_bp: Systolic blood pressure
            heart_rate: Heart rate
            consciousness: "alert", "verbal", "pain", "unresponsive"

        Returns:
            NEWS2 score interpretation and escalation guidance
        """
        user_message = f"""Calculate and interpret NEWS2 for these vital signs:

Respiratory Rate: {resp_rate}
O2 Saturation: {o2_sat}%
Supplemental O2: {"Yes" if supplemental_o2 else "No"}
Temperature: {temp}°C
Systolic BP: {systolic_bp}
Heart Rate: {heart_rate}
Consciousness: {consciousness.upper()}

Please provide:
1. NEWS2 score calculation (show scoring for each parameter)
2. Total score and risk level
3. Recommended response/escalation level
4. Monitoring frequency recommendation
5. Specific concerns based on these values
6. When to activate rapid response team
7. Documentation requirements"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=600
        )

    def nursing_calculation(
        self,
        calc_type: str,
        **params,
    ) -> str:
        """
        Perform common nursing calculations

        Args:
            calc_type: Type of calculation
                - "drip_rate": IV drip rate (mL/hr or gtts/min)
                - "dose_weight": Weight-based dosing
                - "bsa": Body surface area
                - "creatinine_clearance": CrCl for renal dosing
                - "corrected_calcium": Calcium correction for albumin
                - "anion_gap": Anion gap calculation
                - "map": Mean arterial pressure
            **params: Calculation-specific parameters

        Returns:
            Calculation result with clinical interpretation
        """
        param_str = "\n".join([f"  {k}: {v}" for k, v in params.items()])

        user_message = f"""Perform this nursing calculation:

Calculation Type: {calc_type}
Parameters:
{param_str}

Please provide:
1. Step-by-step calculation
2. Final result with appropriate units
3. Clinical interpretation of the result
4. Normal/expected ranges for context
5. Nursing considerations
6. When to be concerned about this value
7. Double-check formula used"""

        return self._generate_response(
            self.system_prompts["clinical_ref"],
            user_message,
            max_new_tokens=500
        )


# ==================== DEMO FUNCTIONS ====================

def demo_quick_explain():
    """Demo the Quick Explain module"""
    examples = [
        ("atrial fibrillation", "The patient was just diagnosed after their heart monitor showed irregular rhythm"),
        ("acute exacerbation of COPD", "The patient came in short of breath"),
        ("tracheostomy", "The patient will need this procedure tomorrow"),
        ("sepsis", "The patient's blood cultures came back positive"),
    ]
    return examples


def demo_med_helper():
    """Demo the Med Helper module"""
    examples = [
        "metoprolol",
        "heparin",
        "vancomycin",
        "furosemide",
        "insulin lispro",
    ]
    return examples


def demo_shift_sidekick():
    """Demo SBAR generation"""
    sample_info = """
    72 y/o male, admitted 3 days ago for pneumonia
    Currently on day 3 of Ceftriaxone and Azithromycin
    Vitals trending stable: T 99.2, HR 88, BP 138/82, RR 20, O2 sat 94% on 2L NC
    Morning labs: WBC improved to 11.2 from 14.6 yesterday
    Patient reports feeling better, eating 50% of meals
    Still requiring O2 when ambulating, sats drop to 89% without
    IV access good, PIV in right forearm, flushes well
    PT/OT consult ordered, pending evaluation
    """
    return sample_info


if __name__ == "__main__":
    print("Nurse Companion - MedGemma Impact Challenge")
    print("=" * 50)
    print("Modules available:")
    print("1. Quick Explain - Medical jargon to plain English")
    print("2. Med Helper - Medication information")
    print("3. Shift Sidekick - SBAR handoff reports")
    print("4. Clinical Quick Ref - Lab values and procedures")
    print("5. Assessment Scales - GCS, NIHSS, Braden, NEWS2, Fall Risk")
    print("6. Nursing Calculations - Drip rates, dosing, clinical formulas")
    print("=" * 50)
    print("\nTo use, initialize with: companion = NurseCompanion()")
    print("Then load model with: companion.load_model()")
