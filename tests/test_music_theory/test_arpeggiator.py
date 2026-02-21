"""Tests for arpeggiator utility."""

import pytest
import sys
import os

# Add music_theory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestArpeggiator:
    """Tests for arpeggiator function."""

    def test_eighth_note_strum_maj7(self):
        """Test 8th note strum for maj7 chord."""
        from music_theory.arpeggiator import arpeggiate_chord

        # Cmaj7: C5 (72), E5 (76), G5 (79), B5 (83)
        original_notes = [72, 76, 79, 83]
        arpeggiated = arpeggiate_chord(original_notes, rate="1/8", repeats=2)

        # Expect 8 notes (4 notes × 2 repeats at 1/8)
        assert len(arpeggiated) == 8
        # First note = root (C5)
        assert arpeggiated[0]["pitch"] == 72
        assert arpeggiated[0]["start_time"] == 0.0
        # Second note: 3rd (E5) at 0.5 beats
        assert arpeggiated[1]["pitch"] == 76
        assert arpeggiated[1]["start_time"] == 0.5

    def test_sixteenth_note_triplet_min7(self):
        """Test 16th note triplet pattern for min7."""
        from music_theory.arpeggiator import arpeggiate_chord

        # Amin7: A4 (69), C5 (72), E5 (76), G5 (79)
        original_notes = [69, 72, 76, 79]
        arpeggiated = arpeggiate_chord(
            original_notes, rate="1/16", swing=0.2, repeats=1
        )

        # Expect 4 notes at 1/16 interval
        assert len(arpeggiated) == 4
        assert arpeggiated[0]["start_time"] == 0.0
        assert (
            arpeggiated[1]["start_time"] == 0.275
        )  # Swing: 1/16 (0.25) + swing delay (0.2 * 0.125 = 0.025) = 0.275

    def test_up_down_voicing(self):
        """Test arpeggiator with up/down direction."""
        from music_theory.arpeggiator import arpeggiate_chord

        # Cmaj7
        original_notes = [60, 64, 67]
        arpeggiated = arpeggiate_chord(
            original_notes, direction="down", rate="1/4", repeats=1
        )

        # Last note should be first in down direction
        assert arpeggiated[-1]["pitch"] == 60

    def test_voicing_template_preservation(self):
        """Test arpeggiator preserves incoming voicing order."""
        from music_theory.arpeggiator import arpeggiate_chord

        # Jazz voicing: 7-3-5 (B5, E5, G5)
        original_notes = [83, 76, 79]  # B5 > E5 > G5
        arpeggiated = arpeggiate_chord(original_notes, rate="1/8", repeats=1)

        # Preserve incoming voicing order: B5 → E5 → G5
        pitches = [note["pitch"] for note in arpeggiated]
        assert pitches == [83, 76, 79]

    def test_midi_127_overflow_protection(self):
        """Test arpeggiator protects against MIDI 127 overflow."""
        from music_theory.arpeggiator import arpeggiate_chord

        # Request B8 (119) chord -> should cap at 127
        very_high_notes = [119, 123, 126]
        arpeggiated = arpeggiate_chord(very_high_notes, rate="1/8", repeats=1)

        for note in arpeggiated:
            assert note["pitch"] <= 127
