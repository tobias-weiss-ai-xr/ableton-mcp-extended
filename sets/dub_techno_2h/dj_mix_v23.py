#!/usr/bin/env python3
"""DJ Mix Controller - Variation 23

Executes initial commands and continues evolving the dub techno mix.
Rules:
- Bass: Volume 0.85-0.95 (main focus)
- Lead: Max volume 0.5
- Stabs: Volume 0.45, change rarely
- Evolve all patterns over time
"""

import sys
import time
import random

sys.path.insert(0, "C:/Users/Tobias/git/ableton-mcp-extended/sets/generative")
from mcp_client import MCPClient


def main():
    with MCPClient() as client:
        print("=== DJ MIX - VARIATION 23 ===\n")

        # Step 1: Execute initial commands
        print(">>> Firing initial clips...")

        # Fire track 6 clip 2 (lead/pad element)
        client.send("fire_clip", {"track_index": 6, "clip_index": 2})
        print("  Track 6, Clip 2 fired")

        # Fire track 1 clip 1 (bass element)
        client.send("fire_clip", {"track_index": 1, "clip_index": 1})
        print("  Track 1, Clip 1 fired")

        # Set master volume
        client.send("set_master_volume", {"volume": 0.82})
        print("  Master volume: 0.82")

        # Set bass track volume (track 1 is bass)
        client.send("set_track_volume", {"track_index": 1, "volume": 0.90})
        print("  Bass (Track 1) volume: 0.90")

        print("\n>>> Initial commands executed!")
        print("\n>>> Continuing mix evolution...")

        # Step 2: Evolve the mix
        # Apply filter sweeps and volume adjustments

        # Bass filter sweep (track 1)
        print("\n  Evolving bass...")
        bass_filter = random.uniform(0.35, 0.65)
        client.send(
            "set_device_parameter",
            {
                "track_index": 1,
                "device_index": 0,
                "parameter_index": 10,  # Filter cutoff
                "value": bass_filter,
            },
        )
        print(f"    Bass filter: {bass_filter:.2f}")

        # Pad/lead evolution (track 6) - keep volume low
        print("\n  Evolving pad/lead...")
        lead_volume = random.uniform(0.35, 0.50)  # Max 0.5 per rules
        client.send("set_track_volume", {"track_index": 6, "volume": lead_volume})
        print(f"    Lead volume: {lead_volume:.2f}")

        pad_filter = random.uniform(0.4, 0.7)
        client.send(
            "set_device_parameter",
            {
                "track_index": 6,
                "device_index": 0,
                "parameter_index": 1,  # Filter cutoff
                "value": pad_filter,
            },
        )
        print(f"    Pad filter: {pad_filter:.2f}")

        # Stabs (track 7 if exists) - keep at 0.45, change rarely
        print("\n  Checking stabs...")
        stab_volume = 0.45  # Fixed per rules
        client.send("set_track_volume", {"track_index": 7, "volume": stab_volume})
        print(f"    Stab volume: {stab_volume:.2f}")

        # Drums evolution (track 4) - add some filter movement
        print("\n  Evolving drums...")
        drums_filter = random.uniform(0.4, 0.75)
        client.send(
            "set_device_parameter",
            {
                "track_index": 4,
                "device_index": 0,
                "parameter_index": 2,  # Filter cutoff
                "value": drums_filter,
            },
        )
        print(f"    Drums filter: {drums_filter:.2f}")

        # Add some reverb/delay space
        drums_reverb = random.uniform(0.15, 0.35)
        client.send(
            "set_device_parameter",
            {
                "track_index": 4,
                "device_index": 0,
                "parameter_index": 8,  # Reverb
                "value": drums_reverb,
            },
        )
        print(f"    Drums reverb: {drums_reverb:.2f}")

        print("\n=== MIX EVOLUTION COMPLETE ===")
        print(f"  Bass focus: Volume 0.90")
        print(f"  Lead max: Volume {lead_volume:.2f}")
        print(f"  Stabs: Volume 0.45 (rarely changed)")
        print("\n  Ready for next variation...")


if __name__ == "__main__":
    main()
