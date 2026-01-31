"""
NurseGemma - Agentic Medical AI for Nursing Practice
MedGemma Impact Challenge 2026 - Agentic Category

🆕 NEW MedGemma 1.5 Features:
- MedASR Voice Input (hands-free nursing mode)
- Longitudinal CXR Comparison (compare X-rays over time)
- 3D CT/MRI Volume Analysis
- Lab Report Extraction (structured data)
- Anatomical Localization (bounding boxes on CXR)

Architecture:
- Gemini 2.0 Flash (Orchestrator): Intent classification, routing, synthesis
- MedGemma 1.5 4B (Medical Specialist): Image analysis, clinical QA
- MedASR (Voice): Medical speech-to-text
- Evidence Agent: Guidelines search via Gemini grounding

Built by a nurse, for nurses.
"""

import os
import json
import base64
import tempfile
import gradio as gr
from PIL import Image
from pathlib import Path
from datetime import datetime
from io import BytesIO
from typing import List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
USE_MEDGEMMA = os.environ.get("USE_MEDGEMMA", "false").lower() == "true"
USE_MEDASR = os.environ.get("USE_MEDASR", "false").lower() == "true"

# GPU Backend URL (for remote 4090 inference)
# Set this to your gpu_backend.py server URL for real MedGemma power
GPU_BACKEND_URL = os.environ.get("GPU_BACKEND_URL", "")

# Model IDs - Updated to MedGemma 1.5
MEDGEMMA_MODEL_ID = "google/medgemma-1.5-4b-it"
MEDASR_MODEL_ID = "google/medasr"


# ============================================================================
# GPU BACKEND CLIENT (Remote 4090 inference)
# ============================================================================

import requests

class GPUBackendClient:
    """Client for calling remote GPU backend (your 4090)."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.available = self._check_health()
    
    def _check_health(self) -> bool:
        """Check if backend is available."""
        if not self.base_url:
            return False
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            if resp.ok:
                data = resp.json()
                print(f"✅ GPU Backend connected: {data.get('gpu', 'unknown')}")
                return True
        except Exception as e:
            print(f"⚠️ GPU Backend not available: {e}")
        return False
    
    def analyze_images(self, images: List[Image.Image], prompt: str, max_tokens: int = 800) -> str:
        """Send images to GPU backend for MedGemma analysis."""
        if not self.available:
            return None
        
        # Convert images to base64
        images_b64 = []
        for img in images:
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            b64 = base64.b64encode(buffer.getvalue()).decode()
            images_b64.append(b64)
        
        try:
            resp = requests.post(
                f"{self.base_url}/analyze",
                json={"prompt": prompt, "images_base64": images_b64, "max_tokens": max_tokens},
                timeout=60
            )
            if resp.ok:
                return resp.json().get("response")
        except Exception as e:
            print(f"GPU Backend error: {e}")
        return None
    
    def clinical_qa(self, prompt: str, max_tokens: int = 600) -> str:
        """Send clinical question to GPU backend."""
        if not self.available:
            return None
        
        try:
            resp = requests.post(
                f"{self.base_url}/clinical",
                json={"prompt": prompt, "max_tokens": max_tokens},
                timeout=30
            )
            if resp.ok:
                return resp.json().get("response")
        except Exception as e:
            print(f"GPU Backend error: {e}")
        return None
    
    def transcribe(self, audio_path: str) -> str:
        """Send audio to GPU backend for MedASR transcription."""
        if not self.available:
            return None
        
        try:
            with open(audio_path, "rb") as f:
                resp = requests.post(
                    f"{self.base_url}/transcribe",
                    files={"audio": f},
                    timeout=30
                )
            if resp.ok:
                return resp.json().get("text")
        except Exception as e:
            print(f"GPU Backend transcription error: {e}")
        return None


# Initialize GPU backend client
gpu_backend = GPUBackendClient(GPU_BACKEND_URL) if GPU_BACKEND_URL else None

# Sample images
SAMPLES_DIR = Path(__file__).parent / "samples"
SAMPLE_IMAGES = {
    "normal_cxr": {
        "path": SAMPLES_DIR / "normal_cxr.png",
        "label": "Normal Chest X-ray",
        "description": "PA chest radiograph - normal cardiopulmonary structures"
    },
    "pneumonia_cxr": {
        "path": SAMPLES_DIR / "pneumonia_covid_cxr.jpg",
        "label": "COVID Pneumonia",
        "description": "Chest X-ray showing bilateral ground-glass opacities"
    },
    "viral_pneumonia_cxr": {
        "path": SAMPLES_DIR / "viral_pneumonia_cxr.jpg",
        "label": "Viral Pneumonia",
        "description": "Chest X-ray showing viral pneumonia pattern"
    }
}

# ============================================================================
# GEMINI CLIENT
# ============================================================================

import google.generativeai as genai

def init_gemini():
    """Initialize Gemini client."""
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.0-flash')
    return None

gemini_model = init_gemini()

# ============================================================================
# MEDGEMMA 1.5 CLIENT (Updated for 1.5 features)
# ============================================================================

medgemma_model = None
medgemma_processor = None
medgemma_available = False

def init_medgemma():
    """Initialize MedGemma 1.5 if available."""
    global medgemma_model, medgemma_processor, medgemma_available
    
    if not USE_MEDGEMMA:
        return False
    
    try:
        import torch
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from huggingface_hub import login
        
        if HF_TOKEN:
            login(token=HF_TOKEN)
        
        medgemma_processor = AutoProcessor.from_pretrained(MEDGEMMA_MODEL_ID)
        medgemma_model = AutoModelForImageTextToText.from_pretrained(
            MEDGEMMA_MODEL_ID, 
            torch_dtype=torch.bfloat16, 
            device_map="auto"
        )
        device = next(medgemma_model.parameters()).device
        print(f"✅ MedGemma 1.5 loaded on {device}")
        medgemma_available = True
        return True
    except Exception as e:
        print(f"⚠️ MedGemma 1.5 not available: {e}")
        return False

# ============================================================================
# MEDASR VOICE INPUT (NEW - Hands-free nursing mode)
# ============================================================================

medasr_model = None
medasr_processor = None
medasr_available = False

def init_medasr():
    """Initialize MedASR for medical speech-to-text."""
    global medasr_model, medasr_processor, medasr_available
    
    if not USE_MEDASR:
        return False
    
    try:
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
        from huggingface_hub import login
        
        if HF_TOKEN:
            login(token=HF_TOKEN)
        
        medasr_processor = AutoProcessor.from_pretrained(MEDASR_MODEL_ID)
        medasr_model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MEDASR_MODEL_ID,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        device = next(medasr_model.parameters()).device
        print(f"✅ MedASR loaded on {device}")
        medasr_available = True
        return True
    except Exception as e:
        print(f"⚠️ MedASR not available: {e}")
        return False


def transcribe_medical_audio(audio_path: str) -> str:
    """
    Transcribe medical audio using MedASR.
    82% fewer errors than Whisper on medical dictation!
    """
    # Try GPU backend first
    if gpu_backend and gpu_backend.available:
        result = gpu_backend.transcribe(audio_path)
        if result:
            return result
    
    if not medasr_available:
        # Fallback to Whisper if MedASR not available
        return transcribe_with_whisper(audio_path)
    
    try:
        import torch
        import librosa
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=16000)
        
        # Process with MedASR
        inputs = medasr_processor(audio, sampling_rate=sr, return_tensors="pt")
        inputs = inputs.to(medasr_model.device)
        
        with torch.inference_mode():
            generated_ids = medasr_model.generate(**inputs, max_new_tokens=256)
        
        transcription = medasr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return transcription
    except Exception as e:
        print(f"MedASR error: {e}, falling back to Whisper")
        return transcribe_with_whisper(audio_path)


def transcribe_with_whisper(audio_path: str) -> str:
    """Fallback to Whisper for transcription."""
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        return f"[Transcription unavailable: {e}]"


# ============================================================================
# AGENTS
# ============================================================================

class OrchestratorAgent:
    """Routes queries to appropriate specialist agents."""
    
    def __init__(self, model):
        self.model = model
    
    def route(self, query: str, has_image: bool, has_multiple_images: bool = False, 
              has_audio: bool = False, has_lab_report: bool = False) -> dict:
        """Classify intent and determine routing."""
        
        prompt = f"""You are the orchestrator for NurseGemma, a nursing-focused medical AI.

Analyze this query and route to the best agent.

Query: "{query}"
Has Image Attached: {has_image}
Has Multiple Images: {has_multiple_images}
Has Audio Input: {has_audio}
Appears to be Lab Report: {has_lab_report}

Agents:
- IMAGE_AGENT: Analyze single medical images (X-rays, CT slices, wounds)
- LONGITUDINAL_AGENT: Compare multiple images over time (trending, progression)
- VOLUMETRIC_AGENT: Analyze 3D CT/MRI volumes (multiple slices of same scan)
- LAB_AGENT: Extract and interpret lab report images
- CLINICAL_AGENT: Answer clinical questions (meds, labs, procedures, assessments)
- EVIDENCE_AGENT: Search evidence-based practice, guidelines, research
- ANATOMY_AGENT: Localize anatomical structures in chest X-rays

Rules:
- Multiple images + "compare" or "progression" or "trending" → LONGITUDINAL_AGENT
- Multiple images + same scan type → VOLUMETRIC_AGENT
- Image that looks like lab report → LAB_AGENT
- Single image + anatomy question → ANATOMY_AGENT
- Single image + general analysis → IMAGE_AGENT
- Guidelines, evidence, research → EVIDENCE_AGENT
- Clinical questions → CLINICAL_AGENT

Respond in JSON only:
{{"agent": "AGENT_NAME", "reason": "brief explanation", "nursing_focus": "how this helps nursing practice"}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
        except Exception as e:
            if has_multiple_images:
                return {"agent": "LONGITUDINAL_AGENT", "reason": "Multiple images", "nursing_focus": "Trending assessment"}
            if has_image:
                return {"agent": "IMAGE_AGENT", "reason": "Image attached", "nursing_focus": "Image assessment"}
            return {"agent": "CLINICAL_AGENT", "reason": f"Default (error: {e})", "nursing_focus": "Clinical support"}


class ImageAgent:
    """Analyzes medical images with nursing focus. Supports MedGemma 1.5."""
    
    def __init__(self, gemini_model, medgemma_model=None, medgemma_processor=None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def analyze(self, image: Image.Image, query: str) -> str:
        """Analyze medical image."""
        # Try GPU backend first (remote 4090)
        if gpu_backend and gpu_backend.available:
            prompt = self._build_analysis_prompt(query)
            result = gpu_backend.analyze_images([image], prompt)
            if result:
                return result
        
        # Local MedGemma
        if self.medgemma and self.processor:
            return self._analyze_medgemma(image, query)
        return self._analyze_gemini(image, query)
    
    def _build_analysis_prompt(self, query: str) -> str:
        """Build nursing-focused analysis prompt."""
        return f"""Analyze this medical image for a nursing assessment.

Query: {query if query else "Describe the findings and nursing implications."}

Provide:
1. Image modality and type
2. Key findings (normal/abnormal)
3. Nursing considerations
4. Suggested actions"""
    
    def _analyze_gemini(self, image: Image.Image, query: str) -> str:
        """Analyze with Gemini (multimodal)."""
        prompt = f"""You are NurseGemma, a nursing-focused medical image analyst.

Analyze this medical image and provide:
1. **Image Type**: What kind of image is this?
2. **Key Findings**: What do you observe? (normal and abnormal)
3. **Nursing Considerations**: What should the nurse monitor or report?
4. **Suggested Actions**: What nursing interventions or escalations are appropriate?

User Query: {query if query else "Please analyze this medical image."}

Be thorough but concise. Focus on nursing-relevant findings.

Analysis:"""

        try:
            response = self.gemini.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def _analyze_medgemma(self, image: Image.Image, query: str) -> str:
        """Analyze with MedGemma 1.5."""
        import torch
        
        prompt = f"""Analyze this medical image for a nursing assessment.

Query: {query if query else "Describe the findings and nursing implications."}

Provide:
1. Image modality and type
2. Key findings (normal/abnormal)
3. Nursing considerations
4. Suggested actions"""

        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }]
        
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.medgemma.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.medgemma.generate(**inputs, max_new_tokens=600, do_sample=False)
        
        decoded = self.processor.decode(output[0], skip_special_tokens=True)
        # Extract just the assistant's response
        if "assistant" in decoded.lower():
            parts = decoded.split("assistant")
            if len(parts) > 1:
                return parts[-1].strip()
        return decoded


class LongitudinalAgent:
    """
    🆕 NEW: Compare X-rays over time (MedGemma 1.5 feature)
    Perfect for ICU nursing - track patient progression!
    """
    
    def __init__(self, gemini_model, medgemma_model=None, medgemma_processor=None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def compare(self, images: List[Image.Image], query: str, timestamps: List[str] = None) -> str:
        """Compare multiple images over time."""
        
        if not timestamps:
            timestamps = [f"Image {i+1}" for i in range(len(images))]
        
        # Try GPU backend first (remote 4090)
        if gpu_backend and gpu_backend.available:
            prompt = self._build_comparison_prompt(query, timestamps)
            result = gpu_backend.analyze_images(images, prompt, max_tokens=800)
            if result:
                return result
        
        if self.medgemma and self.processor:
            return self._compare_medgemma(images, query, timestamps)
        return self._compare_gemini(images, query, timestamps)
    
    def _build_comparison_prompt(self, query: str, timestamps: List[str]) -> str:
        """Build longitudinal comparison prompt."""
        time_labels = " → ".join(timestamps)
        return f"""Compare these medical images taken over time ({time_labels}).

Query: {query if query else "Analyze the progression and changes."}

Provide a NURSING-FOCUSED longitudinal assessment:
1. Baseline findings (first image)
2. Changes observed over time (improved/worsened/new/resolved)
3. Trending assessment (improving/stable/worsening)
4. Nursing implications for handoff
5. Recommended monitoring"""
    
    def _compare_gemini(self, images: List[Image.Image], query: str, timestamps: List[str]) -> str:
        """Compare with Gemini."""
        
        time_labels = " → ".join(timestamps)
        prompt = f"""You are NurseGemma's Longitudinal Imaging Specialist.

You are comparing {len(images)} medical images taken over time: {time_labels}

Query: {query if query else "Compare these images and describe the progression."}

Provide a NURSING-FOCUSED longitudinal assessment:

1. **Baseline (First Image)**: Key findings
2. **Progression**: What changed between images?
   - Improved findings
   - Worsened findings  
   - New findings
   - Resolved findings
3. **Trending Assessment**: Is the patient improving, stable, or declining?
4. **Nursing Implications**: 
   - What should be documented for handoff?
   - What should be reported to the provider?
   - Any urgent concerns?
5. **Recommended Monitoring**: What to watch for next

This is critical for shift handoffs and trending patient status!

Longitudinal Analysis:"""

        try:
            content = [prompt] + images
            response = self.gemini.generate_content(content)
            return response.text
        except Exception as e:
            return f"Error comparing images: {str(e)}"
    
    def _compare_medgemma(self, images: List[Image.Image], query: str, timestamps: List[str]) -> str:
        """Compare with MedGemma 1.5's longitudinal capability."""
        import torch
        
        time_labels = " → ".join(timestamps)
        prompt = f"""Compare these {len(images)} medical images taken over time ({time_labels}).

Query: {query if query else "Analyze the progression and changes."}

Provide:
1. Baseline findings (first image)
2. Changes observed over time
3. Trending assessment (improving/stable/worsening)
4. Nursing implications for handoff
5. Recommended monitoring"""

        # Build message with multiple images
        content = []
        for i, img in enumerate(images):
            content.append({"type": "image", "image": img})
            content.append({"type": "text", "text": f"[{timestamps[i]}]"})
        content.append({"type": "text", "text": prompt})
        
        messages = [{"role": "user", "content": content}]
        
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.medgemma.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.medgemma.generate(**inputs, max_new_tokens=800, do_sample=False)
        
        return self.processor.decode(output[0], skip_special_tokens=True)


class VolumetricAgent:
    """
    🆕 NEW: Analyze 3D CT/MRI volumes (MedGemma 1.5 feature)
    First open model with true 3D medical imaging support!
    """
    
    def __init__(self, gemini_model, medgemma_model=None, medgemma_processor=None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def analyze_volume(self, slices: List[Image.Image], modality: str, query: str) -> str:
        """Analyze a stack of CT/MRI slices as a volume."""
        
        if self.medgemma and self.processor:
            return self._analyze_medgemma(slices, modality, query)
        return self._analyze_gemini(slices, modality, query)
    
    def _analyze_gemini(self, slices: List[Image.Image], modality: str, query: str) -> str:
        """Analyze volume with Gemini."""
        
        prompt = f"""You are NurseGemma's Volumetric Imaging Specialist.

You are analyzing a {modality} volume consisting of {len(slices)} slices.

Query: {query if query else f"Analyze this {modality} volume and describe findings."}

Provide a comprehensive NURSING-FOCUSED 3D assessment:

1. **Scan Overview**: Type, region, quality
2. **Key Findings by Region**:
   - What pathology is present?
   - Location and extent (which slices/levels)
   - Size/measurements if relevant
3. **Clinical Correlation**:
   - How do these findings relate to patient presentation?
   - What symptoms would you expect?
4. **Nursing Considerations**:
   - Monitoring parameters
   - Potential complications to watch for
   - Patient positioning considerations
5. **Communication**: Key findings for provider report

3D Volume Analysis:"""

        try:
            # Send representative slices (first, middle, last) to avoid token limits
            if len(slices) > 5:
                indices = [0, len(slices)//4, len(slices)//2, 3*len(slices)//4, -1]
                selected = [slices[i] for i in indices]
            else:
                selected = slices
            
            content = [prompt] + selected
            response = self.gemini.generate_content(content)
            return response.text
        except Exception as e:
            return f"Error analyzing volume: {str(e)}"
    
    def _analyze_medgemma(self, slices: List[Image.Image], modality: str, query: str) -> str:
        """Analyze volume with MedGemma 1.5's 3D capability."""
        import torch
        
        prompt = f"""Analyze this {modality} volume ({len(slices)} slices).

Query: {query if query else "Provide comprehensive findings."}

Include:
1. Scan overview and quality
2. Key findings with anatomical localization
3. Clinical correlation
4. Nursing monitoring recommendations"""

        # Build message with all slices
        content = []
        for i, img in enumerate(slices):
            content.append({"type": "image", "image": img})
        content.append({"type": "text", "text": prompt})
        
        messages = [{"role": "user", "content": content}]
        
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.medgemma.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.medgemma.generate(**inputs, max_new_tokens=800, do_sample=False)
        
        return self.processor.decode(output[0], skip_special_tokens=True)


class LabReportAgent:
    """
    🆕 NEW: Extract structured data from lab report images (MedGemma 1.5 feature)
    18% improvement in extraction accuracy!
    """
    
    def __init__(self, gemini_model, medgemma_model=None, medgemma_processor=None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def extract_and_interpret(self, image: Image.Image, query: str = None) -> str:
        """Extract lab values and provide nursing interpretation."""
        
        if self.medgemma and self.processor:
            return self._extract_medgemma(image, query)
        return self._extract_gemini(image, query)
    
    def _extract_gemini(self, image: Image.Image, query: str) -> str:
        """Extract with Gemini."""
        
        prompt = f"""You are NurseGemma's Lab Report Specialist.

Extract all lab values from this lab report image and provide nursing interpretation.

{f"Specific question: {query}" if query else ""}

Provide:

1. **Extracted Lab Values** (table format):
| Test | Value | Units | Reference Range | Status |
|------|-------|-------|-----------------|--------|
(fill in all visible values)

2. **Critical Values** ⚠️
List any values that require immediate notification

3. **Abnormal Values Analysis**
For each abnormal value:
- Clinical significance
- Possible causes
- Nursing implications

4. **Trending** (if multiple dates visible)
Are values improving or worsening?

5. **Nursing Actions**
- Which values require immediate provider notification?
- What monitoring is indicated?
- Any medication considerations?

6. **Patient Education**
Key points to explain to patient/family

Lab Report Analysis:"""

        try:
            response = self.gemini.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error extracting lab values: {str(e)}"
    
    def _extract_medgemma(self, image: Image.Image, query: str) -> str:
        """Extract with MedGemma 1.5's lab extraction capability."""
        import torch
        
        prompt = f"""Extract all lab values from this lab report image.

{f"Question: {query}" if query else ""}

Provide:
1. Table of all lab values (test, value, units, reference, status)
2. Critical values requiring notification
3. Abnormal value analysis with nursing implications
4. Recommended actions"""

        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }]
        
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.medgemma.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.medgemma.generate(**inputs, max_new_tokens=800, do_sample=False)
        
        return self.processor.decode(output[0], skip_special_tokens=True)


class AnatomyAgent:
    """
    🆕 NEW: Anatomical localization in chest X-rays (MedGemma 1.5 feature)
    35% improvement in localization accuracy!
    """
    
    def __init__(self, gemini_model, medgemma_model=None, medgemma_processor=None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def localize(self, image: Image.Image, structure: str = None) -> str:
        """Identify and describe anatomical structures in CXR."""
        
        if self.medgemma and self.processor:
            return self._localize_medgemma(image, structure)
        return self._localize_gemini(image, structure)
    
    def _localize_gemini(self, image: Image.Image, structure: str) -> str:
        """Localize with Gemini."""
        
        specific = f"Focus on: {structure}" if structure else "Identify all major structures"
        
        prompt = f"""You are NurseGemma's Chest X-ray Anatomy Specialist.

{specific}

Provide a systematic anatomical review of this chest X-ray:

**Systematic CXR Review:**

1. **Airway** (trachea, carina, main bronchi)
   - Position, patency, any deviation

2. **Breathing** (lungs, pleura)
   - Lung fields: expansion, infiltrates, masses
   - Costophrenic angles: sharp or blunted
   - Pleural spaces: effusions, pneumothorax

3. **Circulation** (heart, mediastinum, great vessels)
   - Heart size (cardiothoracic ratio)
   - Mediastinal width
   - Aortic knob, pulmonary arteries

4. **Diaphragm**
   - Position, contour, free air underneath

5. **Everything else** (bones, soft tissues, devices)
   - Ribs, clavicles, spine
   - Tubes, lines, devices - position assessment
   - Soft tissue abnormalities

**Nursing Relevance:**
- Line/tube position verification
- Changes from prior (if known)
- Findings requiring immediate attention

Anatomical Review:"""

        try:
            response = self.gemini.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error analyzing anatomy: {str(e)}"
    
    def _localize_medgemma(self, image: Image.Image, structure: str) -> str:
        """Localize with MedGemma 1.5's improved localization."""
        import torch
        
        specific = f"Focus on: {structure}" if structure else "Systematic review all structures"
        
        prompt = f"""Provide anatomical localization for this chest X-ray.

{specific}

Include:
1. Airway assessment
2. Lung fields and pleura
3. Cardiac silhouette and mediastinum
4. Diaphragm position
5. Bones and soft tissues
6. Any tubes/lines/devices - verify positions
7. Nursing-relevant findings"""

        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }]
        
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.medgemma.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.medgemma.generate(**inputs, max_new_tokens=700, do_sample=False)
        
        return self.processor.decode(output[0], skip_special_tokens=True)


class ClinicalAgent:
    """Answers clinical nursing questions."""
    
    def __init__(self, model):
        self.model = model
    
    def answer(self, query: str) -> str:
        """Answer clinical question with nursing focus."""
        
        prompt = f"""You are NurseGemma, a clinical nursing AI assistant.

Answer this clinical question with a nursing focus:

Question: {query}

Provide:
1. **Direct Answer**: Clear, accurate response
2. **Nursing Considerations**: What nurses should know/monitor
3. **Safety Alerts**: Any critical warnings or contraindications
4. **When to Escalate**: When to notify the provider

Use proper medical terminology. Be concise but thorough.

Answer:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"


class EvidenceAgent:
    """Searches evidence-based practice guidelines."""
    
    def __init__(self, model):
        self.model = model
    
    def search(self, query: str) -> str:
        """Search for evidence-based practice information."""
        
        prompt = f"""You are NurseGemma's Evidence-Based Practice agent.

Search your knowledge for evidence-based guidelines related to:

Query: {query}

Provide:
1. **Summary of Evidence**: What does current evidence say?
2. **Key Guidelines**: Relevant professional guidelines (SCCM, AACN, CDC, AHA, etc.)
3. **Level of Evidence**: How strong is the evidence?
4. **Practice Implications**: How should this inform nursing practice?
5. **Sources**: Cite specific guidelines or landmark studies

Focus on:
- Critical care / ICU guidelines (SCCM, AACN)
- Nursing-specific recommendations
- Recent updates (within last 5 years when possible)

Evidence Summary:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error searching evidence: {str(e)}"


# ============================================================================
# AGENT INITIALIZATION
# ============================================================================

# Initialize base agents
orchestrator = OrchestratorAgent(gemini_model) if gemini_model else None
image_agent = ImageAgent(gemini_model, medgemma_model, medgemma_processor)
clinical_agent = ClinicalAgent(gemini_model) if gemini_model else None
evidence_agent = EvidenceAgent(gemini_model) if gemini_model else None

# New MedGemma 1.5 agents
longitudinal_agent = LongitudinalAgent(gemini_model, medgemma_model, medgemma_processor)
volumetric_agent = VolumetricAgent(gemini_model, medgemma_model, medgemma_processor)
lab_agent = LabReportAgent(gemini_model, medgemma_model, medgemma_processor)
anatomy_agent = AnatomyAgent(gemini_model, medgemma_model, medgemma_processor)

# Code Blue Agent (voice-activated ACLS documentation)
from code_blue_agent import CodeBlueAgent
code_blue_agent = CodeBlueAgent()


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_query(
    query: str, 
    image: Image.Image = None,
    image2: Image.Image = None,
    image3: Image.Image = None,
    audio = None,
    analysis_mode: str = "Auto-detect"
) -> Tuple[str, str]:
    """
    Process query through agentic pipeline.
    
    Returns: (response, routing_info)
    """
    
    if not gemini_model:
        return ("⚠️ Gemini API key not configured. Set GEMINI_API_KEY environment variable.", "")
    
    # Handle voice input first
    if audio is not None:
        transcription = transcribe_medical_audio(audio)
        query = transcription
        voice_note = f"\n🎤 **Voice Input Transcribed:** \"{transcription}\"\n\n---\n"
    else:
        voice_note = ""
    
    if not query.strip() and image is None:
        return ("Please enter a question, upload an image, or use voice input.", "")
    
    # Collect all images
    images = [img for img in [image, image2, image3] if img is not None]
    has_image = len(images) > 0
    has_multiple_images = len(images) > 1
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Manual mode override
    if analysis_mode != "Auto-detect":
        agent_name = {
            "Single Image Analysis": "IMAGE_AGENT",
            "Longitudinal Comparison": "LONGITUDINAL_AGENT",
            "3D Volume Analysis": "VOLUMETRIC_AGENT",
            "Lab Report Extraction": "LAB_AGENT",
            "Anatomical Localization": "ANATOMY_AGENT",
            "Clinical Q&A": "CLINICAL_AGENT",
            "Evidence Search": "EVIDENCE_AGENT"
        }.get(analysis_mode, "CLINICAL_AGENT")
        routing = {
            "agent": agent_name,
            "reason": f"Manual mode: {analysis_mode}",
            "nursing_focus": "User-selected analysis type"
        }
    else:
        # Auto-detect with orchestrator
        routing = orchestrator.route(query, has_image, has_multiple_images)
    
    agent_name = routing.get("agent", "CLINICAL_AGENT")
    
    routing_info = f"""{voice_note}### 🧠 Orchestrator Decision ({timestamp})

**Routed to:** `{agent_name}`  
**Reason:** {routing.get('reason', 'N/A')}  
**Nursing Focus:** {routing.get('nursing_focus', 'N/A')}

---
"""
    
    # Execute appropriate agent
    if agent_name == "LONGITUDINAL_AGENT" and has_multiple_images:
        response = longitudinal_agent.compare(images, query)
        routing_info += f"**Agent:** Longitudinal Comparison ({len(images)} images)"
        
    elif agent_name == "VOLUMETRIC_AGENT" and has_multiple_images:
        modality = "CT" if "ct" in query.lower() else "MRI" if "mri" in query.lower() else "CT/MRI"
        response = volumetric_agent.analyze_volume(images, modality, query)
        routing_info += f"**Agent:** 3D Volume Analysis ({len(images)} slices)"
        
    elif agent_name == "LAB_AGENT" and has_image:
        response = lab_agent.extract_and_interpret(images[0], query)
        routing_info += "**Agent:** Lab Report Extraction"
        
    elif agent_name == "ANATOMY_AGENT" and has_image:
        response = anatomy_agent.localize(images[0], query)
        routing_info += "**Agent:** Anatomical Localization"
        
    elif agent_name == "IMAGE_AGENT" and has_image:
        response = image_agent.analyze(images[0], query)
        routing_info += f"**Agent:** Image Analysis ({'MedGemma 1.5' if medgemma_available else 'Gemini'})"
        
    elif agent_name == "EVIDENCE_AGENT":
        response = evidence_agent.search(query)
        routing_info += "**Agent:** Evidence-Based Practice Search"
        
    else:
        response = clinical_agent.answer(query)
        routing_info += "**Agent:** Clinical Q&A"
    
    # Add model badge
    model_badge = "🟢 MedGemma 1.5" if medgemma_available else "🟡 Gemini"
    routing_info += f"\n**Model:** {model_badge}"
    
    return (response, routing_info)


def load_sample_image(sample_key: str) -> Image.Image:
    """Load a sample image."""
    if sample_key not in SAMPLE_IMAGES:
        return None
    
    path = SAMPLE_IMAGES[sample_key]["path"]
    if path.exists():
        return Image.open(path).convert("RGB")
    return None


# ============================================================================
# GRADIO UI
# ============================================================================

def create_ui():
    """Build the Gradio interface."""
    
    # Check for models at startup
    mg_available = init_medgemma()
    asr_available = init_medasr()
    
    with gr.Blocks(
        title="NurseGemma - Agentic Medical AI",
        theme=gr.themes.Soft(),
        css="""
        .sample-btn { margin: 2px !important; }
        .agent-box { background: #f0f7ff; padding: 10px; border-radius: 8px; }
        .new-feature { background: #e8f5e9; padding: 5px 10px; border-radius: 4px; font-size: 0.9em; }
        """
    ) as demo:
        
        # Header
        gr.Markdown("""
# 🩺 NurseGemma
## Agentic Medical AI for Nursing Practice

**Architecture:** Gemini Orchestrator → Specialized MedGemma 1.5 Agents

*Built by a nurse, for nurses | MedGemma Impact Challenge 2026*

---

### 🆕 New MedGemma 1.5 Features
""")
        
        # Feature badges
        with gr.Row():
            gr.Markdown("🎤 **MedASR Voice Input** - Hands-free dictation", elem_classes="new-feature")
            gr.Markdown("📊 **Longitudinal Comparison** - Track progression", elem_classes="new-feature")
            gr.Markdown("🚨 **Code Blue Mode** - Voice-activated ACLS", elem_classes="new-feature")
            gr.Markdown("🔬 **Lab Extraction** - Structured data", elem_classes="new-feature")
        
        gr.Markdown("---")
        
        # Status banner
        statuses = []
        if gpu_backend and gpu_backend.available:
            statuses.append("🟢 GPU Backend (4090)")
        statuses.append("🟢 MedGemma 1.5" if mg_available else "🟡 MedGemma (GPU required)")
        statuses.append("🟢 MedASR" if asr_available else "🟡 MedASR (GPU required)")
        statuses.append("🟢 Gemini" if gemini_model else "🔴 Gemini (API key needed)")
        gr.Markdown(f"**Model Status:** {' | '.join(statuses)}")
        
        if gpu_backend and gpu_backend.available:
            gr.Markdown("*🚀 Connected to remote RTX 4090 for real MedGemma 1.5 inference!*")
        
        with gr.Row():
            # Left: Input
            with gr.Column(scale=1):
                gr.Markdown("### 💬 Ask NurseGemma")
                
                # Analysis mode selector
                analysis_mode = gr.Radio(
                    choices=[
                        "Auto-detect",
                        "Single Image Analysis",
                        "Longitudinal Comparison",
                        "3D Volume Analysis", 
                        "Lab Report Extraction",
                        "Anatomical Localization",
                        "Clinical Q&A",
                        "Evidence Search"
                    ],
                    value="Auto-detect",
                    label="Analysis Mode"
                )
                
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'Compare these X-rays - is pneumonia improving?' or 'What are nursing considerations for Lasix?'",
                    lines=3
                )
                
                # 🆕 Voice input
                with gr.Accordion("🎤 Voice Input (MedASR)", open=False):
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="filepath",
                        label="Click to record (hands-free nursing mode)"
                    )
                    gr.Markdown("*82% fewer transcription errors than Whisper on medical speech!*")
                
                # Image inputs for longitudinal/volumetric
                with gr.Accordion("📷 Medical Images", open=True):
                    image_input = gr.Image(type="pil", label="Image 1 (Primary)")
                    
                    with gr.Row():
                        image_input2 = gr.Image(type="pil", label="Image 2 (Comparison/Slice)")
                        image_input3 = gr.Image(type="pil", label="Image 3 (Comparison/Slice)")
                    
                    gr.Markdown("*Upload multiple images for longitudinal comparison or 3D volume analysis*")
                    
                    gr.Markdown("**Quick Test - Sample X-rays:**")
                    with gr.Row():
                        for key, info in SAMPLE_IMAGES.items():
                            btn = gr.Button(info["label"], size="sm", elem_classes="sample-btn")
                            btn.click(
                                fn=lambda k=key: load_sample_image(k),
                                outputs=image_input
                            )
                
                submit_btn = gr.Button("🚀 Ask NurseGemma", variant="primary", size="lg")
            
            # Right: Output
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Response")
                response_output = gr.Markdown(label="Answer")
                
                with gr.Accordion("🔍 Agent Routing Details", open=True):
                    routing_output = gr.Markdown(label="Routing", elem_classes="agent-box")
        
        # Examples organized by feature
        gr.Markdown("---\n### 💡 Try These Examples")
        
        with gr.Tabs():
            with gr.Tab("🖼️ Image Analysis"):
                gr.Examples(
                    examples=[
                        ["Analyze this chest X-ray. What findings should I report?"],
                        ["Is there evidence of pneumonia? What nursing assessments are indicated?"],
                        ["Check tube and line positions on this X-ray"],
                    ],
                    inputs=[query_input],
                )
            
            with gr.Tab("📊 Longitudinal (NEW)"):
                gr.Examples(
                    examples=[
                        ["Compare these X-rays - is the pneumonia improving or worsening?"],
                        ["Track the progression between admission and day 3 X-rays"],
                        ["What changed between these two images? Update for handoff."],
                    ],
                    inputs=[query_input],
                )
            
            with gr.Tab("🔬 Lab Reports (NEW)"):
                gr.Examples(
                    examples=[
                        ["Extract all lab values from this report"],
                        ["Which values are critical and need immediate reporting?"],
                        ["Interpret these labs for a post-op cardiac patient"],
                    ],
                    inputs=[query_input],
                )
            
            with gr.Tab("💊 Clinical Q&A"):
                gr.Examples(
                    examples=[
                        ["What are the nursing considerations for a patient on Lasix?"],
                        ["My patient's potassium is 3.1 mEq/L. What should I do?"],
                        ["Interpret troponin trending: 0.04 → 0.15 → 0.38 over 6 hours"],
                        ["Patient has new onset confusion and left-sided weakness. Priority assessment?"],
                    ],
                    inputs=[query_input],
                )
            
            with gr.Tab("📚 Evidence"):
                gr.Examples(
                    examples=[
                        ["What does the evidence say about prone positioning in ARDS?"],
                        ["SCCM guidelines for early mobility in ICU"],
                        ["Best practices for preventing CAUTI"],
                    ],
                    inputs=[query_input],
                )
        
        # ========================================================================
        # 🚨 CODE BLUE MODE - Voice-Activated ACLS Documentation
        # ========================================================================
        gr.Markdown("---")
        gr.Markdown("## 🚨 Code Blue Mode")
        gr.Markdown("*Voice-activated cardiac arrest documentation with ACLS algorithm guidance*")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎤 Voice Commands")
                
                code_blue_audio = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🔴 Click to speak (hands-free during code)"
                )
                
                code_blue_text = gr.Textbox(
                    label="Or type command",
                    placeholder="CPR started, Epi given, V-fib, Shock delivered, ROSC...",
                    lines=1
                )
                
                with gr.Row():
                    start_code_btn = gr.Button("🚨 Start Code Blue", variant="primary")
                    end_code_btn = gr.Button("⏹️ End Code", variant="secondary")
                
                gr.Markdown("""
**Voice Commands:**
| Say This | Action |
|----------|--------|
| "CPR started" | Start CPR timer |
| "V-fib" / "Asystole" / "PEA" | Log rhythm |
| "Epi given" | Log epinephrine |
| "Shock delivered" | Log defibrillation |
| "ROSC" | Return of circulation |
| "Switch" | Compressor change |
""")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Code Blue Record")
                code_blue_output = gr.Markdown(
                    value="🎤 Say **'Code called'** or click **Start Code Blue** to begin documentation",
                    label="Live Documentation"
                )
                code_blue_status = gr.Markdown(value="", label="Status")
        
        # Code Blue processing function
        def process_code_blue(audio_path, text_input):
            """Process Code Blue voice/text input."""
            # Get text from voice or text input
            if audio_path:
                text = transcribe_medical_audio(audio_path)
            else:
                text = text_input
            
            if not text or not text.strip():
                return code_blue_agent.get_status() if code_blue_agent.session else "🎤 Waiting for input...", ""
            
            # Process through Code Blue agent
            response = code_blue_agent.process_voice(text)
            status = code_blue_agent.get_status() if code_blue_agent.session else ""
            
            return response, status
        
        def start_code():
            """Start a new Code Blue session."""
            return code_blue_agent.start_code(), code_blue_agent.get_status()
        
        def end_code():
            """End Code Blue and generate record."""
            if code_blue_agent.session:
                response = code_blue_agent.process_voice("code ended")
                return response, ""
            return "No active code", ""
        
        # Wire up Code Blue
        code_blue_audio.change(
            process_code_blue,
            inputs=[code_blue_audio, code_blue_text],
            outputs=[code_blue_output, code_blue_status]
        )
        
        code_blue_text.submit(
            process_code_blue,
            inputs=[code_blue_audio, code_blue_text],
            outputs=[code_blue_output, code_blue_status]
        )
        
        start_code_btn.click(
            start_code,
            outputs=[code_blue_output, code_blue_status]
        )
        
        end_code_btn.click(
            end_code,
            outputs=[code_blue_output, code_blue_status]
        )
        
        # Footer
        gr.Markdown("""
---
⚠️ **Disclaimer:** NurseGemma is an educational tool. All outputs require verification by qualified healthcare professionals. Not for diagnostic or treatment decisions.

*Powered by MedGemma 1.5 + MedASR + Gemini | [GitHub](https://github.com/AIHeartICU/NurseGemma)*
""")
        
        # Wire up
        submit_btn.click(
            process_query,
            inputs=[query_input, image_input, image_input2, image_input3, audio_input, analysis_mode],
            outputs=[response_output, routing_output]
        )
        
        query_input.submit(
            process_query,
            inputs=[query_input, image_input, image_input2, image_input3, audio_input, analysis_mode],
            outputs=[response_output, routing_output]
        )
    
    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=True)
