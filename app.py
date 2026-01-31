#!/usr/bin/env python3
"""NurseGemma - Fixed for Gradio 6.5.1 (uses messages format)"""

import gradio as gr
from code_blue_agent import CodeBlueAgent

agent = CodeBlueAgent()

def cb_chat(msg, hist):
    if not msg or not msg.strip():
        return hist, "", cb_status()
    try:
        resp = agent.process_voice(msg.strip())
        if agent.session and agent.session.outcome == "ROSC":
            resp += "\n\n" + agent.generate_code_record()
    except Exception as e:
        resp = f"⚠️ Error: {e}"
    hist = hist or []
    hist.append({"role": "user", "content": msg})
    hist.append({"role": "assistant", "content": resp})
    return hist, "", cb_status()

def cb_status():
    if not agent.session:
        return "⏸️ Say CODE BLUE"
    s = agent.session
    m, sec = divmod(s.get_run_time(), 60)
    r = s.current_rhythm.value if s.current_rhythm else "?"
    return f"🚨 {m:02d}:{sec:02d} | {r} | ⚡{len(s.shocks)} | 💉{len(s.epi_doses)}"

def cb_reset():
    agent.session = None
    return [], "", "⏸️ Say CODE BLUE"

def fam_chat(msg, hist):
    if not msg: 
        return hist, ""
    m = msg.lower()
    if "cpr" in m:
        r = "💙 CPR = chest compressions to pump blood while we restart the heart."
    elif "shock" in m:
        r = "💙 The shock tries to reset the heart's rhythm back to normal."
    elif "epi" in m:
        r = "💙 Epinephrine (adrenaline) helps strengthen the heart."
    elif "ok" in m:
        r = "💙 The team is doing everything possible. We'll keep you updated."
    else:
        r = "💙 The team is providing the best care. Ask about: CPR, shock, epi"
    hist = hist or []
    hist.append({"role": "user", "content": msg})
    hist.append({"role": "assistant", "content": r})
    return hist, ""

SAMPLES = {
    "normal": "🔬 **Normal CXR**\n\n✅ Clear lungs, normal heart size, no acute disease.",
    "covid": "🔬 **COVID Pneumonia**\n\n⚠️ Bilateral ground-glass opacities, peripheral pattern.\n\nImpression: Viral pneumonia, COVID-19 suspected.",
    "viral": "🔬 **Viral Pneumonia**\n\n⚠️ Diffuse bilateral infiltrates.\n\nImpression: Interstitial pneumonia.",
    "ecg": "🔬 **ECG Strip**\n\n✅ Normal sinus rhythm, rate ~75, no ischemic changes."
}

def mg_sample(name, hist):
    hist = hist or []
    hist.append({"role": "user", "content": f"📷 Analyze {name}"})
    hist.append({"role": "assistant", "content": SAMPLES.get(name, "Not found")})
    return hist

def mg_upload(img, q, hist):
    hist = hist or []
    if img is None:
        hist.append({"role": "user", "content": "Upload"})
        hist.append({"role": "assistant", "content": "⚠️ Upload an image first"})
        return hist, ""
    hist.append({"role": "user", "content": f"📷 {q or 'Analyze'}"})
    hist.append({"role": "assistant", "content": "🔬 Image received. Click sample buttons for demo."})
    return hist, ""

VOICE = """() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert('Use Chrome for voice'); return; }
    const r = new SR(); r.lang = 'en-US';
    r.onresult = (e) => {
        const t = e.results[0][0].transcript;
        const box = document.querySelector('textarea');
        if (box) { box.value = t; box.dispatchEvent(new Event('input', {bubbles:true})); }
        setTimeout(() => {
            const btn = [...document.querySelectorAll('button')].find(b => b.innerText.includes('Send'));
            if (btn) btn.click();
        }, 200);
    };
    r.start();
}"""

with gr.Blocks(title="NurseGemma") as demo:
    gr.HTML('<h2 style="text-align:center">🩺 NurseGemma</h2>')
    
    with gr.Tabs():
        with gr.Tab("🚨 Code Blue"):
            st = gr.Markdown("⏸️ Say CODE BLUE")
            gr.Button("🎤 VOICE", size="lg").click(None, js=VOICE)
            ch = gr.Chatbot(height=200)
            with gr.Row():
                tx = gr.Textbox(placeholder="code blue, vfib, shock, epi, rosc...", show_label=False, scale=4)
                sb = gr.Button("Send", scale=1)
            rb = gr.Button("Reset", size="sm")
            tx.submit(cb_chat, [tx, ch], [ch, tx, st])
            sb.click(cb_chat, [tx, ch], [ch, tx, st])
            rb.click(cb_reset, outputs=[ch, tx, st])
        
        with gr.Tab("💙 Family"):
            gr.Button("🎤 VOICE", size="lg").click(None, js=VOICE)
            fc = gr.Chatbot(height=200)
            with gr.Row():
                ft = gr.Textbox(placeholder="What is CPR?", show_label=False, scale=4)
                fs = gr.Button("Send", scale=1)
            ft.submit(fam_chat, [ft, fc], [fc, ft])
            fs.click(fam_chat, [ft, fc], [fc, ft])
        
        with gr.Tab("📷 MedGemma"):
            gr.Markdown("**Click sample for analysis:**")
            mc = gr.Chatbot(height=200)
            with gr.Row():
                gr.Button("🫁 Normal").click(lambda h: mg_sample("normal", h), [mc], [mc])
                gr.Button("🦠 COVID").click(lambda h: mg_sample("covid", h), [mc], [mc])
                gr.Button("🤒 Viral").click(lambda h: mg_sample("viral", h), [mc], [mc])
                gr.Button("💓 ECG").click(lambda h: mg_sample("ecg", h), [mc], [mc])
            gr.Markdown("**Or upload:**")
            with gr.Row():
                mi = gr.Image(type="filepath", height=100)
                mq = gr.Textbox(placeholder="Question", show_label=False)
            gr.Button("Analyze").click(mg_upload, [mi, mq, mc], [mc, mq])

if __name__ == "__main__":
    demo.launch(share=True, server_port=7901)
