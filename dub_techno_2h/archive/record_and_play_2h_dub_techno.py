import socket
import json
import time

# ============================================================================
# 2-HOUR DUB TECHNOPO - PLAYBACK AUTOMATION
# ============================================================================
# This script automates playback of the 2-hour dub techno track
# Sections: 30 sections x 4 minutes = 120 minutes (2 hours)
# ============================================================================

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return full response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


def fire_clip(track_index, clip_index):
    """Fire a specific clip"""
    send_command(
        {
            "type": "fire_clip",
            "params": {"track_index": track_index, "clip_index": clip_index},
        }
    )


def stop_clip(track_index, clip_index=0):
    """Stop a specific clip"""
    send_command(
        {
            "type": "stop_clip",
            "params": {"track_index": track_index, "clip_index": clip_index},
        }
    )


def start_playback():
    """Start playback"""
    send_command({"type": "start_playback", "params": {}})


def stop_playback():
    """Stop playback"""
    send_command({"type": "stop_playback", "params": {}})


# ============================================================================
# SECTION DEFINITIONS
# ============================================================================

sections = [
    # PHASE 1: INTRODUCTION (0:00 - 0:16) - Sections 0-3
    {
        "name": "Section 0 - Deep Intro",
        "description": "Minimal elements establish the groove",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 0),  # Bass: Root Drone
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 1 - Subtle Build",
        "description": "Adding slight variations, more delays",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 0),  # Bass: Root Drone
            (2, 0),  # Hi-hat: Offbeats
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 2 - Atmosphere Enters",
        "description": "Synth pads create depth",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 1),  # Bass: Octave Drop
            (2, 0),  # Hi-hat: Offbeats
            (3, 0),  # Pad: Cm
            (4, 3),  # FX: Silent
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 3 - First Build",
        "description": "Energy starts to rise",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 2),  # Bass: Syncopated
            (2, 0),  # Hi-hat: Offbeats
            (3, 0),  # Pad: Cm
            (4, 1),  # FX: Impact
            (5, 0),  # Delay: Regular
        ],
    },
    # PHASE 2: HYPNOTIC GROOVE (0:16 - 0:32) - Sections 4-7
    {
        "name": "Section 4 - Hypnotic State",
        "description": "Full groove engaged",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 2),  # Bass: Syncopated
            (2, 1),  # Hi-hat: Active
            (3, 0),  # Pad: Cm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 5 - Slight Shift",
        "description": "Subtle evolution continues",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 1),  # Pad: Fm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 6 - Building Up",
        "description": "More energy in the hi-hats",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 2),  # Pad: Gm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 7 - First Peak",
        "description": "Elements come together",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 4),  # Bass: Staccato
            (2, 4),  # Hi-hat: 16ths
            (3, 2),  # Pad: Gm
            (4, 2),  # FX: Reverse
            (5, 2),  # Delay: Minimal
        ],
    },
    # PHASE 3: BUILDUP PHASE (0:32 - 0:48) - Sections 8-11
    {
        "name": "Section 8 - Buildup Begins",
        "description": "Starting the first major buildup",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 4),  # Bass: Staccato
            (2, 5),  # Hi-hat: Open
            (3, 2),  # Pad: Gm
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 9 - Rising Higher",
        "description": "Intensity increases",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 5),  # Bass: F Drone
            (2, 4),  # Hi-hat: 16ths
            (3, 3),  # Pad: Eb
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 10 - Approaching Peak",
        "description": "Almost at the first peak",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 5),  # Bass: F Drone
            (2, 4),  # Hi-hat: 16ths
            (3, 3),  # Pad: Eb
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 11 - Peak 1",
        "description": "First major peak reached",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 6),  # Bass: G Drone
            (2, 7),  # Hi-hat: 2 and 4
            (3, 0),  # Pad: Cm
            (4, 7),  # FX: Riser
            (5, 6),  # Delay: Tail
        ],
    },
    # PHASE 4: BREAKDOWN (0:48 - 1:04) - Sections 12-15
    {
        "name": "Section 12 - Start Breakdown",
        "description": "Removing elements for space",
        "clips": [
            (0, 3),  # Kick: Half
            (1, 4),  # Bass: Staccato
            (2, 3),  # Hi-hat: Silent
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 13 - Minimal State",
        "description": "Very stripped back",
        "clips": [
            (0, 5),  # Kick: Sparse
            (1, 0),  # Bass: Root Drone
            (2, 3),  # Hi-hat: Silent
            (3, 4),  # Pad: Minimal
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 14 - Atmospheric",
        "description": "Focus on pads and atmosphere",
        "clips": [
            (0, 5),  # Kick: Sparse
            (1, 0),  # Bass: Root Drone
            (2, 3),  # Hi-hat: Silent
            (3, 5),  # Pad: Silent
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 15 - Deep Space",
        "description": "Maximum atmosphere, minimal elements",
        "clips": [
            (0, 7),  # Kick: Soft
            (1, 0),  # Bass: Root Drone
            (2, 3),  # Hi-hat: Silent
            (3, 7),  # Pad: High Drone
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
    # PHASE 5: SECOND BUILD (1:04 - 1:20) - Sections 16-19
    {
        "name": "Section 16 - Elements Return",
        "description": "Elements slowly return",
        "clips": [
            (0, 3),  # Kick: Half
            (1, 2),  # Bass: Syncopated
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 17 - Building Again",
        "description": "Second buildup begins",
        "clips": [
            (0, 4),  # Kick: Syncopated
            (1, 3),  # Bass: Rising
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 5),  # FX: Noise Build
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 18 - Gathering Momentum",
        "description": "Energy building up again",
        "clips": [
            (0, 4),  # Kick: Syncopated
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 4),  # Pad: Minimal
            (4, 5),  # FX: Noise Build
            (5, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 19 - Peak 2 Approaching",
        "description": "Reaching second peak",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 3),  # Bass: Rising
            (2, 1),  # Hi-hat: Active
            (3, 4),  # Pad: Minimal
            (4, 7),  # FX: Riser
            (5, 4),  # Delay: Echo Build
        ],
    },
    # PHASE 6: JOURNEY (1:20 - 1:36) - Sections 20-23
    {
        "name": "Section 20 - Peak 2",
        "description": "Second major peak",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 2),  # Bass: Syncopated
            (2, 1),  # Hi-hat: Active
            (3, 1),  # Pad: Fm
            (4, 3),  # FX: Silent
            (5, 6),  # Delay: Tail
        ],
    },
    {
        "name": "Section 21 - Sustained Energy",
        "description": "Maintaining the peak energy",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 2),  # Bass: Syncopated
            (2, 1),  # Hi-hat: Active
            (3, 1),  # Pad: Fm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 22 - Subtle Evolution",
        "description": "Gentle variations in the groove",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 3),  # Bass: Rising
            (2, 0),  # Hi-hat: Offbeats
            (3, 2),  # Pad: Gm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 23 - Continuing Journey",
        "description": "Deep hypnotic state continues",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 6),  # Bass: G Drone
            (2, 6),  # Hi-hat: Swung
            (3, 2),  # Pad: Gm
            (4, 3),  # FX: Silent
            (5, 1),  # Delay: Active
        ],
    },
    # PHASE 7: FINAL PUSH (1:36 - 1:52) - Sections 24-27
    {
        "name": "Section 24 - Final Buildup",
        "description": "Building to final peak",
        "clips": [
            (0, 6),  # Kick: Buildup
            (1, 4),  # Bass: Staccato
            (2, 4),  # Hi-hat: 16ths
            (3, 0),  # Pad: Cm
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 25 - Maximum Energy",
        "description": "Highest energy state",
        "clips": [
            (0, 2),  # Kick: Emphasized
            (1, 5),  # Bass: F Drone
            (2, 4),  # Hi-hat: 16ths
            (3, 3),  # Pad: Eb
            (4, 5),  # FX: Noise Build
            (5, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 26 - Peak 3",
        "description": "Third and final peak",
        "clips": [
            (0, 0),  # Kick: Basic
            (1, 7),  # Bass: Alternating
            (2, 7),  # Hi-hat: 2 and 4
            (3, 6),  # Pad: Cm7
            (4, 7),  # FX: Riser
            (5, 5),  # Delay: Stutter
        ],
    },
    {
        "name": "Section 27 - Holding Peak",
        "description": "Sustaining maximum energy",
        "clips": [
            (0, 1),  # Kick: Swing
            (1, 3),  # Bass: Rising
            (2, 7),  # Hi-hat: 2 and 4
            (3, 6),  # Pad: Cm7
            (4, 1),  # FX: Impact
            (5, 5),  # Delay: Stutter
        ],
    },
    # PHASE 8: WIND DOWN (1:52 - 2:00) - Sections 28-29
    {
        "name": "Section 28 - Starting to Fade",
        "description": "Beginning to strip elements back",
        "clips": [
            (0, 5),  # Kick: Sparse
            (1, 4),  # Bass: Staccato
            (2, 2),  # Hi-hat: Minimal
            (3, 4),  # Pad: Minimal
            (4, 3),  # FX: Silent
            (5, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 29 - Final Fade Out",
        "description": "Gently fading to silence",
        "clips": [
            (0, 7),  # Kick: Soft
            (1, 4),  # Bass: Staccato
            (2, 3),  # Hi-hat: Silent
            (3, 5),  # Pad: Silent
            (4, 6),  # FX: Reverb Tail
            (5, 2),  # Delay: Minimal
        ],
    },
]


# ============================================================================
# MAIN AUTOMATION LOOP
# ============================================================================

print("=" * 80)
print("2-HOUR DUB TECHNOPO - AUTOMATED PLAYBACK")
print("=" * 80)
print(f"Total Duration: 2 hours (120 minutes)")
print(f"Sections: {len(sections)} sections x 4 minutes each")
print(f"Tempo: 126 BPM")
print(f"Beat Duration: 4 minutes = {4 * 126 / 60:.1} bars")
print("=" * 80)
print()
print("INSTRUCTIONS FOR RECORDING:")
print("=" * 80)
print("To record to dubking.mp3:")
print()
print("1. In Ableton Live, enable recording on the Master track:")
print("   - Click the 'Record' button on the Master track")
print("   - Or press Shift+R to enable master recording")
print()
print("2. Set the recording location:")
print("   - File > Export Audio/Video")
print("   - Select sample rate (44100 or 48000 Hz)")
print("   - Select bit depth (16-bit or 24-bit)")
print("   - Choose 'Master' as the source")
print("   - Set format to WAV (for best quality, convert to MP3 later)")
print("   - Set duration to 'Loop' or specify 2 hours")
print()
print("3. Press Record in Ableton (or press R)")
print()
print("4. Run this script (press Enter below) to start automation")
print()
print("5. The automation will run for 2 hours")
print("   - Sections change every 4 minutes")
print("   - Progress will be shown in the console")
print()
print("6. Press Ctrl+C to stop early (and stop recording in Ableton)")
print("=" * 80)
print()

# Ask user to start
input(
    "Press Enter to start the 2-hour playback automation... (Make sure recording is enabled in Ableton!)"
)

print("\n" + "=" * 80)
print("STARTING 2-HOUR PLAYBACK AUTOMATION")
print("=" * 80)
print()

try:
    # Fire initial clips for Section 0
    print(f"\n[00:00] Section 0 - Deep Intro")
    section = sections[0]
    for track_index, clip_index in section["clips"]:
        fire_clip(track_index, clip_index)

    # Start playback
    start_playback()
    print("  ✓ Playback started")
    time.sleep(1)

    # Progress through all sections
    for section_idx in range(1, len(sections)):
        section = sections[section_idx]
        elapsed_minutes = section_idx * 4
        hours = elapsed_minutes // 60
        minutes = elapsed_minutes % 60

        # Calculate progress bar
        progress = section_idx / len(sections)
        bar_length = 40
        filled = int(bar_length * progress)
        progress_bar = "[" + "=" * filled + "-" * (bar_length - filled) + "]"

        print(f"\n{progress_bar} {progress * 100:.1f}%")
        print(f"[{hours:02d}:{minutes:02d}] Section {section_idx} - {section['name']}")
        print(f"  Description: {section['description']}")

        # Fire clips for this section
        for track_index, clip_index in section["clips"]:
            fire_clip(track_index, clip_index)

        print(f"  ✓ Clips fired")

        # Wait 4 minutes for this section (4 minutes = 240 seconds)
        for remaining in range(240, 0, -60):
            minutes_left = remaining // 60
            if minutes_left > 0:
                time.sleep(60)
                if remaining % 60 == 0:
                    pass  # Already showed section start
            else:
                time.sleep(remaining)
                break

    # Final section complete
    final_progress = 1.0
    progress_bar = "[" + "=" * 40 + "]"
    print(f"\n{progress_bar} {final_progress * 100:.1f}%")
    print("\n" + "=" * 80)
    print("2-HOUR PLAYBACK COMPLETE!")
    print("=" * 80)
    print()
    print("All 30 sections have been played.")
    print("Total duration: 2 hours (120 minutes)")
    print()
    print("Your recording in Ableton should now contain the full 2-hour track.")
    print("Remember to:")
    print("  1. Stop recording in Ableton")
    print("  2. Export the recorded audio")
    print("  3. Convert to MP3 (dubking.mp3) if needed")
    print()

except KeyboardInterrupt:
    print("\n\n" + "=" * 80)
    print("AUTOMATION STOPPED BY USER")
    print("=" * 80)
    print()
    print("Please stop recording in Ableton.")
    print("To resume, run the script again.")
    print()

finally:
    # Stop playback
    try:
        stop_playback()
        print("Playback stopped.")
    except Exception as e:
        print(f"Error stopping playback: {e}")

    s.close()

print("\n" + "=" * 80)
print("Thank you for using AbletonMCP!")
print("=" * 80)
