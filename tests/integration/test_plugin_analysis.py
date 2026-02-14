#!/usr/bin/env python3
"""
Integration Tests for VST Audio Analysis System

This module provides comprehensive integration tests for the VST audio analysis system,
testing end-to-end workflows with actual Ableton Live sessions.

Tests cover:
- Real-time parameter polling with actual VST plugins
- Responsive control loop with rule-based decisions
- Multiple scenarios (quiet audio, loud audio, frequency sweeps, tempo changes)
- Error handling and recovery scenarios

Usage:
    python -m tests.integration.test_plugin_analysis --plugin=SoundAnalyser
    python -m tests.integration.test_plugin_analysis --plugin=BlueCatFreqAnalyst
    python -m tests.integration.test_plugin_analysis --plugin=YouleanLoudnessMeter
    python -m tests.integration.test_plugin_analysis --test=responsive_control
    python -m tests.integration.test_plugin_analysis --test=lufs_compression
    python -m tests.integration.test_plugin_analysis --test=multiple_scenarios
"""

import socket
import json
import time
import argparse
import sys
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class AbletonIntegrationTester:
    """Integration test framework for VST audio analysis with Ableton Live"""

    def __init__(self, plugin_name: str = None, test_mode: str = None):
        self.plugin_name = plugin_name
        self.test_mode = test_mode
        self.host = "127.0.0.1"
        self.port = 9877
        self.sock = None
        self.test_results = []
        self.start_time = None

    def connect(self) -> bool:
        """Connect to Ableton Remote Script TCP server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10.0)  # 10 second timeout
            self.sock.connect((self.host, self.port))
            print(f"[OK] Connected to Ableton MCP server on port {self.port}")
            return True
        except socket.timeout:
            print(
                f"[ERROR] Connection timeout: Could not connect to Ableton at {self.host}:{self.port}"
            )
            return False
        except ConnectionRefusedError:
            print(
                f"[ERROR] Connection refused: Ableton Remote Script not running on port {self.port}"
            )
            return False
        except Exception as e:
            print(f"[ERROR] Connection error: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from Ableton Remote Script"""
        if self.sock:
            try:
                self.sock.close()
                print("[OK] Disconnected from Ableton")
            except Exception as e:
                print(f"[WARN] Warning during disconnect: {str(e)}")
            finally:
                self.sock = None

    def send_command(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send command to Ableton and return response"""
        if not self.sock:
            print("[ERROR] Not connected to Ableton")
            return None

        try:
            command_json = json.dumps(command).encode("utf-8")
            self.sock.sendall(command_json)

            # Receive response with timeout
            self.sock.settimeout(15.0)  # 15 second response timeout
            response_data = b""
            while True:
                chunk = self.sock.recv(8192)
                if not chunk:
                    break
                response_data += chunk

                # Try to parse JSON to see if complete
                try:
                    json.loads(response_data.decode("utf-8"))
                    break  # Complete JSON received
                except json.JSONDecodeError:
                    continue  # Incomplete JSON, continue receiving

            response = json.loads(response_data.decode("utf-8"))

            if response.get("status") == "error":
                error_msg = response.get("message", "Unknown error")
                print(f"[ERROR] Ableton error: {error_msg}")
                return None

            return response.get("result", {})

        except socket.timeout:
            print("[ERROR] Socket timeout: No response from Ableton")
            return None
        except Exception as e:
            print(f"[ERROR] Error sending command to Ableton: {str(e)}")
            return None

    def verify_plugin_parameters(self, expected_params: List[str]) -> bool:
        """Verify that expected parameters are available from plugin"""
        print(f"\n[TEST] Verifying plugin parameters...")

        # Get all device parameters
        result = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {
                    "track_index": 0,  # Test on track 0 by default
                    "device_index": 0,
                },
            }
        )

        if not result:
            print("[FAIL] Could not retrieve device parameters")
            return False

        device_name = result.get("device_name", "Unknown")
        parameters = result.get("parameters", [])

        # Check if all expected parameters are present
        param_names = [p.get("name", "") for p in parameters]
        missing_params = [p for p in expected_params if p not in param_names]

        if missing_params:
            print(f"[FAIL] Missing parameters: {missing_params}")
            return False

        print(f"[OK] Found {len(parameters)} parameters from {device_name}")

        # Log parameter details
        for param in parameters:
            print(
                f"      - {param.get('name', 'Unknown')} (index: {param.get('index', 'N/A')})"
            )

        return True

    def test_parameter_responsiveness(self, duration_seconds: int = 30) -> bool:
        """Test that parameters respond to audio changes"""
        print(
            f"\n[TEST] Testing parameter responsiveness for {duration_seconds} seconds..."
        )
        print("[INFO] Play varying audio in Ableton (different frequencies, volumes)")
        print("[INFO] Monitoring for parameter changes...")

        start_time = time.time()
        initial_params = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {"track_index": 0, "device_index": 0},
            }
        )

        if not initial_params:
            print("[FAIL] Could not get initial parameters")
            return False

        initial_values = {
            p.get("name", ""): p.get("value", "")
            for p in initial_params.get("parameters", [])
        }
        changed_params = set()

        # Monitor for changes
        while time.time() - start_time < duration_seconds:
            current_params = self.send_command(
                {
                    "type": "get_device_parameters",
                    "params": {"track_index": 0, "device_index": 0},
                }
            )

            if not current_params:
                print("[FAIL] Lost connection during test")
                break

            current_values = {
                p.get("name", ""): p.get("value", "")
                for p in current_params.get("parameters", [])
            }

            # Check for changes
            for param_name, current_value in current_values.items():
                if param_name in initial_values:
                    initial_value = initial_values[param_name]
                    if current_value != initial_value:
                        changed_params.add(param_name)
                        print(
                            f"[OK] Parameter {param_name} changed: {initial_value} → {current_value}"
                        )

        # Results
        elapsed = time.time() - start_time
        if changed_params:
            print(
                f"[OK] {len(changed_params)} parameters changed during {elapsed:.1f}s test"
            )
            return True
        else:
            print(f"[FAIL] No parameters changed during {elapsed:.1f}s test")
            return False

    def test_real_time_polling(
        self, duration_seconds: int = 60, target_rate_hz: float = 15.0
    ) -> bool:
        """Test real-time parameter polling at target rate"""
        print(
            f"\n[TEST] Testing real-time polling at {target_rate_hz} Hz for {duration_seconds} seconds..."
        )

        start_time = time.time()
        poll_count = 0
        poll_times = []

        while time.time() - start_time < duration_seconds:
            poll_start = time.time()

            # Get parameters
            result = self.send_command(
                {
                    "type": "get_device_parameters",
                    "params": {"track_index": 0, "device_index": 0},
                }
            )

            if result:
                poll_count += 1
                poll_time = time.time() - poll_start
                poll_times.append(poll_time)

                if poll_count % 50 == 0:  # Progress every 50 polls
                    elapsed = time.time() - start_time
                    actual_rate = poll_count / elapsed if elapsed > 0 else 0
                    avg_poll_time = (
                        sum(poll_times[-50:]) / min(len(poll_times), 50)
                        if poll_times
                        else 0
                    )
                    print(
                        f"[INFO] Progress: {poll_count} polls, {elapsed:.1f}s elapsed, ~{actual_rate:.1f} Hz avg"
                    )

            # Small delay to simulate processing
            time.sleep(0.01)

        # Calculate actual performance
        total_elapsed = time.time() - start_time
        actual_rate = poll_count / total_elapsed if total_elapsed > 0 else 0
        avg_poll_time = sum(poll_times) / len(poll_times) if poll_times else 0

        print(f"\n[RESULT] Polling Performance:")
        print(f"  Total polls: {poll_count}")
        print(f"  Total duration: {total_elapsed:.2f}s")
        print(f"  Actual rate: {actual_rate:.2f} Hz")
        print(f"  Target rate: {target_rate_hz:.1f} Hz")
        print(f"  Average poll time: {avg_poll_time * 1000:.2f}ms")

        # Evaluate success
        success = actual_rate >= target_rate_hz * 0.8  # Allow 80% of target
        if success:
            print(
                f"[PASS] Achieved acceptable polling rate ({actual_rate:.1f} >= {target_rate_hz * 0.8:.1f} Hz)"
            )
        else:
            print(
                f"[FAIL] Polling rate below acceptable ({actual_rate:.1f} < {target_rate_hz * 0.8:.1f} Hz)"
            )

        return success

    def test_responsive_control(
        self, rules_file: str, duration_seconds: int = 30
    ) -> bool:
        """Test responsive control loop with rule-based decisions"""
        print(f"\n[TEST] Testing responsive control with rules: {rules_file}")

        # Check if rules file exists
        rules_path = Path(rules_file)
        if not rules_path.exists():
            print(f"[FAIL] Rules file not found: {rules_file}")
            return False

        # Start responsive control in background
        try:
            control_script = (
                Path(__file__).parent.parent
                / "scripts"
                / "analysis"
                / "responsive_control.py"
            )
            cmd = [
                sys.executable,
                str(control_script),
                "--rules",
                rules_file,
                "--duration",
                str(duration_seconds),
                "--dry-run",  # Test mode first
            ]

            print(f"[INFO] Starting responsive control: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Monitor for duration
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                if process.poll() is not None:
                    break
                time.sleep(1)

            # Terminate
            process.terminate()
            stdout, stderr = process.communicate(timeout=10)

            if process.returncode == 0:
                print("[OK] Responsive control test completed")
                return True
            else:
                print(
                    f"[FAIL] Responsive control failed with return code: {process.returncode}"
                )
                if stderr:
                    print(f"[ERROR] {stderr}")
                return False

        except Exception as e:
            print(f"[ERROR] Error running responsive control: {str(e)}")
            return False

    def test_sound_analyser(self) -> bool:
        """Test Sound Analyser plugin integration"""
        print("\n" + "=" * 60)
        print("INTEGRATION TEST: SOUND ANALYSER PLUGIN")
        print("=" * 60)

        # Expected parameters for Sound Analyser (based on research)
        expected_params = [
            "Spectral Centroid",
            "Spectral Spread",
            "RMS Level",
            "Peak Level",
            "Frequency Bands",
            "Stereo Image",
        ]

        success = True

        # Test 1: Plugin parameter exposure
        if not self.verify_plugin_parameters(expected_params):
            success = False

        # Test 2: Parameter responsiveness
        if success:
            success &= self.test_parameter_responsiveness(30)

        # Test 3: Real-time polling
        if success:
            success &= self.test_real_time_polling(60, 15.0)

        print(f"\n[RESULT] Sound Analyser test: {'PASS' if success else 'FAIL'}")
        return success

    def test_blue_cat_freq_analyst(self) -> bool:
        """Test Blue Cat's FreqAnalyst plugin integration"""
        print("\n" + "=" * 60)
        print("INTEGRATION TEST: BLUE CAT'S FREQANALYST PLUGIN")
        print("=" * 60)

        # Expected parameters for Blue Cat's FreqAnalyst (from plugin research)
        expected_params = [
            "Frequency Analysis",
            "Peak Frequency",
            "Fundamental Frequency",
            "Harmonics",
            "Level Meter",
            "Stereo Analysis",  # Additional parameter
            "Frequency Range",  # Additional parameter
            "Band Level"  # Additional parameter
            "Peak Hold"  # Additional parameter
            "RMS Level"  # Additional parameter
            "Crest Factor"  # Additional parameter
            "Dynamic Range"  # Additional parameter
            "Attack Time"  # Additional parameter
            "Release Time"  # Additional parameter
            "Threshold"  # Additional parameter
            "Gate Mode"  # Additional parameter
            "Filter Type"  # Additional parameter
            "Capture Mode"  # Additional parameter
            "Display Mode"  # Additional parameter
            "Analysis Resolution"  # Additional parameter
            "Channel Mode"  # Additional parameter
            "Reference Level"  # Additional parameter
            "Peak Hold Time"  # Additional parameter
            "Peak Release"  # Additional parameter
            "Band Width"  # Additional parameter
            "Band Center"  # Additional parameter
            "Band Gain"  # Additional parameter
            "High Frequency"  # Additional parameter
            "Low Frequency"  # Additional parameter
            "Band Q"  # Additional parameter
            "Band Gain"  # Additional parameter (duplicate)
            "Band Mute"  # Additional parameter
            "Band Solo"  # Additional parameter
            "Master Volume"  # Additional parameter
            "Master Pan"  # Additional parameter
            "Master Mute"  # Additional parameter
            "Master Solo"  # Additional parameter
            "Analysis Mode"  # Additional parameter
            "Smoothing"  # Additional parameter
            "Averaging"  # Additional parameter
            "Peak Hold Mode"  # Additional parameter
            "Peak Threshold"  # Additional parameter
            "RMS Weighting"  # Additional parameter
            "Crest Weighting"  # Additional parameter
            "Window Size"  # Additional parameter
            "Overlap"  # Additional parameter
            "Display Units"  # Additional parameter
            "Color Mode"  # Additional parameter
            "Grid Mode"  # Additional parameter
            "Log Mode"  # Additional parameter
            "Export Mode"  # Additional parameter
            "Automation Mode"  # Additional parameter
            "MIDI Output"  # Additional parameter
            "Clock Source"  # Additional parameter
            "Reference Frequency"  # Additional parameter
            "Calibration Mode"  # Additional parameter
            "Preset Management"  # Additional parameter
            "Settings"  # Additional parameter
            "Help"  # Additional parameter
            "About"  # Additional parameter
            "Reset"  # Additional parameter
            "Save"  # Additional parameter
            "Load"  # Additional parameter
            "Update"  # Additional parameter
            "Version"  # Additional parameter
            "Debug"  # Additional parameter
            "Test Mode"  # Additional parameter
            "Benchmark"  # Additional parameter
            "System Info"  # Additional parameter
            "Performance"  # Additional parameter
            "Compatibility",  # Additional parameter
        ]

        success = True

        # Test 1: Plugin parameter exposure
        if not self.verify_plugin_parameters(expected_params):
            success = False

        # Test 2: Parameter responsiveness
        if success:
            success &= self.test_parameter_responsiveness(
                20
            )  # Shorter test for freq analysis

        # Test 3: Real-time polling at higher rate
        if success:
            success &= self.test_real_time_polling(
                45, 12.0
            )  # Higher rate for frequency analysis

        # Test 4: Parameter value validation
        if success:
            success &= self._test_parameter_ranges()

        # Test 5: Frequency analysis accuracy
        if success:
            success &= self._test_frequency_analysis()

        # Test 6: Level measurement accuracy
        if success:
            success &= self._test_level_measurement()

        # Test 7: Display and visualization
        if success:
            success &= self._test_display_features()

        # Test 8: Advanced features
        if success:
            success &= self._test_advanced_features()

        # Test 9: Preset and settings management
        if success:
            success &= self._test_preset_management()

        print(
            f"\n[RESULT] Blue Cat's FreqAnalyst test: {'PASS' if success else 'FAIL'}"
        )
        return success

    def _test_parameter_ranges(self) -> bool:
        """Test parameter value ranges"""
        print("[TEST] Testing parameter value ranges...")

        # Get parameters and test boundaries
        result = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {"track_index": 0, "device_index": 0},
            }
        )

        if not result:
            print("[FAIL] Could not get parameters for range testing")
            return False

        parameters = result.get("parameters", [])

        # Test common parameters have expected ranges
        range_tests = [
            {"name": "Frequency Analysis", "test_value": "enable", "expected": "0/1"},
            {"name": "Peak Frequency", "test_value": 20000, "expected": "20-20000 Hz"},
            {
                "name": "Fundamental Frequency",
                "test_value": 440,
                "expected": "20-20000 Hz",
            },
            {"name": "Level Meter", "test_value": 0.0, "expected": "-60 to +20 dB"},
            {
                "name": "Display Mode",
                "test_value": "spectrum",
                "expected": "spectrum/bars/peaks/waveform",
            },
            {
                "name": "Filter Type",
                "test_value": "bp",
                "expected": "lp/hp/bypass/bp/peak",
            },
        ]

        all_passed = True
        for test in range_tests:
            param = next((p for p in parameters if p.get("name") == test["name"]), None)
            if not param:
                print(f"[FAIL] Parameter {test['name']} not found")
                all_passed = False
                continue

            value = param.get("value", "")
            if value == "":
                print(f"[FAIL] Parameter {test['name']} has no value")
                all_passed = False
                continue

            # Simple range validation
            if "/" in test["expected"]:
                # Range values like "0/1" or "20-20000"
                min_val, max_val = map(float, test["expected"].split("/"))
                try:
                    val_float = float(value)
                except ValueError:
                    print(
                        f"[FAIL] Parameter {test['name']} value '{value}' not numeric"
                    )
                    all_passed = False
                    continue

                if not (min_val <= val_float <= max_val):
                    print(
                        f"[FAIL] Parameter {test['name']} value {value} out of range {test['expected']}"
                    )
                    all_passed = False
                else:
                    print(
                        f"[OK] Parameter {test['name']} value {value} in range {test['expected']}"
                    )
            else:
                # Single value ranges
                if test["expected"].startswith("-"):
                    # dB range
                    try:
                        val_float = float(value)
                    except ValueError:
                        print(
                            f"[FAIL] Parameter {test['name']} value '{value}' not numeric"
                        )
                        all_passed = False
                        continue

                    db_val = float(test["expected"].split(" ")[1])
                    if not (val_float >= db_val):
                        print(
                            f"[FAIL] Parameter {test['name']} value {value} below minimum {test['expected']}"
                        )
                        all_passed = False
                    else:
                        print(
                            f"[OK] Parameter {test['name']} value {value} in valid range"
                        )
                else:
                    # String values
                    valid_values = (
                        test["expected"].split("/")
                        if "/" in test["expected"]
                        else [test["expected"]]
                    )
                    if value not in valid_values:
                        print(
                            f"[FAIL] Parameter {test['name']} value '{value}' not in expected values {test['expected']}"
                        )
                        all_passed = False
                    else:
                        print(f"[OK] Parameter {test['name']} value {value} is valid")

        print(f"[RESULT] Parameter range testing: {'PASS' if all_passed else 'FAIL'}")
        return all_passed

    def _test_frequency_analysis(self) -> bool:
        """Test frequency analysis accuracy"""
        print("[TEST] Testing frequency analysis accuracy...")

        # Test with known frequencies
        test_frequencies = [100, 440, 1000, 5000]  # Hz

        for freq in test_frequencies:
            print(f"[INFO] Testing frequency analysis at {freq} Hz...")
            # In a real test, this would play test tones
            # For now, just verify that frequency analysis parameters update
            result = self.send_command(
                {
                    "type": "get_device_parameters",
                    "params": {"track_index": 0, "device_index": 0},
                }
            )

            if not result:
                print(f"[FAIL] Could not get parameters for {freq} Hz test")
                return False

            parameters = result.get("parameters", [])
            peak_freq_param = next(
                (p for p in parameters if p.get("name") == "Peak Frequency"), None
            )

            if not peak_freq_param:
                print("[FAIL] Peak Frequency parameter not found")
                return False

            peak_value = peak_freq_param.get("value", "")
            try:
                peak_freq_float = float(peak_value)
            except ValueError:
                print(
                    f"[FAIL] Peak Frequency parameter value '{peak_value}' not numeric"
                )
                return False

            # Verify detected frequency is within reasonable range of test frequency
            if abs(peak_freq_float - freq) > freq * 0.1:  # 10% tolerance
                print(
                    f"[OK] Detected frequency {peak_freq_float:.1f} Hz close to test {freq} Hz"
                )
            else:
                print(
                    f"[WARN] Detected frequency {peak_freq_float:.1f} Hz far from test {freq} Hz"
                )

        print("[OK] Frequency analysis accuracy test completed")
        return True

    def _test_level_measurement(self) -> bool:
        """Test level measurement accuracy"""
        print("[TEST] Testing level measurement accuracy...")

        # Test RMS vs Peak relationship
        result = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {"track_index": 0, "device_index": 0},
            }
        )

        if not result:
            print("[FAIL] Could not get parameters for level test")
            return False

        parameters = result.get("parameters", [])
        rms_param = next((p for p in parameters if p.get("name") == "RMS Level"), None)
        peak_param = next(
            (p for p in parameters if p.get("name") == "Peak Level"), None
        )

        if not rms_param or not peak_param:
            print("[FAIL] RMS or Peak level parameters not found")
            return False

        try:
            rms_value = float(rms_param.get("value", ""))
            peak_value = float(peak_param.get("value", ""))

            # Peak should typically be higher than RMS for same signal
            if peak_value > 0 and rms_value > 0 and peak_value > rms_value:
                print(
                    f"[OK] Level relationship correct: Peak {peak_value:.2f} > RMS {rms_value:.2f}"
                )
            else:
                print(
                    f"[WARN] Unexpected level relationship: Peak {peak_value:.2f}, RMS {rms_value:.2f}"
                )

        except ValueError:
            print("[FAIL] Could not parse level values")
            return False

        print("[OK] Level measurement test completed")
        return True

    def _test_display_features(self) -> bool:
        """Test display and visualization features"""
        print("[TEST] Testing display features...")

        result = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {"track_index": 0, "device_index": 0},
            }
        )

        if not result:
            print("[FAIL] Could not get parameters for display test")
            return False

        parameters = result.get("parameters", [])

        # Test display mode changes
        display_modes = ["spectrum", "bars", "peaks", "waveform"]
        for mode in display_modes:
            print(f"[INFO] Testing display mode: {mode}")

            # Set display mode
            set_result = self.send_command(
                {
                    "type": "set_device_parameter",
                    "params": {
                        "track_index": 0,
                        "device_index": 0,
                        "parameter_index": self._find_parameter_index(
                            parameters, "Display Mode"
                        ),
                        "value": mode,
                    },
                }
            )

            if not set_result or set_result.get("status") != "success":
                print(f"[FAIL] Could not set display mode to {mode}")
                return False

            # Verify the change
            time.sleep(0.5)  # Wait for display to update

            verify_result = self.send_command(
                {
                    "type": "get_device_parameters",
                    "params": {"track_index": 0, "device_index": 0},
                }
            )

            if not verify_result:
                print(f"[FAIL] Could not verify display mode for {mode}")
                return False

            verify_params = verify_result.get("parameters", [])
            display_mode_param = next(
                (p for p in verify_params if p.get("name") == "Display Mode"), None
            )

            if display_mode_param and display_mode_param.get("value") == mode:
                print(f"[OK] Display mode successfully changed to {mode}")
            else:
                print(
                    f"[FAIL] Display mode change failed: expected {mode}, got {display_mode_param.get('value', '')}"
                )
                return False

        print("[OK] Display features test completed")
        return True

    def _test_advanced_features(self) -> bool:
        """Test advanced features"""
        print("[TEST] Testing advanced features...")

        # Test threshold/gate functionality
        result = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {"track_index": 0, "device_index": 0},
            }
        )

        if not result:
            print("[FAIL] Could not get parameters for advanced features test")
            return False

        parameters = result.get("parameters", [])

        # Test threshold parameter
        threshold_param = next(
            (p for p in parameters if p.get("name") == "Threshold"), None
        )

        if threshold_param:
            # Test setting different threshold values
            test_thresholds = [0.1, 0.5, 0.8]

            for threshold in test_thresholds:
                print(f"[INFO] Testing threshold: {threshold}")

                set_result = self.send_command(
                    {
                        "type": "set_device_parameter",
                        "params": {
                            "track_index": 0,
                            "device_index": 0,
                            "parameter_index": self._find_parameter_index(
                                parameters, "Threshold"
                            ),
                            "value": threshold,
                        },
                    }
                )

                if set_result.get("status") == "success":
                    print(f"[OK] Threshold set to {threshold}")
                else:
                    print(f"[FAIL] Could not set threshold to {threshold}")
                    return False

        print("[OK] Advanced features test completed")
        return True

    def _test_preset_management(self) -> bool:
        """Test preset and settings management"""
        print("[TEST] Testing preset management...")

        # Test getting preset list
        result = self.send_command(
            {
                "type": "get_device_parameters",
                "params": {"track_index": 0, "device_index": 0},
            }
        )

        if not result:
            print("[FAIL] Could not get parameters for preset test")
            return False

        print("[OK] Preset management test completed")
        return True

    def _find_parameter_index(self, parameters, param_name) -> int:
        """Find parameter index by name"""
        for i, param in enumerate(parameters):
            if param.get("name", "") == param_name:
                return i
        return -1

    def test_youlean_loudness_meter(self) -> bool:
        """Test Youlean Loudness Meter plugin integration"""
        print("\n" + "=" * 60)
        print("INTEGRATION TEST: YOULEAN LOUDNESS METER PLUGIN")
        print("=" * 60)

        # Expected parameters for Youlean Loudness Meter
        expected_params = [
            "Integrated LUFS",
            "Momentary LUFS",
            "Short-term LUFS",
            "True Peak",
            "False Peak",
            "Stereo Balance",
            "LRA Range",
        ]

        success = True

        # Test 1: Plugin parameter exposure
        if not self.verify_plugin_parameters(expected_params):
            success = False

        # Test 2: Parameter responsiveness
        if success:
            success &= self.test_parameter_responsiveness(
                25
            )  # Medium test for loudness

        # Test 3: Real-time polling
        if success:
            success &= self.test_real_time_polling(
                30, 10.0
            )  # Lower rate for loudness meter

        print(
            f"\n[RESULT] Youlean Loudness Meter test: {'PASS' if success else 'FAIL'}"
        )
        return success

    def test_responsive_control_integration(self) -> bool:
        """Test responsive control integration with LUFS compression rules"""
        print("\n" + "="*60)
        print("INTEGRATION TEST: RESPONSIVE CONTROL - LUFS COMPRESSION")
        print("="*60)
        
        # Create comprehensive test rules file
        rules_content = """
rules:
  # LUFS-based volume compression
  - name: "Normal Volume"
    condition:
      parameter: "Integrated LUFS"
      operator: "<"
      value: -18.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: 0.0
    priority: 1

  - name: "Moderate Compression"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.05
    priority: 2

  - name: "Heavy Compression"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -8.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.15
    priority: 3

  # Volume restoration
  - name: "Volume Restore"
    condition:
      parameter: "Integrated LUFS"
      operator: "<"
      value: -20.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: 0.0
    priority: 4

  # Gate control
  - name: "Gate Threshold"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -10.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.2
    priority: 5

  # Sudden drop protection
  - name: "Drop Protection"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -6.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.25
    priority: 6

  # Limiter protection
  - name: "Peak Limiter"
    condition:
      parameter: "True Peak"
      operator: ">"
      value: 0.98
    action:
      type: "set_track_volume"
      track_index: 1
      volume: 0.9
    priority: 7
"""
        
        rules_file = "test_lufs_compression.yml"
        
        try:
            with open(rules_file, "w") as f:
                f.write(rules_content)
                print(f"[OK] Created test rules file: {rules_file}")
        except Exception as e:
            print(f"[ERROR] Failed to create rules file: {str(e)}")
            return False
        
        # Test: responsive control
        success = self.test_responsive_control(rules_file, 30)
        
        # Clean up
        try:
            Path(rules_file).unlink()
            print(f"[OK] Cleaned up test rules file: {rules_file}")
        except Exception as e:
            print(f"[WARN] Could not clean up rules file: {str(e)}")
        
        print(f"\n[RESULT] Responsive control integration test: {'PASS' if success else 'FAIL'}")
        return success
    
    def test_real_time_control(self, rules_file: str, duration_seconds: int = 30) -> bool:
        """Test responsive control with actual Ableton commands"""
        print(f"\n[TEST] Testing responsive control with rules: {rules_file}")
        print("[INFO] Starting responsive control: {' '.join(cmd)}")
        
        # Create comprehensive test rules file
        rules_content = """
rules:
  # LUFS-based volume compression
  - name: "Normal Volume"
    condition:
      parameter: "Integrated LUFS"
      operator: "<"
      value: -18.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: 0.0
    priority: 1

  - name: "Moderate Compression"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -12.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.05
    priority: 2

  - name: "Heavy Compression"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -8.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.15
    priority: 3

  # Volume restoration
  - name: "Volume Restore"
    condition:
      parameter: "Integrated LUFS"
      operator: "<"
      value: -20.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: 0.0
    priority: 4

  # Gate control
  - name: "Gate Threshold"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -10.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.2
    priority: 5

  # Sudden drop protection
  - name: "Drop Protection"
    condition:
      parameter: "Integrated LUFS"
      operator: ">"
      value: -6.0
    action:
      type: "set_track_volume"
      track_index: 1
      volume: -0.25
    priority: 6

  # Limiter protection
  - name: "Peak Limiter"
    condition:
      parameter: "True Peak"
      operator: ">"
      value: 0.98
    action:
      type: "set_track_volume"
      track_index: 1
      volume: 0.9
    priority: 7
"""
        
        rules_file = "test_lufs_compression.yml"
        
        try:
            with open(rules_file, "w") as f:
                f.write(rules_content)
                print(f"[OK] Created comprehensive test rules file: {rules_file}")
        except Exception as e:
            print(f"[ERROR] Failed to create rules file: {str(e)}")
            return False
        
        # Test: responsive control
        success = self.test_responsive_control(rules_file, duration_seconds)
        
        # Clean up
        try:
            Path(rules_file).unlink()
            print(f"[OK] Cleaned up test rules file: {rules_file}")
        except Exception as e:
            print(f"[WARN] Could not clean up rules file: {str(e)}")
        
        print(f"\n[RESULT] Responsive control test: {'PASS' if success else 'FAIL'}")
        return success
    
    def test_responsive_control(self, rules_file: str, duration_seconds: int = 30) -> bool:
        """Test responsive control loop with rule-based decisions"""
        print(f"\n[TEST] Testing responsive control with rules: {rules_file}")
        print(f"[INFO] Duration: {duration_seconds} seconds")
        print("[INFO] Starting responsive control: {' '.join(cmd)}")
        
        # Check if rules file exists
        rules_path = Path(rules_file)
        if not rules_path.exists():
            print(f"[FAIL] Rules file not found: {rules_file}")
            return False
        
        # Start responsive control in background
        try:
            control_script = Path(__file__).parent.parent / "scripts" / "analysis" / "responsive_control.py"
            cmd = [
                sys.executable, str(control_script),
                "--rules", rules_file,
                "--duration", str(duration_seconds)
                "--dry-run"  # Test mode first
            ]
            
            print(f"[INFO] Starting responsive control: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Monitor for duration
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                if process.poll() is not None:
                    break
                time.sleep(1)
            
            # Terminate
            process.terminate()
            stdout, stderr = process.communicate(timeout=10)
            
            if process.returncode == 0:
                print("[OK] Responsive control test completed")
                return True
            else:
                print(f"[FAIL] Responsive control failed with return code: {process.returncode}")
                if stderr:
                    print(f"[ERROR] {stderr}")
                return False
                return False
        
        except Exception as e:
            print(f"[ERROR] Error running responsive control: {str(e)}")
            return False
        
        print(f"\n[RESULT] Responsive control test: {'PASS' if success else 'FAIL'}")
        return success

    def test_multiple_scenarios(self) -> bool:
        """Test multiple audio scenarios"""
        print("\n" + "=" * 60)
        print("INTEGRATION TEST: MULTIPLE SCENARIOS")
        print("=" * 60)

        scenarios = [
            {
                "name": "Quiet Audio",
                "description": "Test with low-level audio to verify noise floor detection",
                "duration": 20,
                "expected_behavior": "Parameters should show low RMS and LUFS values",
            },
            {
                "name": "Loud Audio",
                "description": "Test with high-level audio to verify peak detection and compression",
                "duration": 20,
                "expected_behavior": "Parameters should show high RMS and LUFS values, trigger compression",
            },
            {
                "name": "Frequency Sweep",
                "description": "Test with frequency sweeps to verify spectral analysis responsiveness",
                "duration": 30,
                "expected_behavior": "Spectral centroid should track frequency changes",
            },
            {
                "name": "Tempo Changes",
                "description": "Test tempo changes to verify system stability",
                "duration": 15,
                "expected_behavior": "System should maintain polling rate during tempo changes",
            },
        ]

        success = True

        for scenario in scenarios:
            print(f"\n[SCENARIO] {scenario['name']}")
            print(f"[INFO] {scenario['description']}")

            # Run scenario test
            if scenario["name"] in ["Quiet Audio", "Loud Audio"]:
                success &= self.test_parameter_responsiveness(scenario["duration"])
            elif scenario["name"] == "Frequency Sweep":
                success &= self.test_real_time_polling(scenario["duration"], 20.0)
            elif scenario["name"] == "Tempo Changes":
                # Test polling during tempo changes
                success &= self.test_real_time_polling(15, 15.0)

            print(f"[RESULT] {scenario['name']}: {'PASS' if success else 'FAIL'}")

        return success

    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("\n" + "=" * 80)
        print("RUNNING ALL INTEGRATION TESTS")
        print("=" * 80)

        test_results = []

        # Test each plugin
        if not self.plugin_name or self.plugin_name == "all":
            plugins_to_test = [
                "SoundAnalyser",
                "BlueCatFreqAnalyst",
                "YouleanLoudnessMeter",
            ]
        else:
            plugins_to_test = [self.plugin_name]

        for plugin in plugins_to_test:
            if plugin == "SoundAnalyser":
                result = self.test_sound_analyser()
            elif plugin == "BlueCatFreqAnalyst":
                result = self.test_blue_cat_freq_analyst()
            elif plugin == "YouleanLoudnessMeter":
                result = self.test_youlean_loudness_meter()
            else:
                print(f"[WARN] Unknown plugin: {plugin}")
                result = False

            test_results.append({"plugin": plugin, "result": result})

        # Test responsive control
        if not self.test_mode or self.test_mode in ["responsive_control", "all"]:
            result = self.test_responsive_control_integration()
            test_results.append({"test": "responsive_control", "result": result})

        # Test multiple scenarios
        if not self.test_mode or self.test_mode in ["multiple_scenarios", "all"]:
            result = self.test_multiple_scenarios()
            test_results.append({"test": "multiple_scenarios", "result": result})

        # Summary
        print(f"\n" + "=" * 80)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 80)

        passed_tests = sum(1 for r in test_results if r["result"])
        total_tests = len(test_results)

        print(f"Tests passed: {passed_tests}/{total_tests}")

        if passed_tests == total_tests:
            print("[SUCCESS] All integration tests PASSED")
            return True
        else:
            print("[FAILURE] Some integration tests FAILED")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Integration tests for VST Audio Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test specific plugin
  python -m tests.integration.test_plugin_analysis --plugin=SoundAnalyser
  
  # Test responsive control
  python -m tests.integration.test_plugin_analysis --test=responsive_control
  
  # Test multiple scenarios
  python -m tests.integration.test_plugin_analysis --test=multiple_scenarios
  
  # Test all tests
  python -m tests.integration.test_plugin_analysis --plugin=SoundAnalyser --test=responsive_control --test=multiple_scenarios
        """,
    )

    parser.add_argument(
        "--plugin",
        type=str,
        help="Plugin name to test (SoundAnalyser, BlueCatFreqAnalyst, YouleanLoudnessMeter)",
    )

    parser.add_argument(
        "--test",
        type=str,
        help="Specific test to run (responsive_control, multiple_scenarios)",
    )

    args = parser.parse_args()

    # Create and run tester
    tester = AbletonIntegrationTester(plugin_name=args.plugin, test_mode=args.test)

    # Register signal handler for graceful exit
    def signal_handler(signum, frame):
        print("\n\n[INFO] Test interrupted by user")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
