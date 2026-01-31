"""
NurseGemma Code Blue Agent
Real-time voice-activated cardiac arrest documentation with ACLS 2025 algorithm

Fully compliant with AHA 2025 Guidelines for CPR and ECC.

Voice commands → Auto-timestamped events → ACLS-guided prompts → Code Blue Record

Key ACLS 2025 features:
- VF/pVT: Shock first, Epi after 2nd shock, Amio after 3rd shock
- PEA/Asystole: Epi ASAP, treat H's and T's
- CPR quality prompts (100-120/min, >2 inches, q2min switch)
- Drug timing alerts (Epi q3-5min)
- H's and T's checklist
- ETCO2 monitoring prompts
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import ACLS protocol reference
try:
    from acls_protocol import (
        DRUGS, CPR_QUALITY, REVERSIBLE_CAUSES, 
        VF_PVT_ALGORITHM, PEA_ASYSTOLE_ALGORITHM,
        get_epi_timing_advice, get_antiarrhythmic_advice, format_hs_ts_checklist
    )
    ACLS_LOADED = True
except ImportError:
    ACLS_LOADED = False


class Rhythm(Enum):
    UNKNOWN = "Unknown"
    VF = "Ventricular Fibrillation"
    VT = "Pulseless VT"
    PEA = "Pulseless Electrical Activity"
    ASYSTOLE = "Asystole"
    ROSC = "ROSC"
    

class ACLSPath(Enum):
    SHOCKABLE = "VF/pVT (Shockable)"
    NON_SHOCKABLE = "PEA/Asystole (Non-Shockable)"


@dataclass
class CodeEvent:
    """Single event during code blue."""
    timestamp: datetime
    event_type: str
    details: str
    run_time_seconds: int  # Time since code started
    
    def format_time(self) -> str:
        """Format as HH:MM:SS."""
        return self.timestamp.strftime("%H:%M:%S")
    
    def format_run_time(self) -> str:
        """Format run time as MM:SS."""
        mins = self.run_time_seconds // 60
        secs = self.run_time_seconds % 60
        return f"{mins:02d}:{secs:02d}"


@dataclass 
class CodeBlueSession:
    """Active code blue documentation session - ACLS 2025 compliant."""
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    # Events log
    events: List[CodeEvent] = field(default_factory=list)
    
    # ACLS tracking
    current_rhythm: Rhythm = Rhythm.UNKNOWN
    acls_path: Optional[ACLSPath] = None
    
    # CPR tracking
    cpr_cycles: int = 0
    last_cpr_start: Optional[datetime] = None
    compressor_changes: List[datetime] = field(default_factory=list)
    
    # Medication tracking - ACLS 2025 compliant timing
    epi_doses: List[datetime] = field(default_factory=list)
    amiodarone_doses: List[tuple] = field(default_factory=list)  # (time, mg)
    lidocaine_doses: List[tuple] = field(default_factory=list)  # (time, mg)
    other_meds: List[tuple] = field(default_factory=list)  # (time, med, dose)
    
    # Defibrillation
    shocks: List[tuple] = field(default_factory=list)  # (time, joules)
    
    # Airway
    airway_type: Optional[str] = None
    airway_time: Optional[datetime] = None
    
    # Access
    iv_access: bool = False
    io_access: bool = False
    access_time: Optional[datetime] = None
    
    # ETCO2 monitoring (ACLS 2025)
    etco2_values: List[tuple] = field(default_factory=list)  # (time, value)
    
    # H's and T's checked
    hs_ts_checked: bool = False
    
    # Outcome
    outcome: Optional[str] = None  # ROSC, Expired, Transferred
    
    def get_run_time(self) -> int:
        """Get seconds since code started."""
        return int((datetime.now() - self.start_time).total_seconds())
    
    def add_event(self, event_type: str, details: str = ""):
        """Add timestamped event."""
        event = CodeEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            details=details,
            run_time_seconds=self.get_run_time()
        )
        self.events.append(event)
        return event
    
    def time_since_last_epi(self) -> Optional[int]:
        """Seconds since last epinephrine dose."""
        if not self.epi_doses:
            return None
        return int((datetime.now() - self.epi_doses[-1]).total_seconds())
    
    def is_epi_due(self) -> bool:
        """Check if epinephrine is due (every 3-5 min)."""
        elapsed = self.time_since_last_epi()
        if elapsed is None:
            return True  # No epi given yet
        return elapsed >= 180  # 3 minutes
    
    def time_since_cpr_start(self) -> Optional[int]:
        """Seconds since current CPR cycle started."""
        if not self.last_cpr_start:
            return None
        return int((datetime.now() - self.last_cpr_start).total_seconds())
    
    def is_rhythm_check_due(self) -> bool:
        """Check if 2-minute rhythm check is due."""
        elapsed = self.time_since_cpr_start()
        if elapsed is None:
            return False
        return elapsed >= 120  # 2 minutes


class CodeBlueAgent:
    """
    Voice-activated Code Blue documentation agent.
    
    Integrates with ACLS 2025 algorithm:
    - VF/pVT pathway: Shock → CPR → Epi → Shock → Amio/Lido
    - PEA/Asystole pathway: CPR → Epi → CPR → Treat reversible causes
    """
    
    # Voice command patterns
    COMMANDS = {
        # CPR
        "cpr started": "start_cpr",
        "cpr start": "start_cpr",
        "start cpr": "start_cpr",
        "compressions started": "start_cpr",
        "cpr stopped": "stop_cpr",
        "cpr paused": "pause_cpr",
        "switch": "switch_compressor",
        "switch compressor": "switch_compressor",
        "compressor change": "switch_compressor",
        
        # Rhythm/Pulse
        "pulse check": "pulse_check",
        "check pulse": "pulse_check",
        "rhythm check": "rhythm_check",
        "check rhythm": "rhythm_check",
        "no pulse": "no_pulse",
        "pulse present": "pulse_present",
        "rosc": "rosc",
        "got a pulse": "rosc",
        "we have a pulse": "rosc",
        
        # Rhythms
        "v fib": "rhythm_vf",
        "v-fib": "rhythm_vf",
        "vfib": "rhythm_vf",
        "vf": "rhythm_vf",
        "ventricular fibrillation": "rhythm_vf",
        "v tach": "rhythm_vt",
        "v-tach": "rhythm_vt",
        "vtach": "rhythm_vt",
        "vt": "rhythm_vt",
        "pulseless vt": "rhythm_vt",
        "pulseless v-tach": "rhythm_vt",
        "pea": "rhythm_pea",
        "p.e.a": "rhythm_pea",
        "pulseless electrical": "rhythm_pea",
        "asystole": "rhythm_asystole",
        "flatline": "rhythm_asystole",
        "flat line": "rhythm_asystole",
        "sinus rhythm": "rhythm_sinus",
        "sinus": "rhythm_sinus",
        "nsr": "rhythm_sinus",
        "normal sinus": "rhythm_sinus",
        
        # Defibrillation
        "shock advised": "shock_advised",
        "charging": "charging",
        "clear": "clear",
        "shock delivered": "shock_delivered",
        "shock given": "shock_delivered",
        "no shock advised": "no_shock_advised",
        
        # Medications
        "epi given": "epi_given",
        "epinephrine given": "epi_given",
        "epi in": "epi_given",
        "1 of epi": "epi_given",
        "push epi": "epi_given",
        "amiodarone": "amio_given",
        "amio given": "amio_given",
        "amio 300": "amio_300",
        "300 of amio": "amio_300",
        "300 amio": "amio_300",
        "amio 150": "amio_150",
        "150 of amio": "amio_150",
        "150 amio": "amio_150",
        "lidocaine": "lido_given",
        "lido given": "lido_given",
        "lido": "lido_given",
        "1 of lido": "lido_given",
        
        # ETCO2 monitoring (ACLS 2025)
        "etco2": "etco2",
        "end tidal": "etco2",
        "co2": "etco2",
        "capnography": "etco2",
        
        # H's and T's
        "check h's and t's": "hs_ts_check",
        "reversible causes": "hs_ts_check",
        "h's and t's": "hs_ts_check",
        
        "bicarb": "bicarb_given",
        "calcium": "calcium_given",
        "mag": "mag_given",
        "magnesium": "mag_given",
        
        # Airway
        "intubated": "intubated",
        "tube in": "intubated",
        "et tube placed": "intubated",
        "lma placed": "lma_placed",
        "supraglottic": "lma_placed",
        "bagging": "bvm",
        "bvm": "bvm",
        
        # Access
        "iv access": "iv_access",
        "iv in": "iv_access",
        "io access": "io_access",
        "io in": "io_access",
        
        # Code status
        "code called": "code_start",
        "code blue team": "team_arrives",
        "team arrives": "team_arrives",
        "team arrived": "team_arrives",
        "code team": "team_arrives",
        "rapid response": "rrt_arrives",
        "rrt arrives": "rrt_arrives",
        "anesthesia": "anesthesia_arrives",
        "respiratory": "rt_arrives",
        "rt arrives": "rt_arrives",
        "pharmacy": "pharmacy_arrives",
        "attending": "attending_arrives",
        "doctor": "md_arrives",
        "md arrives": "md_arrives",
        "time of death": "time_of_death",
        "code ended": "code_end",
        "stop code": "code_end",
    }
    
    def __init__(self):
        self.session: Optional[CodeBlueSession] = None
        
    def start_code(self, start_time: Optional[datetime] = None) -> str:
        """Initialize new code blue session with optional manual start time."""
        self.session = CodeBlueSession()
        if start_time:
            self.session.start_time = start_time
        event = self.session.add_event("CODE_CALLED", "Code Blue initiated")
        return f"""
🚨 **CODE BLUE INITIATED** - {event.format_time()}

**ACLS Protocol Active**
━━━━━━━━━━━━━━━━━━━━━━━

📋 **Immediate Actions:**
1. Start high-quality CPR (100-120/min, 2+ inches)
2. Attach monitor/defibrillator  
3. Establish IV/IO access
4. Identify rhythm

🎤 **Voice Commands Ready:**
- "CPR started"
- "Rhythm check" / "V-fib" / "Asystole" / "PEA"
- "Epi given" / "Shock delivered"
- "ROSC" when pulse returns

⏱️ Timer running...
"""

    def process_voice(self, text: str) -> str:
        """Process voice input and return response with prompts."""
        if not self.session:
            # Auto-start if saying code-related things
            if any(cmd in text.lower() for cmd in ["code", "cpr", "arrest"]):
                # Check for manual start time
                manual_time = self._extract_time(text) if hasattr(self, '_extract_time') else None
                return self.start_code(manual_time)
            return "🎤 Say 'Code called' to start Code Blue documentation"
        
        text_lower = text.lower().strip()
        
        # Find matching command
        for pattern, action in self.COMMANDS.items():
            if pattern in text_lower:
                return self._execute_action(action, text)
        
        # No command matched - log as note
        event = self.session.add_event("NOTE", text)
        return f"📝 [{event.format_run_time()}] Note: {text}"
    
    def _execute_action(self, action: str, original_text: str) -> str:
        """Execute recognized action and return formatted response."""
        
        # Check for manual timestamp in the text
        manual_time = self._extract_time(original_text)
        time_note = f" *(manual: {manual_time.strftime('%H:%M:%S')})*" if manual_time else ""
        
        # === CPR ===
        if action == "start_cpr":
            event_time = manual_time or datetime.now()
            self.session.last_cpr_start = event_time
            self.session.cpr_cycles += 1
            event = self.add_event_with_time("CPR_START", f"Cycle {self.session.cpr_cycles}", manual_time)
            return self._format_cpr_start(event) + time_note
        
        if action == "switch_compressor":
            event_time = manual_time or datetime.now()
            self.session.compressor_changes.append(event_time)
            event = self.add_event_with_time("COMPRESSOR_SWITCH", "", manual_time)
            return f"🔄 [{event.format_run_time()}] **Compressor switched** - Good teamwork!{time_note}"
        
        # === Rhythm ===
        if action == "pulse_check" or action == "rhythm_check":
            event = self.add_event_with_time("RHYTHM_CHECK", "", manual_time)
            return self._format_rhythm_check(event) + time_note
        
        if action == "rhythm_vf":
            self.session.current_rhythm = Rhythm.VF
            self.session.acls_path = ACLSPath.SHOCKABLE
            event = self.add_event_with_time("RHYTHM", "VF identified", manual_time)
            return self._format_shockable_rhythm(event, "V-FIB") + time_note
        
        if action == "rhythm_vt":
            self.session.current_rhythm = Rhythm.VT
            self.session.acls_path = ACLSPath.SHOCKABLE
            event = self.add_event_with_time("RHYTHM", "Pulseless VT identified", manual_time)
            return self._format_shockable_rhythm(event, "Pulseless V-TACH") + time_note
        
        if action == "rhythm_pea":
            self.session.current_rhythm = Rhythm.PEA
            self.session.acls_path = ACLSPath.NON_SHOCKABLE
            event = self.add_event_with_time("RHYTHM", "PEA identified", manual_time)
            return self._format_non_shockable_rhythm(event, "PEA") + time_note
        
        if action == "rhythm_asystole":
            self.session.current_rhythm = Rhythm.ASYSTOLE
            self.session.acls_path = ACLSPath.NON_SHOCKABLE
            event = self.add_event_with_time("RHYTHM", "Asystole", manual_time)
            return self._format_non_shockable_rhythm(event, "ASYSTOLE") + time_note
        
        if action == "rhythm_sinus":
            event = self.add_event_with_time("RHYTHM", "Sinus rhythm - organized!", manual_time)
            return f"💓 [{event.format_run_time()}] **Sinus Rhythm** - Organized rhythm!{time_note}\n\n🔍 **CHECK PULSE NOW!** Could be ROSC!"
        
        if action == "no_pulse":
            event = self.add_event_with_time("PULSE_CHECK", "No pulse", manual_time)
            return f"❌ [{event.format_run_time()}] **No pulse** - Continue CPR{time_note}\n\n{self._get_next_prompt()}"
        
        # === ROSC ===
        if action == "rosc" or action == "pulse_present":
            self.session.current_rhythm = Rhythm.ROSC
            self.session.outcome = "ROSC"
            event = self.add_event_with_time("ROSC", "Return of spontaneous circulation", manual_time)
            return self._format_rosc(event) + time_note
        
        # === Defibrillation ===
        if action == "shock_advised":
            event = self.add_event_with_time("DEFIB", "Shock advised", manual_time)
            return f"⚡ [{event.format_run_time()}] **Shock advised** - Charging...{time_note}\n🔊 Say 'Clear' then 'Shock delivered'"
        
        if action == "clear":
            event = self.add_event_with_time("DEFIB", "Clear called", manual_time)
            return f"⚠️ [{event.format_run_time()}] **CLEAR!** - Deliver shock{time_note}"
        
        if action == "shock_delivered":
            joules = self._extract_joules(original_text) or 200
            event_time = manual_time or datetime.now()
            self.session.shocks.append((event_time, joules))
            event = self.add_event_with_time("SHOCK", f"{joules}J delivered", manual_time)
            return self._format_shock_delivered(event, joules) + time_note
        
        if action == "no_shock_advised":
            event = self.add_event_with_time("DEFIB", "No shock advised", manual_time)
            return f"🚫 [{event.format_run_time()}] **No shock advised** - Non-shockable rhythm{time_note}\n\n➡️ Continue CPR, give Epi ASAP"
        
        # === Medications ===
        if action == "epi_given":
            event_time = manual_time or datetime.now()
            self.session.epi_doses.append(event_time)
            dose_num = len(self.session.epi_doses)
            event = self.add_event_with_time("MED", f"Epinephrine 1mg IV (dose #{dose_num})", manual_time)
            return self._format_epi_given(event, dose_num) + time_note
        
        if action == "amio_given" or action == "amio_300":
            mg = 300 if not self.session.amiodarone_doses else 150
            event_time = manual_time or datetime.now()
            self.session.amiodarone_doses.append((event_time, mg))
            event = self.add_event_with_time("MED", f"Amiodarone {mg}mg IV", manual_time)
            return f"💊 [{event.format_run_time()}] **Amiodarone {mg}mg** given{time_note}\n\n{'➡️ Second dose: 150mg if needed' if mg == 300 else ''}"
        
        if action == "amio_150":
            event_time = manual_time or datetime.now()
            self.session.amiodarone_doses.append((event_time, 150))
            event = self.add_event_with_time("MED", "Amiodarone 150mg IV", manual_time)
            return f"💊 [{event.format_run_time()}] **Amiodarone 150mg** given{time_note}"
        
        if action == "lido_given":
            # Lidocaine: 1-1.5 mg/kg first, 0.5-0.75 mg/kg subsequent
            dose_num = len(self.session.lidocaine_doses) + 1
            dose = "1-1.5 mg/kg" if dose_num == 1 else "0.5-0.75 mg/kg"
            event_time = manual_time or datetime.now()
            self.session.lidocaine_doses.append((event_time, dose))
            event = self.add_event_with_time("MED", f"Lidocaine {dose} IV (dose #{dose_num})", manual_time)
            return f"💊 [{event.format_run_time()}] **Lidocaine {dose}** given (dose #{dose_num}){time_note}\n\n{'⚠️ Max 3 mg/kg total' if dose_num >= 2 else ''}"
        
        # === ETCO2 Monitoring (ACLS 2025) ===
        if action == "etco2":
            # Try to extract ETCO2 value from text
            import re
            search_text = original_text.lower()
            
            # Remove any time patterns first (HH:MM or HH:MM:SS)
            search_text = re.sub(r'\d{1,2}:\d{2}(:\d{2})?', '', search_text)
            
            # First try: number right after etco2/co2/end tidal
            specific_match = re.search(r'(?:etco2|co2|end tidal|capnography)\s*[:\-]?\s*(\d+)', search_text)
            if specific_match:
                value = int(specific_match.group(1))
            else:
                # Fallback: find all remaining numbers (after time removed)
                all_nums = re.findall(r'\b(\d{1,3})\b', search_text)
                valid_nums = [int(n) for n in all_nums if 0 <= int(n) <= 100]
                if valid_nums:
                    value = valid_nums[-1]  # Take last number (usually the value)
                else:
                    return "📊 Say ETCO2 value (e.g., 'ETCO2 25' or 'End tidal 40')"
            
            event_time = manual_time or datetime.now()
            self.session.etco2_values.append((event_time, value))
            event = self.add_event_with_time("ETCO2", f"{value} mmHg", manual_time)
            
            # ACLS interpretation
            if value >= 40:
                interpretation = "🎉 **ETCO2 ≥40 - Possible ROSC!** Check pulse!"
            elif value >= 10:
                interpretation = "✅ ETCO2 adequate - continue CPR"
            else:
                interpretation = "⚠️ **Low ETCO2 (<10)** - Reassess CPR quality!"
            
            return f"📊 [{event.format_run_time()}] **ETCO2: {value} mmHg**{time_note}\n\n{interpretation}"
        
        # === H's and T's Checklist ===
        if action == "hs_ts_check":
            self.session.hs_ts_checked = True
            event = self.add_event_with_time("ASSESSMENT", "H's and T's reviewed", manual_time)
            if ACLS_LOADED:
                checklist = format_hs_ts_checklist()
            else:
                checklist = """
🔍 **REVERSIBLE CAUSES - Check Now!**

**5 H's:**
□ Hypovolemia → Fluids/blood
□ Hypoxia → Airway/O2
□ H+ (Acidosis) → Ventilate, bicarb?
□ Hypo/Hyperkalemia → ECG, treat K+
□ Hypothermia → Rewarm

**5 T's:**
□ Tension pneumo → Needle decompress
□ Tamponade → Pericardiocentesis  
□ Toxins → Antidotes
□ Thrombosis (PE) → Lytics/ECMO
□ Thrombosis (MI) → PCI
"""
            return f"🔍 [{event.format_run_time()}] **Checking Reversible Causes**{time_note}\n{checklist}"
        
        if action == "bicarb_given":
            event_time = manual_time or datetime.now()
            self.session.other_meds.append((event_time, "Sodium Bicarbonate", "50mEq"))
            event = self.add_event_with_time("MED", "Sodium Bicarbonate 50mEq IV", manual_time)
            return f"💊 [{event.format_run_time()}] **Bicarb 50mEq** given{time_note}"
        
        if action == "calcium_given":
            event_time = manual_time or datetime.now()
            self.session.other_meds.append((event_time, "Calcium Chloride", "1g"))
            event = self.add_event_with_time("MED", "Calcium Chloride 1g IV", manual_time)
            return f"💊 [{event.format_run_time()}] **Calcium 1g** given{time_note}"
        
        if action == "mag_given":
            event_time = manual_time or datetime.now()
            self.session.other_meds.append((event_time, "Magnesium Sulfate", "2g"))
            event = self.add_event_with_time("MED", "Magnesium Sulfate 2g IV", manual_time)
            return f"💊 [{event.format_run_time()}] **Mag 2g** given (Torsades protocol){time_note}"
        
        # === Airway ===
        if action == "intubated":
            self.session.airway_type = "ETT"
            self.session.airway_time = manual_time or datetime.now()
            event = self.add_event_with_time("AIRWAY", "ET tube placed", manual_time)
            return f"🫁 [{event.format_run_time()}] **Intubated** - Confirm with waveform capnography{time_note}\n\n➡️ Continuous compressions, 1 breath q6 sec"
        
        if action == "lma_placed":
            self.session.airway_type = "LMA"
            self.session.airway_time = manual_time or datetime.now()
            event = self.add_event_with_time("AIRWAY", "Supraglottic airway placed", manual_time)
            return f"🫁 [{event.format_run_time()}] **LMA placed** - Confirm placement{time_note}\n\n➡️ Continuous compressions, 1 breath q6 sec"
        
        # === Access ===
        if action == "iv_access":
            self.session.iv_access = True
            self.session.access_time = manual_time or datetime.now()
            event = self.add_event_with_time("ACCESS", "IV access established", manual_time)
            return f"💉 [{event.format_run_time()}] **IV access** established{time_note}\n\n{'➡️ Give Epinephrine 1mg now!' if self.session.is_epi_due() else ''}"
        
        if action == "io_access":
            self.session.io_access = True
            self.session.access_time = manual_time or datetime.now()
            event = self.add_event_with_time("ACCESS", "IO access established", manual_time)
            return f"🦴 [{event.format_run_time()}] **IO access** established{time_note}\n\n{'➡️ Give Epinephrine 1mg now!' if self.session.is_epi_due() else ''}"
        
        # === Team Arrivals ===
        if action == "team_arrives":
            event = self.add_event_with_time("TEAM", "Code Blue team arrived", manual_time)
            return f"👥 [{event.format_run_time()}] **Code Blue Team arrived**{time_note}"
        
        if action == "rrt_arrives":
            event = self.add_event_with_time("TEAM", "Rapid Response Team arrived", manual_time)
            return f"👥 [{event.format_run_time()}] **RRT arrived**{time_note}"
        
        if action == "anesthesia_arrives":
            event = self.add_event_with_time("TEAM", "Anesthesia arrived", manual_time)
            return f"👨‍⚕️ [{event.format_run_time()}] **Anesthesia arrived**{time_note}"
        
        if action == "rt_arrives":
            event = self.add_event_with_time("TEAM", "Respiratory Therapy arrived", manual_time)
            return f"🫁 [{event.format_run_time()}] **RT arrived**{time_note}"
        
        if action == "pharmacy_arrives":
            event = self.add_event_with_time("TEAM", "Pharmacy arrived", manual_time)
            return f"💊 [{event.format_run_time()}] **Pharmacy arrived**{time_note}"
        
        if action == "attending_arrives":
            event = self.add_event_with_time("TEAM", "Attending physician arrived", manual_time)
            return f"👨‍⚕️ [{event.format_run_time()}] **Attending arrived**{time_note}"
        
        if action == "md_arrives":
            event = self.add_event_with_time("TEAM", "Physician arrived", manual_time)
            return f"👨‍⚕️ [{event.format_run_time()}] **MD arrived**{time_note}"
        
        # === Code End ===
        if action == "time_of_death":
            self.session.end_time = manual_time or datetime.now()
            self.session.outcome = "Expired"
            event = self.add_event_with_time("CODE_END", "Time of death called", manual_time)
            return self._format_code_end(event, "Expired")
        
        if action == "code_end":
            self.session.end_time = manual_time or datetime.now()
            if not self.session.outcome:
                self.session.outcome = "Ended"
            event = self.add_event_with_time("CODE_END", "Code concluded", manual_time)
            return self._format_code_end(event, self.session.outcome)
        
        return f"📝 Noted: {original_text}"
    
    # === Formatting Helpers ===
    
    def _format_cpr_start(self, event: CodeEvent) -> str:
        cycle = self.session.cpr_cycles
        return f"""
💪 [{event.format_run_time()}] **CPR Cycle {cycle} Started**

📋 **High-Quality CPR:**
• Push hard: ≥2 inches (5 cm)
• Push fast: 100-120/min
• Full chest recoil
• Minimize interruptions

⏱️ 2-minute timer started...
{self._get_next_prompt()}
"""

    def _format_rhythm_check(self, event: CodeEvent) -> str:
        prompts = []
        if self.session.is_epi_due():
            epi_time = self.session.time_since_last_epi()
            if epi_time:
                prompts.append(f"⚠️ Epi due! Last dose {epi_time//60}:{epi_time%60:02d} ago")
            else:
                prompts.append("⚠️ No Epi given yet!")
        
        return f"""
🔍 [{event.format_run_time()}] **RHYTHM CHECK**

🎤 **What's the rhythm?**
• "V-fib" or "V-tach" → Shockable
• "PEA" or "Asystole" → Non-shockable
• "ROSC" → We got 'em back!

{chr(10).join(prompts)}
"""

    def _format_shockable_rhythm(self, event: CodeEvent, rhythm: str) -> str:
        shock_num = len(self.session.shocks) + 1
        epi_doses = len(self.session.epi_doses)
        amio_doses = len(self.session.amiodarone_doses)
        
        # ACLS 2025 compliant guidance
        if shock_num == 1:
            next_steps = """1. ⚡ **SHOCK NOW** (120-200J biphasic)
2. 💪 Resume CPR immediately x 2 min
3. 🔍 Rhythm check at 2 min"""
        elif shock_num == 2:
            next_steps = """1. ⚡ **SHOCK #2** 
2. 💪 Resume CPR immediately
3. 💉 **Give Epi 1mg** (after this shock!)
4. 🔍 Rhythm check at 2 min"""
        elif shock_num == 3:
            next_steps = f"""1. ⚡ **SHOCK #3**
2. 💪 Resume CPR immediately  
3. {'💉 Epi 1mg (if >3min since last)' if epi_doses > 0 else '💉 Give Epi 1mg!'}
4. 💊 **Amiodarone 300mg** (refractory VF/pVT)
5. 🔍 Rhythm check at 2 min"""
        else:
            next_steps = f"""1. ⚡ **SHOCK #{shock_num}**
2. 💪 Resume CPR immediately
3. Continue Epi q3-5min
4. {'Amio 150mg if still refractory' if amio_doses == 1 else 'Consider causes'}
5. 🔍 **Check H's and T's**"""
        
        return f"""
⚡ [{event.format_run_time()}] **{rhythm}** - SHOCKABLE RHYTHM

**ACLS 2025 VF/pVT Protocol:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{next_steps}

**CPR Quality:** 100-120/min, >2 inches, full recoil
🔊 Say "Shock delivered" after defibrillation
"""

    def _format_non_shockable_rhythm(self, event: CodeEvent, rhythm: str) -> str:
        epi_doses = len(self.session.epi_doses)
        has_access = self.session.iv_access or self.session.io_access
        
        if epi_doses == 0:
            epi_prompt = "💉 **Epi 1mg IV/IO IMMEDIATELY!**" if has_access else "💉 **Get IV/IO → Epi 1mg ASAP!**"
        else:
            epi_prompt = "💉 Continue Epi 1mg q3-5min"
        
        return f"""
🚫 [{event.format_run_time()}] **{rhythm}** - NON-SHOCKABLE

**ACLS 2025 PEA/Asystole Protocol:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 💪 **High-quality CPR** (100-120/min, >2in)
2. {epi_prompt}
3. 🔍 **TREAT REVERSIBLE CAUSES!**

**5 H's:**
• Hypovolemia → Fluids
• Hypoxia → Airway/O2
• H+ (acidosis) → Ventilate
• Hypo/Hyperkalemia → Check ECG
• Hypothermia → Rewarm

**5 T's:**
• Tension pneumo → Decompress
• Tamponade → Pericardiocentesis
• Toxins → Antidotes
• Thrombosis (PE) → Lytics
• Thrombosis (MI) → PCI

🔊 Say "Epi given" or "Check H's and T's"
"""

    def _format_shock_delivered(self, event: CodeEvent, joules: int) -> str:
        shock_num = len(self.session.shocks)
        return f"""
⚡ [{event.format_run_time()}] **SHOCK #{shock_num} DELIVERED** - {joules}J

➡️ **RESUME CPR IMMEDIATELY!**

{self._get_post_shock_prompt(shock_num)}
"""

    def _get_post_shock_prompt(self, shock_num: int) -> str:
        prompts = ["💪 CPR x 2 minutes"]
        
        if self.session.is_epi_due():
            prompts.append("💉 Give Epi 1mg now!")
        
        if shock_num >= 2 and not self.session.amiodarone_doses:
            prompts.append("💊 Consider Amiodarone 300mg")
        
        return "\n".join(prompts)

    def _format_epi_given(self, event: CodeEvent, dose_num: int) -> str:
        return f"""
💉 [{event.format_run_time()}] **Epinephrine 1mg IV** (Dose #{dose_num})

⏱️ Next Epi due in 3-5 minutes
{self._get_next_prompt()}
"""

    def _format_rosc(self, event: CodeEvent) -> str:
        duration = event.run_time_seconds
        mins = duration // 60
        secs = duration % 60
        
        return f"""
🎉 [{event.format_run_time()}] **ROSC ACHIEVED!**

**Code Duration:** {mins} min {secs} sec
**Total Shocks:** {len(self.session.shocks)}
**Total Epi Doses:** {len(self.session.epi_doses)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

**POST-CARDIAC ARREST CARE:**

1. 🫁 **Airway** - Secure, confirm ETCO2
2. 🩸 **Circulation** - Target MAP ≥65, treat hypotension
3. 🧠 **Neuro** - Targeted temperature management?
4. ❤️ **Cardiac** - 12-lead ECG, cath lab if STEMI
5. 🔬 **Labs** - ABG, lactate, electrolytes

🔊 Say "Code ended" when documentation complete
"""

    def _format_code_end(self, event: CodeEvent, outcome: str) -> str:
        duration = event.run_time_seconds
        mins = duration // 60
        secs = duration % 60
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
**CODE BLUE ENDED** - {event.format_time()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Outcome:** {outcome}
**Duration:** {mins} min {secs} sec

**Summary:**
• CPR Cycles: {self.session.cpr_cycles}
• Shocks: {len(self.session.shocks)}
• Epi Doses: {len(self.session.epi_doses)}
• Amiodarone: {len(self.session.amiodarone_doses)} doses

📄 **Generating Code Blue Record...**

{self.generate_code_record()}
"""

    def _get_next_prompt(self) -> str:
        """Get contextual next-action prompt - ACLS 2025 compliant."""
        prompts = []
        s = self.session
        
        # === ACLS 2025 Drug Timing ===
        
        # Epinephrine timing depends on rhythm!
        if s.acls_path == ACLSPath.SHOCKABLE:
            # VF/pVT: Epi AFTER 2nd shock
            if len(s.epi_doses) == 0:
                if len(s.shocks) >= 2:
                    prompts.append("💉 **Give Epi 1mg NOW!** (After 2nd shock per ACLS)")
                # Don't prompt for Epi before 2nd shock in VF/pVT
            elif s.is_epi_due():
                epi_time = s.time_since_last_epi()
                prompts.append(f"💉 **Epi due!** (Last: {epi_time//60}m {epi_time%60}s ago)")
        else:
            # PEA/Asystole: Epi ASAP
            if len(s.epi_doses) == 0:
                if s.iv_access or s.io_access:
                    prompts.append("💉 **Give Epi 1mg ASAP!** (Non-shockable rhythm)")
            elif s.is_epi_due():
                epi_time = s.time_since_last_epi()
                prompts.append(f"💉 **Epi due!** (Last: {epi_time//60}m {epi_time%60}s ago)")
        
        # Amiodarone: After 3rd shock for refractory VF/pVT
        if s.acls_path == ACLSPath.SHOCKABLE:
            if len(s.shocks) >= 3 and not s.amiodarone_doses and not s.lidocaine_doses:
                prompts.append("💊 **Consider Amiodarone 300mg** (refractory VF/pVT)")
        
        # H's and T's reminder for non-shockable
        if s.acls_path == ACLSPath.NON_SHOCKABLE and not s.hs_ts_checked:
            prompts.append("🔍 **Check H's and T's!** (reversible causes)")
        
        # CPR quality - rhythm check due
        if s.is_rhythm_check_due():
            prompts.append("🔍 **2-min rhythm check due!**")
        
        # Compressor change reminder
        cpr_time = s.time_since_cpr_start()
        if cpr_time and cpr_time >= 110:  # 10 sec before 2 min
            prompts.append("🔄 **Switch compressor soon!** (q2min per ACLS)")
        
        # Access reminder
        if not s.iv_access and not s.io_access:
            prompts.append("💉 **Need IV/IO access for meds!**")
        
        # ETCO2 reminder if no values recorded
        if s.airway_type and not s.etco2_values:
            prompts.append("📊 **Confirm ETCO2** (waveform capnography)")
        
        return "\n".join(prompts) if prompts else ""
    
    def _extract_joules(self, text: str) -> Optional[int]:
        """Extract joules from text like '200 joules' or '360J'."""
        import re
        match = re.search(r'(\d+)\s*[jJ]', text)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_time(self, text: str) -> Optional[datetime]:
        """
        Extract manual timestamp from text.
        Supports: "23:04", "2304", "11:04 PM", "23:04:30"
        """
        import re
        
        # Pattern: HH:MM:SS or HH:MM
        match = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            second = int(match.group(3)) if match.group(3) else 0
            try:
                now = datetime.now()
                return now.replace(hour=hour, minute=minute, second=second, microsecond=0)
            except ValueError:
                pass
        
        # Pattern: HHMM (military time like "2304")
        match = re.search(r'\b(\d{2})(\d{2})\b', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                try:
                    now = datetime.now()
                    return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                except ValueError:
                    pass
        
        return None
    
    def add_event_with_time(self, event_type: str, details: str, manual_time: Optional[datetime] = None) -> CodeEvent:
        """Add event with optional manual timestamp."""
        timestamp = manual_time or datetime.now()
        
        # Calculate run time from code start
        run_time = int((timestamp - self.session.start_time).total_seconds())
        if run_time < 0:
            run_time = 0  # Don't go negative
        
        event = CodeEvent(
            timestamp=timestamp,
            event_type=event_type,
            details=details,
            run_time_seconds=run_time
        )
        self.session.events.append(event)
        return event
    
    def generate_code_record(self) -> str:
        """Generate formatted Code Blue documentation - ACLS 2025 compliant."""
        if not self.session:
            return "No active session"
        
        s = self.session
        duration = s.get_run_time()
        
        # Calculate ACLS compliance metrics
        epi_intervals = []
        for i in range(1, len(s.epi_doses)):
            interval = (s.epi_doses[i] - s.epi_doses[i-1]).total_seconds()
            epi_intervals.append(interval)
        avg_epi_interval = sum(epi_intervals) / len(epi_intervals) if epi_intervals else 0
        epi_compliant = all(180 <= i <= 300 for i in epi_intervals) if epi_intervals else True
        
        record = f"""
╔══════════════════════════════════════════════════════════════╗
║              CODE BLUE RECORD - ACLS 2025                    ║
╚══════════════════════════════════════════════════════════════╝

**Date:** {s.start_time.strftime("%Y-%m-%d")}
**Time Called:** {s.start_time.strftime("%H:%M:%S")}
**Time Ended:** {s.end_time.strftime("%H:%M:%S") if s.end_time else "Ongoing"}
**Duration:** {duration//60} min {duration%60} sec
**Outcome:** {s.outcome or "Ongoing"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**RHYTHM PROGRESSION:**
Initial: {s.events[0].details if s.events else "Unknown"}
Final: {s.current_rhythm.value}
ACLS Pathway: {s.acls_path.value if s.acls_path else "N/A"}
H's & T's Reviewed: {"Yes" if s.hs_ts_checked else "No"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**CPR:**
Cycles: {s.cpr_cycles}
Compressor Changes: {len(s.compressor_changes)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**DEFIBRILLATION:**
Total Shocks: {len(s.shocks)}
"""
        for i, (t, j) in enumerate(s.shocks, 1):
            record += f"  Shock {i}: {t.strftime('%H:%M:%S')} - {j}J\n"
        
        record += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**MEDICATIONS:**
Epinephrine 1mg x {len(s.epi_doses)} doses
"""
        for i, t in enumerate(s.epi_doses, 1):
            record += f"  Dose {i}: {t.strftime('%H:%M:%S')}\n"
        
        if s.amiodarone_doses:
            record += f"Amiodarone: {len(s.amiodarone_doses)} doses\n"
            for t, mg in s.amiodarone_doses:
                record += f"  {t.strftime('%H:%M:%S')} - {mg}mg\n"
        
        if s.other_meds:
            record += "Other Medications:\n"
            for t, med, dose in s.other_meds:
                record += f"  {t.strftime('%H:%M:%S')} - {med} {dose}\n"
        
        record += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**AIRWAY:**
Type: {s.airway_type or "BVM"}
Time Secured: {s.airway_time.strftime('%H:%M:%S') if s.airway_time else "N/A"}

**ACCESS:**
IV: {"Yes" if s.iv_access else "No"}
IO: {"Yes" if s.io_access else "No"}
Time: {s.access_time.strftime('%H:%M:%S') if s.access_time else "N/A"}

**ETCO2 MONITORING:**
"""
        if s.etco2_values:
            for t, val in s.etco2_values:
                record += f"  {t.strftime('%H:%M:%S')} - {val} mmHg\n"
        else:
            record += "  Not recorded\n"

        record += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**EVENT LOG:**
"""
        record += "| Time | Run | Event | Details |\n"
        record += "|------|-----|-------|--------|\n"
        for e in s.events:
            record += f"| {e.format_time()} | {e.format_run_time()} | {e.event_type} | {e.details} |\n"
        
        record += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recorder: NurseGemma AI
Verified by: _______________________
"""
        return record

    def get_status(self) -> str:
        """Get current code status summary."""
        if not self.session:
            return "No active code"
        
        s = self.session
        run_time = s.get_run_time()
        
        status = f"""
**⏱️ Run Time:** {run_time//60}:{run_time%60:02d}
**💓 Rhythm:** {s.current_rhythm.value}
**💪 CPR Cycles:** {s.cpr_cycles}
**⚡ Shocks:** {len(s.shocks)}
**💉 Epi Doses:** {len(s.epi_doses)}
"""
        
        if s.is_epi_due():
            elapsed = s.time_since_last_epi()
            if elapsed:
                status += f"\n⚠️ **Epi due!** ({elapsed//60}m {elapsed%60}s since last)"
            else:
                status += "\n⚠️ **No Epi given yet!**"
        
        if s.is_rhythm_check_due():
            status += "\n🔍 **Rhythm check due!**"
        
        return status


# Export for use in main app
code_blue_agent = CodeBlueAgent()
