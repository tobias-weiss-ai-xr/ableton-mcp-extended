"""Tests for config/system.yaml + MCP_Server/system_config.py loader.

Covers:
  - Loading from YAML file
  - Defaults fallback when file is missing
  - UDP whitelist exactness (10 commands, no more, no less)
  - Typed accessor correctness
  - KeyError for unknown drum patterns / kits / presets
  - reload_config() replaces module-level state
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from MCP_Server.system_config import (
    _DEFAULTS,
    _deep_merge,
    drum_kit_fileid,
    drum_pattern,
    drum_pattern_names,
    instrument_preset,
    load_config,
    get_port,
    reconnect_delays,
    reconnect_max_attempts,
    reload_config,
    tcp_port,
    udp_port,
    udp_whitelist,
)

# ── Constants (expected from AGENTS.md contract) ─────────────────────────────

EXPECTED_UDP_WHITELIST = [
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

EXPECTED_PATTERN_NAMES = [
    "one_drop",
    "rockers",
    "steppers",
    "house_basic",
    "techno_4x4",
    "dub_techno",
]


# ── 1. Loading from actual config/system.yaml ───────────────────────────────

class TestLoadFromYAML:
    """Verify load_config reads config/system.yaml correctly."""

    def test_load_returns_dict(self):
        cfg = load_config()
        assert isinstance(cfg, dict)

    def test_tcp_port(self):
        assert get_port("tcp") == 9877

    def test_udp_port(self):
        assert get_port("udp") == 9878

    def test_tcp_port_accessor(self):
        assert tcp_port() == 9877

    def test_udp_port_accessor(self):
        assert udp_port() == 9878

    def test_reconnect_max_attempts(self):
        assert reconnect_max_attempts() == 3

    def test_reconnect_delays(self):
        assert reconnect_delays() == [1.0, 2.0, 4.0]

    def test_drum_kit_default_fileid(self):
        assert drum_kit_fileid("default") == "query:Drums#FileId_58622"


# ── 2. Defaults fallback when file is missing ─────────────────────────────────

class TestDefaultsFallback:
    """When YAML file does not exist, sane defaults must be returned."""

    def test_missing_file_returns_defaults(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.yaml"
        cfg = load_config(missing)
        assert cfg["ports"]["tcp"] == 9877
        assert cfg["ports"]["udp"] == 9878

    def test_missing_file_has_full_udp_whitelist(self, tmp_path: Path):
        cfg = load_config(tmp_path / "missing.yaml")
        assert set(cfg["udp_whitelist"]) == set(EXPECTED_UDP_WHITELIST)

    def test_missing_file_has_all_patterns(self, tmp_path: Path):
        cfg = load_config(tmp_path / "missing.yaml")
        for name in EXPECTED_PATTERN_NAMES:
            assert name in cfg["drum_patterns"], f"Missing pattern {name}"

    def test_empty_yaml_falls_back_to_defaults(self, tmp_path: Path):
        empty = tmp_path / "empty.yaml"
        empty.write_text("")
        cfg = load_config(empty)
        assert cfg["ports"]["tcp"] == 9877


# ── 3. UDP whitelist exactness ──────────────────────────────────────────────

class TestUDPWhitelist:
    """The whitelist must be exactly 10 commands matching the AGENTS.md spec."""

    def test_whitelist_length(self):
        wl = udp_whitelist()
        assert len(wl) == 10

    def test_whitelist_exact_members(self):
        wl = udp_whitelist()
        assert set(wl) == set(EXPECTED_UDP_WHITELIST)

    def test_whitelist_is_frozenset(self):
        assert isinstance(udp_whitelist(), frozenset)

    def test_no_get_commands_in_whitelist(self):
        """get_* commands must NOT be in the UDP whitelist."""
        for cmd in udp_whitelist():
            assert not cmd.startswith("get_"), (
                f"{cmd} must not be UDP-eligible (get_* requires TCP)"
            )

    def test_no_delete_commands_in_whitelist(self):
        for cmd in udp_whitelist():
            assert not cmd.startswith("delete_"), (
                f"{cmd} must not be UDP-eligible (delete_* requires TCP)"
            )

    def test_no_quantize_or_undo_in_whitelist(self):
        forbidden = {"quantize", "undo", "redo"}
        for cmd in udp_whitelist():
            assert cmd not in forbidden, (
                f"{cmd} must not be UDP-eligible (requires TCP)"
            )


# ── 4. Drum patterns ────────────────────────────────────────────────────────

class TestDrumPatterns:
    def test_pattern_names(self):
        assert drum_pattern_names() == EXPECTED_PATTERN_NAMES

    def test_each_pattern_has_notes(self):
        for name in EXPECTED_PATTERN_NAMES:
            pat = drum_pattern(name)
            assert "notes" in pat, f"Pattern {name} missing 'notes'"
            assert isinstance(pat["notes"], dict)

    def test_each_pattern_has_description(self):
        for name in EXPECTED_PATTERN_NAMES:
            pat = drum_pattern(name)
            assert "description" in pat, f"Pattern {name} missing 'description'"

    def test_each_pattern_has_bpm_range(self):
        for name in EXPECTED_PATTERN_NAMES:
            pat = drum_pattern(name)
            assert "bpm_range" in pat, f"Pattern {name} missing 'bpm_range'"
            lo, hi = pat["bpm_range"]
            assert isinstance(lo, int)
            assert isinstance(hi, int)
            assert lo <= hi

    def test_pattern_times_within_bar(self):
        """All note positions should be within one bar (0.0 to 4.0 beats)."""
        for name in EXPECTED_PATTERN_NAMES:
            pat = drum_pattern(name)
            for instrument, hits in pat["notes"].items():
                for t in hits:
                    assert 0.0 <= t < 4.0, (
                        f"{name}/{instrument} beat {t} outside 0-4 range"
                    )

    def test_unknown_pattern_raises(self):
        with pytest.raises(KeyError, match="Unknown drum pattern"):
            drum_pattern("nonexistent_pattern")

    def test_one_drop_has_kick_on_3(self):
        pat = drum_pattern("one_drop")
        assert 2.0 in pat["notes"]["kick"]

    def test_dub_techno_is_sparse(self):
        """Dub techno should have few hits — max 2 instruments, few hits."""
        pat = drum_pattern("dub_techno")
        total_hits = sum(len(v) for v in pat["notes"].values())
        assert total_hits <= 5, "dub_techno should be sparse"


# ── 5. Instrument presets ────────────────────────────────────────────────────

class TestInstrumentPresets:
    def test_default_drum_preset(self):
        assert instrument_preset("drums_default") == "query:Drums#FileId_58622"

    def test_reverb_preset(self):
        assert instrument_preset("reverb") == "query:Audio Effects#Reverb"

    def test_unknown_preset_raises(self):
        with pytest.raises(KeyError, match="Unknown instrument preset"):
            instrument_preset("nonexistent")


# ── 6. Drum kits ────────────────────────────────────────────────────────────

class TestDrumKits:
    def test_default_kit_exists(self):
        assert drum_kit_fileid("default") == "query:Drums#FileId_58622"

    def test_unknown_kit_raises(self):
        with pytest.raises(KeyError, match="Unknown drum kit"):
            drum_kit_fileid("nonexistent_kit")


# ── 7. Deep merge helper ───────────────────────────────────────────────────

class TestDeepMerge:
    def test_shallow_override(self):
        base = {"a": 1, "b": 2}
        override = {"b": 99}
        assert _deep_merge(base, override) == {"a": 1, "b": 99}

    def test_nested_merge(self):
        base = {"ports": {"tcp": 9877, "udp": 9878}}
        override = {"ports": {"tcp": 9999}}
        result = _deep_merge(base, override)
        assert result == {"ports": {"tcp": 9999, "udp": 9878}}

    def test_does_not_mutate_base(self):
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        _deep_merge(base, override)
        assert "c" not in base["a"]


# ── 8. reload_config ───────────────────────────────────────────────────────

class TestReloadConfig:
    def test_reload_from_custom_path(self, tmp_path: Path):
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            textwrap.dedent("""\
            ports:
              tcp: 5555
              udp: 6666
            """)
        )
        # Reload and verify module-level state changed
        cfg = reload_config(custom)
        assert cfg["ports"]["tcp"] == 5555
        assert tcp_port() == 5555
        assert udp_port() == 6666

        # Reload back to default to not pollute other tests
        reload_config()

    def test_reload_missing_uses_defaults(self, tmp_path: Path):
        reload_config(tmp_path / "nope.yaml")
        assert tcp_port() == 9877
        reload_config()


# ── 9. YAML round-trip: defaults match what load_config returns ──────────────

class TestDefaultsConsistency:
    """Ensure the _DEFAULTS dict is internally consistent."""

    def test_defaults_has_10_udp_commands(self):
        assert len(_DEFAULTS["udp_whitelist"]) == 10

    def test_defaults_has_6_drum_patterns(self):
        assert len(_DEFAULTS["drum_patterns"]) == 6

    def test_defaults_udp_matches_expected(self):
        assert set(_DEFAULTS["udp_whitelist"]) == set(EXPECTED_UDP_WHITELIST)


# ── 10. Table-driven: port accessors (core contract) ───────────────────────

@pytest.mark.parametrize("name, expected_field", [
    ("tcp", "tcp_port"),
    ("udp", "udp_port"),
    ("reconnect", "reconnect"),  # non-port accessor name
])
def test_get_port_table(name, expected_field):
    result = get_port(name)
    assert isinstance(result, int)
    assert result > 0


# ── 11. Table-driven: UDP whitelist must NOT contain non-UDP commands ────────

@pytest.mark.parametrize("forbidden_prefix", [
    "get_",
    "delete_",
    "create_",
    "set_track_volume_exceeds",
    "quantize",
    "undo",
    "redo",
    "start_",
    "stop_",
])
def test_udp_whitelist_excludes(forbidden_prefix):
    wl = udp_whitelist()
    hits = [c for c in wl if c.startswith(forbidden_prefix)]
    assert not hits, f"UDP whitelist must not contain {forbidden_prefix}* commands: {hits}"


# ── 12. Table-driven: drum pattern must have non-empty note grids ────────────

@pytest.mark.parametrize("pattern_name", [
    "one_drop",
    "rockers",
    "steppers",
    "house_basic",
    "techno_4x4",
    "dub_techno",
])
def test_pattern_has_notes_table(pattern_name):
    from MCP_Server.system_config import drum_pattern
    grid = drum_pattern(pattern_name)
    assert grid is not None, f"pattern {pattern_name} returned None"
    assert len(grid) > 0, f"pattern {pattern_name} is empty"


# ── Value-asserting tests to kill mutations ────────────────────────────────

class TestMutationKillingValueAssertions:
    """Tests that exercise specific values to kill injected mutations."""

    def test_tcp_port_is_9877(self):
        """Mutation: 'name == \"tcp\"' → != would return wrong default."""
        assert get_port("tcp") == 9877

    def test_udp_port_is_9878(self):
        """Mutation: 'name == \"tcp\"' → != would affect UDP too."""
        assert get_port("udp") == 9878

    def test_tcp_accessor_matches_get_port(self):
        """Mutation: any accessor deviation would break equality."""
        assert tcp_port() == get_port("tcp")

    def test_udp_accessor_matches_get_port(self):
        assert udp_port() == get_port("udp")

    def test_udp_whitelist_is_frozen(self):
        """Mutation: frozenset behavior check."""
        wl = udp_whitelist()
        assert isinstance(wl, frozenset), f"Expected frozenset, got {type(wl)}"
        with pytest.raises(AttributeError):
            wl.add("should_not_work")

    def test_deep_merge_override_wins(self):
        """Mutation: 'and' in isinstance checks — must correctly merge nested dicts."""
        base = {"a": {"b": 1, "c": 2}}
        override = {"a": {"c": 99, "d": 3}}
        result = _deep_merge(base, override)
        assert result["a"]["b"] == 1, "Base value should survive"
        assert result["a"]["c"] == 99, "Override should win for key 'c'"
        assert result["a"]["d"] == 3, "Override should add new key 'd'"

    def test_deep_merge_flat_values(self):
        """Mutation: '+' vs '-' in string concat logic."""
        base = {"x": 10, "y": 20}
        override = {"y": 30, "z": 40}
        result = _deep_merge(base, override)
        assert result == {"x": 10, "y": 30, "z": 40}

    def test_reconnect_defaults(self):
        """Mutation: default value checks."""
        delays = reconnect_delays()
        assert isinstance(delays, list)
        assert len(delays) > 0
        assert all(isinstance(d, (int, float)) for d in delays)
        assert reconnect_max_attempts() > 0


class TestPortFallbackMutationKilling:
    """Force the get_port ternary default path (ports dict without the key)."""

    def test_get_port_fallback_when_ports_empty(self, tmp_path):
        from MCP_Server.system_config import get_port, reload_config
        cfg = tmp_path / "sys.yaml"
        cfg.write_text("ports: {}\n", encoding="utf-8")
        try:
            reload_config(cfg)
            assert get_port("tcp") == 9877   # ternary default path (name == "tcp")
            assert get_port("udp") == 9878   # ternary default path (else branch)
        finally:
            reload_config()  # restore module singleton for other tests
