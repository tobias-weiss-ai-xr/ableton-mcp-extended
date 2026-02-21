"""Tests for chord namer utility."""

import pytest
import sys
import os

# Add music_theory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestChordNamer:
    """Tests for chord namer function."""

    def test_major_chord_naming(self):
        """Test major chord naming."""
        from music_theory.chord import generate_chord_name

        # C major
        assert generate_chord_name(60, [0, 4, 7]) == "Cmaj"
        # A minor (relative minor of C)
        assert generate_chord_name(57, [0, 3, 7]) == "Amin"

    def test_7th_chord_naming(self):
        """Test 7th chord naming."""
        from music_theory.chord import generate_chord_name

        # C dominant 7
        assert generate_chord_name(60, [0, 4, 7, 10]) == "C7"
        # A minor 7
        assert generate_chord_name(57, [0, 3, 7, 10]) == "Amin7"

    def test_power_chord_naming(self):
        """Test power chord naming."""
        from music_theory.chord import generate_chord_name

        # Power chord: root and fifth only
        assert generate_chord_name(60, [0, 7]) == "C5"

    def test_octave_handling(self):
        """Test chord naming across octaves."""
        from music_theory.chord import generate_chord_name

        # C0 major
        assert generate_chord_name(12, [0, 4, 7]) == "Cmaj"
        # C8 major (above standard MIDI range)
        assert generate_chord_name(120, [0, 4, 7]) == "Cmaj"

    def test_unknown_chord(self):
        """Test unknown chord pattern."""
        from music_theory.chord import generate_chord_name

        assert generate_chord_name(60, [0, 1, 2]) == "C??"
