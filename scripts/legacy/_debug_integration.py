"""Debug script for integration test"""
from contextlib import ExitStack
from unittest.mock import patch
import time

from agentic_mix.state import (
    Config, Section, create_session_info, create_track_state,
    create_playback_metrics,
)


class FakeClient(dict):
    """Dict-based fake client (msgpack-safe)."""
    def __init__(self):
        super().__init__({"trigger_scene_calls": [], "call_count": 0})
    def trigger_scene(self, scene_index):
        self["trigger_scene_calls"].append(scene_index)
        self["call_count"] += 1


config = Config(tempo=120, duration_minutes=1, genre="dub_techno",
                track_count=3, key="Fm", energy_curve="gradual",
                variation_level=0.5, section_duration_beats=16.0)

arrangement = [
    Section(index=0, name="intro", start_beat=0.0, end_beat=16.0,
            energy_level=3.0, tracks_active=[0],
            mixing_technique="none", scene_index=0),
    Section(index=1, name="drop", start_beat=16.0, end_beat=32.0,
            energy_level=8.0, tracks_active=[0, 1, 2],
            mixing_technique="dub_drop", scene_index=1),
]

state = {
    "config": config,
    "session_info": create_session_info(),
    "arrangement": arrangement,
    "track_states": [create_track_state() for _ in range(3)],
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


t0 = time.time()

print(f"Starting at {time.time()-t0:.2f}s", flush=True)

with ExitStack() as stack:
    stack.enter_context(patch("agentic_mix.graph.configure_node", _noop))
    stack.enter_context(patch("agentic_mix.graph.setup_session_node", _noop))
    stack.enter_context(patch("agentic_mix.graph.generate_clips_node", _noop))
    stack.enter_context(patch("agentic_mix.graph.construct_arrangement_node", _noop))
    stack.enter_context(patch("agentic_mix.nodes.execute_section.time.sleep"))
    # Patch mixing technique resolver to avoid TCP connections
    stack.enter_context(
        patch("agentic_mix.nodes.execute_section._resolve_technique_fn",
              return_value=None)
    )
    mock_cap = stack.enter_context(
        patch("agentic_mix.nodes.analyze_section.capture_audio_snapshot")
    )
    mock_cap.return_value = {
        "timestamp": 1.0, "bpm": 120.0, "beat": 0.5, "rms": 0.6,
        "loudness_lufs": -18.0, "key": "Fm", "key_confidence": 0.9,
        "spectral_centroid_hz": 2000.0, "spectral_rolloff_hz": 4000.0,
    }
    print(f"Patched at {time.time()-t0:.2f}s", flush=True)

    print(f"Importing at {time.time()-t0:.2f}s", flush=True)
    from agentic_mix.graph import create_mix_pipeline
    print(f"Creating at {time.time()-t0:.2f}s", flush=True)
    app = create_mix_pipeline()

    print(f"Graph created: {time.time()-t0:.2f}s", flush=True)
    print(f"Nodes: {list(app.nodes.keys())}", flush=True)

    try:
        result = app.invoke(state, config={"configurable": {"thread_id": "test"}})
        print(f"Done: {time.time()-t0:.2f}s", flush=True)
        print(f"History: {len(result['feedback']['history'])}", flush=True)
        print(f"Errors: {result['errors']}", flush=True)
    except Exception as e:
        print(f"FAILED after {time.time()-t0:.2f}s: {e}", flush=True)
        import traceback
        traceback.print_exc()
