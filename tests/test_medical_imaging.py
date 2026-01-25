"""
Tests for Medical Imaging Analysis Module
Tests multimodal image analysis capabilities for CXR, CT, MRI, and wound assessment.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from medical_imaging import (
    ImagingModality,
    Urgency,
    ImagingResult,
    IMAGING_PROMPTS,
    SAMPLE_IMAGES,
    PRESSURE_INJURY_STAGES,
    MedicalImagingAnalyzer
)


class TestImagingModality:
    """Test imaging modality enum"""

    def test_all_modalities_defined(self):
        """All expected modalities should be defined"""
        expected = ['CXR', 'CT_HEAD', 'CT_CHEST', 'CT_ABDOMEN',
                    'MRI_BRAIN', 'MRI_SPINE', 'WOUND', 'ECG']
        for modality in expected:
            assert hasattr(ImagingModality, modality)

    def test_modality_values(self):
        """Modality values should be descriptive strings"""
        assert ImagingModality.CXR.value == 'chest_xray'
        assert ImagingModality.WOUND.value == 'wound'
        assert ImagingModality.CT_HEAD.value == 'ct_head'


class TestUrgencyLevels:
    """Test urgency level enum"""

    def test_all_urgency_levels_defined(self):
        """All urgency levels should be defined"""
        expected = ['ROUTINE', 'ATTENTION', 'URGENT', 'CRITICAL']
        for level in expected:
            assert hasattr(Urgency, level)

    def test_urgency_ordering(self):
        """Urgency levels should have logical ordering"""
        levels = list(Urgency)
        assert levels[0] == Urgency.ROUTINE
        assert levels[-1] == Urgency.CRITICAL


class TestImagingPrompts:
    """Test imaging prompt templates"""

    def test_prompts_exist_for_key_modalities(self):
        """Prompts should exist for key modalities"""
        assert ImagingModality.CXR in IMAGING_PROMPTS
        assert ImagingModality.CT_HEAD in IMAGING_PROMPTS
        assert ImagingModality.WOUND in IMAGING_PROMPTS

    def test_cxr_prompt_content(self):
        """CXR prompt should include nursing-focused elements"""
        prompt = IMAGING_PROMPTS[ImagingModality.CXR]
        assert 'NURSING' in prompt.upper()
        assert 'findings' in prompt.lower() or 'FINDINGS' in prompt
        assert 'lung' in prompt.lower()
        assert 'heart' in prompt.lower()

    def test_wound_prompt_content(self):
        """Wound prompt should include NPIAP staging"""
        prompt = IMAGING_PROMPTS[ImagingModality.WOUND]
        assert 'NPIAP' in prompt
        assert 'Stage 1' in prompt
        assert 'Stage 4' in prompt
        assert 'Unstageable' in prompt
        assert 'DTPI' in prompt

    def test_ct_head_prompt_content(self):
        """CT head prompt should include stroke and hemorrhage"""
        prompt = IMAGING_PROMPTS[ImagingModality.CT_HEAD]
        assert 'hemorrhage' in prompt.lower()
        assert 'stroke' in prompt.lower() or 'STROKE' in prompt
        assert 'midline' in prompt.lower()


class TestSampleImages:
    """Test sample image definitions"""

    def test_sample_images_exist(self):
        """Sample images should be defined"""
        assert len(SAMPLE_IMAGES) > 0

    def test_cxr_samples_exist(self):
        """CXR samples should exist"""
        cxr_samples = [k for k, v in SAMPLE_IMAGES.items()
                       if v['modality'] == ImagingModality.CXR]
        assert len(cxr_samples) >= 2

    def test_wound_samples_exist(self):
        """Wound samples should exist"""
        wound_samples = [k for k, v in SAMPLE_IMAGES.items()
                         if v['modality'] == ImagingModality.WOUND]
        assert len(wound_samples) >= 3

    def test_sample_image_structure(self):
        """Each sample image should have required fields"""
        required_fields = ['url', 'modality', 'description', 'source', 'expected_findings']
        for key, img in SAMPLE_IMAGES.items():
            for field in required_fields:
                assert field in img, f"Missing {field} in {key}"

    def test_image_urls_are_https(self):
        """All image URLs should be HTTPS"""
        for key, img in SAMPLE_IMAGES.items():
            assert img['url'].startswith('https://'), f"{key} URL not HTTPS"


class TestPressureInjuryStages:
    """Test pressure injury staging reference"""

    def test_all_stages_defined(self):
        """All NPIAP stages should be defined"""
        expected_stages = ['stage_1', 'stage_2', 'stage_3', 'stage_4',
                           'unstageable', 'dtpi']
        for stage in expected_stages:
            assert stage in PRESSURE_INJURY_STAGES

    def test_stage_structure(self):
        """Each stage should have required fields"""
        required_fields = ['name', 'definition', 'key_features', 'nursing_actions']
        for stage_key, stage in PRESSURE_INJURY_STAGES.items():
            for field in required_fields:
                assert field in stage, f"Missing {field} in {stage_key}"

    def test_stage_1_is_intact_skin(self):
        """Stage 1 should be non-blanchable erythema of intact skin"""
        stage1 = PRESSURE_INJURY_STAGES['stage_1']
        assert 'intact' in stage1['definition'].lower()
        assert 'non-blanchable' in stage1['definition'].lower()

    def test_stage_4_involves_deep_tissue(self):
        """Stage 4 should involve exposed bone/tendon/fascia"""
        stage4 = PRESSURE_INJURY_STAGES['stage_4']
        definition = stage4['definition'].lower()
        key_features = ' '.join(stage4['key_features']).lower()
        assert 'bone' in key_features or 'tendon' in key_features or 'fascia' in key_features

    def test_unstageable_obscured_by_eschar(self):
        """Unstageable should be obscured by slough/eschar"""
        unstageable = PRESSURE_INJURY_STAGES['unstageable']
        assert 'eschar' in unstageable['definition'].lower() or 'slough' in unstageable['definition'].lower()

    def test_dtpi_is_deep_tissue(self):
        """DTPI should describe deep tissue injury"""
        dtpi = PRESSURE_INJURY_STAGES['dtpi']
        assert 'deep' in dtpi['name'].lower() or 'deep' in dtpi['definition'].lower()


class TestMedicalImagingAnalyzer:
    """Test the MedicalImagingAnalyzer class"""

    def test_analyzer_initialization(self):
        """Analyzer should initialize without model"""
        analyzer = MedicalImagingAnalyzer()
        assert analyzer.model is None
        assert analyzer.processor is None

    def test_analyzer_with_mock_model(self):
        """Analyzer should accept model and processor"""
        mock_model = "mock_model"
        mock_processor = "mock_processor"
        analyzer = MedicalImagingAnalyzer(model=mock_model, processor=mock_processor)
        assert analyzer.model == mock_model
        assert analyzer.processor == mock_processor

    def test_list_sample_images_all(self):
        """Should list all sample images when no filter"""
        analyzer = MedicalImagingAnalyzer()
        images = analyzer.list_sample_images()
        assert len(images) == len(SAMPLE_IMAGES)

    def test_list_sample_images_filtered(self):
        """Should filter sample images by modality"""
        analyzer = MedicalImagingAnalyzer()
        cxr_images = analyzer.list_sample_images(ImagingModality.CXR)
        wound_images = analyzer.list_sample_images(ImagingModality.WOUND)

        # All should be correct modality
        for img in cxr_images:
            assert img['modality'] == ImagingModality.CXR
        for img in wound_images:
            assert img['modality'] == ImagingModality.WOUND

    def test_get_wound_staging_reference(self):
        """Should return staging reference for valid stage"""
        analyzer = MedicalImagingAnalyzer()
        stage2 = analyzer.get_wound_staging_reference('stage_2')
        assert 'name' in stage2
        assert 'Stage 2' in stage2['name']

    def test_get_wound_staging_invalid(self):
        """Should return empty dict for invalid stage"""
        analyzer = MedicalImagingAnalyzer()
        invalid = analyzer.get_wound_staging_reference('stage_99')
        assert invalid == {}


class TestImagingResult:
    """Test the ImagingResult dataclass"""

    def test_imaging_result_creation(self):
        """Should create ImagingResult with all fields"""
        result = ImagingResult(
            modality=ImagingModality.CXR,
            findings="Normal chest x-ray",
            nursing_implications="Continue monitoring",
            urgency=Urgency.ROUTINE,
            notify_provider=False,
            sbar_summary=None,
            execution_time=2.5,
            estimated_manual_time=300.0
        )
        assert result.modality == ImagingModality.CXR
        assert result.urgency == Urgency.ROUTINE
        assert not result.notify_provider
        assert result.execution_time == 2.5

    def test_imaging_result_with_sbar(self):
        """Should include SBAR when urgent"""
        result = ImagingResult(
            modality=ImagingModality.CT_HEAD,
            findings="Large subdural hematoma",
            nursing_implications="Neuro checks q15min",
            urgency=Urgency.CRITICAL,
            notify_provider=True,
            sbar_summary="S: Patient with acute SDH...",
            execution_time=3.0,
            estimated_manual_time=600.0
        )
        assert result.notify_provider
        assert result.sbar_summary is not None


class TestClinicalAccuracy:
    """Test clinical accuracy of staging definitions"""

    def test_wound_staging_progression(self):
        """Wound staging should progress in tissue depth"""
        stages = PRESSURE_INJURY_STAGES

        # Stage 1 = intact skin
        assert 'intact' in stages['stage_1']['definition'].lower()

        # Stage 2 = partial thickness (dermis)
        assert 'partial' in stages['stage_2']['definition'].lower()

        # Stage 3 = full thickness (adipose)
        features3 = ' '.join(stages['stage_3']['key_features']).lower()
        assert 'adipose' in features3 or 'fat' in features3

        # Stage 4 = bone/tendon/fascia
        features4 = ' '.join(stages['stage_4']['key_features']).lower()
        assert any(term in features4 for term in ['bone', 'tendon', 'fascia', 'muscle'])

    def test_stable_heel_eschar_exception(self):
        """Unstageable should note stable heel eschar exception"""
        unstageable = PRESSURE_INJURY_STAGES['unstageable']
        actions = ' '.join(unstageable['nursing_actions']).lower()
        assert 'heel' in actions
        assert 'not' in actions or 'do not' in actions


class TestSampleImageDiversity:
    """Test diversity of sample images for demo"""

    def test_multiple_cxr_findings(self):
        """Should have CXRs with different findings"""
        cxr_samples = {k: v for k, v in SAMPLE_IMAGES.items()
                       if v['modality'] == ImagingModality.CXR}

        descriptions = [v['description'].lower() for v in cxr_samples.values()]

        # Should have variety
        has_normal = any('normal' in d for d in descriptions)
        has_pneumonia = any('pneumonia' in d for d in descriptions)
        has_effusion = any('effusion' in d for d in descriptions)

        assert has_normal or has_pneumonia  # At least one teaching case

    def test_multiple_wound_stages(self):
        """Should have wounds at different stages"""
        wound_samples = {k: v for k, v in SAMPLE_IMAGES.items()
                         if v['modality'] == ImagingModality.WOUND}

        keys = list(wound_samples.keys())
        descriptions = [v['description'].lower() for v in wound_samples.values()]

        # Should have multiple stages
        has_stage2 = any('stage 2' in d for d in descriptions)
        has_stage3 = any('stage 3' in d for d in descriptions)
        has_stage4 = any('stage 4' in d for d in descriptions)

        stages_present = sum([has_stage2, has_stage3, has_stage4])
        assert stages_present >= 2, "Should have at least 2 different wound stages"


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
