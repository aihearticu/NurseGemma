import torch
import gradio as gr
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image

print("Loading MedGemma 4B...")
MODEL_ID = "google/medgemma-4b-it"
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda"
)
print(f"✅ Loaded on {next(model.parameters()).device}")

FAMILY_PROMPT = """You are NurseGemma, a warm nurse educator helping families understand medical information.
Use simple language (8th grade level). Avoid jargon. Be warm and reassuring."""

NURSE_PROMPT = """You are NurseGemma, a clinical nurse assistant for healthcare professionals.
Use proper medical terminology. Be concise and clinically accurate."""

def chat(message, history, mode, image):
    text = message if isinstance(message, str) else ""
    if not text.strip() and image is None:
        return ""
    
    system = FAMILY_PROMPT if "Family" in mode else NURSE_PROMPT
    conv = [system + "\n"]
    
    for h in history:
        if isinstance(h, dict):
            role = h.get("role", "")
            content = h.get("content", "")
            if role == "user":
                conv.append(f"User: {content}\n")
            elif role == "assistant":
                conv.append(f"NurseGemma: {content}\n")
    
    conv.append(f"User: {text}\nNurseGemma:")
    
    content = [{"type": "text", "text": "".join(conv)}]
    
    if image is not None:
        content.insert(0, {"type": "image", "image": image})
    
    messages = [{"role": "user", "content": content}]
    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, 
        tokenize=True, return_dict=True, return_tensors="pt"
    ).to("cuda", dtype=torch.bfloat16)
    
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=512, do_sample=True, temperature=0.7)
    
    response = processor.decode(output[0], skip_special_tokens=True)
    return response.split("NurseGemma:")[-1].strip()

with gr.Blocks(title="NurseGemma") as demo:
    gr.Markdown("# 🩺 NurseGemma\n**Running MedGemma 4B on RTX 4090**")
    
    mode = gr.Radio(["👨‍👩‍👧 Family Mode", "👩‍⚕️ Nurse Mode"], value="👨‍👩‍👧 Family Mode", label="Mode")
    image = gr.Image(type="pil", label="Upload Image (wound, scan, etc.)")
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(placeholder="Ask a question...", label="Message")
    
    def respond(message, chat_history, mode, image):
        response = chat(message, chat_history, mode, image)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot, mode, image], [msg, chatbot])
    
    gr.Markdown("---\n⚠️ Educational only. Not for medical decisions.")

demo.launch(share=True)
