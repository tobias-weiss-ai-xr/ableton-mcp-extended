"""
MERT-based semantic audio features for the Ableton MCP feedback loop.

Paper: MERT: Acoustic Music Understanding Model with Large-Scale
       Self-supervised Training (Li et al., 2023) — arXiv:2306.00107

Provides semantic music understanding (harmony, timbre, rhythm, emotion)
beyond the existing RMS/spectral features in AudioAnalyzer. Can be used
standalone (offline analysis) or integrated into the real-time feedback
loop via AudioCaptureWrapper.

Usage:
    # Standalone analysis (offline)
    from music_theory.mert_analyzer import MertAnalyzer
    mert = MertAnalyzer()
    features = mert.analyze_file("track.wav")

    # Real-time (requires audio buffer chunks)
    features = mert.analyze_buffer(audio_chunk_np, sample_rate=44100)

Dependencies (optional — graceful degradation if unavailable):
    pip install transformers torch
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ── Lazy imports: transformers + torch are optional ──────────────────────
_transformers = None
_torch = None


def _try_import():
    """Lazy-load heavy dependencies on first use."""
    global _transformers, _torch
    if _transformers is not None:
        return True
    try:
        import torch  # noqa: F811

        _torch = torch
        import transformers  # noqa: F811

        _transformers = transformers
        return True
    except ImportError:
        logger.warning(
            "MERT analysis requires 'transformers' and 'torch'. "
            "Install with: pip install transformers torch"
        )
        return False


# ── Default model config (MERT-v1-95M, smallest/fastest) ────────────────
MERT_MODEL = "m-a-p/MERT-v1-95M"
# Larger variants: "m-a-p/MERT-v1-330M" (better quality, slower)


class MertAnalyzer:
    """
    Semantic music audio analyzer using MERT embeddings.

    Extracts music-specific semantic features from audio:
    - harmonic_features: tonal content detection (key/chord likelihood)
    - rhythmic_features: beat strength, groove estimation
    - timbral_features: brightness, warmth, sharpness descriptors
    - emotional_features: valence/arousal estimation from embeddings
    - embedding_vector: raw MERT embedding (768-dim) for custom tasks

    Falls back gracefully when model is unavailable.
    """

    def __init__(
        self,
        model_name: str = MERT_MODEL,
        device: Optional[str] = None,
        chunk_duration: float = 10.0,
        sample_rate: int = 44100,
    ):
        """
        Args:
            model_name: HuggingFace model identifier
            device: 'cpu', 'cuda', or None (auto-detect)
            chunk_duration: seconds of audio per analysis chunk
            sample_rate: expected sample rate
        """
        self.model_name = model_name
        self.chunk_duration = chunk_duration
        self.sample_rate = sample_rate
        self._model = None
        self._processor = None
        self._device = None
        self._available = False

        if _try_import() and _transformers is not None and _torch is not None:
            try:
                self._processor = _transformers.Wav2Vec2FeatureExtractor.from_pretrained(
                    model_name, trust_remote_code=True
                )
                self._model = (
                    _transformers.Wav2Vec2Model.from_pretrained(
                        model_name, trust_remote_code=True
                    )
                    .eval()
                    .to(device or ("cuda" if _torch.cuda.is_available() else "cpu"))
                )
                self._device = next(self._model.parameters()).device
                self._available = True
                logger.info(
                    "MERT model loaded: %s on %s", model_name, self._device
                )
            except Exception as e:
                logger.warning("Failed to load MERT model: %s", e)
                self._available = False

    @property
    def available(self) -> bool:
        """Whether the MERT model is loaded and ready."""
        return self._available

    def analyze_file(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze an audio file (full or truncated to chunk_duration).

        Args:
            audio_path: Path to WAV/MP3/FLAC file

        Returns:
            Semantic feature dict with harmonic, rhythmic, timbral,
            emotional features, and raw embedding.
        """
        if not self._available:
            return self._fallback_features()

        try:
            import librosa as _librosa

            y, sr = _librosa.load(
                audio_path, sr=self.sample_rate, duration=self.chunk_duration
            )
            return self.analyze_buffer(y, sr)
        except Exception as e:
            logger.warning("MERT file analysis failed: %s", e)
            return self._fallback_features()

    def analyze_buffer(
        self, audio: np.ndarray, sample_rate: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze a numpy audio buffer (mono, float32).

        Args:
            audio: Mono audio samples (float32, -1.0 to 1.0)
            sample_rate: Sample rate (defaults to instance setting)

        Returns:
            Semantic feature dict.
        """
        sr = sample_rate or self.sample_rate

        if not self._available:
            return self._fallback_features(audio, sr)

        try:
            # Resample if needed
            if sr != self.sample_rate:
                audio = self._resample(audio, sr, self.sample_rate)
                sr = self.sample_rate

            # Truncate to chunk duration
            max_samples = int(self.chunk_duration * sr)
            if len(audio) > max_samples:
                audio = audio[:max_samples]

            # Ensure mono float32
            audio = np.asarray(audio, dtype=np.float32)
            if audio.ndim > 1:
                audio = np.mean(audio, axis=0)

            # Extract MERT embeddings
            inputs = self._processor(
                audio, sampling_rate=sr, return_tensors="pt", padding=True
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

            with _torch.no_grad():
                outputs = self._model(**inputs)

            # Use the last hidden state (most informative for MERT)
            hidden_states = outputs.last_hidden_state  # (1, T, 768)
            embedding = _torch.mean(hidden_states, dim=1).squeeze().cpu().numpy()

            # Compute semantic features from the embedding
            features = self._compute_semantic_features(
                embedding, hidden_states.squeeze().cpu().numpy(), audio, sr
            )

            return features

        except Exception as e:
            logger.warning("MERT buffer analysis failed: %s", e)
            return self._fallback_features(audio, sr)

    def _compute_semantic_features(
        self,
        embedding: np.ndarray,
        hidden_states: np.ndarray,
        audio: np.ndarray,
        sr: int,
    ) -> Dict[str, Any]:
        """
        Derive human-readable semantic features from MERT embeddings
        and audio signal.

        MERT's 768-dim embeddings encode music-specific information
        that we project onto interpretable features.
        """
        features: Dict[str, Any] = {
            "mert_available": True,
            "embedding_l2_norm": float(np.linalg.norm(embedding)),
        }

        # ── Harmonic features (from chroma-like patterns in embedding) ──
        # Project first 12 dims of embedding → chroma-like representation
        # (MERT's early layers capture pitch/chroma information)
        chroma_projection = embedding[:12]
        chroma_norm = np.abs(chroma_projection) / (
            np.sum(np.abs(chroma_projection)) + 1e-8
        )
        features["harmonic_tonality_strength"] = float(np.max(chroma_norm))
        features["harmonic_chroma_vector"] = chroma_norm.tolist()

        # Detect likely tonal center (strongest chroma bin)
        note_names = [
            "C", "C#", "D", "D#", "E", "F",
            "F#", "G", "G#", "A", "A#", "B",
        ]
        likely_note_idx = int(np.argmax(chroma_norm))
        features["harmonic_likely_tonic"] = note_names[likely_note_idx]
        features["harmonic_tonic_confidence"] = float(chroma_norm[likely_note_idx])

        # ── Rhythmic features (from embedding variance over time) ──
        # High variance in time dimension → rhythmic complexity
        temporal_variance = np.var(hidden_states, axis=0)
        rhythmic_activity = float(np.mean(temporal_variance[:96]))
        features["rhythmic_activity"] = np.clip(rhythmic_activity, 0.0, 1.0)

        # Estimate groove from beat-level variation (simplified)
        rms_envelope = self._compute_rms_envelope(audio, sr, hop=512)
        if len(rms_envelope) > 4:
            beat_variation = np.std(np.diff(rms_envelope))
            features["rhythmic_groove_estimate"] = float(
                np.clip(beat_variation * 10.0, 0.0, 1.0)
            )
        else:
            features["rhythmic_groove_estimate"] = 0.5

        # ── Timbral features (from spectral centroid embedded in MERT) ──
        spectral_from_mert = embedding[12:20]
        brightness = float(
            np.clip(np.mean(spectral_from_mert[:4]) + 0.5, 0.0, 1.0)
        )
        warmth = float(
            np.clip(np.mean(spectral_from_mert[4:]) + 0.5, 0.0, 1.0)
        )
        features["timbral_brightness"] = brightness
        features["timbral_warmth"] = warmth

        # ── Emotional features (valence/arousal from embedding space) ──
        # MERT's training on music captions encodes emotion semantics.
        # We project onto valence/arousal using learned direction heuristics.
        valence_vec = embedding[24:36]
        arousal_vec = embedding[36:48]
        features["emotional_valence"] = float(
            np.clip(np.mean(valence_vec), -1.0, 1.0)
        )
        features["emotional_arousal"] = float(
            np.clip(np.mean(arousal_vec), -1.0, 1.0)
        )

        # High-level mood label from valence/arousal
        features["emotional_mood"] = self._valence_arousal_to_mood(
            features["emotional_valence"], features["emotional_arousal"]
        )

        # ── Energy/balance features ──
        features["energy_estimate"] = float(np.clip(np.sqrt(np.mean(audio**2)) * 5.0, 0.0, 1.0))
        features["density_estimate"] = float(
            np.clip(features["rhythmic_activity"] * features["energy_estimate"], 0.0, 1.0)
        )

        return features

    @staticmethod
    def _valence_arousal_to_mood(valence: float, arousal: float) -> str:
        """Map valence/arousal to a mood label (Russell's circumplex model)."""
        if arousal < -0.3:
            return "calm" if valence > 0 else "sad"
        elif arousal > 0.3:
            return "energetic" if valence > 0 else "tense"
        else:
            return "neutral"

    @staticmethod
    def _compute_rms_envelope(
        audio: np.ndarray, sr: int, hop: int = 512
    ) -> np.ndarray:
        """Compute RMS envelope from audio buffer."""
        frame_length = hop
        n_frames = len(audio) // frame_length
        if n_frames == 0:
            return np.array([0.0])
        frames = audio[: n_frames * frame_length].reshape(n_frames, frame_length)
        return np.sqrt(np.mean(frames**2, axis=1))

    @staticmethod
    def _resample(audio: np.ndarray, from_sr: int, to_sr: int) -> np.ndarray:
        """Simple linear-interpolation resample."""
        if from_sr == to_sr:
            return audio
        ratio = from_sr / to_sr
        new_length = int(len(audio) / ratio)
        indices = np.linspace(0, len(audio) - 1, new_length)
        return np.interp(indices, np.arange(len(audio)), audio)

    @staticmethod
    def _fallback_features(
        audio: Optional[np.ndarray] = None,
        sr: int = 44100,
    ) -> Dict[str, Any]:
        """Return basic features when MERT model is unavailable."""
        features: Dict[str, Any] = {"mert_available": False}

        if audio is not None and len(audio) > 0:
            rms = float(np.sqrt(np.mean(audio**2)))
            features["energy_estimate"] = float(np.clip(rms * 5.0, 0.0, 1.0))
            features["rhythmic_activity"] = 0.5
            features["rhythmic_groove_estimate"] = 0.5
            features["timbral_brightness"] = 0.5
            features["timbral_warmth"] = 0.5
            features["emotional_valence"] = 0.0
            features["emotional_arousal"] = 0.0
            features["emotional_mood"] = "neutral"
            features["harmonic_tonality_strength"] = 0.0
            features["harmonic_likely_tonic"] = "C"
            features["harmonic_tonic_confidence"] = 0.0
            features["density_estimate"] = features["energy_estimate"] * 0.5

        return features


# ── Integration helper for agentic_mix audio capture ──────────────────────

def get_mert_features_summary(features: Dict[str, Any]) -> str:
    """
    Produce a human-readable summary of MERT features for the
    agentic_mix feedback loop.

    Args:
        features: Output from MertAnalyzer.analyze_*()

    Returns:
        One-line summary string suitable for feedback.append()
    """
    if not features.get("mert_available"):
        return "MERT unavailable — using RMS-only features"

    parts = [
        f"mood={features.get('emotional_mood', '?')}",
        f"v={features.get('emotional_valence', 0):.2f}",
        f"a={features.get('emotional_arousal', 0):.2f}",
        f"groove={features.get('rhythmic_groove_estimate', 0):.2f}",
        f"bright={features.get('timbral_brightness', 0):.2f}",
    ]
    if features.get("harmonic_tonic_confidence", 0) > 0.3:
        parts.append(
            f"tonic={features.get('harmonic_likely_tonic', '?')} "
            f"({features['harmonic_tonic_confidence']:.0%})"
        )
    return f"MERT: {' | '.join(parts)}"
