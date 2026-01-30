"""
NurseGemma - Agentic Medical AI for Nursing Practice
MedGemma Impact Challenge 2026 - Agentic Category

Architecture:
- Gemini 2.0 Flash (Orchestrator): Intent classification, routing, synthesis
- MedGemma 1.5 4B (Medical Specialist): Image analysis, clinical QA (when GPU available)
- Gemini (Fallback): When MedGemma not available
- Evidence Agent: PubMed/guidelines search via Gemini grounding

Built by a nurse, for nurses.
"""

import os
import json
import base64
import gradio as gr
from PIL import Image
from pathlib import Path
from datetime import datetime
from io import BytesIO

# ============================================================================
# CONFIGURATION
# ============================================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
USE_MEDGEMMA = os.environ.get("USE_MEDGEMMA", "false").lower() == "true"

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
# MEDGEMMA CLIENT (Optional - requires GPU)
# ============================================================================

medgemma_model = None
medgemma_processor = None

def init_medgemma():
    """Initialize MedGemma if available."""
    global medgemma_model, medgemma_processor
    
    if not USE_MEDGEMMA:
        return False
    
    try:
        import torch
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from huggingface_hub import login
        
        if HF_TOKEN:
            login(token=HF_TOKEN)
        
        MODEL_ID = "google/medgemma-4b-it"
        medgemma_processor = AutoProcessor.from_pretrained(MODEL_ID)
        medgemma_model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto"
        )
        print(f"✅ MedGemma loaded on {next(medgemma_model.parameters()).device}")
        return True
    except Exception as e:
        print(f"⚠️ MedGemma not available: {e}")
        return False

# ============================================================================
# AGENTS
# ============================================================================

class OrchestratorAgent:
    """Routes queries to appropriate specialist agents."""
    
    def __init__(self, model):
        self.model = model
    
    def route(self, query: str, has_image: bool) -> dict:
        """Classify intent and determine routing."""
        
        prompt = f"""You are the orchestrator for NurseGemma, a nursing-focused medical AI.

Analyze this query and route to the best agent.

Query: "{query}"
Has Image Attached: {has_image}

Agents:
- IMAGE_AGENT: Analyze medical images (X-rays, CT, wounds)
- CLINICAL_AGENT: Answer clinical questions (meds, labs, procedures, assessments)
- EVIDENCE_AGENT: Search evidence-based practice, guidelines, research

Rules:
- If image attached AND query mentions image → IMAGE_AGENT
- If asking about guidelines, evidence, research, "what does evidence say" → EVIDENCE_AGENT
- Clinical questions about meds, labs, patient care → CLINICAL_AGENT
- Default to CLINICAL_AGENT if unclear

Respond in JSON only:
{{"agent": "AGENT_NAME", "reason": "brief explanation", "nursing_focus": "how this helps nursing practice"}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Parse JSON
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
        except Exception as e:
            # Default routing
            if has_image:
                return {"agent": "IMAGE_AGENT", "reason": "Image attached", "nursing_focus": "Image assessment"}
            return {"agent": "CLINICAL_AGENT", "reason": f"Default (error: {e})", "nursing_focus": "Clinical support"}


class ImageAgent:
    """Analyzes medical images with nursing focus."""
    
    def __init__(self, gemini_model, medgemma_model=None, medgemma_processor=None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def analyze(self, image: Image.Image, query: str) -> str:
        """Analyze medical image."""
        
        # Try MedGemma first if available
        if self.medgemma and self.processor:
            return self._analyze_medgemma(image, query)
        
        # Fallback to Gemini
        return self._analyze_gemini(image, query)
    
    def _analyze_gemini(self, image: Image.Image, query: str) -> str:
        """Analyze with Gemini (multimodal)."""
        
        prompt = f"""You are NurseGemma, a nursing-focused medical image analyst.

Analyze this medical image and provide:
1. **Image Type**: What kind of image is this?
2. **Key Findings**: What do you observe? (normal and abnormal)
3. **Nursing Considerations**: What should the nurse monitor or report?
4. **Suggested Actions**: What nursing interventions or escalations are appropriate?

User Query: {query if query else "Please analyze this medical image."}

Be thorough but concise. Use clinical terminology appropriate for nursing professionals.

Analysis:"""

        try:
            response = self.model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def _analyze_medgemma(self, image: Image.Image, query: str) -> str:
        """Analyze with MedGemma (when GPU available)."""
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
2. **Key Guidelines**: Relevant professional guidelines (SCCM, AACN, CDC, etc.)
3. **Level of Evidence**: How strong is the evidence?
4. **Practice Implications**: How should this inform nursing practice?
5. **Sources**: Cite specific guidelines or landmark studies when possible

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
# MAIN PROCESSING
# ============================================================================

# Initialize agents
orchestrator = OrchestratorAgent(gemini_model) if gemini_model else None
image_agent = ImageAgent(gemini_model, medgemma_model, medgemma_processor)
clinical_agent = ClinicalAgent(gemini_model) if gemini_model else None
evidence_agent = EvidenceAgent(gemini_model) if gemini_model else None

def process_query(query: str, image: Image.Image = None) -> tuple:
    """
    Process query through agentic pipeline.
    
    Returns: (response, routing_info)
    """
    
    if not gemini_model:
        return ("⚠️ Gemini API key not configured. Set GEMINI_API_KEY environment variable.", "")
    
    if not query.strip() and image is None:
        return ("Please enter a question or upload an image.", "")
    
    has_image = image is not None
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Step 1: Orchestrator routes the query
    routing = orchestrator.route(query, has_image)
    agent_name = routing.get("agent", "CLINICAL_AGENT")
    
    routing_info = f"""### 🧠 Orchestrator Decision ({timestamp})

**Routed to:** `{agent_name}`  
**Reason:** {routing.get('reason', 'N/A')}  
**Nursing Focus:** {routing.get('nursing_focus', 'N/A')}

---
"""
    
    # Step 2: Execute the appropriate agent
    if agent_name == "IMAGE_AGENT" and has_image:
        response = image_agent.analyze(image, query)
        routing_info += f"**Agent:** Image Analysis ({'MedGemma' if medgemma_model else 'Gemini'})"
    elif agent_name == "EVIDENCE_AGENT":
        response = evidence_agent.search(query)
        routing_info += "**Agent:** Evidence-Based Practice Search"
    else:
        response = clinical_agent.answer(query)
        routing_info += "**Agent:** Clinical Q&A"
    
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
    
    # Check for MedGemma at startup
    medgemma_available = init_medgemma()
    
    with gr.Blocks(
        title="NurseGemma - Agentic Medical AI",
        theme=gr.themes.Soft(),
        css="""
        .sample-btn { margin: 2px !important; }
        .agent-box { background: #f0f7ff; padding: 10px; border-radius: 8px; }
        """
    ) as demo:
        
        # Header
        gr.Markdown("""
# 🩺 NurseGemma
## Agentic Medical AI for Nursing Practice

**Architecture:** Gemini Orchestrator → Specialized Agents (Image, Clinical, Evidence)

*Built by a nurse, for nurses | MedGemma Impact Challenge 2026*
""")
        
        # Status banner
        model_status = "🟢 MedGemma Active" if medgemma_available else "🟡 Using Gemini (MedGemma requires GPU)"
        gr.Markdown(f"**Model Status:** {model_status}")
        
        with gr.Row():
            # Left: Input
            with gr.Column(scale=1):
                gr.Markdown("### 💬 Ask NurseGemma")
                
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'What are nursing considerations for Lasix?' or 'Analyze this X-ray'",
                    lines=3
                )
                
                with gr.Accordion("📷 Medical Image (Optional)", open=True):
                    image_input = gr.Image(type="pil", label="Upload X-ray, CT, wound photo, etc.")
                    
                    gr.Markdown("**Quick Test - Click to load sample:**")
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
        
        # Examples
        gr.Markdown("---\n### 💡 Try These Examples")
        gr.Examples(
            examples=[
                ["Analyze this chest X-ray. What findings should I report?", None],
                ["What are the nursing considerations for a patient on Lasix (furosemide)?", None],
                ["My patient's potassium is 3.1 mEq/L. What should I do?", None],
                ["What does the evidence say about prone positioning in ARDS?", None],
                ["Patient has new onset confusion and left-sided weakness. Priority assessment?", None],
                ["Interpret troponin trending: 0.04 → 0.15 → 0.38 over 6 hours", None],
            ],
            inputs=[query_input, image_input],
        )
        
        # Footer
        gr.Markdown("""
---
⚠️ **Disclaimer:** NurseGemma is an educational tool. All outputs require verification by qualified healthcare professionals. Not for diagnostic or treatment decisions.

*Powered by Google MedGemma + Gemini | [GitHub](https://github.com/AIHeartICU/NurseGemma)*
""")
        
        # Wire up
        submit_btn.click(
            process_query,
            inputs=[query_input, image_input],
            outputs=[response_output, routing_output]
        )
        
        # Also submit on Enter
        query_input.submit(
            process_query,
            inputs=[query_input, image_input],
            outputs=[response_output, routing_output]
        )
    
    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=True)
