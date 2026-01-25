#!/usr/bin/env python3
"""
NurseGemma Quick Test - CPU Mode with 4-bit Quantization
For full GPU testing, run on Kaggle notebook
"""

import os
os.environ['KAGGLE_USERNAME'] = 'aihearticu'
os.environ['KAGGLE_KEY'] = '568f017fb62efc90e39c48848942a80f'
os.environ['KERAS_BACKEND'] = 'torch'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU

import warnings
warnings.filterwarnings('ignore')

import time
from datetime import datetime

print("=" * 70)
print("NURSEGEMMA QUICK TEST - CPU MODE")
print("=" * 70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Note: CPU inference is slow. For production, use Kaggle GPU.")

# Load model
print("\n[LOADING] MedGemma 1.5 4B (CPU mode - this will take a few minutes)...")
start_load = time.time()

import keras_hub

try:
    model = keras_hub.models.Gemma3CausalLM.from_preset(
        'kaggle://keras/medgemma/keras/medgemma_1.5_instruct_4b'
    )
    load_time = time.time() - start_load
    print(f"Model loaded in {load_time:.1f} seconds")
    MODEL_LOADED = True
except Exception as e:
    print(f"Error loading model: {e}")
    MODEL_LOADED = False

if not MODEL_LOADED:
    print("\nModel loading failed. Try running on Kaggle with GPU.")
    exit(1)

def ask_medgemma(system_prompt: str, query: str, max_tokens: int = 256) -> str:
    """Query MedGemma"""
    prompt = f"<start_of_turn>user\n{system_prompt}\n\n{query}<end_of_turn>\n<start_of_turn>model\n"
    response = model.generate(prompt, max_length=max_tokens)
    if "<start_of_turn>model" in response:
        response = response.split("<start_of_turn>model")[-1]
    return response.strip()

# Quick tests
print("\n" + "=" * 70)
print("RUNNING QUICK TESTS (3 samples)")
print("=" * 70)

tests = [
    ("Quick Explain", "Explain atrial fibrillation to a worried family member in simple terms."),
    ("Med Helper", "What should a nurse know before giving Heparin? Include safety checks."),
    ("Lab Interpretation", "Potassium is 3.1 mEq/L in a patient on Lasix. What should the nurse do?"),
]

for name, query in tests:
    print(f"\n--- {name} ---")
    print(f"Query: {query[:60]}...")

    start = time.time()
    result = ask_medgemma("You are a nursing assistant.", query)
    duration = time.time() - start

    print(f"Time: {duration:.1f}s")
    print(f"Response ({len(result)} chars):")
    print("-" * 40)
    print(result[:800] if len(result) > 800 else result)
    print("-" * 40)

print("\n" + "=" * 70)
print("QUICK TEST COMPLETE")
print("For full comprehensive testing, run on Kaggle notebook with GPU.")
print("=" * 70)
