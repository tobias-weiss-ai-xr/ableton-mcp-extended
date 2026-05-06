#!/usr/bin/env python3
"""Simple script to create a working dub techno session with instruments and clips."""

from dub.mcp.client import MCPClient
from dub.core.pattern_generator import PatternGenerator
from dub.config.settings import (
    TRACKS,
    TRACK_NAMES,
    CLIPS_PER_TRACK,
    PATTERN_DURATIONS,
    TEMPO,
)


def main():
    print("=" * 60)
    print("CREATING DUB TECHNO SESSION")
    print("=" * 60)
    print()

    try:
        client = MCPClient()
        client.connect()
        print("Connected to Ableton MCP\n")

        # Step 1: Set tempo
        print("[1/6] Setting tempo...")
        result = client.tcp_command("set_tempo", {"tempo": TEMPO})
        print(f"  Tempo set to {TEMPO} BPM\n")

        # Step 2: Clear existing tracks
        print("[2/6] Clearing existing tracks...")
        result = client.tcp_command("delete_all_tracks", {})
        deleted = result.get("result", {}).get("deleted_count", 0)
        print(f"  Deleted {deleted} tracks\n")

        # Step 3: Create 8 MIDI tracks
        print("[3/6] Creating 8 MIDI tracks...")
        for track_idx in range(8):
            client.tcp_command("create_midi_track", {"index": -1})
            client.tcp_command(
                "set_track_name",
                {"track_index": track_idx, "name": TRACK_NAMES[track_idx]},
            )
        print(f"  Created {len(TRACK_NAMES)} tracks\n")

        # Step 4: Load instruments
        print("[4/6] Loading instruments...")
        instruments = {
            0: "Operator",  # Kick
            1: "Operator",  # Sub-bass
            2: "Drums/Drum Rack",  # Hi-hats
            3: "Wavetable",  # Synth Pads
            4: "Wavetable",  # FX
            5: "Analog",  # Dub Delays
            6: "Drums/Drum Rack",  # Percussion
            7: "Wavetable",  # Synth Lead
        }

        for track_idx, device_name in instruments.items():
            uri = f"query:Synths#{device_name}"
            result = client.tcp_command(
                "load_browser_item", {"track_index": track_idx, "item_uri": uri}
            )
            print(f"  Track {track_idx} ({TRACK_NAMES[track_idx]}): {device_name}")

        # Load drum kit for hihat
        result = client.tcp_command(
            "load_drum_kit",
            {
                "track_index": 2,
                "rack_uri": "Drums/Drum Rack",
                "kit_path": "Drums/Drum Rack/Kits 909",
            },
        )
        print("  Loaded 909 drum kit for hihats\n")

        # Step 5: Generate patterns
        print("[5/6] Generating MIDI patterns...")
        pattern_gen = PatternGenerator()
        patterns = {}

        for track_name, track_idx in TRACKS.items():
            bars = PATTERN_DURATIONS[track_idx % 3]

            if track_name == "kick":
                notes = pattern_gen.generate_kick(bars)
            elif track_name == "bass":
                notes = pattern_gen.generate_bass(bars, root=36)
            elif track_name == "hihat":
                notes = pattern_gen.generate_hihat(bars, density="medium")
            elif track_name == "pads":
                notes = pattern_gen.generate_pads(bars, chord_type="minor")
            elif track_name == "fx":
                notes = pattern_gen.generate_fx(bars, fx_type="sweep")
            elif track_name == "delays":
                notes = pattern_gen.generate_fx(bars, fx_type="impact")
            elif track_name == "percussion":
                notes = pattern_gen.generate_fx(bars, fx_type="impact")
            elif track_name == "lead":
                notes = pattern_gen.generate_pads(bars, chord_type="minor")

            patterns[track_name] = notes
            print(f"  Generated {len(notes)} notes for {track_name}")
        print()

        # Step 6: Create clips with notes
        print("[6/6] Creating clips with notes...")
        clips_created = 0

        for track_name, track_idx in TRACKS.items():
            notes = patterns[track_name]
            bars = PATTERN_DURATIONS[track_idx % 3]
            clip_length = bars * 4.0

            for clip_index in range(CLIPS_PER_TRACK):
                try:
                    # Create clip
                    client.tcp_command(
                        "create_clip",
                        {
                            "track_index": track_idx,
                            "clip_index": clip_index,
                            "length": clip_length,
                        },
                    )

                    # Add notes
                    if notes:
                        client.tcp_command(
                            "add_notes_to_clip",
                            {
                                "track_index": track_idx,
                                "clip_index": clip_index,
                                "notes": notes,
                            },
                        )

                    # Set clip name
                    clip_name = f"{track_name[:3]}_{bars}bar_{clip_index + 1}"
                    client.tcp_command(
                        "set_clip_name",
                        {
                            "track_index": track_idx,
                            "clip_index": clip_index,
                            "name": clip_name,
                        },
                    )

                    clips_created += 1
                except Exception as e:
                    print(f"  ERROR creating clip {track_idx}/{clip_index}: {e}")

        print(f"\n  Created {clips_created} clips ({CLIPS_PER_TRACK} per track)\n")

        # Summary
        print("=" * 60)
        print("SESSION CREATION COMPLETE!")
        print("=" * 60)
        print(f"  {len(TRACKS)} MIDI tracks")
        print(f"  {clips_created} clips total")
        print(f"  {TEMPO} BPM")
        print()
        print("Track instruments:")
        for track_idx, device_name in instruments.items():
            print(f"  Track {track_idx} ({TRACK_NAMES[track_idx]}): {device_name}")
        print()

        client.close()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
