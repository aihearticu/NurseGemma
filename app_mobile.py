"""
NurseGemma Mobile - Optimized for iPhone/Mobile
Code Blue Agent with large touch targets and voice-first design

Mobile-optimized features:
- Large buttons for gloved hands
- Voice-first input
- Quick Code Blue commands
- Responsive single-column layout
"""

import gradio as gr
from code_blue_agent import CodeBlueAgent

# Initialize Code Blue Agent
agent = CodeBlueAgent()

# Custom CSS for mobile optimization
MOBILE_CSS = """
/* Mobile-First Responsive Design */
* { 
    -webkit-tap-highlight-color: transparent; 
    box-sizing: border-box;
}

.gradio-container {
    max-width: 100% !important;
    padding: 8px !important;
}

/* Large touch-friendly buttons */
.big-button {
    min-height: 60px !important;
    font-size: 18px !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    margin: 4px !important;
}

.code-blue-btn {
    background: linear-gradient(135deg, #f5365c 0%, #f56036 100%) !important;
    color: white !important;
    font-size: 20px !important;
    min-height: 70px !important;
}

.acls-btn {
    background: linear-gradient(135deg, #2dce89 0%, #26a65b 100%) !important;
    color: white !important;
}

.shock-btn {
    background: linear-gradient(135deg, #f7b731 0%, #fa8231 100%) !important;
    color: black !important;
}

.med-btn {
    background: linear-gradient(135deg, #5e72e4 0%, #825ee4 100%) !important;
    color: white !important;
}

.rhythm-btn {
    background: linear-gradient(135deg, #11cdef 0%, #1171ef 100%) !important;
    color: white !important;
}

/* Response area - large readable text */
.response-area {
    font-size: 16px !important;
    line-height: 1.6 !important;
    padding: 16px !important;
    background: #1a1a2e !important;
    border-radius: 12px !important;
    min-height: 200px !important;
}

/* Status bar */
.status-bar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 12px;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 12px;
}

.status-bar.active {
    background: linear-gradient(135deg, #f5365c 0%, #f56036 100%);
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.9; transform: scale(1.02); }
}

/* Voice input prominent */
.voice-container {
    background: #2d2d44 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin: 8px 0 !important;
}

/* Text input - large for mobile keyboard */
.mobile-input textarea {
    font-size: 18px !important;
    min-height: 50px !important;
    border-radius: 12px !important;
}

/* Quick command grid */
.command-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin: 8px 0;
}

/* Timer display */
.timer-display {
    font-size: 32px;
    font-weight: bold;
    text-align: center;
    font-family: monospace;
    color: #2dce89;
    background: #1a1a2e;
    padding: 12px;
    border-radius: 8px;
}

/* Mobile scroll optimization */
.scroll-area {
    max-height: 40vh;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}

/* Hide desktop elements on mobile */
@media (max-width: 768px) {
    .desktop-only { display: none !important; }
    .gradio-container { padding: 4px !important; }
}

/* Landscape mode adjustments */
@media (orientation: landscape) and (max-height: 500px) {
    .response-area { min-height: 120px !important; }
}
"""

def process_command(text: str) -> tuple:
    """Process voice/text command and return response + status."""
    if not text.strip():
        return "🎤 Waiting for command...", get_status()
    
    response = agent.process_voice(text)
    status = get_status()
    return response, status

def get_status() -> str:
    """Get current code status for status bar."""
    if not agent.session:
        return "⏸️ Ready - Say 'Code Blue' to start"
    
    s = agent.session
    run_time = s.get_run_time()
    mins, secs = divmod(run_time, 60)
    
    rhythm = s.current_rhythm.value if s.current_rhythm else "?"
    shocks = len(s.shocks)
    epis = len(s.epi_doses)
    
    if s.outcome == "ROSC":
        return f"🎉 ROSC at {mins}:{secs:02d} | Post-arrest care"
    
    return f"🚨 {mins}:{secs:02d} | {rhythm} | ⚡{shocks} | 💉{epis}"

def quick_command(cmd: str) -> tuple:
    """Execute a quick command button."""
    return process_command(cmd)

def end_code() -> tuple:
    """End the current code and generate record."""
    if agent.session:
        record = agent.generate_code_record()
        agent.session = None
        return record, "✅ Code ended - Record generated"
    return "No active code", "⏸️ Ready"

def clear_all() -> tuple:
    """Clear everything and start fresh."""
    agent.session = None
    return "🎤 Ready for commands", "⏸️ Ready - Say 'Code Blue' to start"

def create_mobile_ui():
    """Create mobile-optimized Gradio interface."""
    
    with gr.Blocks(
        title="NurseGemma Code Blue",
        theme=gr.themes.Base(
            primary_hue="red",
            secondary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=MOBILE_CSS
    ) as demo:
        
        # Header
        gr.HTML("""
        <div style="text-align: center; padding: 8px;">
            <h1 style="margin: 0; font-size: 24px;">🩺 NurseGemma</h1>
            <p style="margin: 4px 0; color: #888; font-size: 14px;">Code Blue Agent - ACLS 2025</p>
        </div>
        """)
        
        # Status bar (updates with code status)
        status_bar = gr.Markdown(
            value="⏸️ Ready - Say 'Code Blue' to start",
            elem_classes="status-bar"
        )
        
        # Main response area
        response_output = gr.Markdown(
            value="🎤 **Tap the microphone or type a command**\n\nQuick start: Tap **'Code Blue'** button below",
            elem_classes="response-area"
        )
        
        # Voice input (prominent for hands-free use)
        gr.Markdown("### 🎤 Voice Command", elem_classes="voice-container")
        with gr.Row():
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Tap to record",
                elem_classes="voice-container"
            )
        
        # Text input (backup)
        text_input = gr.Textbox(
            placeholder="Or type: CPR started, V-fib, Epi given, ROSC...",
            show_label=False,
            elem_classes="mobile-input"
        )
        
        # Quick command buttons - Code Blue start
        gr.Markdown("### 🚨 Start/End Code")
        with gr.Row():
            code_blue_btn = gr.Button(
                "🚨 CODE BLUE",
                variant="primary",
                elem_classes="big-button code-blue-btn"
            )
            end_btn = gr.Button(
                "⏹️ End Code",
                elem_classes="big-button"
            )
        
        # ACLS Quick Commands
        gr.Markdown("### ⚡ ACLS Commands")
        
        # CPR Row
        with gr.Row():
            cpr_btn = gr.Button("💪 CPR Started", elem_classes="big-button acls-btn")
            switch_btn = gr.Button("🔄 Switch Compressor", elem_classes="big-button acls-btn")
        
        # Rhythm Row
        with gr.Row():
            vfib_btn = gr.Button("⚡ V-Fib", elem_classes="big-button rhythm-btn")
            asystole_btn = gr.Button("📉 Asystole", elem_classes="big-button rhythm-btn")
        with gr.Row():
            pea_btn = gr.Button("💔 PEA", elem_classes="big-button rhythm-btn")
            rhythm_btn = gr.Button("🔍 Rhythm Check", elem_classes="big-button rhythm-btn")
        
        # Interventions Row
        with gr.Row():
            shock_btn = gr.Button("⚡ Shock 200J", elem_classes="big-button shock-btn")
            epi_btn = gr.Button("💉 Epi Given", elem_classes="big-button med-btn")
        with gr.Row():
            amio_btn = gr.Button("💊 Amio 300", elem_classes="big-button med-btn")
            iv_btn = gr.Button("💉 IV Access", elem_classes="big-button med-btn")
        
        # Airway/Monitoring
        with gr.Row():
            intubate_btn = gr.Button("🫁 Intubated", elem_classes="big-button")
            rosc_btn = gr.Button("🎉 ROSC!", elem_classes="big-button acls-btn")
        
        # H's and T's / Post-ROSC
        gr.Markdown("### 🔍 Assessment")
        with gr.Row():
            hs_ts_btn = gr.Button("📋 H's & T's", elem_classes="big-button")
            post_rosc_btn = gr.Button("📊 Post-ROSC", elem_classes="big-button")
        
        # Clear button
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear All", elem_classes="big-button")
        
        # Footer
        gr.Markdown("""
---
**ACLS 2025** | VF/pVT: Shock→Epi after 2nd→Amio after 3rd | PEA/Asystole: Epi ASAP
        
⚠️ Educational tool - verify with ACLS protocol
        """, elem_classes="desktop-only")
        
        # === Event Handlers ===
        
        # Text input
        text_input.submit(
            process_command,
            inputs=[text_input],
            outputs=[response_output, status_bar]
        ).then(lambda: "", outputs=[text_input])
        
        # Voice input (auto-transcribe and process)
        def process_audio(audio_path):
            if audio_path:
                try:
                    # Try whisper for transcription
                    import whisper
                    model = whisper.load_model("tiny")  # Fast model for mobile
                    result = model.transcribe(audio_path)
                    transcription = result["text"].strip()
                    if transcription:
                        response, status = process_command(transcription)
                        return f"🎤 *\"{transcription}\"*\n\n{response}", status
                except ImportError:
                    pass
                except Exception as e:
                    return f"⚠️ Transcription error: {e}", get_status()
            return "🎤 Tap microphone to record", get_status()
        
        audio_input.change(
            process_audio,
            inputs=[audio_input],
            outputs=[response_output, status_bar]
        )
        
        # Quick command buttons
        code_blue_btn.click(lambda: quick_command("Code blue called"), outputs=[response_output, status_bar])
        end_btn.click(end_code, outputs=[response_output, status_bar])
        
        cpr_btn.click(lambda: quick_command("CPR started"), outputs=[response_output, status_bar])
        switch_btn.click(lambda: quick_command("Switch compressor"), outputs=[response_output, status_bar])
        
        vfib_btn.click(lambda: quick_command("V-fib"), outputs=[response_output, status_bar])
        asystole_btn.click(lambda: quick_command("Asystole"), outputs=[response_output, status_bar])
        pea_btn.click(lambda: quick_command("PEA"), outputs=[response_output, status_bar])
        rhythm_btn.click(lambda: quick_command("Rhythm check"), outputs=[response_output, status_bar])
        
        shock_btn.click(lambda: quick_command("Shock delivered 200J"), outputs=[response_output, status_bar])
        epi_btn.click(lambda: quick_command("Epi given"), outputs=[response_output, status_bar])
        amio_btn.click(lambda: quick_command("Amio 300"), outputs=[response_output, status_bar])
        iv_btn.click(lambda: quick_command("IV access"), outputs=[response_output, status_bar])
        
        intubate_btn.click(lambda: quick_command("Intubated"), outputs=[response_output, status_bar])
        rosc_btn.click(lambda: quick_command("ROSC"), outputs=[response_output, status_bar])
        
        hs_ts_btn.click(lambda: quick_command("Check H's and T's"), outputs=[response_output, status_bar])
        post_rosc_btn.click(lambda: quick_command("Post ROSC"), outputs=[response_output, status_bar])
        
        clear_btn.click(clear_all, outputs=[response_output, status_bar])
    
    return demo


if __name__ == "__main__":
    demo = create_mobile_ui()
    demo.launch(
        share=True,  # Get public URL for iPhone testing
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860
    )
