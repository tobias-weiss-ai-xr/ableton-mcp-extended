#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-Hour Reggae Dub - Instrument and Effect Loading
==================================================

Loads instruments and effects onto tracks created by create_2h_dub_reggae.py

Tracks (8 total):
  0 - Drums (MIDI) - Drum Rack
  1 - Dub Bass (MIDI) - Operator
  2 - Guitar Chop (MIDI) - Electric
  3 - Organ Bubble (MIDI) - Organ
  4 - Synth Pad (MIDI) - Wavetable
  5 - FX (MIDI) - Simpler
  6 - Reverb Send (Audio) - Hybrid Reverb
  7 - Delay Send (Audio) - Simple Delay

Usage:
    python load_instruments_2h.py
    python load_instruments_2h.py --dry-run
"""

import socket
import json
import time
import sys
import argparse

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Server configuration
TCP_HOST = "localhost"
TCP_PORT = 9877


def send_command(command_type, params=None):
    """Send command to Ableton MCP server"""
    if params is None:
        params = {}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((TCP_HOST, TCP_PORT))

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))

        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()
        return response
    except Exception as e:
        print(f"Error sending command {command_type}: {str(e)}")
        return {"status": "error", "message": str(e)}


def print_separator():
    print("=" * 70)


def print_section(title):
    print_separator()
    print(f"  {title}")
    print_separator()


def main():
    parser = argparse.ArgumentParser(description="Load instruments for 2h dub reggae")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without executing"
    )
    args = parser.parse_args()

    print_separator()
    print("  2-HOUR REGGAE DUB - INSTRUMENT LOADING")
    print("  8 Tracks | 6 Instruments + 2 Effects")
    print_separator()
    print()

    if args.dry_run:
        print("[DRY RUN MODE] No commands will be sent to Ableton\n")

    # ============================================================================
    # INSTRUMENT DEFINITIONS (6 MIDI tracks)
    # ============================================================================
    instruments = [
        # (track_index, track_name, instrument_query)
        (0, "Drums", "query:Drums#Drum%20Rack"),
        (1, "Dub Bass", "query:Synths#Operator"),
        (2, "Guitar Chop", "query:Instruments#Electric"),
        (3, "Organ Bubble", "query:Instruments#Organ"),
        (4, "Synth Pad", "query:Synths#Wavetable"),
        (5, "FX", "query:Instruments#Simpler"),
    ]

    # ============================================================================
    # EFFECT DEFINITIONS (2 audio send tracks)
    # ============================================================================
    effects = [
        # (track_index, track_name, effect_query)
        (6, "Reverb Send", "query:Audio%20Effects#Hybrid%20Reverb"),
        (7, "Delay Send", "query:Audio%20Effects#Simple%20Delay"),
    ]

    # ============================================================================
    # VOLUME SETTINGS (dB values, bass prominent)
    # ============================================================================
    volumes = {
        0: -6.0,  # Drums - standard level
        1: -4.0,  # Dub Bass - prominent (main focus)
        2: -8.0,  # Guitar Chop - supporting
        3: -10.0,  # Organ Bubble - background texture
        4: -12.0,  # Synth Pad - subtle atmosphere
        5: -14.0,  # FX - occasional accents
        6: -6.0,  # Reverb Send - send level
        7: -6.0,  # Delay Send - send level
    }

    # ============================================================================
    # PHASE 1: LOAD INSTRUMENTS
    # ============================================================================
    print_section("PHASE 1: LOADING INSTRUMENTS")

    for track_idx, track_name, query in instruments:
        print(f"\n[{track_idx}] Loading {track_name}...")

        if args.dry_run:
            print(f"      [DRY RUN] Would load: {query}")
            continue

        result = send_command(
            "load_instrument_or_effect", {"track_index": track_idx, "uri": query}
        )

        if result.get("status") == "success":
            print(f"      [OK] {track_name}: {query}")
        else:
            print(f"      [ERROR] {result.get('message')}")

        time.sleep(0.5)

    # ============================================================================
    # PHASE 2: LOAD EFFECTS
    # ============================================================================
    print_section("PHASE 2: LOADING EFFECTS")

    for track_idx, track_name, query in effects:
        print(f"\n[{track_idx}] Loading {track_name}...")

        if args.dry_run:
            print(f"      [DRY RUN] Would load: {query}")
            continue

        result = send_command(
            "load_instrument_or_effect", {"track_index": track_idx, "uri": query}
        )

        if result.get("status") == "success":
            print(f"      [OK] {track_name}: {query}")
        else:
            print(f"      [ERROR] {result.get('message')}")

        time.sleep(0.5)

    # ============================================================================
    # PHASE 3: SET VOLUMES
    # ============================================================================
    print_section("PHASE 3: SETTING VOLUMES")

    # Convert dB to normalized value (approximate: 0dB = 0.85, -6dB = 0.70, etc.)
    def db_to_normalized(db):
        """Convert dB to normalized 0.0-1.0 range"""
        # Ableton uses: 0dB = 0.85, each 6dB = factor of 2
        # Simplified formula for typical range
        return max(0.0, min(1.0, 0.85 + (db / 60.0)))

    for track_idx, db in volumes.items():
        track_names = {
            0: "Drums",
            1: "Dub Bass",
            2: "Guitar Chop",
            3: "Organ Bubble",
            4: "Synth Pad",
            5: "FX",
            6: "Reverb Send",
            7: "Delay Send",
        }
        normalized = db_to_normalized(db)
        print(
            f"\n[{track_idx}] {track_names[track_idx]}: {db:+.1f}dB ({normalized:.2f})"
        )

        if args.dry_run:
            print(f"      [DRY RUN] Would set volume to {normalized:.2f}")
            continue

        result = send_command(
            "set_track_volume", {"track_index": track_idx, "volume": normalized}
        )

        if result.get("status") == "success":
            print(f"      [OK] Volume set")
        else:
            print(f"      [ERROR] {result.get('message')}")

        time.sleep(0.2)

    # ============================================================================
    # COMPLETE
    # ============================================================================
    print_section("LOADING COMPLETE")

    print("""
Manual Setup Required:
----------------------
1. Configure drum kit in Drum Rack (track 0)
   - Load kick, snare, hi-hat samples or preset

2. Set up send routing:
   - Route Drums -> Reverb Send (A)
   - Route Drums -> Delay Send (B)
   - Route Dub Bass -> Delay Send (B)
   - Route Guitar Chop -> Reverb Send (A)
   - Route Organ Bubble -> Reverb Send (A)
   - Route Synth Pad -> Reverb Send (A)

3. Configure effects:
   - Hybrid Reverb: Room size ~40%, Decay ~50%
   - Simple Delay: Time 1/4, Feedback 40%

4. Adjust instrument presets:
   - Operator: Choose a sub-bass preset (sine wave)
   - Electric: Choose a choppy electric piano tone
   - Organ: Choose a bubbly organ preset
   - Wavetable: Choose a warm pad sound

5. Fine-tune mix levels based on your monitoring environment

Run automation:
    python automate_2h_dub_reggae.py
""")

    print_separator()


if __name__ == "__main__":
    main()
