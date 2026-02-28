"""AudioAnalyzer - Real-time audio analysis with BPM detection.

Extends real-time analysis with key detection, spectral analysis, and loudness measurement.
"""

from __future__ import annotations

import threading
import time
from typing import Optional, Dict, Any

import numpy as np
import sounddevice as sd

# Optional audio analysis libraries
try:
    import aubio as _aubio

    HAS_AUBIO = True
except Exception:
    _aubio = None
    HAS_AUBIO = False

try:
    import librosa as _librosa

    HAS_LIBROSA = True
except Exception:
    _librosa = None
    HAS_LIBROSA = False

try:
    import pyloudnorm as _pyln

    HAS_PYLOUDNORM = True
except Exception:
    _pyln = None
    HAS_PYLOUDNORM = False

from .config import AudioAnalyzerConfig


class AudioAnalyzer:
    """Real-time audio analyzer with BPM detection and extended features."""

    def __init__(self, config: Optional[AudioAnalyzerConfig] = None):
        self.config = config or AudioAnalyzerConfig()
        self._running = False
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self._analysis: Dict[str, Any] = {
            "bpm": 0.0,
            "beat": False,
            "rms": 0.0,
            "timestamp": 0.0,
            # Extended features
            "key": "unknown",
            "key_confidence": 0.0,
            "spectral_centroid": 0.0,
            "spectral_rolloff": 0.0,
            "loudness_lufs": -100.0,
        }

        # Buffer for analysis (for periodic key detection)
        self._audio_buffer = np.zeros(self.config.buffer_size * 4, dtype=np.float32)
        self._buffer_pos = 0

        self._device_index: Optional[int] = None
        self._tempo: Optional[Any] = None
        self._hop_size = 512

        # Optional meters
        if HAS_PYLOUDNORM:
            self._meter = _pyln.Meter(self.config.sample_rate)  # type: ignore
        else:
            self._meter = None
        # Callback counter (for diagnostics)
        self._callback_count = 0


    def _find_vb_cable_index(self) -> Optional[int]:
        """Find VB-Cable INPUT device (CABLE Output)."""
        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            name = dev.get("name", "")
            if isinstance(name, str):
                nm = name.upper()
                if "VB-AUDIO" in nm or "CABLE" in nm:
                    if dev.get("max_input_channels", 0) > 0:
                        return idx
        return None

    def start(self) -> bool:
        """Start audio capture. Returns False if device not found."""
        if self._running:
            return True

        # Find VB-Cable device if not already set
        if self._device_index is None:
            self._device_index = self._find_vb_cable_index()
        if self._device_index is None:
            print("VB-Audio Cable not found. Install from: https://vb-audio.com/Cable/")
            return False

        # Initialize aubio tempo detection
        if HAS_AUBIO:
            self._tempo = _aubio.tempo(
                "default",
                self.config.buffer_size,
                self._hop_size,
                self.config.sample_rate,
            )

        try:
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.config.buffer_size,
                device=self._device_index,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._running = True
            return True
        except Exception as e:
            print(f"Failed to start audio stream: {e}")
            return False
            self._running = True
            return True
        except Exception as e:
            print(f"Failed to start audio stream: {e}")
            return False

    def stop(self) -> None:
        """Stop audio capture."""
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
        self._stream = None

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info, status
    ) -> None:
        """Sounddevice callback for audio processing."""
        if status:
            pass  # Handle overflow/underflow silently
        self._callback_count += 1  # Diagnostic counter

        samples = indata[:, 0].astype(np.float32)

        # Buffer accumulation for key detection (4x buffer as in guidelines)
        if self._audio_buffer is not None:
            n = samples.shape[0]
            end_pos = self._buffer_pos + n
            if end_pos <= len(self._audio_buffer):
                self._audio_buffer[self._buffer_pos : end_pos] = samples
                self._buffer_pos = end_pos
            else:
                remaining = len(self._audio_buffer) - self._buffer_pos
                if remaining > 0:
                    self._audio_buffer[self._buffer_pos :] = samples[:remaining]
                # Trigger key-detection once a full buffer has accumulated
                key = "unknown"
                key_confidence = 0.0
                if (
                    HAS_LIBROSA
                    and self.config.analysis_features.get("key", True)
                    and _librosa is not None
                ):
                    try:
                        chroma = _librosa.feature.chroma_cqt(
                            y=self._audio_buffer, sr=self.config.sample_rate
                        )
                        chroma_sum = np.sum(chroma, axis=1)
                        if chroma_sum.size:
                            key_idx = int(np.argmax(chroma_sum))
                            key_names = [
                                "C",
                                "C#",
                                "D",
                                "D#",
                                "E",
                                "F",
                                "F#",
                                "G",
                                "G#",
                                "A",
                                "A#",
                                "B",
                            ]
                            key = key_names[key_idx % 12]
                            denom = np.sum(chroma_sum)
                            key_confidence = (
                                float(np.max(chroma_sum) / denom) if denom != 0 else 0.0
                            )
                    except Exception:
                        key = "unknown"
                        key_confidence = 0.0
                self._buffer_pos = 0

        # RMS
        rms = float(np.sqrt(np.mean(samples**2)))

        # BPM detection with aubio
        bpm = 0.0
        beat = False
        if self._tempo is not None and self.config.analysis_features.get("bpm", True):
            beat = self._tempo(samples)
            if beat:
                bpm = self._tempo.get_bpm()

        # Spectral analysis
        spectral_centroid = 0.0
        spectral_rolloff = 0.0
        if (
            HAS_LIBROSA
            and self.config.analysis_features.get("spectral", True)
            and _librosa is not None
        ):
            try:
                centroid = _librosa.feature.spectral_centroid(
                    y=samples, sr=self.config.sample_rate
                )
                rolloff = _librosa.feature.spectral_rolloff(
                    y=samples, sr=self.config.sample_rate
                )
                spectral_centroid = float(np.mean(centroid)) if centroid.size else 0.0
                spectral_rolloff = float(np.mean(rolloff)) if rolloff.size else 0.0
            except Exception:
                spectral_centroid = 0.0
                spectral_rolloff = 0.0

        # LUFS loudness
        loudness_lufs = -100.0
        if (
            HAS_PYLOUDNORM
            and self._meter is not None
            and self.config.analysis_features.get("loudness", True)
        ):
            try:
                loudness_lufs = float(self._meter.integrated_loudness(samples))
                if not np.isfinite(loudness_lufs):
                    loudness_lufs = -100.0
            except Exception:
                loudness_lufs = -100.0

        # Update cached results (thread-safe)
        with self._lock:
            self._analysis["bpm"] = bpm
            self._analysis["beat"] = bool(beat)
            self._analysis["rms"] = rms
            self._analysis["timestamp"] = time.time()
            # Update extended features if detected
            if "key" in locals():
                self._analysis["key"] = key
                self._analysis["key_confidence"] = key_confidence
            self._analysis["spectral_centroid"] = spectral_centroid
            self._analysis["spectral_rolloff"] = spectral_rolloff
            self._analysis["loudness_lufs"] = loudness_lufs

    def get_analysis(self) -> Dict[str, Any]:
        """Return cached analysis results (thread-safe)."""
        with self._lock:
            return dict(self._analysis)

    def get_status(self) -> Dict[str, Any]:
        """Return analyzer status."""
        return {
            "running": self._running,
            "device_index": self._device_index,
            "sample_rate": self.config.sample_rate,
            "buffer_size": self.config.buffer_size,
        }

    def __del__(self):
        self.stop()
