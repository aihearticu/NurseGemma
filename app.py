"""
NurseGemma - Agentic Medical AI for Nursing

Architecture:
- Gemini (Orchestrator): Routes queries, reasoning, multi-step planning
- MedGemma 1.5 4B (Medical Specialist): Image interpretation, clinical QA
- Evidence Agent (RAG): Guidelines, PubMed (future)

Built for MedGemma Impact Challenge 2026 - Agentic Category
"""

import os
import json
import torch
import gradio as gr
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Sample medical images - paths relative to app directory
# For demo: users upload their own OR use examples from Kaggle datasets
SAMPLE_IMAGES = {
    "chest_xray": {
        "path": "samples/chest_xray.jpg",
        "label": "Chest X-ray",
        "category": "X-ray",
        "description": "PA chest radiograph - upload your own or use example"
    },
    "ct_scan": {
        "path": "samples/ct_scan.jpg", 
        "label": "CT Scan",
        "category": "CT",
        "description": "Axial CT slice - upload your own or use example"
    },
    "wound_photo": {
        "path": "samples/wound.jpg",
        "label": "Wound Assessment",
        "category": "Wound",
        "description": "Wound photo for staging - upload your own"
    }
}

# For web demo, we'll generate placeholder images if samples don't exist
def ensure_sample_images():
    """Create placeholder images for demo if real samples not present."""
    import os
    os.makedirs("samples", exist_ok=True)
    
    for key, info in SAMPLE_IMAGES.items():
        path = info["path"]
        if not os.path.exists(path):
            # Create a simple placeholder
            try:
                img = Image.new('RGB', (512, 512), color=(50, 50, 50))
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.text((150, 240), f"Upload {info['label']}", fill=(200, 200, 200))
                draw.text((120, 270), "Click 'Upload Image' above", fill=(150, 150, 150))
                img.save(path)
            except:
                pass

# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

class OrchestratorAgent:
    """
    Gemini-based orchestrator that:
    1. Analyzes user intent
    2. Routes to appropriate specialist agent
    3. Synthesizes multi-agent responses
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def classify_intent(self, query: str, has_image: bool = False) -> dict:
        """Classify the user's intent and determine routing."""
        
        prompt = f"""You are an AI orchestrator for NurseGemma, a nursing-focused medical AI assistant.

Analyze this query and determine the best agent to handle it.

Query: "{query}"
Has Image: {has_image}

Available agents:
1. IMAGE_AGENT - For analyzing medical images (X-rays, CT, MRI, wounds)
2. CLINICAL_QA_AGENT - For clinical questions (medications, lab values, procedures)
3. EVIDENCE_AGENT - For evidence-based practice questions (guidelines, research)
4. PATIENT_SUMMARY_AGENT - For generating handoffs, summaries, documentation

Respond in JSON format:
{{
    "primary_agent": "AGENT_NAME",
    "secondary_agents": ["AGENT_NAME"],
    "reasoning": "brief explanation",
    "nursing_context": "how this relates to nursing practice",
    "follow_up_questions": ["suggested follow-ups"]
}}

JSON Response:"""
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON from response
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            return {
                "primary_agent": "CLINICAL_QA_AGENT" if not has_image else "IMAGE_AGENT",
                "secondary_agents": [],
                "reasoning": f"Default routing (parse error: {str(e)})",
                "nursing_context": "General nursing query",
                "follow_up_questions": []
            }
    
    def synthesize_response(self, query: str, agent_responses: dict, routing: dict) -> str:
        """Synthesize responses from multiple agents into cohesive answer."""
        
        prompt = f"""You are NurseGemma, synthesizing information from multiple AI agents into a helpful nursing response.

Original Query: "{query}"

Agent Responses:
{json.dumps(agent_responses, indent=2)}

Routing Context:
{json.dumps(routing, indent=2)}

Create a unified, nursing-focused response that:
1. Directly answers the user's question
2. Highlights nursing-relevant considerations
3. Uses clear, professional language
4. Includes any important safety considerations
5. Suggests follow-up actions if appropriate

Response:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error synthesizing response: {str(e)}"


class ImageAgent:
    """
    MedGemma-based agent for medical image interpretation.
    Specialized for nursing-relevant findings.
    """
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.loaded = False
        
    def load_model(self):
        """Lazy load MedGemma model."""
        if self.loaded:
            return
            
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from huggingface_hub import login
        
        if HF_TOKEN:
            login(token=HF_TOKEN)
        
        MODEL_ID = "google/medgemma-1.5-4b-it"
        self.processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        self.model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        self.loaded = True
        
    def analyze(self, image: Image.Image, query: str, context: str = "") -> str:
        """Analyze medical image with nursing focus."""
        
        self.load_model()
        
        prompt = f"""You are a medical imaging AI assistant helping nurses interpret images.

CONTEXT: {context if context else "General nursing assessment"}

TASK: Analyze this medical image and provide:
1. Image type/modality identification
2. Key findings (normal and abnormal)
3. Nursing-relevant observations
4. Suggested nursing actions or monitoring

USER QUERY: {query if query else "Please analyze this medical image."}

Analysis:"""

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
        ).to(self.model.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=800, do_sample=False)
        
        response = self.processor.decode(output[0], skip_special_tokens=True)
        if "Analysis:" in response:
            response = response.split("Analysis:")[-1].strip()
        
        return response


class ClinicalQAAgent:
    """
    MedGemma-based agent for clinical questions.
    Handles medications, lab values, procedures, protocols.
    """
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.loaded = False
        
    def load_model(self):
        """Lazy load MedGemma model."""
        if self.loaded:
            return
            
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from huggingface_hub import login
        
        if HF_TOKEN:
            login(token=HF_TOKEN)
        
        MODEL_ID = "google/medgemma-1.5-4b-it"
        self.processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        self.model = AutoModelForImageTextToText.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        self.loaded = True
        
    def answer(self, question: str, context: str = "") -> str:
        """Answer clinical nursing question."""
        
        self.load_model()
        
        prompt = f"""You are a clinical nursing AI assistant with expertise in:
- Medication administration and interactions
- Lab value interpretation
- Clinical procedures and protocols
- Patient assessment findings

CONTEXT: {context if context else "General nursing practice"}

QUESTION: {question}

Provide a clear, nursing-focused answer that includes:
1. Direct answer to the question
2. Nursing considerations
3. Important safety points
4. When to escalate or notify provider

Answer:"""

        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True,
            tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self.model.device, dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=600, do_sample=False)
        
        response = self.processor.decode(output[0], skip_special_tokens=True)
        if "Answer:" in response:
            response = response.split("Answer:")[-1].strip()
        
        return response


class EvidenceAgent:
    """
    RAG-based agent for evidence-based practice queries.
    Searches guidelines (SCCM, AACN) and literature.
    """
    
    def __init__(self):
        # TODO: Implement RAG with PubMed/guidelines
        pass
        
    def search(self, query: str) -> str:
        """Search evidence base for nursing practice guidelines."""
        # Placeholder - would integrate RAG here
        return f"[Evidence Agent] Searching guidelines for: {query}\n\nNote: Full RAG integration coming soon. For now, recommend consulting SCCM, AACN, and specialty guidelines directly."


# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Initialize agents
orchestrator = None
image_agent = None
clinical_qa_agent = None
evidence_agent = None

def initialize_agents():
    """Initialize all agents."""
    global orchestrator, image_agent, clinical_qa_agent, evidence_agent
    
    if GEMINI_API_KEY:
        orchestrator = OrchestratorAgent(GEMINI_API_KEY)
    
    image_agent = ImageAgent()
    clinical_qa_agent = ClinicalQAAgent()
    evidence_agent = EvidenceAgent()


def load_sample_image(image_key: str) -> Image.Image:
    """Load a sample image by key."""
    if image_key not in SAMPLE_IMAGES:
        return None
    
    path = SAMPLE_IMAGES[image_key]["path"]
    try:
        if os.path.exists(path):
            return Image.open(path).convert("RGB")
        else:
            return None
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def process_query(query: str, image: Image.Image = None) -> tuple:
    """
    Main processing function with agentic routing.
    
    Returns: (response, routing_info, agent_log)
    """
    global orchestrator, image_agent, clinical_qa_agent, evidence_agent
    
    has_image = image is not None
    agent_responses = {}
    
    # Step 1: Orchestrator classifies intent
    if orchestrator:
        routing = orchestrator.classify_intent(query, has_image)
    else:
        routing = {
            "primary_agent": "IMAGE_AGENT" if has_image else "CLINICAL_QA_AGENT",
            "secondary_agents": [],
            "reasoning": "Default routing (no Gemini API key)",
            "nursing_context": "Direct routing",
            "follow_up_questions": []
        }
    
    routing_display = f"""**🧠 Orchestrator Routing:**
- Primary Agent: `{routing['primary_agent']}`
- Secondary: `{routing.get('secondary_agents', [])}`
- Reasoning: {routing.get('reasoning', 'N/A')}
- Nursing Context: {routing.get('nursing_context', 'N/A')}
"""
    
    # Step 2: Route to primary agent
    primary = routing["primary_agent"]
    
    if primary == "IMAGE_AGENT" and has_image:
        agent_responses["IMAGE_AGENT"] = image_agent.analyze(image, query)
    elif primary == "CLINICAL_QA_AGENT":
        agent_responses["CLINICAL_QA_AGENT"] = clinical_qa_agent.answer(query)
    elif primary == "EVIDENCE_AGENT":
        agent_responses["EVIDENCE_AGENT"] = evidence_agent.search(query)
    else:
        # Default to clinical QA
        agent_responses["CLINICAL_QA_AGENT"] = clinical_qa_agent.answer(query)
    
    # Step 3: Call secondary agents if needed
    for agent_name in routing.get("secondary_agents", []):
        if agent_name == "EVIDENCE_AGENT" and agent_name not in agent_responses:
            agent_responses["EVIDENCE_AGENT"] = evidence_agent.search(query)
    
    # Step 4: Synthesize final response
    if orchestrator and len(agent_responses) > 1:
        final_response = orchestrator.synthesize_response(query, agent_responses, routing)
    else:
        # Single agent response
        final_response = list(agent_responses.values())[0]
    
    # Build agent log
    agent_log = "**📋 Agent Execution Log:**\n"
    for agent, response in agent_responses.items():
        agent_log += f"\n**{agent}:**\n{response[:500]}{'...' if len(response) > 500 else ''}\n"
    
    return final_response, routing_display, agent_log


def create_sample_gallery():
    """Create HTML for sample image gallery."""
    html = """
    <div style="padding: 15px; background: #f5f5f5; border-radius: 8px; margin: 10px 0;">
        <h4 style="margin-top: 0;">📁 Recommended Test Images</h4>
        <p style="color: #666; font-size: 14px;">
            For best results, upload medical images from these public datasets:
        </p>
        <ul style="font-size: 14px;">
            <li><strong>Chest X-rays:</strong> <a href="https://www.kaggle.com/datasets/nih-chest-xrays/data" target="_blank">NIH Chest X-ray Dataset</a></li>
            <li><strong>CT Scans:</strong> <a href="https://www.kaggle.com/datasets/mohamedhanyyy/chest-ctscan-images" target="_blank">Chest CT-Scan Images</a></li>
            <li><strong>Brain MRI:</strong> <a href="https://www.kaggle.com/datasets/navoneel/brain-mri-images-for-brain-tumor-detection" target="_blank">Brain MRI Dataset</a></li>
            <li><strong>Skin/Wound:</strong> <a href="https://www.kaggle.com/datasets/fanconic/skin-cancer-malignant-vs-benign" target="_blank">Skin Cancer Dataset</a></li>
        </ul>
        <p style="color: #888; font-size: 12px; margin-bottom: 0;">
            💡 Tip: Download sample images from Kaggle and upload them to test NurseGemma's image analysis.
        </p>
    </div>
    """
    return html


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def build_interface():
    """Build the Gradio interface."""
    
    initialize_agents()
    
    with gr.Blocks(title="NurseGemma - Agentic Medical AI", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🩺 NurseGemma
        ## Agentic Medical AI for Nursing Practice
        
        **Architecture:** Gemini (Orchestrator) → MedGemma 1.5 (Medical Specialist)
        
        *Built by a nurse, for nurses. MedGemma Impact Challenge 2026.*
        
        ---
        """)
        
        with gr.Row():
            # Left column - Input
            with gr.Column(scale=1):
                gr.Markdown("### 💬 Ask NurseGemma")
                
                query_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g., 'Analyze this chest X-ray for my ICU patient' or 'What are the nursing considerations for Lasix?'",
                    lines=3
                )
                
                with gr.Accordion("📷 Upload Medical Image", open=True):
                    image_input = gr.Image(type="pil", label="Upload Image (X-ray, CT, MRI, wound photo)")
                    gr.Markdown("*Supports: JPEG, PNG, DICOM (converted). Max 10MB.*")
                
                submit_btn = gr.Button("🚀 Process Query", variant="primary")
            
            # Right column - Output
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Response")
                
                response_output = gr.Markdown(label="NurseGemma Response")
                
                with gr.Accordion("🔍 Agent Details", open=False):
                    routing_output = gr.Markdown(label="Routing")
                    agent_log_output = gr.Markdown(label="Agent Log")
        
        # Sample images gallery
        gr.Markdown("---\n### 🖼️ Sample Medical Images\n*Click dropdown above to use these for testing*")
        gr.HTML(create_sample_gallery())
        
        # Example queries
        gr.Markdown("---\n### 💡 Example Queries")
        gr.Examples(
            examples=[
                ["Analyze this chest X-ray. What findings should I report to the physician?", None],
                ["What are the nursing considerations for a patient on Lasix (furosemide)?", None],
                ["My patient's potassium is 3.1. What should I do?", None],
                ["Assess this wound for staging and suggest documentation.", None],
                ["What does the evidence say about prone positioning in ARDS?", None],
                ["Patient has new onset confusion and left-sided weakness. What's my priority assessment?", None],
            ],
            inputs=[query_input, image_input],
        )
        
        # Footer
        gr.Markdown("""
        ---
        ⚠️ **Disclaimer**: NurseGemma is an educational tool. All outputs require verification by qualified healthcare professionals. 
        Not for diagnostic or treatment decisions.
        
        *Powered by Google MedGemma 1.5 + Gemini | Built for the MedGemma Impact Challenge 2026*
        """)
        
        # Wire up the interface
        submit_btn.click(
            process_query,
            inputs=[query_input, image_input],
            outputs=[response_output, routing_output, agent_log_output]
        )
    
    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demo = build_interface()
    demo.launch(share=True)
