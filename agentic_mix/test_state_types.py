"""Test state type definitions for audio feedback system"""

import pytest
from agentic_mix.state import (
    AudioAnalysisData,
    Adaptation,
    FeedbackState,
    GraphState,
    create_config,
    create_session_info,
    create_playback_metrics,
    create_track_state,
)


def test_audio_analysis_data_type():
    """Test AudioAnalysisData TypedDict structure"""
    snapshot: AudioAnalysisData = {
        "timestamp": 1234567890.0,
        "bpm": 126.0,
        "beat": 1.2,
        "rms": 0.75,
        "loudness_lufs": -12.5,
        "key": "Fm",
        "key_confidence": 0.85,
        "spectral_centroid_hz": 5000.0,
        "spectral_rolloff_hz": 8000.0,
    }
    
    assert snapshot["timestamp"] == 1234567890.0
    assert snapshot["bpm"] == 126.0
    assert snapshot["rms"] == 0.75
    
    # Test with optional fields as None
    minimal_snapshot: AudioAnalysisData = {
        "timestamp": 1234567890.0,
        "bpm": None,
        "beat": None,
        "rms": 0.75,
        "loudness_lufs": -12.5,
        "key": None,
        "key_confidence": None,
        "spectral_centroid_hz": 5000.0,
        "spectral_rolloff_hz": 8000.0,
    }
    
    assert minimal_snapshot["bpm"] is None
    assert minimal_snapshot["key"] is None


def test_adaptation_type():
    """Test Adaptation TypedDict structure"""
    adaptation: Adaptation = {
        "type": "energy_boost",
        "target_section": 3,
        "value": 0.8,
        "tracks": [0, 2, 4],
        "from_technique": "dub_drop",
        "to_technique": "bass_forward",
    }
    
    assert adaptation["type"] == "energy_boost"
    assert adaptation["target_section"] == 3
    assert adaptation["value"] == 0.8
    assert adaptation["tracks"] == [0, 2, 4]
    
    # Test minimal adaptation without optional fields
    minimal_adaptation: Adaptation = {
        "type": "filter_adjust_down",
        "target_section": 2,
        "value": 0.3,
        "tracks": None,
        "from_technique": None,
        "to_technique": None,
    }
    
    assert minimal_adaptation["tracks"] is None
    assert minimal_adaptation["from_technique"] is None


def test_feedback_state_type():
    """Test FeedbackState TypedDict structure"""
    snapshot1: AudioAnalysisData = {
        "timestamp": 1234567890.0,
        "bpm": 126.0,
        "beat": 1.0,
        "rms": 0.75,
        "loudness_lufs": -12.5,
        "key": "Fm",
        "key_confidence": 0.85,
        "spectral_centroid_hz": 5000.0,
        "spectral_rolloff_hz": 8000.0,
    }
    
    snapshot2: AudioAnalysisData = {
        "timestamp": 1234567892.0,
        "bpm": 126.0,
        "beat": 1.2,
        "rms": 0.82,
        "loudness_lufs": -11.0,
        "key": "Fm",
        "key_confidence": 0.88,
        "spectral_centroid_hz": 5200.0,
        "spectral_rolloff_hz": 8200.0,
    }
    
    adaptation1: Adaptation = {
        "type": "energy_boost",
        "target_section": 2,
        "value": 0.8,
        "tracks": None,
        "from_technique": None,
        "to_technique": None,
    }
    
    feedback: FeedbackState = {
        "history": [(0, snapshot1), (1, snapshot2)],
        "adaptations": [adaptation1],
        "energy_trend": [0.75, 0.82],
    }
    
    assert len(feedback["history"]) == 2
    assert feedback["history"][0] == (0, snapshot1)
    assert len(feedback["adaptations"]) == 1
    assert feedback["adaptations"][0]["type"] == "energy_boost"
    assert feedback["energy_trend"] == [0.75, 0.82]


def test_graph_state_with_new_fields():
    """Test GraphState includes new audio feedback fields"""
    config = create_config()
    session_info = create_session_info()
    playback_metrics = create_playback_metrics()
    
    # Create minimal GraphState with new fields
    state: GraphState = {
        "config": config,
        "session_info": session_info,
        "arrangement": [],
        "track_states": [],
        "playback_metrics": playback_metrics,
        "feedback": [],
        "errors": [],
        "complete": False,
        "current_section_index": 0,
        "audio_snapshot": None,
    }
    
    # Verify new fields exist and have correct values
    assert "current_section_index" in state
    assert state["current_section_index"] == 0
    
    assert "audio_snapshot" in state
    assert state["audio_snapshot"] is None
    
    # Test with actual audio snapshot
    snapshot: AudioAnalysisData = {
        "timestamp": 1234567890.0,
        "bpm": 126.0,
        "beat": 1.0,
        "rms": 0.75,
        "loudness_lufs": -12.5,
        "key": "Fm",
        "key_confidence": 0.85,
        "spectral_centroid_hz": 5000.0,
        "spectral_rolloff_hz": 8000.0,
    }
    
    state_with_audio: GraphState = {
        "config": config,
        "session_info": session_info,
        "arrangement": [],
        "track_states": [],
        "playback_metrics": playback_metrics,
        "feedback": [],
        "errors": [],
        "complete": False,
        "current_section_index": 1,
        "audio_snapshot": snapshot,
    }
    
    assert state_with_audio["current_section_index"] == 1
    assert state_with_audio["audio_snapshot"] == snapshot
    assert state_with_audio["audio_snapshot"]["rms"] == 0.75


if __name__ == "__main__":
    pytest.main([__file__, "-v"])