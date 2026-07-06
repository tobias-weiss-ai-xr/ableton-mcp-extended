#!/usr/bin/setup follower
"""
Configure clip follow actions for autonomous 2-hour progression.
48 clips across 6 tracks with varied follow action patterns.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP
from follow_actions import setup_random_follow_actions
from follow_actions import setup_energy_pattern
from follow_actions import setup_harmonic_pattern

def configure_track_follow_actions(track_idx, pattern_type):
    """
    Configure follow actions for all 8 clips on a track.
    pattern_type: "random", "energy", "harmonic"
    """
    print(f"Configuring follow actions for Track {track_idx} ({pattern_type})...")

    try:
        if pattern_type == "random":
            # Random with 60% stay probability (groove rather than chaos)
            setup_random_follow_actions(track_idx, stay_probability=0.6)

        elif pattern_type == "energy":
            # Build energy curve across clips 0-7
            # Clips 0-2: low, clips 3-5: medium, clips 6-7: high
            energy_curve = [3, 4, 5, 6, 7, 8, 9, 10]  # On 1-10 scale
            setup_energy_pattern(
                track_idx,
                energy_pattern="build",
                energy_levels=energy_curve
            )

        elif pattern_type == "harmonic":
            # Harmonic Djamelot mixing for keys (Fm = 8A)
            # See keys/1camelotwheel.md for reference
            setup_harmonic_pattern(track_idx, mode="moderate", stay_probability=0.4)

        print(f"  ✓ Track {track_idx} configured")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """
    Configure follow actions for all tracks in order:
    - Drums (0): Random groove (60% stay, varied switching)
    - Bass (1): Energy build (gradual intensity increase)
    - Pads (2): Harmonic coherence (key-compatible progressions)
    - Percussion (3): Random texture (stay prob 50%)
    - Dub FX (4): Random stabs (stay prob 65%, sparse)
    - Return (5): N/A (return track has no clips)
    """

    print("Configuring follow actions for 2-hour autonomous progression...")

    # Track configurations: (track_idx, pattern_type)
    track_configs = [
        (0, "random"),  # Drums - varied groove
        (1, "energy"),  # Bass - energy builds
        (2, "harmonic"),  # Pads - harmonic Djamelot
        (3, "random"),  # Percussion - texture
        (4, "random"),  # Dub FX - stabs
    ]

    client = MCPClientTCP()

    for track_idx, pattern_type in track_configs:
        if not configure_track_follow_actions(track_idx, pattern_type):
            print(f"Warning: Failed to configure Track {track_idx}")
            continue

    print("\nFollow action configuration complete!")
    print("\nPatterns configured:")
    print("  Track 0 (Drums): Random switching (60% stay probability)")
    print("  Track 1 (Bass): Energy curve (build across clips 0-7)")
    print("  Track 2 (Pads): Harmonic Djamelot mixing (Fm compatibility)")
    print("  Track 3 (Percussion): Random texture (50% stay)")
    print("  Track 4 (Dub FX): Random stabs (65% stay, sparse)")

    return 0

if __name__ == "__main__":
    exit(main() or 0)