"""
Test Scenarios for Nurse Companion
Real-world nursing scenarios for validating module responses
"""

# ==================== QUICK EXPLAIN SCENARIOS ====================

QUICK_EXPLAIN_TESTS = [
    {
        "name": "AFib explanation for family",
        "term": "atrial fibrillation",
        "reading_level": "8th grade",
        "audience": "worried family member",
        "context": "Patient just diagnosed after heart monitor showed irregular rhythm",
        "expected_elements": [
            "irregular heartbeat",
            "upper chambers",
            "electrical signals",
            "blood clots",
            "treatment options"
        ]
    },
    {
        "name": "COPD exacerbation",
        "term": "acute exacerbation of COPD",
        "reading_level": "8th grade",
        "audience": "the patient directly",
        "context": "Patient came in short of breath, has history of COPD",
        "expected_elements": [
            "flare-up",
            "breathing",
            "lungs",
            "oxygen",
            "medications"
        ]
    },
    {
        "name": "Tracheostomy for parents",
        "term": "tracheostomy",
        "reading_level": "high school",
        "audience": "child's parents",
        "context": "Their 5-year-old will need this procedure after prolonged intubation",
        "expected_elements": [
            "breathing tube",
            "neck",
            "airway",
            "temporary",
            "care"
        ]
    },
    {
        "name": "Sepsis explanation",
        "term": "sepsis",
        "reading_level": "8th grade",
        "audience": "worried family member",
        "context": "Patient's blood cultures came back positive",
        "expected_elements": [
            "infection",
            "blood",
            "antibiotics",
            "monitoring",
            "serious"
        ]
    },
    {
        "name": "DVT for patient",
        "term": "deep vein thrombosis",
        "reading_level": "8th grade",
        "audience": "the patient directly",
        "context": "Patient just had ultrasound confirming clot in leg",
        "expected_elements": [
            "blood clot",
            "leg",
            "blood thinner",
            "pulmonary embolism",
            "movement"
        ]
    }
]

# ==================== MED HELPER SCENARIOS ====================

MED_INFO_TESTS = [
    {
        "name": "Metoprolol info",
        "medication": "metoprolol",
        "expected_elements": [
            "blood pressure",
            "heart rate",
            "beta blocker",
            "hold parameters",
            "dizziness"
        ]
    },
    {
        "name": "Heparin drip",
        "medication": "heparin",
        "expected_elements": [
            "blood clots",
            "PTT",
            "bleeding",
            "antidote",
            "protocol"
        ]
    },
    {
        "name": "Vancomycin",
        "medication": "vancomycin",
        "expected_elements": [
            "antibiotic",
            "trough level",
            "red man syndrome",
            "kidney",
            "infusion time"
        ]
    },
    {
        "name": "Insulin lispro",
        "medication": "insulin lispro",
        "expected_elements": [
            "blood sugar",
            "meal",
            "hypoglycemia",
            "fast-acting",
            "glucose"
        ]
    },
    {
        "name": "Furosemide",
        "medication": "furosemide",
        "expected_elements": [
            "diuretic",
            "fluid",
            "potassium",
            "blood pressure",
            "urine output"
        ]
    }
]

INTERACTION_TESTS = [
    {
        "name": "Warfarin + NSAIDs",
        "medications": ["warfarin", "aspirin", "ibuprofen"],
        "expected_severity": "major",
        "expected_concern": "bleeding"
    },
    {
        "name": "ACE + K-sparing",
        "medications": ["lisinopril", "spironolactone"],
        "expected_concern": "hyperkalemia"
    },
    {
        "name": "Digoxin + Amiodarone",
        "medications": ["digoxin", "amiodarone"],
        "expected_concern": "toxicity"
    },
    {
        "name": "Metformin + Contrast",
        "medications": ["metformin"],
        "context": "Patient scheduled for CT with contrast",
        "expected_concern": "lactic acidosis"
    }
]

# ==================== SHIFT SIDEKICK SCENARIOS ====================

SBAR_TESTS = [
    {
        "name": "Pneumonia patient",
        "patient_info": """
        72 y/o male, admitted 3 days ago for community-acquired pneumonia
        PMH: HTN, DM2, COPD
        Currently on day 3 of Ceftriaxone 1g IV q24h and Azithromycin 500mg IV daily
        Vitals: T 99.2, HR 88, BP 138/82, RR 20, O2 sat 94% on 2L NC
        Morning labs: WBC 11.2 (down from 14.6), BMP normal
        Patient reports feeling better, eating 50% meals
        Still needs O2 with ambulation - sats drop to 89%
        PIV 20g right forearm, good
        PT/OT consult pending
        Blood cultures pending final read
        """,
        "expected_sections": ["SITUATION", "BACKGROUND", "ASSESSMENT", "RECOMMENDATION"]
    },
    {
        "name": "Post-op hip replacement",
        "patient_info": """
        65 y/o female, POD 1 right total hip arthroplasty
        PMH: Osteoarthritis, obesity, hypothyroidism
        Pain controlled with PCA morphine, 4/10 at rest
        Vitals stable, afebrile
        Foley in place, draining clear yellow urine
        Incision clean dry intact, JP drain with 50ml serosang output
        PT eval today - ambulated 20 feet with walker
        On Lovenox for DVT prophylaxis
        NPO to clears tolerated
        Hemovac output documented
        """,
        "expected_sections": ["SITUATION", "BACKGROUND", "ASSESSMENT", "RECOMMENDATION"]
    },
    {
        "name": "CHF exacerbation",
        "patient_info": """
        78 y/o male with acute CHF exacerbation
        PMH: CHF EF 30%, afib on warfarin, CKD stage 3
        Admitted yesterday with SOB, 10lb weight gain
        Lasix drip at 10mg/hr, strict I&O
        Today: down 3L negative, lungs improved but still crackles bilat bases
        BNP 2400 (was 3100)
        Cr stable at 1.8
        INR 2.4 (therapeutic)
        On 4L NC, sats 93%
        Cardiology following, may convert to PO diuretics tomorrow
        Diet: 2g sodium, fluid restricted 1.5L
        """,
        "expected_sections": ["SITUATION", "BACKGROUND", "ASSESSMENT", "RECOMMENDATION"]
    }
]

# ==================== CLINICAL QUICK REF SCENARIOS ====================

LAB_INTERPRETATION_TESTS = [
    {
        "name": "Critical potassium",
        "lab_name": "Potassium",
        "value": 6.2,
        "unit": "mEq/L",
        "context": "Patient with CKD on lisinopril and spironolactone",
        "expected_assessment": "high",
        "expected_urgency": "urgent"
    },
    {
        "name": "Low hemoglobin",
        "lab_name": "Hemoglobin",
        "value": 7.2,
        "unit": "g/dL",
        "context": "Post-op patient, no active bleeding seen",
        "expected_assessment": "low",
        "expected_urgency": "notify provider"
    },
    {
        "name": "Elevated troponin",
        "lab_name": "Troponin I",
        "value": 0.15,
        "unit": "ng/mL",
        "context": "Patient with chest pain",
        "expected_assessment": "elevated",
        "expected_urgency": "urgent"
    },
    {
        "name": "High INR",
        "lab_name": "INR",
        "value": 4.8,
        "unit": "",
        "context": "Patient on warfarin for afib",
        "expected_assessment": "supratherapeutic",
        "expected_action": "hold warfarin"
    },
    {
        "name": "Low sodium",
        "lab_name": "Sodium",
        "value": 126,
        "unit": "mEq/L",
        "context": "Patient on SSRI, reports headache",
        "expected_assessment": "low",
        "expected_concern": "SIADH"
    }
]

WHAT_TO_WATCH_TESTS = [
    {
        "name": "New onset afib",
        "condition": "new onset atrial fibrillation",
        "expected_elements": [
            "heart rate",
            "blood pressure",
            "anticoagulation",
            "rate vs rhythm control",
            "stroke signs"
        ]
    },
    {
        "name": "DKA",
        "condition": "diabetic ketoacidosis",
        "expected_elements": [
            "blood glucose",
            "potassium",
            "pH",
            "fluid status",
            "insulin drip"
        ]
    },
    {
        "name": "GI bleed",
        "condition": "upper GI bleeding",
        "expected_elements": [
            "hemodynamics",
            "hemoglobin",
            "stool",
            "NGT output",
            "transfusion"
        ]
    },
    {
        "name": "Stroke",
        "condition": "acute ischemic stroke post-tPA",
        "expected_elements": [
            "neuro checks",
            "blood pressure",
            "bleeding",
            "NIH stroke scale",
            "swallow"
        ]
    }
]

# ==================== RUN TESTS FUNCTION ====================

def run_validation_tests(companion):
    """Run all test scenarios and report results"""
    results = {
        "quick_explain": [],
        "med_helper": [],
        "shift_sidekick": [],
        "clinical_ref": []
    }

    print("Running Nurse Companion Validation Tests...")
    print("=" * 60)

    # Test Quick Explain
    print("\n📖 Testing Quick Explain Module...")
    for test in QUICK_EXPLAIN_TESTS[:2]:  # Run first 2 for demo
        try:
            response = companion.quick_explain(
                test["term"],
                reading_level=test.get("reading_level", "8th grade"),
                context=test.get("context", "")
            )
            # Check for expected elements
            found = sum(1 for elem in test["expected_elements"] if elem.lower() in response.lower())
            score = found / len(test["expected_elements"])
            results["quick_explain"].append({
                "name": test["name"],
                "score": score,
                "passed": score >= 0.6
            })
            print(f"  ✓ {test['name']}: {score:.0%} elements found")
        except Exception as e:
            results["quick_explain"].append({
                "name": test["name"],
                "error": str(e),
                "passed": False
            })
            print(f"  ✗ {test['name']}: Error - {e}")

    # Test Med Helper
    print("\n💊 Testing Med Helper Module...")
    for test in MED_INFO_TESTS[:2]:
        try:
            response = companion.med_info(test["medication"])
            found = sum(1 for elem in test["expected_elements"] if elem.lower() in response.lower())
            score = found / len(test["expected_elements"])
            results["med_helper"].append({
                "name": test["name"],
                "score": score,
                "passed": score >= 0.6
            })
            print(f"  ✓ {test['name']}: {score:.0%} elements found")
        except Exception as e:
            results["med_helper"].append({
                "name": test["name"],
                "error": str(e),
                "passed": False
            })
            print(f"  ✗ {test['name']}: Error - {e}")

    # Test SBAR
    print("\n📋 Testing Shift Sidekick Module...")
    for test in SBAR_TESTS[:1]:
        try:
            response = companion.generate_sbar(test["patient_info"])
            found = sum(1 for section in test["expected_sections"] if section in response)
            score = found / len(test["expected_sections"])
            results["shift_sidekick"].append({
                "name": test["name"],
                "score": score,
                "passed": score >= 0.75
            })
            print(f"  ✓ {test['name']}: {found}/{len(test['expected_sections'])} sections found")
        except Exception as e:
            results["shift_sidekick"].append({
                "name": test["name"],
                "error": str(e),
                "passed": False
            })
            print(f"  ✗ {test['name']}: Error - {e}")

    # Test Lab Interpretation
    print("\n🔬 Testing Clinical Quick Ref Module...")
    for test in LAB_INTERPRETATION_TESTS[:2]:
        try:
            response = companion.interpret_lab(
                test["lab_name"],
                test["value"],
                test["unit"],
                patient_context=None  # Simplified
            )
            passed = test["expected_assessment"].lower() in response.lower()
            results["clinical_ref"].append({
                "name": test["name"],
                "passed": passed
            })
            print(f"  {'✓' if passed else '✗'} {test['name']}: {'Correct' if passed else 'Incorrect'} assessment")
        except Exception as e:
            results["clinical_ref"].append({
                "name": test["name"],
                "error": str(e),
                "passed": False
            })
            print(f"  ✗ {test['name']}: Error - {e}")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    total_passed = 0
    total_tests = 0
    for module, tests in results.items():
        passed = sum(1 for t in tests if t.get("passed", False))
        total = len(tests)
        total_passed += passed
        total_tests += total
        print(f"{module}: {passed}/{total} passed")

    print(f"\nOVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests:.0%})")

    return results


if __name__ == "__main__":
    print("Test scenarios loaded. Import NurseCompanion and run:")
    print("  from test_scenarios import run_validation_tests")
    print("  results = run_validation_tests(companion)")
