"""
NurseGemma - Quick Test Script for Google Colab
Copy this into a Colab notebook with GPU enabled.

Instructions:
1. Go to colab.research.google.com
2. Create new notebook
3. Runtime → Change runtime type → GPU (T4)
4. Copy this code and run each cell
"""

# =============================================================================
# CELL 1: Install dependencies
# =============================================================================
# !pip install -q transformers accelerate requests pillow

# =============================================================================
# CELL 2: Setup and authenticate
# =============================================================================
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Authenticate with HuggingFace
from huggingface_hub import login

# Option A: Use your token directly (replace with your actual token)
# login(token="hf_YOUR_TOKEN_HERE")

# Option B: Interactive login
login()

# =============================================================================
# CELL 3: Load MedGemma
# =============================================================================
from transformers import AutoProcessor, AutoModelForImageTextToText

MODEL_ID = "google/medgemma-1.5-4b-it"

print("Loading MedGemma 1.5 4B...")
processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)
print(f"Model loaded on: {next(model.parameters()).device}")

# =============================================================================
# CELL 4: Text inference helper
# =============================================================================
def ask_medgemma(prompt: str, max_tokens: int = 500) -> str:
    """Query MedGemma with a text prompt"""
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)

    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)

    return processor.decode(output[0], skip_special_tokens=True)

# =============================================================================
# CELL 5: Image inference helper
# =============================================================================
import requests
from PIL import Image
from io import BytesIO

def analyze_image(image_url: str, prompt: str, max_tokens: int = 800) -> str:
    """Analyze a medical image with MedGemma"""
    # Download image
    response = requests.get(image_url, headers={"User-Agent": "NurseGemma"}, timeout=30)
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # Build multimodal message
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt}
        ]
    }]

    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)

    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)

    return processor.decode(output[0], skip_special_tokens=True)

# =============================================================================
# CELL 6: TEST 1 - Explain CHF to family
# =============================================================================
import time

print("=" * 60)
print("TEST 1: Explain CHF to worried family member")
print("=" * 60)

start = time.time()
result = ask_medgemma("""You are a helpful nursing assistant.
A patient's daughter asks: "What is CHF? The doctor keeps saying it but I don't understand."

Explain CHF (Congestive Heart Failure) in simple terms for a worried family member.
Use 8th grade reading level, simple analogies, and a compassionate tone.""")

print(f"\nResponse time: {time.time() - start:.1f}s\n")
print(result)

# =============================================================================
# CELL 7: TEST 2 - Critical Lab Analysis
# =============================================================================
print("\n" + "=" * 60)
print("TEST 2: Critical Lab Analysis (Digoxin + Low K+)")
print("=" * 60)

start = time.time()
result = ask_medgemma("""You are a clinical nursing reference assistant.

Patient: 68F with CHF on Digoxin 0.125mg daily
Labs: K+ 3.2 mEq/L (normal 3.5-5.0), Digoxin level 1.8 ng/mL (therapeutic 0.8-2.0)
Vitals: BP 92/58, HR 52

Analyze this situation:
1. What is the clinical concern with low K+ and Digoxin?
2. Priority level (Routine/Urgent/Critical)?
3. What should the nurse do?
4. Generate SBAR for MD notification.""")

print(f"\nResponse time: {time.time() - start:.1f}s\n")
print(result)

# =============================================================================
# CELL 8: TEST 3 - Chest X-Ray Analysis (MULTIMODAL)
# =============================================================================
print("\n" + "=" * 60)
print("TEST 3: Chest X-Ray Analysis (Pneumonia)")
print("=" * 60)

CXR_URL = "https://upload.wikimedia.org/wikipedia/commons/8/87/X-ray_of_lobar_pneumonia.jpg"
print(f"Analyzing: {CXR_URL}\n")

start = time.time()
result = analyze_image(CXR_URL, """You are a clinical nurse educator.
Analyze this chest X-ray and provide:
1. Key findings (lung fields, heart size, any abnormalities)
2. Clinical significance
3. Nursing implications (what to monitor, when to notify MD)
4. Urgency level: ROUTINE / ATTENTION / URGENT / CRITICAL""")

print(f"\nResponse time: {time.time() - start:.1f}s\n")
print(result)

# =============================================================================
# CELL 9: TEST 4 - Wound Assessment (MULTIMODAL)
# =============================================================================
print("\n" + "=" * 60)
print("TEST 4: Pressure Injury Wound Assessment")
print("=" * 60)

WOUND_URL = "https://upload.wikimedia.org/wikipedia/commons/f/fc/Grade3.jpg"
print(f"Analyzing: {WOUND_URL}\n")

start = time.time()
result = analyze_image(WOUND_URL, """You are a wound care nurse specialist.
Analyze this wound per NPIAP guidelines and provide:
1. Staging (Stage 1/2/3/4/Unstageable/DTPI) with justification
2. Tissue types visible (granulation, slough, eschar, epithelial)
3. Wound characteristics
4. Nursing recommendations (dressing, positioning, when to escalate)
5. Urgency level""")

print(f"\nResponse time: {time.time() - start:.1f}s\n")
print(result)

# =============================================================================
# CELL 10: Summary
# =============================================================================
print("\n" + "=" * 60)
print("NURSEGEMMA TEST COMPLETE")
print("=" * 60)
print("""
Tests completed:
1. ✓ Text: Explain CHF to family
2. ✓ Text: Critical lab analysis
3. ✓ Multimodal: CXR interpretation
4. ✓ Multimodal: Wound assessment

MedGemma 1.5 4B is working with both text and image inputs!
""")
