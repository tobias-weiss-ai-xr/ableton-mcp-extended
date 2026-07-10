"""Tests for analyze section node"""

import pytest
from unittest.mock import patch


@pytest.fixture
def sample_audio_snapshot():
    from agentic_mix.state import AudioAnalysisData
    return AudioAnalysisData(
        timestamp=1.0, bpm=120.0, beat=1.0, rms=0.6,
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, loudness_lufs=-18.0
    )


@patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
def test_analyze_section_node_captures_and_stores(mock_capture, sample_audio_snapshot):
    """Capture audio, store in feedback history"""

    from agentic_mix.nodes.analyze_section import analyze_section_node
    from agentic_mix.state import Section

    mock_capture.return_value = sample_audio_snapshot
    sections = [
        Section(index=0, name="intro", start_beat=0.0, end_beat=16.0, energy_level=3.0,
                tracks_active=[], mixing_technique="none", scene_index=0),
        Section(index=1, name="groove_a", start_beat=16.0, end_beat=32.0, energy_level=5.0,
                tracks_active=[], mixing_technique="none", scene_index=1),
    ]

    state = {
        "current_section_index": 0,
        "arrangement": sections,
        "config": {"tempo": 120},
        "audio_snapshot": None,
        "feedback": {
            "history": [],
            "adaptations": [],
            "energy_trend": [],
        },
        "errors": [],
    }

    result = analyze_section_node(state)

    mock_capture.assert_called_once()

    assert len(result["feedback"]["history"]) == 1
    section_idx, snapshot = result["feedback"]["history"][0]
    assert section_idx == 0
    assert snapshot["rms"] == 0.6
    assert len(result["feedback"]["energy_trend"]) == 1
    assert result["feedback"]["energy_trend"][0] == 0.6


@patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
def test_analyze_section_node_adapts_next_section(mock_capture, sample_audio_snapshot):
    """Quiet RMS triggers energy boost applied to next section"""

    from agentic_mix.nodes.analyze_section import analyze_section_node
    from agentic_mix.state import Section, AudioAnalysisData

    quiet_snapshot = AudioAnalysisData(
        timestamp=1.0, bpm=120.0, beat=1.0, rms=0.2,
        spectral_centroid_hz=5000.0, spectral_rolloff_hz=1000.0,
        key=None, key_confidence=None, loudness_lufs=-20.0
    )

    mock_capture.return_value = quiet_snapshot

    sections = [
        Section(index=0, name="intro", start_beat=0.0, end_beat=16.0, energy_level=3.0,
                tracks_active=[], mixing_technique="none", scene_index=0),
        Section(index=1, name="groove_a", start_beat=16.0, end_beat=32.0, energy_level=5.0,
                tracks_active=[], mixing_technique="none", scene_index=1),
    ]

    state = {
        "current_section_index": 0,
        "arrangement": sections,
        "config": {"tempo": 120},
        "audio_snapshot": None,
        "feedback": {"history": [], "adaptations": [], "energy_trend": []},
        "errors": [],
    }

    result = analyze_section_node(state)

    assert len(result["feedback"]["adaptations"]) > 0
    energy_adapt = next(
        (a for a in result["feedback"]["adaptations"] if a["type"] == "energy_boost"),
        None,
    )
    assert energy_adapt is not None
    assert energy_adapt["target_section"] == 1

    assert result["arrangement"][1]["energy_level"] > 5.0


@patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
def test_analyze_section_node_handles_invalid_snapshot(mock_capture):
    """Invalid readings record error but don't crash"""

    from agentic_mix.nodes.analyze_section import analyze_section_node
    from agentic_mix.state import Section, AudioAnalysisData

    invalid_snapshot = AudioAnalysisData(
        timestamp=1.0, rms=1.5,
        spectral_centroid_hz=0.0,
        spectral_rolloff_hz=0.0,
        key=None, key_confidence=None, bpm=0.0, beat=0.0, loudness_lufs=0.0
    )

    mock_capture.return_value = invalid_snapshot

    sections = [
        Section(index=0, name="intro", start_beat=0.0, end_beat=16.0, energy_level=3.0,
                tracks_active=[], mixing_technique="none", scene_index=0),
    ]

    state = {
        "current_section_index": 0,
        "arrangement": sections,
        "config": {"tempo": 120},
        "audio_snapshot": None,
        "feedback": {"history": [], "adaptations": [], "energy_trend": []},
        "errors": [],
    }

    result = analyze_section_node(state)

    assert len(result["errors"]) > 0


@patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
def test_analyze_section_node_last_section_no_adaptation(mock_capture, sample_audio_snapshot):
    """Last section doesn't adapt (no next section to modify)"""

    from agentic_mix.nodes.analyze_section import analyze_section_node
    from agentic_mix.state import Section

    mock_capture.return_value = sample_audio_snapshot

    sections = [
        Section(index=0, name="outro", start_beat=96.0, end_beat=112.0, energy_level=3.0,
                tracks_active=[], mixing_technique="none", scene_index=7),
    ]

    state = {
        "current_section_index": 0,
        "arrangement": sections,
        "config": {"tempo": 120},
        "audio_snapshot": None,
        "feedback": {"history": [], "adaptations": [], "energy_trend": []},
        "errors": [],
    }

    result = analyze_section_node(state)

    assert len(result["feedback"]["history"]) == 1
    assert len(result["feedback"]["adaptations"]) == 0
