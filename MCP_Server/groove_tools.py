"""MCP tools for groove template manipulation."""

from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger("AbletonMCPServer")


def register_groove_tools(mcp: FastMCP, get_ableton_connection):
    """Register groove template MCP tools."""

    # ------------------------------------------------------------------
    # List Groove Templates
    # ------------------------------------------------------------------

    @mcp.tool()
    def list_groove_templates(ctx: Context) -> str:
        """List all available groove templates from Live's groove pool.

        Returns the names of every groove template currently loaded
        in Ableton's groove pool.

        Examples:
        - list_groove_templates()
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("get_available_grooves", {})
            return json.dumps({"status": "success", "grooves": result}, indent=2)
        except Exception as e:
            logger.error(f"Error listing groove templates: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Apply Groove to Clip
    # ------------------------------------------------------------------

    @mcp.tool()
    def apply_groove_to_clip(
        ctx: Context,
        track_index: int,
        clip_index: int,
        groove_name: str,
        amount: float = 1.0,
    ) -> str:
        """Apply a groove template to a clip.

        Validates that the groove exists in the pool before applying.
        Only applies to MIDI clips (audio clips do not support grooves).

        Parameters:
        - track_index: Index of the track containing the clip
        - clip_index: Index of the clip slot
        - groove_name: Name of the groove template to apply
        - amount: Groove amount (0.0-1.0, default 1.0)

        Examples:
        - apply_groove_to_clip(0, 0, "Swing", 0.75)
        - apply_groove_to_clip(1, 2, "Shuffle", 1.0)
        """
        try:
            ableton = get_ableton_connection()

            # Validate groove exists before applying
            grooves_result = ableton.send_command("get_available_grooves", {})
            groove_names = []
            if isinstance(grooves_result, dict):
                groove_list = grooves_result.get("grooves", [])
                groove_names = [g.get("name", "") for g in groove_list]

            if groove_name not in groove_names:
                return json.dumps({
                    "status": "error",
                    "message": f"Groove '{groove_name}' not found. Available grooves: {', '.join(groove_names) if groove_names else 'none'}",
                }, indent=2)

            amount = max(0.0, min(1.0, amount))
            result = ableton.send_command("apply_groove_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "groove_name": groove_name,
                "amount": amount,
            })
            return json.dumps({"status": "success", "result": result}, indent=2)
        except Exception as e:
            logger.error(f"Error applying groove to clip: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Remove Groove from Clip
    # ------------------------------------------------------------------

    @mcp.tool()
    def remove_groove_from_clip(
        ctx: Context,
        track_index: int,
        clip_index: int,
    ) -> str:
        """Remove the groove template from a clip.

        Resets the clip's groove assignment and groove amount to zero.

        Parameters:
        - track_index: Index of the track containing the clip
        - clip_index: Index of the clip slot

        Examples:
        - remove_groove_from_clip(0, 0)
        """
        try:
            ableton = get_ableton_connection()
            result = ableton.send_command("remove_groove_from_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
            })
            return json.dumps({"status": "success", "result": result}, indent=2)
        except Exception as e:
            logger.error(f"Error removing groove from clip: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})

    # ------------------------------------------------------------------
    # Set Global Groove Amount
    # ------------------------------------------------------------------

    @mcp.tool()
    def set_global_groove_amount(
        ctx: Context,
        amount: float = 1.0,
    ) -> str:
        """Set the global groove amount for the session (0.0-1.0).

        Controls how much the applied grooves affect clip timing.
        0.0 = no groove effect, 1.0 = full groove effect.

        Parameters:
        - amount: Global groove amount (0.0-1.0, default 1.0)

        Examples:
        - set_global_groove_amount(0.5)
        - set_global_groove_amount(1.0)
        """
        try:
            ableton = get_ableton_connection()
            amount = max(0.0, min(1.0, amount))
            result = ableton.send_command("set_global_groove_amount", {
                "amount": amount,
            })
            return json.dumps({"status": "success", "result": result}, indent=2)
        except Exception as e:
            logger.error(f"Error setting global groove amount: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)})
