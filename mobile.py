#!/usr/bin/env python3
"""
NurseGemma Code Blue - Mobile App
Optimized for iPhone testing with large buttons
"""
import gradio as gr
from code_blue_agent import CodeBlueAgent

agent = CodeBlueAgent()

def process_cmd(text):
    if not text.strip(): 
        return '🎤 Waiting...', '⏸️ Ready'
    response = agent.process_voice(text)
    if agent.session:
        s = agent.session
        mins, secs = divmod(s.get_run_time(), 60)
        status = f'🚨 {mins}:{secs:02d} | ⚡{len(s.shocks)} | 💉{len(s.epi_doses)}'
    else:
        status = '⏸️ Ready'
    return response, status

CSS = """
.big-btn { min-height: 55px !important; font-size: 16px !important; margin: 3px !important; }
.red-btn { background: #dc3545 !important; color: white !important; }
.green-btn { background: #28a745 !important; color: white !important; }
.blue-btn { background: #007bff !important; color: white !important; }
.yellow-btn { background: #ffc107 !important; color: black !important; }
"""

with gr.Blocks(title='NurseGemma Mobile', css=CSS) as demo:
    gr.Markdown('# 🩺 NurseGemma Code Blue\n*ACLS 2025 Mobile*')
    status = gr.Markdown('⏸️ Ready - Tap CODE BLUE to start')
    output = gr.Markdown('🎤 Ready for commands', elem_id='output')
    text = gr.Textbox(placeholder='Or type: CPR started, V-fib, Epi given...', show_label=False)
    
    gr.Markdown('### 🚨 Start/End')
    with gr.Row():
        gr.Button('🚨 CODE BLUE', elem_classes='big-btn red-btn').click(
            lambda: process_cmd('Code blue'), outputs=[output, status])
        gr.Button('🎉 ROSC!', elem_classes='big-btn green-btn').click(
            lambda: process_cmd('ROSC'), outputs=[output, status])
    
    gr.Markdown('### 💪 CPR')
    with gr.Row():
        gr.Button('CPR Started', elem_classes='big-btn').click(
            lambda: process_cmd('CPR started'), outputs=[output, status])
        gr.Button('🔄 Switch', elem_classes='big-btn').click(
            lambda: process_cmd('Switch compressor'), outputs=[output, status])
    
    gr.Markdown('### ⚡ Rhythm')
    with gr.Row():
        gr.Button('V-Fib', elem_classes='big-btn blue-btn').click(
            lambda: process_cmd('V-fib'), outputs=[output, status])
        gr.Button('Asystole', elem_classes='big-btn blue-btn').click(
            lambda: process_cmd('Asystole'), outputs=[output, status])
        gr.Button('PEA', elem_classes='big-btn blue-btn').click(
            lambda: process_cmd('PEA'), outputs=[output, status])
    with gr.Row():
        gr.Button('🔍 Rhythm Check', elem_classes='big-btn').click(
            lambda: process_cmd('Rhythm check'), outputs=[output, status])
    
    gr.Markdown('### 💊 Interventions')
    with gr.Row():
        gr.Button('⚡ Shock 200J', elem_classes='big-btn yellow-btn').click(
            lambda: process_cmd('Shock 200J'), outputs=[output, status])
        gr.Button('💉 Epi', elem_classes='big-btn green-btn').click(
            lambda: process_cmd('Epi given'), outputs=[output, status])
    with gr.Row():
        gr.Button('💊 Amio 300', elem_classes='big-btn').click(
            lambda: process_cmd('Amio 300'), outputs=[output, status])
        gr.Button('💉 IV Access', elem_classes='big-btn').click(
            lambda: process_cmd('IV access'), outputs=[output, status])
    
    gr.Markdown('### 📋 Assessment')
    with gr.Row():
        gr.Button("H's & T's", elem_classes='big-btn').click(
            lambda: process_cmd("Check H's and T's"), outputs=[output, status])
        gr.Button('Post-ROSC', elem_classes='big-btn').click(
            lambda: process_cmd('Post ROSC'), outputs=[output, status])
    
    text.submit(process_cmd, inputs=[text], outputs=[output, status]).then(lambda:'', outputs=[text])
    
    gr.Markdown('---\n*VF/pVT: Shock→Epi after 2nd→Amio after 3rd | PEA/Asystole: Epi ASAP*')

if __name__ == '__main__':
    print("Starting NurseGemma Mobile...")
    demo.launch(share=True, server_port=7865, show_error=True)
