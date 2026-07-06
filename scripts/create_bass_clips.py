#!/usr/bin/env python
"""
Create 8 bass clips for Track 1 using F minor scale.
Deep dub techno basslines with varied patterns.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP
from clip_patterns import create_bass_notes
from clip_patterns import create_drum_pattern

def main():
    """
    Create 8 bass clips with F minor scale variations for Track 1.
    Root note: F3 (MIDI 53), F minor: F-53, G#-56, Bb-58, C-60
    Each clip spans 16 beats (4 bars).
    """
    print("Creating 8 bass clips for Track 1 (Bass)...")

    track_idx = 1
    # F minor scale notes (F3 to C4)
    f_minor = [53, 56, 58, 60]  # F, G#, Bb, C

    # Pattern variations: (description, chord progression)
    clip_patterns = [
        ("Root emphasis", [[53] * 4, [56] * 2, [58] * 2, [60] * 4]),
        ("Root movement", [[53, 56], [56, 58], [58, 60], [60, 53]]),
        ("Triadic pulses", [[53], [56], [58], [60]]),
        ("Hold and glide", [[53], [53], [53], [53]]),
        ("Sub-bass anchor", [[53], [53, 53], [53, 53], [53, 53, 53]]),
        ("Melodic variation", [[55, 57, 59, 60], [53, 56, 58, 60], [54, 57, 58, 61], [53, 56, 58, 60]]),
        ("Staccato funk", [[53], [56], [60], [58]]),
        ("Retrograde descent", [[60], [58], [56], [53]]),
    ]

    client = MCPClientTCP()

    for clip_idx, (description, bars) in enumerate(clip_patterns):
        print(f"  Clip {clip_idx}: {description}")

        try:
            client.send_command("create_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "length": 16.0
            })

            notes = []
            beat = 0.0
            for bar in bars:
                pitch = bar[0]  # Use first note from bar pattern
                duration = 4.0  # Full bar
                notes.append({
                    "pitch": pitch,
                    "start_time": beat,
                    "duration": duration,
                    "velocity": 110
                })
                beat += 4.0

            # Add notes to clip
            result = client.send_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": clip_idx,
                "notes": notes
            })
            print(f"    {'✓' if result else '✗'} Created")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    print("\nBass clips creation complete!")

if __name__ == "__main__":
    main()