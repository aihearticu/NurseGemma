# NurseGemma Setup Instructions

## Quick Setup (5 minutes)

### Step 1: Get HuggingFace Token
1. Go to https://huggingface.co/settings/tokens
2. Click "Create new token"
3. Name it "kaggle" and select "Read" access
4. Copy the token (starts with `hf_...`)

### Step 2: Accept MedGemma License
1. Go to https://huggingface.co/google/medgemma-1.5-4b-it
2. Click "Agree and access repository"
3. Wait for instant approval

### Step 3: Add Token to Kaggle
1. Open the notebook: https://www.kaggle.com/code/aihearticu/nursegemma-ai-companion-for-nurses
2. Click "Edit" to open in editor mode
3. Click **Add-ons** (top menu) → **Secrets**
4. Click "Add a new secret"
5. Label: `HUGGINGFACE_TOKEN`
6. Value: Paste your `hf_...` token
7. Click "Save"

### Step 4: Enable GPU
1. In the notebook sidebar, find "Accelerator"
2. Select "GPU T4 x2" (free tier)
3. Click "Save & Run All"

### Step 5: Wait for Model to Load
- First run takes ~3-5 minutes to download model
- Subsequent runs are faster (cached)

---

## Troubleshooting

### Error: "Access to model is restricted"
- Make sure you accepted the license at https://huggingface.co/google/medgemma-1.5-4b-it
- Verify your token is correct in Kaggle Secrets

### Error: "CUDA out of memory"
- GPU T4 x2 should work, but if issues:
  - Try restarting the kernel
  - Reduce `max_new_tokens` in generation

### Error: "Secret not found"
- Double-check the secret name is exactly: `HUGGINGFACE_TOKEN`
- Make sure you clicked "Save" after adding

---

## Notebook URLs

- **NurseGemma Notebook**: https://www.kaggle.com/code/aihearticu/nursegemma-ai-companion-for-nurses
- **Competition Page**: https://www.kaggle.com/competitions/med-gemma-impact-challenge

---

## What the Notebook Does

When running successfully, you'll see:

1. **Setup Output**:
   ```
   ✓ Successfully authenticated with HuggingFace!
   Loading google/medgemma-1.5-4b-it...
   ✓ MedGemma 1.5 loaded successfully!
   Device: cuda:0
   ```

2. **Quick Explain Demo**: Explains "atrial fibrillation" in plain language

3. **Med Helper Demo**: Shows metoprolol info and drug interactions

4. **Shift Sidekick Demo**: Generates SBAR handoff report

5. **Clinical Ref Demo**: Interprets potassium lab value

6. **Gradio UI**: Interactive interface with all 4 modules

---

## Expected Outputs

### Quick Explain Example
```
Atrial fibrillation (often called "AFib") is when your heart beats
irregularly instead of in a steady rhythm...

[Plain language explanation continues]
```

### Med Helper Example
```
## What is Metoprolol?
Metoprolol is a beta-blocker medication that helps slow down your
heart rate and lower blood pressure...

## Side Effects to Monitor
- Dizziness
- Fatigue
- Cold hands/feet
...
```

### SBAR Report Example
```
**SITUATION**
72-year-old male admitted 3 days ago for community-acquired pneumonia,
currently stable on day 3 of antibiotics...

**BACKGROUND**
PMH: HTN, DM2, COPD...
```
