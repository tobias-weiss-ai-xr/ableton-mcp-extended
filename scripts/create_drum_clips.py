#!/usr/bin/env python
"""
Create 8 varied drum clips for Track 0 using dub techno patterns.
Patterns: one_drop, rockers, steppers, dub_techno variants.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP
from clip_patterns import create_drum_pattern

def main():
    """
    Create 8 drum clips with varied dub techno patterns for Track 0.
    Each clip spans 16 beats (4 bars) to use one_drop/dub_techno grids effectively.
    """
    print("Creating 8 drum clips for Track 0 (Drums)...")

    # Track 0, all 8 clip slots (0-7)
    track_idx = 0

    # Pattern configurations for each clip slot
    clip_configs = [
        ("one_drop", "Classic dub kick on 1, delayed snare on 3"),
        ("rockers", "Jamaican skank - offbeat emphasis"),
        ("steppers", "Driving 4x4 kick distribution"),
        ("dub_techno", "Syncopated dub with offbeat accents"),
        ("one_drop", "Minimal version - more space"),
        ("rockers", "Busier version - more hi-hats"),
        ("steppers", "Breakdown variant - less hits"),
        ("dub_techno", "Maximum syncopation - full energy"),
    ]

    client = MCPClientTCP()

    for clip_idx, (pattern_name, description) in enumerate(clip_configs):
        print(f"  Clip {clip_idx}: {pattern_name} - {description}")

        try:
            # Create clip with 16 beats (4 bars) for pattern flexibility
            result = create_drum_pattern(
                track_idx=track_idx,
                clip_idx=clip_idx,
                pattern_type=pattern_name,
                length=16.0
            )

            if result and result.get("success"):
                print(f"    ✓ Created")
            else:
                print(f"    ✗ Failed: {result.get('error', 'unknown')}")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    print("\nDrum clips creation complete!")

if __name__ == "__main__":
    main()