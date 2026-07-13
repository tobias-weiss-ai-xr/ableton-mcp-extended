"""Tests for audio capture wrapper"""

import pytest
from unittest.mock import patch


@patch('agentic_mix.audio_capture.audio_analysis_start')
@patch('agentic_mix.audio_capture.audio_analysis_get')
@patch('agentic_mix.audio_capture.audio_analysis_stop')
def test_capture_audio_snapshot_success(mock_stop, mock_get, mock_start):
    """Capture successful audio snapshot via MCP"""

    from agentic_mix.audio_capture import capture_audio_snapshot

    mock_start.return_value = {"running": True}
    mock_get.return_value = {
        "bpm": 120.5,
        "beat": 3.0,
        "rms": 0.5,
        "key": "Am",
        "key_confidence": 0.8,
        "spectral_centroid": 4203.2,
        "spectral_rolloff": 892.1,
        "loudness_lufs": -16.4,
    }

    config = {"tempo": 120}
    result = capture_audio_snapshot(config)

    mock_start.assert_called_once()
    mock_get.assert_called_once()
    mock_stop.assert_called_once()

    assert result["timestamp"] > 0
    assert result["bpm"] == 120.5
    assert result["rms"] == 0.5
    assert result["key"] == "Am"
    assert result["spectral_centroid_hz"] == 4203.2


@patch('agentic_mix.audio_capture.audio_analysis_start')
def test_capture_audio_snapshot_start_failure(mock_start):
    """Raise error if audio analyzer fails to start"""

    from agentic_mix.audio_capture import capture_audio_snapshot

    mock_start.return_value = {"running": False}
    config = {"tempo": 120}

    with pytest.raises(RuntimeError, match="Failed to start audio analyzer"):
        capture_audio_snapshot(config)
