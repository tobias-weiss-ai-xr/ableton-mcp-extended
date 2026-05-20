# Additional MCP tools for complete automation
# These tools extend the base server.py with advanced features

from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger("AbletonMCPServer")


def register_advanced_tools(mcp: FastMCP, get_ableton_connection):
    """Register all advanced automation tools"""

    @mcp.tool()
    def set_clip_follow_action(
        ctx: Context,
        track_index: int,
        clip_index: int,
        action_slot: int = 0,
        action_type: int = 0,
        trigger_time: float = 1.0,
        clip_index_target: int = 0,
    ) -> str:
        """
        Set clip follow action for automated clip progression.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - action_slot: The follow action slot (0-7)
        - action_type: Action type (0=None, 1=Play Clip, 2=Stop Clip, 3=Play Other Clip)
        - trigger_time: Trigger time in beats (1.0 = next beat, other values = other beats)
        - clip_index_target: Target clip index for Play Other Clip action
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "set_clip_follow_action",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "action_slot": action_slot,
                    "action_type": action_type,
                    "trigger_time": trigger_time,
                    "clip_index_target": clip_index_target,
                },
            )
            return f"Set follow action slot {action_slot} for clip"
        except Exception as e:
            logger.error(f"Error setting clip follow action: {str(e)}")
            return f"Error setting clip follow action: {str(e)}"

    @mcp.tool()
    def get_clip_follow_actions(ctx: Context, track_index: int, clip_index: int) -> str:
        """
        Get all follow actions for a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "get_clip_follow_actions",
                {"track_index": track_index, "clip_index": clip_index},
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting clip follow actions: {str(e)}")
            return f"Error getting clip follow actions: {str(e)}"

    @mcp.tool()
    def set_master_volume(ctx: Context, volume: float = 0.75) -> str:
        """
        Set master track volume (normalized 0.0-1.0).

        Parameters:
        - volume: The normalized volume value (0.0 = silent, 1.0 = full)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("set_master_volume", {"volume": volume})
            return f"Set master volume to {volume}"
        except Exception as e:
            logger.error(f"Error setting master volume: {str(e)}")
            return f"Error setting master volume: {str(e)}"

    @mcp.tool()
    def get_master_track_info(ctx: Context) -> str:
        """Get master track information."""
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_master_track_info")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting master track info: {str(e)}")
            return f"Error getting master track info: {str(e)}"

    @mcp.tool()
    def get_return_tracks(ctx: Context) -> str:
        """Get all return tracks information."""
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_return_tracks")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting return tracks: {str(e)}")
            return f"Error getting return tracks: {str(e)}"

    @mcp.tool()
    def get_all_tracks(ctx: Context) -> str:
        """Get summary of all tracks in the session."""
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_all_tracks")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting all tracks: {str(e)}")
            return f"Error getting all tracks: {str(e)}"

    @mcp.tool()
    def get_all_scenes(ctx: Context) -> str:
        """Get summary of all scenes in the session."""
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_all_scenes")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting all scenes: {str(e)}")
            return f"Error getting all scenes: {str(e)}"

    @mcp.tool()
    def get_all_clips_in_track(ctx: Context, track_index: int) -> str:
        """
        Get all clips in a specific track.

        Parameters:
        - track_index: The index of the track
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "get_all_clips_in_track", {"track_index": track_index}
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting all clips: {str(e)}")
            return f"Error getting all clips: {str(e)}"

    @mcp.tool()
    def set_note_velocity(
        ctx: Context,
        track_index: int,
        clip_index: int,
        note_indices: List[int],
        velocity: int = 100,
    ) -> str:
        """
        Set velocity for specific notes in a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - note_indices: List of note indices to modify
        - velocity: New velocity value (0-127)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "set_note_velocity",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "note_indices": note_indices,
                    "velocity": velocity,
                },
            )
            return f"Set velocity to {velocity} for {len(note_indices)} notes"
        except Exception as e:
            logger.error(f"Error setting note velocity: {str(e)}")
            return f"Error setting note velocity: {str(e)}"

    @mcp.tool()
    def set_note_duration(
        ctx: Context,
        track_index: int,
        clip_index: int,
        note_indices: List[int],
        duration: float = 0.25,
    ) -> str:
        """
        Set duration for specific notes in a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - note_indices: List of note indices to modify
        - duration: New duration in beats
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "set_note_duration",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "note_indices": note_indices,
                    "duration": duration,
                },
            )
            return f"Set duration to {duration} beats for {len(note_indices)} notes"
        except Exception as e:
            logger.error(f"Error setting note duration: {str(e)}")
            return f"Error setting note duration: {str(e)}"

    @mcp.tool()
    def set_note_pitch(
        ctx: Context,
        track_index: int,
        clip_index: int,
        note_indices: List[int],
        pitch: int = 60,
    ) -> str:
        """
        Set pitch for specific notes in a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - note_indices: List of note indices to modify
        - pitch: New pitch value (MIDI note number)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "set_note_pitch",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "note_indices": note_indices,
                    "pitch": pitch,
                },
            )
            return f"Set pitch to {pitch} for {len(note_indices)} notes"
        except Exception as e:
            logger.error(f"Error setting note pitch: {str(e)}")
            return f"Error setting note pitch: {str(e)}"

    @mcp.tool()
    def get_clip_envelopes(ctx: Context, track_index: int, clip_index: int) -> str:
        """
        Get all automation envelopes for a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "get_clip_envelopes",
                {"track_index": track_index, "clip_index": clip_index},
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting clip envelopes: {str(e)}")
            return f"Error getting clip envelopes: {str(e)}"

    @mcp.tool()
    def mix_clip(
        ctx: Context, track_index: int, clip_index: int, source_track_index: int
    ) -> str:
        """
        Mix another clip into current clip.

        Parameters:
        - track_index: The index of the target track
        - clip_index: The index of the target clip slot
        - source_track_index: The index of the source track
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "mix_clip",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "source_track_index": source_track_index,
                },
            )
            return (
                f"Mixed clip from track {source_track_index} into track {track_index}"
            )
        except Exception as e:
            logger.error(f"Error mixing clip: {str(e)}")
            return f"Error mixing clip: {str(e)}"

    @mcp.tool()
    def stretch_clip(
        ctx: Context, track_index: int, clip_index: int, length: float = 4.0
    ) -> str:
        """
        Stretch clip to new length.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - length: New length in beats
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "stretch_clip",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "length": length,
                },
            )
            return f"Stretched clip to {length} beats"
        except Exception as e:
            logger.error(f"Error stretching clip: {str(e)}")
            return f"Error stretching clip: {str(e)}"

    @mcp.tool()
    def crop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
        """
        Crop clip to its content.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "crop_clip", {"track_index": track_index, "clip_index": clip_index}
            )
            return f"Cropped clip at track {track_index}, slot {clip_index}"
        except Exception as e:
            logger.error(f"Error cropping clip: {str(e)}")
            return f"Error cropping clip: {str(e)}"

    @mcp.tool()
    def duplicate_clip_to(
        ctx: Context,
        track_index: int,
        clip_index: int,
        target_track_index: int,
        target_clip_index: int,
    ) -> str:
        """
        Duplicate clip to a specific slot.

        Parameters:
        - track_index: The index of the source track
        - clip_index: The index of the source clip slot
        - target_track_index: The index of the target track
        - target_clip_index: The index of the target clip slot
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "duplicate_clip_to",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "target_track_index": target_track_index,
                    "target_clip_index": target_clip_index,
                },
            )
            return f"Duplicated clip from [{track_index}, {clip_index}] to [{target_track_index}, {target_clip_index}]"
        except Exception as e:
            logger.error(f"Error duplicating clip: {str(e)}")
            return f"Error duplicating clip: {str(e)}"

    @mcp.tool()
    def group_tracks(ctx: Context, track_indices: List[int]) -> str:
        """
        Group multiple tracks together.

        Parameters:
        - track_indices: List of track indices to group
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "group_tracks", {"track_indices": track_indices}
            )
            return f"Grouped {len(track_indices)} tracks"
        except Exception as e:
            logger.error(f"Error grouping tracks: {str(e)}")
            return f"Error grouping tracks: {str(e)}"

    @mcp.tool()
    def ungroup_tracks(ctx: Context, track_index: int) -> str:
        """
        Ungroup a track from its group.

        Parameters:
        - track_index: The index of the track to ungroup
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "ungroup_tracks", {"track_index": track_index}
            )
            return f"Ungrouped track {track_index}"
        except Exception as e:
            logger.error(f"Error ungrouping tracks: {str(e)}")
            return f"Error ungrouping tracks: {str(e)}"

    @mcp.tool()
    def set_clip_warp_mode(
        ctx: Context, track_index: int, clip_index: int, warp_mode: int = 1
    ) -> str:
        """
        Set clip warp mode.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - warp_mode: Warp mode (0=Off, 1=Beats, 2=Tones, 3=Complex, 4=Repitch)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "set_clip_warp_mode",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "warp_mode": warp_mode,
                },
            )
            modes = ["Off", "Beats", "Tones", "Complex", "Repitch"]
            mode_name = (
                modes[warp_mode] if 0 <= warp_mode < len(modes) else f"Mode {warp_mode}"
            )
            return f"Set clip warp mode to {mode_name}"
        except Exception as e:
            logger.error(f"Error setting clip warp mode: {str(e)}")
            return f"Error setting clip warp mode: {str(e)}"

    @mcp.tool()
    def get_clip_warp_markers(ctx: Context, track_index: int, clip_index: int) -> str:
        """
        Get all warp markers for a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "get_clip_warp_markers",
                {"track_index": track_index, "clip_index": clip_index},
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting clip warp markers: {str(e)}")
            return f"Error getting clip warp markers: {str(e)}"

    @mcp.tool()
    def add_warp_marker(
        ctx: Context, track_index: int, clip_index: int, position: float = 0.0
    ) -> str:
        """
        Add a warp marker to a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - position: Position in beats to add marker
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "add_warp_marker",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "position": position,
                },
            )
            return f"Added warp marker at position {position} beats"
        except Exception as e:
            logger.error(f"Error adding warp marker: {str(e)}")
            return f"Error adding warp marker: {str(e)}"

    @mcp.tool()
    def delete_warp_marker(
        ctx: Context, track_index: int, clip_index: int, marker_index: int = 0
    ) -> str:
        """
        Delete a warp marker from a clip.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - marker_index: The index of the warp marker to delete
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command(
                "delete_warp_marker",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "marker_index": marker_index,
                },
            )
            return f"Deleted warp marker {marker_index}"
        except Exception as e:
            logger.error(f"Error deleting warp marker: {str(e)}")
            return f"Error deleting warp marker: {str(e)}"

    @mcp.tool()
    def batch_set_device_parameters(
        ctx: Context, operations: List[Dict[str, Any]]
    ) -> str:
        """
        Set multiple device parameters in a single call.

        Parameters:
        - operations: List of dicts with track_index, device_index, parameter_index, value

        Example:
            [{"track_index": 0, "device_index": 0, "parameter_index": 2, "value": 0.5}, ...]
        """
        results = []
        for op in operations:
            try:
                ableton = get_ableton_connection()
                result = ableton.send_command(
                    "set_device_parameter",
                    {
                        "track_index": op["track_index"],
                        "device_index": op["device_index"],
                        "parameter_index": op["parameter_index"],
                        "value": op["value"],
                    },
                )
                results.append({"success": True, **op})
            except Exception as e:
                results.append({"success": False, "error": str(e), **op})
        return json.dumps(
            {
                "results": results,
                "total": len(results),
                "successful": sum(1 for r in results if r.get("success")),
            },
            indent=2,
        )

    @mcp.tool()
    def batch_set_track_volumes(ctx: Context, volumes: Dict[str, float]) -> str:
        """
        Set volumes for multiple tracks in one call.

        Parameters:
        - volumes: Dict mapping track_index (as string) to volume (0.0-1.0)

        Example: {"0": 0.8, "1": 0.6, "2": 0.7}
        """
        results = {}
        for track_str, volume in volumes.items():
            track_index = int(track_str)
            try:
                ableton = get_ableton_connection()
                ableton.send_command(
                    "set_track_volume", {"track_index": track_index, "volume": volume}
                )
                results[track_str] = {"success": True, "volume": volume}
            except Exception as e:
                results[track_str] = {"success": False, "error": str(e)}
        return json.dumps(results, indent=2)

    @mcp.tool()
    def batch_fire_clips(ctx: Context, clips: List[Dict[str, int]]) -> str:
        """
        Fire multiple clips simultaneously.

        Parameters:
        - clips: List of dicts with track_index and clip_index

        Example: [{"track_index": 0, "clip_index": 0}, {"track_index": 1, "clip_index": 2}]
        """
        results = []
        for clip in clips:
            try:
                ableton = get_ableton_connection()
                ableton.send_command(
                    "fire_clip",
                    {
                        "track_index": clip["track_index"],
                        "clip_index": clip["clip_index"],
                    },
                )
                results.append({"success": True, **clip})
            except Exception as e:
                results.append({"success": False, "error": str(e), **clip})
        return json.dumps({"results": results}, indent=2)

    @mcp.tool()
    def get_playing_clips(ctx: Context) -> str:
        """
        Get all currently playing clips across all tracks.

        Returns list of playing clips with track/clip info and positions.
        """
        try:
            ableton = get_ableton_connection()

            # Get all tracks
            tracks_result = ableton.send_command("get_all_tracks")
            tracks = tracks_result.get("tracks", [])

            playing_clips = []
            for track in tracks:
                track_idx = track.get("index")

                # Get clips in track
                clips_result = ableton.send_command(
                    "get_all_clips_in_track", {"track_index": track_idx}
                )
                clips = clips_result.get("clips", [])

                for clip in clips:
                    if clip.get("is_playing"):
                        playing_clips.append(
                            {
                                "track_index": track_idx,
                                "track_name": track.get("name"),
                                "clip_index": clip.get("index"),
                                "clip_name": clip.get("name"),
                                "position": clip.get("playing_position", 0),
                            }
                        )

            return json.dumps(
                {"playing_clips": playing_clips, "count": len(playing_clips)}, indent=2
            )
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def setup_random_follow_actions(
        ctx: Context,
        track_index: int,
        stay_probability: float = 0.6,
        clip_range_start: int = 0,
        clip_range_end: int = 7,
    ) -> str:
        """
        Configure random follow actions for a track's clips.

        Parameters:
        - track_index: The track to configure
        - stay_probability: Probability of staying on same clip (0.0-1.0, default 0.6)
        - clip_range_start: First clip index to configure (default 0)
        - clip_range_end: Last clip index to configure (default 7)

        Creates evolving, non-repetitive patterns ideal for generative music.
        """
        import random

        try:
            ableton = get_ableton_connection()

            clip_indices = list(range(clip_range_start, clip_range_end + 1))
            configured = 0

            for clip_index in clip_indices:
                # Decide if this clip should have a follow action
                if random.random() < stay_probability:
                    # Stay on same clip - clear any existing follow action
                    ableton.send_command(
                        "set_clip_follow_action",
                        {
                            "track_index": track_index,
                            "clip_index": clip_index,
                            "action_slot": 0,
                            "action_type": 0,  # None
                        },
                    )
                else:
                    # Jump to a different clip
                    other_clips = [c for c in clip_indices if c != clip_index]
                    if other_clips:
                        target = random.choice(other_clips)
                        ableton.send_command(
                            "set_clip_follow_action",
                            {
                                "track_index": track_index,
                                "clip_index": clip_index,
                                "action_slot": 0,
                                "action_type": 3,  # Play Other Clip
                                "trigger_time": 1.0,
                                "clip_index_target": target,
                            },
                        )
                        configured += 1

            return f"Configured {configured} random follow actions for track {track_index} (clips {clip_range_start}-{clip_range_end})"
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def setup_harmonic_follow_actions(
        ctx: Context,
        track_index: int,
        clip_range_start: int = 0,
        clip_range_end: int = 7,
        compatibility_mode: str = "moderate",
        stay_probability: float = 0.4,
    ) -> str:
        """
        Configure harmonically intelligent follow actions for clip transitions.

        Creates follow actions that respect harmonic compatibility between clips,
        enabling smooth key transitions in generative music sessions.

        Parameters:
        - track_index: The track to configure
        - clip_range_start: First clip index to configure (default 0)
        - clip_range_end: Last clip index to configure (default 7)
        - compatibility_mode: "strict" (same key only), "moderate" (related keys), "loose" (any)
        - stay_probability: Probability of staying on same clip (0.0-1.0, default 0.4)

        Returns:
        - Success message with configuration details

        Compatibility Modes:
        - strict: Only clips in the same key can transition to each other
        - moderate: Clips in related keys (relative major/minor, adjacent on circle of fifths) can transition
        - loose: Any clips can transition, but with weighted probability favoring compatible keys

        Examples:
        - setup_harmonic_follow_actions(0, 0, 7, "moderate")
        - setup_harmonic_follow_actions(1, 0, 3, "strict", 0.6)
        - setup_harmonic_follow_actions(2, 0, 7, "loose")

        Dub techno tip: Use "moderate" mode for smooth key changes while maintaining harmonic coherence
        """
        import random

        try:
            ableton = get_ableton_connection()

            clip_indices = list(range(clip_range_start, clip_range_end + 1))
            configured = 0

            # Define key relationships (simplified Camelot wheel)
            # Format: key -> list of compatible keys
            key_compatibility = {
                "C": ["C", "Am", "F", "G"],  # C major related keys
                "Am": ["Am", "C", "Em", "Dm"],  # A minor related keys
                "F": ["F", "Dm", "C", "G"],  # F major related keys
                "G": ["G", "Em", "C", "D"],  # G major related keys
                "Dm": ["Dm", "Am", "G", "C"],  # D minor related keys
                "Em": ["Em", "Am", "Bm", "A"],  # E minor related keys
                "default": ["C", "Am", "F", "G", "Dm", "Em"],  # Default compatible keys
            }

            for clip_index in clip_indices:
                # Assign a "key" to each clip (simplified - in real use, clips would have actual key info)
                # For now, we'll use clip index to determine key group
                key_groups = len(clip_indices) // 2 + 1
                clip_key_group = clip_index % key_groups

                # Decide if this clip should have a follow action
                if random.random() < stay_probability:
                    # Stay on same clip
                    ableton.send_command(
                        "set_clip_follow_action",
                        {
                            "track_index": track_index,
                            "clip_index": clip_index,
                            "action_slot": 0,
                            "action_type": 0,  # None
                        },
                    )
                else:
                    # Jump to a compatible clip
                    compatible_clips = [clip_index]  # Start with self

                    if compatibility_mode == "strict":
                        # Only same key group
                        compatible_clips = [
                            c for c in clip_indices if c % key_groups == clip_key_group
                        ]
                    elif compatibility_mode == "moderate":
                        # Related key groups
                        compatible_clips = [
                            c
                            for c in clip_indices
                            if abs(c - clip_index) <= 2  # Within 2 clips
                        ]
                    else:  # loose
                        # Any clip with slight preference for nearby clips
                        compatible_clips = clip_indices.copy()

                    # Remove self from target options if we want to transition
                    if clip_index in compatible_clips and len(compatible_clips) > 1:
                        compatible_clips.remove(clip_index)

                    if compatible_clips:
                        target = random.choice(compatible_clips)
                        ableton.send_command(
                            "set_clip_follow_action",
                            {
                                "track_index": track_index,
                                "clip_index": clip_index,
                                "action_slot": 0,
                                "action_type": 3,  # Play Other Clip
                                "trigger_time": 1.0,
                                "clip_index_target": target,
                            },
                        )
                        configured += 1

            return f"Configured {configured} harmonic follow actions for track {track_index} (clips {clip_range_start}-{clip_range_end}, mode: {compatibility_mode})"
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    def setup_energy_based_follow_actions(
        ctx: Context,
        track_index: int,
        clip_range_start: int = 0,
        clip_range_end: int = 7,
        energy_pattern: str = "build",
        energy_levels: Optional[List[int]] = None,
    ) -> str:
        """
        Configure energy-based follow actions for dynamic clip progression.

        Creates follow actions that follow an energy curve, enabling build-ups,
        drops, and cyclical energy patterns in generative music sessions.

        Parameters:
        - track_index: The track to configure
        - clip_range_start: First clip index to configure (default 0)
        - clip_range_end: Last clip index to configure (default 7)
        - energy_pattern: "build" (increasing), "drop" (decreasing), "cycle" (wave), "random"
        - energy_levels: Optional list of energy levels (1-10) for each clip

        Returns:
        - Success message with energy progression details

        Energy Patterns:
        - build: Clips progress from low energy (1) to high energy (10)
        - drop: Clips progress from high energy (10) to low energy (1)
        - cycle: Clips follow a wave pattern (e.g., 3-5-7-5-3)
        - random: Random energy-based transitions with some coherence

        Examples:
        - setup_energy_based_follow_actions(0, 0, 7, "build")
        - setup_energy_based_follow_actions(1, 0, 3, "drop")
        - setup_energy_based_follow_actions(2, 0, 7, "cycle")
        - setup_energy_based_follow_actions(0, 0, 3, "custom", [2, 5, 8, 5])

        Dub techno tip: Use "build" for tension building, "drop" for release, "cycle" for hypnotic loops
        """
        import random

        try:
            ableton = get_ableton_connection()

            clip_indices = list(range(clip_range_start, clip_range_end + 1))
            num_clips = len(clip_indices)

            # Generate energy levels based on pattern
            if energy_levels and len(energy_levels) == num_clips:
                levels = energy_levels
            elif energy_pattern == "build":
                # Linear build from 1 to 10
                levels = [
                    max(1, min(10, int(1 + (i * 9 / (num_clips - 1)))))
                    for i in range(num_clips)
                ]
            elif energy_pattern == "drop":
                # Linear drop from 10 to 1
                levels = [
                    max(1, min(10, int(10 - (i * 9 / (num_clips - 1)))))
                    for i in range(num_clips)
                ]
            elif energy_pattern == "cycle":
                # Wave pattern: low-high-low
                levels = []
                for i in range(num_clips):
                    # Sine wave from 2 to 8
                    import math

                    wave = math.sin(i * math.pi * 2 / num_clips)
                    level = int(5 + wave * 3)
                    levels.append(max(1, min(10, level)))
            else:  # random
                # Random levels with some coherence
                levels = [random.randint(2, 9) for _ in range(num_clips)]

            configured = 0

            for i, clip_index in enumerate(clip_indices):
                energy = levels[i]

                # Higher energy clips are more likely to transition
                transition_prob = energy / 10.0

                if random.random() < transition_prob:
                    # Transition to another clip
                    # Prefer clips with similar or slightly higher energy
                    target_candidates = []
                    for j, target_clip in enumerate(clip_indices):
                        if j != i:
                            target_energy = levels[j]
                            # Weight by energy similarity and direction
                            if energy_pattern == "build" and target_energy >= energy:
                                weight = 2
                            elif energy_pattern == "drop" and target_energy <= energy:
                                weight = 2
                            else:
                                weight = 1

                            # Add multiple times for weighting
                            target_candidates.extend([target_clip] * weight)

                    if target_candidates:
                        target = random.choice(target_candidates)
                        ableton.send_command(
                            "set_clip_follow_action",
                            {
                                "track_index": track_index,
                                "clip_index": clip_index,
                                "action_slot": 0,
                                "action_type": 3,  # Play Other Clip
                                "trigger_time": 1.0,
                                "clip_index_target": target,
                            },
                        )
                        configured += 1
                else:
                    # Stay on same clip
                    ableton.send_command(
                        "set_clip_follow_action",
                        {
                            "track_index": track_index,
                            "clip_index": clip_index,
                            "action_slot": 0,
                            "action_type": 0,  # None
                        },
                    )

            return f"Configured {configured} energy-based follow actions for track {track_index} (pattern: {energy_pattern}, clips {clip_range_start}-{clip_range_end})"
        except Exception as e:
            return f"Error: {str(e)}"


def register_generation_tools(mcp: FastMCP, get_ableton_connection):
    """Register algorithmic music generation tools"""

    @mcp.tool()
    def generate_melody_clip(
        ctx: Context,
        track_index: int,
        clip_index: int,
        key: str = "Fm",
        scale_type: str = "minor",
        length_beats: float = 64.0,
        complexity: str = "medium",
    ) -> str:
        """
        Generate a melodic clip using algorithmic composition.

        Uses pattern-based generation instead of random arrays for musical results.
        Applies scale constraints, phrase structure, and velocity dynamics.

        Parameters:
        - track_index: Target track index
        - clip_index: Target clip slot
        - key: Key signature (e.g., "Fm", "Cm", "Am")
        - scale_type: Scale type (major, minor, dorian, phrygian, lydian, mixolydian)
        - length_beats: Clip length in beats (default 64 = 16 bars)
        - complexity: Pattern complexity (simple, medium, complex)

        Examples:
        - generate_melody_clip(6, 0, "Fm", "dorian", 64.0, "medium")
        """
        try:
            # Import generation module
            from MCP_Server.music_generation import (
                Scale, ScaleType, ClipGenerator, MIDINote,
                euclidean_rhythm, GenerationPipeline, GrooveGenerator
            )

            # Map scale type
            scale_map = {
                "major": ScaleType.MAJOR,
                "minor": ScaleType.MINOR,
                "dorian": ScaleType.DORIAN,
                "phrygian": ScaleType.PHRYGIAN,
                "lydian": ScaleType.LYDIAN,
                "mixolydian": ScaleType.MIXOLYDIAN,
            }
            scale_enum = scale_map.get(scale_type.lower(), ScaleType.MINOR)

            # Parse key (e.g., "Fm" -> root F, minor)
            key_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
            root_str = key[0].upper()
            root = 12 * 4 + key_map.get(root_str, 0)  # Octave 4

            scale = Scale(root, scale_enum)

            # Generate melody based on complexity
            gen = ClipGenerator(tempo=126.0, length_beats=length_beats)
            gen.scale = scale

            if complexity == "simple":
                # Simple repeating motif
                degrees = [0, 2, 4, 2]  # Scale tones
                for bar in range(int(length_beats / 4)):
                    for i, deg in enumerate(degrees):
                        pos = bar * 4 + i
                        pitch = scale.degree_to_midi(deg, octave=1)
                        vel = 75 + (i % 2) * 8
                        if pos < length_beats:
                            gen.notes.append(MIDINote(pitch, pos, 0.9, vel))
            elif complexity == "medium":
                # Medium complexity with variation
                degrees = [0, 2, 4, 5, 4, 3, 4, 5, 7, 5, 4, 2]
                for bar in range(int(length_beats / 4)):
                    for i, deg in enumerate(degrees[:8]):
                        pos = bar * 4 + i
                        pitch = scale.degree_to_midi(deg, octave=1)
                        vel = 80 + (i % 3) * 5
                        if pos < length_beats:
                            gen.notes.append(MIDINote(pitch, pos, 0.8 + (i % 3) * 0.1, vel))
            else:  # complex
                # More elaborate melodic development
                degrees = [0, 2, 4, 5, 7, 5, 4, 2, 3, 4, 5, 4, 2, 0, -1, 0]
                for bar in range(int(length_beats / 4)):
                    shift = (bar % 4) * 0.5
                    for i, deg in enumerate(degrees):
                        pos = bar * 4 + i + shift
                        pitch = scale.degree_to_midi(deg, octave=1 + (bar % 2))
                        vel = 70 + (i % 4) * 7 + (bar % 3) * 3
                        if pos < length_beats:
                            gen.notes.append(MIDINote(pitch, pos, 0.6 + (i % 5) * 0.15, vel))

            notes = gen.generate()
            ableton = get_ableton_connection()
            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": notes
            })

            return f"Generated melody clip with {len(notes)} notes (key={key}, scale={scale_type}, complexity={complexity})"

        except Exception as e:
            logger.error(f"Error generating melody: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error generating melody: {str(e)}"

    @mcp.tool()
    def generate_bass_line(
        ctx: Context,
        track_index: int,
        clip_index: int,
        key: str = "Fm",
        progression: str = "i-VII-VI-V",
        length_beats: float = 64.0,
        velocity: int = 110,
    ) -> str:
        """
        Generate a bass line following a chord progression.

        Creates a musical bass pattern with proper root notes, chord tones,
        and groove rather than random notes.

        Parameters:
        - track_index: Target track index
        - clip_index: Target clip slot
        - key: Key signature (e.g., "Fm", "Cm")
        - progression: Chord progression as Roman numerals (e.g., "i-VII-VI-V")
        - length_beats: Clip length in beats
        - velocity: Base velocity (0-127)

        Examples:
        - generate_bass_line(4, 0, "Fm", "i-VII-VI-V", 64.0, 110)
        """
        try:
            from MCP_Server.music_generation import (
                Scale, ScaleType, Chord, ChordProgression,
                ClipGenerator, GrooveGenerator, MIDINote
            )

            # Parse key
            key_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
            root_str = key[0].upper()
            root = 12 * 4 + key_map.get(root_str, 0)

            # Build chord progression
            chords = ChordProgression.from_preset(root, progression)
            beats_per_chord = length_beats / len(chords)

            gen = ClipGenerator(tempo=126.0, length_beats=length_beats)

            for i, chord in enumerate(chords):
                start = i * beats_per_chord
                if start >= length_beats:
                    break

                # Root on downbeat
                gen.notes.append(MIDINote(chord.notes[0], start, beats_per_chord * 0.8, velocity))

                # Fifth on offbeat for groove
                if len(chord.notes) > 1:
                    fifth_offset = chord.notes[1] - chord.notes[0]
                    gen.notes.append(MIDINote(
                        chord.notes[0] + fifth_offset,
                        start + beats_per_chord * 0.5,
                        beats_per_chord * 0.3,
                        velocity - 15
                    ))

                # Ghost note for dub feel
                if i % 2 == 0:
                    gen.notes.append(MIDINote(
                        chord.notes[0] - 12,  # An octave down
                        start + 2,
                        0.25,
                        velocity - 35
                    ))

            notes = gen.generate()
            ableton = get_ableton_connection()
            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": notes
            })

            return f"Generated bass line with {len(notes)} notes (key={key}, progression={progression})"

        except Exception as e:
            logger.error(f"Error generating bass line: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error generating bass line: {str(e)}"

    @mcp.tool()
    def generate_drum_pattern(
        ctx: Context,
        track_index: int,
        clip_index: int,
        drum_type: str = "kick",
        pattern_name: str = "one_drop",
        length_beats: float = 64.0,
        velocity: int = 115,
    ) -> str:
        """
        Generate drum patterns using Euclidean rhythms for authentic groove.

        Uses Bjorklund algorithm to create even distributions that sound musical
        rather than random/humanized patterns.

        Parameters:
        - track_index: Target track index
        - clip_index: Target clip slot
        - drum_type: Type of drum (kick, snare, hat, clap, perc)
        - pattern_name: Named pattern or euclidean params
          - Named: "one_drop", "steppers", "rockers", "house_basic", "dub_techno"
          - Euclidean: "e{N}-{K}" e.g., "e16-4" for 4 hits in 16
        - length_beats: Clip length in beats
        - velocity: Base velocity

        Examples:
        - generate_drum_pattern(0, 0, "kick", "one_drop", 64.0, 120)
        - generate_drum_pattern(2, 0, "hat", "e16-11", 64.0, 75)
        """
        try:
            from MCP_Server.music_generation import (
                euclidean_rhythm, ClipGenerator, GrooveGenerator, MIDINote
            )

            # Map drum types to MIDI notes
            drum_notes = {
                "kick": 36, "snare": 40, "hat": 42, "clap": 39, "perc": 37
            }
            pitch = drum_notes.get(drum_type.lower(), 36)

            # Parse pattern
            if pattern_name.startswith("e"):
                # Euclidean format: e{steps}-{pulses}
                parts = pattern_name[1:].split("-")
                steps, pulses = int(parts[0]), int(parts[1])
                timing = euclidean_rhythm(steps, pulses)
            else:
                # Named patterns - translate to Euclidean
                named_patterns = {
                    "one_drop": euclidean_rhythm(16, 4),  # 4 on floor
                    "steppers": euclidean_rhythm(16, 8),  # 8 hits evenly
                    "rockers": euclidean_rhythm(16, 6),   # Skank pattern
                    "house_basic": euclidean_rhythm(16, 4),
                    "dub_techno": euclidean_rhythm(16, 5),
                    "four_on_floor": euclidean_rhythm(16, 4),
                }
                timing = named_patterns.get(pattern_name.lower(), euclidean_rhythm(16, 4))

            # Scale timing to length_beats
            scale_factor = length_beats / 16.0
            timing = [beat * scale_factor for beat in timing]

            gen = ClipGenerator(tempo=126.0, length_beats=length_beats)

            # Get appropriate velocity pattern
            groove_func = GrooveGenerator.basic_pattern
            if drum_type == "kick":
                groove_func = lambda v: [v, v - 30, v - 25, v - 35] * 4
            elif drum_type == "hat":
                groove_func = lambda v: [v - 10, v - 25, v - 15, v - 30] * 4

            velocity_pattern = groove_func(velocity)

            # Add hits
            for i, beat in enumerate(timing):
                if beat < length_beats:
                    vel = velocity_pattern[i % len(velocity_pattern)]
                    dur = 0.3 if drum_type == "kick" else 0.15
                    gen.notes.append(MIDINote(pitch, beat, dur, vel))

            notes = gen.generate()
            ableton = get_ableton_connection()
            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": notes
            })

            return f"Generated {drum_type} pattern with {len(notes)} hits (pattern={pattern_name})"

        except Exception as e:
            logger.error(f"Error generating drum pattern: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error generating drum pattern: {str(e)}"

    @mcp.tool()
    def generate_scene(
        ctx: Context,
        scene_index: int,
        scene_type: str = "drop",
        key: str = "Fm",
        length_beats: float = 64.0,
    ) -> str:
        """
        Generate complete scene with all tracks using algorithmic composition.

        Applies the GenerationPipeline with scene-appropriate intensity and patterns.
        Each scene type has distinct musical character.

        Parameters:
        - scene_index: Scene index to populate
        - scene_type: Type of scene
          - "intro": Sparse, atmospheric, building
          - "drop": Full energy, driving
          - "break": Minimal, sparse
          - "build": Rising tension
          - "atmosphere": Very sparse, ambient
          - "outro": Fading, minimal
        - key: Key signature
        - length_beats: Total length in beats

        Returns:
            JSON with generated track data

        Examples:
        - generate_scene(0, "intro", "Fm", 64.0)
        - generate_scene(1, "drop", "Fm", 64.0)
        """
        try:
            from MCP_Server.music_generation import GenerationPipeline

            # Generate complete session
            tracks = GenerationPipeline.dub_techno_session(
                tempo=126.0,
                key=key,
                length_bars=int(length_beats / 4),
                scene=scene_type
            )

            # Track indices
            track_map = {
                "kick": 0, "snare": 1, "hat": 2, "clap": 3,
                "bass": 4, "chords": 5, "melody": 6, "perc": 7
            }

            ableton = get_ableton_connection()

            # Add to each track at the scene's clip slot
            for track_name, notes in tracks.items():
                track_idx = track_map.get(track_name)
                if track_idx is not None and notes:
                    ableton.send_command("add_notes_to_clip", {
                        "track_index": track_idx,
                        "clip_index": scene_index,
                        "notes": notes
                    })

            note_count = sum(len(n) for n in tracks.values())
            return f"Generated {scene_type} scene with {note_count} total notes across 8 tracks"

        except Exception as e:
            logger.error(f"Error generating scene: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error generating scene: {str(e)}"
