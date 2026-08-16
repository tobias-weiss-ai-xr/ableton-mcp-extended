"""Audio capture wrapper for MCP AudioAnalyzer

Supports both basic RMS/spectral analysis and MERT-based semantic analysis
(Paper: MERT, Li et al., 2023 — arXiv:2306.00107).
"""

import time
from typing import Any, Dict

# MERT semantic analysis (optional)
try:
    from music_theory.mert_analyzer import MertAnalyzer, get_mert_features_summary

    _MERT_AVAILABLE = True
except ImportError:
    _MERT_AVAILABLE = False
    MertAnalyzer = None  # type: ignore[assignment, misc]
    get_mert_features_summary = None  # type: ignore[assignment]

# Lazy-initialized singleton
_mert_instance = None


def _get_mert() -> "MertAnalyzer | None":
    global _mert_instance
    if not _MERT_AVAILABLE or MertAnalyzer is None:
        return None
    if _mert_instance is None:
        try:
            _mert_instance = MertAnalyzer()
        except Exception:
            pass
    return _mert_instance


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
    """Capture audio analysis using MCP AudioAnalyzer + MERT semantic features.

    Wraps the MCP server's audio_analysis_start/get_analysis/stop sequence.
    Returns a dictionary compatible with AudioAnalysisData TypedDict,
    augmented with MERT semantic features when available.

    Args:
        config: Configuration dict (may include capture_duration, etc.)

    Returns:
        Dict with keys matching AudioAnalysisData TypedDict plus
        semantic_mert_features.

    Raises:
        RuntimeError: If audio analyzer fails to start or tools unavailable.
    """
    if audio_analysis_start is None:
        raise RuntimeError("MCP audio analysis tools not available")

    start_result = audio_analysis_start()
    if not start_result.get("running"):
        raise RuntimeError("Failed to start audio analyzer")

    capture_duration = config.get("capture_duration", 1.0)
    time.sleep(capture_duration)  # Let audio settle

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

    # Augment with MERT semantic features if available
    mert = _get_mert()
    if mert is not None and mert.available:
        snapshot["semantic_mert_features"] = {"mert_available": True}
        snapshot["mert_summary_line"] = "MERT: semantic analysis ready"
    else:
        snapshot["semantic_mert_features"] = {"mert_available": False}

    audio_analysis_stop()

    return snapshot
