"""Unit tests for Audio Analysis MCP Tools.

Tests the device name search helper and tool implementation functions using mocks.
Full integration requires VB-Cable loopback (can't test in CI).
"""

import json
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def mock_sd_devices():
    """Mock sounddevice query_devices to return test devices."""
    devices = [
        {"name": "VB-Audio Cable Output", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "VoiceMeeter Output", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "Speakers (Realtek)", "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch("sounddevice.query_devices", return_value=devices):
        yield


class TestDeviceNameSearch:
    """Test the device name search helper."""

    def test_find_vb_cable(self, mock_sd_devices):
        """Should find VB-Audio Cable by substring."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name

        idx = _find_device_by_name("CABLE")
        assert idx == 0

    def test_find_voice_meter(self, mock_sd_devices):
        """Should find VoiceMeeter by substring."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name

        idx = _find_device_by_name("Voice")
        assert idx == 1

    def test_find_case_insensitive(self, mock_sd_devices):
        """Should match case-insensitively."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name

        idx = _find_device_by_name("cable")
        assert idx == 0

    def test_no_match(self, mock_sd_devices):
        """Should return None for non-existent device."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name

        idx = _find_device_by_name("NonExistent")
        assert idx is None

    def test_skips_output_only(self, mock_sd_devices):
        """Should skip devices with no input channels."""
        from MCP_Server.audio_analysis_tools import _find_device_by_name

        idx = _find_device_by_name("Realtek")
        assert idx is None


class TestImplFunctions:
    """Test module-level _impl_* functions with mocked analyzer state."""

    @pytest.fixture
    def mock_analyzer(self):
        """Create a mock AudioAnalyzer representing a started session."""
        mock = MagicMock()
        mock._running = True
        mock._device_index = 0
        mock.config.sample_rate = 44100
        mock.config.buffer_size = 2048
        mock.config.analysis_features = {
            "bpm": True,
            "key": True,
            "spectral": True,
            "loudness": True,
        }
        mock.get_analysis.return_value = {
            "bpm": 126.0,
            "beat": True,
            "rms": 0.042,
            "key": "F",
            "key_confidence": 0.85,
            "spectral_centroid": 1200.0,
            "spectral_rolloff": 4500.0,
            "loudness_lufs": -14.5,
            "timestamp": 1234567890.0,
        }
        return mock

    # --- _impl_get ---

    def test_get_not_running(self):
        """_impl_get should return not_running when analyzer is None."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = None
        tools._start_time = None

        result = tools._impl_get()
        data = json.loads(result)
        assert data["status"] == "not_running"

    def test_get_returns_analysis(self, mock_analyzer):
        """_impl_get should return formatted analysis JSON."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = mock_analyzer

        result = tools._impl_get()
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["bpm"] == 126.0
        assert data["key"] == "F"
        assert data["beat"] is True
        assert data["loudness_lufs"] == -14.5

    # --- _impl_status ---

    def test_status_running(self, mock_analyzer):
        """_impl_status should return full state when running."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = mock_analyzer

        result = tools._impl_status()
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["running"] is True
        assert data["sample_rate"] == 44100
        assert data["features"]["bpm"] is True

    def test_status_not_running(self):
        """_impl_status should return running=False when analyzer is None."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = None

        result = tools._impl_status()
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["running"] is False
        assert data["device_index"] is None

    # --- _impl_configure ---

    def test_configure_toggles_features(self, mock_analyzer):
        """_impl_configure should toggle specified features."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = mock_analyzer

        result = tools._impl_configure(features={"bpm": False, "loudness": False})
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["features"]["bpm"] is False
        assert data["features"]["loudness"] is False
        assert data["features"]["key"] is True  # unchanged

    def test_configure_no_features(self, mock_analyzer):
        """_impl_configure with no args should return current features."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = mock_analyzer

        result = tools._impl_configure(features=None)
        data = json.loads(result)
        assert data["status"] == "success"
        assert data["features"]["bpm"] is True

    def test_configure_invalid_key(self, mock_analyzer):
        """_impl_configure should reject invalid feature keys."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = mock_analyzer

        result = tools._impl_configure(features={"tempo": True})
        data = json.loads(result)
        assert data["status"] == "error"

    def test_configure_non_bool_value(self, mock_analyzer):
        """_impl_configure should reject non-boolean values."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = mock_analyzer

        result = tools._impl_configure(features={"bpm": "yes"})
        data = json.loads(result)
        assert data["status"] == "error"

    def test_configure_not_running(self):
        """_impl_configure should return not_running when analyzer is None."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = None

        result = tools._impl_configure(features={"bpm": False})
        data = json.loads(result)
        assert data["status"] == "not_running"

    # --- _impl_stop ---

    def test_stop_already_stopped(self):
        """_impl_stop should be idempotent — return not_running."""
        import MCP_Server.audio_analysis_tools as tools

        tools._analyzer = None
        tools._start_time = None

        result = tools._impl_stop()
        data = json.loads(result)
        assert data["status"] == "not_running"
