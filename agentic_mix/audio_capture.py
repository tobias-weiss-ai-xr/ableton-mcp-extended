"""Audio capture wrapper for MCP AudioAnalyzer"""

import time
from typing import Any, Dict


# MCP tools (import from available module)
# These will be available when execute in MCP server context
try:
    from ableton_mcp_extended import (  # type: ignore[import-unidentified]
        audio_analysis_start,
        audio_analysis_get,
        audio_analysis_stop,
    )
except ImportError:
    # Fallback for testing outside MCP context
    audio_analysis_start = None  # type: ignore[assignment]
    audio_analysis_get = None  # type: ignore[assignment]
    audio_analysis_stop = None  # type: ignore[assignment]


def capture_audio_snapshot(config: Dict[str, Any]) -> Dict[str, Any]:
    """Capture audio analysis using MCP AudioAnalyzer

    Wraps the MCP server's audio_analysis_start/get_analysis/stop sequence.
    Returns a dictionary compatible with AudioAnalysisData TypedDict.

    Args:
        config: Configuration dict (may include capture_duration, etc.)

    Returns:
        Dict with keys matching AudioAnalysisData TypedDict.

    Raises:
        RuntimeError: If audio analyzer fails to start or tools unavailable.
    """
    if audio_analysis_start is None:
        raise RuntimeError("MCP audio analysis tools not available")

    start_result = audio_analysis_start()
    if not start_result.get("running"):
        raise RuntimeError("Failed to start audio analyzer")

    time.sleep(1.0)  # Let audio settle, capture 1 second

    analysis_dict = audio_analysis_get()

    snapshot: Dict[str, Any] = {
        "timestamp": time.time(),
        "bpm": analysis_dict.get("bpm"),
        "beat": analysis_dict.get("beat"),
        "rms": analysis_dict.get("rms", 0.5),
        "loudness_lufs": analysis_dict.get("loudness_lufs", -18.0),
        "key": analysis_dict.get("key"),
        "key_confidence": analysis_dict.get("key_confidence"),
        "spectral_centroid_hz": analysis_dict.get("spectral_centroid", 5000.0),
        "spectral_rolloff_hz": analysis_dict.get("spectral_rolloff", 1000.0),
    }

    audio_analysis_stop()

    return snapshot
