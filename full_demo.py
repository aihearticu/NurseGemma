import gradio as gr
from code_blue_agent import CodeBlueAgent

agent = CodeBlueAgent()

def process_cmd(text):
    if not text or not text.strip(): 
        return gr.update(), gr.update()
    try:
        response = agent.process_voice(text.strip())
        if agent.session and agent.session.outcome == "ROSC":
            response += "\n\n" + agent.generate_code_record()
        return str(response), get_status()
    except Exception as e:
        return f'Error: {e}', get_status()

def get_status():
    if not agent.session:
        return '⏸️ Ready'
    s = agent.session
    mins, secs = divmod(s.get_run_time(), 60)
    rhythm = s.current_rhythm.value if s.current_rhythm else "?"
    return f'🚨 **{mins}:{secs:02d}** | {rhythm} | ⚡{len(s.shocks)} | 💉{len(s.epi_doses)}'

def quick(cmd):
    return process_cmd(cmd)

def reset():
    agent.session = None
    return '🎤 Ready - Tap a button or use voice', '⏸️ Ready'

def get_summary():
    if not agent.session:
        return "Start a code first", '⏸️ Ready'
    return agent.generate_code_record(), get_status()

# Simplified, more reliable voice JS
SPEECH_JS = """
async () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert('Voice not supported - use Chrome'); return; }
    
    const r = new SR();
    r.continuous = false;
    r.interimResults = true;  // Show partial results
    r.lang = 'en-US';
    
    const btn = document.querySelector('#voice-btn');
    const output = document.querySelector('#live-text');
    
    if (btn) btn.style.background = '#dc3545';
    if (btn) btn.innerText = '🎙️ LISTENING...';
    if (output) output.innerText = '🎙️ Speak now...';
    
    r.onresult = (e) => {
        const text = e.results[e.results.length-1][0].transcript;
        if (output) output.innerText = '🗣️ ' + text;
        
        if (e.results[e.results.length-1].isFinal) {
            // Final result - submit it
            const textbox = document.querySelector('textarea');
            if (textbox) {
                textbox.value = text;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                // Click send after brief delay
                setTimeout(() => {
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {
                        if (b.innerText.includes('Send')) { b.click(); break; }
                    }
                }, 300);
            }
        }
    };
    
    r.onerror = (e) => { 
        if (output) output.innerText = '❌ Error: ' + e.error;
        if (btn) btn.innerText = '🎤 Voice';
        if (btn) btn.style.background = '';
    };
    r.onend = () => { 
        if (btn) btn.innerText = '🎤 Voice';
        if (btn) btn.style.background = '';
    };
    
    r.start();
}
"""

with gr.Blocks(title='NurseGemma Code Blue', theme=gr.themes.Soft()) as demo:
    gr.HTML('<h2 style="margin:0;text-align:center">🩺 NurseGemma Code Blue</h2>')
    
    status = gr.Markdown('⏸️ Ready', elem_id='status')
    
    # Live voice feedback
    gr.HTML('<div id="live-text" style="text-align:center;padding:8px;color:#666;font-size:14px">Tap 🎤 Voice or buttons below</div>')
    
    output = gr.Markdown('🎤 **Ready** - Start with CODE BLUE', elem_id='output')
    
    # Voice + Text input row
    with gr.Row():
        voice_btn = gr.Button('🎤 Voice', elem_id='voice-btn', variant='primary', scale=1)
        text = gr.Textbox(placeholder='Type command...', show_label=False, scale=3)
        send_btn = gr.Button('Send', scale=1)
    
    voice_btn.click(None, js=SPEECH_JS)
    
    # Main action buttons - BIG
    gr.Markdown('---')
    with gr.Row():
        code_btn = gr.Button('🚨 CODE BLUE', variant='primary', size='lg')
        rosc_btn = gr.Button('🎉 ROSC', variant='secondary', size='lg')
    
    # Rhythm
    with gr.Row():
        gr.Button('⚡ V-Fib').click(lambda: quick('V-fib'), outputs=[output, status])
        gr.Button('⚡ V-Tach').click(lambda: quick('V-tach'), outputs=[output, status])
        gr.Button('❌ Asystole').click(lambda: quick('Asystole'), outputs=[output, status])
        gr.Button('❌ PEA').click(lambda: quick('PEA'), outputs=[output, status])
    
    # Interventions
    with gr.Row():
        gr.Button('⚡ SHOCK').click(lambda: quick('Shock'), outputs=[output, status])
        gr.Button('💉 EPI').click(lambda: quick('Epi'), outputs=[output, status])
        gr.Button('💊 AMIO').click(lambda: quick('Amio'), outputs=[output, status])
    
    with gr.Row():
        gr.Button('💪 CPR').click(lambda: quick('CPR'), outputs=[output, status])
        gr.Button('💉 IV').click(lambda: quick('IV access'), outputs=[output, status])
        gr.Button("🔍 H's T's").click(lambda: quick("H's and T's"), outputs=[output, status])
    
    with gr.Row():
        gr.Button('📋 Report').click(get_summary, outputs=[output, status])
        gr.Button('🗑️ Reset', variant='stop').click(reset, outputs=[output, status])
    
    # Wire buttons
    code_btn.click(lambda: quick('Code blue'), outputs=[output, status])
    rosc_btn.click(lambda: quick('ROSC'), outputs=[output, status])
    text.submit(process_cmd, inputs=[text], outputs=[output, status]).then(lambda: '', outputs=[text])
    send_btn.click(process_cmd, inputs=[text], outputs=[output, status]).then(lambda: '', outputs=[text])

demo.launch(share=True, server_port=7891)
