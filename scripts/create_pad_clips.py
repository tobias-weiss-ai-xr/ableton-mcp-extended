#!/usr/bin/env python
"""
Create 8 pad chord clips for Track 2 using F minor harmony.
Atmospheric dub techno pads with chord progressions.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP

def build_chord(root, intervals):
    """Build chord from root note with semitone intervals."""
    return [root + interval for interval in intervals]

def main():
    """
    Create 8 pad chord clips for Track 2 (Pads/Keys).
    F minor: F3-53, Ab3-56, Bb3-58, C4-60, Eb4-63, F4-65
    Chord types: Minor triads, 7ths, minor 9ths, suspended voicings
    Each clip spans 16 beats (4 bars), one chord per bar.
    """
    print("Creating 8 pad clips for Track 2 (Pads/Keys)...")

    track_idx = 2

    # F minor chord progressions: 4 chords x 4 bars/clip = 16 beats
    # Each clip gets a different progression
    clip_progressions = [
        # F minor triads
        [[53, 56, 60], [56, 59, 63], [58, 61, 65], [60, 56, 53]],
        # Minor 7ths
        [[53, 56, 60], [53, 56, 60, 63], [56, 59, 63], [56, 59, 63, 66]],
        # Sus2 and Sus4 voicings
        [[53, 56], [53, 58], [56, 59], [56, 61]],
        # Root + octave + major 7th (Australian minimal)
        [[53, 65], [56, 68], [58, 70], [60, 72]],
        # Small voicings around C4-C5
        [[56, 59, 63], [58, 61, 65], [53, 56, 60], [58, 61, 65]],
        # Root position with wide spread
        [[53, 56, 63], [56, 59, 65], [58, 61, 68], [60, 56, 53]],
        # Cluster chords (tight voicing with second intervals)
        [[53, 56, 60], [54, 58, 62], [55, 59, 63], [56, 60, 64]],
        # Open voicings for atmosphere
        [[53, 60], [56, 63], [58, 65], [60, 67]],
    ]

    client = MCPClientTCP()

    for clip_idx, progression in enumerate(clip_progressions):
        print(f"  Clip {clip_idx}: {progression}")
        try:
            # Create clip
            client.send_command("create_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "length": 16.0
            })

            # Build notes: one chord per bar (4 beats)
            notes = []
            for bar_idx, chord in enumerate(progression):
                start_beat = bar_idx * 4.0
                for pitch in chord:
                    notes.append({
                        "pitch": pitch,
                        "start_time": start_beat,
                        "duration": 4.0,
                        "velocity": 80
                    })

            result = client.send_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "notes": notes
            })
            print(f"    {'✓' if result else '✗'} Created")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    print("\nPad chord clips creation complete!")

if __name__ == "__main__":
    main()