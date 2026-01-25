"""
Medical Imaging Analysis Module for NurseGemma
Multimodal analysis using MedGemma's vision capabilities.

Supports:
- Chest X-Ray (CXR) interpretation
- CT scan analysis (head, chest, abdomen)
- MRI interpretation
- Wound assessment with NPIAP staging

Built BY a nurse, FOR nurses - making radiology accessible at the bedside.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import time


class ImagingModality(Enum):
    """Types of medical imaging supported"""
    CXR = "chest_xray"
    CT_HEAD = "ct_head"
    CT_CHEST = "ct_chest"
    CT_ABDOMEN = "ct_abdomen"
    MRI_BRAIN = "mri_brain"
    MRI_SPINE = "mri_spine"
    WOUND = "wound"
    ECG = "ecg"


class Urgency(Enum):
    """Clinical urgency levels for findings"""
    ROUTINE = "routine"
    ATTENTION = "attention"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class ImagingResult:
    """Result from image analysis"""
    modality: ImagingModality
    findings: str
    nursing_implications: str
    urgency: Urgency
    notify_provider: bool
    sbar_summary: Optional[str]
    execution_time: float
    estimated_manual_time: float  # How long a nurse would take to get this info


# =============================================================================
# CLINICAL CONTEXT PROMPTS FOR EACH MODALITY
# =============================================================================

IMAGING_PROMPTS = {
    ImagingModality.CXR: """You are a clinical nurse educator helping interpret this chest X-ray.

Analyze this CXR and provide a NURSING-FOCUSED interpretation:

1. **KEY FINDINGS** - What's visible (normal vs abnormal)
   - Lung fields (clear, infiltrates, consolidation, effusion)
   - Heart size (normal, enlarged - estimate CTR if visible)
   - Mediastinum (normal, widened, shifted)
   - Costophrenic angles (sharp, blunted)
   - Any tubes/lines (ETT position, central lines, NG tube, chest tubes)

2. **CLINICAL SIGNIFICANCE** - What this means for patient care
   - Is this a change from baseline?
   - Does this explain patient symptoms?

3. **NURSING IMPLICATIONS**
   - What to monitor (SpO2, respiratory rate, work of breathing)
   - Position recommendations
   - When to notify the physician

4. **URGENCY LEVEL**: [ROUTINE/ATTENTION/URGENT/CRITICAL]

Be specific and actionable. Avoid radiologist jargon when simpler terms work.""",

    ImagingModality.CT_HEAD: """You are a clinical nurse educator helping interpret this CT head.

Analyze this CT head and provide a NURSING-FOCUSED interpretation:

1. **KEY FINDINGS**
   - Hemorrhage (epidural, subdural, subarachnoid, intraparenchymal)
   - Midline shift (if any, estimate mm)
   - Ventricles (normal, dilated, compressed)
   - Mass effect or edema
   - Skull fractures
   - Old vs acute changes

2. **STROKE ASSESSMENT** (if applicable)
   - Early ischemic changes
   - Hyperdense vessel sign
   - ASPECTS score considerations

3. **NURSING IMPLICATIONS**
   - Neuro check frequency
   - HOB positioning
   - BP parameters
   - Pupil assessment priority
   - Seizure precautions needed?

4. **URGENCY LEVEL**: [ROUTINE/ATTENTION/URGENT/CRITICAL]

5. **NOTIFY PROVIDER IF**: Specific parameters that warrant immediate call""",

    ImagingModality.CT_CHEST: """You are a clinical nurse educator helping interpret this CT chest.

Analyze this CT chest and provide a NURSING-FOCUSED interpretation:

1. **KEY FINDINGS**
   - Pulmonary embolism (PE) - filling defects in pulmonary arteries
   - Lung parenchyma (consolidation, ground-glass, nodules)
   - Pleural effusions
   - Pneumothorax
   - Mediastinal abnormalities
   - Lymphadenopathy

2. **CLINICAL SIGNIFICANCE**
   - Correlation with patient symptoms
   - Severity assessment

3. **NURSING IMPLICATIONS**
   - Oxygen requirements
   - Activity restrictions
   - Anticoagulation considerations
   - Monitoring parameters

4. **URGENCY LEVEL**: [ROUTINE/ATTENTION/URGENT/CRITICAL]""",

    ImagingModality.MRI_BRAIN: """You are a clinical nurse educator helping interpret this brain MRI.

Analyze this MRI and provide a NURSING-FOCUSED interpretation:

1. **KEY FINDINGS**
   - Signal abnormalities (T1, T2, FLAIR, DWI)
   - Location of lesions
   - Mass effect or midline shift
   - Enhancement patterns (if contrast given)
   - Acute vs chronic changes

2. **CLINICAL CORRELATIONS**
   - Stroke (DWI restriction)
   - MS lesions (periventricular, juxtacortical)
   - Tumor characteristics
   - Infection/abscess

3. **NURSING IMPLICATIONS**
   - Neuro assessment priorities
   - Fall risk considerations
   - Cognitive/behavioral changes to monitor
   - Medication implications

4. **URGENCY LEVEL**: [ROUTINE/ATTENTION/URGENT/CRITICAL]""",

    ImagingModality.WOUND: """You are a wound care nurse specialist analyzing this wound image.

Provide a comprehensive wound assessment based on NPIAP/EPUAP guidelines:

1. **STAGING** (per NPIAP criteria)
   - Stage 1: Non-blanchable erythema, intact skin
   - Stage 2: Partial-thickness, exposed dermis
   - Stage 3: Full-thickness, adipose visible
   - Stage 4: Full-thickness, fascia/muscle/bone exposed
   - Unstageable: Obscured by slough/eschar
   - DTPI: Deep tissue pressure injury

2. **WOUND BED ASSESSMENT**
   - Tissue types present (% of each):
     * Granulation (red, beefy)
     * Slough (yellow, tan, gray)
     * Eschar (black, brown, dry)
     * Epithelial (pink, pearly)
   - Wound bed moisture

3. **WOUND CHARACTERISTICS**
   - Estimated size (L x W)
   - Wound edges (attached, rolled, undermining)
   - Periwound skin (intact, macerated, erythematous)
   - Exudate (type: serous/sanguineous/purulent, amount)

4. **INFECTION ASSESSMENT**
   - NERDS criteria (superficial): Non-healing, Exudate, Red friable tissue, Debris, Smell
   - STONEES criteria (deep): Size increasing, Temperature, Os (bone), New breakdown, Exudate, Erythema, Smell

5. **NURSING RECOMMENDATIONS**
   - Dressing recommendations
   - Offloading/positioning
   - Frequency of assessment
   - When to escalate to wound care/surgery

6. **URGENCY LEVEL**: [ROUTINE/ATTENTION/URGENT/CRITICAL]"""
}

# =============================================================================
# SAMPLE MEDICAL IMAGES FOR DEMO (Public Domain/CC Licensed)
# =============================================================================

SAMPLE_IMAGES = {
    # Chest X-Rays
    "cxr_normal": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Chest_Xray_PA_3-8-2010.png",
        "modality": ImagingModality.CXR,
        "description": "Normal PA Chest X-ray",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Clear lung fields", "Normal heart size", "Sharp costophrenic angles"]
    },
    "cxr_pneumonia": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/87/X-ray_of_lobar_pneumonia.jpg",
        "modality": ImagingModality.CXR,
        "description": "Lobar Pneumonia - Right Lower Lobe",
        "source": "Wikimedia Commons - Mikael Haggstrom (CC BY-SA)",
        "expected_findings": ["Dense consolidation RLL", "Air bronchograms", "Silhouette sign"]
    },
    "cxr_pleural_effusion": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Massive_Effusion2008.jpg",
        "modality": ImagingModality.CXR,
        "description": "Large Left Pleural Effusion",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Blunted costophrenic angle", "Meniscus sign", "Mediastinal shift"]
    },
    "cxr_cardiomegaly": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Chest_radiograph_of_a_person_with_congestive_heart_failure.jpg",
        "modality": ImagingModality.CXR,
        "description": "Cardiomegaly with CHF",
        "source": "Wikimedia Commons (CC BY-SA 4.0)",
        "expected_findings": ["CTR >50%", "Cephalization of vessels", "Kerley B lines", "Pulmonary edema"]
    },

    # CT Scans
    "ct_pulmonary_embolism": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Pulmonary_embolism.png",
        "modality": ImagingModality.CT_CHEST,
        "description": "CT showing Pulmonary Embolism",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Filling defect in pulmonary artery", "Saddle embolus", "RV strain"]
    },
    "ct_stroke": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5b/MCA_territory_infarct.jpg",
        "modality": ImagingModality.CT_HEAD,
        "description": "CT Head - MCA Territory Stroke",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Hypodensity MCA territory", "Loss of gray-white differentiation", "Sulcal effacement"]
    },

    # MRI
    "mri_ms": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/ae/MS_brain_MRI.jpg",
        "modality": ImagingModality.MRI_BRAIN,
        "description": "Brain MRI FLAIR - Multiple Sclerosis",
        "source": "Wikimedia Commons (CC BY-SA 3.0)",
        "expected_findings": ["Periventricular hyperintensities", "Dawson fingers", "Juxtacortical lesions"]
    },

    # Wounds
    "wound_stage2": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Gradestage2.jpg",
        "modality": ImagingModality.WOUND,
        "description": "Stage 2 Pressure Injury - Sacral",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Partial-thickness", "Pink wound bed", "No slough/eschar"]
    },
    "wound_stage3": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/fc/Grade3.jpg",
        "modality": ImagingModality.WOUND,
        "description": "Stage 3 Pressure Injury",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Full-thickness", "Adipose visible", "Granulation tissue"]
    },
    "wound_stage4": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Grade4.jpg",
        "modality": ImagingModality.WOUND,
        "description": "Stage 4 Pressure Injury",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Bone/tendon visible", "Deep tissue damage", "Requires specialty consult"]
    },
    "wound_unstageable": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Decubitus_ulcer.jpg",
        "modality": ImagingModality.WOUND,
        "description": "Unstageable - Covered by Eschar",
        "source": "Wikimedia Commons (Public Domain)",
        "expected_findings": ["Cannot determine depth", "Eschar obscures bed", "Stage 3 or 4 after debridement"]
    },
    "wound_diabetic_foot": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/18/Neuropathic_heel_ulcer_diabetisches_Fussulkus.jpg",
        "modality": ImagingModality.WOUND,
        "description": "Diabetic Foot Ulcer - Neuropathic",
        "source": "Wikimedia Commons (CC BY-SA 3.0)",
        "expected_findings": ["Neuropathic etiology", "Often painless", "Offloading critical"]
    }
}


# =============================================================================
# PRESSURE INJURY STAGING REFERENCE (NPIAP 2024)
# =============================================================================

PRESSURE_INJURY_STAGES = {
    "stage_1": {
        "name": "Stage 1",
        "definition": "Non-blanchable erythema of intact skin",
        "key_features": [
            "Skin intact - no open wound",
            "Non-blanchable redness",
            "May be painful, firm, soft, warmer or cooler"
        ],
        "nursing_actions": [
            "Relieve pressure immediately",
            "Assess every shift",
            "Barrier cream if moisture present",
            "Turning schedule q2h"
        ]
    },
    "stage_2": {
        "name": "Stage 2",
        "definition": "Partial-thickness skin loss with exposed dermis",
        "key_features": [
            "Shallow open ulcer",
            "Pink/red wound bed",
            "May be intact or ruptured blister",
            "No slough or eschar"
        ],
        "nursing_actions": [
            "Cleanse with saline",
            "Moisture-retentive dressing",
            "Protect from friction",
            "Monitor for infection"
        ]
    },
    "stage_3": {
        "name": "Stage 3",
        "definition": "Full-thickness skin loss",
        "key_features": [
            "Adipose (fat) visible",
            "Slough may be present",
            "Undermining/tunneling may occur",
            "Bone/tendon NOT visible"
        ],
        "nursing_actions": [
            "Wound care consult",
            "Pack dead space loosely",
            "Measure L x W x D",
            "Assess for infection (NERDS/STONEES)"
        ]
    },
    "stage_4": {
        "name": "Stage 4",
        "definition": "Full-thickness skin AND tissue loss",
        "key_features": [
            "Exposed bone, tendon, fascia, muscle",
            "Slough/eschar may be present",
            "Often has undermining/tunneling"
        ],
        "nursing_actions": [
            "URGENT wound care/surgery consult",
            "Culture if infected",
            "High protein nutrition",
            "Specialty bed required",
            "Consider wound VAC"
        ]
    },
    "unstageable": {
        "name": "Unstageable",
        "definition": "Full-thickness loss obscured by slough/eschar",
        "key_features": [
            "True depth unknown",
            "Covered by slough or eschar",
            "Will be Stage 3 or 4 after debridement"
        ],
        "nursing_actions": [
            "Do NOT remove stable heel eschar",
            "Debridement consult for non-heel",
            "Monitor for infection under eschar"
        ]
    },
    "dtpi": {
        "name": "Deep Tissue Pressure Injury",
        "definition": "Persistent non-blanchable deep red/maroon/purple",
        "key_features": [
            "Intact or non-intact skin",
            "Deep discoloration",
            "May have blood-filled blister",
            "Pain precedes visible changes"
        ],
        "nursing_actions": [
            "Document timeline (when first noticed)",
            "Photograph for baseline",
            "Complete pressure relief",
            "Monitor q4h - can evolve rapidly",
            "Do NOT massage"
        ]
    }
}


class MedicalImagingAnalyzer:
    """
    Multimodal medical image analyzer using MedGemma.

    Provides nursing-focused interpretations of:
    - Chest X-rays
    - CT scans (head, chest, abdomen)
    - MRI (brain, spine)
    - Wound photos
    """

    def __init__(self, model=None, processor=None):
        """
        Initialize analyzer with MedGemma model.

        Args:
            model: Pre-loaded MedGemma model
            processor: Pre-loaded processor
        """
        self.model = model
        self.processor = processor

    def analyze_image(
        self,
        image,
        modality: ImagingModality,
        clinical_context: str = "",
        patient_info: str = ""
    ) -> ImagingResult:
        """
        Analyze a medical image with MedGemma.

        Args:
            image: PIL Image, URL string, or file path
            modality: Type of imaging study
            clinical_context: Why the study was ordered
            patient_info: Relevant patient history

        Returns:
            ImagingResult with findings and nursing implications
        """
        start_time = time.time()

        # Get modality-specific prompt
        base_prompt = IMAGING_PROMPTS.get(modality, IMAGING_PROMPTS[ImagingModality.CXR])

        # Add clinical context
        full_prompt = f"""{base_prompt}

CLINICAL CONTEXT: {clinical_context if clinical_context else "Not provided"}
PATIENT INFO: {patient_info if patient_info else "Not provided"}

Provide a clear, nursing-focused interpretation."""

        # Perform analysis
        try:
            analysis = self._analyze_with_medgemma(image, full_prompt)
            urgency = self._determine_urgency(analysis)
            notify = urgency in [Urgency.URGENT, Urgency.CRITICAL]

            # Generate SBAR if urgent
            sbar = self._generate_sbar(analysis, modality) if notify else None

        except Exception as e:
            analysis = f"Analysis error: {str(e)}"
            urgency = Urgency.ATTENTION
            notify = True
            sbar = None

        execution_time = time.time() - start_time

        # Estimate manual time (asking radiologist, looking up, understanding)
        manual_times = {
            ImagingModality.CXR: 300,  # 5 minutes
            ImagingModality.CT_HEAD: 600,  # 10 minutes
            ImagingModality.CT_CHEST: 480,  # 8 minutes
            ImagingModality.MRI_BRAIN: 600,  # 10 minutes
            ImagingModality.WOUND: 480,  # 8 minutes
        }

        return ImagingResult(
            modality=modality,
            findings=analysis,
            nursing_implications=self._extract_nursing_implications(analysis),
            urgency=urgency,
            notify_provider=notify,
            sbar_summary=sbar,
            execution_time=execution_time,
            estimated_manual_time=manual_times.get(modality, 300)
        )

    def _analyze_with_medgemma(self, image, prompt: str) -> str:
        """Perform multimodal analysis with MedGemma."""
        import requests
        from PIL import Image
        from io import BytesIO
        import torch

        # Handle different image input types
        if isinstance(image, str):
            if image.startswith('http'):
                # Download from URL
                headers = {"User-Agent": "NurseGemma Medical AI"}
                response = requests.get(image, headers=headers, timeout=30)
                response.raise_for_status()
                pil_image = Image.open(BytesIO(response.content))
            else:
                # Local file path
                pil_image = Image.open(image)
        else:
            # Already a PIL Image
            pil_image = image

        # Convert to RGB
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Build multimodal message
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil_image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        # Process with MedGemma
        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to(self.model.device, dtype=torch.bfloat16)

        with torch.inference_mode():
            generation = self.model.generate(
                **inputs,
                max_new_tokens=1000,
                do_sample=False
            )

        # Decode response
        decoded = self.processor.decode(generation[0], skip_special_tokens=True)

        # Extract assistant response
        if "assistant" in decoded.lower():
            parts = decoded.split("assistant")
            if len(parts) > 1:
                return parts[-1].strip()

        return decoded

    def _determine_urgency(self, analysis: str) -> Urgency:
        """Determine urgency level from analysis text."""
        analysis_lower = analysis.lower()

        # Critical findings
        critical_terms = [
            "critical", "stat", "emergent", "immediate", "life-threatening",
            "tension pneumothorax", "massive pe", "hemorrhage", "herniation",
            "code", "arrest", "septic", "unstable"
        ]
        if any(term in analysis_lower for term in critical_terms):
            return Urgency.CRITICAL

        # Urgent findings
        urgent_terms = [
            "urgent", "notify immediately", "call provider", "worrisome",
            "pneumothorax", "pulmonary embolism", "stroke", "acute",
            "new infiltrate", "worsening", "deteriorating"
        ]
        if any(term in analysis_lower for term in urgent_terms):
            return Urgency.URGENT

        # Needs attention
        attention_terms = [
            "attention", "follow up", "monitor closely", "concerning",
            "abnormal", "recommend", "suggest"
        ]
        if any(term in analysis_lower for term in attention_terms):
            return Urgency.ATTENTION

        return Urgency.ROUTINE

    def _extract_nursing_implications(self, analysis: str) -> str:
        """Extract nursing implications from analysis."""
        # Look for nursing implications section
        lower = analysis.lower()

        markers = ["nursing implications", "nursing actions", "nursing recommendations",
                   "what to monitor", "nursing assessment"]

        for marker in markers:
            if marker in lower:
                idx = lower.index(marker)
                # Extract section (up to 500 chars or next major section)
                section = analysis[idx:idx+500]
                # Clean up
                lines = section.split('\n')
                return '\n'.join(lines[:10])

        return "See full analysis for nursing implications."

    def _generate_sbar(self, analysis: str, modality: ImagingModality) -> str:
        """Generate SBAR summary for provider notification."""
        modality_names = {
            ImagingModality.CXR: "chest X-ray",
            ImagingModality.CT_HEAD: "CT head",
            ImagingModality.CT_CHEST: "CT chest",
            ImagingModality.MRI_BRAIN: "brain MRI",
            ImagingModality.WOUND: "wound assessment"
        }

        return f"""**SBAR - Imaging Findings**

**S - Situation:**
Reporting findings from {modality_names.get(modality, 'imaging study')}.

**B - Background:**
[Insert relevant patient history]

**A - Assessment:**
{analysis[:300]}...

**R - Recommendation:**
Please review findings and advise on plan of care."""

    # =============================================================================
    # CONVENIENCE METHODS FOR SPECIFIC MODALITIES
    # =============================================================================

    def analyze_cxr(self, image, clinical_context: str = "") -> ImagingResult:
        """Analyze a chest X-ray."""
        return self.analyze_image(image, ImagingModality.CXR, clinical_context)

    def analyze_ct_head(self, image, clinical_context: str = "") -> ImagingResult:
        """Analyze a CT head."""
        return self.analyze_image(image, ImagingModality.CT_HEAD, clinical_context)

    def analyze_ct_chest(self, image, clinical_context: str = "") -> ImagingResult:
        """Analyze a CT chest (PE protocol, etc.)."""
        return self.analyze_image(image, ImagingModality.CT_CHEST, clinical_context)

    def analyze_wound(
        self,
        image,
        location: str = "sacrum",
        patient_context: str = ""
    ) -> ImagingResult:
        """
        Analyze a wound photo with NPIAP staging.

        Args:
            image: Wound photo
            location: Anatomical location (sacrum, heel, etc.)
            patient_context: Relevant history (diabetes, immobility, etc.)
        """
        context = f"Wound location: {location}. {patient_context}"
        return self.analyze_image(image, ImagingModality.WOUND, context)

    def get_wound_staging_reference(self, stage: str) -> Dict[str, Any]:
        """Get reference information for a pressure injury stage."""
        return PRESSURE_INJURY_STAGES.get(stage.lower(), {})

    def list_sample_images(self, modality: Optional[ImagingModality] = None) -> List[Dict]:
        """List available sample images for demo/testing."""
        if modality:
            return [
                {"key": k, **v}
                for k, v in SAMPLE_IMAGES.items()
                if v["modality"] == modality
            ]
        return [{"key": k, **v} for k, v in SAMPLE_IMAGES.items()]


# =============================================================================
# STANDALONE FUNCTIONS FOR NOTEBOOK USE
# =============================================================================

def analyze_medical_image(
    image,
    modality: str,
    model,
    processor,
    clinical_context: str = ""
) -> str:
    """
    Standalone function for analyzing medical images in notebooks.

    Args:
        image: Image URL, file path, or PIL Image
        modality: "cxr", "ct_head", "ct_chest", "mri_brain", "wound"
        model: Loaded MedGemma model
        processor: Loaded processor
        clinical_context: Why study was ordered

    Returns:
        Formatted analysis string
    """
    modality_map = {
        "cxr": ImagingModality.CXR,
        "chest_xray": ImagingModality.CXR,
        "ct_head": ImagingModality.CT_HEAD,
        "ct_chest": ImagingModality.CT_CHEST,
        "mri_brain": ImagingModality.MRI_BRAIN,
        "wound": ImagingModality.WOUND
    }

    imaging_modality = modality_map.get(modality.lower(), ImagingModality.CXR)

    analyzer = MedicalImagingAnalyzer(model, processor)
    result = analyzer.analyze_image(image, imaging_modality, clinical_context)

    # Format output
    output = f"""## Medical Image Analysis

**Modality:** {result.modality.value}
**Urgency:** {result.urgency.value.upper()}
**Notify Provider:** {"Yes" if result.notify_provider else "No"}
**Analysis Time:** {result.execution_time:.1f}s (Manual estimate: {result.estimated_manual_time/60:.0f} min)

---

### Findings

{result.findings}

---

### Nursing Implications

{result.nursing_implications}
"""

    if result.sbar_summary:
        output += f"""
---

### SBAR for Provider

{result.sbar_summary}
"""

    return output


def test_imaging_analysis(image_key: str, model, processor) -> str:
    """
    Test image analysis with a sample image.

    Args:
        image_key: Key from SAMPLE_IMAGES (e.g., "cxr_normal", "wound_stage2")
        model: Loaded MedGemma model
        processor: Loaded processor
    """
    if image_key not in SAMPLE_IMAGES:
        available = ", ".join(SAMPLE_IMAGES.keys())
        return f"Image key '{image_key}' not found. Available: {available}"

    img_info = SAMPLE_IMAGES[image_key]

    output = f"""## Testing MedGemma Image Analysis

**Image:** {img_info['description']}
**Source:** {img_info['source']}
**Modality:** {img_info['modality'].value}

**Expected Findings:**
"""
    for finding in img_info['expected_findings']:
        output += f"- {finding}\n"

    output += "\n---\n\n**MedGemma Analysis:**\n\n"

    try:
        result = analyze_medical_image(
            img_info['url'],
            img_info['modality'].value,
            model,
            processor,
            f"Sample {img_info['description']} for educational demo"
        )
        output += result
    except Exception as e:
        output += f"[Error: {str(e)}]\n"
        output += "Ensure GPU runtime is enabled for image analysis."

    return output


# Module info
print("Medical Imaging Module loaded")
print(f"  Modalities: {len(ImagingModality)} types")
print(f"  Sample images: {len(SAMPLE_IMAGES)}")
print(f"  Functions: analyze_medical_image, test_imaging_analysis")
print(f"  Class: MedicalImagingAnalyzer")
