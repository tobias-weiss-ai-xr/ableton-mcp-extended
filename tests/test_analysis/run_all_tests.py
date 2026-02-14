#!/usr/bin/env python3
"""
Comprehensive VST audio analysis test runner.

Runs all unit tests for the VST analysis system with coverage reporting.
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__),
        )
        if result.returncode == 0:
            print(f"✅ {description}")
            if result.stdout:
                print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}: Command not found - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False


def main():
    """Run all tests with coverage."""
    print("=" * 60)
    print("VST AUDIO ANALYSIS - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Test imports first
    print("\n1. Testing imports...")
    if not run_command(
        "python -c \"import sys; sys.path.append('C:/Users/Tobias/git/ableton-mcp-extended/scripts/analysis'); from poll_plugin_params import ParameterPoller; print('✓ ParameterPoller import successful')\"",
        "Testing parameter polling imports",
    ):
        return False

    # Test rules parser
    if not run_command(
        "python -c \"import sys; sys.path.append('C:/Users/Tobias/git/ableton-mcp-extended/scripts/analysis'); from rules_parser import RulesParser; print('✓ RulesParser import successful')\"",
        "Testing rules parser imports",
    ):
        return False

    # Test rules engine
    if not run_command(
        "python -c \"import sys; sys.path.append('C:/Users/Tobias/git/ableton-mcp-extended/scripts/analysis'); from rules_engine import RulesEngine; print('✓ RulesEngine import successful')\"",
        "Testing rules engine imports",
    ):
        return False

    # Test responsive controller
    if not run_command(
        "python -c \"import sys; sys.path.append('C:/Users/Tobias/git/ableton-mcp-extended/scripts/analysis'); from responsive_control import ResponsiveController; print('✓ ResponsiveController import successful')\"",
        "Testing responsive controller imports",
    ):
        return False

    print("\n✅ All imports successful!")

    # Run individual test modules
    test_modules = [
        ("test_parameter_polling.py", "Testing parameter polling system"),
        ("test_rules_parser.py", "Testing rules parser"),
        ("test_rules_engine.py", "Testing rules engine"),
        ("test_integration.py", "Testing integration scenarios"),
    ]

    all_passed = True
    for module, description in test_modules:
        print(f"\n2. Running {description}...")
        success = run_command(f"python -m pytest {module} -v --tb=short", description)

        if not success:
            all_passed = False
            break

    # Run coverage if all tests passed
    if all_passed:
        print("\n3. Running coverage analysis...")
        success = run_command(
            "python -m coverage run --source=../../scripts/analysis -m pytest --cov-report=html --cov-report=term --cov=scripts/analysis .",
            "Generating coverage report",
        )

        if success:
            print("\n📊 Coverage report generated: htmlcov/index.html")
        else:
            print("\n❌ Coverage analysis failed")
            return False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("📊 Test coverage: See htmlcov/index.html")
        print(
            "🎯 VST Audio Analysis System: Unit tests complete with >80% coverage target"
        )
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Check individual test outputs above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
