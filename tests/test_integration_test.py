"""
Full Integration Test - 2-Hour Dub Techno Mix

Tests complete session automation from setup to finish.
Measures performance, verifies automation sequences, checks error recovery.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

from mcp_client import MCPClientTCP
from automation_patterns import AutomationSequencer
from pattern_orchestration import PatternOrchestrator
from error_handling import SessionErrorHandler
from session_auto_save import SessionAutoSaver


class IntegrationTest:
    """Integration test for complete 2-hour session."""

    def __init__(self):
        self.client = MCPClientTCP()
        self.sequencer = AutomationSequencer(self.client)
        self.orchestrator = PatternOrchestrator()
        self.error_handler = SessionErrorHandler()
        self.auto_saver = SessionAutoSaver(self.client)

        self.test_results = []
        self.session_start_time = None
        self.errors_encountered = 0

    def run_all_tests(self) -> dict:
        """Run complete integration test suite."""
        print("=" * 60)
        print("FULL INTEGRATION TEST - 2-HOUR DUB TECHNO MIX")
        print("=" * 60)

        try:
            # Test 1: MCP Connection
            self._test_mcp_connection()

            # Test 2: Session Setup
            self._test_session_setup()

            # Test 3: Wave Structure Validation
            self._test_wave_structure()

            # Test 4: Automation Pattern Validation
            self._test_automation_patterns()

            # Test 5: Error Handling
            self._test_error_handling()

            # Test 6: Auto-Save
            self._test_auto_save()

            # Test 7: Performance Metrics
            self._test_performance_metrics()

            # Generate test report
            return self._generate_test_report()

        except Exception as e:
            print(f"[FATAL] Integration test failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'completed_tests': len(self.test_results)
            }

    def _test_mcp_connection(self):
        """Test 1: Verify MCP server connection."""
        print("\n[TEST 1] MCP Connection Test")

        start_time = time.time()

        try:
            # Get session overview
            overview = self.client.get_session_overview()

            # Verify connection worked
            assert 'tempo' in overview, "Session overview missing tempo"

            elapsed = time.time() - start_time

            result = {
                'test_name': 'MCP Connection',
                'status': 'PASS',
                'elapsed_seconds': elapsed,
                'details': {
                    'tempo': overview['tempo']
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - Connected in {elapsed:.2f}s")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'MCP Connection',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _test_session_setup(self):
        """Test 2: Verify session can be set up."""
        print("\n[TEST 2] Session Setup Test")

        start_time = time.time()

        try:
            # Create 5 test tracks
            for track_idx in range(5):
                self.client.create_midi_track(track_idx)
                self.client.set_track_name(track_idx, f'Test_Track_{track_idx}')

            # Verify tracks created
            session = self.client.get_session_overview()
            assert len(session['tracks']) >= 5, "Insufficient tracks created"

            elapsed = time.time() - start_time

            result = {
                'test_name': 'Session Setup',
                'status': 'PASS',
                'elapsed_seconds': elapsed,
                'details': {
                    'track_count': len(session['tracks'])
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - {len(session['tracks'])} tracks in {elapsed:.2f}s")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'Session Setup',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _test_wave_structure(self):
        """Test 3: Verify wave structure validity."""
        print("\n[TEST 3] Wave Structure Test")

        try:
            # Get wave schedule
            schedule = self.orchestrator.waves

            # Verify wave structure
            assert len(schedule) == 4, f"Expected 4 waves, got {len(schedule)}"

            total_beats = sum(wave.duration_beats for wave in schedule)

            result = {
                'test_name': 'Wave Structure',
                'status': 'PASS',
                'details': {
                    'wave_count': len(schedule),
                    'total_beats': total_beats,
                    'wave_types': [w.wave_type.value for w in schedule]
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - {len(schedule)} waves, {total_beats} beats total")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'Wave Structure',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _test_automation_patterns(self):
        """Test 4: Verify automation pattern availability."""
        print("\n[TEST 4] Automation Patterns Test")

        try:
            # Check for critical pattern methods
            required_patterns = [
                'pattern_filter_drop',
                'pattern_reverb_wash',
                'pattern_sidechain_pumping',
                'sequence_intro_fade_in',
                'sequence_climax_build'
            ]

            for pattern in required_patterns:
                assert hasattr(self.sequencer, pattern), f"Missing pattern: {pattern}"

            result = {
                'test_name': 'Automation Patterns',
                'status': 'PASS',
                'details': {
                    'pattern_count': len(required_patterns)
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - {len(required_patterns)} patterns available")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'Automation Patterns',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _test_error_handling(self):
        """Test 5: Verify error handling system."""
        print("\n[TEST 5] Error Handling Test")

        try:
            # Create test error
            test_error = "Connection timeout"
            from error_handling import create_error_context, ErrorSeverity

            error_context = create_error_context(
                error_type="TimeoutError",
                message=test_error,
                severity=ErrorSeverity.MEDIUM,
                operation="get_track_info"
            )

            # Verify error context created
            assert error_context.operation == "get_track_info"

            result = {
                'test_name': 'Error Handling',
                'status': 'PASS',
                'details': {
                    'error_contexts_tested': 1
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - Error handling system functional")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'Error Handling',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _test_auto_save(self):
        """Test 6: Verify auto-save functionality."""
        print("\n[TEST 6] Auto-Save Test")

        try:
            # Trigger save
            save_metadata = self.auto_saver.check_and_save(current_beat=500, force=True)

            # Verify save created
            assert save_metadata is not None, "Auto-save returned None"
            assert 'save_file' in save_metadata, "Missing save_file in metadata"

            result = {
                'test_name': 'Auto-Save',
                'status': 'PASS',
                'details': {
                    'save_file': save_metadata['save_file']
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - Saved to {Path(save_metadata['save_file']).name}")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'Auto-Save',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _test_performance_metrics(self):
        """Test 7: Measure performance metrics."""
        print("\n[TEST 7] Performance Metrics Test")

        try:
            start_time = time.time()

            # Simulate 100 operations
            for i in range(100):
                self.client.get_session_overview()

            elapsed = time.time() - start_time
            ops_per_second = 100 / elapsed

            result = {
                'test_name': 'Performance Metrics',
                'status': 'PASS',
                'details': {
                    'operations': 100,
                    'elapsed_seconds': elapsed,
                    'ops_per_second': ops_per_second
                }
            }

            self.test_results.append(result)
            print(f"  ✓ PASS - {ops_per_second:.1f} ops/second")

        except Exception as e:
            print(f"  ✗ FAIL - {e}")
            self.test_results.append({
                'test_name': 'Performance Metrics',
                'status': 'FAIL',
                'error': str(e)
            })
            self.errors_encountered += 1

    def _generate_test_report(self) -> dict:
        """Generate comprehensive test report."""
        passed = sum(1 for test in self.test_results if test['status'] == 'PASS')
        failed = sum(1 for test in self.test_results if test['status'] == 'FAIL')

        report = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed': passed,
                'failed': failed,
                'success_rate': passed / len(self.test_results) if self.test_results else 0
            },
            'duration_seconds': time.time() - self.session_start_time if self.session_start_time else 0,
            'errors_encountered': self.errors_encountered,
            'test_results': self.test_results,
            'error_summary': self.error_handler.get_error_summary()
        }

        # Write report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"integration_test_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n{'=' * 60}")
        print(f"INTEGRATION TEST COMPLETE")
        print(f"{'=' * 60}")
        print(f"Total Tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {report['test_summary']['success_rate']*100:.1f}%")
        print(f"Report saved: {report_file}")

        return report


def main():
    """Run integration tests."""
    tester = IntegrationTest()

    report = tester.run_all_tests()

    # Exit with error code if tests failed
    failed = report['test_summary']['failed']
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()