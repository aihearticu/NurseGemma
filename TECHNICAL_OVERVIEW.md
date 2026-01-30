# NurseGemma: Agentic Medical AI for Nursing Practice

**MedGemma Impact Challenge 2026 - Technical Overview**

*Team: AIHeartICU | Category: Agentic AI*

---

## Executive Summary

NurseGemma is a multi-agent medical AI system designed specifically for nursing workflows. Unlike generic medical AI tools, NurseGemma understands the unique needs of bedside nurses—from interpreting a chest X-ray to answering a worried family member's questions to finding evidence-based practice guidelines.

**Key Innovation:** A nursing-focused agentic architecture where a Gemini orchestrator routes queries to specialized MedGemma-powered agents based on intent classification.

---

## 1. Problem Statement

### The Nursing Crisis
- **4+ million nurses** in the US alone
- **40% of nursing time** spent on documentation, not patient care
- **Families wait anxiously** with questions while nurses are stretched thin
- **Information gap** between clinical findings and family understanding

### Why Existing Solutions Fall Short
- Generic medical AI doesn't understand nursing workflows
- Single-model approaches can't handle diverse nursing tasks
- No tool designed by nurses, for nurses

---

## 2. Solution Architecture

### Multi-Agent Design

```
                         ┌─────────────────────────┐
           User Query →  │   GEMINI ORCHESTRATOR   │
                         │  (Intent Classification) │
                         └───────────┬─────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            ↓                        ↓                        ↓
   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
   │   IMAGE AGENT   │     │  CLINICAL AGENT │     │ EVIDENCE AGENT  │
   │   (MedGemma)    │     │   (MedGemma)    │     │    (Gemini)     │
   │                 │     │                 │     │                 │
   │ • X-ray/CT/MRI  │     │ • Medications   │     │ • Guidelines    │
   │ • Wound photos  │     │ • Lab values    │     │ • PubMed/SCCM   │
   │ • Nursing focus │     │ • Assessments   │     │ • Best practices│
   └─────────────────┘     └─────────────────┘     └─────────────────┘
            │                        │                        │
            └────────────────────────┴────────────────────────┘
                                     │
                         ┌───────────┴───────────┐
                         │  Nursing-Focused      │
                         │  Response             │
                         └───────────────────────┘
```

### Agent Descriptions

| Agent | Model | Function |
|-------|-------|----------|
| **Orchestrator** | Gemini 2.0 Flash | Classifies intent, routes to specialist, synthesizes responses |
| **Image Agent** | MedGemma 1.5 4B | Analyzes X-rays, CT, MRI, wound photos with nursing focus |
| **Clinical Agent** | MedGemma 1.5 4B | Answers medication, lab value, and assessment questions |
| **Evidence Agent** | Gemini + Grounding | Searches evidence-based practice guidelines |

---

## 3. Technical Implementation

### 3.1 Orchestrator (Intent Classification)

The orchestrator uses Gemini 2.0 Flash to classify user intent and route to the appropriate agent:

```python
routing = orchestrator.route(query, has_image=True)
# Returns: {"agent": "IMAGE_AGENT", "reason": "X-ray analysis requested"}
```

**Routing Logic:**
- Image attached + image-related query → IMAGE_AGENT
- Keywords: "evidence", "guidelines", "research" → EVIDENCE_AGENT
- Clinical questions (meds, labs, assessments) → CLINICAL_AGENT

### 3.2 Image Agent (MedGemma)

When available, uses MedGemma 1.5 4B for medical image analysis:

```python
response = image_agent.analyze(image, query)
# Provides: Image type, key findings, nursing considerations, suggested actions
```

**Fallback:** When GPU unavailable, uses Gemini's multimodal capabilities.

### 3.3 Clinical Agent

Answers clinical nursing questions with structured responses:
- Direct answer
- Nursing considerations
- Safety alerts
- When to escalate

### 3.4 Evidence Agent

Searches for evidence-based practice information:
- Professional guidelines (SCCM, AACN, CDC)
- Level of evidence assessment
- Practice implications

---

## 4. Effective Use of HAI-DEF Models

### MedGemma 1.5 4B
- **Primary use:** Medical image interpretation
- **Secondary use:** Clinical Q&A
- **Nursing focus:** All prompts emphasize nursing-relevant findings

### Integration Approach
1. MedGemma for specialized medical tasks
2. Gemini for orchestration and fallback
3. Graceful degradation when GPU unavailable

---

## 5. Real-World Impact

### Target Users
1. **Bedside nurses** - Quick clinical decision support
2. **Families** - Plain-English explanations
3. **Nurse educators** - Teaching tool for image interpretation

### Use Cases

| Scenario | Agent | Value |
|----------|-------|-------|
| "Analyze this chest X-ray" | Image | Faster assessment documentation |
| "What should I monitor on Lasix?" | Clinical | Safer medication administration |
| "Evidence for prone positioning?" | Evidence | Evidence-based practice support |
| "My dad's diagnosis—explain simply" | Clinical | Better family communication |

### Projected Impact
- **Time saved:** 15-30 min per shift on documentation
- **Safety:** Structured alerts for critical findings
- **Education:** On-demand evidence-based guidance

---

## 6. Technical Feasibility

### Deployment Options

| Option | Requirements | Use Case |
|--------|--------------|----------|
| **HuggingFace Spaces** | Gemini API key | Web demo |
| **Local GPU** | RTX 4090 + HF token | Full MedGemma |
| **Kaggle** | GPU notebook | Competition testing |

### Resource Requirements
- **Gemini API:** Free tier sufficient
- **MedGemma 4B:** 16GB VRAM (bfloat16)
- **Inference time:** 2-5 seconds per query

---

## 7. Reproducibility

### Quick Start
```bash
git clone https://github.com/AIHeartICU/NurseGemma
cd NurseGemma
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
python app.py
```

### Environment Variables
- `GEMINI_API_KEY` - Required for orchestrator
- `HF_TOKEN` - Required for MedGemma access
- `USE_MEDGEMMA` - Set to "true" to enable MedGemma

---

## 8. Innovation Summary

### What Makes NurseGemma Different

1. **Nursing-Focused:** First medical AI designed specifically for nursing workflows
2. **Agentic Architecture:** Multi-agent system with intelligent routing
3. **Practical Design:** Works without GPU, enhanced with GPU
4. **Real Domain Expertise:** Built by an ICU nurse who understands the problems

### Agentic Features
- ✅ Intent classification and routing
- ✅ Specialized agents for different tasks
- ✅ Multi-step reasoning
- ✅ Graceful degradation
- ✅ Transparent decision logging

---

## 9. Future Roadmap

- [ ] MedASR integration for voice input (hands-free nursing)
- [ ] RAG with PubMed for real-time literature search
- [ ] SBAR report generation
- [ ] Integration with EHR systems
- [ ] Mobile app for bedside use

---

## 10. Conclusion

NurseGemma demonstrates how agentic AI architecture can transform nursing practice. By combining Gemini's orchestration capabilities with MedGemma's medical expertise, we've created a tool that understands what nurses actually need—not just medical answers, but nursing-relevant guidance.

**Built by a nurse, for nurses.**

---

## References

1. Google MedGemma Technical Report (2025)
2. SCCM ICU Liberation Guidelines
3. AACN Practice Alerts
4. HAI-DEF Documentation

---

*GitHub: https://github.com/AIHeartICU/NurseGemma*
*Demo: https://huggingface.co/spaces/AIHeartICU/nursegemma*
