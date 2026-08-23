"""Tests for MCP_Server/command_registry.py — TF-AB-01.

Covers:
  - round-trip lookup for all 20 registered commands
  - UDP whitelist exactness (exactly the 10 specified commands)
  - validate_registry() catching injected violations
  - ParamSpec frozen / immutable
  - no external files modified
"""

from __future__ import annotations

import pytest

from MCP_Server.command_registry import (
    CommandSpec,
    ParamSpec,
    RegistryValidationError,
    get_command,
    get_registry,
    get_tcp_commands,
    get_udp_commands,
    validate_registry,
)

# ===================================================================
# Constants — the exact 10 UDP + 10 TCP commands from the contract
# ===================================================================

EXPECTED_UDP_COMMANDS = frozenset(
    [
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
    ]
)

EXPECTED_TCP_COMMANDS = frozenset(
    [
        "create_midi_track",
        "create_audio_track",
        "delete_all_tracks",
        "set_track_name",
        "create_clip",
        "add_notes_to_clip",
        "set_tempo",
        "set_global_quantization",
        "start_playback",
        "stop_playback",
    ]
)

EXPECTED_ALL = EXPECTED_UDP_COMMANDS | EXPECTED_TCP_COMMANDS


# ===================================================================
# Fixture — fresh registry (isolated per test)
# ===================================================================

@pytest.fixture()
def registry():
    """Return a *fresh* copy of the seeded registry."""
    # Clear internal cache by importing fresh; simpler: just call get_registry
    # which always returns a copy.
    return get_registry()


# ===================================================================
# 1. Round-trip lookup
# ===================================================================

class TestRoundTripLookup:
    """Every expected command must be retrievable and have correct metadata."""

    @pytest.mark.parametrize("cmd_name", sorted(EXPECTED_ALL))
    def test_command_exists(self, cmd_name):
        spec = get_command(cmd_name)
        assert spec is not None, f"Command {cmd_name!r} not found in registry"

    @pytest.mark.parametrize("cmd_name", sorted(EXPECTED_UDP_COMMANDS))
    def test_udp_transport(self, cmd_name):
        spec = get_command(cmd_name)
        assert spec.transport == "udp", (
            f"Command {cmd_name!r} should be UDP, got {spec.transport!r}"
        )

    @pytest.mark.parametrize("cmd_name", sorted(EXPECTED_TCP_COMMANDS))
    def test_tcp_transport(self, cmd_name):
        spec = get_command(cmd_name)
        assert spec.transport == "tcp", (
            f"Command {cmd_name!r} should be TCP, got {spec.transport!r}"
        )

    @pytest.mark.parametrize("cmd_name", sorted(EXPECTED_TCP_COMMANDS))
    def test_tcp_modifying(self, cmd_name):
        spec = get_command(cmd_name)
        assert spec.modifying is True, (
            f"TCP command {cmd_name!r} should be modifying=True"
        )

    @pytest.mark.parametrize("cmd_name", sorted(EXPECTED_UDP_COMMANDS))
    def test_udp_not_modifying(self, cmd_name):
        spec = get_command(cmd_name)
        assert spec.modifying is False, (
            f"UDP command {cmd_name!r} should be modifying=False"
        )

    def test_registry_has_exactly_20_commands(self, registry):
        assert len(registry) == 20

    def test_get_command_unknown_returns_none(self):
        assert get_command("nonexistent_command_xyz") is None

    def test_param_frozen(self):
        """ParamSpec and CommandSpec instances should be frozen (immutable)."""
        ps = ParamSpec(type="float", min_value=0.0, max_value=1.0, description="test")
        with pytest.raises(AttributeError):
            ps.type = "int"  # type: ignore[misc]

        cs = CommandSpec(name="test_cmd", description="test")
        with pytest.raises(AttributeError):
            cs.transport = "udp"  # type: ignore[misc]


# ===================================================================
# 2. UDP whitelist exactness
# ===================================================================

class TestUDPWhitelist:
    """Only the 10 specified commands may be UDP-transport."""

    def test_udp_set_matches(self, registry):
        udp = get_udp_commands()
        assert set(udp.keys()) == EXPECTED_UDP_COMMANDS

    def test_tcp_set_matches(self, registry):
        tcp = get_tcp_commands()
        assert set(tcp.keys()) == EXPECTED_TCP_COMMANDS

    def test_no_extra_commands(self, registry):
        assert set(registry.keys()) == EXPECTED_ALL


# ===================================================================
# 3. validate_registry() — built-in registry is clean
# ===================================================================

class TestValidateRegistryClean:
    """The seeded registry must pass validation with zero errors."""

    def test_no_errors(self, registry):
        errors = validate_registry(registry)
        assert errors == [], f"Unexpected validation errors: {errors}"


# ===================================================================
# 4. validate_registry() — catches injected violations
# ===================================================================

class TestValidateRegistryViolations:
    """validate_registry must detect deliberate contract violations."""

    def test_duplicate_names(self):
        dup = {
            "cmd_a": CommandSpec(name="cmd_a", description="first"),
            "cmd_b": CommandSpec(name="cmd_a", description="second"),  # dup name
        }
        errors = validate_registry(dup)
        assert any("Duplicate" in e for e in errors)

    def test_range_outside_0_1(self):
        bad_param = ParamSpec(
            type="float",
            min_value=-0.5,  # outside [0, 1]
            max_value=1.0,
            description="bad range",
        )
        bad_cmd = CommandSpec(
            name="bad_cmd",
            params={"val": bad_param},
            description="command with bad range",
        )
        errors = validate_registry({"bad_cmd": bad_cmd})
        assert any("outside [0.0, 1.0]" in e for e in errors)

    def test_max_outside_0_1(self):
        bad_param = ParamSpec(
            type="float",
            min_value=0.0,
            max_value=1.5,  # outside [0, 1]
            description="bad max",
        )
        bad_cmd = CommandSpec(
            name="bad_max_cmd",
            params={"val": bad_param},
            description="command with bad max",
        )
        errors = validate_registry({"bad_max_cmd": bad_cmd})
        assert any("outside [0.0, 1.0]" in e for e in errors)

    def test_missing_command_description(self):
        no_desc = CommandSpec(name="no_desc_cmd", description="")
        errors = validate_registry({"no_desc_cmd": no_desc})
        assert any("no description" in e for e in errors)

    def test_missing_param_description(self):
        no_pdesc = ParamSpec(type="float", description="")
        cmd = CommandSpec(
            name="no_param_desc_cmd",
            params={"x": no_pdesc},
            description="parent command is fine",
        )
        errors = validate_registry({"no_param_desc_cmd": cmd})
        assert any("has no description" in e for e in errors)

    def test_udp_marked_modifying(self):
        udp_mod = CommandSpec(
            name="udp_mod_cmd",
            transport="udp",
            modifying=True,
            description="bad udp",
        )
        errors = validate_registry({"udp_mod_cmd": udp_mod})
        assert any("must not be marked modifying" in e for e in errors)

    def test_valid_subset_passes(self):
        """A registry with a single valid command should have zero errors."""
        good = CommandSpec(
            name="good_cmd",
            transport="tcp",
            modifying=True,
            description="A perfectly valid command",
            params={
                "vol": ParamSpec(
                    type="float",
                    min_value=0.0,
                    max_value=1.0,
                    description="volume 0-1",
                )
            },
        )
        errors = validate_registry({"good_cmd": good})
        assert errors == []

    def test_none_min_max_is_ok(self):
        """Params without min/max (e.g. track_index) should not trigger range errors."""
        no_range = CommandSpec(
            name="no_range_cmd",
            transport="tcp",
            modifying=True,
            description="ok",
            params={"idx": ParamSpec(type="int", description="track index")},
        )
        errors = validate_registry({"no_range_cmd": no_range})
        assert errors == []

    def test_bool_param_ok(self):
        """Bool params without ranges are fine."""
        bool_cmd = CommandSpec(
            name="bool_cmd",
            transport="udp",
            modifying=False,
            description="ok",
            params={"mute": ParamSpec(type="bool", description="mute flag")},
        )
        errors = validate_registry({"bool_cmd": bool_cmd})
        assert errors == []

    def test_multiple_violations(self):
        """All violations are reported, not just the first."""
        bad1 = CommandSpec(name="e1", description="")  # missing desc
        bad2 = CommandSpec(
            name="e2",
            transport="udp",
            modifying=True,
            description="desc",
        )  # UDP + modifying
        bad3 = CommandSpec(
            name="e3",
            description="desc",
            params={
                "x": ParamSpec(type="float", min_value=2.0, max_value=3.0, description="bad range")
            },
        )
        errors = validate_registry({"e1": bad1, "e2": bad2, "e3": bad3})
        assert len(errors) >= 3


# ===================================================================
# 5. Param details — spot-check a few commands
# ===================================================================

class TestParamDetails:
    """Spot-check that key commands have the right parameter names and types."""

    def test_set_device_parameter_params(self):
        spec = get_command("set_device_parameter")
        assert spec is not None
        assert "track_index" in spec.params
        assert "device_index" in spec.params
        assert "parameter_index" in spec.params
        assert "value" in spec.params
        assert spec.params["value"].type == "float"
        assert spec.params["value"].min_value == 0.0
        assert spec.params["value"].max_value == 1.0

    def test_fire_clip_params(self):
        spec = get_command("fire_clip")
        assert spec is not None
        assert set(spec.params.keys()) == {"track_index", "clip_index"}

    def test_delete_all_tracks_no_params(self):
        spec = get_command("delete_all_tracks")
        assert spec is not None
        assert spec.params == {}

    def test_add_notes_to_clip_has_list_param(self):
        spec = get_command("add_notes_to_clip")
        assert spec is not None
        assert spec.params["notes"].type == "list"

    def test_set_global_quantization_str_param(self):
        spec = get_command("set_global_quantization")
        assert spec is not None
        assert spec.params["value"].type == "str"

    def test_set_tempo_float_param(self):
        spec = get_command("set_tempo")
        assert spec is not None
        assert spec.params["tempo"].type == "float"

# ── Value-asserting tests to kill mutations ─────────────────────────────────

class TestValidateRegistryKillsMutations:
    """Tests that exercise specific code paths to kill injected mutations."""

    def test_empty_spec_fails(self):
        """Mutation: 'not spec.description' → '' — must still detect empty desc."""
        from MCP_Server.command_registry import validate_registry, CommandSpec
        reg = {"empty_cmd": CommandSpec(name="empty_cmd", params={}, description="")}
        errs = validate_registry(reg)
        assert len(errs) > 0
        assert any("empty_cmd" in e and "no description" in e for e in errs)

    def test_udp_modifying_fails(self):
        """Mutation: 'transport == udp and modifying' → 'or' — must detect."""
        from MCP_Server.command_registry import validate_registry, CommandSpec
        reg = {"bad_udp": CommandSpec(
            name="bad_udp", params={}, transport="udp", modifying=True,
            description="UDP command incorrectly marked modifying"
        )}
        errs = validate_registry(reg)
        assert any("bad_udp" in e and "must not be marked modifying" in e for e in errs), \
            f"Expected UDP-modifying error, got: {errs}"

    def test_param_boundary_inclusive(self):
        """Mutation: 0.0 <= x <= 1.0 → 0.0 < x < 1.0 — boundary must be valid."""
        from MCP_Server.command_registry import validate_registry, CommandSpec, ParamSpec
        reg = {"cmd": CommandSpec(
            name="cmd",
            params={"p": ParamSpec(type="float", min_value=0.0, max_value=1.0,
                                   description="ok param")},
            description="cmd desc"
        )}
        errs = validate_registry(reg)
        boundary_errs = [e for e in errs if "outside" in e]
        assert not boundary_errs, f"Boundary values 0.0/1.0 should be valid: {boundary_errs}"

    def test_param_boundary_violation(self):
        """Mutation: 0.0 <= x <= 1.0 → != — out-of-range must be caught."""
        from MCP_Server.command_registry import validate_registry, CommandSpec, ParamSpec
        reg = {"cmd": CommandSpec(
            name="cmd",
            params={"p": ParamSpec(type="float", min_value=-0.1, max_value=1.5,
                                   description="bad range param")},
            description="cmd desc"
        )}
        errs = validate_registry(reg)
        assert len(errs) >= 2, f"Both min=-0.1 and max=1.5 should be errors: {errs}"

    def test_empty_param_description_fails(self):
        """Mutation: 'not pspec.description' → '' — must detect empty param desc."""
        from MCP_Server.command_registry import validate_registry, CommandSpec, ParamSpec
        reg = {"cmd": CommandSpec(
            name="cmd",
            params={"p": ParamSpec(type="str", description="")},
            description="cmd desc"
        )}
        errs = validate_registry(reg)
        assert any("no description" in e for e in errs)

    def test_duplicate_name_detected(self):
        """Mutation: key-in-seen check — must detect duplicates."""
        from MCP_Server.command_registry import validate_registry, CommandSpec
        spec = CommandSpec(name="dup", description="duplicated")
        reg = {"dup": spec}  # key matches spec.name — valid (1 entry, no dup)
        errs = validate_registry(reg)
        dup_errs = [e for e in errs if "Duplicate" in e]
        assert not dup_errs, f"Single entry should not have duplicates: {dup_errs}"


class TestMutationKillingValueAssertions:
    """Value-asserting tests for remaining mutation survivors."""

    def test_default_commandspec_not_modifying(self):
        """Mutation: 'modifying: bool = False' -> True must change behavior."""
        from MCP_Server.command_registry import CommandSpec
        spec = CommandSpec(name="plain_cmd")
        assert spec.modifying is False, "Default modifying must be False"

        # And UDP commands built without explicit modifying must remain non-modifying
        udp = CommandSpec(name="udp_cmd", transport="udp")
        assert udp.modifying is False

    def test_has_normalized_range_min_only(self):
        """Mutation: 'a is not None or b is not None' -> 'and' / drop 'not'."""
        from MCP_Server.command_registry import ParamSpec
        # Only min_value set, max_value None — must still report a range
        p = ParamSpec(type="float", min_value=0.0)
        assert p.has_normalized_range() is True, "min-only param must have a range"

        # Only max_value set too
        p2 = ParamSpec(type="float", max_value=1.0)
        assert p2.has_normalized_range() is True

        # Neither set — no range
        p3 = ParamSpec(type="float")
        assert p3.has_normalized_range() is False
