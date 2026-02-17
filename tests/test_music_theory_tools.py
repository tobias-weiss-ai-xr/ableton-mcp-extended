"""Tests for music theory and live performance MCP tools."""

import pytest
import sys
import os

# Add MCP_Server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "MCP_Server"))


class TestHarmonicMixing:
    """Tests for harmonic mixing utilities."""

    def test_get_compatible_keys_major(self):
        """Test get_compatible_keys for major key."""
        import json
        from server import get_compatible_keys

        # Test 8A (A minor)
        result = json.loads(get_compatible_keys(None, "8A"))

        assert "compatible_keys" in result
        assert "9A" in result["compatible_keys"]["one_up"]
        assert "7A" in result["compatible_keys"]["one_down"]
        assert "8B" in result["compatible_keys"]["relative"]

    def test_get_compatible_keys_minor(self):
        """Test get_compatible_keys for minor key."""
        import json
        from server import get_compatible_keys

        result = json.loads(get_compatible_keys(None, "5B"))

        assert "compatible_keys" in result
        assert "6B" in result["compatible_keys"]["one_up"]
        assert "4B" in result["compatible_keys"]["one_down"]
        assert "5A" in result["compatible_keys"]["relative"]

    def test_get_compatible_keys_invalid_format(self):
        """Test get_compatible_keys with invalid format."""
        import json
        from server import get_compatible_keys

        result = json.loads(get_compatible_keys(None, "invalid"))
        assert "error" in result

    def test_get_compatible_keys_invalid_letter(self):
        """Test get_compatible_keys with invalid letter."""
        import json
        from server import get_compatible_keys

        result = json.loads(get_compatible_keys(None, "8C"))
        assert "error" in result

    def test_get_compatible_keys_invalid_number(self):
        """Test get_compatible_keys with invalid number."""
        import json
        from server import get_compatible_keys

        result = json.loads(get_compatible_keys(None, "13A"))
        assert "error" in result


class TestScaleIntervals:
    """Tests for scale interval constants."""

    def test_major_scale_intervals(self):
        """Test major scale has correct intervals."""
        from server import SCALE_INTERVALS

        assert SCALE_INTERVALS["major"] == [0, 2, 4, 5, 7, 9, 11]

    def test_minor_scale_intervals(self):
        """Test minor scale has correct intervals."""
        from server import SCALE_INTERVALS

        assert SCALE_INTERVALS["minor"] == [0, 2, 3, 5, 7, 8, 10]

    def test_dorian_scale_intervals(self):
        """Test dorian scale has correct intervals."""
        from server import SCALE_INTERVALS

        assert SCALE_INTERVALS["dorian"] == [0, 2, 3, 5, 7, 9, 10]

    def test_mixolydian_scale_intervals(self):
        """Test mixolydian scale has correct intervals."""
        from server import SCALE_INTERVALS

        assert SCALE_INTERVALS["mixolydian"] == [0, 2, 4, 5, 7, 9, 10]

    def test_pentatonic_scales_have_5_notes(self):
        """Test pentatonic scales have 5 notes."""
        from server import SCALE_INTERVALS

        assert len(SCALE_INTERVALS["pentatonic_major"]) == 5
        assert len(SCALE_INTERVALS["pentatonic_minor"]) == 5

    def test_blues_scale_has_6_notes(self):
        """Test blues scale has 6 notes."""
        from server import SCALE_INTERVALS

        assert len(SCALE_INTERVALS["blues"]) == 6


class TestChordIntervals:
    """Tests for chord interval constants."""

    def test_major_chord_intervals(self):
        """Test major chord has root, third, fifth."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["major"] == [0, 4, 7]

    def test_minor_chord_intervals(self):
        """Test minor chord has root, minor third, fifth."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["minor"] == [0, 3, 7]

    def test_diminished_chord_intervals(self):
        """Test diminished chord has correct intervals."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["dim"] == [0, 3, 6]

    def test_augmented_chord_intervals(self):
        """Test augmented chord has correct intervals."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["aug"] == [0, 4, 8]

    def test_seventh_chords_have_4_notes(self):
        """Test 7th chords have 4 notes."""
        from server import CHORD_INTERVALS

        assert len(CHORD_INTERVALS["maj7"]) == 4
        assert len(CHORD_INTERVALS["min7"]) == 4
        assert len(CHORD_INTERVALS["dom7"]) == 4
        assert len(CHORD_INTERVALS["dim7"]) == 4

    def test_seventh_chord_intervals(self):
        """Test specific 7th chord intervals."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["maj7"] == [0, 4, 7, 11]
        assert CHORD_INTERVALS["min7"] == [0, 3, 7, 10]
        assert CHORD_INTERVALS["dom7"] == [0, 4, 7, 10]

    def test_suspended_chords(self):
        """Test suspended chord intervals."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["sus2"] == [0, 2, 7]
        assert CHORD_INTERVALS["sus4"] == [0, 5, 7]

    def test_power_chord_has_2_notes(self):
        """Test power chord has root and fifth only."""
        from server import CHORD_INTERVALS

        assert CHORD_INTERVALS["power"] == [0, 7]
        assert len(CHORD_INTERVALS["power"]) == 2


class TestDrumPatterns:
    """Tests for drum pattern constants."""

    def test_drum_patterns_exist(self):
        """Test all expected drum patterns are defined."""
        from server import DRUM_PATTERNS

        expected = [
            "one_drop",
            "rockers",
            "steppers",
            "house_basic",
            "techno_4x4",
            "dub_techno",
        ]
        for pattern in expected:
            assert pattern in DRUM_PATTERNS, f"Missing drum pattern: {pattern}"

    def test_drum_patterns_have_kick(self):
        """Test all patterns have kick defined."""
        from server import DRUM_PATTERNS

        for pattern_name, pattern in DRUM_PATTERNS.items():
            assert "kick" in pattern["notes"], f"Pattern {pattern_name} missing kick"

    def test_drum_patterns_have_description(self):
        """Test all patterns have description."""
        from server import DRUM_PATTERNS

        for pattern_name, pattern in DRUM_PATTERNS.items():
            assert "description" in pattern, (
                f"Pattern {pattern_name} missing description"
            )

    def test_drum_patterns_have_bpm_range(self):
        """Test all patterns have bpm_range."""
        from server import DRUM_PATTERNS

        for pattern_name, pattern in DRUM_PATTERNS.items():
            assert "bpm_range" in pattern, f"Pattern {pattern_name} missing bpm_range"
            assert len(pattern["bpm_range"]) == 2, (
                f"Pattern {pattern_name} bpm_range should have 2 values"
            )

    def test_steppers_pattern_has_4_on_floor(self):
        """Test steppers pattern has 4-on-floor kick."""
        from server import DRUM_PATTERNS

        steppers_kick = DRUM_PATTERNS["steppers"]["notes"]["kick"]
        assert steppers_kick == [0.0, 1.0, 2.0, 3.0]

    def test_house_basic_pattern(self):
        """Test house_basic pattern structure."""
        from server import DRUM_PATTERNS

        pattern = DRUM_PATTERNS["house_basic"]
        assert pattern["notes"]["kick"] == [0.0, 1.0, 2.0, 3.0]
        assert pattern["notes"]["clap"] == [1.0, 3.0]
        assert "hat" in pattern["notes"]


class TestCamelotWheel:
    """Tests for Camelot wheel constant."""

    def test_camelot_wheel_has_24_keys(self):
        """Test Camelot wheel has all 24 keys."""
        from server import CAMELOT_WHEEL

        assert len(CAMELOT_WHEEL) == 24

    def test_camelot_wheel_major_minor_pairs(self):
        """Test major/minor pairs exist."""
        from server import CAMELOT_WHEEL

        for i in range(1, 13):
            assert f"{i}A" in CAMELOT_WHEEL, f"Missing key {i}A"
            assert f"{i}B" in CAMELOT_WHEEL, f"Missing key {i}B"

    def test_camelot_wheel_key_names_are_tuples(self):
        """Test key names are stored as tuples."""
        from server import CAMELOT_WHEEL

        for key, names in CAMELOT_WHEEL.items():
            assert isinstance(names, tuple), f"Key {key} names should be tuple"
            assert len(names) >= 1, f"Key {key} should have at least one name"

    def test_camelot_wheel_common_keys(self):
        """Test common key mappings."""
        from server import CAMELOT_WHEEL

        # 8A = A minor
        assert "A minor" in CAMELOT_WHEEL["8A"]
        # 8B = C major
        assert "C major" in CAMELOT_WHEEL["8B"]
        # 5A = C minor
        assert "C minor" in CAMELOT_WHEEL["5A"]


class TestConstantsCompleteness:
    """Tests to ensure all constants are properly defined."""

    def test_scale_intervals_all_scales_defined(self):
        """Test all expected scales are defined."""
        from server import SCALE_INTERVALS

        expected_scales = [
            "major",
            "minor",
            "dorian",
            "mixolydian",
            "phrygian",
            "lydian",
            "pentatonic_major",
            "pentatonic_minor",
            "blues",
        ]
        for scale in expected_scales:
            assert scale in SCALE_INTERVALS, f"Missing scale: {scale}"

    def test_chord_intervals_all_chords_defined(self):
        """Test all expected chord types are defined."""
        from server import CHORD_INTERVALS

        expected_chords = [
            "major",
            "minor",
            "dim",
            "aug",
            "maj7",
            "min7",
            "dom7",
            "dim7",
            "sus2",
            "sus4",
            "add9",
            "power",
        ]
        for chord in expected_chords:
            assert chord in CHORD_INTERVALS, f"Missing chord type: {chord}"
