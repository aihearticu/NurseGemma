"""
Sample Patient Data for NurseGemma
Realistic patient scenarios for demonstration and testing.

These patients represent common nursing scenarios:
1. Mrs. Johnson - CHF exacerbation with electrolyte concerns
2. Mr. Smith - Pneumonia Day 3, improving
3. Ms. Rodriguez - New DKA, insulin management
4. Mr. Chen - Post-op hip, pain management

All data is fictional and for educational purposes only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta


@dataclass
class VitalSigns:
    """Vital sign readings"""
    time: str
    bp_systolic: int
    bp_diastolic: int
    heart_rate: int
    respiratory_rate: int
    temperature: float
    o2_sat: int
    o2_device: str = "RA"
    pain: Optional[int] = None


@dataclass
class LabValue:
    """Individual lab value"""
    name: str
    value: float
    unit: str
    normal_low: float
    normal_high: float
    collected_time: str

    @property
    def status(self) -> str:
        if self.value < self.normal_low:
            return "L"
        elif self.value > self.normal_high:
            return "H"
        return ""


@dataclass
class Medication:
    """Medication entry for MAR"""
    name: str
    dose: str
    route: str
    frequency: str
    scheduled_times: List[str]
    given_times: Dict[str, bool]  # time -> given (True/False)
    high_alert: bool = False
    notes: str = ""


@dataclass
class SamplePatient:
    """Complete sample patient for demo"""
    # Demographics
    name: str
    age: int
    sex: str
    room: str
    mrn: str
    admission_date: str
    attending_md: str
    specialty: str

    # Clinical
    chief_complaint: str
    diagnosis: str
    history: List[str]
    allergies: List[str]

    # Current data
    vitals: List[VitalSigns]
    labs: List[LabValue]
    medications: List[Medication]
    nursing_notes: List[str]

    # Pending
    pending_orders: List[str]
    pending_consults: List[str]

    # MD Progress Note (optional - for highlight-to-explain feature)
    md_progress_note: str = ""

    # Property aliases for compatibility
    @property
    def diagnoses(self) -> List[str]:
        """Alias for diagnosis as list"""
        return [self.diagnosis] if self.diagnosis else []

    @property
    def attending(self) -> str:
        """Alias for attending_md"""
        return self.attending_md

    def get_mar_display(self) -> str:
        """Generate MAR display string"""
        lines = [
            "MEDICATION ADMINISTRATION RECORD",
            "=" * 60,
        ]

        for med in self.medications:
            alert = " HIGH-ALERT" if med.high_alert else ""
            times = "  ".join([
                f"{t}: {'GIVEN' if med.given_times.get(t) else 'DUE'}"
                for t in med.scheduled_times
            ])
            lines.append(f"{'*' if med.high_alert else ' '} {med.name} {med.dose} {med.route} {med.frequency}")
            lines.append(f"   {times}")

        return "\n".join(lines)

    def get_labs_display(self) -> str:
        """Generate labs display string"""
        lines = [
            f"LABORATORY RESULTS - Collected {self.labs[0].collected_time if self.labs else 'N/A'}",
            "=" * 60,
            f"{'Test':<20} {'Result':<12} {'Reference':<20}",
            "-" * 60,
        ]

        for lab in self.labs:
            status = f" ({lab.status})" if lab.status else ""
            lines.append(
                f"{lab.name:<20} {lab.value}{lab.unit}{status:<12} {lab.normal_low}-{lab.normal_high} {lab.unit}"
            )

        return "\n".join(lines)

    def get_vitals_display(self) -> str:
        """Generate vitals display string"""
        lines = [
            "VITAL SIGNS FLOWSHEET",
            "=" * 60,
        ]

        header = f"{'Time':<8}"
        for vs in self.vitals:
            header += f"{vs.time:<10}"
        lines.append(header)
        lines.append("-" * 60)

        # BP
        bp_line = f"{'BP':<8}"
        for vs in self.vitals:
            bp_line += f"{vs.bp_systolic}/{vs.bp_diastolic:<10}"
        lines.append(bp_line)

        # HR
        hr_line = f"{'HR':<8}"
        for vs in self.vitals:
            hr_line += f"{vs.heart_rate:<10}"
        lines.append(hr_line)

        # RR
        rr_line = f"{'RR':<8}"
        for vs in self.vitals:
            rr_line += f"{vs.respiratory_rate:<10}"
        lines.append(rr_line)

        # Temp
        temp_line = f"{'Temp':<8}"
        for vs in self.vitals:
            temp_line += f"{vs.temperature:<10}"
        lines.append(temp_line)

        # O2
        o2_line = f"{'SpO2':<8}"
        for vs in self.vitals:
            o2_line += f"{vs.o2_sat}% {vs.o2_device:<10}"
        lines.append(o2_line)

        return "\n".join(lines)

    def get_md_note_display(self) -> str:
        """Generate MD progress note display string"""
        if not self.md_progress_note:
            return "No MD progress note available."
        return self.md_progress_note.strip()

    def get_full_context(self) -> str:
        """Get full patient context for workflows"""
        md_note_section = ""
        if self.md_progress_note:
            md_note_section = f"""

MD PROGRESS NOTE:
{self.get_md_note_display()}
"""
        return f"""
PATIENT: {self.name} ({self.age}{self.sex})
ROOM: {self.room} | MRN: {self.mrn}
ATTENDING: Dr. {self.attending_md} ({self.specialty})
ADMITTED: {self.admission_date}

CHIEF COMPLAINT: {self.chief_complaint}
DIAGNOSIS: {self.diagnosis}

HISTORY: {', '.join(self.history)}
ALLERGIES: {', '.join(self.allergies) if self.allergies else 'NKDA'}

CURRENT VITALS:
{self.get_vitals_display()}

MEDICATIONS:
{self.get_mar_display()}

LABS:
{self.get_labs_display()}

NURSING NOTES:
{chr(10).join('- ' + note for note in self.nursing_notes)}

PENDING:
- Orders: {', '.join(self.pending_orders) if self.pending_orders else 'None'}
- Consults: {', '.join(self.pending_consults) if self.pending_consults else 'None'}
{md_note_section}"""


# ==================== SAMPLE PATIENTS ====================

MRS_JOHNSON = SamplePatient(
    # Demographics
    name="Mary Johnson",
    age=68,
    sex="F",
    room="412-1",
    mrn="12345678",
    admission_date="01/20/2026",
    attending_md="Smith, James",
    specialty="Cardiology",

    # Clinical
    chief_complaint="Shortness of breath x 3 days",
    diagnosis="Acute exacerbation of CHF",
    history=[
        "CHF (EF 35%)",
        "Hypertension",
        "Type 2 Diabetes",
        "CKD Stage 3",
        "A-fib on anticoagulation"
    ],
    allergies=["Penicillin (rash)", "Sulfa (hives)"],

    # Vitals - showing declining trend
    vitals=[
        VitalSigns("0400", 142, 88, 82, 18, 99.2, 94, "2L NC", 2),
        VitalSigns("0800", 138, 84, 78, 18, 98.8, 95, "2L NC", 1),
        VitalSigns("1200", 128, 76, 72, 20, 98.6, 94, "2L NC", 0),
        VitalSigns("1600", 92, 58, 52, 18, 98.4, 96, "2L NC", 0),
    ],

    # Labs - note low K+ with Lasix/Digoxin combo
    labs=[
        LabValue("Sodium", 138, " mEq/L", 136, 145, "0600"),
        LabValue("Potassium", 3.2, " mEq/L", 3.5, 5.0, "0600"),
        LabValue("Chloride", 102, " mEq/L", 98, 106, "0600"),
        LabValue("CO2", 24, " mEq/L", 22, 29, "0600"),
        LabValue("BUN", 28, " mg/dL", 7, 20, "0600"),
        LabValue("Creatinine", 1.4, " mg/dL", 0.6, 1.2, "0600"),
        LabValue("Glucose", 142, " mg/dL", 70, 100, "0600"),
        LabValue("BNP", 892, " pg/mL", 0, 100, "0600"),
        LabValue("Digoxin Level", 1.8, " ng/mL", 0.8, 2.0, "0600"),
    ],

    # Medications - high-alert combo
    medications=[
        Medication("METOPROLOL", "25mg", "PO", "BID",
                   ["0800", "2000"], {"0800": True, "2000": False}),
        Medication("LISINOPRIL", "10mg", "PO", "Daily",
                   ["0800"], {"0800": True}),
        Medication("FUROSEMIDE", "40mg", "IV", "Q12H",
                   ["0600", "1800"], {"0600": True, "1800": False},
                   notes="Monitor K+"),
        Medication("DIGOXIN", "0.125mg", "PO", "Daily",
                   ["0800"], {"0800": True}, high_alert=True,
                   notes="Hold if HR <60"),
        Medication("HEPARIN", "5000 units", "SC", "Q8H",
                   ["0600", "1400", "2200"], {"0600": True, "1400": False, "2200": False},
                   high_alert=True),
        Medication("METFORMIN", "500mg", "PO", "BID",
                   ["0800", "1800"], {"0800": True, "1800": False}),
        Medication("POTASSIUM CL", "20mEq", "PO", "PRN",
                   [], {}, high_alert=True, notes="For K+ <3.5"),
    ],

    # Notes - setup for demo scenarios
    nursing_notes=[
        "0700: Patient resting comfortably. Received report from night shift.",
        "0800: AM meds given. Patient tolerated breakfast 50%.",
        "1000: PT/OT evaluated patient. Ambulated 50 feet with walker, O2 sat dropped to 89% - returned to bed.",
        "1200: Lunch tolerated 75%. Patient's daughter asking about diagnosis.",
        "1400: Noted BP and HR dropping. Patient denies dizziness.",
        "1600: BP 92/58, HR 52. Hold parameters for Metoprolol are HR <60. K+ 3.2 this AM.",
    ],

    pending_orders=["Echo (scheduled tomorrow)", "Daily weights"],
    pending_consults=["Dietary consult", "Social work for discharge planning"],

    md_progress_note="""
PROGRESS NOTE - 01/21/2026 08:00
Provider: Dr. James Smith, MD - Cardiology

SUBJECTIVE:
68F with h/o CHFrEF (EF 35%), A-fib on anticoagulation, HTN, CKD3, T2DM admitted
for acute on chronic systolic CHF exacerbation. Patient reports improved dyspnea
at rest but continues with DOE. Denies orthopnea, PND, or chest pain. Diet compliance
questionable - admits to "salty foods" at granddaughter's birthday party last week.

OBJECTIVE:
Vitals: T 98.6, HR 72 (irregular), BP 128/76, RR 20, SpO2 94% on 2L NC
Gen: NAD, alert and oriented x3
CV: Irregularly irregular rhythm, no murmurs/rubs/gallops, JVD to angle of jaw
Pulm: Bibasilar crackles, L>R, no wheezes
Abd: Soft, NT/ND, BS+
Ext: 2+ pitting edema bilateral LE to mid-shin, improved from admission

Labs: BMP notable for K+ 3.2 (LOW), Cr 1.4 (baseline 1.2), BUN 28
BNP 892 (down from 1,245 on admission)
Digoxin level 1.8 (therapeutic range)

ASSESSMENT/PLAN:
1. Acute on chronic systolic heart failure - improving
   - Continue Lasix 40mg IV q12h, goal I/O negative 1-1.5L/day
   - Daily weights, low sodium diet
   - Monitor renal function and electrolytes

2. Hypokalemia - K+ 3.2, likely from diuresis
   - Replete with KCL 40mEq PO x1
   - Recheck BMP tomorrow
   - CAUTION: Patient on Digoxin - hypokalemia increases dig toxicity risk

3. Atrial fibrillation - rate controlled
   - Continue Metoprolol 25mg BID
   - Continue anticoagulation per outpatient regimen

4. CKD Stage 3 - Cr slightly elevated
   - Monitor with continued diuresis
   - Hold ACEi if Cr rises >30% from baseline

5. T2DM - continue home regimen
   - Hold Metformin if Cr worsens

Echo scheduled for tomorrow to reassess EF.
Anticipated discharge in 2-3 days if continues improving.

James Smith, MD
Cardiology Attending
""",
)


MR_SMITH = SamplePatient(
    # Demographics
    name="Robert Smith",
    age=72,
    sex="M",
    room="315-2",
    mrn="87654321",
    admission_date="01/18/2026",
    attending_md="Garcia, Maria",
    specialty="Pulmonology",

    # Clinical
    chief_complaint="Cough, fever, shortness of breath",
    diagnosis="Community-acquired pneumonia",
    history=[
        "COPD",
        "Former smoker (40 pack-years)",
        "Hypertension",
        "BPH"
    ],
    allergies=["NKDA"],

    # Vitals - improving trend
    vitals=[
        VitalSigns("0400", 138, 82, 88, 20, 99.2, 94, "2L NC"),
        VitalSigns("0800", 136, 80, 84, 20, 98.8, 95, "2L NC"),
        VitalSigns("1200", 132, 78, 80, 18, 98.4, 95, "2L NC"),
        VitalSigns("1600", 130, 76, 78, 18, 98.2, 96, "2L NC"),
    ],

    # Labs - improving
    labs=[
        LabValue("WBC", 11.2, " K/uL", 4.5, 11.0, "0600"),
        LabValue("Hemoglobin", 13.8, " g/dL", 13.5, 17.5, "0600"),
        LabValue("Platelets", 245, " K/uL", 150, 400, "0600"),
        LabValue("Sodium", 140, " mEq/L", 136, 145, "0600"),
        LabValue("Potassium", 4.2, " mEq/L", 3.5, 5.0, "0600"),
        LabValue("Creatinine", 1.0, " mg/dL", 0.6, 1.2, "0600"),
        LabValue("Procalcitonin", 0.8, " ng/mL", 0, 0.5, "0600"),
    ],

    # Medications
    medications=[
        Medication("CEFTRIAXONE", "1g", "IV", "Q24H",
                   ["0800"], {"0800": True},
                   notes="Day 3 of 5"),
        Medication("AZITHROMYCIN", "500mg", "PO", "Daily",
                   ["0800"], {"0800": True},
                   notes="Day 3 of 5"),
        Medication("ALBUTEROL", "2.5mg", "NEB", "Q4H PRN",
                   [], {}, notes="For SOB/wheezing"),
        Medication("LISINOPRIL", "20mg", "PO", "Daily",
                   ["0800"], {"0800": True}),
        Medication("TAMSULOSIN", "0.4mg", "PO", "Daily",
                   ["2000"], {"2000": False}),
        Medication("ACETAMINOPHEN", "650mg", "PO", "Q6H PRN",
                   [], {}, notes="For fever >100.4"),
    ],

    nursing_notes=[
        "0700: Patient reports feeling better than yesterday. Cough productive.",
        "0800: AM meds given. Breakfast 50% taken.",
        "1000: PT evaluated. Ambulated 100 feet, sats maintained on 2L NC.",
        "1200: Lunch 75%. Daughter visited, patient in good spirits.",
        "1400: Resting comfortably. WBC trending down from 14.6 to 11.2.",
        "1600: Team discussed possible step-down to room air tomorrow if continues improving.",
    ],

    pending_orders=["Repeat CXR tomorrow", "PT/OT daily"],
    pending_consults=["PT/OT for discharge readiness"],

    md_progress_note="""
PROGRESS NOTE - 01/21/2026 09:30
Provider: Dr. Maria Garcia, MD - Pulmonology

SUBJECTIVE:
72M with PMHx of COPD (FEV1 55% predicted), former smoker 40 pack-years, HTN, BPH
admitted with CAP. Day 3 of admission. Patient reports feeling "much better" -
cough still productive but less frequent. Able to ambulate to bathroom without
significant SOB. Good appetite returning. Denies fever, chills, rigors, hemoptysis.

OBJECTIVE:
Vitals: T 98.2 (Tmax 99.2), HR 78 reg, BP 130/76, RR 18, SpO2 95-96% on 2L NC
Gen: NAD, comfortable appearing, conversant in full sentences
HEENT: OP clear, MMM
Pulm: Rhonchi RLL, improved inspiratory crackles, good air movement bilaterally
CV: RRR, S1/S2 normal, no murmurs
Ext: No edema, cyanosis, or clubbing

CXR (01/18): RLL consolidation consistent with pneumonia, no effusion
Labs: WBC 11.2 (down from 14.6 on admit, 18.2 two days ago)
      Procalcitonin 0.8 (down from 2.1)
      BMP: wnl

ASSESSMENT/PLAN:
1. Community-acquired pneumonia, RLL - improving
   - Continue Ceftriaxone 1g IV daily + Azithromycin 500mg PO daily (Day 3 of 5)
   - Blood cultures NGTD at 48h - will finalize tomorrow
   - Repeat CXR tomorrow to assess resolution
   - Consider PO antibiotics for discharge if continues improving

2. COPD - stable, no acute exacerbation component
   - Continue home Spiriva
   - Albuterol nebs PRN, using infrequently
   - Smoking cessation discussed, patient receptive

3. Oxygen requirement - improving
   - Currently 2L NC
   - Goal: wean to RA by tomorrow if SpO2 maintained >92%
   - Desat to 89% noted with ambulation - expect improvement with pneumonia resolution

4. Disposition
   - PT/OT evaluated - recommends 1-2 more days for safe discharge
   - Discuss home health vs SNF if oxygen dependent at discharge
   - Anticipated discharge in 2-3 days

Maria Garcia, MD
Pulmonology Attending
""",
)


MS_RODRIGUEZ = SamplePatient(
    # Demographics
    name="Sofia Rodriguez",
    age=45,
    sex="F",
    room="ICU-4",
    mrn="11223344",
    admission_date="01/22/2026",
    attending_md="Patel, Raj",
    specialty="Endocrinology",

    # Clinical
    chief_complaint="Nausea, vomiting, abdominal pain",
    diagnosis="Diabetic Ketoacidosis (DKA)",
    history=[
        "Type 1 Diabetes (diagnosed age 12)",
        "Depression",
        "Non-compliant with insulin"
    ],
    allergies=["Latex"],

    # Vitals - critical scenario
    vitals=[
        VitalSigns("0400", 98, 58, 118, 28, 99.8, 98, "4L NC"),
        VitalSigns("0800", 102, 62, 110, 24, 99.2, 99, "2L NC"),
        VitalSigns("1200", 108, 66, 102, 22, 98.8, 99, "2L NC"),
        VitalSigns("1600", 112, 68, 98, 20, 98.6, 99, "RA"),
    ],

    # Labs - DKA panel
    labs=[
        LabValue("Glucose", 428, " mg/dL", 70, 100, "0600"),
        LabValue("Potassium", 5.8, " mEq/L", 3.5, 5.0, "0600"),
        LabValue("pH (VBG)", 7.18, "", 7.35, 7.45, "0600"),
        LabValue("HCO3", 12, " mEq/L", 22, 29, "0600"),
        LabValue("Anion Gap", 24, "", 3, 11, "0600"),
        LabValue("Beta-HB", 6.2, " mmol/L", 0, 0.6, "0600"),
        LabValue("Sodium", 132, " mEq/L", 136, 145, "0600"),
        LabValue("Creatinine", 1.6, " mg/dL", 0.6, 1.2, "0600"),
    ],

    # Medications - insulin drip
    medications=[
        Medication("INSULIN REGULAR", "0.1 units/kg/hr", "IV DRIP", "Continuous",
                   ["Continuous"], {"Continuous": True}, high_alert=True,
                   notes="Per DKA protocol - titrate to BG"),
        Medication("NORMAL SALINE", "500mL/hr", "IV", "Continuous",
                   ["Continuous"], {"Continuous": True},
                   notes="Fluid resuscitation"),
        Medication("POTASSIUM CL", "40mEq in NS", "IV", "PRN",
                   [], {}, high_alert=True,
                   notes="Give when K+ <5.0"),
        Medication("ONDANSETRON", "4mg", "IV", "Q6H PRN",
                   [], {}, notes="For nausea"),
    ],

    nursing_notes=[
        "0700: Received from ED. DKA protocol initiated. Insulin drip at 5 units/hr.",
        "0800: Q1H BG: 428 -> 382. Anion gap 24. Patient alert and oriented.",
        "1000: Q1H BG: 341. K+ rechecked - 5.2, down from 5.8. Continue monitoring.",
        "1200: Q1H BG: 298. Patient tolerating sips of water. Nausea improving.",
        "1400: Q1H BG: 246. Gap closing (18). May transition to subQ insulin soon.",
        "1600: Q1H BG: 198. Team discussing adding D5 to fluids and reducing drip.",
    ],

    pending_orders=["Q1H glucose checks", "BMP Q4H", "VBG Q4H"],
    pending_consults=["Diabetes educator", "Social work"],

    md_progress_note="""
PROGRESS NOTE - 01/22/2026 14:00
Provider: Dr. Raj Patel, MD - Endocrinology

SUBJECTIVE:
45F with T1DM x 33 years (diagnosed age 12), history of multiple DKA admissions,
presents with DKA likely precipitated by insulin non-compliance and possible
concurrent viral illness (reported URI symptoms 3 days prior). Patient admits to
running out of Lantus 5 days ago and "trying to get by" with Humalog alone.
Currently feels "better" - nausea resolved, abdominal pain improving.

OBJECTIVE:
Vitals: T 98.6, HR 98 (down from 118 on admit), BP 112/68, RR 20, SpO2 99% RA
Gen: Alert, oriented, mildly fatigued appearing, no Kussmaul respirations
HEENT: Dry mucous membranes improving, fruity breath odor resolved
CV: Tachycardic but improved, regular rhythm
Pulm: CTAB, no respiratory distress
Abd: Soft, mild diffuse tenderness improving, BS+

Labs trend (0600 -> 1400):
- Glucose: 428 -> 198 mg/dL
- pH: 7.18 -> 7.31 (VBG)
- HCO3: 12 -> 18 mEq/L
- Anion gap: 24 -> 14 (closing)
- Beta-hydroxybutyrate: 6.2 -> 1.8 mmol/L
- K+: 5.8 -> 4.2 mEq/L (now in target range)
- Na+: 132 -> 138 mEq/L (corrected: 140 -> 140)

ASSESSMENT/PLAN:
1. DKA - resolving
   - Anion gap closing (24 -> 14), pH improving
   - Continue insulin drip for now, transition to subQ when:
     * Anion gap < 12
     * pH > 7.30
     * Patient tolerating PO
   - Add D5 1/2NS when glucose < 200 to allow continued insulin infusion
   - WATCH: K+ will continue to drop as acidosis resolves - may need repletion

2. T1DM - poor control (last A1c 11.2%)
   - Diabetes educator to see today
   - Address medication access barriers - prior authorization issues identified
   - Social work consult for insulin assistance programs
   - Will restart Lantus + Humalog when transitioned off drip

3. Fluid/Electrolyte status
   - Initial 6L deficit, approximately 3L replaced
   - Continue NS at 250mL/hr, reassess at evening labs
   - K+ now 4.2 - hold potassium supplementation

4. AKI - resolving
   - Cr 1.6 on admission, likely prerenal from dehydration
   - Expect improvement with volume resuscitation

DISPOSITION:
ICU stay anticipated 24-48h more, then step down to medicine floor.
Strong emphasis on outpatient DM management and insulin adherence.

Raj Patel, MD
Endocrinology Attending
""",
)


MR_CHEN = SamplePatient(
    # Demographics
    name="William Chen",
    age=55,
    sex="M",
    room="Ortho-208",
    mrn="55667788",
    admission_date="01/21/2026",
    attending_md="Williams, Sarah",
    specialty="Orthopedics",

    # Clinical
    chief_complaint="Left hip pain after fall",
    diagnosis="Left hip fracture s/p ORIF POD#2",
    history=[
        "Hypertension",
        "Hyperlipidemia",
        "Osteoporosis"
    ],
    allergies=["Morphine (nausea)", "Codeine (severe nausea)"],

    # Vitals - stable post-op
    vitals=[
        VitalSigns("0400", 132, 78, 76, 16, 98.4, 97, "RA", 6),
        VitalSigns("0800", 128, 76, 72, 16, 98.2, 98, "RA", 4),
        VitalSigns("1200", 126, 74, 74, 16, 98.0, 98, "RA", 3),
        VitalSigns("1600", 124, 72, 70, 16, 98.2, 98, "RA", 5),
    ],

    # Labs
    labs=[
        LabValue("Hemoglobin", 9.8, " g/dL", 13.5, 17.5, "0600"),
        LabValue("Hematocrit", 29.4, " %", 38.5, 50.0, "0600"),
        LabValue("WBC", 12.8, " K/uL", 4.5, 11.0, "0600"),
        LabValue("Platelets", 178, " K/uL", 150, 400, "0600"),
        LabValue("Creatinine", 1.1, " mg/dL", 0.6, 1.2, "0600"),
        LabValue("INR", 1.0, "", 0.9, 1.1, "0600"),
    ],

    # Medications - pain management focus
    medications=[
        Medication("HYDROMORPHONE", "0.5mg", "IV", "Q3H PRN",
                   [], {}, high_alert=True,
                   notes="For severe pain (7-10)"),
        Medication("OXYCODONE", "5mg", "PO", "Q4H PRN",
                   [], {},
                   notes="For moderate pain (4-6)"),
        Medication("ACETAMINOPHEN", "1000mg", "PO", "Q6H",
                   ["0600", "1200", "1800", "0000"],
                   {"0600": True, "1200": True, "1800": False, "0000": False},
                   notes="Scheduled around the clock"),
        Medication("ENOXAPARIN", "40mg", "SC", "Daily",
                   ["2100"], {"2100": False}, high_alert=True,
                   notes="DVT prophylaxis - hold if signs of bleeding"),
        Medication("AMLODIPINE", "10mg", "PO", "Daily",
                   ["0800"], {"0800": True}),
        Medication("ATORVASTATIN", "20mg", "PO", "Daily",
                   ["2100"], {"2100": False}),
        Medication("DOCUSATE", "100mg", "PO", "BID",
                   ["0800", "2000"], {"0800": True, "2000": False},
                   notes="Bowel regimen - opioid use"),
        Medication("SENNA", "8.6mg", "PO", "Daily PRN",
                   [], {}, notes="For constipation"),
    ],

    nursing_notes=[
        "0700: Patient resting. Pain 4/10 at baseline. Incision C/D/I, dressing intact.",
        "0800: AM meds given. Assisted to chair. Tolerated 30 min sitting.",
        "1000: PT worked with patient. Partial weight bearing with walker. Fatigued after.",
        "1200: Lunch 100%. Pain increased to 6/10 with movement, given Oxycodone.",
        "1400: Resting, pain improved to 3/10. H&H checked - Hgb 9.8 (baseline post-op).",
        "1600: Pain increased to 5/10 with repositioning. Requesting pain med.",
    ],

    pending_orders=["CBC tomorrow", "Physical therapy daily", "Occupational therapy"],
    pending_consults=["Case management for SNF placement", "PT/OT daily"],

    md_progress_note="""
PROGRESS NOTE - 01/23/2026 07:30
Provider: Dr. Sarah Williams, MD - Orthopedic Surgery

SUBJECTIVE:
55M POD#2 s/p L hip ORIF for intertrochanteric femur fracture sustained after
mechanical fall at home (tripped over dog). Patient with h/o HTN, HLD, osteoporosis.
Rates pain 5/10 at rest, 7/10 with movement. Able to participate with PT yesterday.
Passed voiding trial. Tolerating regular diet. Denies numbness/tingling in LE, calf
pain, chest pain, or SOB. BM today with stool softeners.

ALLERGIES: Morphine (severe nausea), Codeine (nausea)
   - Using Hydromorphone IV PRN + Oxycodone PO for pain control

OBJECTIVE:
Vitals: T 98.2, HR 70, BP 124/72, RR 16, SpO2 98% RA
Gen: NAD, comfortable at rest
CV: RRR, no murmurs
Pulm: CTAB
Ext:
   - LLE: Surgical incision C/D/I, Steri-Strips intact, minimal ecchymosis
   - Mild swelling at surgical site
   - Sensation intact L1-S1 dermatomal distribution
   - DP/PT pulses 2+ bilaterally
   - Negative Homans sign bilaterally
   - No erythema, warmth, or calf tenderness (no DVT signs)

Labs: H&H 9.8/29.4 (down from 13.2/39.6 pre-op - expected post-op drop)
      WBC 12.8 (mild elevation post-op, no signs of infection)
      INR 1.0, appropriate for Lovenox

ASSESSMENT/PLAN:
1. L intertrochanteric femur fracture s/p ORIF - POD#2
   - Surgical site healing well, no signs of infection
   - Weight bearing as tolerated (WBAT) per protocol
   - Continue ice, elevation
   - PT/OT daily - goal independent transfers and ambulation with walker

2. Post-operative anemia
   - H&H 9.8/29.4 - expected surgical blood loss
   - Asymptomatic, no transfusion indicated
   - Recheck CBC tomorrow
   - Iron supplementation if doesn't improve

3. Pain management
   - Patient with morphine/codeine allergies - using alternatives
   - Current: Hydromorphone 0.5mg IV q3h PRN (for severe pain)
            Oxycodone 5mg PO q4h PRN (for moderate pain)
            Acetaminophen 1000mg PO q6h scheduled
   - Goal: transition to PO only by discharge
   - Bowel regimen: Docusate + Senna PRN

4. DVT prophylaxis
   - Enoxaparin 40mg SC daily
   - SCDs while in bed
   - Early mobilization

5. Osteoporosis
   - Will need DEXA scan as outpatient
   - Consider bisphosphonate therapy once healing complete
   - Vitamin D/Calcium supplementation

DISPOSITION:
PT eval today will determine discharge needs - likely SNF vs home with PT
depending on progress. Anticipated discharge POD#3-4.

Sarah Williams, MD
Orthopedic Surgery Attending
""",
)


# ==================== PATIENT DICTIONARY ====================

SAMPLE_PATIENTS = {
    "mrs_johnson": MRS_JOHNSON,
    "mr_smith": MR_SMITH,
    "ms_rodriguez": MS_RODRIGUEZ,
    "mr_chen": MR_CHEN,
}


def get_patient(name: str) -> Optional[SamplePatient]:
    """Get patient by name key"""
    return SAMPLE_PATIENTS.get(name.lower().replace(" ", "_"))


def list_patients() -> List[str]:
    """List available patient names"""
    return [
        f"{p.name} ({p.age}{p.sex}) - {p.diagnosis}"
        for p in SAMPLE_PATIENTS.values()
    ]


# ==================== DEMO SCENARIOS ====================

def get_demo_scenario(scenario: str) -> Dict:
    """Get demo scenario data"""
    scenarios = {
        "busy_morning": {
            "patient": MRS_JOHNSON,
            "situation": "Multiple patients, low K+ flagged on labs",
            "demo_action": "Paste lab values -> AI auto-analyzes",
            "expected_output": "Priority flagging of K+ with Lasix/Digoxin concern",
        },
        "worried_family": {
            "patient": MRS_JOHNSON,
            "situation": "Daughter asks 'What does CHF mean?'",
            "demo_action": "Generate 8th-grade explanation",
            "expected_output": "Plain language with heart pump analogy",
        },
        "critical_lab": {
            "patient": MS_RODRIGUEZ,
            "situation": "DKA with high K+ and low pH",
            "demo_action": "Critical lab response workflow",
            "expected_output": "Prioritized concerns with DKA management",
        },
        "shift_handoff": {
            "patient": MR_SMITH,
            "situation": "End of day shift, improving pneumonia",
            "demo_action": "Generate SBAR handoff",
            "expected_output": "Complete handoff with improving trend noted",
        },
        "pain_management": {
            "patient": MR_CHEN,
            "situation": "Post-op pain management, morphine allergy",
            "demo_action": "Medication safety check",
            "expected_output": "Allergy flagged, alternative opioids noted",
        },
    }
    return scenarios.get(scenario, {})


if __name__ == "__main__":
    print("=" * 60)
    print("NurseGemma Sample Patients")
    print("=" * 60)
    print()
    print("Available patients:")
    for name, patient in SAMPLE_PATIENTS.items():
        print(f"  - {name}: {patient.name} ({patient.age}{patient.sex}) - {patient.diagnosis}")
    print()
    print("Usage:")
    print("  from sample_patients import MRS_JOHNSON, get_patient")
    print("  patient = get_patient('mrs_johnson')")
    print("  print(patient.get_full_context())")
    print()
    print("Demo scenarios:")
    for scenario in ["busy_morning", "worried_family", "critical_lab", "shift_handoff", "pain_management"]:
        data = get_demo_scenario(scenario)
        if data:
            print(f"  - {scenario}: {data.get('situation', '')}")
