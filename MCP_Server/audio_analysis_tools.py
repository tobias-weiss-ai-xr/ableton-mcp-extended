# Audio Analysis MCP Tools
# Exposes existing AudioAnalyzer as callable MCP tools

from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any
import json
import logging
import time
import threading

from MCP_Server.audio_analysis import AudioAnalyzer, AudioAnalyzerConfig

logger = logging.getLogger("AbletonMCPServer")

# Module-level singleton
_analyzer: Optional[AudioAnalyzer] = None
_analyzer_lock = threading.Lock()
_start_time: Optional[float] = None


def _find_device_by_name(name_substring: str) -> Optional[int]:
    """Find a sound device whose name contains the given substring (case-insensitive)."""
    import sounddevice as sd

    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        dev_name = dev.get("name", "")
        if isinstance(dev_name, str) and name_substring.lower() in dev_name.lower():
            if dev.get("max_input_channels", 0) > 0:
                return idx
    return None


# ---------------------------------------------------------------------------
# Implementation functions (module-level for testability)
# ---------------------------------------------------------------------------


def _impl_start(device_name: Optional[str] = None) -> str:
    """Implementation of audio_analysis_start."""
    global _analyzer, _start_time
    try:
        config = AudioAnalyzerConfig()
        if device_name:
            device_index = _find_device_by_name(device_name)
            if device_index is None:
                return json.dumps(
                    {
                        "status": "error",
                        "message": f"No input device found matching '{device_name}'",
                    },
                    indent=2,
                )
            config.device_name = device_name

        with _analyzer_lock:
            if _analyzer is not None and _analyzer._running:
                return json.dumps(
                    {
                        "status": "already_running",
                        "device_index": _analyzer._device_index,
                        "sample_rate": _analyzer.config.sample_rate,
                    },
                    indent=2,
                )

            _analyzer = AudioAnalyzer(config)
            success = _analyzer.start()
            if not success:
                _analyzer = None
                return json.dumps(
                    {
                        "status": "error",
                        "message": "Failed to start audio capture. Is VB-Audio Cable installed?",
                    },
                    indent=2,
                )
            _start_time = time.time()
            return json.dumps(
                {
                    "status": "started",
                    "device_index": _analyzer._device_index,
                    "sample_rate": _analyzer.config.sample_rate,
                    "buffer_size": _analyzer.config.buffer_size,
                },
                indent=2,
            )
    except Exception as e:
        logger.error(f"Error starting audio analysis: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def _impl_stop() -> str:
    """Implementation of audio_analysis_stop."""
    global _analyzer, _start_time
    try:
        with _analyzer_lock:
            if _analyzer is None:
                return json.dumps({"status": "not_running"}, indent=2)

            duration = 0.0
            if _start_time:
                duration = time.time() - _start_time

            _analyzer.stop()
            _analyzer = None
            _start_time = None

            return json.dumps(
                {
                    "status": "stopped",
                    "capture_duration_seconds": round(duration, 1),
                },
                indent=2,
            )
    except Exception as e:
        logger.error(f"Error stopping audio analysis: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def _impl_get() -> str:
    """Implementation of audio_analysis_get."""
    try:
        with _analyzer_lock:
            if _analyzer is None or not _analyzer._running:
                return json.dumps(
                    {
                        "status": "not_running",
                        "message": "Audio analysis not started. Call audio_analysis_start first.",
                    },
                    indent=2,
                )
            analysis = _analyzer.get_analysis()

        return json.dumps(
            {
                "status": "success",
                "bpm": analysis["bpm"],
                "beat": analysis["beat"],
                "rms": round(analysis["rms"], 6),
                "key": analysis["key"],
                "key_confidence": round(analysis["key_confidence"], 4),
                "spectral_centroid_hz": round(analysis["spectral_centroid"], 2),
                "spectral_rolloff_hz": round(analysis["spectral_rolloff"], 2),
                "loudness_lufs": round(analysis["loudness_lufs"], 2),
                "timestamp": analysis["timestamp"],
            },
            indent=2,
        )
    except Exception as e:
        logger.error(f"Error getting audio analysis: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def _impl_status() -> str:
    """Implementation of audio_analysis_status."""
    try:
        with _analyzer_lock:
            if _analyzer is None:
                return json.dumps(
                    {
                        "status": "success",
                        "running": False,
                        "device_index": None,
                        "sample_rate": None,
                        "buffer_size": None,
                        "features": None,
                    },
                    indent=2,
                )

            return json.dumps(
                {
                    "status": "success",
                    "running": _analyzer._running,
                    "device_index": _analyzer._device_index,
                    "sample_rate": _analyzer.config.sample_rate,
                    "buffer_size": _analyzer.config.buffer_size,
                    "features": dict(_analyzer.config.analysis_features),
                },
                indent=2,
            )
    except Exception as e:
        logger.error(f"Error getting audio analysis status: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


def _impl_configure(features: Optional[dict] = None) -> str:
    """Implementation of audio_analysis_configure."""
    try:
        with _analyzer_lock:
            if _analyzer is None:
                return json.dumps(
                    {
                        "status": "not_running",
                        "message": "Configure before starting, or start first then configure.",
                    },
                    indent=2,
                )

            if features is None:
                return json.dumps(
                    {
                        "status": "success",
                        "features": dict(_analyzer.config.analysis_features),
                    },
                    indent=2,
                )

            valid_keys = {"bpm", "key", "spectral", "loudness"}
            for key in features:
                if key not in valid_keys:
                    return json.dumps(
                        {
                            "status": "error",
                            "message": f"Invalid feature key '{key}'. Valid keys: {sorted(valid_keys)}",
                        },
                        indent=2,
                    )
                if not isinstance(features[key], bool):
                    return json.dumps(
                        {
                            "status": "error",
                            "message": f"Feature '{key}' must be a boolean",
                        },
                        indent=2,
                    )
                _analyzer.config.analysis_features[key] = features[key]

            return json.dumps(
                {
                    "status": "success",
                    "features": dict(_analyzer.config.analysis_features),
                },
                indent=2,
            )
    except Exception as e:
        logger.error(f"Error configuring audio analysis: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)}, indent=2)


# ---------------------------------------------------------------------------
# MCP tool registration (thin wrappers)
# ---------------------------------------------------------------------------


def register_audio_analysis_tools(mcp: FastMCP, get_ableton_connection):
    """Register all audio analysis MCP tools."""

    @mcp.tool()
    def audio_analysis_start(
        ctx: Context, device_name: Optional[str] = None
    ) -> str:
        """
        Start real-time audio capture and analysis.

        Parameters:
        - device_name: Optional device name (substring, case-insensitive).
                       If omitted, auto-detects VB-Audio Cable.

        Returns JSON with status, device info, sample rate.
        """
        return _impl_start(device_name)

    @mcp.tool()
    def audio_analysis_stop(ctx: Context) -> str:
        """
        Stop audio capture and release the stream.

        Returns JSON with status and capture duration.
        """
        return _impl_stop()

    @mcp.tool()
    def audio_analysis_get(ctx: Context) -> str:
        """
        Get the latest analysis snapshot.

        Returns JSON with: bpm, beat, rms, key, key_confidence,
        spectral_centroid, spectral_rolloff, loudness_lufs, timestamp.
        """
        return _impl_get()

    @mcp.tool()
    def audio_analysis_status(ctx: Context) -> str:
        """
        Return analyzer configuration and state.

        Returns JSON with: running, device_index, sample_rate,
        buffer_size, analysis_features.
        """
        return _impl_status()

    @mcp.tool()
    def audio_analysis_configure(
        ctx: Context, features: Optional[dict] = None
    ) -> str:
        """
        Update analysis feature flags at runtime.

        Parameters:
        - features: Dict of feature keys to boolean values.
                    Valid keys: "bpm", "key", "spectral", "loudness".
                    Partial update — only specified keys change.

        Returns new config state.
        """
        return _impl_configure(features)
