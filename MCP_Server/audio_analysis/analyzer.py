"""AudioAnalyzer - Real-time audio analysis with BPM detection."""

from __future__ import annotations

import threading
import time
from typing import Optional, Dict, Any

import numpy as np
import sounddevice as sd

try:
    import aubio

    HAS_AUBIO = True
except ImportError:
    HAS_AUBIO = False

from .config import AudioAnalyzerConfig


class AudioAnalyzer:
    """Real-time audio analyzer with BPM detection."""

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
        }
        self._device_index: Optional[int] = None
        self._tempo: Optional[Any] = None
        self._hop_size = 512

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

        # Find VB-Cable device
        self._device_index = self._find_vb_cable_index()
        if self._device_index is None:
            print("VB-Audio Cable not found. Install from: https://vb-audio.com/Cable/")
            return False

        # Initialize aubio tempo detection
        if HAS_AUBIO:
            self._tempo = aubio.tempo(
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

        samples = indata[:, 0].astype(np.float32)

        # Calculate RMS
        rms = float(np.sqrt(np.mean(samples**2)))

        # BPM detection with aubio
        bpm = 0.0
        beat = False
        if self._tempo is not None and self.config.analysis_features.get("bpm", True):
            beat = self._tempo(samples)
            if beat:
                bpm = self._tempo.get_bpm()

        # Update cached results (thread-safe)
        with self._lock:
            self._analysis["bpm"] = bpm
            self._analysis["beat"] = bool(beat)
            self._analysis["rms"] = rms
            self._analysis["timestamp"] = time.time()

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
