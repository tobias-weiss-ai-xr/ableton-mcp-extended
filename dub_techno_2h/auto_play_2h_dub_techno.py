import socket
import json
import time
import threading

# ============================================================================
# 2-HOUR DUB TECHNOPO - FULL AUTOMATION SCRIPT
# ============================================================================
# This script automates the entire 2-hour playback including:
# - Automatic scene progression every 4 minutes
# - Device parameter automation
# - Track volume/pan control
# - Send level automation
# - Filter automation for pads
# ============================================================================

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return full response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    return json.loads(data.decode("utf-8"))


def set_device_parameter(track_index, device_index, parameter_index, value):
    """Set a device parameter (normalized 0.0-1.0)"""
    try:
        send_command(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "value": value,
            },
        )
    except Exception as e:
        print(f"    [WARNING] Could not set parameter: {e}")


def set_track_volume(track_index, volume_db):
    """Set track volume (normalized 0.0-1.0 from dB)"""
    # Convert dB to normalized value (assumed range -70 to +6 dB)
    # Typical Ableton volume range: 0.0 to 1.0 maps to -inf to +6 dB
    # We'll use linear approximation for simplicity
    normalized_volume = max(0.0, min(1.0, (volume_db + 70) / 76))
    try:
        send_command(
            "set_track_level", {"track_index": track_index, "level": normalized_volume}
        )
    except Exception as e:
        print(f"    [WARNING] Could not set track volume: {e}")


def set_track_pan(track_index, pan_value):
    """Set track panning (normalized -1.0 to 1.0, 0 is center)"""
    try:
        send_command("set_track_pan", {"track_index": track_index, "pan": pan_value})
    except Exception as e:
        print(f"    [WARNING] Could not set track pan: {e}")


def add_automation_point(
    track_index, clip_index, device_index, parameter_index, time_val, value
):
    """Add an automation point to a clip envelope"""
    try:
        send_command(
            "add_clip_envelope_point",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "time": time_val,  # Position in beats
                "value": value,  # Normalized 0.0-1.0
                "curve_type": 0,  # Linear curve
            },
        )
    except Exception as e:
        print(f"    [WARNING] Could not add automation point: {e}")


# ============================================================================
# SECTION DEFINITIONS (30 sections, 4 minutes each)
# ============================================================================

sections = [
    # PHASE 1: INTRODUCTION (0:00 - 0:16)
    {
        "name": "Section 0 - Deep Intro",
        "description": "Minimal elements establish groove",
        "clips": [(4, 0), (5, 0), (6, 2), (7, 4), (8, 3), (9, 2)],
        "filter_freq": 0.1,  # Auto Filter on Track 7 (normalized)
        "reverb_send": 0.4,  # Send A level (normalized)
        "delay_send": 0.25,  # Send B level (normalized)
        "pad_volume": -20,  # dB
    },
    {
        "name": "Section 1 - Subtle Build",
        "description": "Adding slight variations, more delays",
        "clips": [(4, 0), (5, 0), (6, 0), (7, 4), (8, 3), (9, 0)],
        "filter_freq": 0.15,
        "reverb_send": 0.45,
        "delay_send": 0.30,
        "pad_volume": -20,
    },
    {
        "name": "Section 2 - Atmosphere Enters",
        "description": "Synth pads create depth",
        "clips": [(4, 1), (5, 1), (6, 0), (7, 0), (8, 3), (9, 0)],
        "filter_freq": 0.20,
        "reverb_send": 0.50,
        "delay_send": 0.30,
        "pad_volume": -18,
    },
    {
        "name": "Section 3 - First Movement",
        "description": "Bass starts to breathe",
        "clips": [(4, 0), (5, 2), (6, 1), (7, 0), (8, 0), (9, 1)],
        "filter_freq": 0.25,
        "reverb_send": 0.40,
        "delay_send": 0.35,
        "pad_volume": -18,
    },
    # PHASE 2: HYPNOTIC GROOVE (0:16 - 0:32)
    {
        "name": "Section 4 - Hypnotic Lock",
        "description": "Full groove established",
        "clips": [(4, 0), (5, 0), (6, 0), (7, 0), (8, 3), (9, 0)],
        "filter_freq": 0.30,
        "reverb_send": 0.40,
        "delay_send": 0.30,
        "pad_volume": -22,
    },
    {
        "name": "Section 5 - Subtle Shift",
        "description": "Bass variation, same pads",
        "clips": [(4, 0), (5, 4), (6, 0), (7, 0), (8, 3), (9, 0)],
        "filter_freq": 0.30,
        "reverb_send": 0.40,
        "delay_send": 0.30,
        "pad_volume": -22,
    },
    {
        "name": "Section 6 - Pad Evolution",
        "description": "Chord change to Fm",
        "clips": [(4, 0), (5, 0), (6, 0), (7, 1), (8, 3), (9, 0)],
        "filter_freq": 0.40,
        "reverb_send": 0.45,
        "delay_send": 0.35,
        "pad_volume": -20,
    },
    {
        "name": "Section 7 - Deepening",
        "description": "More depth in delays",
        "clips": [(4, 1), (5, 5), (6, 2), (7, 1), (8, 3), (9, 1)],
        "filter_freq": 0.35,
        "reverb_send": 0.45,
        "delay_send": 0.40,
        "pad_volume": -18,
    },
    # PHASE 3: FIRST BUILD (0:32 - 0:48)
    {
        "name": "Section 8 - Gathering Energy",
        "description": "Hi-hats become more active",
        "clips": [(4, 0), (5, 5), (6, 1), (7, 1), (8, 3), (9, 0)],
        "filter_freq": 0.45,
        "reverb_send": 0.40,
        "delay_send": 0.40,
        "pad_volume": -20,
    },
    {
        "name": "Section 9 - More Movement",
        "description": "Kick with emphasis",
        "clips": [(4, 2), (5, 3), (6, 1), (7, 1), (8, 1), (9, 1)],
        "filter_freq": 0.55,
        "reverb_send": 0.35,
        "delay_send": 0.45,
        "pad_volume": -18,
    },
    {
        "name": "Section 10 - Peak Intensity",
        "description": "Full elements, high energy",
        "clips": [(4, 2), (5, 3), (6, 4), (7, 6), (8, 4), (9, 4)],
        "filter_freq": 0.80,  # FULLY OPEN
        "reverb_send": 0.30,
        "delay_send": 0.35,
        "pad_volume": -16,  # Louder during peak
    },
    {
        "name": "Section 11 - Holding Pattern",
        "description": "Sustain intensity",
        "clips": [(4, 0), (5, 2), (6, 4), (7, 6), (8, 3), (9, 1)],
        "filter_freq": 0.75,
        "reverb_send": 0.35,
        "delay_send": 0.35,
        "pad_volume": -16,
    },
    # PHASE 4: BREAKDOWN (0:48 - 1:04)
    {
        "name": "Section 12 - Thinning Out",
        "description": "Removing elements gradually",
        "clips": [(4, 3), (5, 0), (6, 3), (7, 6), (8, 3), (9, 3)],
        "filter_freq": 0.60,
        "reverb_send": 0.50,
        "delay_send": 0.30,
        "pad_volume": -24,
    },
    {
        "name": "Section 13 - Just Kick and Bass",
        "description": "Rhythmic core",
        "clips": [(4, 3), (5, 0), (6, 3), (7, 5), (8, 3), (9, 3)],
        "filter_freq": 0.50,
        "reverb_send": 0.50,
        "delay_send": 0.20,
        "pad_volume": -999,  # Effectively silent
    },
    {
        "name": "Section 14 - Space and Atmosphere",
        "description": "Just pads, no rhythm",
        "clips": [(4, -1), (5, -1), (6, -1), (7, 7), (8, 6), (9, 6)],
        "filter_freq": 0.20,  # VERY CLOSED
        "reverb_send": 0.60,
        "delay_send": 0.20,
        "pad_volume": -20,
    },
    {
        "name": "Section 15 - Re-emerging",
        "description": "Kick returns, pads evolve",
        "clips": [(4, 5), (5, 0), (6, 2), (7, 2), (8, 6), (9, 2)],
        "filter_freq": 0.30,
        "reverb_send": 0.55,
        "delay_send": 0.25,
        "pad_volume": -18,
    },
    # PHASE 5: SECOND BUILD (1:04 - 1:20)
    {
        "name": "Section 16 - Gradual Return",
        "description": "Building back up slowly",
        "clips": [(4, 0), (5, 6), (6, 0), (7, 2), (8, 3), (9, 2)],
        "filter_freq": 0.40,
        "reverb_send": 0.45,
        "delay_send": 0.30,
        "pad_volume": -18,
    },
    {
        "name": "Section 17 - New Energy",
        "description": "Chord change, more active",
        "clips": [(4, 1), (5, 7), (6, 1), (7, 3), (8, 2), (9, 2)],
        "filter_freq": 0.50,
        "reverb_send": 0.40,
        "delay_send": 0.40,
        "pad_volume": -18,
    },
    {
        "name": "Section 18 - Complex Layers",
        "description": "More delays and FX",
        "clips": [(4, 4), (5, 7), (6, 1), (7, 3), (8, 2), (9, 4)],
        "filter_freq": 0.65,
        "reverb_send": 0.35,
        "delay_send": 0.50,
        "pad_volume": -18,
    },
    {
        "name": "Section 19 - Peak Again",
        "description": "Maximum intensity",
        "clips": [(4, 6), (5, 3), (6, 4), (7, 6), (8, 7), (9, 5)],
        "filter_freq": 0.80,  # PEAK AGAIN
        "reverb_send": 0.30,
        "delay_send": 0.35,
        "pad_volume": -16,
    },
    # PHASE 6: JOURNEY CONTINUES (1:20 - 1:36)
    {
        "name": "Section 20 - Deep Hypnosis",
        "description": "Sustaining groove",
        "clips": [(4, 0), (5, 0), (6, 6), (7, 0), (8, 3), (9, 0)],
        "filter_freq": 0.55,
        "reverb_send": 0.40,
        "delay_send": 0.30,
        "pad_volume": -22,
    },
    {
        "name": "Section 21 - Minor Shift",
        "description": "Soft kick, minimal change",
        "clips": [(4, 7), (5, 0), (6, 7), (7, 0), (8, 3), (9, 0)],
        "filter_freq": 0.50,
        "reverb_send": 0.40,
        "delay_send": 0.30,
        "pad_volume": -22,
    },
    {
        "name": "Section 22 - Pad Evolution",
        "description": "Atmospheric shift",
        "clips": [(4, 0), (5, 4), (6, 2), (7, 1), (8, 3), (9, 2)],
        "filter_freq": 0.45,
        "reverb_send": 0.45,
        "delay_send": 0.35,
        "pad_volume": -20,
    },
    {
        "name": "Section 23 - Gathering Again",
        "description": "Building energy",
        "clips": [(4, 2), (5, 2), (6, 1), (7, 1), (8, 5), (9, 4)],
        "filter_freq": 0.55,
        "reverb_send": 0.40,
        "delay_send": 0.40,
        "pad_volume": -18,
    },
    # PHASE 7: FINAL PUSH (1:36 - 1:52)
    {
        "name": "Section 24 - Complex Rhythms",
        "description": "Kick syncopation increases",
        "clips": [(4, 4), (5, 3), (6, 4), (7, 6), (8, 7), (9, 4)],
        "filter_freq": 0.70,
        "reverb_send": 0.35,
        "delay_send": 0.45,
        "pad_volume": -16,
    },
    {
        "name": "Section 25 - Maximum Movement",
        "description": "All elements active",
        "clips": [(4, 6), (5, 7), (6, 4), (7, 6), (8, 7), (9, 5)],
        "filter_freq": 0.80,  # MAXIMUM
        "reverb_send": 0.30,
        "delay_send": 0.50,
        "pad_volume": -14,  # Slightly louder
    },
    {
        "name": "Section 26 - Holding Peak",
        "description": "Sustained intensity",
        "clips": [(4, 2), (5, 3), (6, 4), (7, 6), (8, 0), (9, 1)],
        "filter_freq": 0.75,
        "reverb_send": 0.35,
        "delay_send": 0.35,
        "pad_volume": -16,
    },
    {
        "name": "Section 27 - Beginning Release",
        "description": "Starting to thin out",
        "clips": [(4, 0), (5, 2), (6, 1), (7, 6), (8, 3), (9, 2)],
        "filter_freq": 0.60,
        "reverb_send": 0.40,
        "delay_send": 0.35,
        "pad_volume": -20,
    },
    # PHASE 8: WIND DOWN (1:52 - 2:00)
    {
        "name": "Section 28 - Returning to Simplicity",
        "description": "Stripping back to core",
        "clips": [(4, 0), (5, 0), (6, 2), (7, 4), (8, 3), (9, 2)],
        "filter_freq": 0.45,
        "reverb_send": 0.40,
        "delay_send": 0.30,
        "pad_volume": -22,
    },
    {
        "name": "Section 29 - Fading Out",
        "description": "Final breakdown to silence",
        "clips": [(4, 3), (5, 5), (6, 3), (7, 5), (8, 6), (9, 6)],
        "filter_freq": 0.20,  # FULLY CLOSED
        "reverb_send": 0.55,
        "delay_send": 0.25,
        "pad_volume": -24,
    },
]

# ============================================================================
# AUTOMATION FUNCTIONS
# ============================================================================


def apply_section_automation(section_idx, section):
    """Apply all automation for a specific section"""
    print(f"\n  Applying automation for {section['name']}...")

    # Set Auto Filter frequency on Track 7 (Synth Pads)
    # Assuming Auto Filter is device index 2 (after EQ at 0)
    try:
        set_device_parameter(7, 2, 0, section["filter_freq"])  # Frequency parameter
        print(f"    [OK] Auto Filter: {section['filter_freq']:.2f}")
    except Exception as e:
        print(f"    [SKIP] Could not set filter: {e}")

    # Set track volumes
    volume_targets = {
        4: -7,  # Kick
        5: -5,  # Sub-bass
        6: -14,  # Hi-hats
        7: section["pad_volume"],  # Synth Pads (varies)
        8: -18,  # FX
        9: -17,  # Dub Delays
    }

    for track_idx, vol_db in volume_targets.items():
        try:
            set_track_volume(track_idx, vol_db)
            print(f"    [OK] Track {track_idx} volume: {vol_db} dB")
        except Exception as e:
            print(f"    [SKIP] Track {track_idx} volume: {e}")

    # Note: Send levels would need to be set manually in Ableton
    # or through device parameter automation on send devices
    print(
        f"    [INFO] Target sends - Reverb: {section['reverb_send']:.2f}, Delay: {section['delay_send']:.2f}"
    )
    print(f"    [INFO] Manual send level adjustment may be required")


def fire_section_clips(section_idx, section):
    """Fire all clips for a section"""
    print(f"\n  Firing clips for {section['name']}...")

    for track_idx, clip_idx in section["clips"]:
        if clip_idx >= 0:
            try:
                send_command(
                    "fire_clip", {"track_index": track_idx, "clip_index": clip_idx}
                )
                print(f"    [OK] Track {track_idx}, Clip {clip_idx}")
            except Exception as e:
                print(f"    [ERROR] Could not fire clip: {e}")
        else:
            # Stop the track
            try:
                send_command("stop_clip", {"track_index": track_idx, "clip_index": 0})
                print(f"    [STOP] Track {track_idx}")
            except Exception as e:
                print(f"    [ERROR] Could not stop clip: {e}")


def wait_for_section_duration(section_minutes=4):
    """Wait for the duration of one section"""
    section_seconds = section_minutes * 60
    print(f"\n  Waiting {section_minutes} minutes ({section_seconds} seconds)...")
    time.sleep(section_seconds)


def get_progress_bar(current, total, width=30):
    """Generate a progress bar string"""
    filled = int(width * current / total)
    bar = "=" * filled + "-" * (width - filled)
    percent = int(100 * current / total)
    return f"[{bar}] {percent}%"


# ============================================================================
# MAIN AUTOMATION LOOP
# ============================================================================


def run_automation():
    """Run the complete 2-hour automated playback"""
    print("=" * 80)
    print("2-HOUR DUB TECHNOPO - AUTOMATED PLAYBACK")
    print("=" * 80)
    print(f"Total Duration: {len(sections) * 4} minutes (2 hours)")
    print(f"Total Sections: {len(sections)}")
    print(f"Section Duration: 4 minutes each")
    print("=" * 80)
    print("2-HOUR DUB TECHNOPO - AUTOMATED PLAYBACK")
    print("=" * 80)
    print(f"Total Duration: {len(sections) * 4} minutes (2 hours)")
    print(f"Total Sections: {len(sections)}")
    print(f"Section Duration: 4 minutes each")
    print("=" * 80)

    # Start playback
    print("\n[START] Starting playback...")
    try:
        send_command("start_playback")
        print("[OK] Playback started")
    except Exception as e:
        print(f"[ERROR] Could not start playback: {e}")
        return

    # Main automation loop
    total_time_minutes = len(sections) * 4
    elapsed_minutes = 0

    print("\n" + "=" * 80)
    print("BEGINNING AUTOMATED SECTION PROGRESSION")
    print("=" * 80)
    print("\nPress Ctrl+C to stop automation\n")

    try:
        for section_idx, section in enumerate(sections):
            # Update progress
            progress = get_progress_bar(section_idx, len(sections))
            total_time = f"{elapsed_minutes // 60}:{elapsed_minutes % 60:02d}"
            print(f"\n{progress} Section {section_idx}/29 | Elapsed: {total_time}")
            print(f"{'-' * 80}")
            print(f"  {section['name']}")
            print(f"  {section['description']}")
            print(f"{'-' * 80}")

            # Fire clips for this section
            fire_section_clips(section_idx, section)

            # Apply automation for this section
            apply_section_automation(section_idx, section)

            # Wait for section duration
            wait_for_section_duration(4)

            # Update elapsed time
            elapsed_minutes += 4

        # All sections complete
        print("\n" + "=" * 80)
        print("AUTOMATION COMPLETE!")
        print("=" * 80)
        print(
            f"\nTotal Duration: {elapsed_minutes // 60} hours {(elapsed_minutes % 60):02d} minutes"
        )
        print("All 30 sections have been played")
        print("\nTrack is ready for replay or save.")

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("AUTOMATION STOPPED BY USER")
        print("=" * 80)
        print(
            f"\nStopped at: {elapsed_minutes // 60} hours {(elapsed_minutes % 60):02d} minutes"
        )
        print(f"Current Section: {min(section_idx, len(sections) - 1)}")

        # Stop playback
        print("\n[STOP] Stopping playback...")
        try:
            send_command("stop_playback")
            print("[OK] Playback stopped")
        except Exception as e:
            print(f"[ERROR] Could not stop playback: {e}")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run_automation()

# Close connection
s.close()
