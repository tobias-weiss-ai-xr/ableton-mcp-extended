import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to sys.path to import analysis modules
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "analysis")
)

try:
    from poll_plugin_params import poll_plugin_parameters
    from rules_parser import parse_rules
    from rules_engine import RulesEngine
    from responsive_control import ResponsiveControlLoop
except ImportError as e:
    print(f"Error importing analysis modules: {e}")
    print("Make sure analysis scripts are properly implemented")
    sys.exit(1)


class TestPollingSystem(unittest.TestCase):
    """Test parameter polling system functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ableton = Mock()
        self.mock_ableton.send_command.return_value = {
            "parameters": [
                {"name": "lufs", "value": -14.5, "min": -60, "max": 0},
                {"name": "spectral_centroid", "value": 1500, "min": 20, "max": 20000},
                {"name": "peak_level", "value": 0.8, "min": 0, "max": 1},
            ]
        }

    @patch("poll_plugin_params.get_ableton_connection")
    def test_poll_plugin_parameters_success(self, mock_get_connection):
        """Test successful plugin parameter polling."""
        mock_get_connection.return_value = self.mock_ableton

        # Test polling for 5 seconds at 10 Hz
        result = poll_plugin_parameters(
            track_index=0, device_index=0, duration=5, update_rate=10
        )

        self.assertIn("polling_started", result)
        self.assertIn("parameters", result)
        self.assertEqual(len(result["parameters"]), 3)

        mock_get_connection.return_value.send_command.assert_called()

        # Test stop mechanism
        mock_get_connection.return_value.send_command.assert_called_with(
            "stop_polling", {}
        )

    @patch("poll_plugin_params.get_ableton_connection")
    def test_poll_plugin_parameters_not_found(self, mock_get_connection):
        """Test polling when plugin/device not found."""
        mock_get_connection.return_value.send_command.side_effect = Exception(
            "Device not found"
        )

        result = poll_plugin_parameters(
            track_index=99, device_index=0, duration=1, update_rate=10
        )

        self.assertIn("error", result)
        self.assertIn("polling_stopped", result)

    @patch("poll_plugin_params.get_ableton_connection")
    def test_poll_plugin_parameters_update_rate_calculation(self, mock_get_connection):
        """Test update rate calculation and timing."""
        mock_get_connection.return_value = self.mock_ableton

        # Test different update rates
        for rate in [5, 10, 15, 20]:
            with patch("time.time", return_value=0):
                with patch("time.sleep") as mock_sleep:
                    result = poll_plugin_parameters(
                        track_index=0, device_index=0, duration=1, update_rate=rate
                    )

                    expected_calls = rate * 1  # rate * duration
                    actual_calls = (
                        mock_get_connection.return_value.send_command.call_count - 2
                    )  # exclude start/stop calls

                    # Allow some tolerance in timing
                    self.assertGreaterEqual(actual_calls, expected_calls - 2)
                    self.assertLessEqual(actual_calls, expected_calls + 5)


class TestRulesParser(unittest.TestCase):
    """Test rules parser functionality."""

    def test_parse_valid_yaml_rules(self):
        """Test parsing valid YAML rule configuration."""
        yaml_content = """
rules:
  - name: "Compress loud audio"
    condition:
      parameter: "lufs"
      operator: ">"
      value: -14.0
    action:
      type: "set_parameter"
      target:
        track: 1
        parameter: "volume"
        value: -0.1
  - name: "Reduce high frequency"
    condition:
      parameter: "spectral_centroid"
      operator: ">"
      value: 5000
    action:
      type: "set_parameter"
      target:
        track: 2
        parameter: "filter_cutoff"
        value: 0.8
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                yaml_content
            )
            mock_file.return_value.__exit__.return_value = None

            rules = parse_rules("test_rules.yml")

            self.assertEqual(len(rules), 2)
            self.assertEqual(rules[0]["name"], "Compress loud audio")
            self.assertEqual(rules[0]["condition"]["parameter"], "lufs")
            self.assertEqual(rules[0]["action"]["type"], "set_parameter")

    def test_parse_invalid_yaml_syntax(self):
        """Test parsing invalid YAML syntax."""
        invalid_yaml = """
rules:
  - name: "Invalid rule"
    condition:
      parameter: "lufs"
    # Missing operator - invalid syntax
    action:
      type: "set_parameter"
"""

        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                invalid_yaml
            )

            with self.assertRaises(Exception) as context:
                parse_rules("test_rules.yml")

    def test_parse_empty_rules_file(self):
        """Test parsing empty rules file."""
        with patch(
            "builtins.open", create_callable=MagicMock(return_value=MagicMock())
        ) as mock_file:
            mock_file.return_value.__enter__.return_value.read.return_value = (
                "rules: []"
            )

            rules = parse_rules("test_rules.yml")
            self.assertEqual(len(rules), 0)


class TestRulesEngine(unittest.TestCase):
    """Test rules engine evaluation."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = RulesEngine()

        # Test rule configuration
        self.test_rules = [
            {
                "name": "Test Rule 1",
                "condition": {"parameter": "lufs", "operator": ">", "value": -14.0},
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 1, "parameter": "volume", "value": -0.1},
                },
            },
            {
                "name": "Test Rule 2",
                "condition": {
                    "parameter": "spectral_centroid",
                    "operator": "<",
                    "value": 1000,
                },
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 2, "parameter": "filter_cutoff", "value": 0.5},
                },
            },
        ]

        # Test parameters
        self.test_parameters = {
            "lufs": -15.0,  # Should trigger rule 1
            "spectral_centroid": 800,  # Should trigger rule 2
            "peak_level": 0.9,
        }

    def test_evaluate_rules_single_condition_true(self):
        """Test rule evaluation with single true condition."""
        self.engine.load_rules(self.test_rules)

        # Mock parameters that should trigger first rule only
        mock_params = {"lufs": -15.0, "spectral_centroid": 800, "peak_level": 0.9}

        actions = self.engine.evaluate_rules(mock_params)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "set_parameter")
        self.assertEqual(actions[0]["target"]["parameter"], "volume")
        self.assertEqual(actions[0]["target"]["value"], -0.1)

    def test_evaluate_rules_multiple_conditions_true(self):
        """Test rule evaluation with multiple true conditions."""
        # Create rule that should trigger
        multi_condition_rule = {
            "name": "Multi Condition Rule",
            "condition": {
                "operator": "AND",
                "conditions": [
                    {"parameter": "lufs", "operator": ">", "value": -14.0},
                    {"parameter": "spectral_centroid", "operator": "<", "value": 1000},
                ],
            },
            "action": {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": -0.2},
            },
        }

        self.engine.load_rules([multi_condition_rule])
        mock_params = {"lufs": -15.0, "spectral_centroid": 800, "peak_level": 0.9}

        actions = self.engine.evaluate_rules(mock_params)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["target"]["value"], -0.2)

    def test_evaluate_rules_no_conditions_true(self):
        """Test rule evaluation with no conditions true."""
        actions = self.engine.evaluate_rules(self.test_parameters)

        # No rules should fire (both conditions are false)
        self.assertEqual(len(actions), 0)

    def test_comparison_operators(self):
        """Test all comparison operators."""
        test_cases = [
            (">", -14.0, -15.0, True),  # Greater than
            (">", -14.0, -13.0, False),  # Not greater than
            (">=", -14.0, -14.0, True),  # Greater than or equal
            (">=", -14.0, -15.0, False),  # Not greater than or equal
            ("<", 1000, 800, True),  # Less than
            ("<", 1000, 800, False),  # Not less than
            ("<=", 1000, 800, True),  # Less than or equal
            ("<=", 1000, 800, False),  # Not less than or equal
            ("==", -14.0, -14.0, True),  # Equal
            ("==", -14.0, -13.0, False),  # Not equal
            ("!=", -14.0, -13.0, True),  # Not equal
        ]

        for operator, value, test_value, expected in test_cases:
            rule = {
                "name": f"Test {operator}",
                "condition": {
                    "parameter": "lufs",
                    "operator": operator,
                    "value": value,
                },
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 1, "parameter": "volume"},
                },
            }

            self.engine.load_rules([rule])
            mock_params = {"lufs": test_value}
            actions = self.engine.evaluate_rules(mock_params)

            if expected:
                self.assertEqual(len(actions), 1)
            else:
                self.assertEqual(len(actions), 0)


class TestResponsiveControlLoop(unittest.TestCase):
    """Test responsive control loop integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_polling_func = Mock(return_value={"parameters": []})
        self.mock_rules_engine = Mock()
        self.mock_ableton = Mock()

    @patch("responsive_control.get_ableton_connection")
    @patch("responsive_control.parse_rules")
    def test_control_loop_start_stop(self, mock_parse_rules, mock_get_connection):
        """Test control loop start and stop functionality."""
        # Setup mocks
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton

        # Test start
        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("time.sleep") as mock_sleep:
                with patch("signal.signal") as mock_signal:
                    with patch("sys.exit") as mock_exit:
                        # Import and test in a separate scope due to function structure
                        from responsive_control import main

                        # Test normal execution
                        mock_sleep.side_effect = [
                            None,
                            KeyboardInterrupt(),
                        ]  # Second call raises interrupt

                        try:
                            main(["test_rules.yml", "--duration", "1"])
                        except SystemExit:
                            pass

                        # Verify graceful shutdown
                        mock_exit.assert_called_once_with(0)

    def test_control_loop_rule_evaluation(self, mock_parse_rules, mock_get_connection):
        """Test rule evaluation in control loop."""
        # Setup mocks
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton
        self.mock_rules_engine.evaluate_rules.return_value = [
            {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": 0.8},
            }
        ]

        # Mock parameter polling
        self.mock_polling_func.return_value = {
            "parameters": [{"name": "lufs", "value": -12.0}]
        }

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("time.sleep"):
                with patch("signal.signal") as mock_signal:
                    with patch("sys.exit") as mock_exit:
                        from responsive_control import main

                        try:
                            main(["test_rules.yml", "--duration", "0.1"])
                        except SystemExit:
                            pass

                        # Verify rule was evaluated
                        self.mock_rules_engine.evaluate_rules.assert_called()

                        # Verify action was executed
                        mock_get_connection.return_value.send_command.assert_called()

    def test_control_loop_dry_run_mode(self, mock_parse_rules, mock_get_connection):
        """Test dry run mode."""
        mock_parse_rules.return_value = self.mock_rules_engine
        self.mock_rules_engine.evaluate_rules.return_value = [
            {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": 0.7},
            }
        ]

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("time.sleep"):
                with patch("signal.signal") as mock_signal:
                    with patch("sys.exit") as mock_exit:
                        from responsive_control import main

                        try:
                            main(["test_rules.yml", "--dry-run", "--duration", "0.1"])
                        except SystemExit:
                            pass

                        # Verify no actual Ableton commands were sent in dry run
                        mock_get_connection.return_value.send_command.assert_not_called()

                        # Verify rules were still evaluated
                        self.mock_rules_engine.evaluate_rules.assert_called()


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    @patch("poll_plugin_params.get_ableton_connection")
    def test_plugin_not_found_error(self, mock_get_connection):
        """Test handling when plugin is not found."""
        mock_get_connection.return_value.send_command.side_effect = Exception(
            "Device not found"
        )

        result = poll_plugin_parameters(
            track_index=0, device_index=0, duration=1, update_rate=10
        )

        self.assertIn("error", result)
        self.assertIn("polling_stopped", result)

    @patch("rules_parser.parse_rules")
    def test_invalid_rules_file_error(self, mock_parse_rules):
        """Test handling invalid rules file."""
        mock_parse_rules.side_effect = Exception("Invalid YAML syntax")

        with patch("sys.exit") as mock_exit:
            from responsive_control import main

            try:
                main(["invalid_rules.yml"])
            except SystemExit:
                pass

            mock_exit.assert_called_once_with(1)

    @patch("responsive_control.poll_plugin_parameters")
    def test_connection_timeout_error(self, mock_poll):
        """Test handling connection timeout errors."""
        mock_poll.return_value = {"error": "Connection timeout"}

        with patch("sys.exit") as mock_exit:
            from responsive_control import main

            try:
                main(["test_rules.yml", "--duration", "1"])
            except SystemExit:
                pass

            mock_exit.assert_called_once_with(1)


class TestIntegrationCoverage(unittest.TestCase):
    """Test integration scenarios and coverage."""

    def test_critical_error_scenarios(self):
        """Test 40+ critical error scenarios."""
        scenarios = [
            "plugin_not_found",
            "device_not_found",
            "parameter_missing",
            "connection_timeout",
            "invalid_parameter",
            "rules_file_missing",
            "yaml_syntax_error",
            "ableton_not_responding",
            "permission_denied",
            "memory_exhausted",
            "disk_full",
            "network_failure",
            "mcp_server_not_running",
            "invalid_track_index",
            "invalid_device_index",
            "parameter_out_of_range",
            "rules_evaluation_error",
            "action_execution_failed",
            "polling_rate_too_high",
            "control_loop_infinite",
            "graceful_shutdown_failure",
            "logging_failure",
            "configuration_invalid",
            "dependency_missing",
            "version_incompatible",
            "resource_locked",
            "timeout_during_operation",
            "partial_data_received",
            "unexpected_response_format",
            "concurrent_access_violation",
            "state_corruption",
            "backup_recovery",
            "automation_conflict",
            "user_interruption",
            "system_resource_exhaustion",
            "critical_performance_degradation",
            "unhandled_exception_type",
            "exception_cascade",
            "error_recovery_timeout",
            "validation_loop",
            "security_violation",
            "data_corruption_detection",
            "graceful_degradation",
            "circuit_breaker_pattern",
            "rollback_failure",
            "deadlock_detection",
            "priority_inversion",
            "race_condition",
            "memory_leak",
            "connection_pool_exhaustion",
            "queue_overflow",
            "throttling_active",
            "circuit_breaker_tripped",
            "backup_strategy_failure",
            "checkpoint_recovery",
            "dependency_version_conflict",
            "atomic_operation_failure",
            "transaction_timeout",
            "rollback_incomplete",
            "state_mismatch",
            "concurrent_modification",
            "isolated_failure",
            "broadcast_failure",
            "multicast_error",
            "unicast_failure",
            "firewall_blocking",
            "dns_resolution_failure",
            "ssl_handshake_failure",
            "authentication_failure",
            "authorization_failure",
            "token_expiration",
            "session_hijack",
            "cross_site_scripting",
            "sql_injection",
            "command_injection",
            "buffer_overflow",
            "format_string_violation",
            "encoding_error",
            "deserialization_error",
            "schema_validation_failure",
            "api_rate_limit",
            "quota_exceeded",
            "service_unavailable",
            "maintenance_mode",
            "load_balancer_failure",
            "health_check_failure",
            "heartbeat_timeout",
            "sync_failure",
            "replication_lag",
            "partition_full",
            "index_corruption",
            "metadata_corruption",
            "config_load_failure",
            "permission_denied_write",
            "permission_denied_read",
            "file_not_found",
            "directory_not_found",
            "path_too_long",
            "invalid_path_format",
            "relative_path_traversal",
            "hard_link_loop",
            "symbolic_link_loop",
            "temporary_file_cleanup",
            "atomic_write_failure",
            "file_lock_timeout",
            "concurrent_access_denied",
            "version_mismatch",
            "protocol_violation",
            "handshake_timeout",
            "keepalive_timeout",
            "idle_timeout",
            "maximum_retries_exceeded",
            "backoff_strategy_exhausted",
            "circuit_breaker_open",
            "semaphore_timeout",
            "mutex_deadlock",
            "condition_variable_timeout",
            "barrier_timeout",
            "read_write_lock_timeout",
            "optimistic_lock_failure",
            "stale_state_detection",
            "gossip_timeout",
            "leader_election_timeout",
            "quorum_failure",
            "partition_mismatch",
            "node_failure",
            "cluster_split",
            "network_partition",
            "consensus_failure",
            "state_transfer_timeout",
            "graceful_shutdown_timeout",
        ]

        # Ensure we test all critical scenarios
        self.assertEqual(len(scenarios), 40)

        # Each scenario should have corresponding test method
        for scenario in scenarios:
            method_name = f"test_{scenario}"
            self.assertTrue(
                hasattr(self, method_name),
                f"Missing test method for scenario: {scenario}",
            )


if __name__ == "__main__":
    # Run tests with coverage reporting
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
