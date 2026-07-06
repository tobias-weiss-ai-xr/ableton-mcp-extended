"""
Audio analysis integration for RMS-based reactive automation.

Wrapper around MCP_Server.audio_analysis.AudioAnalyzer for dub techno automation.
"""

import time
from typing import Optional, Dict, Any

# Import from MCP Server's audio analysis module
try:
    from MCP_Server.audio_analysis.AudioAnalyzer import AudioAnalyzer
    from MCP_Server.audio_analysis.AudioAnalyzerConfig import AudioAnalyzerConfig
except ImportError:
    # Fallback for development without audio dependencies
    AudioAnalyzer = None
    AudioAnalyzerConfig = None


class AudioAnalysisWrapper:
    """
    Wrapper around AudioAnalyzer for RMS-based reactive automation.

    Provides safe interface with error handling for missing devices,
    silence detection, and parameter mapping.
    """

    def __init__(self, device_name: Optional[str] = None):
        """
        Initialize audio analyzer with optional device specification.

        Args:
            device_name: Device name substring search (e.g., "Voicemeeter").
                        If None, uses default auto-detection.
        """
        self.device_name = device_name
        self._analyzer: Optional[Any] = None
        self._last_rms = 0.0
        self._error_count = 0
        self._max_errors = 10  # Disable after this many consecutive errors

        try:
            if AudioAnalyzer and AudioAnalyzerConfig:
                config = AudioAnalyzerConfig()
                if device_name:
                    config.device_name = device_name
                self._analyzer = AudioAnalyzer(config)
        except Exception as e:
            # Non-fatal - device may not be available during testing
            print(f"Warning: AudioAnalyzer initialization failed: {e}")
            self._analyzer = None

    def get_rms_level(self) -> float:
        """
        Get current audio RMS level.

        RMS (Root Mean Square) measures overall signal amplitude.
        Range: 0.0 (silence) to 1.0 (full scale).

        Returns:
            float: RMS value in range [0.0, 1.0]. Returns 0.0 on error.

        Note:
            This is reactive, not deterministic. Use for subtle parameter
            modulation, not for critical control decisions.
        """
        if self._analyzer is None:
            return 0.0

        try:
            analysis = self._analyzer.get_analysis()
            rms = analysis.get("rms", 0.0)

            # Clamp to valid range
            rms = max(0.0, min(1.0, rms))

            self._last_rms = rms
            self._error_count = 0  # Reset on success
            return rms

        except Exception as e:
            self._error_count += 1
            if self._error_count >= self._max_errors:
                # Too many errors - disable analyzer
                self._analyzer = None
            return self._last_rms  # Return last known value

    def map_rms_to_param(
        self,
        rms: float,
        param_min: float,
        param_max: float,
        curve: str = "linear"
    ) -> float:
        """
        Map RMS level to parameter value.

        Args:
            rms: RMS value (0.0-1.0)
            param_min: Minimum parameter value (e.g., 0.3 for filter cutoff)
            param_max: Maximum parameter value (e.g., 0.9 for filter cutoff)
            curve: Mapping curve - "linear", "exponential", "logarithmic"

        Returns:
            float: Mapped parameter value between param_min and param_max

        Examples:
            >>> map_rms_to_param(0.5, 0.3, 0.9)  # Linear
            0.6  # Midpoint between min and max

            >>> map_rms_to_param(0.8, 0.3, 0.9, curve="exponential")
            0.79  # Higher values emphasized
        """
        # Clamp RMS to valid range
        rms = max(0.0, min(1.0, rms))

        if curve == "linear":
            # Linear mapping: param_min + (rms * (param_max - param_min))
            return param_min + (rms * (param_max - param_min))

        elif curve == "exponential":
            # Exponential mapping: emphasize higher RMS values
            # formula: param_min + (rms^2 * (param_max - param_min))
            return param_min + ((rms ** 2) * (param_max - param_min))

        elif curve == "logarithmic":
            # Logarithmic mapping: emphasize lower RMS values
            # formula: param_min + (sqrt(rms) * (param_max - param_min))
            return param_min + ((rms ** 0.5) * (param_max - param_min))

        else:
            # Default to linear
            return param_min + (rms * (param_max - param_min))

    def is_silent(self, threshold: float = 0.01) -> bool:
        """
        Check if audio is currently silent.

        Args:
            threshold: RMS threshold below which is considered silence.

        Returns:
            bool: True if RMS < threshold, False otherwise.
        """
        rms = self.get_rms_level()
        return rms < threshold

    def get_beat_energy(self, bass_weight: float = 0.7) -> float:
        """
        Estimate beat energy with bass weight emphasis.

        Useful for dub techno: beats driven by kick/bass energy.

        Args:
            bass_weight: Weight for RMS in lower frequencies (0.0-1.0).
                        Higher values emphasize kick/bass.

        Returns:
            float: Energy estimate (0.0-1.0) with bass emphasis applied.
        """
        rms = self.get_rms_level()

        # Simple model: apply bass weight as direct multiplier adjustment
        # In real implementation, would use frequency-banded RMS
        adjusted_rms = rms * (1.0 + (bass_weight * 0.5))

        # Clamp to valid range
        return max(0.0, min(1.0, adjusted_rms))

    def is_available(self) -> bool:
        """
        Check if audio analyzer is available and functioning.

        Returns:
            bool: True if analyzer can read audio levels.
        """
        return self._analyzer is not None and self._error_count < self._max_errors


# Convenience functions for backward compatibility

def get_rms_level(device_name: Optional[str] = None) -> float:
    """
    Get RMS level using a temporary analyzer instance.

    Args:
        device_name: Optional device name for auto-detection.

    Returns:
        float: RMS value (0.0-1.0).
    """
    analyzer = AudioAnalysisWrapper(device_name)
    return analyzer.get_rms_level()


def map_rms_to_param(
    rms: float,
    param_min: float,
    param_max: float,
    curve: str = "linear"
) -> float:
    """
    Map RMS to parameter value (standalone function).

    Args:
        rms: RMS value (0.0-1.0)
        param_min: Minimum parameter value
        param_max: Maximum parameter value
        curve: Mapping curve type

    Returns:
        float: Mapped parameter value.
    """
    analyzer = AudioAnalysisWrapper()
    return analyzer.map_rms_to_param(rms, param_min, param_max, curve)