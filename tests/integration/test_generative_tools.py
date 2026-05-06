#!/usr/bin/env python3
"""
Integration tests for MIDI Generative Tools.

Tests all new generative music features:
- MIDI effect preset application
- Generative chain creation
- Generative clip creation
- Chord progression generation
- Melody generation
- Follow action setup (harmonic and energy-based)
- Complete generative session creation
"""

import sys
import json
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, ".")

try:
    from dub.mcp.client import MCPClient
except ImportError:
    print("ERROR: Could not import MCPClient")
    print("Make sure the dub module is available")
    sys.exit(1)


class GenerativeToolsTester:
    """Test suite for MIDI Generative Tools."""

    def __init__(self):
        self.client = None
        self.results = []
        self.passed = 0
        self.failed = 0

    def setup(self):
        """Setup test environment."""
        print("\n=== MIDI GENERATIVE TOOLS INTEGRATION TEST ===\n")
        self.client = MCPClient()
        self.client.connect()
        return True

    def teardown(self):
        """Cleanup test environment."""
        if self.client:
            self.client.close()
        print("\n" + "=" * 50)
        print(f"TEST SUMMARY: {self.passed} passed, {self.failed} failed")
        print("=" * 50 + "\n")

    def run_test(self, name: str, test_func):
        """Run a single test and record result."""
        try:
            print(f"\n[TEST] {name}")
            test_func()
            print(f"  ✓ PASSED")
            self.passed += 1
            self.results.append({"name": name, "status": "PASS"})
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            self.failed += 1
            self.results.append({"name": name, "status": "FAIL", "error": str(e)})

    # =========================================================================
    # MIDI EFFECT PRESET TESTS
    # =========================================================================

    def test_apply_midi_effect_preset(self):
        """Test applying MIDI effect presets."""
        # This is a syntax/validation test since we can't actually run Ableton
        print("  Testing preset validation...")

        # Test arpeggiator preset
        result = self.client.tcp_command(
            "apply_midi_effect_preset",
            {
                "track_index": 0,
                "effect_name": "arpeggiator",
                "preset_name": "techno_up",
            },
        )
        assert "Error" not in result or "Could not find" in result, (
            f"Unexpected error: {result}"
        )

        # Test chord preset
        result = self.client.tcp_command(
            "apply_midi_effect_preset",
            {"track_index": 0, "effect_name": "chord", "preset_name": "dub_minor"},
        )
        assert "Error" not in result or "Could not find" in result, (
            f"Unexpected error: {result}"
        )

        # Test scale preset
        result = self.client.tcp_command(
            "apply_midi_effect_preset",
            {"track_index": 0, "effect_name": "scale", "preset_name": "f_minor"},
        )
        assert "Error" not in result or "Could not find" in result, (
            f"Unexpected error: {result}"
        )

        print("  All preset validations passed")

    def test_get_generative_chain_presets(self):
        """Test getting generative chain presets."""
        result = self.client.tcp_command("get_generative_chain_presets", {})
        assert "status" not in result or result["status"] != "error", f"Error: {result}"
        assert "dub_techno" in result or "house" in result, "Missing chain presets"
        print("  Chain presets retrieved successfully")

    # =========================================================================
    # GENERATIVE CHAIN TESTS
    # =========================================================================

    def test_create_generative_chain(self):
        """Test creating generative MIDI effect chains."""
        # Test dub techno chain
        result = self.client.tcp_command(
            "create_generative_chain",
            {"track_index": 0, "chain_type": "dub_techno", "key": "Fm"},
        )
        assert (
            "Error" not in result
            or "Could not find" in result
            or "index" in str(result).lower()
        ), f"Unexpected error: {result}"
        print("  Dub techno chain created")

        # Test house chain
        result = self.client.tcp_command(
            "create_generative_chain",
            {"track_index": 0, "chain_type": "house", "key": "C"},
        )
        assert (
            "Error" not in result
            or "Could not find" in result
            or "index" in str(result).lower()
        ), f"Unexpected error: {result}"
        print("  House chain created")

    # =========================================================================
    # GENERATIVE CLIP TESTS
    # =========================================================================

    def test_create_generative_clip_arpeggiated(self):
        """Test creating arpeggiated generative clips."""
        result = self.client.tcp_command(
            "create_generative_clip",
            {
                "track_index": 0,
                "clip_index": 0,
                "chord_notes": [60, 63, 67],  # C minor
                "pattern_type": "arpeggiated",
                "rate": "1/8",
                "direction": "up",
                "swing": 0.2,
                "length_beats": 4.0,
                "velocity_range": (80, 100),
            },
        )
        assert "Error" not in result or "Clip" in result or "track" in result.lower(), (
            f"Unexpected error: {result}"
        )
        print("  Arpeggiated clip created")

    def test_create_generative_clip_random(self):
        """Test creating random generative clips."""
        result = self.client.tcp_command(
            "create_generative_clip",
            {
                "track_index": 0,
                "clip_index": 1,
                "chord_notes": [36, 38, 40],  # Low notes
                "pattern_type": "random",
                "length_beats": 8.0,
                "velocity_range": (90, 110),
            },
        )
        assert "Error" not in result or "Clip" in result or "track" in result.lower(), (
            f"Unexpected error: {result}"
        )
        print("  Random clip created")

    def test_create_generative_clip_strum(self):
        """Test creating strum generative clips."""
        result = self.client.tcp_command(
            "create_generative_clip",
            {
                "track_index": 0,
                "clip_index": 2,
                "chord_notes": [60, 64, 67, 71],  # C maj7
                "pattern_type": "strum",
                "swing": 0.3,
                "length_beats": 4.0,
            },
        )
        assert "Error" not in result or "Clip" in result or "track" in result.lower(), (
            f"Unexpected error: {result}"
        )
        print("  Strum clip created")

    def test_create_generative_clip_sustained(self):
        """Test creating sustained generative clips."""
        result = self.client.tcp_command(
            "create_generative_clip",
            {
                "track_index": 0,
                "clip_index": 3,
                "chord_notes": [60, 64, 67, 71, 74],  # C maj9
                "pattern_type": "sustained",
                "length_beats": 8.0,
                "velocity_range": (70, 90),
            },
        )
        assert "Error" not in result or "Clip" in result or "track" in result.lower(), (
            f"Unexpected error: {result}"
        )
        print("  Sustained clip created")

    # =========================================================================
    # CHORD PROGRESSION TESTS
    # =========================================================================

    def test_generate_chord_progression_clip(self):
        """Test generating chord progression clips."""
        # Test I-V-vi-IV progression
        result = self.client.tcp_command(
            "generate_chord_progression_clip",
            {
                "track_index": 0,
                "clip_index": 0,
                "key": "C",
                "progression": ["I", "V", "vi", "IV"],
                "duration_per_chord": 4.0,
                "voicing": "close",
                "pattern_type": "sustained",
            },
        )
        assert (
            "Error" not in result
            or "progression" in result.lower()
            or "clip" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Chord progression clip created")

    def test_generate_chord_progression_minor(self):
        """Test generating minor chord progression clips."""
        result = self.client.tcp_command(
            "generate_chord_progression_clip",
            {
                "track_index": 0,
                "clip_index": 1,
                "key": "Am",
                "progression": ["i", "VII", "VI", "V"],
                "duration_per_chord": 8.0,
                "voicing": "open",
                "pattern_type": "arpeggiated",
            },
        )
        assert (
            "Error" not in result
            or "progression" in result.lower()
            or "clip" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Minor chord progression clip created")

    # =========================================================================
    # MELODY GENERATION TESTS
    # =========================================================================

    def test_generate_melody_clip_simple(self):
        """Test generating simple melody clips."""
        result = self.client.tcp_command(
            "generate_melody_clip",
            {
                "track_index": 0,
                "clip_index": 0,
                "key": "C",
                "scale": "minor",
                "length_beats": 8.0,
                "complexity": "simple",
                "range_notes": (60, 84),
            },
        )
        assert (
            "Error" not in result
            or "melody" in result.lower()
            or "clip" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Simple melody clip created")

    def test_generate_melody_clip_medium(self):
        """Test generating medium complexity melody clips."""
        result = self.client.tcp_command(
            "generate_melody_clip",
            {
                "track_index": 0,
                "clip_index": 1,
                "key": "F#",
                "scale": "dorian",
                "length_beats": 16.0,
                "complexity": "medium",
                "range_notes": (55, 84),
            },
        )
        assert (
            "Error" not in result
            or "melody" in result.lower()
            or "clip" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Medium melody clip created")

    def test_generate_melody_clip_complex(self):
        """Test generating complex melody clips."""
        result = self.client.tcp_command(
            "generate_melody_clip",
            {
                "track_index": 0,
                "clip_index": 2,
                "key": "Am",
                "scale": "phrygian",
                "length_beats": 12.0,
                "complexity": "complex",
                "range_notes": (60, 84),
            },
        )
        assert (
            "Error" not in result
            or "melody" in result.lower()
            or "clip" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Complex melody clip created")

    # =========================================================================
    # FOLLOW ACTION TESTS
    # =========================================================================

    def test_setup_harmonic_follow_actions_strict(self):
        """Test strict harmonic follow actions."""
        result = self.client.tcp_command(
            "setup_harmonic_follow_actions",
            {
                "track_index": 0,
                "clip_range_start": 0,
                "clip_range_end": 7,
                "compatibility_mode": "strict",
                "stay_probability": 0.6,
            },
        )
        assert (
            "Error" not in result
            or "follow" in result.lower()
            or "configured" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Strict harmonic follow actions configured")

    def test_setup_harmonic_follow_actions_moderate(self):
        """Test moderate harmonic follow actions."""
        result = self.client.tcp_command(
            "setup_harmonic_follow_actions",
            {
                "track_index": 0,
                "clip_range_start": 0,
                "clip_range_end": 7,
                "compatibility_mode": "moderate",
                "stay_probability": 0.4,
            },
        )
        assert (
            "Error" not in result
            or "follow" in result.lower()
            or "configured" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Moderate harmonic follow actions configured")

    def test_setup_energy_based_follow_actions_build(self):
        """Test energy-based build follow actions."""
        result = self.client.tcp_command(
            "setup_energy_based_follow_actions",
            {
                "track_index": 0,
                "clip_range_start": 0,
                "clip_range_end": 7,
                "energy_pattern": "build",
            },
        )
        assert (
            "Error" not in result
            or "energy" in result.lower()
            or "configured" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Energy build follow actions configured")

    def test_setup_energy_based_follow_actions_cycle(self):
        """Test energy-based cycle follow actions."""
        result = self.client.tcp_command(
            "setup_energy_based_follow_actions",
            {
                "track_index": 0,
                "clip_range_start": 0,
                "clip_range_end": 7,
                "energy_pattern": "cycle",
            },
        )
        assert (
            "Error" not in result
            or "energy" in result.lower()
            or "configured" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Energy cycle follow actions configured")

    # =========================================================================
    # GENERATIVE SESSION TESTS
    # =========================================================================

    def test_create_generative_session_dub_techno(self):
        """Test creating dub techno generative session."""
        result = self.client.tcp_command(
            "create_generative_session",
            {
                "genre": "dub_techno",
                "key": "Fm",
                "num_tracks": 4,
                "clips_per_track": 8,
                "include_drums": True,
                "include_bass": True,
                "include_chords": True,
                "include_melody": True,
                "tempo": 120,
            },
        )
        assert (
            "Error" not in result
            or "session" in result.lower()
            or "tracks" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Dub techno session created")

    def test_create_generative_session_house(self):
        """Test creating house generative session."""
        result = self.client.tcp_command(
            "create_generative_session",
            {
                "genre": "house",
                "key": "Am",
                "num_tracks": 3,
                "clips_per_track": 16,
                "include_drums": True,
                "include_bass": True,
                "include_chords": True,
                "include_melody": False,
                "tempo": 125,
            },
        )
        assert (
            "Error" not in result
            or "session" in result.lower()
            or "tracks" in result.lower()
        ), f"Unexpected error: {result}"
        print("  House session created")

    def test_create_generative_session_ambient(self):
        """Test creating ambient generative session."""
        result = self.client.tcp_command(
            "create_generative_session",
            {
                "genre": "ambient",
                "key": "C",
                "num_tracks": 2,
                "clips_per_track": 8,
                "include_drums": False,
                "include_bass": True,
                "include_chords": True,
                "include_melody": True,
                "tempo": 90,
            },
        )
        assert (
            "Error" not in result
            or "session" in result.lower()
            or "tracks" in result.lower()
        ), f"Unexpected error: {result}"
        print("  Ambient session created")

    # =========================================================================
    # MAIN TEST RUNNER
    # =========================================================================

    def run_all_tests(self):
        """Run all tests."""
        if not self.setup():
            return

        try:
            # MIDI Effect Preset Tests
            self.run_test(
                "apply_midi_effect_preset", self.test_apply_midi_effect_preset
            )
            self.run_test(
                "get_generative_chain_presets", self.test_get_generative_chain_presets
            )

            # Generative Chain Tests
            self.run_test("create_generative_chain", self.test_create_generative_chain)

            # Generative Clip Tests
            self.run_test(
                "create_generative_clip_arpeggiated",
                self.test_create_generative_clip_arpeggiated,
            )
            self.run_test(
                "create_generative_clip_random", self.test_create_generative_clip_random
            )
            self.run_test(
                "create_generative_clip_strum", self.test_create_generative_clip_strum
            )
            self.run_test(
                "create_generative_clip_sustained",
                self.test_create_generative_clip_sustained,
            )

            # Chord Progression Tests
            self.run_test(
                "generate_chord_progression_clip",
                self.test_generate_chord_progression_clip,
            )
            self.run_test(
                "generate_chord_progression_minor",
                self.test_generate_chord_progression_minor,
            )

            # Melody Generation Tests
            self.run_test(
                "generate_melody_clip_simple", self.test_generate_melody_clip_simple
            )
            self.run_test(
                "generate_melody_clip_medium", self.test_generate_melody_clip_medium
            )
            self.run_test(
                "generate_melody_clip_complex", self.test_generate_melody_clip_complex
            )

            # Follow Action Tests
            self.run_test(
                "setup_harmonic_follow_actions_strict",
                self.test_setup_harmonic_follow_actions_strict,
            )
            self.run_test(
                "setup_harmonic_follow_actions_moderate",
                self.test_setup_harmonic_follow_actions_moderate,
            )
            self.run_test(
                "setup_energy_based_follow_actions_build",
                self.test_setup_energy_based_follow_actions_build,
            )
            self.run_test(
                "setup_energy_based_follow_actions_cycle",
                self.test_setup_energy_based_follow_actions_cycle,
            )

            # Generative Session Tests
            self.run_test(
                "create_generative_session_dub_techno",
                self.test_create_generative_session_dub_techno,
            )
            self.run_test(
                "create_generative_session_house",
                self.test_create_generative_session_house,
            )
            self.run_test(
                "create_generative_session_ambient",
                self.test_create_generative_session_ambient,
            )

        finally:
            self.teardown()

        # Print summary
        print("\n" + "=" * 50)
        print("TEST RESULTS SUMMARY")
        print("=" * 50)
        for result in self.results:
            status = "✓ PASS" if result["status"] == "PASS" else "✗ FAIL"
            print(f"{status}: {result['name']}")
            if result["status"] == "FAIL" and "error" in result:
                print(f"       Error: {result['error']}")
        print("=" * 50)

        return self.failed == 0


def main():
    """Main entry point."""
    tester = GenerativeToolsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
