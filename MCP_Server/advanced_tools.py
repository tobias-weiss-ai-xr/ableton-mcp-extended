# Additional MCP tools for complete automation
# These tools extend the base server.py with advanced features

from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any
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
