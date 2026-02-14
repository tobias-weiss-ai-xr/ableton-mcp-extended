"""
Unit tests for CLI monitor components.

Tests MonitorDisplay, MonitorConfig, and AudioAnalysisMonitor classes.
"""

import unittest
import time
import threading
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from MCP_Server.audio_analysis.cli_monitor import (
    MonitorColors,
    MonitorConfig,
    MonitorDisplay,
    AudioAnalysisMonitor,
)


class TestMonitorColors(unittest.TestCase):
    """Test ANSI color code class."""

    def test_color_codes_defined(self):
        """Verify all color codes are defined."""
        self.assertIsNotNone(MonitorColors.RESET)
        self.assertIsNotNone(MonitorColors.BOLD)
        self.assertIsNotNone(MonitorColors.RED)
        self.assertIsNotNone(MonitorColors.GREEN)
        self.assertIsNotNone(MonitorColors.YELLOW)
        self.assertIsNotNone(MonitorColors.BG_GREEN)


class TestMonitorConfig(unittest.TestCase):
    """Test MonitorConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MonitorConfig()
        self.assertEqual(config.refresh_rate_hz, 10)
        self.assertTrue(config.show_raw_values)
        self.assertTrue(config.show_history)
        self.assertFalse(config.show_debug)
        self.assertEqual(config.terminal_width, 80)
        self.assertEqual(config.progress_bar_width, 20)

    def test_custom_config(self):
        """Test custom configuration values."""
        config = MonitorConfig(
            refresh_rate_hz=20, show_raw_values=False, show_debug=True
        )
        self.assertEqual(config.refresh_rate_hz, 20)
        self.assertFalse(config.show_raw_values)
        self.assertTrue(config.show_debug)


class TestMonitorDisplay(unittest.TestCase):
    """Test MonitorDisplay class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MonitorConfig()
        self.display = MonitorDisplay(self.config)

    def test_initialization(self):
        """Test display initialization."""
        self.assertEqual(self.display.config, self.config)
        self.assertEqual(self.display._last_reresh_time, 0.0)

    def test_render_header(self):
        """Test section header rendering."""
        header = self.display.render_header("TEST")
        self.assertIn("TEST", header)
        self.assertIn(MonitorColors.CYAN, header)

    def test_render_parameter_row(self):
        """Test parameter row rendering."""
        row = self.display.render_parameter_row(
            param_index=2,
            param_name="Test Param",
            normalized_value=0.75,
            raw_value=0.5,
            min_value=0.0,
            max_value=1.0,
            unit="dB",
        )
        self.assertIn("[ 2]", row)
        self.assertIn("Test Param", row)
        self.assertIn("0.750", row)
        self.assertIn("0.50 dB", row)

    def test_render_parameter_row_color_levels(self):
        """Test color levels based on value."""
        # High value -> RED
        high_row = self.display.render_parameter_row(0, "High", 0.9)
        self.assertIn(MonitorColors.RED, high_row)

        # Medium-high value -> YELLOW
        med_high_row = self.display.render_parameter_row(0, "MedHigh", 0.7)
        self.assertIn(MonitorColors.YELLOW, med_high_row)

        # Medium value -> GREEN
        med_row = self.display.render_parameter_row(0, "Medium", 0.5)
        self.assertIn(MonitorColors.GREEN, med_row)

        # Low value -> DIM
        low_row = self.display.render_parameter_row(0, "Low", 0.2)
        self.assertIn(MonitorColors.DIM, low_row)

    def test_render_parameter_row_no_raw(self):
        """Test parameter row without raw value."""
        row = self.display.render_parameter_row(
            param_index=0, param_name="No Raw", normalized_value=0.5
        )
        self.assertNotIn("raw:", row)

    def test_render_polling_status(self):
        """Test polling status rendering."""
        status = self.display.render_polling_status(
            actual_rate_hz=10.5,
            target_rate_hz=10.0,
            uptime_seconds=120.5,
            total_snapshots=1205,
        )
        self.assertIn("10.50 Hz", status)
        self.assertIn("2.0m", status)
        self.assertIn("1205", status)
        self.assertIn("[OK]", status)  # 10.5/10.0 = 105% >= 95%

    def test_render_polling_status_slow(self):
        """Test polling status with slow rate."""
        status = self.display.render_polling_status(
            actual_rate_hz=8.5,
            target_rate_hz=10.0,
            uptime_seconds=100.0,
            total_snapshots=850,
        )
        self.assertIn("[SLOW]", status)  # 8.5/10.0 = 85% < 95%, >= 80%

    def test_render_polling_status_unstable(self):
        """Test polling status with unstable rate."""
        status = self.display.render_polling_status(
            actual_rate_hz=3.0,
            target_rate_hz=10.0,
            uptime_seconds=50.0,
            total_snapshots=150,
        )
        self.assertIn("[UNSTABLE]", status)  # 3.0/10.0 = 30% < 80%

    def test_render_rule_stats(self):
        """Test rule engine statistics rendering."""
        stats = self.display.render_rule_stats(
            evaluations=1000,
            triggers=50,
            actions=200,
            errors=0,
            enabled_rules=3,
            total_rules=5,
        )
        self.assertIn("1000", stats)
        self.assertIn("50", stats)
        self.assertIn("200", stats)
        self.assertIn("3/ 5", stats)  # Note the space between 3 and 5 due to formatting

    def test_render_rule_stats_with_errors(self):
        """Test rule statistics with errors."""
        stats = self.display.render_rule_stats(
            evaluations=100,
            triggers=10,
            actions=20,
            errors=5,
            enabled_rules=2,
            total_rules=4,
        )
        self.assertIn(MonitorColors.RED, stats)  # Errors get red color

    def test_render_active_rules_empty(self):
        """Test empty triggered rules list."""
        active = self.display.render_active_rules([])
        self.assertIn("No recent triggers", active)

    def test_render_active_rules_with_data(self):
        """Test triggered rules with data."""
        rules = [
            {
                "rule_id": "rule_1",
                "rule_name": "Test Rule",
                "triggered_at": time.time(),
                "actions": ["set_parameter", "trigger_clip"],
            }
        ]
        active = self.display.render_active_rules(rules)
        self.assertIn("Test Rule", active)
        self.assertIn("set_parameter", active)

    def test_render_monitor_display(self):
        """Test complete monitor display rendering."""
        poller_status = {
            "actual_rate_hz": 10.0,
            "target_rate_hz": 10.0,
            "uptime_seconds": 60.0,
            "total_snapshots": 600,
        }

        parameter_configs = [
            {
                "index": 0,
                "name": "Param 1",
                "min_value": 0.0,
                "max_value": 1.0,
                "unit": "dB",
            }
        ]

        current_values = {0: 0.5, "raw_0": 0.0}

        rule_stats = {
            "evaluations": 100,
            "triggers": 5,
            "actions": 10,
            "errors": 0,
            "enabled_rules": 2,
            "total_rules": 3,
        }

        display_text = self.display.render_monitor_display(
            poller_status=poller_status,
            parameter_configs=parameter_configs,
            current_values=current_values,
            rule_stats=rule_stats,
            active_rules=[],
        )

        self.assertIn("POLLING STATUS", display_text)
        self.assertIn("PARAMETER VALUES", display_text)
        self.assertIn("RULE ENGINE", display_text)
        self.assertIn("Param 1", display_text)

    @patch("builtins.print")
    def test_update_display(self, mock_print):
        """Test display update."""
        display_text = "Test Display"
        self.display.update_display(display_text)

        # Verify print was called twice (clear + display text)
        self.assertEqual(mock_print.call_count, 2)

        # Verify second call has display text
        call_args = mock_print.call_args[0]
        self.assertEqual(call_args[0], display_text)


class TestAudioAnalysisMonitor(unittest.TestCase):
    """Test AudioAnalysisMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_controller = Mock()
        self.mock_poller = Mock()
        self.mock_rule_engine = Mock()

        # Set up controller mock
        self.mock_controller._poller = self.mock_poller
        self.mock_controller._rule_engine = self.mock_rule_engine
        self.mock_controller.get_status.return_value = {
            "actual_rate_hz": 10.0,
            "target_rate_hz": 10.0,
            "uptime_seconds": 60.0,
            "total_snapshots": 600,
        }

        # Set up poller mock
        self.mock_poller.get_latest_snapshot.return_value = None
        self.mock_poller._params_to_poll = []

        # Set up rule engine mock
        self.mock_rule_engine.get_stats.return_value = {
            "evaluations": 100,
            "triggers": 5,
            "actions": 10,
            "errors": 0,
        }
        self.mock_rule_engine._rules = []
        self.mock_rule_engine.add_callback = Mock()

        self.monitor = AudioAnalysisMonitor(self.mock_controller)

    def test_initialization(self):
        """Test monitor initialization."""
        self.assertEqual(self.monitor.controller, self.mock_controller)
        self.assertFalse(self.monitor._running)
        self.assertEqual(len(self.monitor._recent_triggers), 0)

    def test_on_rule_actions(self):
        """Test rule action callback."""
        actions = [
            {"rule_id": "rule_1", "rule_name": "Rule 1", "actions": ["action_1"]}
        ]

        self.monitor.on_rule_actions(actions)

        self.assertEqual(len(self.monitor._recent_triggers), 1)
        self.assertEqual(self.monitor._recent_triggers[0]["rule_id"], "rule_1")

    def test_on_rule_actions_limit(self):
        """Test trigger list size limit."""
        max_triggers = self.monitor._max_triggers

        # Add more than max triggers
        for i in range(max_triggers + 5):
            self.monitor.on_rule_actions(
                [{"rule_id": f"rule_{i}", "rule_name": f"Rule {i}", "actions": []}]
            )

        # Verify list is limited
        self.assertEqual(len(self.monitor._recent_triggers), max_triggers)

    def test_toggle_debug(self):
        """Test debug toggle."""
        initial_state = self.monitor.display.config.show_debug
        self.monitor.toggle_debug()
        self.assertEqual(self.monitor.display.config.show_debug, not initial_state)

    def test_set_refresh_rate_valid(self):
        """Test setting valid refresh rate."""
        self.monitor.set_refresh_rate(20)
        self.assertEqual(self.monitor.display.config.refresh_rate_hz, 20)

    def test_set_refresh_rate_invalid(self):
        """Test setting invalid refresh rate."""
        original_rate = self.monitor.display.config.refresh_rate_hz

        # Too low
        self.monitor.set_refresh_rate(0)
        self.assertEqual(self.monitor.display.config.refresh_rate_hz, original_rate)

        # Too high
        self.monitor.set_refresh_rate(100)
        self.assertEqual(self.monitor.display.config.refresh_rate_hz, original_rate)

    def test_start_registers_callback(self):
        """Test that start registers callback with rule engine."""
        self.monitor.start()

        # Verify callback was registered
        self.mock_rule_engine.add_callback.assert_called_once()
        callback = self.mock_rule_engine.add_callback.call_args[0][0]
        self.assertEqual(callback, self.monitor.on_rule_actions)

        # Cleanup
        self.monitor.stop()

    def test_start_stops_immediately(self):
        """Test start/stop cycle."""
        self.monitor.start()
        self.assertTrue(self.monitor._running)

        self.monitor.stop()
        self.assertFalse(self.monitor._running)

    def test_thread_safety(self):
        """Test thread safety of trigger list updates."""
        num_threads = 5
        actions_per_thread = 10

        def add_triggers(thread_id):
            for i in range(actions_per_thread):
                self.monitor.on_rule_actions(
                    [
                        {
                            "rule_id": f"rule_{thread_id}_{i}",
                            "rule_name": f"Rule {thread_id}_{i}",
                            "actions": [],
                        }
                    ]
                )

        # Start multiple threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=add_triggers, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify no duplicates and correct count
        expected_max = min(num_threads * actions_per_thread, self.monitor._max_triggers)
        self.assertLessEqual(len(self.monitor._recent_triggers), expected_max)


if __name__ == "__main__":
    unittest.main()
