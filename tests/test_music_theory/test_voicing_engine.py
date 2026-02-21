"""Tests for voicing engine utility."""

import pytest
import sys
import os

# Add music_theory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestVoicingEngine:
    """Tests for voicing engine function."""

    def test_root_position_voicing(self):
        """Test root position voicing (all notes clustered)."""
        from music_theory.voicing import generate_voicing

        # Cmaj7: C4 (60), E4 (64), G4 (67), B4 (71)
        voicing = generate_voicing(60, "maj7", "root")
        assert voicing == [60, 64, 67, 71]

    def test_drop_2_voicing_maj7(self):
        """Test drop 2 voicing for maj7."""
        from music_theory.voicing import generate_voicing

        # Drop 2 voicing: 7th dropped an octave, others in root position
        voicing = generate_voicing(60, "maj7", "drop_2")
        expected_voicing = [71, 60, 64, 67]  # B4 (71), C4 (60), E4 (64), G4 (67)
        assert voicing == expected_voicing

    def test_7_3_5_voicing_min7(self):
        """Test 7-3-5 voicing for min7 (common jazz voicing)."""
        from music_theory.voicing import generate_voicing

        # Cmin7: Bb (70), Eb (63), G (67) → 7-3-5
        voicing = generate_voicing(60, "min7", "7_3_5")
        assert voicing == [70, 63, 67]

    def test_power_chord_voicing_high_octave(self):
        """Test power chord voicing with high octave."""
        from music_theory.voicing import generate_voicing

        # Power chord C5: C (72) and G (79), keep in high octave
        voicing = generate_voicing(72, "5", "root")
        assert voicing == [72, 79]

    def test_avoid_clash_with_bass(self):
        """Test voicing avoids clashing with bass (MIDI < 50)."""
        from music_theory.voicing import generate_voicing

        # Play Cmaj7 in high octave (C5 = 72) to avoid clashing with bass C3 (48)
        voicing = generate_voicing(72, "maj7", "root")
        expected_notes = [min(note, 84) for note in [72, 76, 79, 83]]  # Cap at C6
        assert voicing == expected_notes

    def test_midi_127_overflow_protection(self):
        """Test voicing protects against MIDI 127 overflow."""
        from music_theory.voicing import generate_voicing

        # Request B8 (119) maj7 voicing
        voicing = generate_voicing(119, "maj7", "root")
        assert all(note <= 127 for note in voicing)
