#!/usr/bin/env python3
"""
NurseGemma Code Blue - ACLS 2025 Voice-Activated Cardiac Arrest Assistant
Hackathon Demo - Mobile-first UI with real-time documentation
"""

import gradio as gr
from datetime import datetime
from code_blue_agent import CodeBlueAgent

# Initialize agent
agent = CodeBlueAgent()

# ============== CORE FUNCTIONS ==============

def process_command(text: str) -> tuple[str, str]:
    """Process voice/text command and return response + status."""
    if not text or not text.strip():
        return "🎤 Say a command or tap a button", get_status()
    
    try:
        response = agent.process_voice(text.strip())
        
        # Auto-append report on ROSC
        if agent.session and agent.session.outcome == "ROSC":
            response += "\n\n" + generate_report()
        
        return str(response), get_status()
    except Exception as e:
        return f"⚠️ Error: {str(e)}", get_status()

def get_status() -> str:
    """Get current code status for header."""
    if not agent.session:
        return "⏸️ **Ready** - Tap CODE BLUE to start"
    
    s = agent.session
    mins, secs = divmod(s.get_run_time(), 60)
    rhythm = s.current_rhythm.value if s.current_rhythm else "Unknown"
    shocks = len(s.shocks)
    epis = len(s.epi_doses)
    
    return f"🚨 **{mins:02d}:{secs:02d}** | {rhythm} | ⚡{shocks} | 💉{epis}"

def quick_action(cmd: str) -> tuple[str, str]:
    """Quick action button handler."""
    return process_command(cmd)

def generate_report() -> str:
    """Generate documentation report."""
    if not agent.session:
        return "❌ No active code - start with CODE BLUE first"
    return agent.generate_code_record()

def get_report() -> tuple[str, str]:
    """Get report for button click."""
    return generate_report(), get_status()

def reset_session() -> tuple[str, str]:
    """Reset and start fresh."""
    agent.session = None
    return "🎤 **Reset complete** - Ready for new code", "⏸️ **Ready** - Tap CODE BLUE to start"

# ============== VOICE JS ==============

VOICE_JS = """
async () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { 
        document.getElementById('voice-status').innerText = '❌ Voice not supported - use buttons';
        return; 
    }
    
    const recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    const voiceBtn = document.getElementById('voice-btn');
    const voiceStatus = document.getElementById('voice-status');
    
    // Visual feedback
    if (voiceBtn) {
        voiceBtn.style.backgroundColor = '#dc3545';
        voiceBtn.innerText = '🎙️ LISTENING...';
    }
    if (voiceStatus) voiceStatus.innerText = '🎙️ Speak now...';
    
    recognition.onresult = (event) => {
        const result = event.results[event.results.length - 1];
        const text = result[0].transcript;
        
        if (voiceStatus) voiceStatus.innerText = '🗣️ Heard: "' + text + '"';
        
        if (result.isFinal) {
            // Find textbox and set value
            const textbox = document.querySelector('textarea');
            if (textbox) {
                textbox.value = text;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Find and click Send button
                setTimeout(() => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.innerText.includes('Send')) {
                            btn.click();
                            break;
                        }
                    }
                }, 200);
            }
        }
    };
    
    recognition.onerror = (e) => {
        if (voiceStatus) voiceStatus.innerText = '❌ Voice error: ' + e.error;
        resetVoiceBtn();
    };
    
    recognition.onend = () => {
        resetVoiceBtn();
    };
    
    function resetVoiceBtn() {
        if (voiceBtn) {
            voiceBtn.style.backgroundColor = '';
            voiceBtn.innerText = '🎤 Voice';
        }
    }
    
    recognition.start();
}
"""

# ============== CUSTOM CSS ==============

CUSTOM_CSS = """
/* Mobile-first, ICU-friendly design */
.gradio-container { max-width: 100% !important; }

/* Large touch targets */
button { 
    min-height: 52px !important; 
    font-size: 16px !important; 
    font-weight: 600 !important;
    border-radius: 8px !important;
}

/* Status bar */
#status { 
    font-size: 20px !important; 
    text-align: center !important;
    padding: 12px !important;
    background: linear-gradient(135deg, #1a1a2e, #16213e) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}

/* Output area */
#output {
    min-height: 150px;
    padding: 16px;
    background: #0d1117;
    border-radius: 12px;
    border: 1px solid #30363d;
}

/* Voice status */
#voice-status {
    text-align: center;
    padding: 8px;
    color: #8b949e;
    font-size: 14px;
}

/* Primary action buttons */
.primary-action {
    background: linear-gradient(135deg, #dc3545, #c82333) !important;
    color: white !important;
}

/* Shockable rhythm buttons */
.shockable {
    border-left: 4px solid #ffc107 !important;
}

/* Non-shockable rhythm buttons */
.non-shockable {
    border-left: 4px solid #6c757d !important;
}
"""

# ============== BUILD UI ==============

with gr.Blocks(
    title="NurseGemma Code Blue",
    css=CUSTOM_CSS,
    theme=gr.themes.Base(
        primary_hue="red",
        neutral_hue="slate",
    )
) as demo:
    
    # Header
    gr.HTML("""
        <div style="text-align:center; padding:8px 0;">
            <h1 style="margin:0; font-size:24px;">🩺 NurseGemma Code Blue</h1>
            <p style="margin:4px 0 0 0; color:#8b949e; font-size:14px;">ACLS 2025 • Voice or Tap</p>
        </div>
    """)
    
    # Status bar (always visible)
    status = gr.Markdown("⏸️ **Ready** - Tap CODE BLUE to start", elem_id="status")
    
    # Voice status indicator
    gr.HTML('<div id="voice-status">Tap 🎤 Voice or use buttons below</div>')
    
    # Output area
    output = gr.Markdown("🎤 **Ready** - Start with CODE BLUE button", elem_id="output")
    
    # Voice + Text input
    with gr.Row():
        voice_btn = gr.Button("🎤 Voice", elem_id="voice-btn", variant="primary", scale=1)
        text_input = gr.Textbox(
            placeholder="Type: code blue, vfib, shock, epi, rosc...",
            show_label=False,
            scale=3
        )
        send_btn = gr.Button("Send", scale=1)
    
    voice_btn.click(None, js=VOICE_JS)
    
    # Divider
    gr.HTML('<hr style="margin: 12px 0; border-color: #30363d;">')
    
    # === MAIN ACTIONS ===
    with gr.Row():
        code_btn = gr.Button("🚨 CODE BLUE", variant="primary", size="lg", scale=2)
        rosc_btn = gr.Button("🎉 ROSC", variant="secondary", size="lg", scale=1)
    
    # === RHYTHM ===
    gr.Markdown("### ⚡ Rhythm Check")
    with gr.Row():
        vfib_btn = gr.Button("⚡ V-Fib", elem_classes=["shockable"])
        vtach_btn = gr.Button("⚡ V-Tach", elem_classes=["shockable"])
        asys_btn = gr.Button("❌ Asystole", elem_classes=["non-shockable"])
        pea_btn = gr.Button("❌ PEA", elem_classes=["non-shockable"])
    
    # === INTERVENTIONS ===
    gr.Markdown("### 💊 Interventions")
    with gr.Row():
        shock_btn = gr.Button("⚡ SHOCK 200J")
        epi_btn = gr.Button("💉 EPI 1mg")
        amio_btn = gr.Button("💊 AMIO 300mg")
    
    with gr.Row():
        cpr_btn = gr.Button("💪 CPR Started")
        iv_btn = gr.Button("💉 IV Access")
        hs_ts_btn = gr.Button("🔍 H's & T's")
    
    # === DOCUMENTATION ===
    gr.Markdown("### 📋 Documentation")
    with gr.Row():
        report_btn = gr.Button("📋 Generate Report")
        reset_btn = gr.Button("🗑️ Reset", variant="stop")
    
    # Footer
    gr.HTML("""
        <div style="text-align:center; padding:8px; color:#6c757d; font-size:12px;">
            ⚠️ Educational tool only • ACLS 2025 Guidelines
        </div>
    """)
    
    # === WIRE UP ALL BUTTONS ===
    code_btn.click(lambda: quick_action("Code blue"), outputs=[output, status])
    rosc_btn.click(lambda: quick_action("ROSC"), outputs=[output, status])
    
    vfib_btn.click(lambda: quick_action("V-fib"), outputs=[output, status])
    vtach_btn.click(lambda: quick_action("V-tach"), outputs=[output, status])
    asys_btn.click(lambda: quick_action("Asystole"), outputs=[output, status])
    pea_btn.click(lambda: quick_action("PEA"), outputs=[output, status])
    
    shock_btn.click(lambda: quick_action("Shock 200J"), outputs=[output, status])
    epi_btn.click(lambda: quick_action("Epi given"), outputs=[output, status])
    amio_btn.click(lambda: quick_action("Amiodarone 300"), outputs=[output, status])
    
    cpr_btn.click(lambda: quick_action("CPR started"), outputs=[output, status])
    iv_btn.click(lambda: quick_action("IV access"), outputs=[output, status])
    hs_ts_btn.click(lambda: quick_action("H's and T's"), outputs=[output, status])
    
    report_btn.click(get_report, outputs=[output, status])
    reset_btn.click(reset_session, outputs=[output, status])
    
    # Text input handlers
    text_input.submit(process_command, inputs=[text_input], outputs=[output, status]).then(
        lambda: "", outputs=[text_input]
    )
    send_btn.click(process_command, inputs=[text_input], outputs=[output, status]).then(
        lambda: "", outputs=[text_input]
    )

# ============== LAUNCH ==============

if __name__ == "__main__":
    demo.launch(
        share=True,
        server_port=7892,
        show_error=True
    )
