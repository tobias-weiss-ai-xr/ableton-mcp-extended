"""
Setup session node - Create Ableton Live session with tracks and initial configuration.
"""
from typing import List
from agentic_mix.state import GraphState, SessionInfo
from agentic_mix.tools import (
    delete_all_tracks, create_midi_track, set_track_name,
    set_tempo, set_time_signature
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
        track_names = _get_track_names_for_genre(config.genre, config.track_count)

        for i, track_name in enumerate(track_names):
            result = create_midi_track(index=i)
            track_index = result.get("track_index", i)

            set_track_name(track_index, track_name)
            track_indices.append(track_index)

            feedback.append(f"Created track {track_index}: {track_name}")

        # Set tempo
        set_tempo(config.tempo)
        feedback.append(f"Set tempo to {config.tempo} BPM")

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
            tempo=config.tempo,
            time_signature=(4, 4)
        )

        state["session_info"] = session_info
        feedback.append("Session setup complete")

    except Exception as e:
        state["error"] = f"Session setup failed: {str(e)}"
        feedback.append(f"ERROR: {state['error']}")

    return state


def _get_track_names_for_genre(genre: str, track_count: int) -> List[str]:
    """Get appropriate track names for the genre."""
    track_templates = {
        "dub_techno": ["Drums 1", "Drums 2", "Bass", "Chords", "Pads", "FX", "Atmosphere", "Percussion"],
        "house": ["Drums", "Bass", "Chords", "Pads", "Vocals", "FX", "Atmosphere", "Percussion"],
        "techno": ["Drums", "Bass", "Synth 1", "Synth 2", "Atmosphere", "FX", "Pads", "Percussion"],
        "ambient": ["Pads", "Bass", "Atmosphere", "FX", "Percussion", "Texture", "Drone", "Reverbed"],
    }

    templates = track_templates.get(genre, track_templates["dub_techno"])
    return templates[:track_count] if len(templates) >= track_count else templates
