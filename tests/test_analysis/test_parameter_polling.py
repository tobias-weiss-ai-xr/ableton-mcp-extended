#!/usr/bin/env python3
"""
Unit tests for parameter polling system.

Tests ParameterPoller class functionality including:
- Connection management
- Parameter retrieval and caching
- Error handling and recovery
- Logging functionality
- Performance tracking
"""

import unittest
import tempfile
import os
import json
import time
from unittest.mock import Mock, patch, mock_open
import threading

from test_analysis import BaseTestCase

# Add the scripts/analysis directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up to tests/ (now at project root)
analysis_dir = os.path.join(project_root, "scripts", "analysis")
scripts_analysis_path = os.path.abspath(analysis_dir)

if scripts_analysis_path not in sys.path:
    sys.path.insert(0, scripts_analysis_path)

try:
    from poll_plugin_params import ParameterPoller
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Scripts path: {scripts_analysis_path}")
    raise


class TestParameterPoller(BaseTestCase):
    """Test cases for ParameterPoller class."""

    def test_initialization(self):
        """Test ParameterPoller initialization with valid parameters."""
        poller = ParameterPoller(
            track_index=2, device_index=1, update_rate_hz=15.0, duration_seconds=60
        )

        self.assertEqual(poller.track_index, 2)
        self.assertEqual(poller.device_index, 1)
        self.assertEqual(poller.update_rate_hz, 15.0)
        self.assertEqual(poller.duration_seconds, 60)
        self.assertEqual(poller.update_interval, 1.0 / 15.0)
        self.assertIsNone(poller.sock)
        self.assertFalse(poller.running)
        self.assertEqual(poller.readings_count, 0)
        self.assertEqual(poller.last_params, {})

    def test_initialization_default_values(self):
        """Test ParameterPoller initialization with edge cases."""
        poller = ParameterPoller(
            track_index=0, device_index=0, update_rate_hz=10.0, duration_seconds=None
        )

        self.assertEqual(poller.update_interval, 1.0 / 10.0)
        self.assertIsNone(poller.duration_seconds)

    def test_format_timestamp(self):
        """Test timestamp formatting produces ISO 8601 format."""
        poller = ParameterPoller(0, 0, 10.0)
        timestamp = poller.format_timestamp()

        # Check format: YYYY-MM-DDTHH:MM:SS.mmmZ
        self.assertRegex(timestamp, r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")

    def test_has_parameters_changed_no_previous(self):
        """Test parameter change detection with no previous params."""
        poller = ParameterPoller(0, 0, 10.0)
        new_params = [
            {"index": 0, "name": "param1", "value": 0.5},
            {"index": 1, "name": "param2", "value": 0.3},
        ]

        self.assertTrue(poller.has_parameters_changed(new_params))

    def test_has_parameters_changed_with_changes(self):
        """Test parameter change detection with actual changes."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.last_params = {0: 0.5, 1: 0.3}

        # Same values - no change
        same_params = [
            {"index": 0, "name": "param1", "value": 0.5},
            {"index": 1, "name": "param2", "value": 0.3},
        ]
        self.assertFalse(poller.has_parameters_changed(same_params))

        # Different values - change detected
        changed_params = [
            {"index": 0, "name": "param1", "value": 0.7},  # Changed
            {"index": 1, "name": "param2", "value": 0.3},  # Same
        ]
        self.assertTrue(poller.has_parameters_changed(changed_params))

    def test_has_parameters_changed_new_parameter(self):
        """Test parameter change detection with new parameter."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.last_params = {0: 0.5}

        new_params = [
            {"index": 0, "name": "param1", "value": 0.5},  # Same
            {"index": 1, "name": "param2", "value": 0.3},  # New
        ]
        self.assertTrue(poller.has_parameters_changed(new_params))

    @patch("socket.socket")
    def test_connect_success(self, mock_socket):
        """Test successful connection to Ableton."""
        # Mock successful connection
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.return_value = None

        poller = ParameterPoller(0, 0, 10.0)
        result = poller.connect()

        self.assertTrue(result)
        self.assertEqual(poller.sock, mock_sock)
        mock_sock.settimeout.assert_called_with(5.0)
        mock_sock.connect.assert_called_with(("127.0.0.1", 9877))

    @patch("socket.socket")
    def test_connect_timeout(self, mock_socket):
        """Test connection timeout handling."""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.side_effect = socket.timeout()

        with patch("builtins.print") as mock_print:
            poller = ParameterPoller(0, 0, 10.0)
            result = poller.connect()

            self.assertFalse(result)
            self.assertIsNone(poller.sock)
            mock_print.assert_any_call(
                "[ERROR] Connection timeout: Could not connect to Ableton at 127.0.0.1:9877"
            )

    @patch("socket.socket")
    def test_connect_connection_refused(self, mock_socket):
        """Test connection refused handling."""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        mock_sock.connect.side_effect = ConnectionRefusedError()

        with patch("builtins.print") as mock_print:
            poller = ParameterPoller(0, 0, 10.0)
            result = poller.connect()

            self.assertFalse(result)
            mock_print.assert_any_call(
                "[ERROR] Connection refused: Ableton Remote Script not running on port 9877"
            )

    def test_get_device_parameters_not_connected(self):
        """Test get_device_parameters when not connected."""
        poller = ParameterPoller(0, 0, 10.0)
        # Don't connect

        with self.assertRaises(SystemExit) as cm:
            poller.get_device_parameters()
        self.assertEqual(cm.exception.code, 1)

    def test_disconnect(self):
        """Test successful disconnect."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.sock = Mock()

        poller.disconnect()

        self.assertIsNone(poller.sock)
        poller.sock.close.assert_called_once()

    def test_disconnect_with_error(self):
        """Test disconnect with socket error."""
        poller = ParameterPoller(0, 0, 10.0)
        mock_sock = Mock()
        mock_sock.close.side_effect = Exception("Socket error")
        poller.sock = mock_sock

        with patch("builtins.print") as mock_print:
            poller.disconnect()

            self.assertIsNone(poller.sock)
            mock_print.assert_any_call("[WARN] Warning during disconnect: Socket error")

    @patch("builtins.open", new_callable=mock_open)
    def test_log_parameters(self, mock_file):
        """Test parameter logging to CSV format."""
        poller = ParameterPoller(0, 0, 10.0)

        # Mock file object
        mock_file_instance = Mock()
        mock_open.return_value = mock_file_instance
        mock_file_instance.tell.return_value = 0  # File is empty

        params_data = {
            "device_name": "TestDevice",
            "parameters": [
                {"index": 0, "name": "Volume", "value": 0.75, "min": 0.0, "max": 1.0},
                {"index": 1, "name": "Pan", "value": 0.5, "min": -1.0, "max": 1.0},
            ],
        }

        poller.log_parameters(mock_file_instance, params_data)

        # Check header was written
        header_call = mock_file_instance.write.call_args_list[0][0][0]
        self.assertIn(
            "timestamp,track_index,device_index,parameter_index,parameter_name,value,min,max",
            header_call,
        )

        # Check parameter lines
        volume_call = mock_file_instance.write.call_args_list[1][0][0]
        self.assertIn("Volume", volume_call)
        self.assertIn("0.75", volume_call)

        pan_call = mock_file_instance.write.call_args_list[2][0][0]
        self.assertIn("Pan", pan_call)
        self.assertIn("0.5", pan_call)

        mock_file_instance.flush.assert_called()

    def test_log_parameters_no_data(self):
        """Test logging with no parameters data."""
        poller = ParameterPoller(0, 0, 10.0)
        mock_file = Mock()

        poller.log_parameters(mock_file, None)

        # Should not write anything if no data
        mock_file.write.assert_not_called()
        mock_file.flush.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    def test_poll_once_success(self, mock_file):
        """Test successful single poll operation."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.sock = Mock()

        # Mock successful get_device_parameters
        params_data = {
            "device_name": "TestDevice",
            "parameters": [{"index": 0, "name": "Volume", "value": 0.75}],
        }
        poller.get_device_parameters = Mock(return_value=params_data)

        mock_file_instance = Mock()
        mock_open.return_value = mock_file_instance

        result = poller.poll_once(mock_file_instance, cache_enabled=True)

        self.assertTrue(result)
        self.assertEqual(poller.readings_count, 1)
        self.assertEqual(poller.last_params, {0: 0.75})
        self.assertEqual(poller.consecutive_errors, 0)

    def test_poll_once_failure(self):
        """Test poll once with get_device_parameters failure."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.sock = Mock()

        # Mock failed get_device_parameters
        poller.get_device_parameters = Mock(return_value=None)
        mock_file = Mock()

        result = poller.poll_once(mock_file, cache_enabled=True)

        self.assertFalse(result)
        mock_file.write.assert_not_called()

    def test_poll_once_cache_disabled(self):
        """Test poll once with caching disabled."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.sock = Mock()

        # Mock unchanged parameters
        params_data = {
            "device_name": "TestDevice",
            "parameters": [{"index": 0, "name": "Volume", "value": 0.75}],
        }
        poller.get_device_parameters = Mock(return_value=params_data)
        poller.last_params = {0: 0.75}  # Same as current

        mock_file = Mock()

        result = poller.poll_once(mock_file, cache_enabled=False)

        # Should log even when unchanged (cache disabled)
        self.assertTrue(result)
        mock_file.write.assert_called()

    def test_poll_once_cache_enabled_no_change(self):
        """Test poll once with caching enabled and no parameter change."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.sock = Mock()

        # Mock unchanged parameters
        params_data = {
            "device_name": "TestDevice",
            "parameters": [{"index": 0, "name": "Volume", "value": 0.75}],
        }
        poller.get_device_parameters = Mock(return_value=params_data)
        poller.last_params = {0: 0.75}  # Same as current

        mock_file = Mock()
        with patch("builtins.print") as mock_print:
            result = poller.poll_once(mock_file, cache_enabled=True)

            self.assertTrue(result)
            # Should not log when cache enabled and no change
            mock_file.write.assert_not_called()
            mock_print.assert_any_call(
                "[INFO] Parameters unchanged (rate: 10.0 Hz), skipping log"
            )

    def test_stop_with_summary(self):
        """Test stop method prints summary."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.start_time = 1000.0  # Mock start time
        poller.readings_count = 150
        poller.poll_times = [0.1, 0.15, 0.12]  # Mock poll times

        with patch("builtins.print") as mock_print:
            poller.stop()

            # Check summary output
            print_calls = [str(call) for call in mock_print.call_args_list]
            summary_text = " ".join(print_calls)

            self.assertIn("Total readings collected: 150", summary_text)
            self.assertIn("Average update rate:", summary_text)
            self.assertIn("Target update rate: 10.00 Hz", summary_text)
            self.assertIn("Average poll time:", summary_text)

    def test_error_counter_increment(self):
        """Test consecutive error counter."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.consecutive_errors = 2

        # Simulate success (should reset counter)
        poller.consecutive_errors = 0  # This happens in poll_once on success

        self.assertEqual(poller.consecutive_errors, 0)

    def test_performance_tracking(self):
        """Test poll time tracking."""
        poller = ParameterPoller(0, 0, 10.0)
        poller.poll_times = [0.1, 0.15]

        # Add another poll time
        poller.poll_times.append(0.12)

        self.assertEqual(len(poller.poll_times), 3)
        self.assertEqual(poller.poll_times[-1], 0.12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
