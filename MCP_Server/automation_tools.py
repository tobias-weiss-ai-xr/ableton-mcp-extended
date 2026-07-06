"""Automation envelope tools for MCP server.

Provides tools for reading and writing clip automation envelopes
(time-sampled envelope points, parameter-level control).
"""

import json
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context

logger = logging.getLogger(__name__)


def register_automation_tools(mcp: FastMCP, get_ableton_connection):
    """Register all automation envelope MCP tools."""

    @mcp.tool()
    def get_clip_envelope_points(
        ctx: Context,
        track_index: int,
        clip_index: int,
        device_index: int = 0,
        parameter_index: int = 0,
        num_samples: int = 64,
    ) -> str:
        """
        Get automation envelope points for a clip parameter via time-sampling.

        Samples the automation envelope at regular intervals across the clip
        length to reconstruct the envelope shape.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - device_index: The index of the device (default: 0)
        - parameter_index: The index of the parameter (default: 0)
        - num_samples: Number of time samples (default: 64, max: 256)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_clip_envelope_points", {
                "track_index": track_index,
                "clip_index": clip_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "num_samples": min(num_samples, 256),
            })
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error getting clip envelope points: {str(e)}")
            return f"Error getting clip envelope points: {str(e)}"

    @mcp.tool()
    def set_clip_envelope_point(
        ctx: Context,
        track_index: int,
        clip_index: int,
        device_index: int,
        parameter_index: int,
        time: float,
        value: float,
    ) -> str:
        """
        Add or update an automation envelope point.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - device_index: The index of the device
        - parameter_index: The index of the parameter
        - time: Time position in beats
        - value: Normalized parameter value (0.0 to 1.0)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("set_clip_envelope_point", {
                "track_index": track_index,
                "clip_index": clip_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "time": time,
                "value": value,
            })
            return f"Set envelope point at beat {time} with value {value}"
        except Exception as e:
            logger.error(f"Error setting clip envelope point: {str(e)}")
            return f"Error setting clip envelope point: {str(e)}"

    @mcp.tool()
    def clear_clip_envelope(
        ctx: Context,
        track_index: int,
        clip_index: int,
        device_index: int,
        parameter_index: int,
    ) -> str:
        """
        Clear automation envelope for a clip parameter.

        Parameters:
        - track_index: The index of the track
        - clip_index: The index of the clip slot
        - device_index: The index of the device
        - parameter_index: The index of the parameter
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("clear_automation", {
                "track_index": track_index,
                "clip_index": clip_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
            })
            return f"Cleared automation for parameter {parameter_index} on device {device_index}"
        except Exception as e:
            logger.error(f"Error clearing clip envelope: {str(e)}")
            return f"Error clearing clip envelope: {str(e)}"
