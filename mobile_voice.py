#!/usr/bin/env python3
"""
NurseGemma Code Blue - Mobile with Browser Speech Recognition
Uses Web Speech API for near-real-time voice (runs on device, no server round-trip)
"""
import gradio as gr
from code_blue_agent import CodeBlueAgent

agent = CodeBlueAgent()

def process_cmd(text):
    if not text or not text.strip(): 
        return '🎤 Listening...', get_status()
    response = agent.process_voice(text.strip())
    return response, get_status()

def get_status():
    if not agent.session:
        return '⏸️ Ready - Say "Code Blue" or tap button'
    s = agent.session
    mins, secs = divmod(s.get_run_time(), 60)
    rhythm = s.current_rhythm.value if s.current_rhythm else "?"
    return f'🚨 **{mins}:{secs:02d}** | {rhythm} | ⚡{len(s.shocks)} | 💉{len(s.epi_doses)}'

def quick(cmd):
    return process_cmd(cmd)

def reset():
    agent.session = None
    return '🎤 Ready', '⏸️ Ready'

# JavaScript for browser-native speech recognition (runs on device = fast!)
SPEECH_JS = """
async () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Speech recognition not supported. Use Chrome/Safari.');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    // Update button to show listening
    const btn = document.querySelector('#voice-btn');
    if (btn) btn.textContent = '🎙️ Listening...';
    
    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        console.log('Heard:', text);
        // Put text in the textbox and submit
        const textbox = document.querySelector('textarea');
        if (textbox) {
            textbox.value = text;
            textbox.dispatchEvent(new Event('input', { bubbles: true }));
            // Trigger submit
            const form = textbox.closest('form');
            if (form) form.dispatchEvent(new Event('submit', { bubbles: true }));
        }
        if (btn) btn.textContent = '🎤 Voice';
    };
    
    recognition.onerror = (event) => {
        console.error('Speech error:', event.error);
        if (btn) btn.textContent = '🎤 Voice';
    };
    
    recognition.onend = () => {
        if (btn) btn.textContent = '🎤 Voice';
    };
    
    recognition.start();
}
"""

CSS = """
/* Mobile-first large buttons */
.container { max-width: 100% !important; padding: 8px !important; }
button { min-height: 56px !important; font-size: 17px !important; font-weight: 600 !important; 
         border-radius: 12px !important; margin: 4px 2px !important; }
.code-btn { background: linear-gradient(135deg, #dc3545, #c82333) !important; color: white !important; }
.rosc-btn { background: linear-gradient(135deg, #28a745, #218838) !important; color: white !important; }
.shock-btn { background: linear-gradient(135deg, #ffc107, #e0a800) !important; color: #000 !important; }
.med-btn { background: linear-gradient(135deg, #6f42c1, #5a32a3) !important; color: white !important; }
.rhythm-btn { background: linear-gradient(135deg, #17a2b8, #138496) !important; color: white !important; }
.voice-btn { background: linear-gradient(135deg, #fd7e14, #e86b00) !important; color: white !important; 
             font-size: 20px !important; }
#status { font-size: 20px !important; text-align: center; padding: 12px; 
          background: #1a1a2e; border-radius: 12px; margin: 8px 0; }
#output { font-size: 15px !important; line-height: 1.5; padding: 12px;
          background: #1a1a2e; border-radius: 12px; min-height: 150px; }
textarea { font-size: 18px !important; }
"""

with gr.Blocks(title='NurseGemma Code Blue', css=CSS) as demo:
    
    gr.HTML("""<div style="text-align:center; padding:8px;">
        <h2 style="margin:0;">🩺 NurseGemma Code Blue</h2>
        <p style="margin:4px 0; color:#888; font-size:14px;">ACLS 2025 • Voice or Tap</p>
    </div>""")
    
    status = gr.Markdown('⏸️ Ready - Say "Code Blue" or tap button', elem_id='status')
    output = gr.Markdown('🎤 **Tap 🎤 Voice or type commands**\n\nCommands: Code blue, CPR, V-fib, Shock, Epi, ROSC', elem_id='output')
    
    # Voice button (uses browser speech recognition - FAST!)
    voice_btn = gr.Button('🎤 Voice (Tap to Speak)', elem_classes='voice-btn', elem_id='voice-btn')
    voice_btn.click(None, js=SPEECH_JS)
    
    # Text input
    text = gr.Textbox(placeholder='Or type: code blue, cpr, vfib, shock, epi...', 
                      show_label=False, autofocus=True)
    
    # Quick buttons
    gr.Markdown('### 🚨 Code')
    with gr.Row():
        gr.Button('🚨 CODE BLUE', elem_classes='code-btn').click(lambda: quick('Code blue'), outputs=[output, status])
        gr.Button('🎉 ROSC!', elem_classes='rosc-btn').click(lambda: quick('ROSC'), outputs=[output, status])
    
    gr.Markdown('### 💪 CPR')
    with gr.Row():
        gr.Button('CPR Started').click(lambda: quick('CPR started'), outputs=[output, status])
        gr.Button('🔄 Switch').click(lambda: quick('Switch compressor'), outputs=[output, status])
    
    gr.Markdown('### ⚡ Rhythm')
    with gr.Row():
        gr.Button('V-Fib', elem_classes='rhythm-btn').click(lambda: quick('V-fib'), outputs=[output, status])
        gr.Button('Asystole', elem_classes='rhythm-btn').click(lambda: quick('Asystole'), outputs=[output, status])
        gr.Button('PEA', elem_classes='rhythm-btn').click(lambda: quick('PEA'), outputs=[output, status])
    
    gr.Markdown('### 💊 Meds & Defib')
    with gr.Row():
        gr.Button('⚡ SHOCK', elem_classes='shock-btn').click(lambda: quick('Shock 200J'), outputs=[output, status])
        gr.Button('💉 EPI', elem_classes='med-btn').click(lambda: quick('Epi given'), outputs=[output, status])
    with gr.Row():
        gr.Button('💊 Amio 300', elem_classes='med-btn').click(lambda: quick('Amio 300'), outputs=[output, status])
        gr.Button('💉 IV Access').click(lambda: quick('IV access'), outputs=[output, status])
    
    gr.Markdown('### 📋 Other')
    with gr.Row():
        gr.Button("H's & T's").click(lambda: quick("Check H's and T's"), outputs=[output, status])
        gr.Button('🔍 Rhythm Check').click(lambda: quick('Rhythm check'), outputs=[output, status])
    with gr.Row():
        gr.Button('🗑️ Reset', variant='secondary').click(reset, outputs=[output, status])
    
    # Wire up text submit
    text.submit(process_cmd, inputs=[text], outputs=[output, status]).then(lambda: '', outputs=[text])
    
    gr.Markdown("""---
**ACLS 2025**: VF/pVT → Shock, Epi after 2nd, Amio after 3rd | PEA/Asystole → Epi ASAP
    
⚠️ Educational tool only""")

if __name__ == '__main__':
    demo.launch(share=True, server_port=7880)
