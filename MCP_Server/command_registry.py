"""Command contract registry for Ableton MCP Extended.

Defines the single source of truth for command signatures, transport
assignments, and parameter contracts.  Used by the MCP server, the
Remote Script dispatch, and tests to guarantee that command names,
parameter types, and normalization ranges are consistent everywhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParamSpec:
    """Contract for a single parameter of a command."""

    type: Literal["int", "float", "bool", "str", "list"]
    min_value: float | None = None   # normalized 0.0-1.0 where applicable
    max_value: float | None = None   # normalized 0.0-1.0 where applicable
    description: str = ""

    # derived helpers -------------------------------------------------------

    def has_normalized_range(self) -> bool:
        return self.min_value is not None or self.max_value is not None


@dataclass(frozen=True)
class CommandSpec:
    """Contract for a single command."""

    name: str
    params: dict[str, ParamSpec] = field(default_factory=dict)
    transport: Literal["tcp", "udp"] = "tcp"
    modifying: bool = False
    description: str = ""


# ---------------------------------------------------------------------------
# Registry singleton
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, CommandSpec] = {}


def _register(spec: CommandSpec) -> None:
    _REGISTRY[spec.name] = spec


def _seed() -> None:
    """Populate the registry with the 10 UDP commands + 10 core TCP commands."""

    # ===================================================================
    # UDP commands (10) — fire-and-forget parameter changes / triggers
    # ===================================================================

    _register(CommandSpec(
        name="set_device_parameter",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "device_index": ParamSpec(type="int", description="Target device index"),
            "parameter_index": ParamSpec(type="int", description="Target parameter index"),
            "value": ParamSpec(
                type="float",
                min_value=0.0,
                max_value=1.0,
                description="Normalized parameter value (0.0-1.0)",
            ),
        },
        transport="udp",
        modifying=False,
        description="Set a device parameter value via UDP",
    ))

    _register(CommandSpec(
        name="set_track_volume",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "volume": ParamSpec(
                type="float",
                min_value=0.0,
                max_value=1.0,
                description="Normalized track volume (0.0-1.0)",
            ),
        },
        transport="udp",
        modifying=False,
        description="Set a track volume via UDP",
    ))

    _register(CommandSpec(
        name="set_track_pan",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "pan": ParamSpec(
                type="float",
                min_value=0.0,
                max_value=1.0,
                description="Normalized pan position (0.0=left, 0.5=center, 1.0=right)",
            ),
        },
        transport="udp",
        modifying=False,
        description="Set a track pan via UDP",
    ))

    _register(CommandSpec(
        name="set_track_mute",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "mute": ParamSpec(type="bool", description="Mute state (True/False)"),
        },
        transport="udp",
        modifying=False,
        description="Set a track mute state via UDP",
    ))

    _register(CommandSpec(
        name="set_track_solo",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "solo": ParamSpec(type="bool", description="Solo state (True/False)"),
        },
        transport="udp",
        modifying=False,
        description="Set a track solo state via UDP",
    ))

    _register(CommandSpec(
        name="set_track_arm",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "arm": ParamSpec(type="bool", description="Arm (record-enable) state (True/False)"),
        },
        transport="udp",
        modifying=False,
        description="Set a track arm state via UDP",
    ))

    _register(CommandSpec(
        name="set_master_volume",
        params={
            "volume": ParamSpec(
                type="float",
                min_value=0.0,
                max_value=1.0,
                description="Normalized master volume (0.0-1.0)",
            ),
        },
        transport="udp",
        modifying=False,
        description="Set the master volume via UDP",
    ))

    _register(CommandSpec(
        name="set_send_amount",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "send_index": ParamSpec(type="int", description="Target send index"),
            "amount": ParamSpec(
                type="float",
                min_value=0.0,
                max_value=1.0,
                description="Normalized send amount (0.0-1.0)",
            ),
        },
        transport="udp",
        modifying=False,
        description="Set a send amount via UDP",
    ))

    _register(CommandSpec(
        name="fire_clip",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "clip_index": ParamSpec(type="int", description="Target clip (slot) index"),
        },
        transport="udp",
        modifying=False,
        description="Fire (trigger) a clip via UDP",
    ))

    _register(CommandSpec(
        name="set_clip_launch_mode",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "clip_index": ParamSpec(type="int", description="Target clip (slot) index"),
            "mode": ParamSpec(type="int", description="Launch mode integer (0=trigger, 1=gate, 2=toggle, 3=repeat)"),
        },
        transport="udp",
        modifying=False,
        description="Set a clip launch mode via UDP",
    ))

    # ===================================================================
    # Core TCP commands (10) — state-modifying operations requiring ACK
    # ===================================================================

    _register(CommandSpec(
        name="create_midi_track",
        params={
            "index": ParamSpec(type="int", description="Track creation index (-1 = append)"),
        },
        transport="tcp",
        modifying=True,
        description="Create a new MIDI track",
    ))

    _register(CommandSpec(
        name="create_audio_track",
        params={
            "index": ParamSpec(type="int", description="Track creation index (-1 = append)"),
        },
        transport="tcp",
        modifying=True,
        description="Create a new audio track",
    ))

    _register(CommandSpec(
        name="delete_all_tracks",
        params={},
        transport="tcp",
        modifying=True,
        description="Delete all tracks in the session",
    ))

    _register(CommandSpec(
        name="set_track_name",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "name": ParamSpec(type="str", description="New track name"),
        },
        transport="tcp",
        modifying=True,
        description="Rename a track",
    ))

    _register(CommandSpec(
        name="create_clip",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "clip_index": ParamSpec(type="int", description="Target clip (slot) index"),
            "length": ParamSpec(type="float", description="Clip length in beats"),
        },
        transport="tcp",
        modifying=True,
        description="Create an empty clip in a track slot",
    ))

    _register(CommandSpec(
        name="add_notes_to_clip",
        params={
            "track_index": ParamSpec(type="int", description="Target track index"),
            "clip_index": ParamSpec(type="int", description="Target clip (slot) index"),
            "notes": ParamSpec(type="list", description="List of note dicts with pitch, start, duration, velocity"),
        },
        transport="tcp",
        modifying=True,
        description="Add MIDI notes to an existing clip",
    ))

    _register(CommandSpec(
        name="set_tempo",
        params={
            "tempo": ParamSpec(type="float", description="Tempo in BPM (e.g. 120.0)"),
        },
        transport="tcp",
        modifying=True,
        description="Set the global tempo",
    ))

    _register(CommandSpec(
        name="set_global_quantization",
        params={
            "value": ParamSpec(type="str", description="Quantization value (e.g. '1 Bar', '1/4', 'None')"),
        },
        transport="tcp",
        modifying=True,
        description="Set the global quantization amount",
    ))

    _register(CommandSpec(
        name="start_playback",
        params={},
        transport="tcp",
        modifying=True,
        description="Start session playback",
    ))

    _register(CommandSpec(
        name="stop_playback",
        params={},
        transport="tcp",
        modifying=True,
        description="Stop session playback",
    ))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_registry() -> dict[str, CommandSpec]:
    """Return the full command registry (dict keyed by command name)."""
    if not _REGISTRY:
        _seed()
    return dict(_REGISTRY)  # defensive copy


def get_command(name: str) -> CommandSpec | None:
    """Look up a single command by name; returns None if not found."""
    return get_registry().get(name)


def get_udp_commands() -> dict[str, CommandSpec]:
    """Return only the UDP-transport commands."""
    return {n: s for n, s in get_registry().items() if s.transport == "udp"}


def get_tcp_commands() -> dict[str, CommandSpec]:
    """Return only the TCP-transport commands."""
    return {n: s for n, s in get_registry().items() if s.transport == "tcp"}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class RegistryValidationError(Exception):
    """Raised when validate_registry() detects a contract violation."""


def validate_registry(registry: dict[str, CommandSpec] | None = None) -> list[str]:
    """Validate the registry and return a list of error messages.

    Checks:
      1. Duplicate command names (should be impossible with a dict, but
         defensive against programmatic construction).
      2. Parameter ranges outside 0.0-1.0.
      3. Missing (empty) descriptions on commands or params.
      4. UDP commands marked as modifying.

    Returns an empty list if the registry is valid.

    Raises nothing — callers should assert ``errors == []`` or raise
    ``RegistryValidationError``.
    """
    if registry is None:
        registry = get_registry()

    errors: list[str] = []

    # 1. Duplicate names — both dict-key level and spec.name level
    seen: set[str] = set()
    for key, spec in registry.items():
        if key in seen:
            errors.append(f"Duplicate command name: {key!r}")
        seen.add(key)
    # Also catch mismatched key/spec.name or duplicate spec.name
    spec_names: list[str] = [spec.name for spec in registry.values()]
    if len(spec_names) != len(set(spec_names)):
        name_seen: set[str] = set()
        for spec in registry.values():
            if spec.name in name_seen:
                errors.append(f"Duplicate command name: {spec.name!r}")
            name_seen.add(spec.name)

    # 2-4. Per-command checks
    for cmd_name, spec in registry.items():
        # 3. Missing command description
        if not spec.description:
            errors.append(f"Command {cmd_name!r} has no description")

        # 4. UDP commands must not be marked modifying
        if spec.transport == "udp" and spec.modifying:
            errors.append(
                f"UDP command {cmd_name!r} must not be marked modifying"
            )

        for param_name, pspec in spec.params.items():
            # 3. Missing param description
            if not pspec.description:
                errors.append(
                    f"Param {param_name!r} of command {cmd_name!r} has no description"
                )

            # 2. Range outside 0.0-1.0
            if pspec.min_value is not None and not (0.0 <= pspec.min_value <= 1.0):
                errors.append(
                    f"Param {param_name!r} of command {cmd_name!r} "
                    f"has min_value={pspec.min_value} outside [0.0, 1.0]"
                )
            if pspec.max_value is not None and not (0.0 <= pspec.max_value <= 1.0):
                errors.append(
                    f"Param {param_name!r} of command {cmd_name!r} "
                    f"has max_value={pspec.max_value} outside [0.0, 1.0]"
                )

    return errors
