"""
NurseGemma - Agentic Medical AI for Nursing Practice
MedGemma Impact Challenge 2026 - Agentic Category

Refactored with:
- Streaming responses for real-time feedback
- Conversation memory for contextual interactions
- Confidence-based agent routing
- Type hints for code quality
- Progress indicators for long operations

Architecture:
- Gemini 2.0 Flash (Orchestrator): Intent classification, routing, synthesis
- MedGemma 1.5 4B (Medical Specialist): Image analysis, clinical QA (when GPU available)
- Gemini (Fallback): When MedGemma not available
- Evidence Agent: PubMed/guidelines search via Gemini grounding

Built by a nurse, for nurses.
"""

from __future__ import annotations

import os
import json
import base64
from typing import Generator, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from io import BytesIO
from pathlib import Path

import gradio as gr
from PIL import Image

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
# TYPE DEFINITIONS
# ============================================================================

class AgentType(Enum):
    """Available agent types for routing."""
    IMAGE_AGENT = "IMAGE_AGENT"
    CLINICAL_AGENT = "CLINICAL_AGENT"
    EVIDENCE_AGENT = "EVIDENCE_AGENT"


@dataclass
class RoutingDecision:
    """Structured routing decision from orchestrator."""
    agent: AgentType
    confidence: float  # 0.0 to 1.0
    reason: str
    nursing_focus: str
    
    @property
    def confidence_label(self) -> str:
        """Human-readable confidence level."""
        if self.confidence >= 0.8:
            return "High"
        elif self.confidence >= 0.5:
            return "Medium"
        return "Low"


@dataclass
class ConversationMessage:
    """Single message in conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    agent_used: Optional[str] = None
    has_image: bool = False


@dataclass
class ConversationMemory:
    """Manages conversation history for context."""
    messages: list[ConversationMessage] = field(default_factory=list)
    max_history: int = 10
    
    def add_message(self, role: str, content: str, agent_used: Optional[str] = None, has_image: bool = False) -> None:
        """Add a message to history, maintaining max size."""
        self.messages.append(ConversationMessage(
            role=role,
            content=content,
            agent_used=agent_used,
            has_image=has_image
        ))
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context_string(self, max_messages: int = 5) -> str:
        """Get recent conversation as context string."""
        if not self.messages:
            return ""
        
        recent = self.messages[-max_messages:]
        context_parts = []
        for msg in recent:
            prefix = "User" if msg.role == "user" else "NurseGemma"
            context_parts.append(f"{prefix}: {msg.content[:200]}...")
        
        return "\n".join(context_parts)
    
    def clear(self) -> None:
        """Clear conversation history."""
        self.messages = []


# ============================================================================
# GEMINI CLIENT
# ============================================================================

import google.generativeai as genai

def init_gemini() -> Optional[genai.GenerativeModel]:
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

def init_medgemma() -> bool:
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
    """Routes queries to appropriate specialist agents with confidence scoring."""
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
    
    def route(self, query: str, has_image: bool, context: str = "") -> RoutingDecision:
        """Classify intent and determine routing with confidence score."""
        
        context_section = f"\nRecent conversation context:\n{context}\n" if context else ""
        
        prompt = f"""You are the orchestrator for NurseGemma, a nursing-focused medical AI.

Analyze this query and route to the best agent. Also provide a confidence score.
{context_section}
Query: "{query}"
Has Image Attached: {has_image}

Agents:
- IMAGE_AGENT: Analyze medical images (X-rays, CT, wounds)
- CLINICAL_AGENT: Answer clinical questions (meds, labs, procedures, assessments)
- EVIDENCE_AGENT: Search evidence-based practice, guidelines, research

Rules:
- If image attached AND query mentions image → IMAGE_AGENT (high confidence)
- If asking about guidelines, evidence, research, "what does evidence say" → EVIDENCE_AGENT
- Clinical questions about meds, labs, patient care → CLINICAL_AGENT
- Consider conversation context for follow-up questions
- Default to CLINICAL_AGENT if unclear (lower confidence)

Respond in JSON only:
{{"agent": "AGENT_NAME", "confidence": 0.0-1.0, "reason": "brief explanation", "nursing_focus": "how this helps nursing practice"}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Parse JSON
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            data = json.loads(text)
            
            return RoutingDecision(
                agent=AgentType[data.get("agent", "CLINICAL_AGENT")],
                confidence=float(data.get("confidence", 0.7)),
                reason=data.get("reason", "N/A"),
                nursing_focus=data.get("nursing_focus", "N/A")
            )
        except Exception as e:
            # Default routing with low confidence
            if has_image:
                return RoutingDecision(
                    agent=AgentType.IMAGE_AGENT,
                    confidence=0.6,
                    reason=f"Image attached (error: {e})",
                    nursing_focus="Image assessment"
                )
            return RoutingDecision(
                agent=AgentType.CLINICAL_AGENT,
                confidence=0.5,
                reason=f"Default (error: {e})",
                nursing_focus="Clinical support"
            )


class ImageAgent:
    """Analyzes medical images with nursing focus and streaming support."""
    
    def __init__(self, gemini_model: genai.GenerativeModel, medgemma_model: Any = None, medgemma_processor: Any = None):
        self.gemini = gemini_model
        self.medgemma = medgemma_model
        self.processor = medgemma_processor
    
    def analyze_stream(self, image: Image.Image, query: str, context: str = "") -> Generator[str, None, None]:
        """Analyze medical image with streaming output."""
        
        # Try MedGemma first if available (no streaming support yet)
        if self.medgemma and self.processor:
            yield self._analyze_medgemma(image, query)
            return
        
        # Stream with Gemini
        yield from self._analyze_gemini_stream(image, query, context)
    
    def _analyze_gemini_stream(self, image: Image.Image, query: str, context: str = "") -> Generator[str, None, None]:
        """Stream analysis with Gemini (multimodal)."""
        
        context_section = f"\nConversation context:\n{context}\n" if context else ""
        
        prompt = f"""You are NurseGemma, a nursing-focused medical image analyst.
{context_section}
Analyze this medical image and provide:
1. **Image Type**: What kind of image is this?
2. **Key Findings**: What do you observe? (normal and abnormal)
3. **Nursing Considerations**: What should the nurse monitor or report?
4. **Suggested Actions**: What nursing interventions or escalations are appropriate?

User Query: {query if query else "Please analyze this medical image."}

Be thorough but concise. Use clinical terminology appropriate for nursing professionals.

Analysis:"""

        try:
            response = self.gemini.generate_content(
                [prompt, image],
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield full_response
        except Exception as e:
            yield f"Error analyzing image: {str(e)}"
    
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
    """Answers clinical nursing questions with streaming support."""
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
    
    def answer_stream(self, query: str, context: str = "") -> Generator[str, None, None]:
        """Stream clinical answer with nursing focus."""
        
        context_section = f"\nRecent conversation:\n{context}\n" if context else ""
        
        prompt = f"""You are NurseGemma, a clinical nursing AI assistant.
{context_section}
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
            response = self.model.generate_content(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield full_response
        except Exception as e:
            yield f"Error: {str(e)}"


class EvidenceAgent:
    """Searches evidence-based practice guidelines with streaming."""
    
    def __init__(self, model: genai.GenerativeModel):
        self.model = model
    
    def search_stream(self, query: str, context: str = "") -> Generator[str, None, None]:
        """Stream evidence-based practice search."""
        
        context_section = f"\nConversation context:\n{context}\n" if context else ""
        
        prompt = f"""You are NurseGemma's Evidence-Based Practice agent.
{context_section}
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
            response = self.model.generate_content(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield full_response
        except Exception as e:
            yield f"Error searching evidence: {str(e)}"


# ============================================================================
# MAIN PROCESSING
# ============================================================================

# Initialize agents
orchestrator = OrchestratorAgent(gemini_model) if gemini_model else None
image_agent = ImageAgent(gemini_model, medgemma_model, medgemma_processor)
clinical_agent = ClinicalAgent(gemini_model) if gemini_model else None
evidence_agent = EvidenceAgent(gemini_model) if gemini_model else None

# Global conversation memory (per session via Gradio state)
def create_memory() -> ConversationMemory:
    """Create new conversation memory instance."""
    return ConversationMemory()


def process_query_stream(
    query: str, 
    image: Optional[Image.Image], 
    memory: ConversationMemory
) -> Generator[tuple[str, str, ConversationMemory], None, None]:
    """
    Process query through agentic pipeline with streaming.
    
    Yields: (response, routing_info, updated_memory)
    """
    
    if not gemini_model:
        yield ("⚠️ Gemini API key not configured. Set GEMINI_API_KEY environment variable.", "", memory)
        return
    
    if not query.strip() and image is None:
        yield ("Please enter a question or upload an image.", "", memory)
        return
    
    has_image = image is not None
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Get conversation context
    context = memory.get_context_string()
    
    # Step 1: Orchestrator routes the query
    routing = orchestrator.route(query, has_image, context)
    
    routing_info = f"""### 🧠 Orchestrator Decision ({timestamp})

**Routed to:** `{routing.agent.value}`  
**Confidence:** {routing.confidence:.0%} ({routing.confidence_label})  
**Reason:** {routing.reason}  
**Nursing Focus:** {routing.nursing_focus}

---
"""
    
    # Add user message to memory
    memory.add_message("user", query, has_image=has_image)
    
    # Step 2: Execute the appropriate agent with streaming
    agent_name = routing.agent
    
    if agent_name == AgentType.IMAGE_AGENT and has_image:
        routing_info += f"**Agent:** Image Analysis ({'MedGemma' if medgemma_model else 'Gemini'})"
        for response in image_agent.analyze_stream(image, query, context):
            yield (response, routing_info, memory)
        # Store final response
        memory.add_message("assistant", response, agent_used="IMAGE_AGENT")
        
    elif agent_name == AgentType.EVIDENCE_AGENT:
        routing_info += "**Agent:** Evidence-Based Practice Search"
        for response in evidence_agent.search_stream(query, context):
            yield (response, routing_info, memory)
        memory.add_message("assistant", response, agent_used="EVIDENCE_AGENT")
        
    else:  # CLINICAL_AGENT
        routing_info += "**Agent:** Clinical Q&A"
        for response in clinical_agent.answer_stream(query, context):
            yield (response, routing_info, memory)
        memory.add_message("assistant", response, agent_used="CLINICAL_AGENT")


def load_sample_image(sample_key: str) -> Optional[Image.Image]:
    """Load a sample image."""
    if sample_key not in SAMPLE_IMAGES:
        return None
    
    path = SAMPLE_IMAGES[sample_key]["path"]
    if path.exists():
        return Image.open(path).convert("RGB")
    return None


def clear_conversation(memory: ConversationMemory) -> tuple[str, str, ConversationMemory]:
    """Clear conversation history and outputs."""
    memory.clear()
    return ("", "", memory)


# ============================================================================
# GRADIO UI
# ============================================================================

def create_ui() -> gr.Blocks:
    """Build the Gradio interface with streaming and memory."""
    
    # Check for MedGemma at startup
    medgemma_available = init_medgemma()
    
    with gr.Blocks(
        title="NurseGemma - Agentic Medical AI",
        theme=gr.themes.Soft(),
        css="""
        .sample-btn { margin: 2px !important; }
        .agent-box { background: #f0f7ff; padding: 10px; border-radius: 8px; }
        .confidence-high { color: #22c55e; font-weight: bold; }
        .confidence-medium { color: #f59e0b; }
        .confidence-low { color: #ef4444; }
        """
    ) as demo:
        
        # Session state for conversation memory
        memory_state = gr.State(create_memory)
        
        # Header
        gr.Markdown("""
# 🩺 NurseGemma
## Agentic Medical AI for Nursing Practice

**Architecture:** Gemini Orchestrator → Specialized Agents (Image, Clinical, Evidence)  
**Features:** 🔄 Streaming responses | 💾 Conversation memory | 📊 Confidence scoring

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
                
                with gr.Row():
                    submit_btn = gr.Button("🚀 Ask NurseGemma", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
            
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
        
        # Wire up - streaming version
        submit_btn.click(
            process_query_stream,
            inputs=[query_input, image_input, memory_state],
            outputs=[response_output, routing_output, memory_state]
        )
        
        # Also submit on Enter
        query_input.submit(
            process_query_stream,
            inputs=[query_input, image_input, memory_state],
            outputs=[response_output, routing_output, memory_state]
        )
        
        # Clear conversation
        clear_btn.click(
            clear_conversation,
            inputs=[memory_state],
            outputs=[response_output, routing_output, memory_state]
        )
    
    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demo = create_ui()
    demo.queue()  # Enable queuing for streaming
    demo.launch(share=True)
