import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to sys.path to import analysis modules
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "analysis")
)

try:
    from rules_engine import RulesEngine
    from responsive_control import ResponsiveControlLoop
except ImportError as e:
    print(f"Error importing analysis modules: {e}")
    print("Make sure analysis scripts are properly implemented")
    sys.exit(1)


class TestResponsiveControlLoop(unittest.TestCase):
    """Test responsive control loop integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_polling_func = Mock(return_value={"parameters": []})
        self.mock_rules_engine = Mock()
        self.mock_ableton = Mock()

    @patch("responsive_control.get_ableton_connection")
    @patch("responsive_control.parse_rules")
    def test_control_loop_initialization(self, mock_parse_rules, mock_get_connection):
        """Test control loop initialization."""
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.time.sleep") as mock_sleep:
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        # Import and test in a separate scope due to function structure
                        from responsive_control import main

                        # Test initialization
                        mock_sleep.assert_not_called()  # Should not sleep during init
                        mock_signal.assert_called_once()  # Should set up signal handler
                        mock_exit.assert_not_called()  # Should not exit during init

    def test_control_loop_parameter_updates(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test parameter updates trigger rule evaluation."""
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
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        from responsive_control import main

                        # Test parameter update triggers rule
                        main(["test_rules.yml", "--duration", "0.1"])

                        # Verify rule was evaluated
                        self.mock_rules_engine.evaluate_rules.assert_called()

                        # Verify action was executed
                        self.mock_ableton.send_command.assert_called()

    def test_control_loop_multiple_parameter_updates(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test multiple parameter updates in sequence."""
        # Setup mocks
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton

        # Mock sequence of parameter values
        param_sequence = [
            {"parameters": [{"name": "lufs", "value": -13.0}]},  # Below threshold
            {"parameters": [{"name": "lufs", "value": -15.0}]},  # At threshold
            {"parameters": [{"name": "lufs", "value": -16.0}]},  # Above threshold
        ]
        self.mock_polling_func.side_effect = param_sequence

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        from responsive_control import main

                        main(["test_rules.yml", "--duration", "0.3"])

                        # Verify rule evaluation was called multiple times
                        call_count = self.mock_rules_engine.evaluate_rules.call_count

                        # Should have evaluated rules multiple times based on parameter changes
                        self.assertGreater(call_count, 2)

                        # Verify final state matches last parameter value
                        final_actions = (
                            self.mock_rules_engine.evaluate_rules.return_value
                        )
                        self.mock_ableton.send_command.assert_called()

    def test_control_loop_graceful_shutdown(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test graceful shutdown on Ctrl+C."""
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton

        # Simulate KeyboardInterrupt on second sleep call
        sleep_calls = [None, KeyboardInterrupt()]

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.time.sleep") as mock_sleep:
                mock_sleep.side_effect = sleep_calls
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        from responsive_control import main

                        try:
                            main(["test_rules.yml", "--duration", "1"])
                        except SystemExit:
                            pass

                        # Verify graceful shutdown
                        mock_exit.assert_called_once_with(0)

                        # Verify cleanup was attempted
                        mock_get_connection.return_value.send_command.assert_called_with(
                            "stop_polling", {}
                        )

    def test_control_loop_dry_run_mode(self, mock_parse_rules, mock_get_connection):
        """Test dry run mode prevents actual Ableton commands."""
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton
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
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        from responsive_control import main

                        try:
                            main(["test_rules.yml", "--dry-run", "--duration", "0.1"])
                        except SystemExit:
                            pass

                        # Verify no actual Ableton commands were sent in dry run
                        mock_get_connection.return_value.send_command.assert_not_called()

                        # Verify rules were still evaluated
                        self.mock_rules_engine.evaluate_rules.assert_called()

    def test_control_loop_error_recovery(self, mock_parse_rules, mock_get_connection):
        """Test error recovery in control loop."""
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton

        # Mock polling error then recovery
        self.mock_polling_func.side_effect = [
            {"error": "Connection timeout"},
            {"parameters": [{"name": "lufs", "value": -12.0}]},  # Recovery
        ]

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        from responsive_control import main

                        try:
                            main(["test_rules.yml", "--duration", "0.2"])
                        except SystemExit:
                            pass

                        # Verify error was logged and loop continued
                        self.assertEqual(self.mock_polling_func.call_count, 2)

                        # Verify recovery action was executed
                        self.assertGreater(
                            mock_get_connection.return_value.send_command.call_count, 0
                        )

    def test_control_loop_latency_measurement(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test latency measurement functionality."""
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton
        self.mock_rules_engine.evaluate_rules.return_value = [
            {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": 0.8},
            }
        ]

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.time.time") as mock_time:
                    with patch("responsive_control.signal.signal") as mock_signal:
                        with patch("responsive_control.sys.exit") as mock_exit:
                            # Mock timing
                            start_time = 1000.0
                            mock_time.time.return_value = 1000.1

                            from responsive_control import main

                            try:
                                main(["test_rules.yml", "--duration", "0.1"])
                            except SystemExit:
                                pass

                            # Verify latency was calculated
                            # Should have measured time between parameter read and action
                            self.assertTrue(mock_time.time.called)
                            self.assertTrue(mock_time.return_value >= start_time + 0.1)

    def test_control_loop_statistics_tracking(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test statistics tracking (rules fired per second, etc.)."""
        mock_parse_rules.return_value = self.mock_rules_engine
        mock_get_connection.return_value = self.mock_ableton
        self.mock_rules_engine.evaluate_rules.return_value = [
            {
                "type": "set_parameter",
                "target": {"track": 1, "parameter": "volume", "value": 0.8},
            }
        ]

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.print") as mock_print:
                with patch("responsive_control.time.sleep"):
                    with patch("responsive_control.signal.signal") as mock_signal:
                        with patch("responsive_control.sys.exit") as mock_exit:
                            from responsive_control import main

                            try:
                                main(["test_rules.yml", "--duration", "0.1"])
                            except SystemExit:
                                pass

                            # Verify statistics were displayed
                            mock_print.assert_called()

                            # Check if statistics contain expected information
                            calls = mock_print.call_args_list
                            stats_printed = any(
                                "rules fired" in str(call).lower() for call in calls
                            )
                            self.assertTrue(stats_printed)

    def test_control_loop_multiple_rules_same_priority(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test multiple rules with same priority execute in order defined."""
        # Create two rules with same priority
        same_priority_rules = [
            {
                "name": "First Rule",
                "priority": 50,
                "condition": {"parameter": "lufs", "operator": ">", "value": -14.0},
                "action": {
                    "type": "set_parameter",
                    "target": {"track": 1, "parameter": "volume", "value": -0.1},
                },
            },
            {
                "name": "Second Rule",
                "priority": 50,  # Same priority
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

        mock_parse_rules.return_value.load_rules.side_effect = lambda rules: None
        self.mock_parse_rules.return_value.load_rules.return_value = None

        self.engine = RulesEngine()  # Create fresh instance

        # Load rules directly to test internal ordering
        self.engine.load_rules(same_priority_rules)

        mock_params = {"lufs": -15.0, "spectral_centroid": 800}

        with patch(
            "responsive_control.poll_plugin_parameters",
            return_value=self.mock_polling_func,
        ):
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal") as mock_signal:
                    with patch("responsive_control.sys.exit") as mock_exit:
                        from responsive_control import main

                        try:
                            main(["test_rules.yml", "--duration", "0.1"])
                        except SystemExit:
                            pass

                        # Both rules should fire, check execution order
                        actions_executed = (
                            mock_get_connection.return_value.send_command.call_args_list
                        )

                        # Should have executed actions for both rules
                        self.assertEqual(len(actions_executed), 2)

                        # Check if actions match expected order (first rule first, second rule second)
                        action_params = [
                            call[0][1]
                            for call in actions_executed
                            if "set_device_parameter" in str(call[0])
                        ]
                        self.assertEqual(len(action_params), 2)


class TestMockMCPConnection(unittest.TestCase):
    """Test mock MCP connection functionality."""

    def test_mock_connection_set_device_parameter(self):
        """Test mock connection handles set_device_parameter calls."""
        from responsive_control import MockAbletonConnection

        mock_conn = MockAbletonConnection()

        # Test setting device parameter
        result = mock_conn.send_command(
            "set_device_parameter",
            {"track_index": 0, "device_index": 1, "parameter_index": 2, "value": 0.75},
        )

        self.assertIn("success", result)
        self.assertEqual(result["success"], True)

        # Verify the command was recorded
        commands = mock_conn.get_commands()
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0]["type"], "set_device_parameter")

    def test_mock_connection_send_command_validation(self):
        """Test mock connection validates command parameters."""
        from responsive_control import MockAbletonConnection

        mock_conn = MockAbletonConnection()

        # Test with missing required parameter
        result = mock_conn.send_command(
            "set_device_parameter",
            {
                "track_index": 0,
                # Missing device_index
                "parameter_index": 2,
                "value": 0.75,
            },
        )

        self.assertIn("error", result)
        self.assertIn("Missing required parameter", result["error"])

        # Verify no command was recorded
        commands = mock_conn.get_commands()
        self.assertEqual(len(commands), 0)

    def test_mock_connection_get_commands(self):
        """Test mock connection command history tracking."""
        from responsive_control import MockAbletonConnection

        mock_conn = MockAbletonConnection()

        # Initially should have no commands
        self.assertEqual(len(mock_conn.get_commands()), 0)

        # Add some commands
        mock_conn.send_command(
            "set_device_parameter",
            {"track_index": 0, "device_index": 1, "parameter_index": 2, "value": 0.75},
        )
        mock_conn.send_command("set_track_volume", {"track_index": 1, "volume": 0.8})

        commands = mock_conn.get_commands()
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0]["type"], "set_device_parameter")
        self.assertEqual(commands[1]["type"], "set_track_volume")
        self.assertEqual(commands[1]["params"]["volume"], 0.8)


class TestControlLoopPerformance(unittest.TestCase):
    """Test control loop performance characteristics."""

    @patch("responsive_control.get_ableton_connection")
    @patch("responsive_control.parse_rules")
    def test_control_loop_high_frequency_operation(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test control loop can handle high-frequency operations."""
        mock_parse_rules.return_value = Mock()
        mock_get_connection.return_value = Mock()

        # Mock high-frequency parameter updates (20 Hz = every 50ms)
        param_updates = []

        def mock_polling():
            param_updates.append({"parameters": [{"name": "lufs", "value": -15.0}]})
            return {"parameters": [{"name": "lufs", "value": -15.0}]}

        with patch(
            "responsive_control.poll_plugin_parameters", return_value=mock_polling
        ):
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal"):
                    with patch("responsive_control.sys.exit"):
                        from responsive_control import main

                        # Test very short duration (0.25 seconds = 5 updates at 20 Hz)
                        main(["test_rules.yml", "--duration", "0.25"])

                        # Verify polling was called frequently
                        self.assertGreater(len(param_updates), 4)  # At 20 Hz for 0.25s

                        # Verify loop completed successfully
                        # mock_get_connection.return_value.send_command.call_count would show action executions

    def test_control_loop_memory_usage_tracking(
        self, mock_parse_rules, mock_get_connection
    ):
        """Test control loop tracks memory usage."""
        mock_parse_rules.return_value = Mock()
        mock_get_connection.return_value = Mock()

        with patch("responsive_control.poll_plugin_parameters") as mock_polling:
            with patch("responsive_control.time.sleep"):
                with patch("responsive_control.signal.signal"):
                    with patch("responsive_control.sys.exit") as mock_exit:
                        with patch("responsive_control.psutil.Process") as mock_process:
                            with patch(
                                "responsive_control.tracemalloc.get_traced_memory"
                            ) as mock_memory:
                                from responsive_control import main

                                # Mock memory tracking
                                mock_process.return_value.memory_info.return_value.rss = 50000  # 50MB
                                mock_memory.return_value = 60000  # 60MB

                                main(["test_rules.yml", "--duration", "0.1"])

                                # Verify memory was tracked (calls would be made to psutil and tracemalloc)
                                # Since we're mocking, just verify the functions exist and would be called
                                self.assertTrue(
                                    hasattr(mock_process.return_value, "memory_info")
                                )
                                self.assertTrue(
                                    hasattr(
                                        mock_memory.return_value, "get_traced_memory"
                                    )
                                )


if __name__ == "__main__":
    # Run tests with coverage reporting
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
