# NurseGemma Sample Outputs
## Demonstrating MedGemma AI Responses

This document shows realistic sample outputs from NurseGemma powered by MedGemma 1.5 4B, demonstrating each feature with a complete patient scenario.

---

## The Scenario: Mrs. Johnson's Busy Morning

**Patient:** Mary Johnson, 68F, Room 412-1
**Diagnosis:** Acute exacerbation of CHF
**Day:** Hospital Day 2, Day Shift (0700)

**Current Situation:**
- Morning labs just came back: K+ 3.2 (LOW)
- Patient on Digoxin 0.125mg daily and Lasix 40mg IV q12h
- BP trending down: 142/88 → 128/76 → 92/58
- HR dropped to 52
- Daughter arriving soon, wants to understand mom's condition
- Shift handoff needed at 1900

---

## Sample Output 1: Critical Lab Response Workflow

**Trigger:** Nurse clicks "Lab Response" button after morning labs posted

### MedGemma Output:

```
🚨 CRITICAL LAB ANALYSIS - Mrs. Johnson (68F, CHF)

═══════════════════════════════════════════════════════════════

PRIORITY: ⚠️ URGENT - Requires Immediate Attention

═══════════════════════════════════════════════════════════════

CRITICAL FINDINGS:

1. POTASSIUM: 3.2 mEq/L (LOW)
   Normal Range: 3.5-5.0 mEq/L

   ⚠️ CLINICAL CONCERN: Patient is on DIGOXIN
   - Hypokalemia increases digoxin toxicity risk
   - Current digoxin level: 1.8 ng/mL (high-therapeutic)
   - Risk of arrhythmias significantly elevated

   IMMEDIATE ACTIONS NEEDED:
   • Hold Digoxin until K+ repleted and rechecked
   • Notify MD for potassium replacement order
   • Monitor for signs of dig toxicity: N/V, visual changes, bradycardia
   • Continuous cardiac monitoring recommended

2. BUN/CREATININE: 28/1.4 (Elevated)
   - BUN elevated likely from CHF/prerenal state
   - Creatinine 1.4 (baseline 1.2) - mild AKI
   - Consider holding ACE inhibitor if continues to rise

3. BNP: 892 pg/mL (Elevated but improving)
   - Down from admission, suggests CHF treatment working
   - Continue current diuretic regimen

═══════════════════════════════════════════════════════════════

RECOMMENDED MD NOTIFICATION (SBAR Format):

"Dr. Smith, this is [Nurse] calling about Mrs. Johnson in 412-1.

SITUATION: Her morning potassium came back at 3.2, and she's on
Digoxin with a level of 1.8.

BACKGROUND: She was admitted for CHF exacerbation, currently on
Lasix 40mg IV q12h which is likely causing the hypokalemia.

ASSESSMENT: I'm concerned about increased digoxin toxicity risk
with this low potassium. Her HR is also down to 52.

RECOMMENDATION: I'd like to hold the Digoxin and get an order for
potassium replacement. Would you also like a repeat BMP after
repletion?"

═══════════════════════════════════════════════════════════════

⏱️ Time: 23 seconds | Manual estimate: 10 minutes | Saved: 9.6 min
```

---

## Sample Output 2: Patient Progress Course

**Trigger:** Nurse clicks "Progress Course" to understand patient's hospital trajectory

### MedGemma Output:

```
📋 PATIENT PROGRESS COURSE: Mary Johnson

═══════════════════════════════════════════════════════════════

HOSPITAL COURSE SUMMARY

ADMISSION (01/20/2026):
• 68-year-old female presented with 3 days of worsening dyspnea
• Found to have acute on chronic systolic CHF exacerbation
• Precipitating factor: Dietary indiscretion (high sodium intake
  at granddaughter's birthday party)
• Admission BNP: 1,245 pg/mL, 2+ bilateral LE edema to thighs
• Started on IV Lasix diuresis protocol

KEY EVENTS:
• Day 1: Aggressive diuresis initiated, 2.5L negative
• Day 2 (Today): BNP improved to 892, edema down to mid-shin
• Morning labs show K+ 3.2 (likely diuretic-induced)
• BP/HR trending down - may need to reassess beta-blocker dose

═══════════════════════════════════════════════════════════════

TREND ANALYSIS

VITALS TREND (Improving → Concerning):
• BP: 142/88 → 138/84 → 128/76 → 92/58 ⚠️ (dropping)
• HR: 82 → 78 → 72 → 52 ⚠️ (bradycardia developing)
• O2: Stable on 2L NC, sats 94-96%
• Weight: -2.3 kg from admission (good diuresis response)

LAB TRENDS:
• BNP: 1,245 → 892 ✓ (improving)
• K+: Dropped to 3.2 ⚠️ (needs repletion)
• Creatinine: 1.2 → 1.4 (mild bump, monitor)
• Digoxin level: 1.8 (therapeutic but HIGH with low K+)

═══════════════════════════════════════════════════════════════

RESPONSE TO TREATMENT

WORKING:
✓ Diuresis effective - negative fluid balance
✓ BNP trending down
✓ Edema improving
✓ Dyspnea at rest improved

CONCERNS:
⚠️ Hypokalemia from aggressive diuresis
⚠️ Hypotension developing (BP 92/58)
⚠️ Bradycardia (HR 52) - may need to hold Metoprolol
⚠️ Mild AKI - cardiorenal syndrome risk

═══════════════════════════════════════════════════════════════

ANTICIPATED COURSE

• Echo scheduled tomorrow to reassess EF
• Likely 2-3 more days if continues improving
• Will need to transition to PO Lasix before discharge
• Dietary education critical - sodium restriction
• May need medication adjustments based on BP/HR

WATCH FOR:
• Worsening renal function with continued diuresis
• Digoxin toxicity signs (bradycardia already present)
• Orthostatic hypotension as diuresis continues

═══════════════════════════════════════════════════════════════

⏱️ Time: 31 seconds | Manual estimate: 10 minutes | Saved: 9.5 min
```

---

## Sample Output 3: Shift Watch (Day Shift)

**Trigger:** Nurse clicks "Day Shift" under Shift Watch

### MedGemma Output:

```
👁️ WHAT TO WATCH THIS SHIFT: Mrs. Johnson
📅 DAY SHIFT | Room 412-1

═══════════════════════════════════════════════════════════════

🚨 RED FLAGS - CALL MD IMMEDIATELY IF:

• HR < 50 or > 110 (currently 52 - AT THRESHOLD)
• BP < 90 systolic (currently 92 - NEAR THRESHOLD)
• New chest pain or palpitations
• Visual disturbances, nausea, or confusion (dig toxicity)
• Urine output < 30 mL/hr x 2 hours
• Respiratory distress or O2 sat < 90%
• New onset irregular rhythm

═══════════════════════════════════════════════════════════════

⚠️ WATCH CLOSELY:

CARDIAC:
• BP trending down - get orthostatics before ambulation
• HR bradycardic - hold Metoprolol if HR < 60
• Telemetry for arrhythmias (dig toxicity risk with low K+)

ELECTROLYTES:
• K+ 3.2 - CRITICAL with Digoxin on board
• Expect potassium replacement order
• Recheck BMP after repletion (likely 4-6 hours)

FLUID STATUS:
• Daily weight (AM) - compare to yesterday
• I&O strict - goal negative 1-1.5L today
• Assess edema at end of shift
• Monitor for signs of over-diuresis

RENAL:
• Creatinine trending up (1.2 → 1.4)
• Hold ACEi if Cr rises > 30% from baseline

═══════════════════════════════════════════════════════════════

📋 SHIFT PRIORITIES:

1. HOLD DIGOXIN until K+ repleted and rechecked
   - Verify with MD before giving AM dose

2. NOTIFY MD about K+ 3.2 and request replacement
   - Use SBAR format (see Lab Response output)

3. GET ORTHOSTATIC VITALS before PT/OT arrives
   - BP 92/58 is concerning for ambulation

4. REASSESS METOPROLOL hold parameters
   - HR 52 may warrant holding PM dose

5. PATIENT/FAMILY EDUCATION
   - Daughter arriving - prepare CHF explanation
   - Dietary sodium teaching

═══════════════════════════════════════════════════════════════

💊 MEDICATION ALERTS:

DUE THIS SHIFT:
• 0800: Metoprolol 25mg PO - CHECK HR FIRST (hold if <60)
• 0800: Lisinopril 10mg PO - CHECK BP FIRST
• 0800: Digoxin 0.125mg PO - ⚠️ HOLD pending K+ repletion
• 1800: Furosemide 40mg IV - assess volume status first
• 1800: Metformin 500mg PO - hold if Cr continues rising

HIGH-ALERT MEDICATIONS:
⚠️ DIGOXIN - Hold until K+ > 3.5 and MD confirms
⚠️ HEPARIN 5000 units SC q8h - check for bleeding
⚠️ KCL when ordered - verify IV access, give slowly

PRN CONSIDERATIONS:
• Potassium repletion (anticipate order)
• Ondansetron if nausea (possible dig toxicity)

═══════════════════════════════════════════════════════════════

📝 DOCUMENTATION FOCUS:

• Telemetry rhythm q4h (watch for PVCs, bradycardia)
• Strict I&O with running totals
• Daily weight comparison
• Edema assessment (document improvement)
• Response to potassium repletion
• Hold medication documentation with rationale

═══════════════════════════════════════════════════════════════

👨‍👩‍👧 ANTICIPATED NEEDS:

EXPECTED ORDERS:
• Potassium replacement (PO or IV)
• Repeat BMP after repletion
• Possible Metoprolol dose adjustment

FAMILY:
• Daughter wants CHF explanation - see "Explain Meds to Family"
• Questions about discharge timeline (2-3 days if improving)
• Dietary teaching - will need low sodium education

DISCHARGE PLANNING:
• Social work consult pending
• Will need PO diuretic transition
• Home health may be needed for medication management

═══════════════════════════════════════════════════════════════

⏱️ Time: 28 seconds | Manual estimate: 5 minutes | Saved: 4.5 min
```

---

## Sample Output 4: Family Med Teach

**Trigger:** Daughter arrives and asks "What are all these medications for?" - Nurse clicks "Explain Meds to Family"

### MedGemma Output:

```
💊 MEDICATION EXPLANATION FOR FAMILY
Patient: Mary Johnson | Explained in Simple Terms

═══════════════════════════════════════════════════════════════

Hello! I'm going to explain your mother's medications in plain
language so you understand what each one does and why she takes it.

───────────────────────────────────────────────────────────────

METOPROLOL (Lopressor) - 25mg twice daily

What it's for: This is a "heart helper" medicine. Your mom's
heart has been working too hard, and this medicine helps it
slow down and beat more efficiently.

What it does: Think of it like taking your foot off the gas
pedal - it lets the heart rest and not work so hard. This also
helps control her blood pressure.

What to watch for: Your mom might feel a bit tired or have
cold hands and feet. These are normal. If she feels very dizzy
or like her heart is beating too slowly, let the nurse know.

Important tip: We check her heart rate before giving this.
If it's too slow (under 60), we may hold it.

───────────────────────────────────────────────────────────────

FUROSEMIDE (Lasix) - 40mg IV twice daily

What it's for: This is a "water pill" that helps your mom's
body get rid of extra fluid. When the heart isn't pumping well,
fluid can build up in the legs and lungs.

What it does: It's like opening a drain - it tells the kidneys
to flush out extra water and salt. That's why she's been going
to the bathroom more often.

What to watch for: This medicine can make her feel thirsty.
It can also lower potassium levels (that's why we check her
blood so often). Let us know if she feels weak or has leg cramps.

Important tip: We weigh her every morning to see how much
fluid is coming off. She's already lost about 5 pounds of
fluid since admission - that's good progress!

───────────────────────────────────────────────────────────────

DIGOXIN (Lanoxin) - 0.125mg daily

What it's for: This medicine helps her heart squeeze stronger
with each beat and keeps her heart rhythm more regular.

What it does: Think of it like a coach helping the heart
perform better - it makes each heartbeat more effective without
making the heart work harder.

What to watch for: ⚠️ This medicine needs careful monitoring.
Too much can cause nausea, vision changes (seeing yellow halos),
or an irregular heartbeat. That's why we check blood levels.

Important tip: Right now, we're holding this medicine because
her potassium is a bit low. Low potassium can make digoxin
build up to unsafe levels. We'll restart it once we get her
potassium back to normal.

───────────────────────────────────────────────────────────────

LISINOPRIL - 10mg daily

What it's for: This protects her heart and kidneys. It's called
an "ACE inhibitor."

What it does: It relaxes blood vessels so blood flows more
easily. This takes pressure off the heart and helps it heal.
It also protects the kidneys, which is important for people
with heart failure.

What to watch for: A dry cough is common (not dangerous, just
annoying). Dizziness when standing up too fast can happen.
Let us know if her lips or tongue swell - that's rare but
needs immediate attention.

Important tip: We monitor her kidney function with this
medicine. If her kidney numbers go up too much, we might
need to adjust the dose.

───────────────────────────────────────────────────────────────

HEPARIN - 5000 units injection 3 times daily

What it's for: This is a "blood thinner" that prevents blood
clots while she's in bed more than usual.

What it does: When people don't move around much, blood can
pool in the legs and form clots. This medicine keeps the blood
flowing smoothly.

What to watch for: Watch for unusual bruising or bleeding.
The injection site might have a small bruise - that's normal.

Important tip: She already takes a blood thinner at home for
her irregular heartbeat. This is a different type that works
while she's in the hospital.

═══════════════════════════════════════════════════════════════

QUESTIONS YOU MIGHT WANT TO ASK:

1. "When will Mom be able to go home, and will she take the
   same medications?"

2. "What signs should we watch for at home that mean we need
   to call the doctor?"

3. "Are there foods she should avoid with these medications?"

═══════════════════════════════════════════════════════════════

⚠️ DISCLAIMER: This information is for educational purposes.
Please always ask the nurse or doctor if you have any concerns
about your mother's medications or condition.

═══════════════════════════════════════════════════════════════

⏱️ Time: 35 seconds | Manual estimate: 8 minutes | Saved: 7.4 min
```

---

## Sample Output 5: Quick Explain (CHF)

**Trigger:** Daughter asks "What is CHF? The doctor keeps saying it but I don't understand"

### MedGemma Output:

```
💬 EXPLAINING: Congestive Heart Failure (CHF)
For: Family Member | Reading Level: 8th Grade

═══════════════════════════════════════════════════════════════

WHAT IT MEANS:

"Congestive Heart Failure" sounds scary, but let me break it
down for you.

Your mom's heart is like a pump that moves blood through her
body. With CHF, the heart has gotten weaker and can't pump as
strongly as it should. It's not that the heart has "failed"
completely - it's just not working at full strength.

Think of it like a tired muscle. When the heart doesn't pump
well, two things happen:

1. FLUID BACKS UP: Blood moves slower, so fluid leaks into
   places it shouldn't - like her legs (that's the swelling)
   and lungs (that's why she's been short of breath).

2. BODY DOESN'T GET ENOUGH: Her organs and muscles don't get
   as much oxygen-rich blood as they need.

The "congestive" part refers to that fluid buildup - it's
"congested" like a stuffy nose, but in her body.

───────────────────────────────────────────────────────────────

WHY THIS IS HAPPENING:

Your mom's heart function is at 35% (we call this "ejection
fraction"). A normal heart pumps out about 55-70% of its blood
with each beat. Hers pumps out less, so it has to work harder.

Several things have contributed to this:
• High blood pressure over the years
• Her irregular heart rhythm (atrial fibrillation)
• This week, eating salty foods caused her to retain more fluid
  than her heart could handle

───────────────────────────────────────────────────────────────

WHAT TO EXPECT:

THE GOOD NEWS:
✓ CHF is treatable and manageable
✓ The medications are helping - she's already improving
✓ Many people live full lives with CHF
✓ Her fluid is coming off well with the water pill

THE ONGOING PART:
• This is a chronic condition - it won't go away completely
• She'll need to take medications long-term
• Diet changes are important (less salt!)
• She'll need regular checkups with her heart doctor

───────────────────────────────────────────────────────────────

QUESTIONS YOU MIGHT WANT TO ASK THE DOCTOR:

1. "What is her prognosis? What can we expect long-term?"

2. "What are the warning signs that she's getting worse
   and needs to come back?"

3. "What lifestyle changes will help the most?"

4. "Will she need any procedures or devices?"

═══════════════════════════════════════════════════════════════

I hope this helps! Please ask me or the doctor if you have
more questions. Understanding the condition helps you support
your mom better.

═══════════════════════════════════════════════════════════════

⏱️ Time: 18 seconds | Manual estimate: 5 minutes | Saved: 4.7 min
```

---

## Sample Output 6: Shift Handoff (SBAR)

**Trigger:** End of day shift - nurse clicks "Shift Handoff"

### MedGemma Output:

```
📋 SHIFT HANDOFF REPORT - SBAR FORMAT
Patient: Johnson, Mary | Room: 412-1 | Day Shift → Evening Shift

═══════════════════════════════════════════════════════════════

📍 SITUATION

Mrs. Johnson is a 68-year-old female, Hospital Day 2, admitted
for acute on chronic CHF exacerbation. She is currently STABLE
but had a concerning morning with low potassium and hypotension.

Key events this shift:
• K+ came back at 3.2 - HELD Digoxin, repleted with KCl 40mEq PO
• BP dropped to 92/58, HR 52 - HELD AM Metoprolol
• Repeat K+ at 1400: 3.6 (improving)
• Repeat vitals 1600: BP 108/68, HR 58 (improving)

═══════════════════════════════════════════════════════════════

📚 BACKGROUND

HISTORY:
• CHF with EF 35%
• A-fib on anticoagulation
• HTN, T2DM, CKD Stage 3
• Allergies: Penicillin (rash), Sulfa (hives)

ADMISSION REASON:
• 3 days progressive dyspnea, weight gain
• Precipitated by dietary indiscretion (high sodium)
• Admission BNP 1,245, now 892 (improving)

CURRENT TREATMENT:
• Lasix 40mg IV q12h (1800 dose due)
• Metoprolol 25mg BID (held AM, reassess for PM)
• Digoxin 0.125mg daily (held today, may resume if K+ stable)
• Lisinopril 10mg daily (given)
• Heparin 5000 units SC q8h (2200 due)

═══════════════════════════════════════════════════════════════

🔍 ASSESSMENT

CARDIOVASCULAR:
• BP improving: 92/58 → 108/68 after holding Metoprolol
• HR still bradycardic at 58, but improved from 52
• Telemetry: A-fib with controlled rate, no ectopy
• JVD present but improved, 2+ LE edema (down from 3+)

RESPIRATORY:
• O2 sat 95% on 2L NC, bibasilar crackles improving
• RR 18, no distress at rest
• Still desats to 89% with ambulation

FLUID STATUS:
• I/O: Intake 1,200mL / Output 2,800mL = -1,600mL (good!)
• Weight: 78.2 kg (down 0.8 kg from yesterday)
• Edema improving

LABS:
• K+ 3.2 → 3.6 after repletion ✓
• Cr stable at 1.4
• Digoxin level 1.8 (therapeutic)

MENTAL STATUS:
• Alert and oriented x3
• Anxious about condition, daughter at bedside providing support
• Good understanding of diagnosis after teaching

═══════════════════════════════════════════════════════════════

💡 RECOMMENDATION

FOR EVENING SHIFT:

1. REASSESS METOPROLOL at 2000
   • If HR > 60 and BP > 100 systolic, may give
   • Call MD if unsure - order says hold for HR < 60

2. RECHECK K+ with evening labs
   • If > 3.5, Digoxin can likely resume tomorrow AM
   • Document in notes for day shift

3. CONTINUE MONITORING
   • Strict I/O - goal another 1L negative overnight
   • Daily weight at 0600
   • Telemetry for arrhythmias

4. PATIENT NEEDS
   • PRN Ondansetron available if nausea
   • Daughter updated, may have questions
   • Low sodium diet - reinforce at dinner

5. PENDING
   • Echo scheduled tomorrow
   • Social work consult for discharge planning
   • Dietary consult ordered

═══════════════════════════════════════════════════════════════

⚠️ WHAT TO WATCH FOR:

• HR dropping below 50 again
• BP dropping below 90 systolic
• Signs of dig toxicity (even though held today): N/V, visual changes
• Worsening respiratory status
• Urine output dropping off

═══════════════════════════════════════════════════════════════

PIV: Right forearm, 20g, day 2, flushes well
Code Status: Full Code
Family: Daughter (Nancy) - cell 555-0199, updated at 1500

═══════════════════════════════════════════════════════════════

⏱️ Time: 32 seconds | Manual estimate: 12 minutes | Saved: 11.5 min
```

---

## Total Time Saved This Scenario

| Feature Used | AI Time | Manual Time | Saved |
|--------------|---------|-------------|-------|
| Critical Lab Response | 23 sec | 10 min | 9.6 min |
| Progress Course | 31 sec | 10 min | 9.5 min |
| Shift Watch | 28 sec | 5 min | 4.5 min |
| Family Med Teach | 35 sec | 8 min | 7.4 min |
| Quick Explain (CHF) | 18 sec | 5 min | 4.7 min |
| Shift Handoff | 32 sec | 12 min | 11.5 min |
| **TOTAL** | **~3 min** | **50 min** | **47 min** |

**For one patient, one shift: Nearly 50 minutes saved.**

With 4-6 patients per shift, potential savings: **3-5 hours per shift**

---

## How MedGemma Powers These Outputs

Each output is generated by MedGemma 1.5 4B through:

1. **Structured Prompting**: Domain-specific system prompts for nursing context
2. **Context Injection**: Full patient data (vitals, labs, meds, notes) provided
3. **Clinical Reasoning**: MedGemma trained on medical literature applies clinical logic
4. **Format Enforcement**: Output structured for clinical usability (SBAR, checklists, etc.)
5. **Safety Checks**: High-alert medications flagged, critical values highlighted

**Agentic Workflows** chain multiple MedGemma calls:
```
Input Data → Parse → Analyze → Prioritize → Format → Output
```

Each step refines the output for maximum clinical utility.

---

*These sample outputs demonstrate the quality and clinical relevance of NurseGemma responses when powered by MedGemma 1.5 4B.*
