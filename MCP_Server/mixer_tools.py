"""MCP tools for crossfader, metering, send/return mixing."""

from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
import json
import logging
import time

logger = logging.getLogger("AbletonMCPServer")


def _resolve_tempo(ableton) -> float:
    """Query Ableton BPM, fallback 120."""
    try:
        result = ableton.send_command("get_session_info", {})
        if isinstance(result, dict):
            return float(result.get("tempo", 120))
    except Exception:
        pass
    return 120.0


def _beats_to_seconds(beats: float, bpm: float) -> float:
    """Convert beats to seconds at given BPM."""
    return (beats / (bpm / 60.0)) if bpm > 0 else beats


def register_mixer_tools(mcp: FastMCP, get_ableton_connection):
    """Register crossfader, metering, and send/return MCP tools."""

    # ------------------------------------------------------------------
    # Crossfader Position
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_crossfader_position(ctx: Context) -> str:
        """Get the master crossfader position (0.0-1.0).

        Returns the current crossfader value and its min/max range.

        Examples:
        - get_crossfader_position()
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_crossfader", {})
            return json.dumps({"status": "success", "crossfader": result}, indent=2)
        except Exception as e:
            logger.error(f"Error getting crossfader: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    def set_crossfader_position(ctx: Context, value: float = 0.5) -> str:
        """Set the master crossfader position (0.0-1.0).

        Parameters:
        - value: Crossfader position (0.0 = full A, 0.5 = center, 1.0 = full B)

        Examples:
        - set_crossfader_position(0.0)
        - set_crossfader_position(0.75)
        """
        try:
            ableton = get_ableton_connection()
            value = max(0.0, min(1.0, value))
            result = ableton.send_command("set_crossfader", {"value": value})
            return json.dumps({"status": "success", "crossfader": result}, indent=2)
        except Exception as e:
            logger.error(f"Error setting crossfader: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Track Crossfader Assignment
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_track_crossfade_assign(ctx: Context, track_index: int) -> str:
        """Get a track's crossfader assignment (A, B, or None).

        Parameters:
        - track_index: Index of the track to query

        Returns the numeric assignment (0=A, 1=None, 2=B) and name.

        Examples:
        - get_track_crossfade_assign(0)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_track_crossfade_assign", {"track_index": track_index})
            return json.dumps({"status": "success", "assignment": result}, indent=2)
        except Exception as e:
            logger.error(f"Error getting crossfade assign: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    def set_track_crossfade_assign(ctx: Context, track_index: int, assign: str = "None") -> str:
        """Set a track's crossfader assignment.

        Parameters:
        - track_index: Index of the track to assign
        - assign: Assignment - "A"/"left" (channel A), "None"/"off" (no assign), "B"/"right" (channel B)

        Examples:
        - set_track_crossfade_assign(0, "A")
        - set_track_crossfade_assign(1, "B")
        - set_track_crossfade_assign(2, "None")
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("set_track_crossfade_assign", {
                "track_index": track_index,
                "assign": assign,
            })
            return json.dumps({"status": "success", "assignment": result}, indent=2)
        except Exception as e:
            logger.error(f"Error setting crossfade assign: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Crossfader Sweep
    # ------------------------------------------------------------------

    @mcp.tool()
    def apply_crossfader_sweep(
        ctx: Context,
        from_value: float = 0.0,
        to_value: float = 1.0,
        duration_beats: float = 16.0,
        steps: int = 16,
    ) -> str:
        """Sweep the crossfader from one position to another over time.

        Creates a smooth crossfader transition using incremental steps.
        Ideal for DJ-style transitions between A/B channels.

        Parameters:
        - from_value: Starting crossfader position (default 0.0)
        - to_value: Ending crossfader position (default 1.0)
        - duration_beats: Sweep duration in beats (default 16.0)
        - steps: Number of interpolation steps (default 16)

        Examples:
        - apply_crossfader_sweep(0.0, 1.0, 32.0)
        - apply_crossfader_sweep(0.5, 0.0, 8.0, 8)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _resolve_tempo(ableton)

            for i in range(steps):
                t = i / (steps - 1) if steps > 1 else 1.0
                val = from_value + (to_value - from_value) * t
                ableton.send_command("set_crossfader", {"value": max(0.0, min(1.0, val))})
                time.sleep(_beats_to_seconds(duration_beats / steps, bpm))

            return json.dumps({
                "status": "success",
                "action": "crossfader_sweep",
                "from": from_value,
                "to": to_value,
                "duration_beats": duration_beats,
                "steps": steps,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in crossfader sweep: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Track Metering
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_level_snapshot(ctx: Context) -> str:
        """Get current meter levels for master and all tracks.

        Returns output_meter_left, output_meter_right, output_meter_level
        for master and every track. Useful for visual monitoring and
        analysis-driven mixing decisions.

        Examples:
        - get_level_snapshot()
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_level_snapshot", {})
            return json.dumps({"status": "success", "levels": result}, indent=2)
        except Exception as e:
            logger.error(f"Error getting level snapshot: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Send/Return Tools
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_track_sends(ctx: Context, track_index: int) -> str:
        """Get all send amounts for a track with return track names.

        Returns each send's index, value (0.0-1.0), and destination return track name.

        Parameters:
        - track_index: Index of the track to query

        Examples:
        - get_track_sends(0)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_track_sends", {"track_index": track_index})
            return json.dumps({"status": "success", "sends": result}, indent=2)
        except Exception as e:
            logger.error(f"Error getting track sends: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    @mcp.tool()
    def apply_send_sweep(
        ctx: Context,
        track_index: int,
        send_index: int,
        from_amount: float = 0.0,
        to_amount: float = 1.0,
        duration_beats: float = 16.0,
        steps: int = 16,
    ) -> str:
        """Sweep a send amount from one value to another over time.

        Creates smooth send automation for dub-style effect washes.
        Uses UDP for real-time updates.

        Parameters:
        - track_index: Track to apply send on
        - send_index: Send/return index to automate
        - from_amount: Starting send value (0.0-1.0, default 0.0)
        - to_amount: Ending send value (0.0-1.0, default 1.0)
        - duration_beats: Sweep duration in beats (default 16.0)
        - steps: Number of interpolation steps (default 16)

        Examples:
        - apply_send_sweep(0, 0, 0.0, 0.8, 16.0)
        - apply_send_sweep(1, 0, 0.5, 0.0, 8.0, 8)
        """
        try:
            ableton = get_ableton_connection()
            bpm = _resolve_tempo(ableton)

            for i in range(steps):
                t = i / (steps - 1) if steps > 1 else 1.0
                val = from_amount + (to_amount - from_amount) * t
                ableton.send_command_udp("set_send_amount", {
                    "track_index": track_index,
                    "send_index": send_index,
                    "amount": max(0.0, min(1.0, val)),
                })
                time.sleep(_beats_to_seconds(duration_beats / steps, bpm))

            return json.dumps({
                "status": "success",
                "action": "send_sweep",
                "track": track_index,
                "send": send_index,
                "from": from_amount,
                "to": to_amount,
                "duration_beats": duration_beats,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error in send sweep: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
