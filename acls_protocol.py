"""
ACLS 2025 Protocol Reference
American Heart Association Guidelines

Used by Code Blue Agent for compliant cardiac arrest management.
"""

# =============================================================================
# ACLS 2025 DRUG DOSING
# =============================================================================

DRUGS = {
    "epinephrine": {
        "dose": "1 mg",
        "route": "IV/IO",
        "interval": "3-5 minutes",
        "interval_sec": 180,  # 3 min minimum
        "max_interval_sec": 300,  # 5 min maximum
        "notes": "Give ASAP for non-shockable, after 2nd shock for VF/pVT"
    },
    "amiodarone": {
        "first_dose": "300 mg",
        "second_dose": "150 mg",
        "route": "IV/IO bolus",
        "indication": "Refractory VF/pVT (after 3rd shock)",
        "notes": "Alternative to lidocaine"
    },
    "lidocaine": {
        "first_dose": "1-1.5 mg/kg",
        "second_dose": "0.5-0.75 mg/kg",
        "route": "IV/IO",
        "indication": "Alternative to amiodarone for refractory VF/pVT",
        "notes": "Can repeat q5-10min, max 3mg/kg"
    },
    "magnesium": {
        "dose": "1-2 g",
        "route": "IV/IO",
        "indication": "Torsades de pointes, hypomagnesemia",
        "notes": "Dilute in 10mL D5W, give over 5-20min"
    },
    "sodium_bicarbonate": {
        "dose": "1 mEq/kg",
        "route": "IV",
        "indication": "Known pre-existing hyperkalemia, bicarbonate-responsive acidosis, TCA overdose",
        "notes": "Not routine - specific indications only"
    },
    "calcium_chloride": {
        "dose": "1-2 g (10-20 mL of 10%)",
        "route": "IV",
        "indication": "Hyperkalemia, hypocalcemia, calcium channel blocker OD",
        "notes": "Give slow IV push"
    },
    "calcium_gluconate": {
        "dose": "3 g (30 mL of 10%)",
        "route": "IV",
        "indication": "Same as calcium chloride (less tissue necrosis risk)",
        "notes": "Preferred in peripheral IV"
    }
}

# =============================================================================
# DEFIBRILLATION ENERGY
# =============================================================================

DEFIB = {
    "biphasic": {
        "initial": "120-200 J (per manufacturer)",
        "subsequent": "Same or higher",
        "unknown": "Maximum available",
        "notes": "Single shock approach, immediate CPR after"
    },
    "monophasic": {
        "all_shocks": "360 J",
        "notes": "Same energy for all shocks"
    }
}

# =============================================================================
# HIGH-QUALITY CPR METRICS (2025)
# =============================================================================

CPR_QUALITY = {
    "rate": {
        "min": 100,
        "max": 120,
        "unit": "compressions/min"
    },
    "depth": {
        "adult_min": 2.0,  # inches
        "adult_max": 2.4,  # inches
        "child": "1/3 AP diameter",
        "unit": "inches"
    },
    "recoil": "Full chest recoil between compressions",
    "fraction": {
        "target": ">80%",
        "notes": "Minimize interruptions"
    },
    "compressor_change": {
        "interval": 120,  # seconds
        "notes": "Every 2 minutes or sooner if fatigued"
    },
    "ventilation": {
        "no_airway": "30:2 compression:ventilation ratio",
        "advanced_airway": "1 breath every 6 seconds (10/min)",
        "avoid": "Excessive ventilation"
    },
    "capnography": {
        "target": "ETCO2 ≥10 mmHg indicates adequate CPR",
        "rosc_indicator": "Abrupt sustained ETCO2 ≥40 mmHg"
    }
}

# =============================================================================
# REVERSIBLE CAUSES (H's and T's)
# =============================================================================

REVERSIBLE_CAUSES = {
    "Hs": {
        "Hypovolemia": {
            "signs": ["Flat neck veins", "Narrow QRS", "Rapid HR before arrest"],
            "treatment": "Volume resuscitation, blood products if bleeding"
        },
        "Hypoxia": {
            "signs": ["Cyanosis", "Low SpO2", "Airway obstruction"],
            "treatment": "Ensure airway, 100% O2, ventilate"
        },
        "Hydrogen ion (Acidosis)": {
            "signs": ["Known DKA", "Renal failure", "Prolonged arrest"],
            "treatment": "Ventilation, consider bicarb if severe"
        },
        "Hypokalemia": {
            "signs": ["Flat T waves", "U waves", "Prolonged QT"],
            "treatment": "IV potassium (10-20 mEq over 1 hour)"
        },
        "Hyperkalemia": {
            "signs": ["Peaked T waves", "Wide QRS", "Sine wave"],
            "treatment": "Calcium, insulin/glucose, bicarb, dialysis"
        },
        "Hypothermia": {
            "signs": ["Environmental exposure", "Core temp <30°C"],
            "treatment": "Active rewarming, may need prolonged CPR"
        }
    },
    "Ts": {
        "Tension pneumothorax": {
            "signs": ["Absent breath sounds", "Tracheal deviation", "JVD"],
            "treatment": "Needle decompression, chest tube"
        },
        "Tamponade (cardiac)": {
            "signs": ["JVD", "Muffled heart sounds", "Narrow pulse pressure"],
            "treatment": "Pericardiocentesis"
        },
        "Toxins": {
            "signs": ["Known ingestion", "Toxidrome", "Pill bottles"],
            "treatment": "Specific antidotes, supportive care"
        },
        "Thrombosis (pulmonary)": {
            "signs": ["Known DVT", "Recent surgery", "Pregnancy"],
            "treatment": "Consider thrombolytics, ECMO"
        },
        "Thrombosis (coronary)": {
            "signs": ["Chest pain pre-arrest", "STEMI on monitor"],
            "treatment": "PCI, thrombolytics if no PCI available"
        }
    }
}

# =============================================================================
# VF/pVT ALGORITHM (Shockable)
# =============================================================================

VF_PVT_ALGORITHM = """
VF/pVT (SHOCKABLE RHYTHM) - ACLS 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ SHOCK immediately (120-200J biphasic)
   └─ Resume CPR immediately after shock

2️⃣ CPR x 2 minutes
   └─ IV/IO access
   └─ Consider advanced airway

3️⃣ RHYTHM CHECK
   ├─ Still VF/pVT? → SHOCK #2
   └─ Resume CPR immediately

4️⃣ CPR x 2 minutes  
   └─ EPINEPHRINE 1mg IV/IO (then q3-5min)

5️⃣ RHYTHM CHECK
   ├─ Still VF/pVT? → SHOCK #3
   └─ Resume CPR immediately

6️⃣ CPR x 2 minutes
   └─ AMIODARONE 300mg IV/IO (or Lidocaine 1-1.5mg/kg)

7️⃣ Continue cycle:
   └─ Rhythm check → Shock if VF/pVT → CPR 2min
   └─ Epi q3-5min
   └─ Amiodarone 150mg after 5th shock (if not already given)
   └─ Treat reversible causes (H's and T's)
"""

PEA_ASYSTOLE_ALGORITHM = """
PEA/ASYSTOLE (NON-SHOCKABLE) - ACLS 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ CPR immediately
   └─ IV/IO access
   └─ EPINEPHRINE 1mg IV/IO ASAP

2️⃣ CPR x 2 minutes
   └─ Consider advanced airway
   └─ Waveform capnography

3️⃣ RHYTHM CHECK
   ├─ Shockable? → Go to VF/pVT algorithm
   └─ Still non-shockable? → Continue CPR

4️⃣ CPR x 2 minutes
   └─ EPINEPHRINE 1mg q3-5min
   └─ TREAT REVERSIBLE CAUSES

5️⃣ Continue cycle:
   └─ CPR 2min → Rhythm check → Epi q3-5min
   └─ Aggressively search for H's and T's
   └─ Consider termination criteria
"""

# =============================================================================
# ROSC INDICATORS
# =============================================================================

ROSC_SIGNS = {
    "definitive": [
        "Palpable pulse",
        "Measurable blood pressure",
        "Arterial waveform on invasive monitoring"
    ],
    "supportive": [
        "Abrupt sustained ETCO2 ≥40 mmHg",
        "Spontaneous movement",
        "Reactive pupils",
        "Improving skin color"
    ]
}

# =============================================================================
# POST-CARDIAC ARREST CARE
# =============================================================================

POST_ARREST_CARE = {
    "immediate": [
        "Optimize ventilation/oxygenation (SpO2 92-98%)",
        "IV fluids/vasopressors for MAP ≥65 mmHg",
        "12-lead ECG - consider emergent PCI if STEMI"
    ],
    "targeted_temperature": {
        "indication": "Comatose patients after ROSC",
        "target": "32-36°C for ≥24 hours",
        "avoid": "Fever (temp >37.7°C)"
    },
    "neuro": [
        "Avoid hypotension (SBP <90)",
        "Avoid hypoxia (SpO2 <94%)",
        "Consider neuroprognostication at 72+ hours"
    ],
    "labs": [
        "ABG/VBG",
        "Lactate",
        "Electrolytes (especially K+)",
        "Troponin",
        "CBC, BMP, coags"
    ]
}

# =============================================================================
# TIMING HELPERS
# =============================================================================

def get_epi_timing_advice(rhythm: str, shocks_given: int, epi_doses: int) -> str:
    """Get ACLS-compliant epinephrine timing advice."""
    
    if rhythm in ["VF", "VT", "pVT"]:
        # Shockable rhythm
        if epi_doses == 0:
            if shocks_given >= 2:
                return "⚠️ Give Epi NOW (after 2nd shock per ACLS)"
            else:
                return f"Epi after 2nd shock (shocks given: {shocks_given})"
        else:
            return "Continue Epi q3-5min"
    else:
        # Non-shockable (PEA/Asystole)
        if epi_doses == 0:
            return "⚠️ Give Epi ASAP (non-shockable rhythm)"
        else:
            return "Continue Epi q3-5min"


def get_antiarrhythmic_advice(shocks_given: int, amio_doses: int, lido_doses: int) -> str:
    """Get ACLS-compliant antiarrhythmic advice for refractory VF/pVT."""
    
    if shocks_given < 3:
        return f"Amiodarone after 3rd shock (shocks: {shocks_given})"
    
    if amio_doses == 0 and lido_doses == 0:
        return "⚠️ Consider Amiodarone 300mg or Lidocaine 1-1.5mg/kg"
    elif amio_doses == 1:
        return "Consider Amiodarone 150mg (2nd dose) if still refractory"
    elif amio_doses >= 2:
        return "Max amiodarone given. Consider Lidocaine if not used."
    
    return "Antiarrhythmic given - continue ACLS"


def format_hs_ts_checklist() -> str:
    """Format the H's and T's for quick reference."""
    
    checklist = """
🔍 REVERSIBLE CAUSES - Check Now!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
    return checklist
