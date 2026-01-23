"""
EPIC-Style UI for NurseGemma
Professional nursing interface matching EPIC EHR visual language.

Design principles (from research):
- Workflow alignment: Design around clinical tasks
- Clarity over beauty: Function first
- Calm visual language: Muted colors, whitespace
- Minimize clicks: Every click costs bedside time
- Surface concerns: Critical info visible immediately

References:
- EHR Interface Design Guide 2026
- Healthcare UI Design 2025 Best Practices
- Denver Health Nursing Workflow Redesign
"""

from typing import Optional, Dict, Any
import time

# Optional gradio import for local testing
try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    gr = None


# ==================== EPIC-STYLE CSS ====================

EPIC_CSS = """
/* EPIC-style color palette */
:root {
    --epic-header-bg: #1a365d;
    --epic-header-text: #ffffff;
    --epic-sidebar-bg: #f7fafc;
    --epic-content-bg: #ffffff;
    --epic-accent: #3182ce;
    --epic-border: #e2e8f0;

    --status-normal: #48bb78;
    --status-warning: #ed8936;
    --status-critical: #e53e3e;
    --status-info: #4299e1;

    --lab-normal: #2d3748;
    --lab-low: #3182ce;
    --lab-high: #e53e3e;
}

/* Main container */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Header bar */
.epic-header {
    background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 12px 12px 0 0;
    margin-bottom: 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.epic-header h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
}

.epic-header .patient-info {
    font-size: 14px;
    opacity: 0.9;
    margin-top: 4px;
}

/* Panel styling */
.chart-panel {
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0 0 0 12px;
    padding: 16px;
    min-height: 400px;
}

.ai-panel {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0 0 12px 0;
    padding: 16px;
    min-height: 400px;
}

/* Tab styling */
.tab-nav {
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 16px;
}

.tab-nav button {
    padding: 8px 16px;
    border: none;
    background: none;
    font-weight: 500;
    color: #4a5568;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}

.tab-nav button.selected {
    color: #3182ce;
    border-bottom-color: #3182ce;
}

/* MAR display */
.mar-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.mar-table th {
    background: #edf2f7;
    padding: 8px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #e2e8f0;
}

.mar-table td {
    padding: 8px;
    border-bottom: 1px solid #e2e8f0;
}

.mar-table .high-alert {
    color: #e53e3e;
    font-weight: 600;
}

.mar-table .given {
    color: #48bb78;
}

.mar-table .due {
    color: #ed8936;
}

/* Lab values */
.lab-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.lab-table th {
    background: #edf2f7;
    padding: 8px;
    text-align: left;
}

.lab-table td {
    padding: 8px;
    border-bottom: 1px solid #e2e8f0;
}

.lab-high {
    color: #e53e3e;
    font-weight: 600;
}

.lab-low {
    color: #3182ce;
    font-weight: 600;
}

.lab-critical {
    background: #fed7d7;
    color: #c53030;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
}

/* AI response cards */
.ai-response {
    background: #f0fff4;
    border-left: 4px solid #48bb78;
    padding: 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 12px;
    font-size: 14px;
    line-height: 1.6;
}

.ai-response.concern {
    background: #fffaf0;
    border-left-color: #ed8936;
}

.ai-response.critical {
    background: #fff5f5;
    border-left-color: #e53e3e;
}

.ai-response .header {
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 8px;
}

/* Workflow buttons */
.workflow-btn {
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.workflow-btn.primary {
    background: #3182ce;
    color: white;
}

.workflow-btn.primary:hover {
    background: #2c5282;
}

.workflow-btn.secondary {
    background: #edf2f7;
    color: #4a5568;
}

.workflow-btn.secondary:hover {
    background: #e2e8f0;
}

/* Time savings badge */
.time-saved {
    display: inline-block;
    background: #c6f6d5;
    color: #22543d;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 8px;
}

/* Status indicators */
.status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.critical {
    background: #fed7d7;
    color: #c53030;
}

.status-badge.urgent {
    background: #feebc8;
    color: #c05621;
}

.status-badge.normal {
    background: #c6f6d5;
    color: #22543d;
}

/* Disclaimer */
.disclaimer {
    background: #fef3c7;
    border: 1px solid #f6e05e;
    border-radius: 8px;
    padding: 12px;
    font-size: 12px;
    color: #744210;
    margin-top: 16px;
}

/* Loading spinner */
.loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #e2e8f0;
    border-top-color: #3182ce;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
"""


# ==================== UI COMPONENTS ====================

def create_patient_header(patient) -> str:
    """Create EPIC-style patient header HTML"""
    return f"""
<div class="epic-header">
    <h1>NurseGemma | {patient.name}</h1>
    <div class="patient-info">
        Room {patient.room} | MRN: {patient.mrn} | {patient.age}{patient.sex} |
        Dr. {patient.attending_md} ({patient.specialty}) |
        Admitted: {patient.admission_date}
    </div>
</div>
"""


def format_mar_html(patient) -> str:
    """Format MAR as HTML table"""
    rows = []
    for med in patient.medications:
        alert_class = "high-alert" if med.high_alert else ""
        alert_icon = " HIGH-ALERT" if med.high_alert else ""

        times_html = []
        for t in med.scheduled_times:
            given = med.given_times.get(t, False)
            status_class = "given" if given else "due"
            status_text = "" if given else ""
            times_html.append(f'<span class="{status_class}">{t} {status_text}</span>')

        times_str = " | ".join(times_html) if times_html else "PRN"

        rows.append(f"""
        <tr class="{alert_class}">
            <td><strong>{med.name}</strong>{alert_icon}<br><small>{med.notes}</small></td>
            <td>{med.dose}</td>
            <td>{med.route}</td>
            <td>{med.frequency}</td>
            <td>{times_str}</td>
        </tr>
        """)

    return f"""
<table class="mar-table">
    <thead>
        <tr>
            <th>Medication</th>
            <th>Dose</th>
            <th>Route</th>
            <th>Freq</th>
            <th>Admin Times</th>
        </tr>
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
"""


def format_labs_html(patient) -> str:
    """Format labs as HTML table with color coding"""
    rows = []
    for lab in patient.labs:
        status = lab.status
        if status == "L":
            value_class = "lab-low"
            value_display = f"{lab.value} (L)"
        elif status == "H":
            value_class = "lab-high"
            value_display = f"{lab.value} (H)"
        else:
            value_class = ""
            value_display = str(lab.value)

        # Check for critical values
        is_critical = False
        lab_name_lower = lab.name.lower()
        if "potassium" in lab_name_lower and (lab.value < 2.5 or lab.value > 6.5):
            is_critical = True
        elif "sodium" in lab_name_lower and (lab.value < 120 or lab.value > 160):
            is_critical = True
        elif "glucose" in lab_name_lower and (lab.value < 50 or lab.value > 500):
            is_critical = True

        if is_critical:
            value_class = "lab-critical"

        rows.append(f"""
        <tr>
            <td>{lab.name}</td>
            <td class="{value_class}">{value_display}{lab.unit}</td>
            <td>{lab.normal_low}-{lab.normal_high}{lab.unit}</td>
        </tr>
        """)

    return f"""
<table class="lab-table">
    <thead>
        <tr>
            <th>Test</th>
            <th>Result</th>
            <th>Reference</th>
        </tr>
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
<p><small>Collected: {patient.labs[0].collected_time if patient.labs else 'N/A'}</small></p>
"""


def format_vitals_html(patient) -> str:
    """Format vitals as HTML table"""
    if not patient.vitals:
        return "<p>No vital signs recorded</p>"

    # Create header row
    header_cells = "<th>Parameter</th>" + "".join(
        f"<th>{vs.time}</th>" for vs in patient.vitals
    )

    # BP row with trend detection
    bp_cells = "<td><strong>BP</strong></td>"
    for i, vs in enumerate(patient.vitals):
        bp_value = f"{vs.bp_systolic}/{vs.bp_diastolic}"
        # Check for concerning values
        if vs.bp_systolic < 100 or vs.bp_diastolic < 60:
            bp_cells += f'<td class="lab-low">{bp_value}</td>'
        elif vs.bp_systolic > 160 or vs.bp_diastolic > 100:
            bp_cells += f'<td class="lab-high">{bp_value}</td>'
        else:
            bp_cells += f"<td>{bp_value}</td>"

    # HR row
    hr_cells = "<td><strong>HR</strong></td>"
    for vs in patient.vitals:
        if vs.heart_rate < 60:
            hr_cells += f'<td class="lab-low">{vs.heart_rate}</td>'
        elif vs.heart_rate > 100:
            hr_cells += f'<td class="lab-high">{vs.heart_rate}</td>'
        else:
            hr_cells += f"<td>{vs.heart_rate}</td>"

    # RR row
    rr_cells = "<td><strong>RR</strong></td>" + "".join(
        f"<td>{vs.respiratory_rate}</td>" for vs in patient.vitals
    )

    # Temp row
    temp_cells = "<td><strong>Temp</strong></td>"
    for vs in patient.vitals:
        if vs.temperature > 100.4:
            temp_cells += f'<td class="lab-high">{vs.temperature}</td>'
        else:
            temp_cells += f"<td>{vs.temperature}</td>"

    # O2 row
    o2_cells = "<td><strong>SpO2</strong></td>"
    for vs in patient.vitals:
        if vs.o2_sat < 92:
            o2_cells += f'<td class="lab-low">{vs.o2_sat}% {vs.o2_device}</td>'
        else:
            o2_cells += f"<td>{vs.o2_sat}% {vs.o2_device}</td>"

    return f"""
<table class="lab-table">
    <thead><tr>{header_cells}</tr></thead>
    <tbody>
        <tr>{bp_cells}</tr>
        <tr>{hr_cells}</tr>
        <tr>{rr_cells}</tr>
        <tr>{temp_cells}</tr>
        <tr>{o2_cells}</tr>
    </tbody>
</table>
"""


def format_notes_html(patient) -> str:
    """Format nursing notes as HTML"""
    notes_html = "<ul style='list-style-type: none; padding-left: 0; margin: 0;'>"
    for note in patient.nursing_notes:
        notes_html += f"<li style='margin-bottom: 8px; padding: 8px; background: #f7fafc; border-radius: 4px;'>{note}</li>"
    notes_html += "</ul>"
    return notes_html


def format_md_note_html(patient) -> str:
    """Format MD progress note as HTML with highlighting instructions"""
    if not hasattr(patient, 'md_progress_note') or not patient.md_progress_note:
        return "<p style='color: #718096;'>No MD progress note available for this patient.</p>"

    # Format the note with pre-wrap to preserve spacing
    note_text = patient.md_progress_note.strip()

    return f"""
<div style="
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
">
{note_text}
</div>
<div style="
    margin-top: 12px;
    padding: 12px;
    background: #ebf8ff;
    border: 1px solid #90cdf4;
    border-radius: 8px;
    font-size: 13px;
    color: #2c5282;
">
    <strong>Tip:</strong> Copy any medical term from the note above (e.g., "CHFrEF", "A-fib", "ORIF")
    and paste it in the "Explain Medical Term" box below for a plain-language explanation.
</div>
"""


def format_ai_response(response: str, response_type: str = "normal") -> str:
    """Format AI response as styled card"""
    type_class = {
        "normal": "",
        "concern": "concern",
        "critical": "critical"
    }.get(response_type, "")

    return f"""
<div class="ai-response {type_class}">
    {response.replace(chr(10), '<br>')}
</div>
"""


def get_disclaimer() -> str:
    """Get safety disclaimer HTML"""
    return """
<div class="disclaimer">
    <strong>Important:</strong> NurseGemma is for educational purposes only.
    It is not a substitute for professional clinical judgment.
    Always verify with facility protocols and consult healthcare providers for patient care decisions.
</div>
"""


def format_time_savings(execution_seconds: float, manual_seconds: float, saved_seconds: float) -> str:
    """Format time savings as an attractive badge/card"""
    # Convert to more readable formats
    if manual_seconds >= 60:
        manual_display = f"{manual_seconds / 60:.1f} min"
    else:
        manual_display = f"{manual_seconds:.0f} sec"

    if execution_seconds >= 60:
        exec_display = f"{execution_seconds:.1f} min"
    else:
        exec_display = f"{execution_seconds:.1f} sec"

    if saved_seconds >= 60:
        saved_display = f"{saved_seconds / 60:.1f} min"
    else:
        saved_display = f"{saved_seconds:.0f} sec"

    # Calculate percentage saved
    percent_saved = (saved_seconds / manual_seconds * 100) if manual_seconds > 0 else 0

    return f"""
<div style="
    display: flex;
    gap: 16px;
    margin: 12px 0;
    padding: 12px;
    background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    border-radius: 8px;
    border-left: 4px solid #48bb78;
">
    <div style="text-align: center; flex: 1;">
        <div style="font-size: 20px; font-weight: 700; color: #22543d;">{saved_display}</div>
        <div style="font-size: 11px; color: #276749; text-transform: uppercase;">Time Saved</div>
    </div>
    <div style="text-align: center; flex: 1; border-left: 1px solid #9ae6b4; padding-left: 16px;">
        <div style="font-size: 14px; color: #2d3748;">{exec_display}</div>
        <div style="font-size: 11px; color: #718096;">NurseGemma</div>
    </div>
    <div style="text-align: center; flex: 1; border-left: 1px solid #9ae6b4; padding-left: 16px;">
        <div style="font-size: 14px; color: #718096; text-decoration: line-through;">{manual_display}</div>
        <div style="font-size: 11px; color: #718096;">Manual</div>
    </div>
    <div style="text-align: center; flex: 1; border-left: 1px solid #9ae6b4; padding-left: 16px;">
        <div style="font-size: 14px; font-weight: 600; color: #48bb78;">{percent_saved:.0f}%</div>
        <div style="font-size: 11px; color: #276749;">Faster</div>
    </div>
</div>
"""


def format_cumulative_time_savings(total_saved_seconds: float, tasks_completed: int) -> str:
    """Format cumulative session time savings"""
    if total_saved_seconds >= 3600:
        saved_display = f"{total_saved_seconds / 3600:.1f} hours"
    elif total_saved_seconds >= 60:
        saved_display = f"{total_saved_seconds / 60:.1f} minutes"
    else:
        saved_display = f"{total_saved_seconds:.0f} seconds"

    return f"""
<div style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    background: #ebf8ff;
    border-radius: 8px;
    margin-bottom: 12px;
">
    <div>
        <span style="font-weight: 600; color: #2c5282;">Session Total:</span>
        <span style="color: #2b6cb0; font-weight: 700; margin-left: 8px;">{saved_display} saved</span>
    </div>
    <div style="
        background: #3182ce;
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 600;
    ">
        {tasks_completed} task{"s" if tasks_completed != 1 else ""} completed
    </div>
</div>
"""


# ==================== MAIN UI BUILDER ====================

def build_epic_ui(companion=None, patient=None):
    """
    Build the EPIC-style NurseGemma interface

    Args:
        companion: NurseCompanion instance (optional)
        patient: SamplePatient instance to display

    Returns:
        Gradio Blocks interface
    """
    # Import sample patients if needed
    try:
        from sample_patients import MRS_JOHNSON, SAMPLE_PATIENTS
    except ImportError:
        from src.sample_patients import MRS_JOHNSON, SAMPLE_PATIENTS

    if patient is None:
        patient = MRS_JOHNSON

    # Import agentic workflows
    try:
        from agentic_workflows import (
            AgenticNurse, WorkflowType,
            quick_admission, quick_lab_response, quick_handoff,
            quick_med_safety, quick_md_message
        )
    except ImportError:
        from src.agentic_workflows import (
            AgenticNurse, WorkflowType,
            quick_admission, quick_lab_response, quick_handoff,
            quick_med_safety, quick_md_message
        )

    # Create agent
    agent = AgenticNurse(companion) if companion else AgenticNurse()

    # Session tracking for cumulative time savings
    session_stats = {
        "total_time_saved": 0.0,
        "tasks_completed": 0
    }

    # Define workflow handlers
    def run_admission_workflow():
        result = agent.run_workflow(
            WorkflowType.ADMISSION,
            patient.get_full_context()
        )
        # Track session stats
        session_stats["total_time_saved"] += result.time_saved_seconds
        session_stats["tasks_completed"] += 1

        # Build response with time savings
        response = format_ai_response(result.final_output, "normal")
        time_display = format_time_savings(
            result.execution_time_seconds,
            result.estimated_manual_time_seconds,
            result.time_saved_seconds
        )
        cumulative = format_cumulative_time_savings(
            session_stats["total_time_saved"],
            session_stats["tasks_completed"]
        )
        return cumulative + time_display + response

    def run_lab_workflow():
        lab_text = "\n".join([
            f"{lab.name}: {lab.value}{lab.unit}"
            for lab in patient.labs
        ])
        result = agent.run_workflow(
            WorkflowType.CRITICAL_LAB,
            lab_text,
            {"patient": patient.name, "medications": [m.name for m in patient.medications]}
        )
        # Track session stats
        session_stats["total_time_saved"] += result.time_saved_seconds
        session_stats["tasks_completed"] += 1

        # Determine response type based on priority
        resp_type = "critical" if "CRITICAL" in result.final_output else "concern" if "URGENT" in result.final_output else "normal"

        # Build response with time savings
        response = format_ai_response(result.final_output, resp_type)
        time_display = format_time_savings(
            result.execution_time_seconds,
            result.estimated_manual_time_seconds,
            result.time_saved_seconds
        )
        cumulative = format_cumulative_time_savings(
            session_stats["total_time_saved"],
            session_stats["tasks_completed"]
        )
        return cumulative + time_display + response

    def run_handoff_workflow():
        notes_text = "\n".join(patient.nursing_notes)
        result = agent.run_workflow(
            WorkflowType.SHIFT_HANDOFF,
            notes_text
        )
        # Track session stats
        session_stats["total_time_saved"] += result.time_saved_seconds
        session_stats["tasks_completed"] += 1

        # Build response with time savings
        response = format_ai_response(result.final_output, "normal")
        time_display = format_time_savings(
            result.execution_time_seconds,
            result.estimated_manual_time_seconds,
            result.time_saved_seconds
        )
        cumulative = format_cumulative_time_savings(
            session_stats["total_time_saved"],
            session_stats["tasks_completed"]
        )
        return cumulative + time_display + response

    def run_med_safety_workflow():
        med_text = "\n".join([
            f"{m.name} {m.dose} {m.route} {m.frequency}"
            for m in patient.medications
        ])
        result = agent.run_workflow(
            WorkflowType.MEDICATION_SAFETY,
            med_text,
            {"patient": patient.name, "allergies": patient.allergies}
        )
        # Track session stats
        session_stats["total_time_saved"] += result.time_saved_seconds
        session_stats["tasks_completed"] += 1

        resp_type = "critical" if any(m.high_alert for m in patient.medications) else "normal"

        # Build response with time savings
        response = format_ai_response(result.final_output, resp_type)
        time_display = format_time_savings(
            result.execution_time_seconds,
            result.estimated_manual_time_seconds,
            result.time_saved_seconds
        )
        cumulative = format_cumulative_time_savings(
            session_stats["total_time_saved"],
            session_stats["tasks_completed"]
        )
        return cumulative + time_display + response

    def run_md_communication(request_text):
        if not request_text:
            return format_ai_response("Please enter what you need from the MD.", "normal")
        result = agent.run_workflow(
            WorkflowType.MD_COMMUNICATION,
            request_text,
            {"patient": patient.name, "vitals": str(patient.vitals[-1] if patient.vitals else {})}
        )
        # Track session stats
        session_stats["total_time_saved"] += result.time_saved_seconds
        session_stats["tasks_completed"] += 1

        # Build response with time savings
        response = format_ai_response(result.final_output, "normal")
        time_display = format_time_savings(
            result.execution_time_seconds,
            result.estimated_manual_time_seconds,
            result.time_saved_seconds
        )
        cumulative = format_cumulative_time_savings(
            session_stats["total_time_saved"],
            session_stats["tasks_completed"]
        )
        return cumulative + time_display + response

    def analyze_input(input_text):
        """Analyze copy/pasted text"""
        if not input_text:
            return format_ai_response("Paste lab values, vitals, or medication list for analysis.", "normal")

        # Detect type and run appropriate workflow
        input_lower = input_text.lower()

        if any(lab in input_lower for lab in ["potassium", "sodium", "glucose", "wbc", "hemoglobin", "creatinine"]):
            result = agent.run_workflow(WorkflowType.CRITICAL_LAB, input_text)
        elif any(med in input_lower for med in ["mg", "mcg", "units", "tablet", "injection"]):
            result = agent.run_workflow(WorkflowType.MEDICATION_SAFETY, input_text)
        else:
            result = agent.run_workflow(WorkflowType.SHIFT_HANDOFF, input_text)

        # Track session stats
        session_stats["total_time_saved"] += result.time_saved_seconds
        session_stats["tasks_completed"] += 1

        resp_type = "critical" if "CRITICAL" in result.final_output else "normal"

        # Build response with time savings
        response = format_ai_response(result.final_output, resp_type)
        time_display = format_time_savings(
            result.execution_time_seconds,
            result.estimated_manual_time_seconds,
            result.time_saved_seconds
        )
        cumulative = format_cumulative_time_savings(
            session_stats["total_time_saved"],
            session_stats["tasks_completed"]
        )
        return cumulative + time_display + response

    def explain_term(term_text, audience):
        """Explain highlighted medical term"""
        if not term_text or not term_text.strip():
            return format_ai_response("Please enter a medical term or abbreviation to explain.", "normal")

        # Use companion if available, otherwise use mock
        if companion:
            try:
                from nurse_companion import ReadingLevel
            except ImportError:
                from src.nurse_companion import ReadingLevel
            reading_level = ReadingLevel.BASIC if audience == "patient" else ReadingLevel.ADVANCED
            explanation = companion.explain_highlighted_text(
                highlighted_text=term_text.strip(),
                reading_level=reading_level,
                audience="patient" if audience == "patient" else "nursing"
            )
            return format_ai_response(explanation, "normal")
        else:
            # Mock response without model
            return format_ai_response(
                f"**Explaining: {term_text.strip()}**\n\n"
                f"This feature will provide a plain-language explanation of the medical term "
                f"'{term_text.strip()}' when MedGemma is loaded.\n\n"
                f"Audience: {audience}\n\n"
                f"*Note: Running in demo mode without model.*",
                "normal"
            )

    def change_patient(patient_name):
        """Switch to different sample patient"""
        new_patient = SAMPLE_PATIENTS.get(patient_name.lower().replace(" ", "_"))
        if new_patient:
            return (
                create_patient_header(new_patient),
                format_mar_html(new_patient),
                format_labs_html(new_patient),
                format_vitals_html(new_patient),
                format_notes_html(new_patient),
                format_md_note_html(new_patient),
            )
        return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update())

    # Build interface
    with gr.Blocks(css=EPIC_CSS, title="NurseGemma", theme=gr.themes.Soft()) as demo:

        # Patient header
        header = gr.HTML(create_patient_header(patient))

        with gr.Row():
            # Left column - Chart Data
            with gr.Column(scale=1):
                gr.Markdown("### Chart Data")

                with gr.Tabs():
                    with gr.Tab("MAR"):
                        mar_display = gr.HTML(format_mar_html(patient))

                    with gr.Tab("Labs"):
                        labs_display = gr.HTML(format_labs_html(patient))

                    with gr.Tab("Vitals"):
                        vitals_display = gr.HTML(format_vitals_html(patient))

                    with gr.Tab("Notes"):
                        notes_display = gr.HTML(format_notes_html(patient))

                    with gr.Tab("MD Note"):
                        md_note_display = gr.HTML(format_md_note_html(patient))

                # Patient selector
                gr.Markdown("---")
                patient_dropdown = gr.Dropdown(
                    choices=["Mrs. Johnson", "Mr. Smith", "Ms. Rodriguez", "Mr. Chen"],
                    value="Mrs. Johnson",
                    label="Select Patient"
                )
                patient_dropdown.change(
                    change_patient,
                    inputs=[patient_dropdown],
                    outputs=[header, mar_display, labs_display, vitals_display, notes_display, md_note_display]
                )

            # Right column - AI Companion
            with gr.Column(scale=1):
                gr.Markdown("### NurseGemma AI Companion")

                # AI output area
                ai_output = gr.HTML(format_ai_response(
                    "Select a workflow below or paste data to analyze.\n\n"
                    "I can help with:\n"
                    "- Analyzing lab values\n"
                    "- Checking medication safety\n"
                    "- Generating SBAR handoffs\n"
                    "- Creating family explanations\n"
                    "- Composing MD communications",
                    "normal"
                ))

                # Input for copy/paste analysis
                with gr.Accordion("Paste Data for Analysis", open=False):
                    paste_input = gr.Textbox(
                        placeholder="Paste lab values, vitals, or notes here...",
                        lines=4,
                        label="Input Data"
                    )
                    analyze_btn = gr.Button("Analyze", variant="secondary")
                    analyze_btn.click(analyze_input, inputs=[paste_input], outputs=[ai_output])

                # Explain Medical Term (highlight-to-explain)
                with gr.Accordion("Explain Medical Term", open=False):
                    gr.Markdown("*Copy a term from the MD Note or any clinical document and paste here for explanation*")
                    term_input = gr.Textbox(
                        placeholder="e.g., CHFrEF, A-fib with RVR, ORIF, DKA, CAP, BNP...",
                        lines=1,
                        label="Medical Term or Abbreviation"
                    )
                    audience_select = gr.Radio(
                        choices=["nursing", "patient"],
                        value="nursing",
                        label="Explanation For",
                        info="Nursing: clinical details | Patient: simple language for families"
                    )
                    explain_btn = gr.Button("Explain", variant="secondary")
                    explain_btn.click(explain_term, inputs=[term_input, audience_select], outputs=[ai_output])

                # MD Communication
                with gr.Accordion("Compose MD Message", open=False):
                    md_request = gr.Textbox(
                        placeholder="What do you need from the MD? e.g., 'BP dropped, should we hold Lisinopril?'",
                        lines=2,
                        label="Your Request"
                    )
                    md_btn = gr.Button("Compose Message", variant="secondary")
                    md_btn.click(run_md_communication, inputs=[md_request], outputs=[ai_output])

        # Workflow buttons
        gr.Markdown("---")
        gr.Markdown("### One-Click Workflows")

        with gr.Row():
            admission_btn = gr.Button(" Admission Analysis", variant="primary")
            lab_btn = gr.Button(" Lab Response", variant="secondary")
            handoff_btn = gr.Button(" Shift Handoff", variant="secondary")
            med_btn = gr.Button(" Med Safety", variant="secondary")

        # Connect buttons
        admission_btn.click(run_admission_workflow, outputs=[ai_output])
        lab_btn.click(run_lab_workflow, outputs=[ai_output])
        handoff_btn.click(run_handoff_workflow, outputs=[ai_output])
        med_btn.click(run_med_safety_workflow, outputs=[ai_output])

        # Disclaimer
        gr.HTML(get_disclaimer())

    return demo


# ==================== STANDALONE LAUNCH ====================

if __name__ == "__main__":
    print("Launching NurseGemma EPIC-Style UI...")
    print("This is a demo without the MedGemma model loaded.")
    print("Workflows will return mock responses.")

    demo = build_epic_ui()
    demo.launch(share=False)
