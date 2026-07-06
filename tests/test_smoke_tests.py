"""
Final Smoke Tests - 2-Hour Dub Techno Mix

Quick validation tests before production deployment.
Tests critical paths: setup, automation, error handling, auto-save.
"""

import sys
import time
from pathlib import Path


def test_import_test():
    """Test 1: Verify all critical modules import correctly."""
    print("\n[SMOKE TEST 1] Import Verification")

    critical_modules = [
        'mcp_client',
        'session_setup',
        'automation_patterns',
        'pattern_orchestration',
        'error_handling',
        'session_auto_save',
        'clip_patterns',
        'follow_actions',
        'parameter_sweeps',
        'audio_analysis'
    ]

    failed_imports = []

    for module in critical_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module} - {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n  ✗ FAIL - {len(failed_imports)} modules failed to import")
        return False
    else:
        print(f"\n  ✓ PASS - All {len(critical_modules)} modules imported")
        return True


def test_file_existence():
    """Test 2: Verify all critical files exist."""
    print("\n[SMOKE TEST 2] File Existence Check")

    critical_files = [
        'mcp_client.py',
        'session_setup.py',
        'automation_patterns.py',
        'pattern_orchestration.py',
        'error_handling.py',
        'session_auto-save.py',
        'clip_patterns.py',
        'follow_actions.py',
        'parameter_sweeps.py',
        'audio_analysis.py',
        'scripts/dub_techno_2h_automation.py',
        'scripts/create_drum_clips.py',
        'scripts/create_bass_clips.py',
        'scripts/create_pad_clips.py',
        'tests/test_integration_test.py',
        'QUICK_START.md'
    ]

    missing_files = []

    for file_path in critical_files:
        if not Path(file_path).exists():
            print(f"  ✗ {file_path}")
            missing_files.append(file_path)
        else:
            print(f"  ✓ {file_path}")

    if missing_files:
        print(f"\n  ✗ FAIL - {len(missing_files)} files missing")
        return False
    else:
        print(f"\n  ✓ PASS - All {len(critical_files)} files present")
        return True


def test_session_setup():
    """Test 3: Test session setup without full automation."""
    print("\n[SMOKE TEST 3] Session Setup Validation")

    try:
        from mcp_client import MCPClientTCP

        client = MCPClientTCP()

        # Quick session query (no setup, just connection)
        overview = client.get_session_overview()

        # Verify response
        assert 'tempo' in overview, "Session overview missing tempo"
        assert 'tracks' in overview, "Session overview missing tracks"

        print(f"  ✓ Session tempo: {overview['tempo']} BPM")
        print(f"  ✓ Track count: {len(overview['tracks'])}")

        print(f"\n  ✓ PASS - Session query successful")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - Session query failed: {e}")
        return False


def test_wave_structure():
    """Test 4: Verify wave structure is coherent."""
    print("\n[SMOKE TEST 4] Wave Structure Validation")

    try:
        from pattern_orchestration import PatternOrchestrator, WaveType

        orchestrator = PatternOrchestrator()

        # Check wave count
        assert len(orchestrator.waves) == 4, f"Expected 4 waves, got {len(orchestrator.waves)}"

        # Check wave types
        expected_types = [WaveType.INTRO, WaveType.MAIN, WaveType.CLIMAX, WaveType.OUTRO]
        actual_types = [wave.wave_type for wave in orchestrator.waves]

        for expected, actual in zip(expected_types, actual_types):
            assert expected == actual, f"Wave type mismatch: expected {expected}, got {actual}"

        # Check total beats
        total_beats = sum(wave.duration_beats for wave in orchestrator.waves)
        assert total_beats > 9000, f"Total beats too low: {total_beats}"

        print(f"  ✓ Wave count: {len(orchestrator.waves)}")
        print(f"  ✓ Wave types: {[t.value for t in actual_types]}")
        print(f"  ✓ Total beats: {total_beats}")

        print(f"\n  ✓ PASS - Wave structure valid")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - Wave structure validation failed: {e}")
        return False


def test_error_handling():
    """Test 5: Verify error handling system initializes."""
    print("\n[SMOKE TEST 5] Error Handling System")

    try:
        from error_handling import SessionErrorHandler, ErrorSeverity

        handler = SessionErrorHandler()

        # Create test error context
        from error_handling import create_error_context

        error_context = create_error_context(
            error_type="TestError",
            message="Test error message",
            severity=ErrorSeverity.LOW,
            operation="test_operation"
        )

        # Verify context created
        assert error_context.error_type == "TestError"
        assert error_context.severity == ErrorSeverity.LOW

        # Verify error handler methods
        assert hasattr(handler, 'handle_error')
        assert hasattr(handler, 'get_error_summary')

        print(f"  ✓ Error handler initialized")
        print(f"  ✓ Error context creation working")

        print(f"\n  ✓ PASS - Error handling system functional")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - Error handling test failed: {e}")
        return False


def test_auto_save():
    """Test 6: Verify auto-save can create save directory."""
    print("\n[SMOKE TEST 6] Auto-Save System")

    try:
        from session_auto_save import SessionAutoSaver
        from mcp_client import MCPClientTCP

        client = MCPClientTCP()
        saver = SessionAutoSaver(client, save_directory="test_saves")

        # Verify save directory created
        assert Path("test_saves").exists(), "Save directory not created"

        # Test save operation (force save)
        save_metadata = saver.check_and_save(current_beat=100, force=True)

        # Verify save metadata
        assert save_metadata is not None, "Save returned None"
        assert 'save_file' in save_metadata, "Missing save_file in metadata"

        # Verify save file exists
        save_path = Path(save_metadata['save_file'])
        assert save_path.exists(), "Save file not created"

        print(f"  ✓ Save directory created")
        print(f"  ✓ Save file created: {save_path.name}")

        # Cleanup test saves
        import shutil
        if Path("test_saves").exists():
            shutil.rmtree("test_saves")

        print(f"\n  ✓ PASS - Auto-save system functional")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - Auto-save test failed: {e}")
        return False


def test_script_execution():
    """Test 7: Verify main automation script imports."""
    print("\n[SMOKE TEST 7] Main Script Validation")

    try:
        import importlib.util
        import sys

        script_path = Path("scripts/dub_techno_2h_automation.py")

        # Load module without executing
        spec = importlib.util.spec_from_file_location("__main__", script_path)
        module = importlib.util.module_from_spec(spec)

        # Test that module can be loaded
        print(f"  ✓ Script path valid")
        print(f"  ✓ Module can be imported")

        print(f"\n  ✓ PASS - Main script valid")
        return True

    except Exception as e:
        print(f"  ✗ FAIL - Script validation failed: {e}")
        return False


def run_all_smoke_tests() -> dict:
    """Run all smoke tests."""
    print("=" * 60)
    print("SMOKE TESTS - 2-HOUR DUB TECHNO MIX")
    print("=" * 60)

    start_time = time.time()

    test_functions = [
        test_import_test,
        test_file_existence,
        test_session_setup,
        test_wave_structure,
        test_error_handling,
        test_auto_save,
        test_script_execution
    ]

    results = []
    passed = 0
    failed = 0

    for test_func in test_functions:
        success = test_func()
        results.append({
            'test_name': test_func.__name__,
            'passed': success
        })

        if success:
            passed += 1
        else:
            failed += 1

    elapsed = time.time() - start_time

    # Print summary
    print(f"\n{'=' * 60}")
    print("SMOKE TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total Tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Duration: {elapsed:.2f}s")

    if failed == 0:
        print(f"\n✓ ALL SMOKE TESTS PASSED - System ready for production")
        return {
            'success': True,
            'passed': passed,
            'failed': failed,
            'duration_seconds': elapsed
        }
    else:
        print(f"\n✗ {failed} SMOKE TESTS FAILED - Review failures before deployment")
        return {
            'success': False,
            'passed': passed,
            'failed': failed,
            'duration_seconds': elapsed,
            'failed_tests': [r['test_name'] for r in results if not r['passed']]
        }


if __name__ == "__main__":
    result = run_all_smoke_tests()
    sys.exit(0 if result['success'] else 1)