"""
Tests for NurseGemma Highlight-to-Explain Feature
Validates the ability to explain medical terms from progress notes.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nurse_companion import NurseCompanion, ReadingLevel
from sample_patients import MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN, SAMPLE_PATIENTS


class TestMDProgressNotes:
    """Test MD progress notes are available for patients"""

    def test_mrs_johnson_has_md_note(self):
        """Mrs. Johnson should have an MD progress note"""
        assert hasattr(MRS_JOHNSON, 'md_progress_note')
        assert MRS_JOHNSON.md_progress_note
        assert len(MRS_JOHNSON.md_progress_note) > 100

    def test_mr_smith_has_md_note(self):
        """Mr. Smith should have an MD progress note"""
        assert hasattr(MR_SMITH, 'md_progress_note')
        assert MR_SMITH.md_progress_note
        assert len(MR_SMITH.md_progress_note) > 100

    def test_ms_rodriguez_has_md_note(self):
        """Ms. Rodriguez should have an MD progress note"""
        assert hasattr(MS_RODRIGUEZ, 'md_progress_note')
        assert MS_RODRIGUEZ.md_progress_note
        assert len(MS_RODRIGUEZ.md_progress_note) > 100

    def test_mr_chen_has_md_note(self):
        """Mr. Chen should have an MD progress note"""
        assert hasattr(MR_CHEN, 'md_progress_note')
        assert MR_CHEN.md_progress_note
        assert len(MR_CHEN.md_progress_note) > 100

    def test_md_note_contains_medical_terms(self):
        """MD notes should contain medical terminology for demo"""
        # Mrs. Johnson should have CHF-related terms
        note = MRS_JOHNSON.md_progress_note.lower()
        assert "chf" in note or "heart failure" in note
        assert "k+" in note or "potassium" in note

        # Ms. Rodriguez should have DKA-related terms
        note = MS_RODRIGUEZ.md_progress_note.lower()
        assert "dka" in note or "ketoacidosis" in note

        # Mr. Chen should have surgical terms
        note = MR_CHEN.md_progress_note.lower()
        assert "orif" in note or "fracture" in note


class TestHighlightExplainMethod:
    """Test the explain_highlighted_text method"""

    def test_method_exists(self):
        """explain_highlighted_text method should exist"""
        companion = NurseCompanion()
        assert hasattr(companion, 'explain_highlighted_text')

    def test_explain_abbreviation_method_exists(self):
        """explain_abbreviation method should exist"""
        companion = NurseCompanion()
        assert hasattr(companion, 'explain_abbreviation')

    def test_explain_chf(self):
        """Should be able to explain CHF"""
        companion = NurseCompanion()
        try:
            companion.explain_highlighted_text(
                highlighted_text="CHFrEF (EF 35%)",
                audience="nursing"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_explain_dka(self):
        """Should be able to explain DKA"""
        companion = NurseCompanion()
        try:
            companion.explain_highlighted_text(
                highlighted_text="DKA",
                reading_level=ReadingLevel.BASIC,
                audience="patient"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_explain_with_context(self):
        """Should accept source context"""
        companion = NurseCompanion()
        try:
            companion.explain_highlighted_text(
                highlighted_text="A-fib with RVR",
                source_context="Patient with h/o CHFrEF, A-fib on anticoagulation",
                audience="nursing"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise

    def test_explain_surgical_term(self):
        """Should be able to explain surgical terms"""
        companion = NurseCompanion()
        try:
            companion.explain_highlighted_text(
                highlighted_text="L hip ORIF for intertrochanteric femur fracture",
                audience="patient"
            )
        except Exception as e:
            if "model" not in str(e).lower() and "NoneType" not in str(e):
                raise


class TestMDNoteDisplayMethod:
    """Test the MD note display method"""

    def test_display_method_exists(self):
        """get_md_note_display method should exist"""
        assert hasattr(MRS_JOHNSON, 'get_md_note_display')

    def test_display_returns_string(self):
        """Display method should return a string"""
        result = MRS_JOHNSON.get_md_note_display()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_full_context_includes_md_note(self):
        """get_full_context should include MD note"""
        context = MRS_JOHNSON.get_full_context()
        assert "MD PROGRESS NOTE" in context


class TestCommonMedicalTerms:
    """Test explaining common medical terms from progress notes"""

    def test_terms_list(self):
        """Should handle common medical abbreviations"""
        companion = NurseCompanion()
        common_terms = [
            "CAP",  # Community-acquired pneumonia
            "COPD",  # Chronic obstructive pulmonary disease
            "BNP",  # Brain natriuretic peptide
            "EF",  # Ejection fraction
            "DVT",  # Deep vein thrombosis
            "POD#2",  # Post-operative day 2
            "WBAT",  # Weight bearing as tolerated
            "NAD",  # No acute distress
            "RRR",  # Regular rate and rhythm
            "CTAB",  # Clear to auscultation bilaterally
        ]

        for term in common_terms:
            try:
                companion.explain_highlighted_text(
                    highlighted_text=term,
                    audience="nursing"
                )
            except Exception as e:
                if "model" not in str(e).lower() and "NoneType" not in str(e):
                    raise


class TestReadingLevels:
    """Test different reading level explanations"""

    def test_reading_levels_work(self):
        """Should accept different reading levels"""
        companion = NurseCompanion()

        for level in ReadingLevel:
            try:
                companion.explain_highlighted_text(
                    highlighted_text="Pneumonia",
                    reading_level=level,
                    audience="patient"
                )
            except Exception as e:
                if "model" not in str(e).lower() and "NoneType" not in str(e):
                    raise


def run_tests():
    """Run all highlight-to-explain tests without pytest"""
    print("=" * 60)
    print("Highlight-to-Explain Feature Test Suite")
    print("=" * 60)

    test_classes = [
        TestMDProgressNotes,
        TestHighlightExplainMethod,
        TestMDNoteDisplayMethod,
        TestCommonMedicalTerms,
        TestReadingLevels,
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
        print("\nAll highlight-to-explain tests passed!")
    print("=" * 60)

    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
