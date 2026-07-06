#!/usr/bin/env python
"""
Create 8 dub FX clips for Track 4.
Dub techno FX: filter sweeps, reverb risers, delay stabs, echo motifs.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP
from clip_patterns import create_drum_pattern  # Reusing pattern generator

def main():
    """
    Create 8 dub FX clips for Track 4.
    Use dub_techno pattern at upper register (C5-C7) for atmospheric FX sounds.
    These clips trigger built-in Live FX sends (Reverb, Delay) for dub stabs.
    """
    print("Creating 8 dub FX clips for Track 4 (Dub FX)...")

    client = MCPClientTCP()
    track_idx = 4

    fx_descriptions = [
        "Reverb riser (build-up)",
        "Delay ping (echo motif)",
        "Filter sweep down (drop)",
        "Reverb decay (wash out)",
        "Delay feedback (repeat)",
        "Filter sweep up (tension)",
        "Short stabs (accent)",
        "Long evolving pad (atmosphere)",
    ]

    for clip_idx in range(8):
        print(f"  Clip {clip_idx}: {fx_descriptions[clip_idx]}")
        try:
            # Use dub_techno pattern for rhythmic stabs
            result = create_drum_pattern(
                track_idx=track_idx,
                clip_index=clip_idx,
                pattern_type="dub_techno",
                length=16.0
            )
            print(f"    {'✓' if result else '✗'} Created")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    print("\nDub FX clips creation complete!")

if __name__ == "__main__":
    main()