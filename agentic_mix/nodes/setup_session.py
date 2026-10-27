"""
Setup session node - Create Ableton Live session with tracks and initial configuration.
"""
from typing import List, Tuple
from agentic_mix.state import GraphState, SessionInfo
from agentic_mix.tools import (
    delete_all_tracks, create_midi_track, set_track_name,
    set_tempo, set_time_signature,
    load_instrument_or_effect,
)
from agentic_mix.sound_sets import (
    track_names_for, chain_for_track, INSTRUMENT_URIS, FX_URIS
)


def setup_session_node(state: GraphState) -> GraphState:
    """
    Create Ableton session with configured tracks.

    This node:
    1. Clears existing session
    2. Creates MIDI tracks
    3. Sets track names based on genre
    4. Configures tempo and time signature
    """
    config = state["config"]
    feedback = state["feedback"]

    feedback.append("Setting up Ableton session...")

    try:
        # Clear existing session
        delete_all_tracks()
        feedback.append("Cleared existing session")

        # Create tracks
        track_indices = []
        track_names = track_names_for(config["genre"], config["track_count"])

        for i, track_name in enumerate(track_names):
            result = create_midi_track(index=i)
            track_index = result.get("track_index", i)

            set_track_name(track_index, track_name)

            # Load instrument + effect chain for this role
            import time
            inst_uri, fx_chain = chain_for_track(track_name)
            load_instrument_or_effect(track_index, inst_uri)
            for fx_key in fx_chain:
                load_instrument_or_effect(track_index, FX_URIS[fx_key])
                time.sleep(1.2)  # inter-FX delay (Live breathing room)
            time.sleep(0.5)  # final yield

            track_indices.append(track_index)
            feedback.append(f"Created track {track_index}: {track_name} ({inst_uri} + {len(fx_chain)} FX)")

        # delete_all_tracks keeps one survivor track (Live needs >=1); it
        # drifts to the end - remove it now that it is no longer the last
        from agentic_mix.tools import get_all_tracks, delete_track
        extras = len(get_all_tracks()) - len(track_names)
        for i in range(len(get_all_tracks()) - 1, len(track_names) - 1, -1):
            delete_track(i)
        if extras > 0:
            feedback.append(f"Removed {extras} leftover track(s)")

        # Set tempo
        set_tempo(config["tempo"])
        feedback.append(f"Set tempo to {config['tempo']} BPM")

        # Set time signature
        set_time_signature(4, 4)

        # Get return tracks
        from agentic_mix.tools import get_return_tracks
        return_tracks = get_return_tracks()
        return_track_indices = [rt["index"] for rt in return_tracks]

        # Update session info
        session_info = SessionInfo(
            initialized=True,
            track_indices=track_indices,
            scene_indices=[],
            return_track_indices=return_track_indices,
            tempo=config["tempo"],
            time_signature=(4, 4)
        )

        state["session_info"] = session_info
        feedback.append("Session setup complete")

    except Exception as e:
        state["errors"].append(f"Session setup failed: {str(e)}")
        feedback.append(f"ERROR: {state['errors'][-1]}")

    return state
