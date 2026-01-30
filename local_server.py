#!/usr/bin/env python3
"""
🩺 NurseGemma Local Server
Run MedGemma 4B locally on your GPU with a public Gradio link.

Requirements:
- NVIDIA GPU with 16GB+ VRAM (RTX 3090, 4090, A100, etc.)
- HuggingFace account with MedGemma access
- Python 3.10+

Usage:
    pip install torch transformers accelerate gradio huggingface_hub
    huggingface-cli login
    python local_server.py
"""

import torch
import gradio as gr
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image

print("🩺 NurseGemma Local Server")
print("=" * 50)

# Check GPU
if not torch.cuda.is_available():
    print("❌ No GPU detected! MedGemma requires CUDA.")
    exit(1)

gpu_name = torch.cuda.get_device_name(0)
gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"✅ GPU: {gpu_name} ({gpu_mem:.1f} GB)")

# Load model
print("\n📥 Loading MedGemma 4B...")
MODEL_ID = "google/medgemma-4b-it"

processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID, 
    torch_dtype=torch.bfloat16, 
    device_map="cuda"
)
print(f"✅ Model loaded on {next(model.parameters()).device}")

# Prompts
FAMILY_PROMPT = """You are NurseGemma, a warm and knowledgeable nurse educator helping families understand medical information.

RULES:
- Use simple, clear language (8th grade reading level)
- Avoid medical jargon - if you must use a term, explain it
- Be warm, reassuring, and empathetic
- Use helpful analogies when explaining complex concepts
- Keep responses concise but complete
- Remind this is educational - consult their healthcare team for decisions"""

NURSE_PROMPT = """You are NurseGemma, an experienced clinical nurse assistant for healthcare professionals.

RULES:
- Use proper medical terminology
- Be concise and clinically accurate
- For wounds: include staging, measurements, tissue types, drainage, recommendations
- For scans: describe findings systematically, note nursing implications
- Include relevant interventions and monitoring parameters
- Reference evidence-based practice when applicable"""


def chat(message, history, mode):
    """Process chat with optional image."""
    text = message.get("text", "") if isinstance(message, dict) else str(message)
    files = message.get("files", []) if isinstance(message, dict) else []
    
    if not text.strip() and not files:
        return ""
    
    # Select prompt
    system = FAMILY_PROMPT if "Family" in mode else NURSE_PROMPT
    
    # Build conversation
    conv = [system + "\n\n"]
    for h in history[-4:]:
        role = "User" if h["role"] == "user" else "NurseGemma"
        conv.append(f"{role}: {h['content']}\n")
    conv.append(f"User: {text}\nNurseGemma:")
    
    # Build message content
    content = [{"type": "text", "text": "".join(conv)}]
    
    # Add image if provided
    if files:
        try:
            img = Image.open(files[0]).convert("RGB")
            content.insert(0, {"type": "image", "image": img})
        except Exception as e:
            print(f"Image error: {e}")
    
    messages = [{"role": "user", "content": content}]
    
    # Generate
    inputs = processor.apply_chat_template(
        messages, 
        add_generation_prompt=True, 
        tokenize=True, 
        return_dict=True, 
        return_tensors="pt"
    ).to("cuda", dtype=torch.bfloat16)
    
    with torch.inference_mode():
        output = model.generate(
            **inputs, 
            max_new_tokens=512, 
            do_sample=True, 
            temperature=0.7,
            top_p=0.95
        )
    
    response = processor.decode(output[0], skip_special_tokens=True)
    # Extract just the response
    if "NurseGemma:" in response:
        response = response.split("NurseGemma:")[-1].strip()
    
    return response


# Gradio UI
DESCRIPTION = """
**🩺 NurseGemma** — Your AI Nursing Companion

Running **MedGemma 4B** locally on GPU.

👨‍👩‍👧 **Family Mode**: Plain language explanations  
👩‍⚕️ **Nurse Mode**: Professional clinical assessments

Upload images for wound assessment or scan interpretation!
"""

with gr.Blocks(title="🩺 NurseGemma", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🩺 NurseGemma")
    gr.Markdown(DESCRIPTION)
    
    mode = gr.Radio(
        ["👨‍👩‍👧 Family Mode", "👩‍⚕️ Nurse Mode"], 
        value="👨‍👩‍👧 Family Mode", 
        label="Mode"
    )
    
    gr.ChatInterface(
        fn=chat,
        type="messages",
        multimodal=True,
        textbox=gr.MultimodalTextbox(
            file_types=["image"], 
            placeholder="Ask a question or upload an image..."
        ),
        additional_inputs=[mode],
    )
    
    gr.Markdown("""
    ---
    ⚠️ *Educational only. Consult healthcare professionals for medical decisions.*
    
    [GitHub](https://github.com/AIHeartICU/NurseGemma) • MedGemma Impact Challenge 2026
    """)

if __name__ == "__main__":
    print("\n🚀 Starting server...")
    demo.launch(share=True)
