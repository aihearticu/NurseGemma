"""
Tests for NurseGemma Agentic Workflows
Validates multi-step clinical reasoning workflows.
"""

import sys
from pathlib import Path

# Optional pytest import for local testing
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_workflows import (
    AgenticNurse, WorkflowType, WorkflowResult, Priority,
    HIGH_ALERT_MEDICATIONS, CRITICAL_VALUES,
    DEMO_ADMISSION_DATA, DEMO_LAB_VALUES
)
from sample_patients import MRS_JOHNSON, MR_SMITH, MS_RODRIGUEZ, MR_CHEN


class TestAgenticNurseInit:
    """Test AgenticNurse initialization"""

    def test_init_without_companion(self):
        """AgenticNurse should initialize without companion for testing"""
        agent = AgenticNurse()
        assert agent is not None
        assert agent.companion is None

    def test_workflows_defined(self):
        """All workflow types should be defined"""
        agent = AgenticNurse()
        for wf_type in WorkflowType:
            assert wf_type in agent.workflows
            assert len(agent.workflows[wf_type]) > 0

    def test_manual_times_defined(self):
        """Manual time estimates should be defined for each workflow"""
        agent = AgenticNurse()
        for wf_type in WorkflowType:
            assert wf_type in agent.manual_times
            assert agent.manual_times[wf_type] > 0


class TestAdmissionWorkflow:
    """Test Smart Admission Workflow"""

    def test_admission_workflow_steps(self):
        """Admission workflow should have 5+ steps"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.ADMISSION]
        assert len(steps) >= 5

    def test_admission_workflow_structure(self):
        """Admission workflow should have required steps"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.ADMISSION]
        step_names = [s.name for s in steps]

        assert "parse_patient_data" in step_names
        assert "medication_analysis" in step_names
        assert "sbar_handoff" in step_names

    def test_admission_workflow_execution(self):
        """Admission workflow should execute without error"""
        agent = AgenticNurse()
        result = agent.run_workflow(
            WorkflowType.ADMISSION,
            DEMO_ADMISSION_DATA
        )

        assert isinstance(result, WorkflowResult)
        assert result.workflow_type == "admission"
        assert len(result.steps_completed) > 0
        assert result.execution_time_seconds >= 0

    def test_admission_with_patient_data(self):
        """Admission workflow should work with sample patient data"""
        agent = AgenticNurse()
        result = agent.run_workflow(
            WorkflowType.ADMISSION,
            MRS_JOHNSON.get_full_context()
        )

        assert result.success or len(result.step_results) > 0


class TestCriticalLabWorkflow:
    """Test Critical Lab Response Workflow"""

    def test_critical_lab_workflow_steps(self):
        """Critical lab workflow should have 5 steps"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.CRITICAL_LAB]
        assert len(steps) >= 5

    def test_critical_lab_workflow_execution(self):
        """Critical lab workflow should execute without error"""
        agent = AgenticNurse()
        result = agent.run_workflow(
            WorkflowType.CRITICAL_LAB,
            DEMO_LAB_VALUES
        )

        assert isinstance(result, WorkflowResult)
        assert result.workflow_type == "critical_lab"

    def test_critical_lab_with_context(self):
        """Critical lab should incorporate patient context"""
        agent = AgenticNurse()
        lab_text = "\n".join([
            f"{lab.name}: {lab.value}{lab.unit}"
            for lab in MRS_JOHNSON.labs
        ])

        result = agent.run_workflow(
            WorkflowType.CRITICAL_LAB,
            lab_text,
            {"patient": MRS_JOHNSON.name, "medications": [m.name for m in MRS_JOHNSON.medications]}
        )

        assert result.workflow_type == "critical_lab"


class TestShiftHandoffWorkflow:
    """Test Shift Handoff Generator Workflow"""

    def test_handoff_workflow_steps(self):
        """Handoff workflow should have 5 steps"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.SHIFT_HANDOFF]
        assert len(steps) >= 5

    def test_handoff_workflow_structure(self):
        """Handoff workflow should generate SBAR"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.SHIFT_HANDOFF]
        step_names = [s.name for s in steps]

        assert "generate_sbar" in step_names
        assert "what_to_watch" in step_names

    def test_handoff_workflow_execution(self):
        """Handoff workflow should execute without error"""
        agent = AgenticNurse()
        notes_text = "\n".join(MR_SMITH.nursing_notes)

        result = agent.run_workflow(
            WorkflowType.SHIFT_HANDOFF,
            notes_text
        )

        assert isinstance(result, WorkflowResult)
        assert result.workflow_type == "shift_handoff"


class TestMedicationSafetyWorkflow:
    """Test Medication Safety Check Workflow"""

    def test_med_safety_workflow_steps(self):
        """Med safety workflow should have 5 steps"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.MEDICATION_SAFETY]
        assert len(steps) >= 5

    def test_med_safety_workflow_structure(self):
        """Med safety workflow should check high-alert meds"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.MEDICATION_SAFETY]
        step_names = [s.name for s in steps]

        assert "identify_high_alert" in step_names
        assert "check_interactions" in step_names

    def test_med_safety_workflow_execution(self):
        """Med safety workflow should execute without error"""
        agent = AgenticNurse()
        med_text = "\n".join([
            f"{m.name} {m.dose} {m.route} {m.frequency}"
            for m in MRS_JOHNSON.medications
        ])

        result = agent.run_workflow(
            WorkflowType.MEDICATION_SAFETY,
            med_text,
            {"patient": MRS_JOHNSON.name, "allergies": MRS_JOHNSON.allergies}
        )

        assert isinstance(result, WorkflowResult)
        assert result.workflow_type == "medication_safety"


class TestMDCommunicationWorkflow:
    """Test MD Communication Helper Workflow"""

    def test_md_comm_workflow_steps(self):
        """MD communication workflow should have 5 steps"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.MD_COMMUNICATION]
        assert len(steps) >= 5

    def test_md_comm_workflow_structure(self):
        """MD communication workflow should format SBAR"""
        agent = AgenticNurse()
        steps = agent.workflows[WorkflowType.MD_COMMUNICATION]
        step_names = [s.name for s in steps]

        assert "structure_sbar" in step_names
        assert "format_message" in step_names

    def test_md_comm_workflow_execution(self):
        """MD communication workflow should execute without error"""
        agent = AgenticNurse()

        result = agent.run_workflow(
            WorkflowType.MD_COMMUNICATION,
            "Patient's BP dropped to 92/58. Should we hold the Lisinopril?",
            {"patient": MRS_JOHNSON.name}
        )

        assert isinstance(result, WorkflowResult)
        assert result.workflow_type == "md_communication"


class TestHighAlertMedications:
    """Test high-alert medication detection"""

    def test_high_alert_list_exists(self):
        """HIGH_ALERT_MEDICATIONS list should be populated"""
        assert len(HIGH_ALERT_MEDICATIONS) > 0

    def test_common_high_alert_meds_included(self):
        """Common high-alert medications should be in the list"""
        expected = ["heparin", "insulin", "morphine", "digoxin", "warfarin"]
        for med in expected:
            assert med in HIGH_ALERT_MEDICATIONS

    def test_safety_flag_detection(self):
        """Agent should detect high-alert medications in text"""
        agent = AgenticNurse()
        warnings = agent._check_safety_flags("Patient receiving heparin drip")

        assert len(warnings) > 0
        assert any("heparin" in w.lower() for w in warnings)


class TestCriticalValues:
    """Test critical value thresholds"""

    def test_critical_values_defined(self):
        """CRITICAL_VALUES should have key labs defined"""
        expected_labs = ["potassium", "sodium", "glucose", "hemoglobin"]
        for lab in expected_labs:
            assert lab in CRITICAL_VALUES

    def test_critical_value_structure(self):
        """Critical values should have low/high thresholds"""
        for lab, values in CRITICAL_VALUES.items():
            assert "low" in values or "high" in values
            assert "unit" in values


class TestPriorityDetermination:
    """Test clinical priority determination"""

    def test_priority_critical(self):
        """Critical keywords should return CRITICAL priority"""
        agent = AgenticNurse()
        priority = agent._determine_priority(
            [],
            {"result": "This is CRITICAL - notify immediately"}
        )
        assert priority == Priority.CRITICAL

    def test_priority_urgent(self):
        """High-alert warnings should return URGENT priority"""
        agent = AgenticNurse()
        priority = agent._determine_priority(
            ["HIGH-ALERT MEDICATION: insulin"],
            {"result": "Normal result"}
        )
        assert priority == Priority.URGENT

    def test_priority_routine(self):
        """Normal results should return ROUTINE priority"""
        agent = AgenticNurse()
        priority = agent._determine_priority(
            [],
            {"result": "All values within normal limits"}
        )
        assert priority == Priority.ROUTINE


class TestWorkflowResult:
    """Test WorkflowResult dataclass"""

    def test_workflow_result_fields(self):
        """WorkflowResult should have required fields"""
        result = WorkflowResult(
            workflow_type="test",
            success=True,
            steps_completed=["step1"],
            step_results={"step1": "done"},
            final_output="Complete",
            priority=Priority.ROUTINE,
            execution_time_seconds=1.5,
            estimated_manual_time_seconds=600,
            time_saved_seconds=598.5
        )

        assert result.workflow_type == "test"
        assert result.success is True
        assert result.time_saved_seconds > 0

    def test_time_saved_calculation(self):
        """Time saved should be correctly calculated"""
        agent = AgenticNurse()
        result = agent.run_workflow(WorkflowType.ADMISSION, "Test data")

        # Time saved = manual time - execution time
        expected_saved = result.estimated_manual_time_seconds - result.execution_time_seconds
        assert abs(result.time_saved_seconds - expected_saved) < 1.0


class TestTimingMetrics:
    """Test workflow timing metrics"""

    def test_execution_time_tracked(self):
        """Workflow should track execution time"""
        agent = AgenticNurse()
        result = agent.run_workflow(WorkflowType.ADMISSION, "Test data")

        assert result.execution_time_seconds > 0

    def test_manual_time_estimated(self):
        """Workflow should estimate manual time"""
        agent = AgenticNurse()
        result = agent.run_workflow(WorkflowType.ADMISSION, "Test data")

        # Admission is estimated at 15 minutes = 900 seconds
        assert result.estimated_manual_time_seconds == 900

    def test_time_savings_positive(self):
        """Time saved should be positive (AI faster than manual)"""
        agent = AgenticNurse()
        result = agent.run_workflow(WorkflowType.ADMISSION, "Test data")

        # AI should be much faster than manual
        assert result.time_saved_seconds > 0


class TestSamplePatientIntegration:
    """Test integration with sample patients"""

    def test_mrs_johnson_admission(self):
        """Admission workflow should work with Mrs. Johnson data"""
        agent = AgenticNurse()
        result = agent.run_workflow(
            WorkflowType.ADMISSION,
            MRS_JOHNSON.get_full_context()
        )
        assert result is not None

    def test_ms_rodriguez_labs(self):
        """Critical lab workflow should work with DKA patient data"""
        agent = AgenticNurse()
        lab_text = "\n".join([
            f"{lab.name}: {lab.value}{lab.unit}"
            for lab in MS_RODRIGUEZ.labs
        ])
        result = agent.run_workflow(WorkflowType.CRITICAL_LAB, lab_text)
        assert result is not None

    def test_mr_chen_medications(self):
        """Med safety workflow should work with post-op patient data"""
        agent = AgenticNurse()
        med_text = "\n".join([
            f"{m.name} {m.dose}"
            for m in MR_CHEN.medications
        ])
        result = agent.run_workflow(WorkflowType.MEDICATION_SAFETY, med_text)
        assert result is not None


def run_tests():
    """Run all agentic workflow tests without pytest"""
    print("=" * 60)
    print("Agentic Workflows Test Suite")
    print("=" * 60)

    test_classes = [
        TestAgenticNurseInit,
        TestAdmissionWorkflow,
        TestCriticalLabWorkflow,
        TestShiftHandoffWorkflow,
        TestMedicationSafetyWorkflow,
        TestMDCommunicationWorkflow,
        TestHighAlertMedications,
        TestCriticalValues,
        TestPriorityDetermination,
        TestWorkflowResult,
        TestTimingMetrics,
        TestSamplePatientIntegration,
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
        print("\nAll agentic workflow tests passed!")
    print("=" * 60)

    return len(failed_tests) == 0


if __name__ == "__main__":
    if PYTEST_AVAILABLE:
        pytest.main([__file__, "-v"])
    else:
        success = run_tests()
        exit(0 if success else 1)
