"""Integration test for full audio feedback loop graph execution.

Uses context-manager patching (which works reliably with LangGraph)
to mock the first 4 graph nodes and audio capture.
"""

from contextlib import ExitStack
import time
from unittest.mock import patch

import pytest

from agentic_mix.state import (
    Config, Section, AudioAnalysisData,
    create_session_info, create_track_state, create_playback_metrics,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

class FakeClient(dict):
    """Msgpack-safe dict-based fake Ableton client."""
    def __init__(self):
        super().__init__({"trigger_scene_calls": [], "call_count": 0})
    def __getattr__(self, name):
        # Fall back to dict access for backwards compat with attribute access
        return self[name]
    def trigger_scene(self, scene_index):
        self["trigger_scene_calls"].append(scene_index)
        self["call_count"] += 1


def make_section(index: int, name: str, beat: float,
                 energy: float = 5.0, technique: str = "none") -> Section:
    return Section(
        index=index, name=name, start_beat=beat,
        end_beat=beat + 16.0, energy_level=energy,
        tracks_active=[0, 1, 2] if energy > 3 else [0],
        mixing_technique=technique, scene_index=index,
    )


def make_snapshot(rms: float = 0.5) -> AudioAnalysisData:
    return AudioAnalysisData(
        timestamp=time.time(), bpm=120.0, beat=0.5, rms=rms,
        loudness_lufs=-18.0, key="Fm", key_confidence=0.9,
        spectral_centroid_hz=2000.0, spectral_rolloff_hz=4000.0,
    )


def _run_graph(config, arrangement, snapshot_results=None,
               capture_exceptions=False):
    """Run the graph with mocked first-4-nodes and optional capture.

    Args:
        config: Config dict
        arrangement: List of Section dicts
        snapshot_results: None (returns valid snapshot) or list of return values
        capture_exceptions: If True, capture_audio_snapshot raises Exception
    """
    state = {
        "config": config,
        "session_info": create_session_info(),
        "arrangement": arrangement,
        "track_states": [create_track_state() for _ in range(config["track_count"])],
        "playback_metrics": create_playback_metrics(),
        "feedback": {"history": [], "adaptations": [], "energy_trend": []},
        "errors": [],
        "complete": False,
        "current_section_index": 0,
        "audio_snapshot": None,
        "client": FakeClient(),
    }

    def _noop(s):
        return s

    with ExitStack() as stack:
        # Patch first 4 graph nodes to noop
        stack.enter_context(patch("agentic_mix.graph.configure_node", _noop))
        stack.enter_context(patch("agentic_mix.graph.setup_session_node", _noop))
        stack.enter_context(patch("agentic_mix.graph.generate_clips_node", _noop))
        stack.enter_context(patch("agentic_mix.graph.construct_arrangement_node", _noop))
        # Patch time.sleep in execute_section to skip waits
        stack.enter_context(patch("agentic_mix.nodes.execute_section.time.sleep"))
        # Patch mixing technique resolver to avoid TCP connections to Ableton
        stack.enter_context(
            patch("agentic_mix.nodes.execute_section._resolve_technique_fn",
                  return_value=None)
        )
        # Patch audio capture
        if capture_exceptions:
            mock_cap = stack.enter_context(
                patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
            )
            mock_cap.side_effect = Exception("Simulated capture failure")
        elif snapshot_results is not None:
            mock_cap = stack.enter_context(
                patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
            )
            mock_cap.side_effect = snapshot_results
        else:
            mock_cap = stack.enter_context(
                patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
            )
            mock_cap.return_value = make_snapshot(rms=0.6)

        from agentic_mix.graph import create_mix_pipeline
        app = create_mix_pipeline()
        result = app.invoke(state, config={"configurable": {"thread_id": "test"}})

    return result, state["client"]


# ── Tests ────────────────────────────────────────────────────────────────────

def test_graph_two_sections():
    """2-section graph completes without errors."""
    config = Config(tempo=120, duration_minutes=1, genre="dub_techno",
                    track_count=3, key="Fm", energy_curve="gradual",
                    variation_level=0.5, section_duration_beats=16.0)
    arrangement = [
        make_section(0, "intro", 0.0, energy=3.0, technique="none"),
        make_section(1, "drop", 16.0, energy=8.0, technique="dub_drop"),
    ]
    result, client = _run_graph(config, arrangement)

    # current_section_index is post-incremented: 0→1→2
    assert result["current_section_index"] == 2
    assert len(result["feedback"]["history"]) == 2
    assert len(result["feedback"]["energy_trend"]) == 2
    assert len(result["errors"]) == 0
    assert len(client.trigger_scene_calls) == 2
    assert len(result["playback_metrics"]["section_transitions"]) == 2


def test_graph_three_sections():
    """3-section graph loops back correctly."""
    config = Config(tempo=120, duration_minutes=1, genre="dub_techno",
                    track_count=3, key="Fm", energy_curve="gradual",
                    variation_level=0.5, section_duration_beats=16.0)
    arrangement = [
        make_section(0, "intro", 0.0, energy=3.0),
        make_section(1, "groove", 16.0, energy=5.0, technique="bass_forward"),
        make_section(2, "drop", 32.0, energy=8.0, technique="dub_drop"),
    ]
    result, client = _run_graph(config, arrangement)

    assert len(result["feedback"]["history"]) == 3
    assert len(result["feedback"]["energy_trend"]) == 3
    assert len(result["playback_metrics"]["section_transitions"]) == 3
    assert len(client.trigger_scene_calls) == 3
    assert len(result["errors"]) == 0
    # Default mock returns rms=0.6 (within safe range, no adaptations triggered)


def test_audio_feedback_adapts_next_section():
    """Low RMS triggers energy_boost adaptation."""
    config = Config(tempo=120, duration_minutes=1, genre="dub_techno",
                    track_count=3, key="Fm", energy_curve="gradual",
                    variation_level=0.5, section_duration_beats=16.0)
    arrangement = [
        make_section(0, "intro", 0.0, energy=3.0),
        make_section(1, "groove", 16.0, energy=5.0, technique="bass_forward"),
        make_section(2, "drop", 32.0, energy=8.0, technique="dub_drop"),
    ]
    result, _ = _run_graph(config, arrangement, snapshot_results=[
        make_snapshot(rms=0.2),
        make_snapshot(rms=0.6),
        make_snapshot(rms=0.6),
    ])

    adaptation_types = [a["type"] for a in result["feedback"]["adaptations"]]
    assert "energy_boost" in adaptation_types

    assert result["feedback"]["energy_trend"][0] == pytest.approx(0.2)
    assert result["feedback"]["energy_trend"][1] == pytest.approx(0.6)


def test_graph_handles_capture_failure():
    """Graph doesn't crash when audio capture fails."""
    config = Config(tempo=120, duration_minutes=1, genre="dub_techno",
                    track_count=3, key="Fm", energy_curve="gradual",
                    variation_level=0.5, section_duration_beats=16.0)
    arrangement = [
        make_section(0, "intro", 0.0, energy=3.0, technique="none"),
        make_section(1, "drop", 16.0, energy=8.0, technique="dub_drop"),
    ]
    result, _ = _run_graph(config, arrangement, capture_exceptions=True)

    assert len(result["errors"]) >= 1
    assert any("analyze_section_node" in e for e in result["errors"])
    # When capture fails, history stays empty (snapshot stored only on success)
    assert len(result["feedback"]["history"]) == 0


def test_more_sections_routing():
    """All sections appear in history in order."""
    config = Config(tempo=120, duration_minutes=1, genre="dub_techno",
                    track_count=3, key="Fm", energy_curve="gradual",
                    variation_level=0.5, section_duration_beats=16.0)
    arrangement = [
        make_section(0, "intro", 0.0, energy=3.0),
        make_section(1, "groove", 16.0, energy=5.0, technique="bass_forward"),
        make_section(2, "drop", 32.0, energy=8.0, technique="dub_drop"),
    ]
    result, _ = _run_graph(config, arrangement)

    history_indices = [h[0] for h in result["feedback"]["history"]]
    assert history_indices == [0, 1, 2]
