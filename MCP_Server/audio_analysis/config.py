from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict
import yaml


@dataclass
class AudioAnalyzerConfig:
    sample_rate: int = 44100
    buffer_size: int = 2048
    analysis_features: Dict[str, bool] = field(
        default_factory=lambda: {
            "bpm": True,
            "key": True,
            "spectral": True,
            "loudness": True,
        }
    )
    cpu_budget_percent: float = 15.0
    device_name: Optional[str] = None
    websocket_port: int = 8765
    analysis_interval_ms: int = 50

    def __post_init__(self):
        # Validate sample_rate
        if self.sample_rate not in (44100, 48000):
            raise ValueError(
                f"Unsupported sample_rate: {self.sample_rate}. Supported: 44100, 48000"
            )
        # Ensure analysis_features contains required keys
        if not isinstance(self.analysis_features, dict):
            self.analysis_features = {}
        for key in ("bpm", "key", "spectral", "loudness"):  # default True if missing
            self.analysis_features.setdefault(key, True)
        # Basic validations
        if self.buffer_size <= 0:
            raise ValueError("buffer_size must be positive")
        if self.websocket_port <= 0 or self.websocket_port > 65535:
            raise ValueError("websocket_port must be a valid port number 1-65535")
        if self.analysis_interval_ms <= 0:
            raise ValueError("analysis_interval_ms must be positive")
        if not isinstance(self.cpu_budget_percent, (int, float)):
            raise TypeError("cpu_budget_percent must be a number")

    @classmethod
    def from_yaml(cls, path: str) -> "AudioAnalyzerConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        sample_rate = data.get("sample_rate", 44100)
        buffer_size = data.get("buffer_size", 2048)
        features = data.get("analysis_features", None)
        if features is None:
            features = {"bpm": True, "key": True, "spectral": True, "loudness": True}
        cpu_budget_percent = data.get("cpu_budget_percent", 15.0)
        device_name = data.get("device_name", None)
        websocket_port = data.get("websocket_port", 8765)
        analysis_interval_ms = data.get("analysis_interval_ms", 50)
        return cls(
            sample_rate=sample_rate,
            buffer_size=buffer_size,
            analysis_features=features,
            cpu_budget_percent=cpu_budget_percent,
            device_name=device_name,
            websocket_port=websocket_port,
            analysis_interval_ms=analysis_interval_ms,
        )
