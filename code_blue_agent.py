"""
NurseGemma Code Blue Agent
Real-time voice-activated cardiac arrest documentation with ACLS algorithm

Voice commands → Auto-timestamped events → ACLS-guided prompts → Code Blue Record

"CPR started" → timestamp
"Pulse check, no pulse" → timestamp, rhythm prompt
"Epi given" → timestamp, dose logged, next dose timer
"Shock given" → timestamp, joules logged
"ROSC" → timestamp, post-arrest care prompts
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


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
    """Active code blue documentation session."""
    
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
    
    # Medication tracking
    epi_doses: List[datetime] = field(default_factory=list)
    amiodarone_doses: List[tuple] = field(default_factory=list)  # (time, mg)
    lidocaine_doses: List[tuple] = field(default_factory=list)
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
        "amiodarone": "amio_given",
        "amio given": "amio_given",
        "300 of amio": "amio_300",
        "150 of amio": "amio_150",
        "lidocaine": "lido_given",
        "lido given": "lido_given",
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
        "time of death": "time_of_death",
        "code ended": "code_end",
        "stop code": "code_end",
    }
    
    def __init__(self):
        self.session: Optional[CodeBlueSession] = None
        
    def start_code(self) -> str:
        """Initialize new code blue session."""
        self.session = CodeBlueSession()
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
                return self.start_code()
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
        
        # === CPR ===
        if action == "start_cpr":
            self.session.last_cpr_start = datetime.now()
            self.session.cpr_cycles += 1
            event = self.session.add_event("CPR_START", f"Cycle {self.session.cpr_cycles}")
            return self._format_cpr_start(event)
        
        if action == "switch_compressor":
            self.session.compressor_changes.append(datetime.now())
            event = self.session.add_event("COMPRESSOR_SWITCH", "")
            return f"🔄 [{event.format_run_time()}] **Compressor switched** - Good teamwork!"
        
        # === Rhythm ===
        if action == "pulse_check" or action == "rhythm_check":
            event = self.session.add_event("RHYTHM_CHECK", "")
            return self._format_rhythm_check(event)
        
        if action == "rhythm_vf":
            self.session.current_rhythm = Rhythm.VF
            self.session.acls_path = ACLSPath.SHOCKABLE
            event = self.session.add_event("RHYTHM", "VF identified")
            return self._format_shockable_rhythm(event, "V-FIB")
        
        if action == "rhythm_vt":
            self.session.current_rhythm = Rhythm.VT
            self.session.acls_path = ACLSPath.SHOCKABLE
            event = self.session.add_event("RHYTHM", "Pulseless VT identified")
            return self._format_shockable_rhythm(event, "Pulseless V-TACH")
        
        if action == "rhythm_pea":
            self.session.current_rhythm = Rhythm.PEA
            self.session.acls_path = ACLSPath.NON_SHOCKABLE
            event = self.session.add_event("RHYTHM", "PEA identified")
            return self._format_non_shockable_rhythm(event, "PEA")
        
        if action == "rhythm_asystole":
            self.session.current_rhythm = Rhythm.ASYSTOLE
            self.session.acls_path = ACLSPath.NON_SHOCKABLE
            event = self.session.add_event("RHYTHM", "Asystole")
            return self._format_non_shockable_rhythm(event, "ASYSTOLE")
        
        if action == "no_pulse":
            event = self.session.add_event("PULSE_CHECK", "No pulse")
            return f"❌ [{event.format_run_time()}] **No pulse** - Continue CPR\n\n{self._get_next_prompt()}"
        
        # === ROSC ===
        if action == "rosc" or action == "pulse_present":
            self.session.current_rhythm = Rhythm.ROSC
            self.session.outcome = "ROSC"
            event = self.session.add_event("ROSC", "Return of spontaneous circulation")
            return self._format_rosc(event)
        
        # === Defibrillation ===
        if action == "shock_advised":
            event = self.session.add_event("DEFIB", "Shock advised")
            return f"⚡ [{event.format_run_time()}] **Shock advised** - Charging...\n🔊 Say 'Clear' then 'Shock delivered'"
        
        if action == "clear":
            event = self.session.add_event("DEFIB", "Clear called")
            return f"⚠️ [{event.format_run_time()}] **CLEAR!** - Deliver shock"
        
        if action == "shock_delivered":
            joules = self._extract_joules(original_text) or 200
            self.session.shocks.append((datetime.now(), joules))
            event = self.session.add_event("SHOCK", f"{joules}J delivered")
            return self._format_shock_delivered(event, joules)
        
        if action == "no_shock_advised":
            event = self.session.add_event("DEFIB", "No shock advised")
            return f"🚫 [{event.format_run_time()}] **No shock advised** - Non-shockable rhythm\n\n➡️ Continue CPR, give Epi ASAP"
        
        # === Medications ===
        if action == "epi_given":
            self.session.epi_doses.append(datetime.now())
            dose_num = len(self.session.epi_doses)
            event = self.session.add_event("MED", f"Epinephrine 1mg IV (dose #{dose_num})")
            return self._format_epi_given(event, dose_num)
        
        if action == "amio_given" or action == "amio_300":
            mg = 300 if not self.session.amiodarone_doses else 150
            self.session.amiodarone_doses.append((datetime.now(), mg))
            event = self.session.add_event("MED", f"Amiodarone {mg}mg IV")
            return f"💊 [{event.format_run_time()}] **Amiodarone {mg}mg** given\n\n{'➡️ Second dose: 150mg if needed' if mg == 300 else ''}"
        
        if action == "amio_150":
            self.session.amiodarone_doses.append((datetime.now(), 150))
            event = self.session.add_event("MED", "Amiodarone 150mg IV")
            return f"💊 [{event.format_run_time()}] **Amiodarone 150mg** given"
        
        if action == "bicarb_given":
            self.session.other_meds.append((datetime.now(), "Sodium Bicarbonate", "50mEq"))
            event = self.session.add_event("MED", "Sodium Bicarbonate 50mEq IV")
            return f"💊 [{event.format_run_time()}] **Bicarb 50mEq** given"
        
        if action == "calcium_given":
            self.session.other_meds.append((datetime.now(), "Calcium Chloride", "1g"))
            event = self.session.add_event("MED", "Calcium Chloride 1g IV")
            return f"💊 [{event.format_run_time()}] **Calcium 1g** given"
        
        if action == "mag_given":
            self.session.other_meds.append((datetime.now(), "Magnesium Sulfate", "2g"))
            event = self.session.add_event("MED", "Magnesium Sulfate 2g IV")
            return f"💊 [{event.format_run_time()}] **Mag 2g** given (Torsades protocol)"
        
        # === Airway ===
        if action == "intubated":
            self.session.airway_type = "ETT"
            self.session.airway_time = datetime.now()
            event = self.session.add_event("AIRWAY", "ET tube placed")
            return f"🫁 [{event.format_run_time()}] **Intubated** - Confirm with waveform capnography\n\n➡️ Continuous compressions, 1 breath q6 sec"
        
        if action == "lma_placed":
            self.session.airway_type = "LMA"
            self.session.airway_time = datetime.now()
            event = self.session.add_event("AIRWAY", "Supraglottic airway placed")
            return f"🫁 [{event.format_run_time()}] **LMA placed** - Confirm placement\n\n➡️ Continuous compressions, 1 breath q6 sec"
        
        # === Access ===
        if action == "iv_access":
            self.session.iv_access = True
            self.session.access_time = datetime.now()
            event = self.session.add_event("ACCESS", "IV access established")
            return f"💉 [{event.format_run_time()}] **IV access** established\n\n{'➡️ Give Epinephrine 1mg now!' if self.session.is_epi_due() else ''}"
        
        if action == "io_access":
            self.session.io_access = True
            self.session.access_time = datetime.now()
            event = self.session.add_event("ACCESS", "IO access established")
            return f"🦴 [{event.format_run_time()}] **IO access** established\n\n{'➡️ Give Epinephrine 1mg now!' if self.session.is_epi_due() else ''}"
        
        # === Code End ===
        if action == "time_of_death":
            self.session.end_time = datetime.now()
            self.session.outcome = "Expired"
            event = self.session.add_event("CODE_END", "Time of death called")
            return self._format_code_end(event, "Expired")
        
        if action == "code_end":
            self.session.end_time = datetime.now()
            if not self.session.outcome:
                self.session.outcome = "Ended"
            event = self.session.add_event("CODE_END", "Code concluded")
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
        return f"""
⚡ [{event.format_run_time()}] **{rhythm}** - SHOCKABLE RHYTHM

**ACLS VF/pVT Protocol:**
━━━━━━━━━━━━━━━━━━━━━━━

1. ⚡ **SHOCK** (200J biphasic) - Shock #{shock_num}
2. 💪 Resume CPR immediately x 2 min
3. 💉 Epi 1mg q3-5min
4. 💊 Amiodarone 300mg after 2nd shock

🔊 Say "Shock delivered" after defibrillation
"""

    def _format_non_shockable_rhythm(self, event: CodeEvent, rhythm: str) -> str:
        return f"""
🚫 [{event.format_run_time()}] **{rhythm}** - NON-SHOCKABLE

**ACLS PEA/Asystole Protocol:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 💪 Continue high-quality CPR
2. 💉 **Epi 1mg IV NOW** (then q3-5min)
3. 🔍 Treat reversible causes (H's & T's)

**5 H's:** Hypovolemia, Hypoxia, H+ (acidosis), Hypo/Hyperkalemia, Hypothermia
**5 T's:** Tension pneumo, Tamponade, Toxins, Thrombosis (PE), Thrombosis (MI)

🔊 Say "Epi given" when administered
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
        """Get contextual next-action prompt."""
        prompts = []
        
        # Check if epi is due
        if self.session.is_epi_due():
            epi_time = self.session.time_since_last_epi()
            if epi_time:
                prompts.append(f"💉 **Epi due!** (Last: {epi_time//60}m {epi_time%60}s ago)")
            elif self.session.iv_access or self.session.io_access:
                prompts.append("💉 **Give Epi 1mg!** (Access established)")
        
        # Check if rhythm check due
        if self.session.is_rhythm_check_due():
            prompts.append("🔍 **2-min rhythm check due!**")
        
        # Shockable rhythm reminders
        if self.session.acls_path == ACLSPath.SHOCKABLE:
            if len(self.session.shocks) >= 2 and not self.session.amiodarone_doses:
                prompts.append("💊 Consider **Amiodarone 300mg**")
        
        # Access reminder
        if not self.session.iv_access and not self.session.io_access:
            prompts.append("💉 Need IV/IO access for meds!")
        
        return "\n".join(prompts) if prompts else ""
    
    def _extract_joules(self, text: str) -> Optional[int]:
        """Extract joules from text like '200 joules' or '360J'."""
        import re
        match = re.search(r'(\d+)\s*[jJ]', text)
        if match:
            return int(match.group(1))
        return None
    
    def generate_code_record(self) -> str:
        """Generate formatted Code Blue documentation."""
        if not self.session:
            return "No active session"
        
        s = self.session
        duration = s.get_run_time()
        
        record = f"""
╔══════════════════════════════════════════════════════════════╗
║                    CODE BLUE RECORD                          ║
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
