"""
NurseGemma GPU Backend Server
Runs MedGemma 1.5 + MedASR on your RTX 4090

This API server handles the heavy GPU inference.
The HuggingFace Space frontend calls this for real MedGemma power.

Usage:
    python gpu_backend.py

Then set GPU_BACKEND_URL in your frontend to point here.
"""

import os
import io
import base64
import torch
import tempfile
from pathlib import Path
from PIL import Image
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ============================================================================
# CONFIGURATION
# ============================================================================

HF_TOKEN = os.environ.get("HF_TOKEN", "")
MEDGEMMA_MODEL_ID = "google/medgemma-1.5-4b-it"
MEDASR_MODEL_ID = "google/medasr"

# ============================================================================
# MODEL LOADING
# ============================================================================

print("🚀 NurseGemma GPU Backend Starting...")
print(f"🎮 CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"🎮 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# Login to HuggingFace
if HF_TOKEN:
    from huggingface_hub import login
    login(token=HF_TOKEN)
    print("✅ Logged into HuggingFace")

# Load MedGemma 1.5
print(f"📥 Loading {MEDGEMMA_MODEL_ID}...")
from transformers import AutoProcessor, AutoModelForImageTextToText

medgemma_processor = AutoProcessor.from_pretrained(MEDGEMMA_MODEL_ID)
medgemma_model = AutoModelForImageTextToText.from_pretrained(
    MEDGEMMA_MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="cuda"
)
print(f"✅ MedGemma 1.5 loaded on {next(medgemma_model.parameters()).device}")

# Load MedASR
medasr_model = None
medasr_processor = None
try:
    print(f"📥 Loading {MEDASR_MODEL_ID}...")
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor as ASRProcessor
    
    medasr_processor = ASRProcessor.from_pretrained(MEDASR_MODEL_ID)
    medasr_model = AutoModelForSpeechSeq2Seq.from_pretrained(
        MEDASR_MODEL_ID,
        torch_dtype=torch.float16,
        device_map="cuda"
    )
    print(f"✅ MedASR loaded")
except Exception as e:
    print(f"⚠️ MedASR not available: {e}")

print("🎉 GPU Backend Ready!")

# ============================================================================
# API SERVER
# ============================================================================

app = FastAPI(
    title="NurseGemma GPU Backend",
    description="MedGemma 1.5 + MedASR inference on RTX 4090",
    version="1.5.0"
)

# Allow CORS for HF Space frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageAnalysisRequest(BaseModel):
    prompt: str
    images_base64: List[str]  # Base64 encoded images
    max_tokens: int = 800


class TextRequest(BaseModel):
    prompt: str
    max_tokens: int = 600


class TranscriptionResponse(BaseModel):
    text: str
    model: str


def decode_image(base64_str: str) -> Image.Image:
    """Decode base64 image."""
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    image_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(image_data)).convert("RGB")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "medgemma": "loaded",
        "medasr": "loaded" if medasr_model else "unavailable",
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
        "vram_free_gb": torch.cuda.memory_reserved(0) / 1024**3 if torch.cuda.is_available() else 0
    }


@app.post("/analyze")
async def analyze_images(request: ImageAnalysisRequest):
    """
    Analyze medical images with MedGemma 1.5.
    Supports single images, longitudinal comparison, and 3D volumes.
    """
    try:
        # Decode images
        images = [decode_image(b64) for b64 in request.images_base64]
        
        # Build message with images
        content = []
        for i, img in enumerate(images):
            content.append({"type": "image", "image": img})
            if len(images) > 1:
                content.append({"type": "text", "text": f"[Image {i+1}]"})
        content.append({"type": "text", "text": request.prompt})
        
        messages = [{"role": "user", "content": content}]
        
        # Process
        inputs = medgemma_processor.apply_chat_template(
            messages, 
            add_generation_prompt=True,
            tokenize=True, 
            return_dict=True, 
            return_tensors="pt"
        ).to("cuda", dtype=torch.bfloat16)
        
        # Generate
        with torch.inference_mode():
            output = medgemma_model.generate(
                **inputs, 
                max_new_tokens=request.max_tokens, 
                do_sample=False
            )
        
        response = medgemma_processor.decode(output[0], skip_special_tokens=True)
        
        # Extract assistant response
        if "assistant" in response.lower():
            parts = response.split("assistant")
            if len(parts) > 1:
                response = parts[-1].strip()
        
        return {"response": response, "model": "medgemma-1.5-4b-it", "num_images": len(images)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clinical")
async def clinical_qa(request: TextRequest):
    """Answer clinical questions with MedGemma 1.5."""
    try:
        messages = [{
            "role": "user",
            "content": [{"type": "text", "text": request.prompt}]
        }]
        
        inputs = medgemma_processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        ).to("cuda", dtype=torch.bfloat16)
        
        with torch.inference_mode():
            output = medgemma_model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                do_sample=False
            )
        
        response = medgemma_processor.decode(output[0], skip_special_tokens=True)
        
        return {"response": response, "model": "medgemma-1.5-4b-it"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe medical audio with MedASR.
    82% fewer errors than Whisper on medical dictation!
    """
    if not medasr_model:
        raise HTTPException(status_code=503, detail="MedASR not available")
    
    try:
        import librosa
        
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load and process audio
        audio_data, sr = librosa.load(tmp_path, sr=16000)
        
        # Transcribe with MedASR
        inputs = medasr_processor(audio_data, sampling_rate=sr, return_tensors="pt")
        inputs = inputs.to("cuda")
        
        with torch.inference_mode():
            generated_ids = medasr_model.generate(**inputs, max_new_tokens=256)
        
        transcription = medasr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Cleanup
        os.unlink(tmp_path)
        
        return TranscriptionResponse(text=transcription, model="medasr")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "NurseGemma GPU Backend",
        "version": "1.5.0",
        "endpoints": {
            "/health": "Health check",
            "/analyze": "POST - Analyze medical images",
            "/clinical": "POST - Clinical Q&A",
            "/transcribe": "POST - Transcribe medical audio"
        },
        "models": {
            "medgemma": MEDGEMMA_MODEL_ID,
            "medasr": MEDASR_MODEL_ID if medasr_model else "unavailable"
        }
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NurseGemma GPU Backend")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7861, help="Port to bind to")
    parser.add_argument("--share", action="store_true", help="Create public URL via ngrok")
    args = parser.parse_args()
    
    if args.share:
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(args.port)
            print(f"\n🌐 Public URL: {public_url}")
            print(f"📋 Set GPU_BACKEND_URL={public_url} in your frontend\n")
        except ImportError:
            print("⚠️ Install pyngrok for --share: pip install pyngrok")
    
    uvicorn.run(app, host=args.host, port=args.port)
