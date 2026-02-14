#!/usr/bin/env python3
"""
Integration tests for VST audio analysis system.

Tests complete integration scenarios including:
- Mock MCP server interactions
- Error handling for server failures
- Parameter polling with rules engine integration
- End-to-end rule evaluation workflows
"""

import unittest
import tempfile
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock

# Import fixes for CI environments
import sys

scripts_analysis_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "analysis")
)
if scripts_analysis_path not in sys.path:
    sys.path.insert(0, scripts_analysis_path)

try:
    from poll_plugin_params import ParameterPoller
    from rules_parser import Rule, Condition, Action
    from rules_engine import RulesEngine, RuleEvaluationResult, RulesEngineError
    from responsive_control import ResponsiveController
except ImportError:
    # Fall back to minimal imports for testing
    print("Import error - using minimal imports")

    from test_analysis import MockMCPServer
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Scripts path: {scripts_analysis_path}")
    raise


class TestVSTAudioAnalysisIntegration(unittest.TestCase):
    """Integration tests for complete VST audio analysis workflow."""

    def setUp(self):
        """Set up test environment with mock server."""
        self.mock_server = MockMCPServer()
        self.mock_server.start()
        time.sleep(0.1)  # Give server time to start

    def tearDown(self):
        """Clean up test environment."""
        self.mock_server.stop()

    def test_parameter_poller_with_rules_engine(self):
        """Test ParameterPoller integrated with RulesEngine."""
        # Create mock parameter poller
        poller = ParameterPoller(
            track_index=0, device_index=0, update_rate_hz=10.0, duration_seconds=1.0
        )

        # Mock the get_device_parameters method to return controlled values
        test_parameters = [
            {"index": 0, "name": "Volume", "value": 0.6, "min": 0.0, "max": 1.0},
            {"index": 1, "name": "Pan", "value": 0.5, "min": -1.0, "max": 1.0},
        ]

        def mock_get_device_parameters(self):
            params_data = {"device_name": "TestDevice", "parameters": test_parameters}
            self.readings_count += 1
            return params_data

        poller.get_device_parameters = mock_get_device_parameters

        # Create rules engine with mock server
        rules_engine = RulesEngine(
            host=self.mock_server.host,
            port=self.mock_server.tcp_port,
            track_index=0,
            device_index=0,
            verbose=False,
        )

        # Create simple rule that should fire
        from rules_parser import Rule, Condition, Action

        rule = Rule(
            name="volume_threshold",
            priority=1,
            condition=Condition(
                operator=">", param1="track:0:device:0:param", param2="0.5"
            ),
            action=Action(
                type="set_parameter", params={"parameter_index": 0, "value": 0.8}
            ),
        )

        # Configure mock server response for set_parameter
        self.mock_server.set_response(
            "set_device_parameter", {"status": "success", "result": {}}
        )

        # Test integrated system
        start_time = time.time()
        results = rules_engine.evaluate_and_execute(
            [rule], {"track:0:device:0:param": 0.6}
        )

        # Verify results
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertTrue(result.fired)
        self.assertEqual(result.rule_name, "volume_threshold")
        self.assertIsNone(result.error)

        # Verify the parameter was set via mock server
        log_commands = self.mock_server.get_log()
        set_commands = [
            cmd for cmd in log_commands if cmd.get("type") == "set_device_parameter"
        ]

        self.assertEqual(len(set_commands), 1)
        sent_command = set_commands[0]
        self.assertEqual(sent_command["params"]["parameter_index"], 0)
        self.assertEqual(sent_command["params"]["value"], 0.8)

    def test_parameter_poller_error_handling(self):
        """Test ParameterPoller error handling with mock server."""
        poller = ParameterPoller(
            track_index=0, device_index=0, update_rate_hz=10.0, duration_seconds=1.0
        )

        # Configure mock server to return error
        self.mock_server.set_response(
            "get_device_parameters", {"status": "error", "message": "Device not found"}
        )

        # Should handle error gracefully
        with patch("builtins.print") as mock_print:
            poller.run("test_log.csv")

            # Verify error was logged
            error_calls = [
                call
                for call in mock_print.call_args_list
                if "Device not found" in str(call)
            ]
            self.assertGreater(len(error_calls), 0)

    def test_rules_engine_error_recovery(self):
        """Test RulesEngine error recovery scenarios."""
        rules_engine = RulesEngine(
            host=self.mock_server.host,
            port=self.mock_server.tcp_port,
            track_index=0,
            device_index=0,
            verbose=True,
        )

        # Test socket timeout
        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            mock_sock.connect.return_value = None
            mock_sock.settimeout.side_effect = socket.timeout()

            from rules_parser import Rule, Condition, Action

            rule = Rule(
                name="timeout_test",
                priority=1,
                condition=Condition(
                    operator=">", param1="track:0:volume", param2="0.5"
                ),
                action=Action(type="set_parameter", params={"value": 0.8}),
            )

            with patch("builtins.print") as mock_print:
                results = rules_engine.evaluate_and_execute(
                    [rule], {"track:0:volume": 0.6}
                )

                # Should handle timeout gracefully
                self.assertEqual(len(results), 1)
                result = results[0]
                self.assertFalse(result.fired)
                self.assertIsNotNone(result.error)
                self.assertIn("MCP server timeout", result.error)
                mock_print.assert_any_call(
                    "[ERROR] Rule 'timeout_test': MCP server timeout"
                )

    def test_responsive_controller_integration(self):
        """Test ResponsiveController integration with mock MCP server."""
        # Create controller with mock server
        controller = ResponsiveController(
            host=self.mock_server.host,
            tcp_port=self.mock_server.tcp_port,
            udp_port=self.mock_server.udp_port,
            track_index=0,
            device_index=0,
            update_rate_hz=50.0,
            enable_high_frequency_mode=True,
            verbose=True,
        )

        # Configure mock server responses
        self.mock_server.set_response(
            "get_device_parameters",
            {
                "status": "success",
                "result": {
                    "device_name": "TestDevice",
                    "parameters": [
                        {
                            "index": 0,
                            "name": "Volume",
                            "value": 0.5,
                            "min": 0.0,
                            "max": 1.0,
                        },
                        {
                            "index": 1,
                            "name": "Pan",
                            "value": 0.0,
                            "min": -1.0,
                            "max": 1.0,
                        },
                    ],
                },
            },
        )

        self.mock_server.set_response(
            "set_device_parameter", {"status": "success", "result": {}}
        )

        # Test controller startup
        controller.start()

        # Wait for initialization
        time.sleep(0.5)

        # Test parameter setting
        success = controller.set_parameter("0:0:volume", 0.8)
        self.assertTrue(success)

        # Test high-frequency parameter update
        success = controller.set_parameter_fast("0:0:volume", 0.9)
        self.assertTrue(success)

        # Stop controller
        controller.stop()

    def test_end_to_end_workflow(self):
        """Test complete end-to-end VST audio analysis workflow."""
        # Create all components
        self.mock_server = MockMCPServer()
        self.mock_server.start()
        time.sleep(0.1)

        # 1. Create rules configuration
        rules_content = """
rules:
  - name: "lufs_warning"
    priority: 1
    condition:
      operator: ">"
      param1: "track:0:device:0:param"
      param2: "-8.0"
    action:
      type: "set_parameter"
      params:
        track_index: 0
        device_index: 0
        parameter_index: 0
        value: 1.0
        value_description: "LUFS too low"
  
  - name: "lufs_normalization"
    priority: 2
    condition:
      operator: "<"
      param1: "track:0:device:0:param"
      param2: "-5.0"
    action:
      type: "set_parameter"
      params:
        track_index: 0
        device_index: 0
        parameter_index: 1
        value: 0.8
        value_description: "Normalize to target LUFS"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(rules_content)
            f.flush()

            # 2. Parse rules
            from rules_parser import RulesParser

            parser = RulesParser()
            rules = parser.parse(f.name)

            # 3. Create parameter poller
            poller = ParameterPoller(
                track_index=0,
                device_index=0,
                update_rate_hz=15.0,
                duration_seconds=10.0,
            )

            # 4. Create rules engine
            rules_engine = RulesEngine(
                host=self.mock_server.host,
                port=self.mock_server.tcp_port,
                track_index=0,
                device_index=0,
                verbose=True,
            )

            # Configure mock server parameter responses
            self.mock_server.set_response(
                "get_device_parameters",
                {
                    "status": "success",
                    "result": {
                        "device_name": "TestDevice",
                        "parameters": [
                            {
                                "index": 0,
                                "name": "LUFS",
                                "value": -9.5,
                                "min": -70.0,
                                "max": 5.0,
                            },
                            {
                                "index": 1,
                                "name": "Target",
                                "value": 0.8,
                                "min": 0.0,
                                "max": 1.0,
                            },
                        ],
                    },
                },
            )

            # Configure mock server action responses
            self.mock_server.set_response(
                "set_device_parameter", {"status": "success", "result": {}}
            )

            # 5. Start the workflow
            rules_engine.start(rules_file=f.name, duration_seconds=10.0)

            # Wait for some processing
            time.sleep(2.0)

            # Stop the workflow
            rules_engine.stop()

            # Verify mock server received commands
            all_commands = self.mock_server.get_log()

            # Should have gotten initial parameter query
            param_queries = [
                cmd
                for cmd in all_commands
                if cmd.get("type") == "get_device_parameters"
            ]
            self.assertEqual(len(param_queries), 1)

            # Should have fired lufs_warning rule (LUFS -9.5 < -8.0)
            rule_fires = [
                cmd for cmd in all_commands if cmd.get("type") == "set_device_parameter"
            ]
            self.assertGreater(len(rule_fires), 0)

            # Check that normalization action was sent
            normalize_action = None
            for cmd in rule_fires:
                if "LUFS too low" in str(cmd):
                    normalize_action = cmd

            self.assertIsNotNone(normalize_action)
            self.assertEqual(normalize_action["params"]["parameter_index"], 0)
            self.assertEqual(normalize_action["params"]["value"], 1.0)

    def test_error_scenarios(self):
        """Test various error handling scenarios."""
        # Test plugin not found during parameter polling
        self.mock_server.set_response(
            "get_device_parameters", {"status": "error", "message": "Plugin not found"}
        )

        poller = ParameterPoller(
            track_index=0, device_index=0, update_rate_hz=10.0, duration_seconds=1.0
        )

        with patch("builtins.print") as mock_print:
            with self.assertRaises(SystemExit) as cm:
                poller.run("test.csv")

            self.assertEqual(cm.exception.code, 1)
            mock_print.assert_any_call("[ERROR] Ableton error: Plugin not found")

        # Test rule with invalid condition
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("invalid_yaml: [")
            f.flush()

            from rules_parser import RulesParser

            with self.assertRaises(RulesParseError):
                RulesParser().parse(f.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
