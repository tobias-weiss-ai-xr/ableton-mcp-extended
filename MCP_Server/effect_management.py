"""
Effect Management System for Ableton Live via MCP

This module provides improved effect/instrument loading capabilities with:
- Preset-based loading with named effects
- Genre-specific effect chains
- Common signal flow configurations
- Device parameter utilities
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class DeviceConfig:
    """Configuration for a single device."""
    name: str
    device_type: str
    uri: str
    preset_name: Optional[str] = None
    position: int = -1
    parameters: Optional[Dict[str, float]] = None


@dataclass
class EffectChain:
    """A chain of effects with routing configuration."""
    name: str
    devices: List[DeviceConfig]
    genre: str


class EffectPresets:
    """Named effect presets organized by category."""

    REVERB = DeviceConfig(
        name="Reverb",
        device_type="audio_effect",
        uri="query:Audio Effects#Reverb",
    )

    DELAY = DeviceConfig(
        name="Delay",
        device_type="audio_effect",
        uri="query:Audio Effects#Simple Delay",
    )

    LIMITER = DeviceConfig(
        name="Limiter",
        device_type="audio_effect",
        uri="query:Audio Effects#Limiter",
        parameters={"gain": 0.0, "ceiling": 0.98, "release": 0.3},
    )

    COMPRESSOR = DeviceConfig(
        name="Compressor",
        device_type="audio_effect",
        uri="query:Audio Effects#Compressor",
        parameters={"ratio": 0.4, "threshold": 0.3, "release": 0.5},
    )

    EQ_THREE = DeviceConfig(
        name="EQ Three",
        device_type="audio_effect",
        uri="query:Audio Effects#EQ Three",
    )

    FILTER_FREQ = DeviceConfig(
        name="Auto Filter",
        device_type="audio_effect",
        uri="query:Audio Effects#Auto Filter",
        parameters={"frequency": 0.7, "resonance": 0.3},
    )

    SATURATOR = DeviceConfig(
        name="Saturator",
        device_type="audio_effect",
        uri="query:Audio Effects#Saturator",
        parameters={"drive": 0.3, "color": 0.0},
    )

    CHORUS = DeviceConfig(
        name="Chorus",
        device_type="audio_effect",
        uri="query:Audio Effects#Chorus",
        parameters={"mix": 0.3, "rate": 0.05, "depth": 0.2},
    )


class GenreEffectChains:
    """Preconfigured effect chains for specific genres."""

    DUB_TECHNO_BASS = EffectChain(
        name="Dub Techno Bass",
        genre="dub_techno",
        devices=[
            EffectPresets.COMPRESSOR,
            EffectPresets.SATURATOR,
            EffectPresets.FILTER_FREQ,
            EffectPresets.LIMITER,
        ],
    )

    DUB_TECHNO_CHORDS = EffectChain(
        name="Dub Techno Chords",
        genre="dub_techno",
        devices=[
            EffectPresets.SATURATOR,
            EffectPresets.REVERB,
            EffectPresets.DELAY,
        ],
    )

    HOUSE_BASS = EffectChain(
        name="House Bass",
        genre="house",
        devices=[
            EffectPresets.EQ_THREE,
            EffectPresets.COMPRESSOR,
            EffectPresets.SATURATOR,
        ],
    )

    TECHNO_LEAD = EffectChain(
        name="Techno Lead",
        genre="techno",
        devices=[
            EffectPresets.FILTER_FREQ,
            EffectPresets.SATURATOR,
            EffectPresets.DELAY,
            EffectPresets.REVERB,
        ],
    )

    AMBIENT_PAD = EffectChain(
        name="Ambient Pad",
        genre="ambient",
        devices=[
            EffectPresets.SATURATOR,
            EffectPresets.EQ_THREE,
            EffectPresets.REVERB,
            EffectPresets.CHORUS,
        ],
    )

    CLASSIC_DRUMS = EffectChain(
        name="Classic Drums",
        genre="electronic",
        devices=[
            EffectPresets.EQ_THREE,
            EffectPresets.COMPRESSOR,
            EffectPresets.LIMITER,
        ],
    )


class EffectLoader:
    """Helper class for loading effects with common names."""

    @staticmethod
    def get_effect_config(effect_name: str) -> Optional[DeviceConfig]:
        """Get device config by common effect name."""
        effect_map = {
            "reverb": EffectPresets.REVERB,
            "delay": EffectPresets.DELAY,
            "limiter": EffectPresets.LIMITER,
            "compressor": EffectPresets.COMPRESSOR,
            "eq": EffectPresets.EQ_THREE,
            "eq3": EffectPresets.EQ_THREE,
            "filter": EffectPresets.FILTER_FREQ,
            "auto-filter": EffectPresets.FILTER_FREQ,
            "saturator": EffectPresets.SATURATOR,
            "chorus": EffectPresets.CHORUS,
        }
        return effect_map.get(effect_name.lower())

    @staticmethod
    def get_genre_chain(genre: str, track_type: str) -> Optional[EffectChain]:
        """Get genre-specific effect chain for a track type."""
        chain_key = f"{genre.upper()}_{track_type.upper()}"
        return getattr(GenreEffectChains, chain_key, None)

    @staticmethod
    def create_mix(genre: str, track_config: Dict[str, str]) -> Dict[str, EffectChain]:
        """Create a complete effect mix for a multi-track setup.

        Args:
            genre: Music genre (dub_techno, house, techno, ambient)
            track_config: Dictionary mapping track types to track names
                         e.g., {"bass": "Bass Track", "chords": "Chord Track"}

        Returns:
            Dictionary mapping track names to effect chains
        """
        mix = {}
        for track_type, track_name in track_config.items():
            chain = EffectLoader.get_genre_chain(genre, track_type)
            if chain:
                mix[track_name] = chain
        return mix

    @staticmethod
    def normalize_parameter(value: float, min_val: float, max_val: float) -> float:
        """Normalize a parameter value to 0.0-1.0 range."""
        return (value - min_val) / (max_val - min_val)

    @staticmethod
    def denormalize_parameter(normalized: float, min_val: float, max_val: float) -> float:
        """Convert normalized value back to actual range."""
        return min_val + (normalized * (max_val - min_val))


class EffectChainBuilder:
    """Templates for building common effect chain configurations."""

    @staticmethod
    def build_dub_techno_return_setup() -> Tuple[EffectChain, EffectChain]:
        """Build typical dub techno return track setup (Reverb and Delay)."""
        reverb_chain = EffectChain(
            name="Dub Reverb Return",
            genre="dub_techno",
            devices=[
                DeviceConfig(
                    name="Reverb",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Reverb",
                    parameters={
                        "decay": 0.8,
                        "size": 0.7,
                        "diffusion": 0.6,
                        "high_cut": 0.7,
                        "low_cut": 0.3,
                    }
                )
            ],
        )

        delay_chain = EffectChain(
            name="Dub Delay Return",
            genre="dub_techno",
            devices=[
                DeviceConfig(
                    name="Simple Delay",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Simple Delay",
                    parameters={
                        "delay_time": 0.25,
                        "feedback": 0.6,
                        "filter": 0.3,
                        "dry_wet": 0.5,
                    }
                )
            ],
        )

        return reverb_chain, delay_chain

    @staticmethod
    def build_dub_techno_master_chain() -> EffectChain:
        """Build dub techno mastering chain."""
        return EffectChain(
            name="Dub Techno Master",
            genre="dub_techno",
            devices=[
                DeviceConfig(
                    name="Utility",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Utility",
                    parameters={"gain": 0.0}
                ),
                DeviceConfig(
                    name="Limiter",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Limiter",
                    parameters={
                        "gain": 0.02,
                        "ceiling": 0.98,
                        "release": 0.4,
                    }
                ),
            ],
        )

    @staticmethod
    def build_parallel_processing_chain() -> EffectChain:
        """Build chain for parallel processing setup."""
        return EffectChain(
            name="Parallel Processing",
            genre="electronic",
            devices=[
                DeviceConfig(
                    name="Utility",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Utility",
                    parameters={"gain": -6.0, "phase": 180}
                ),
                DeviceConfig(
                    name="Saturator",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Saturator",
                    parameters={"drive": 0.6, "color": 0.2}
                ),
                DeviceConfig(
                    name="Compressor",
                    device_type="audio_effect",
                    uri="query:Audio Effects#Compressor",
                    parameters={"ratio": 0.7, "threshold": 0.2}
                ),
            ],
        )


class EffectLibrary:
    """Searchable database of available effects."""

    _library = {
        "reverb": ["Reverb", "Convolution Reverb"],
        "delay": ["Simple Delay", "Delay", "Ping Pong Delay"],
        "compressor": ["Compressor", "Glue Compressor", "Multiband Dynamics"],
        "eq": ["EQ Three", "EQ Eight", "Filter EQ"],
        "filter": ["Auto Filter", "Filter EQ"],
        "distortion": ["Saturator", "Overdrive", "Tube Distortion", "Redux"],
        "modulation": ["Chorus", "Flanger", "Phaser", "Vibrato"],
        "space": ["Reverb", "Convolution Reverb", "Simple Delay", "Echo"],
        "dynamics": ["Compressor", "Limiter", "Gate", "Glue Compressor"],
        "utility": ["Utility", "Gain", "External Audio Effect"],
    }

    @classmethod
    def search(cls, query: str) -> List[str]:
        """Search for effects matching a query."""
        query_lower = query.lower()
        results = []
        for category, effects in cls._library.items():
            if query_lower in category or any(query_lower in effect.lower() for effect in effects):
                results.extend(effects)
        return list(set(results))  # Remove duplicates

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all available effect categories."""
        return list(cls._library.keys())

    @classmethod
    def get_effects_by_category(cls, category: str) -> List[str]:
        """Get all effects in a specific category."""
        return cls._library.get(category.lower(), [])


# Global instance for easy access
effect_library = EffectLibrary()
effect_loader = EffectLoader()
chain_builder = EffectChainBuilder()
genre_chains = GenreEffectChains()
effect_presets = EffectPresets()