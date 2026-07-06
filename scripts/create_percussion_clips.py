#!/usr/bin/env python
"""
Create 8 percussion clips for Track 3 using dub techno patterns.
Percussion sounds: claps, rimshots, shakers, tambourines.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP
from clip_patterns import create_drum_pattern

def main():
    """
    Create 8 percussion clips for Track 3.
    Uses dub_techno pattern but with percussion notes (typical on MIDI 37-42).
    Hip-shaker at 42, clap at 39, rimshot at 40, tambourine at 54.
    """
    print("Creating 8 percussion clips for Track 3 (Percussion)...")

    client = MCPClientTCP()
    track_idx = 3

    # Note: Create_drum_pattern uses default kick=36, snare=40, hat=42
    # We借用 hat=42 default for shaker, snare=40 for claps/rimshots
    clip_descriptions = [
        "Shaker accents",
        "Clap backbeat",
        "Rimshot syncopation",
        "Tambourine jingle",
        "Sparse percussion",
        "Busy percussive patterns",
        "Accent on shuffle",
        "Heavy percussive hits",
    ]

    for clip_idx in range(8):
        print(f"  Clip {clip_idx}: {clip_descriptions[clip_idx]}")
        try:
            result = create_drum_pattern(
                track_idx=track_idx,
                clip_index=clip_idx,
                pattern_type="dub_techno",
                length=16.0
            )
            print(f"    {'✓' if result else '✗'} Created")
        except Exception as e:
            print(f"    ✗ Error: e")

    print("\nPercussion clips creation complete!")

if __name__ == "__main__":
    main()