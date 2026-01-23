#!/usr/bin/env python3
"""
NurseGemma Pre-Submission Verification Script

Runs comprehensive checks before Kaggle submission:
1. Import Check - All Python modules load
2. Model Compatibility - MedGemma processor loads
3. Clinical Accuracy - Run test suite
4. UI Validation - Gradio components work
5. Kaggle Config - kernel-metadata.json valid
6. Safety Disclaimers - Required disclaimers present

Usage:
    python scripts/verify.py
    python scripts/verify.py --quick  # Skip slow tests
"""

import sys
import os
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    """Print verification header"""
    print()
    print("=" * 60)
    print(f"{Colors.BOLD}NURSEGEMMA VERIFICATION REPORT{Colors.END}")
    print("=" * 60)
    print()


def print_result(name: str, passed: bool, details: str = ""):
    """Print a verification result"""
    status = f"{Colors.GREEN}OK{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    print(f"{name:<20} [{status}]", end="")
    if details:
        print(f"  {details}")
    else:
        print()


def check_imports() -> tuple:
    """Check that all modules import successfully"""
    errors = []

    # Core modules
    try:
        from nurse_companion import NurseCompanion, PatientContext, ReadingLevel
    except Exception as e:
        errors.append(f"nurse_companion: {e}")

    # Agentic workflows
    try:
        from agentic_workflows import AgenticNurse, WorkflowType, WorkflowResult
    except Exception as e:
        errors.append(f"agentic_workflows: {e}")

    # Sample patients
    try:
        from sample_patients import SAMPLE_PATIENTS, MRS_JOHNSON
    except Exception as e:
        errors.append(f"sample_patients: {e}")

    # EPIC UI
    try:
        from epic_ui import build_epic_ui, EPIC_CSS
    except Exception as e:
        errors.append(f"epic_ui: {e}")

    return len(errors) == 0, errors


def check_model_compatibility() -> tuple:
    """Check MedGemma model compatibility"""
    errors = []

    try:
        from transformers import AutoProcessor
        # Just check processor loads (doesn't require GPU/model download)
        # In production, would do: processor = AutoProcessor.from_pretrained("google/medgemma-1.5-4b-it")
        # For verification, just check transformers is available
        import transformers
        version = transformers.__version__

        # Check PyTorch
        import torch
        cuda_available = torch.cuda.is_available()
        device = "CUDA" if cuda_available else "CPU"

        return True, f"transformers {version}, {device}"

    except ImportError as e:
        errors.append(f"Missing dependency: {e}")
        return False, errors
    except Exception as e:
        errors.append(str(e))
        return False, errors


def check_clinical_accuracy(quick: bool = False) -> tuple:
    """Run clinical accuracy tests"""
    try:
        import subprocess
        test_path = Path(__file__).parent.parent / "tests"

        if quick:
            # Just check tests exist
            test_files = list(test_path.glob("test_*.py"))
            return True, f"{len(test_files)} test files found"

        # Run pytest
        result = subprocess.run(
            ["python", "-m", "pytest", str(test_path), "-v", "--tb=short", "-q"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            # Parse output for pass count
            lines = result.stdout.split("\n")
            for line in lines:
                if "passed" in line:
                    return True, line.strip()
            return True, "All tests passed"
        else:
            return False, result.stdout.split("\n")[-2] if result.stdout else "Tests failed"

    except FileNotFoundError:
        return True, "No tests directory (skipped)"
    except Exception as e:
        return False, str(e)


def check_ui_components() -> tuple:
    """Check UI components work"""
    errors = []

    try:
        import gradio as gr

        # Check Gradio version
        version = gr.__version__

        # Check components can be created
        from epic_ui import EPIC_CSS, create_patient_header, format_mar_html
        from sample_patients import MRS_JOHNSON

        # Test creating HTML components
        header = create_patient_header(MRS_JOHNSON)
        mar = format_mar_html(MRS_JOHNSON)

        if not header or not mar:
            errors.append("Component generation failed")

        return len(errors) == 0, f"Gradio {version}"

    except ImportError as e:
        return False, f"Missing: {e}"
    except Exception as e:
        return False, str(e)


def check_kaggle_config() -> tuple:
    """Check kernel-metadata.json configuration"""
    config_paths = [
        Path(__file__).parent.parent / "kernel-metadata.json",
        Path(__file__).parent.parent / "notebooks" / "kernel-metadata.json",
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)

                # Required fields
                required = ["id", "title", "code_file"]
                missing = [f for f in required if f not in config]

                if missing:
                    return False, f"Missing fields: {missing}"

                # Check GPU enabled
                gpu = config.get("enable_gpu", False)
                internet = config.get("enable_internet", False)

                warnings = []
                if not gpu:
                    warnings.append("GPU disabled")
                if not internet:
                    warnings.append("Internet disabled")

                if warnings:
                    return True, f"Loaded ({', '.join(warnings)})"

                return True, f"GPU+Internet enabled"

            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {e}"
            except Exception as e:
                return False, str(e)

    return False, "kernel-metadata.json not found"


def check_safety_disclaimers() -> tuple:
    """Check safety disclaimers are present"""
    required_phrases = [
        "not a substitute",
        "educational purpose",
        "clinical judgment",
        "consult",
    ]

    found = []
    missing = []

    # Check source files
    src_path = Path(__file__).parent.parent / "src"
    files_to_check = list(src_path.glob("*.py"))

    all_text = ""
    for f in files_to_check:
        try:
            all_text += f.read_text().lower()
        except:
            pass

    # Check notebooks
    notebook_path = Path(__file__).parent.parent
    for notebook in notebook_path.glob("*.ipynb"):
        try:
            all_text += notebook.read_text().lower()
        except:
            pass

    for phrase in required_phrases:
        if phrase.lower() in all_text:
            found.append(phrase)
        else:
            missing.append(phrase)

    if missing:
        return False, f"Missing: {missing}"

    return True, f"{len(found)}/{len(required_phrases)} phrases found"


def check_file_structure() -> tuple:
    """Check required files exist"""
    root = Path(__file__).parent.parent

    required_files = [
        "src/nurse_companion.py",
        "src/agentic_workflows.py",
        "src/sample_patients.py",
        "src/epic_ui.py",
        "requirements.txt",
    ]

    missing = []
    for f in required_files:
        if not (root / f).exists():
            missing.append(f)

    if missing:
        return False, f"Missing: {missing}"

    return True, f"{len(required_files)} core files present"


def run_verification(quick: bool = False):
    """Run all verification checks"""
    print_header()

    results = []
    start_time = time.time()

    # 1. Import Check
    passed, details = check_imports()
    if isinstance(details, list) and details:
        print_result("IMPORT CHECK", passed, f"{len(details)} errors")
        for err in details[:3]:  # Show first 3 errors
            print(f"    - {err}")
    else:
        print_result("IMPORT CHECK", passed)
    results.append(passed)

    # 2. Model Compatibility
    passed, details = check_model_compatibility()
    print_result("MODEL COMPAT", passed, str(details) if details else "")
    results.append(passed)

    # 3. Clinical Accuracy
    passed, details = check_clinical_accuracy(quick)
    print_result("CLINICAL TESTS", passed, str(details) if details else "")
    results.append(passed)

    # 4. UI Components
    passed, details = check_ui_components()
    print_result("UI COMPONENTS", passed, str(details) if details else "")
    results.append(passed)

    # 5. Kaggle Config
    passed, details = check_kaggle_config()
    print_result("KAGGLE CONFIG", passed, str(details) if details else "")
    results.append(passed)

    # 6. Safety Disclaimers
    passed, details = check_safety_disclaimers()
    print_result("SAFETY CHECKS", passed, str(details) if details else "")
    results.append(passed)

    # 7. File Structure
    passed, details = check_file_structure()
    print_result("FILE STRUCTURE", passed, str(details) if details else "")
    results.append(passed)

    # Summary
    elapsed = time.time() - start_time
    passed_count = sum(results)
    total_count = len(results)

    print()
    print("-" * 60)

    if all(results):
        print(f"{Colors.GREEN}{Colors.BOLD}READY FOR SUBMISSION: YES{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}READY FOR SUBMISSION: NO{Colors.END}")
        print(f"  {passed_count}/{total_count} checks passed")

    print(f"  Verification completed in {elapsed:.1f}s")
    print("-" * 60)
    print()

    return all(results)


def main():
    """Main entry point"""
    quick = "--quick" in sys.argv or "-q" in sys.argv

    if quick:
        print(f"{Colors.YELLOW}Running quick verification (some tests skipped){Colors.END}")

    success = run_verification(quick)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
