# =============================================================================
# Audio Analysis MCP Commands
# =============================================================================
"""MCP commands for real-time audio analysis."""

from .audio_analysis import AudioAnalyzer, AudioAnalyzerConfig
from mcp.server.fastmcp import FastMCP

# Get the mcp instance from server.py (it will be imported when this module is loaded)
# This file should be imported by server.py to register these tools

_audio_analyzer: AudioAnalyzer | None = None


# Note: These functions are decorated with @mcp.tool() but the mcp instance
# must be imported from server.py. When server.py imports this module,
# the decorators will register these tools.


def _register_tools(mcp: FastMCP):
    """Register audio analysis tools with the MCP server.

    Call this from server.py to register the audio analysis commands.
    """
    global _audio_analyzer

    @mcp.tool()
    def get_audio_analysis() -> dict:
        """Get the latest audio analysis results (BPM, key, loudness, spectral).

        Returns cached analysis data from the real-time audio analyzer.
        Response time <10ms as results are pre-computed.

        Returns:
            dict with keys: bpm, key, loudness_lufs, spectral_centroid, rms, beat
        """
        global _audio_analyzer
        if _audio_analyzer is None:
            return {
                "success": False,
                "error": "Audio analyzer not initialized. Call start_audio_analyzer first.",
            }
        return {"success": True, "data": _audio_analyzer.get_analysis()}

    @mcp.tool()
    def get_audio_analyzer_status() -> dict:
        """Get the audio analyzer status and health info.

        Returns:
            dict with keys: running, device_index, sample_rate, buffer_size
        """
        global _audio_analyzer
        if _audio_analyzer is None:
            return {
                "success": False,
                "error": "Audio analyzer not initialized",
                "running": False,
            }
        return {"success": True, "data": _audio_analyzer.get_status()}

    @mcp.tool()
    def start_audio_analyzer(device_name: str = None, sample_rate: int = 44100) -> dict:
        """Start the real-time audio analyzer.

        Captures audio from VB-Cable and performs BPM/key/loudness analysis.
        Requires VB-Audio Cable to be installed (https://vb-audio.com/Cable/).

        Args:
            device_name: Optional device name (auto-detects VB-Cable if not specified)
            sample_rate: Sample rate (44100 or 48000)

        Returns:
            dict with success status
        """
        global _audio_analyzer

        try:
            config = AudioAnalyzerConfig(
                sample_rate=sample_rate, device_name=device_name
            )
            _audio_analyzer = AudioAnalyzer(config)
            started = _audio_analyzer.start()

            if started:
                return {"success": True, "message": "Audio analyzer started"}
            else:
                return {
                    "success": False,
                    "error": "Failed to start. VB-Cable may not be installed.",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def stop_audio_analyzer() -> dict:
        """Stop the real-time audio analyzer.

        Returns:
            dict with success status
        """
        global _audio_analyzer

        if _audio_analyzer is None:
            return {"success": True, "message": "Analyzer was not running"}

        try:
            _audio_analyzer.stop()
            return {"success": True, "message": "Audio analyzer stopped"}
        except Exception as e:
            return {"success": False, "error": str(e)}
