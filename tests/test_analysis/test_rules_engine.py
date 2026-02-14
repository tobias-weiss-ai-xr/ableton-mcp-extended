#!/usr/bin/env python3
"""
Unit tests for VST rules engine.

Tests RulesEngine class functionality including:
- Rule evaluation logic for all operators
- Action execution via MCP server
- Parameter polling integration
- Cooldown management
- Error handling for invalid actions
"""

import unittest
import tempfile
import os
import time
from unittest.mock import Mock, patch, MagicMock
from unittest.mock import mock_open
import threading

# Import fixes for CI environments
import sys

# Add the scripts/analysis directory to path for imports
scripts_analysis_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "analysis")
)
if scripts_analysis_path not in sys.path:
    sys.path.insert(0, scripts_analysis_path)

try:
    from rules_engine import RulesEngine, RuleEvaluationResult, RulesEngineError
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Scripts path: {scripts_analysis_path}")
    raise


class TestRulesEngine(unittest.TestCase):
    """Test cases for RulesEngine class."""

    def setUp(self):
        """Set up test environment."""
        self.engine = RulesEngine()

    def test_initialization(self):
        """Test RulesEngine initialization."""
        self.assertEqual(self.engine.host, "localhost")
        self.assertEqual(self.engine.port, 9877)
        self.assertEqual(self.engine.track_index, 0)
        self.assertEqual(self.engine.device_index, 0)
        self.assertFalse(self.engine.verbose)
        self.assertEqual(self.engine.cooldowns, {})

    def test_initialization_with_custom_params(self):
        """Test RulesEngine initialization with custom parameters."""
        engine = RulesEngine(
            host="192.168.1.100", port=9000, track_index=2, device_index=1, verbose=True
        )

        self.assertEqual(engine.host, "192.168.1.100")
        self.assertEqual(engine.port, 9000)
        self.assertEqual(engine.track_index, 2)
        self.assertEqual(engine.device_index, 1)
        self.assertTrue(engine.verbose)

    def test_resolve_value_parameter_reference(self):
        """Test value resolution for parameter references."""
        engine = RulesEngine()

        # Test parameter reference lookup
        parameter_values = {"track:0:device:0:param": -14.5}
        value = engine._resolve_value("track:0:device:0:param", parameter_values)

        self.assertEqual(value, -14.5)

    def test_resolve_value_literal(self):
        """Test value resolution for literal values."""
        engine = RulesEngine()

        # Test literal value lookup
        parameter_values = {"track:0:volume": 0.8}
        value = engine._resolve_value("0.8", parameter_values)

        self.assertEqual(value, 0.8)

    def test_resolve_value_missing_parameter(self):
        """Test value resolution for missing parameter."""
        engine = RulesEngine()

        parameter_values = {"track:0:volume": 0.8}

        with self.assertRaises(RulesEngineError) as cm:
            engine._resolve_value("track:0:missing_param", parameter_values)

        self.assertIn(
            "Parameter reference 'track:0:missing_param' not found", str(cm.exception)
        )

    def test_resolve_value_invalid_literal(self):
        """Test value resolution for invalid literal."""
        engine = RulesEngine()

        parameter_values = {"track:0:volume": 0.8}

        with self.assertRaises(RulesEngineError) as cm:
            engine._resolve_value("invalid_float", parameter_values)

        self.assertIn("Cannot parse 'invalid_float' as float", str(cm.exception))

    def test_evaluate_condition_greater_than(self):
        """Test > operator evaluation."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = ">"
        condition.param1 = "track:0:volume"
        condition.param2 = "0.7"

        parameter_values = {"track:0:volume": 0.8}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_less_than(self):
        """Test < operator evaluation."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "<"
        condition.param1 = "track:0:volume"
        condition.param2 = "0.7"

        parameter_values = {"track:0:volume": 0.6}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_equals(self):
        """Test == operator evaluation."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "=="
        condition.param1 = "track:0:name"
        condition.param2 = "Kick"

        parameter_values = {"track:0:name": "Kick"}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_not_equals(self):
        """Test != operator evaluation."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "!="
        condition.param1 = "track:0:name"
        condition.param2 = "Kick"

        parameter_values = {"track:0:name": "Snare"}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_greater_than_or_equal(self):
        """Test >= operator evaluation."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = ">="
        condition.param1 = "track:0:volume"
        condition.param2 = "0.7"

        parameter_values = {"track:0:volume": 0.7}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_less_than_or_equal(self):
        """Test <= operator evaluation."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "<="
        condition.param1 = "track:0:volume"
        condition.param2 = "0.7"

        parameter_values = {"track:0:volume": 0.7}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_and_operator_all_true(self):
        """Test AND operator with all true conditions."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "AND"
        condition.conditions = [
            Mock(operator=">", param1="track:0:volume", param2="0.5"),
            Mock(operator="<", param1="track:0:pan", param2="0.8"),
        ]

        parameter_values = {"track:0:volume": 0.6, "track:0:pan": 0.9}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_and_operator_one_false(self):
        """Test AND operator with one false condition."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "AND"
        condition.conditions = [
            Mock(operator=">", param1="track:0:volume", param2="0.5"),
            Mock(operator="<", param1="track:0:pan", param2="0.8"),
        ]

        parameter_values = {
            "track:0:volume": 0.4,
            "track:0:pan": 0.9,
        }  # volume condition fails

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertFalse(result)

    def test_evaluate_condition_or_operator_one_true(self):
        """Test OR operator with one true condition."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "OR"
        condition.conditions = [
            Mock(operator=">", param1="track:0:volume", param2="0.5"),
            Mock(operator="<", param1="track:0:pan", param2="0.8"),
        ]

        parameter_values = {
            "track:0:volume": 0.6,
            "track:0:pan": 0.9,
        }  # volume condition true

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_or_operator_all_false(self):
        """Test OR operator with all false conditions."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "OR"
        condition.conditions = [
            Mock(operator=">", param1="track:0:volume", param2="0.5"),
            Mock(operator="<", param1="track:0:pan", param2="0.8"),
        ]

        parameter_values = {
            "track:0:volume": 0.4,
            "track:0:pan": 0.9,
        }  # both conditions false

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertFalse(result)

    def test_evaluate_condition_not_operator_true_condition(self):
        """Test NOT operator with true condition."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "NOT"
        condition.conditions = [
            Mock(operator=">", param1="track:0:volume", param2="0.5")
        ]

        parameter_values = {"track:0:volume": 0.6}  # condition inside NOT is true

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertFalse(result)

    def test_evaluate_condition_not_operator_false_condition(self):
        """Test NOT operator with false condition."""
        engine = RulesEngine()
        condition = Mock()
        condition.operator = "NOT"
        condition.conditions = [
            Mock(operator=">", param1="track:0:volume", param2="0.5")
        ]

        parameter_values = {"track:0:volume": 0.8}  # condition inside NOT is false

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertTrue(result)

    def test_evaluate_condition_nested_logic(self):
        """Test deeply nested logical conditions."""
        engine = RulesEngine()

        # AND(OR(NOT(volume > 0.8), pan > 0.5), volume < 0.3)
        inner_or = Mock()
        inner_or.operator = "OR"
        inner_or.conditions = [
            Mock(
                operator="NOT",
                conditions=[Mock(operator=">", param1="track:0:volume", param2="0.8")],
            ),
            Mock(operator=">", param1="track:0:pan", param2="0.5"),
        ]

        condition = Mock()
        condition.operator = "AND"
        condition.conditions = [
            inner_or,
            Mock(operator="<", param1="track:0:volume", param2="0.3"),
        ]

        parameter_values = {"track:0:volume": 0.6, "track:0:pan": 0.9}

        result = engine._evaluate_condition(condition, parameter_values)

        self.assertFalse(result)  # volume < 0.3 makes outer AND false

    @patch("socket.socket")
    def test_execute_action_set_parameter(self, mock_socket):
        """Test set_parameter action execution."""
        engine = RulesEngine()

        # Mock successful socket connection and response
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendall.return_value = None
        mock_sock.recv.return_value = b'{"status": "success", "result": {}}'
        mock_sock.close.return_value = None
        mock_sock.settimeout.return_value = None

        action = Mock()
        action.type = "set_parameter"
        action.params = {
            "track_index": 1,
            "device_index": 2,
            "parameter_index": 0,
            "value": 0.75,
        }

        result = engine._execute_action(action)

        self.assertIsNone(result)  # Should return None on success

    @patch("socket.socket")
    def test_execute_action_set_volume(self, mock_socket):
        """Test set_volume action execution with dB conversion."""
        engine = RulesEngine()

        # Mock successful socket connection and response
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendall.return_value = None
        mock_sock.recv.return_value = b'{"status": "success", "result": {}}'
        mock_sock.close.return_value = None
        mock_sock.settimeout.return_value = None

        action = Mock()
        action.type = "set_volume"
        action.params = {"volume": -6.0}  # -6 dB

        result = engine._execute_action(action)

        self.assertIsNone(result)  # Should return None on success

        # Verify the command sent was correctly normalized
        command_sent = mock_sock.sendall.call_args[0][0][1]
        sent_data = json.loads(command_sent)

        self.assertEqual(sent_data["type"], "set_track_volume")
        self.assertEqual(sent_data["params"]["track_index"], 1)
        # -6 dB should normalize to 0.0 (assuming -60 dB = 0.0, 0 dB = 1.0)
        self.assertAlmostEqual(sent_data["params"]["volume"], 0.0, places=2)

    @patch("socket.socket")
    def test_execute_action_socket_timeout(self, mock_socket):
        """Test action execution with socket timeout."""
        engine = RulesEngine()

        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.settimeout.side_effect = socket.timeout()

        action = Mock()
        action.type = "set_parameter"

        with self.assertRaises(RulesEngineError) as cm:
            engine._execute_action(action)

        self.assertIn("MCP server timeout", str(cm.exception))

    @patch("socket.socket")
    def test_execute_action_socket_error(self, mock_socket):
        """Test action execution with socket error."""
        engine = RulesEngine()

        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendall.return_value = None
        mock_sock.recv.side_effect = socket.error("Connection failed")

        action = Mock()
        action.type = "set_parameter"

        with self.assertRaises(RulesEngineError) as cm:
            engine._execute_action(action)

        self.assertIn("Socket error", str(cm.exception))

    @patch("socket.socket")
    def test_execute_action_mcp_error_response(self, mock_socket):
        """Test action execution with MCP error response."""
        engine = RulesEngine()

        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendall.return_value = None
        mock_sock.recv.return_value = (
            b'{"status": "error", "message": "Device not found"}'
        )
        mock_sock.close.return_value = None

        action = Mock()
        action.type = "set_parameter"

        with self.assertRaises(RulesEngineError) as cm:
            engine._execute_action(action)

        self.assertIn("MCP error: Device not found", str(cm.exception))

    @patch("socket.socket")
    def test_execute_action_invalid_json_response(self, mock_socket):
        """Test action execution with invalid JSON response."""
        engine = RulesEngine()

        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None
        mock_sock.sendall.return_value = None
        mock_sock.recv.return_value = b"invalid json response"
        mock_sock.close.return_value = None

        action = Mock()
        action.type = "set_parameter"

        with self.assertRaises(RulesEngineError) as cm:
            engine._execute_action(action)

        self.assertIn("Invalid JSON response", str(cm.exception))

    def test_evaluate_and_execute_rule_fires(self):
        """Test complete rule evaluation and execution."""
        engine = RulesEngine(verbose=True)

        # Create rule that should fire
        from rules_parser import Rule, Condition, Action

        rule = Rule(
            name="test_rule",
            priority=1,
            condition=Condition(operator=">", param1="track:0:volume", param2="0.7"),
            action=Action(type="set_parameter", params={"value": 0.5}),
        )

        # Parameter values that should trigger rule
        parameter_values = {"track:0:volume": 0.8}

        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            mock_sock.connect.return_value = None
            mock_sock.sendall.return_value = None
            mock_sock.recv.return_value = b'{"status": "success"}'
            mock_sock.close.return_value = None

            results = engine.evaluate_and_execute([rule], parameter_values)

            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertTrue(result.fired)
            self.assertEqual(result.rule_name, "test_rule")
            self.assertIsNone(result.error)

    def test_evaluate_and_execute_rule_does_not_fire(self):
        """Test complete rule evaluation when condition not met."""
        engine = RulesEngine(verbose=True)

        # Create rule that should not fire
        from rules_parser import Rule, Condition, Action

        rule = Rule(
            name="test_rule",
            priority=1,
            condition=Condition(operator=">", param1="track:0:volume", param2="0.7"),
            action=Action(type="set_parameter", params={"value": 0.5}),
        )

        # Parameter values that should NOT trigger rule
        parameter_values = {"track:0:volume": 0.6}

        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            mock_sock.connect.return_value = None
            mock_sock.sendall.return_value = None
            mock_sock.recv.return_value = b'{"status": "success"}'
            mock_sock.close.return_value = None

            results = engine.evaluate_and_execute([rule], parameter_values)

            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertFalse(result.fired)
            self.assertEqual(result.rule_name, "test_rule")
            self.assertIsNone(result.error)

    def test_cooldown_prevents_multiple_firings(self):
        """Test that cooldown prevents rule from firing too frequently."""
        engine = RulesEngine(verbose=True)

        from rules_parser import Rule, Condition, Action

        rule = Rule(
            name="test_rule",
            priority=1,
            condition=Condition(operator=">", param1="track:0:volume", param2="0.7"),
            action=Action(type="set_parameter", params={"value": 0.5}),
        )

        parameter_values = {"track:0:volume": 0.8}

        with patch("socket.socket") as mock_socket:
            mock_sock = Mock()
            mock_socket.return_value = mock_sock
            mock_sock.connect.return_value = None
            mock_sock.sendall.return_value = None
            mock_sock.recv.return_value = b'{"status": "success"}'
            mock_sock.close.return_value = None

            start_time = time.time()

            # First evaluation - should fire
            results = engine.evaluate_and_execute([rule], parameter_values)
            self.assertEqual(len(results), 1)
            result = results[0]
            self.assertTrue(result.fired)

            # Immediate second evaluation - should be on cooldown
            with patch("time.time") as mock_time:
                mock_time.return_value = start_time + 0.1  # 0.1 seconds later

                results = engine.evaluate_and_execute([rule], parameter_values)
                self.assertEqual(len(results), 1)
                result = results[0]
                self.assertFalse(result.fired)  # Should not fire due to cooldown

    def test_build_command_set_parameter(self):
        """Test command building for set_parameter action."""
        engine = RulesEngine()

        action = Mock()
        action.type = "set_parameter"
        action.params = {
            "track_index": 1,
            "device_index": 2,
            "parameter_index": 0,
            "value": 0.75,
        }

        command = engine._build_command(action)

        self.assertEqual(command["type"], "set_device_parameter")
        self.assertEqual(command["params"]["track_index"], 1)
        self.assertEqual(command["params"]["device_index"], 2)
        self.assertEqual(command["params"]["parameter_index"], 0)
        self.assertEqual(command["params"]["value"], 0.75)

    def test_build_command_set_parameter_defaults(self):
        """Test command building with default track/device indices."""
        engine = RulesEngine(track_index=3, device_index=1)

        action = Mock()
        action.type = "set_parameter"
        action.params = {"value": 0.5}  # No track/device indices

        command = engine._build_command(action)

        self.assertEqual(command["type"], "set_device_parameter")
        self.assertEqual(command["params"]["track_index"], 3)  # Default applied
        self.assertEqual(command["params"]["device_index"], 1)  # Default applied
        self.assertEqual(command["params"]["value"], 0.5)

    def test_build_command_other_actions(self):
        """Test command building for other action types."""
        engine = RulesEngine()

        test_cases = [
            ("fire_clip", {"clip_index": 1}),
            ("start_playback", {}),
            ("set_volume", {"volume": 0.8}),
            ("set_tempo", {"tempo": 128.0}),
        ]

        for action_type, expected_params in test_cases:
            with self.subTest(action_type=action_type):
                action = Mock()
                action.type = action_type
                action.params = expected_params

                command = engine._build_command(action)

                expected_type = action_type.replace("_", "_")
                self.assertEqual(command["type"], f"set_{expected_type}")
                self.assertEqual(command["params"], expected_params)

    def test_polling_rules_engine_start_stop(self):
        """Test PollingRulesEngine start and stop functionality."""
        from rules_parser import RulesParser

        # Create temporary rules file
        rules_content = """
rules:
  - name: "test_rule"
    priority: 1
    condition:
      operator: ">"
      param1: "track:0:volume"
      param2: "0.7"
    action:
      type: "set_parameter"
      params:
        value: 0.9
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(rules_content)
            f.flush()

            # Test PollingRulesEngine
            polling_engine = PollingRulesEngine(
                host="localhost",
                port=9877,
                track_index=0,
                device_index=0,
                polling_rate_hz=10.0,
                cooldown_seconds=1.0,
                verbose=True,
            )

            start_time = time.time()

            # Start engine
            polling_engine.start(rules_file=f.name, duration_seconds=1.0)

            # Wait for completion
            time.sleep(1.5)

            # Stop engine
            polling_engine.stop()

            # Verify engine ran for approximately 1 second
            # (should have made 10 polls at 10 Hz)
            self.assertLess(time.time() - start_time, 0.2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
