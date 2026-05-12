"""
Session setup utilities for Ableton dub techno automation.

Functions:
    - delete_all_tracks(): Remove all tracks from session
    - create_midi_track(index): Create a MIDI track at index
    - set_track_name(index, name): Rename track to name
    - verify_track_count(expected): Assert track count matches expected
    - create_dub_techno_session(): Create complete 6-track dub techno session
    - setup_tracks(): Name and load instruments on all 6 tracks
    - configure_tempo(): Set tempo to 80 BPM with 4/4 time signature

Usage:
    from session_setup import create_dub_techno_session, setup_tracks, configure_tempo
    create_dub_techno_session()
    setup_tracks()
    configure_tempo()
"""

import logging
from typing import Dict, Any, List, Optional

from mcp_client import MCPClientTCP, MCPClientUDP

logger = logging.getLogger(__name__)


# =============================================================================
# Core Session Setup (Task 3)
# =============================================================================

def delete_all_tracks() -> Dict[str, Any]:
    """
    Delete all tracks from the Ableton session.

    Returns:
        Dictionary with 'deleted' (count removed) and 'tracks' (remaining count)

    Note:
        MUST be called before creating new tracks to ensure clean slate.
    """
    client = MCPClientTCP()
    try:
        response = client.send_command("delete_all_tracks", {})
        logger.info(f"Deleted all tracks: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to delete all tracks: {e}")
        raise


def create_midi_track(index: int = -1) -> Dict[str, Any]:
    """
    Create a new MIDI track at the specified index.

    Args:
        index: Track index to insert at (-1 = end of list)

    Returns:
        Dictionary with 'created' (bool) and 'track_index' (int)
    """
    client = MCPClientTCP()
    try:
        response = client.send_command("create_midi_track", {"index": index})
        logger.info(f"Created MIDI track at index {index}: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to create MIDI track at index {index}: {e}")
        raise


def set_track_name(track_index: int, name: str) -> Dict[str, Any]:
    """
    Set the name of a track.

    Args:
        track_index: Index of track to rename
        name: New name for the track

    Returns:
        Response dictionary (typically empty on success)
    """
    if not name or not name.strip():
        raise ValueError("Track name cannot be empty")
    client = MCPClientTCP()
    try:
        response = client.send_command("set_track_name", {
            "track_index": track_index,
            "name": name
        })
        logger.info(f"Set track {track_index} name to '{name}'")
        return response
    except Exception as e:
        logger.error(f"Failed to set track {track_index} name to '{name}': {e}")
        raise


def verify_track_count(expected: int) -> bool:
    """
    Verify that the session has the expected number of tracks.

    Args:
        expected: Expected track count

    Returns:
        True if count matches, False otherwise
    """
    client = MCPClientTCP()
    try:
        response = client.send_command("get_all_tracks", {})
        actual = len(response) if isinstance(response, list) else 0
        matches = actual == expected
        logger.info(f"Track count verification: expected={expected}, actual={actual}, matches={matches}")
        return matches
    except Exception as e:
        logger.error(f"Failed to verify track count: {e}")
        return False


# =============================================================================
# Complete Session Creation (Task 8, 9, 10)
# =============================================================================

def create_dub_techno_session() -> Dict[str, Any]:
    """
    Create a complete dub techno session from scratch.

    Creates 6 MIDI tracks:
        0: Drums
        1: Bass
        2: Pads
        3: Percussion
        4: Dub FX
        5: Return (audio effects)

    Returns:
        Dictionary with session info and track indices

    Note:
        Calls delete_all_tracks() first to ensure clean slate.
    """
    logger.info("Creating dub techno session...")
    track_names = ["Drums", "Bass", "Pads", "Percussion", "Dub FX", "Return"]

    # Clean slate first
    delete_all_tracks()

    # Create 6 tracks
    for i, name in enumerate(track_names):
        create_midi_track(i if i < 5 else -1)  # Insert at specific indices for first 5

    # Rename all tracks
    for i, name in enumerate(track_names):
        set_track_name(i, name)

    logger.info(f"Created dub techno session with {len(track_names)} tracks")
    return {
        "tracks_created": len(track_names),
        "track_names": track_names,
        "track_indices": list(range(len(track_names)))
    }


def setup_tracks() -> Dict[str, Any]:
    """
    Name and load instruments on all 6 tracks.

    Drum kit: Uses specific FileId (not empty Drum Rack)
    Bass: Analog or Operator
    Pads: Analog or Operator
    Percussion: Impulse or Drum Rack
    Dub FX: Operator
    Return: Audio effects (Reverb, Delay)

    Returns:
        Dictionary with track setup results
    """
    # Track 0: Drums - specific drum kit FileId per AGENTS.md
    drum_kit_uri = "query:Drums#FileId_58622"  # Specific kit, not empty rack

    # Track 1: Bass
    bass_uri = "query:Synths#Analog"

    # Track 2: Pads
    pads_uri = "query:Synths#Operator"

    # Track 3: Percussion
    perc_uri = "query:Drums#Impulse"

    # Track 4: Dub FX
    fx_uri = "query:Synths#Operator"

    # Track 5: Return - audio effects only
    return_uri = ""  # No instrument, just effects

    track_configs = [
        (0, "Drums", drum_kit_uri),
        (1, "Bass", bass_uri),
        (2, "Pads", pads_uri),
        (3, "Percussion", perc_uri),
        (4, "Dub FX", fx_uri),
        (5, "Return", return_uri),
    ]

    results = {}
    client = MCPClientTCP()

    for track_idx, track_name, uri in track_configs:
        # Set track name
        try:
            client.send_command("set_track_name", {
                "track_index": track_idx,
                "name": track_name
            })
        except Exception as e:
            logger.warning(f"Failed to name track {track_idx}: {e}")

        # Load instrument if URI provided
        # NOTE: No need to delete default device - load_instrument_or_effect replaces it automatically
        if uri:
            try:
                client.send_command("load_instrument_or_effect", {
                    "track_index": track_idx,
                    "uri": uri
                })
                logger.info(f"Loaded {uri} on track {track_idx}")
                results[track_name] = {"loaded": True, "uri": uri}
            except Exception as e:
                logger.warning(f"Failed to load instrument on track {track_idx}: {e}")
                results[track_name] = {"loaded": False, "error": str(e)}
        else:
            results[track_name] = {"loaded": False, "reason": "no_instrument"}

    return results


def configure_tempo(tempo: float = 80.0, time_signature: tuple = (4, 4)) -> Dict[str, Any]:
    """
    Configure session tempo and time signature.

    Args:
        tempo: BPM (default 80.0 for mid-range dub)
        time_signature: Tuple of (numerator, denominator), default (4, 4)

    Returns:
        Dictionary with tempo and time signature settings
    """
    if not 75 <= tempo <= 85:
        raise ValueError(f"Tempo {tempo} outside allowed range 75-85 BPM")

    client = MCPClientTCP()
    results = {}

    # Set tempo
    try:
        client.send_command("set_tempo", {"tempo": tempo})
        results["tempo"] = tempo
        logger.info(f"Set tempo to {tempo} BPM")
    except Exception as e:
        logger.error(f"Failed to set tempo: {e}")
        results["tempo_error"] = str(e)

    # Set time signature
    try:
        client.send_command("set_time_signature", {
            "numerator": time_signature[0],
            "denominator": time_signature[1]
        })
        results["time_signature"] = time_signature
        logger.info(f"Set time signature to {time_signature[0]}/{time_signature[1]}")
    except Exception as e:
        logger.error(f"Failed to set time signature: {e}")
        results["time_signature_error"] = str(e)

    # Set global quantization to 1 Bar
    try:
        client.send_command("set_global_quantization", {"value": "1 Bar"})
        results["quantization"] = "1 Bar"
        logger.info("Set global quantization to 1 Bar")
    except Exception as e:
        logger.error(f"Failed to set quantization: {e}")
        results["quantization_error"] = str(e)

    return results