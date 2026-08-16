#!/usr/bin/env python3
"""System configuration loader for Ableton MCP Extended.

Reads config/system.yaml relative to the repo root and exposes typed
accessors for ports, reconnect settings, the UDP whitelist, drum-kit
FileIds, drum pattern grids, and instrument preset URIs.

Mirrors the taxonomy.yaml loader pattern from music-research's
scripts/research_config.py: loads once, falls back to sane defaults
when the file is missing so every module stays runnable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Sequence

import yaml

# Repo root is two levels up from this file (MCP_Server/).
REPO_ROOT = Path(__file__).resolve().parent.parent

_CONFIG_PATH = REPO_ROOT / "config" / "system.yaml"

# ── Hardcoded sane defaults (used when YAML is absent or a key is missing) ───

_DEFAULTS: Dict[str, Any] = {
    "ports": {"tcp": 9877, "udp": 9878},
    "reconnect": {
        "max_attempts": 3,
        "delays": [1.0, 2.0, 4.0],
    },
    "udp_whitelist": [
        "set_device_parameter",
        "set_track_volume",
        "set_track_pan",
        "set_track_mute",
        "set_track_solo",
        "set_track_arm",
        "set_master_volume",
        "set_send_amount",
        "fire_clip",
        "set_clip_launch_mode",
    ],
    "drum_kits": {
        "default": "query:Drums#FileId_58622",
    },
    "drum_patterns": {
        "one_drop": {
            "description": "Classic dub techno - kick on 1, delayed snare",
            "bpm_range": [70, 80],
            "notes": {
                "kick": [2.0],
                "snare": [1.0, 3.0],
                "hat": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
            },
        },
        "rockers": {
            "description": "Jamaican skank - kick/hat offbeat emphasis",
            "bpm_range": [75, 85],
            "notes": {
                "kick": [0.0, 2.0],
                "snare": [1.0, 3.0],
                "hat": [0.5, 1.5, 2.5, 3.5],
            },
        },
        "steppers": {
            "description": "Dub steppers - 4-on-floor kick",
            "bpm_range": [75, 85],
            "notes": {
                "kick": [0.0, 1.0, 2.0, 3.0],
                "snare": [1.0, 3.0],
                "hat": [0.5, 1.5, 2.5, 3.5],
            },
        },
        "house_basic": {
            "description": "Four-on-the-floor with clap",
            "bpm_range": [120, 130],
            "notes": {
                "kick": [0.0, 1.0, 2.0, 3.0],
                "clap": [1.0, 3.0],
                "hat": [0.5, 1.5, 2.5, 3.5],
            },
        },
        "techno_4x4": {
            "description": "Driving techno - continuous kick",
            "bpm_range": [125, 140],
            "notes": {
                "kick": [0.0, 1.0, 2.0, 3.0],
                "hat": [0.5, 1.5, 2.5, 3.5],
            },
        },
        "dub_techno": {
            "description": "Sparse dub techno - offbeat accents",
            "bpm_range": [125, 135],
            "notes": {
                "kick": [0.0, 2.5, 3.0],
                "hat": [0.5, 2.0],
            },
        },
    },
    "instrument_presets": {
        "drums_default": "query:Drums#FileId_58622",
        "reverb": "query:Audio Effects#Reverb",
        "delay": "query:Audio Effects#Delay",
        "eq_eight": "query:Audio Effects#EQ Eight",
        "compressor": "query:Audio Effects#Compressor",
    },
}


# ── Loading helpers ──────────────────────────────────────────────────────────

def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Return *base* with *override* values merged in (shallow dicts recurse)."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load_config(path: Path | str | None = None) -> Dict[str, Any]:
    """Load system config from YAML, falling back to built-in defaults.

    If *path* is ``None`` the default ``config/system.yaml`` relative to
    the repo root is used.  When that file is missing (or empty) the
    hardcoded defaults are returned so callers never break.
    """
    path = Path(path) if path else _CONFIG_PATH
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        return _deep_merge(_DEFAULTS, raw)
    return dict(_DEFAULTS)


# ── Typed accessors ──────────────────────────────────────────────────────────

# Module-level singleton – loaded on first import.
_cfg: Dict[str, Any] | None = None


def _config() -> Dict[str, Any]:
    global _cfg
    if _cfg is None:
        _cfg = load_config()
    return _cfg


def get_port(name: str = "tcp") -> int:
    """Return a port number by name (``"tcp"`` or ``"udp"``)."""
    return _config().get("ports", {}).get(name, 9877 if name == "tcp" else 9878)


def tcp_port() -> int:
    return get_port("tcp")


def udp_port() -> int:
    return get_port("udp")


def reconnect_delays() -> List[float]:
    """Return the list of reconnect back-off delays (seconds)."""
    return list(_config().get("reconnect", {}).get("delays", [1.0, 2.0, 4.0]))


def reconnect_max_attempts() -> int:
    return _config().get("reconnect", {}).get("max_attempts", 3)


def udp_whitelist() -> FrozenSet[str]:
    """Return the frozen set of UDP-eligible command names."""
    return frozenset(_config().get("udp_whitelist", _DEFAULTS["udp_whitelist"]))


def drum_kit_fileid(name: str = "default") -> str:
    """Return the Ableton query URI for a named drum kit.

    Raises ``KeyError`` if *name* is unknown.
    """
    kits = _config().get("drum_kits", {})
    if name in kits:
        return kits[name]
    raise KeyError(f"Unknown drum kit: {name!r}. Available: {list(kits)}")


def drum_pattern(name: str) -> Dict[str, Any]:
    """Return the full pattern dict for *name* (description, bpm_range, notes).

    Raises ``KeyError`` if *name* is unknown.
    """
    patterns = _config().get("drum_patterns", {})
    if name in patterns:
        return patterns[name]
    raise KeyError(
        f"Unknown drum pattern: {name!r}. Available: {list(patterns)}"
    )


def drum_pattern_names() -> List[str]:
    """Return ordered list of available drum-pattern names."""
    return list(_config().get("drum_patterns", {}).keys())


def instrument_preset(name: str) -> str:
    """Return the Ableton query URI for a named instrument/effect preset.

    Raises ``KeyError`` if *name* is unknown.
    """
    presets = _config().get("instrument_presets", {})
    if name in presets:
        return presets[name]
    raise KeyError(
        f"Unknown instrument preset: {name!r}. Available: {list(presets)}"
    )


# ── Convenience: reload from a custom path (useful in tests) ─────────────────

def reload_config(path: Path | str | None = None) -> Dict[str, Any]:
    """Re-read config from *path* and replace the module-level singleton."""
    global _cfg
    _cfg = load_config(path)
    return _cfg


# ── CLI smoke-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    c = load_config()
    print(f"TCP port:  {c['ports']['tcp']}")
    print(f"UDP port:  {c['ports']['udp']}")
    print(f"Reconnect: {c['reconnect']['max_attempts']} attempts, "
          f"delays={c['reconnect']['delays']}")
    print(f"UDP whitelist ({len(c['udp_whitelist'])}): {', '.join(c['udp_whitelist'])}")
    print(f"Drum kits:  {list(c.get('drum_kits', {}))}")
    print(f"Patterns:   {list(c.get('drum_patterns', {}))}")
    print(f"Presets:    {list(c.get('instrument_presets', {}))}")
