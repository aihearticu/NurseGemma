"""
ACLS 2025 Compliance Test Suite
Tests Code Blue Agent against AHA 2025 Guidelines
"""

import pytest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from code_blue_agent import CodeBlueAgent, ACLSPath, Rhythm


class TestACLSDrugTiming:
    """Test ACLS drug timing compliance."""
    
    def test_vf_epi_after_second_shock(self):
        """VF/pVT: Epinephrine should be given AFTER 2nd shock."""
        agent = CodeBlueAgent()
        agent.start_code()
        
        # Process VF scenario
        agent.process_voice("V-fib")
        agent.process_voice("Shock delivered 200J")
        
        # Check prompt - should NOT suggest Epi yet
        prompt = agent._get_next_prompt()
        assert "Epi 1mg NOW" not in prompt, "Should not prompt for Epi before 2nd shock in VF"
        
        # After 2nd shock
        agent.process_voice("Shock delivered 200J")
        prompt = agent._get_next_prompt()
        assert "Epi" in prompt, "Should prompt for Epi after 2nd shock"
    
    def test_pea_epi_asap(self):
        """PEA/Asystole: Epinephrine should be given ASAP."""
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("IV access")
        agent.process_voice("Asystole")
        
        prompt = agent._get_next_prompt()
        assert "ASAP" in prompt or "Epi" in prompt, "Should prompt for Epi ASAP in non-shockable"
    
    def test_amio_after_third_shock(self):
        """Amiodarone should be prompted after 3rd shock for refractory VF/pVT."""
        agent = CodeBlueAgent()
        agent.start_code()
        
        agent.process_voice("V-fib")
        agent.process_voice("Shock delivered")
        agent.process_voice("Shock delivered")
        
        # After 2 shocks - no Amio prompt
        prompt = agent._get_next_prompt()
        assert "Amiodarone" not in prompt, "Should not prompt for Amio before 3rd shock"
        
        # After 3rd shock
        agent.process_voice("Shock delivered")
        prompt = agent._get_next_prompt()
        assert "Amiodarone" in prompt, "Should prompt for Amio after 3rd shock"


class TestACLSPathway:
    """Test ACLS pathway determination."""
    
    def test_vf_is_shockable(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("V-fib")
        assert agent.session.acls_path == ACLSPath.SHOCKABLE
        assert agent.session.current_rhythm == Rhythm.VF
    
    def test_vt_is_shockable(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("V-tach pulseless")
        assert agent.session.acls_path == ACLSPath.SHOCKABLE
    
    def test_pea_is_non_shockable(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("PEA")
        assert agent.session.acls_path == ACLSPath.NON_SHOCKABLE
    
    def test_asystole_is_non_shockable(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("Asystole")
        assert agent.session.acls_path == ACLSPath.NON_SHOCKABLE


class TestETCO2Monitoring:
    """Test ETCO2 monitoring and interpretation."""
    
    def test_etco2_parsing_with_timestamp(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        result = agent.process_voice("ETCO2 25 22:05")
        assert "25 mmHg" in result
        assert len(agent.session.etco2_values) == 1
        assert agent.session.etco2_values[0][1] == 25
    
    def test_etco2_low_warning(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        result = agent.process_voice("ETCO2 8")
        assert "Low ETCO2" in result or "<10" in result
    
    def test_etco2_rosc_indicator(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        result = agent.process_voice("ETCO2 45")
        assert "ROSC" in result or "≥40" in result


class TestHsAndTs:
    """Test H's and T's checklist."""
    
    def test_hs_ts_command(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        result = agent.process_voice("Check H's and T's")
        assert agent.session.hs_ts_checked
        assert "Hypovolemia" in result
        assert "Tension pneumo" in result
    
    def test_hs_ts_prompt_for_pea(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("PEA")
        
        prompt = agent._get_next_prompt()
        assert "H's and T's" in prompt


class TestCPRQuality:
    """Test CPR quality tracking."""
    
    def test_cpr_cycle_tracking(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        agent.process_voice("CPR started")
        assert agent.session.cpr_cycles == 1
        
        agent.process_voice("CPR started")
        assert agent.session.cpr_cycles == 2
    
    def test_compressor_switch_tracking(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        agent.process_voice("CPR started")
        agent.process_voice("Switch compressor")
        
        assert len(agent.session.compressor_changes) == 1


class TestCodeRecord:
    """Test Code Blue Record generation."""
    
    def test_record_contains_acls_header(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("V-fib")
        agent.process_voice("ROSC")
        
        record = agent.generate_code_record()
        assert "ACLS 2025" in record
    
    def test_record_contains_etco2(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("ETCO2 30")
        agent.process_voice("ROSC")
        
        record = agent.generate_code_record()
        assert "ETCO2" in record


class TestTeamRoles:
    """Test team role documentation."""
    
    def test_team_leader_tracking(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        result = agent.process_voice("Team leader: Dr Smith")
        assert "Team Leader" in result
        assert "team_leader" in agent.session.team_roles
    
    def test_multiple_roles(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        agent.process_voice("Recorder: Sarah")
        agent.process_voice("Compressor: Mike")
        agent.process_voice("Airway: RT Lisa")
        
        assert len(agent.session.team_roles) == 3


class TestProviderNotifications:
    """Test provider notification tracking."""
    
    def test_notification_logging(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        result = agent.process_voice("Notified attending")
        assert "notified" in result.lower()
        assert len(agent.session.notifications) == 1


class TestQualityMetrics:
    """Test quality metric tracking."""
    
    def test_time_to_first_shock(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("V-fib")
        agent.process_voice("Shock delivered 200J")
        
        assert agent.session.time_to_first_shock is not None
        assert agent.session.time_to_first_shock >= 0
    
    def test_time_to_first_epi(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("PEA")
        agent.process_voice("IV access")
        agent.process_voice("Epi given")
        
        assert agent.session.time_to_first_epi is not None


class TestPostROSCCare:
    """Test post-ROSC care tracking."""
    
    def test_post_rosc_checklist_display(self):
        agent = CodeBlueAgent()
        agent.start_code()
        
        # ROSC displays post-cardiac arrest care guidance
        result = agent.process_voice("ROSC")
        assert "POST-CARDIAC ARREST" in result or "Airway" in result
        assert "ECG" in result or "cath lab" in result
    
    def test_post_rosc_items(self):
        agent = CodeBlueAgent()
        agent.start_code()
        agent.process_voice("ROSC")
        
        agent.process_voice("12 lead done")
        assert agent.session.post_rosc_checklist["12_lead_ecg"]
        
        agent.process_voice("TTM initiated")
        assert agent.session.post_rosc_checklist["consider_ttm"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
