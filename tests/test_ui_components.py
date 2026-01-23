"""
Tests for NurseGemma EPIC-Style UI Components
Validates all UI helper functions and formatters.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from epic_ui import (
    EPIC_CSS,
    create_patient_header,
    format_mar_html,
    format_labs_html,
    format_vitals_html,
    format_notes_html,
    format_md_note_html,
    format_ai_response,
    format_time_savings,
    format_cumulative_time_savings,
    get_disclaimer,
)
from sample_patients import MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN


class TestEpicCSS:
    """Test CSS styling is properly defined"""

    def test_css_exists(self):
        """EPIC CSS should be defined"""
        assert EPIC_CSS is not None
        assert len(EPIC_CSS) > 100

    def test_css_contains_epic_colors(self):
        """CSS should contain EPIC color palette"""
        assert "--epic-header-bg" in EPIC_CSS
        assert "--epic-accent" in EPIC_CSS
        assert "#1a365d" in EPIC_CSS  # Navy blue

    def test_css_contains_status_colors(self):
        """CSS should contain status colors"""
        assert "--status-normal" in EPIC_CSS
        assert "--status-warning" in EPIC_CSS
        assert "--status-critical" in EPIC_CSS

    def test_css_contains_lab_colors(self):
        """CSS should contain lab value colors"""
        assert "--lab-high" in EPIC_CSS
        assert "--lab-low" in EPIC_CSS


class TestPatientHeader:
    """Test patient header generation"""

    def test_header_contains_patient_name(self):
        """Header should contain patient name"""
        header = create_patient_header(MRS_JOHNSON)
        assert "Mary Johnson" in header

    def test_header_contains_room(self):
        """Header should contain room number"""
        header = create_patient_header(MRS_JOHNSON)
        assert "412" in header

    def test_header_contains_mrn(self):
        """Header should contain MRN"""
        header = create_patient_header(MRS_JOHNSON)
        assert MRS_JOHNSON.mrn in header

    def test_header_contains_attending(self):
        """Header should contain attending physician"""
        header = create_patient_header(MRS_JOHNSON)
        assert "Smith" in header

    def test_header_is_html(self):
        """Header should be valid HTML"""
        header = create_patient_header(MRS_JOHNSON)
        assert "<div" in header
        assert "</div>" in header

    def test_all_patients_work(self):
        """Header should work for all sample patients"""
        for patient in [MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN]:
            header = create_patient_header(patient)
            assert patient.name in header


class TestMARFormatting:
    """Test MAR display formatting"""

    def test_mar_is_html_table(self):
        """MAR should be formatted as HTML table"""
        mar = format_mar_html(MRS_JOHNSON)
        assert "<table" in mar
        assert "</table>" in mar

    def test_mar_contains_medication_names(self):
        """MAR should contain medication names"""
        mar = format_mar_html(MRS_JOHNSON)
        assert "METOPROLOL" in mar
        assert "LISINOPRIL" in mar

    def test_mar_shows_high_alert(self):
        """MAR should flag high-alert medications"""
        mar = format_mar_html(MRS_JOHNSON)
        assert "HIGH-ALERT" in mar or "high-alert" in mar

    def test_mar_shows_doses(self):
        """MAR should show medication doses"""
        mar = format_mar_html(MRS_JOHNSON)
        assert "25mg" in mar or "40mg" in mar

    def test_all_patients_mar_works(self):
        """MAR should work for all sample patients"""
        for patient in [MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN]:
            mar = format_mar_html(patient)
            assert "<table" in mar


class TestLabsFormatting:
    """Test labs display formatting"""

    def test_labs_is_html_table(self):
        """Labs should be formatted as HTML table"""
        labs = format_labs_html(MRS_JOHNSON)
        assert "<table" in labs
        assert "</table>" in labs

    def test_labs_contains_values(self):
        """Labs should contain lab values"""
        labs = format_labs_html(MRS_JOHNSON)
        assert "Potassium" in labs or "potassium" in labs

    def test_labs_shows_abnormal_flags(self):
        """Labs should flag abnormal values"""
        labs = format_labs_html(MRS_JOHNSON)
        # Mrs. Johnson has low K+ (3.2)
        assert "(L)" in labs or "lab-low" in labs

    def test_labs_shows_reference_ranges(self):
        """Labs should show reference ranges"""
        labs = format_labs_html(MRS_JOHNSON)
        assert "3.5" in labs or "5.0" in labs  # K+ reference

    def test_all_patients_labs_work(self):
        """Labs should work for all sample patients"""
        for patient in [MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN]:
            labs = format_labs_html(patient)
            assert "<table" in labs


class TestVitalsFormatting:
    """Test vitals display formatting"""

    def test_vitals_is_html_table(self):
        """Vitals should be formatted as HTML table"""
        vitals = format_vitals_html(MRS_JOHNSON)
        assert "<table" in vitals
        assert "</table>" in vitals

    def test_vitals_shows_bp(self):
        """Vitals should show blood pressure"""
        vitals = format_vitals_html(MRS_JOHNSON)
        assert "BP" in vitals

    def test_vitals_shows_hr(self):
        """Vitals should show heart rate"""
        vitals = format_vitals_html(MRS_JOHNSON)
        assert "HR" in vitals

    def test_vitals_shows_o2(self):
        """Vitals should show O2 saturation"""
        vitals = format_vitals_html(MRS_JOHNSON)
        assert "SpO2" in vitals

    def test_vitals_flags_abnormal(self):
        """Vitals should flag abnormal values"""
        vitals = format_vitals_html(MRS_JOHNSON)
        # Mrs. Johnson has low BP (92/58) in latest reading
        assert "lab-low" in vitals or "lab-high" in vitals

    def test_all_patients_vitals_work(self):
        """Vitals should work for all sample patients"""
        for patient in [MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN]:
            vitals = format_vitals_html(patient)
            assert "<table" in vitals


class TestNotesFormatting:
    """Test nursing notes formatting"""

    def test_notes_is_html_list(self):
        """Notes should be formatted as HTML list"""
        notes = format_notes_html(MRS_JOHNSON)
        assert "<ul" in notes or "<li" in notes

    def test_notes_contains_content(self):
        """Notes should contain nursing note content"""
        notes = format_notes_html(MRS_JOHNSON)
        # Check for times that appear in notes
        assert "0700" in notes or "0800" in notes

    def test_all_patients_notes_work(self):
        """Notes should work for all sample patients"""
        for patient in [MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN]:
            notes = format_notes_html(patient)
            assert len(notes) > 0


class TestMDNoteFormatting:
    """Test MD progress note formatting"""

    def test_md_note_is_html(self):
        """MD note should be formatted as HTML"""
        note = format_md_note_html(MRS_JOHNSON)
        assert "<div" in note

    def test_md_note_contains_content(self):
        """MD note should contain progress note content"""
        note = format_md_note_html(MRS_JOHNSON)
        assert "PROGRESS NOTE" in note or "CHF" in note

    def test_md_note_has_tip(self):
        """MD note should have highlight tip"""
        note = format_md_note_html(MRS_JOHNSON)
        assert "Tip" in note or "highlight" in note.lower()

    def test_all_patients_md_note_work(self):
        """MD note should work for all sample patients"""
        for patient in [MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN]:
            note = format_md_note_html(patient)
            assert len(note) > 0


class TestAIResponseFormatting:
    """Test AI response card formatting"""

    def test_response_is_styled_div(self):
        """Response should be styled div"""
        response = format_ai_response("Test response", "normal")
        assert "<div" in response
        assert "ai-response" in response

    def test_response_types_have_classes(self):
        """Different response types should have different classes"""
        normal = format_ai_response("Normal", "normal")
        concern = format_ai_response("Concern", "concern")
        critical = format_ai_response("Critical", "critical")

        assert "concern" in concern
        assert "critical" in critical

    def test_response_preserves_newlines(self):
        """Response should preserve newlines as <br>"""
        response = format_ai_response("Line 1\nLine 2", "normal")
        assert "<br>" in response


class TestTimeSavingsFormatting:
    """Test time savings display formatting"""

    def test_time_savings_is_html(self):
        """Time savings should be formatted as HTML"""
        result = format_time_savings(2.5, 600, 597.5)
        assert "<div" in result
        assert "</div>" in result

    def test_time_savings_shows_saved(self):
        """Time savings should show amount saved"""
        result = format_time_savings(2.5, 600, 597.5)
        assert "Saved" in result or "saved" in result

    def test_time_savings_shows_percentage(self):
        """Time savings should show percentage faster"""
        result = format_time_savings(2.5, 600, 597.5)
        assert "%" in result
        assert "Faster" in result or "faster" in result

    def test_time_savings_converts_minutes(self):
        """Time savings should convert to minutes for large values"""
        result = format_time_savings(2.5, 600, 597.5)
        assert "min" in result

    def test_cumulative_savings_is_html(self):
        """Cumulative savings should be formatted as HTML"""
        result = format_cumulative_time_savings(1200, 5)
        assert "<div" in result

    def test_cumulative_shows_total(self):
        """Cumulative should show session total"""
        result = format_cumulative_time_savings(1200, 5)
        assert "Session" in result or "session" in result
        assert "5" in result  # tasks completed


class TestDisclaimer:
    """Test safety disclaimer"""

    def test_disclaimer_exists(self):
        """Disclaimer should exist"""
        disclaimer = get_disclaimer()
        assert disclaimer is not None
        assert len(disclaimer) > 0

    def test_disclaimer_mentions_educational(self):
        """Disclaimer should mention educational purposes"""
        disclaimer = get_disclaimer()
        assert "educational" in disclaimer.lower()

    def test_disclaimer_mentions_not_substitute(self):
        """Disclaimer should mention not a substitute"""
        disclaimer = get_disclaimer()
        assert "not" in disclaimer.lower() and "substitute" in disclaimer.lower()

    def test_disclaimer_is_styled(self):
        """Disclaimer should be styled"""
        disclaimer = get_disclaimer()
        assert "class=" in disclaimer or "style=" in disclaimer


def run_tests():
    """Run all UI component tests without pytest"""
    print("=" * 60)
    print("UI Components Test Suite")
    print("=" * 60)

    test_classes = [
        TestEpicCSS,
        TestPatientHeader,
        TestMARFormatting,
        TestLabsFormatting,
        TestVitalsFormatting,
        TestNotesFormatting,
        TestMDNoteFormatting,
        TestAIResponseFormatting,
        TestTimeSavingsFormatting,
        TestDisclaimer,
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
        print("\nAll UI component tests passed!")
    print("=" * 60)

    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
