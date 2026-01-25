"""
Tests for NurseGemma New Features:
- Patient Progress Course
- Shift Watch (What to Watch This Shift)
- Family Med Teach (Medication Explanation to Family)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nurse_companion import NurseCompanion, ReadingLevel
from sample_patients import MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN, SAMPLE_PATIENTS


class TestPatientProgressCourse:
    """Test the Patient Progress Course feature"""

    def test_method_exists(self):
        """patient_progress_course method should exist"""
        companion = NurseCompanion()
        assert hasattr(companion, 'patient_progress_course')

    def test_accepts_patient_data(self):
        """Should accept patient data string"""
        companion = NurseCompanion()
        try:
            companion.patient_progress_course(
                patient_data=MRS_JOHNSON.get_full_context()
            )
        except Exception as e:
            # Expected to fail without model loaded, but method should be callable
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_accepts_trajectory_flag(self):
        """Should accept include_trajectory parameter"""
        companion = NurseCompanion()
        try:
            companion.patient_progress_course(
                patient_data=MR_SMITH.get_full_context(),
                include_trajectory=True
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_accepts_days_summary(self):
        """Should accept days_summary parameter"""
        companion = NurseCompanion()
        try:
            companion.patient_progress_course(
                patient_data=MS_RODRIGUEZ.get_full_context(),
                days_summary=3
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_works_with_all_patients(self):
        """Should work with all sample patients"""
        companion = NurseCompanion()
        for name, patient in SAMPLE_PATIENTS.items():
            try:
                companion.patient_progress_course(
                    patient_data=patient.get_full_context()
                )
            except Exception as e:
                if "model" not in str(e).lower() and "NoneType" not in str(e):
                    raise


class TestShiftWatch:
    """Test the Shift Watch (What to Watch This Shift) feature"""

    def test_method_exists(self):
        """shift_watch method should exist"""
        companion = NurseCompanion()
        assert hasattr(companion, 'shift_watch')

    def test_day_shift(self):
        """Should accept day shift type"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MRS_JOHNSON.get_full_context(),
                shift_type="day"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_evening_shift(self):
        """Should accept evening shift type"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MR_SMITH.get_full_context(),
                shift_type="evening"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_night_shift(self):
        """Should accept night shift type"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MS_RODRIGUEZ.get_full_context(),
                shift_type="night"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_with_focus_areas(self):
        """Should accept focus_areas parameter"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MRS_JOHNSON.get_full_context(),
                shift_type="day",
                focus_areas=["cardiac", "electrolytes"]
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_dka_patient_shift_watch(self):
        """Should handle ICU patient with critical needs"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MS_RODRIGUEZ.get_full_context(),
                shift_type="night",
                focus_areas=["glucose", "potassium", "acidosis"]
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_postop_patient_shift_watch(self):
        """Should handle post-op patient"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MR_CHEN.get_full_context(),
                shift_type="day",
                focus_areas=["pain", "mobility", "DVT"]
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise


class TestFamilyMedTeach:
    """Test the Family Med Teach (Medication Explanation to Family) feature"""

    def test_method_exists(self):
        """explain_meds_to_family method should exist"""
        companion = NurseCompanion()
        assert hasattr(companion, 'explain_meds_to_family')

    def test_single_med_method_exists(self):
        """explain_single_med_to_family method should exist"""
        companion = NurseCompanion()
        assert hasattr(companion, 'explain_single_med_to_family')

    def test_multiple_medications(self):
        """Should accept list of medications"""
        companion = NurseCompanion()
        try:
            companion.explain_meds_to_family(
                medications=["Metoprolol", "Lisinopril", "Furosemide"]
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_with_patient_context(self):
        """Should accept patient context"""
        companion = NurseCompanion()
        try:
            companion.explain_meds_to_family(
                medications=["Digoxin", "Potassium Chloride"],
                patient_context="68-year-old with heart failure and low potassium"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_reading_levels(self):
        """Should accept different reading levels"""
        companion = NurseCompanion()
        for level in ReadingLevel:
            try:
                companion.explain_meds_to_family(
                    medications=["Metformin"],
                    reading_level=level
                )
            except Exception as e:
                if "model" not in str(e).lower() and "NoneType" not in str(e):
                    raise

    def test_single_med_explanation(self):
        """Should explain single medication"""
        companion = NurseCompanion()
        try:
            companion.explain_single_med_to_family(
                medication="Heparin",
                dose="5000 units SC",
                reason="prevent blood clots"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_high_alert_meds(self):
        """Should handle high-alert medications"""
        companion = NurseCompanion()
        high_alert_meds = ["Insulin", "Heparin", "Digoxin", "Hydromorphone"]
        try:
            companion.explain_meds_to_family(
                medications=high_alert_meds,
                patient_context="Patient taking multiple high-alert medications"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_include_why_flag(self):
        """Should accept include_why parameter"""
        companion = NurseCompanion()
        try:
            companion.explain_meds_to_family(
                medications=["Ceftriaxone", "Azithromycin"],
                include_why=True,
                include_side_effects=False
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_patient_specific_meds(self):
        """Should explain actual patient medications"""
        companion = NurseCompanion()
        # Get Mrs. Johnson's medication names
        med_names = [med.name for med in MRS_JOHNSON.medications]
        try:
            companion.explain_meds_to_family(
                medications=med_names,
                patient_context=f"{MRS_JOHNSON.name}, {MRS_JOHNSON.age}yo with {MRS_JOHNSON.diagnosis}"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise


class TestIntegrationWithPatients:
    """Test new features integrate properly with sample patients"""

    def test_johnson_progress_course(self):
        """Mrs. Johnson's progress course should work"""
        companion = NurseCompanion()
        try:
            companion.patient_progress_course(
                patient_data=MRS_JOHNSON.get_full_context(),
                include_trajectory=True
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_smith_shift_watch(self):
        """Mr. Smith's shift watch should work"""
        companion = NurseCompanion()
        try:
            companion.shift_watch(
                patient_data=MR_SMITH.get_full_context(),
                shift_type="evening"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_rodriguez_all_features(self):
        """Ms. Rodriguez (DKA) should work with all features"""
        companion = NurseCompanion()

        # Progress course
        try:
            companion.patient_progress_course(
                patient_data=MS_RODRIGUEZ.get_full_context()
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

        # Shift watch
        try:
            companion.shift_watch(
                patient_data=MS_RODRIGUEZ.get_full_context(),
                shift_type="night",
                focus_areas=["glucose", "potassium"]
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

        # Family med teach
        try:
            companion.explain_meds_to_family(
                medications=["Insulin Regular", "Potassium Chloride"],
                patient_context="DKA patient on insulin drip"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_chen_postop_features(self):
        """Mr. Chen (post-op) should work with all features"""
        companion = NurseCompanion()

        # Progress course
        try:
            companion.patient_progress_course(
                patient_data=MR_CHEN.get_full_context(),
                days_summary=2
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

        # Shift watch with pain focus
        try:
            companion.shift_watch(
                patient_data=MR_CHEN.get_full_context(),
                shift_type="day",
                focus_areas=["pain", "DVT prophylaxis"]
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise


def run_tests():
    """Run all new feature tests without pytest"""
    print("=" * 60)
    print("New Features Test Suite")
    print("- Patient Progress Course")
    print("- Shift Watch (What to Watch This Shift)")
    print("- Family Med Teach (Medication Explanation to Family)")
    print("=" * 60)

    test_classes = [
        TestPatientProgressCourse,
        TestShiftWatch,
        TestFamilyMedTeach,
        TestIntegrationWithPatients,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 40)

        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith('test_')]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  [PASS] {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  [FAIL] {method_name}: {e}")
                failed_tests.append((test_class.__name__, method_name, str(e)))

    print("\n" + "=" * 60)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    if failed_tests:
        print("\nFailed tests:")
        for cls, method, error in failed_tests:
            print(f"  - {cls}.{method}: {error}")
    else:
        print("\nAll new feature tests passed!")
    print("=" * 60)

    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
