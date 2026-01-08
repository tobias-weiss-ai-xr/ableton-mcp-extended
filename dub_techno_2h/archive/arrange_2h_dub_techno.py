import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))


def fire_clip(track_index, clip_index):
    """Fire a specific clip"""
    s.send(
        json.dumps(
            {
                "type": "fire_clip",
                "params": {"track_index": track_index, "clip_index": clip_index},
            }
        ).encode("utf-8")
    )
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


def stop_clip(track_index, clip_index=0):
    """Stop a specific clip"""
    s.send(
        json.dumps(
            {
                "type": "stop_clip",
                "params": {"track_index": track_index, "clip_index": clip_index},
            }
        ).encode("utf-8")
    )
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


def start_playback():
    """Start playback"""
    s.send(json.dumps({"type": "start_playback", "params": {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


def stop_playback():
    """Stop playback"""
    s.send(json.dumps({"type": "stop_playback", "params": {}}).encode("utf-8"))
    response = json.loads(s.recv(8192).decode("utf-8"))
    return response


# ============================================================================
# 2-HOUR DUB TECHNOPO ARRANGEMENT
# ============================================================================
# 30 sections x 4 minutes = 120 minutes (2 hours)
# 126 BPM, hypnotic and evolving
# ============================================================================

print("=" * 80)
print("2-HOUR DUB TECHNOPO ARRANGEMENT")
print("=" * 80)
print(f"Total Duration: 2 hours (120 minutes)")
print(f"Sections: 30 sections x 4 minutes each")
print(f"Tempo: 126 BPM")
print("=" * 80)

# Section definitions
sections = [
    # PHASE 1: INTRODUCTION (0:00 - 0:16) - Sections 0-3
    {
        "name": "Section 0 - Deep Intro",
        "description": "Minimal elements establish the groove",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 0),  # Bass: Root Drone
            (6, 2),  # Hi-hat: Minimal
            (7, 4),  # Pad: Minimal
            (8, 3),  # FX: Silent
            (9, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 1 - Subtle Build",
        "description": "Adding slight variations, more delays",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 0),  # Bass: Root Drone
            (6, 0),  # Hi-hat: Offbeats
            (7, 4),  # Pad: Minimal
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 2 - Atmosphere Enters",
        "description": "Synth pads create depth",
        "duration": "4:00",
        "clips": [
            (4, 1),  # Kick: Swing
            (5, 1),  # Bass: Octave Drop
            (6, 0),  # Hi-hat: Offbeats
            (7, 0),  # Pad: Cm
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 3 - First Movement",
        "description": "Bass starts to breathe",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 2),  # Bass: Syncopated
            (6, 1),  # Hi-hat: Active
            (7, 0),  # Pad: Cm
            (8, 0),  # FX: Sweep
            (9, 1),  # Delay: Active
        ],
    },
    # PHASE 2: HYPNOTIC GROOVE (0:16 - 0:32) - Sections 4-7
    {
        "name": "Section 4 - Hypnotic Lock",
        "description": "Full groove established, minimal evolution",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 0),  # Bass: Root Drone
            (6, 0),  # Hi-hat: Offbeats
            (7, 0),  # Pad: Cm
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 5 - Subtle Shift",
        "description": "Bass variation, same pads",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 4),  # Bass: Staccato
            (6, 0),  # Hi-hat: Offbeats
            (7, 0),  # Pad: Cm
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 6 - Pad Evolution",
        "description": "Chord change to Fm",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 0),  # Bass: Root Drone
            (6, 0),  # Hi-hat: Offbeats
            (7, 1),  # Pad: Fm
            (8, 0),  # FX: Sweep
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 7 - Deepening",
        "description": "More depth in delays",
        "duration": "4:00",
        "clips": [
            (4, 1),  # Kick: Swing
            (5, 5),  # Bass: F Drone
            (6, 2),  # Hi-hat: Minimal
            (7, 1),  # Pad: Fm
            (8, 3),  # FX: Silent
            (9, 1),  # Delay: Active
        ],
    },
    # PHASE 3: FIRST BUILD (0:32 - 0:48) - Sections 8-11
    {
        "name": "Section 8 - Gathering Energy",
        "description": "Hi-hats become more active",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 5),  # Bass: F Drone
            (6, 1),  # Hi-hat: Active
            (7, 1),  # Pad: Fm
            (8, 0),  # FX: Sweep
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 9 - More Movement",
        "description": "Kick with emphasis",
        "duration": "4:00",
        "clips": [
            (4, 2),  # Kick: Emphasized
            (5, 3),  # Bass: Rising
            (6, 1),  # Hi-hat: Active
            (7, 1),  # Pad: Fm
            (8, 1),  # FX: Impact
            (9, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 10 - Peak Intensity",
        "description": "Full elements, high energy",
        "duration": "4:00",
        "clips": [
            (4, 2),  # Kick: Emphasized
            (5, 3),  # Bass: Rising
            (6, 4),  # Hi-hat: 16ths
            (7, 6),  # Pad: Cm7
            (8, 4),  # FX: Sub Drop
            (9, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 11 - Holding Pattern",
        "description": "Sustain intensity",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 2),  # Bass: Syncopated
            (6, 4),  # Hi-hat: 16ths
            (7, 6),  # Pad: Cm7
            (8, 0),  # FX: Sweep
            (9, 1),  # Delay: Active
        ],
    },
    # PHASE 4: BREAKDOWN (0:48 - 1:04) - Sections 12-15
    {
        "name": "Section 12 - Thinning Out",
        "description": "Removing elements gradually",
        "duration": "4:00",
        "clips": [
            (4, 3),  # Kick: Half
            (5, 0),  # Bass: Root Drone
            (6, 3),  # Hi-hat: Silent
            (7, 6),  # Pad: Cm7
            (8, 3),  # FX: Silent
            (9, 3),  # Delay: Silent
        ],
    },
    {
        "name": "Section 13 - Just Kick and Bass",
        "description": "Rhythmic core",
        "duration": "4:00",
        "clips": [
            (4, 3),  # Kick: Half
            (5, 0),  # Bass: Root Drone
            (6, 3),  # Hi-hat: Silent
            (7, 5),  # Pad: Silent
            (8, 3),  # FX: Silent
            (9, 3),  # Delay: Silent
        ],
    },
    {
        "name": "Section 14 - Space and Atmosphere",
        "description": "Just pads, no rhythm",
        "duration": "4:00",
        "clips": [
            (4, -1),  # Kick: Stop
            (5, -1),  # Bass: Stop
            (6, -1),  # Hi-hat: Stop
            (7, 7),  # Pad: High Drone
            (8, 6),  # FX: Reverb Tail
            (9, 6),  # Delay: Tail
        ],
    },
    {
        "name": "Section 15 - Re-emerging",
        "description": "Kick returns, pads evolve",
        "duration": "4:00",
        "clips": [
            (4, 5),  # Kick: Sparse
            (5, 0),  # Bass: Root Drone
            (6, 2),  # Hi-hat: Minimal
            (7, 2),  # Pad: Gm
            (8, 6),  # FX: Reverb Tail
            (9, 2),  # Delay: Minimal
        ],
    },
    # PHASE 5: SECOND BUILD (1:04 - 1:20) - Sections 16-19
    {
        "name": "Section 16 - Gradual Return",
        "description": "Building back up slowly",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 6),  # Bass: G Drone
            (6, 0),  # Hi-hat: Offbeats
            (7, 2),  # Pad: Gm
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 17 - New Energy",
        "description": "Chord change, more active",
        "duration": "4:00",
        "clips": [
            (4, 1),  # Kick: Swing
            (5, 7),  # Bass: Alternating
            (6, 1),  # Hi-hat: Active
            (7, 3),  # Pad: Eb
            (8, 0),  # FX: Sweep
            (9, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 18 - Complex Layers",
        "description": "More delays and FX",
        "duration": "4:00",
        "clips": [
            (4, 4),  # Kick: Syncopated
            (5, 7),  # Bass: Alternating
            (6, 1),  # Hi-hat: Active
            (7, 3),  # Pad: Eb
            (8, 2),  # FX: Reverse
            (9, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 19 - Peak Again",
        "description": "Maximum intensity",
        "duration": "4:00",
        "clips": [
            (4, 6),  # Kick: Buildup
            (5, 3),  # Bass: Rising
            (6, 4),  # Hi-hat: 16ths
            (7, 6),  # Pad: Cm7
            (8, 7),  # FX: Riser
            (9, 5),  # Delay: Stutter
        ],
    },
    # PHASE 6: JOURNEY CONTINUES (1:20 - 1:36) - Sections 20-23
    {
        "name": "Section 20 - Deep Hypnosis",
        "description": "Sustaining groove with variations",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 0),  # Bass: Root Drone
            (6, 6),  # Hi-hat: Swung
            (7, 0),  # Pad: Cm
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 21 - Minor Shift",
        "description": "Soft kick, minimal change",
        "duration": "4:00",
        "clips": [
            (4, 7),  # Kick: Soft
            (5, 0),  # Bass: Root Drone
            (6, 7),  # Hi-hat: 2 and 4
            (7, 0),  # Pad: Cm
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 22 - Pad Evolution",
        "description": "Atmospheric shift",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 4),  # Bass: Staccato
            (6, 2),  # Hi-hat: Minimal
            (7, 1),  # Pad: Fm
            (8, 0),  # FX: Sweep
            (9, 0),  # Delay: Regular
        ],
    },
    {
        "name": "Section 23 - Gathering Again",
        "description": "Building energy once more",
        "duration": "4:00",
        "clips": [
            (4, 2),  # Kick: Emphasized
            (5, 2),  # Bass: Syncopated
            (6, 1),  # Hi-hat: Active
            (7, 1),  # Pad: Fm
            (8, 5),  # FX: Noise Build
            (9, 1),  # Delay: Active
        ],
    },
    # PHASE 7: FINAL PUSH (1:36 - 1:52) - Sections 24-27
    {
        "name": "Section 24 - Complex Rhythms",
        "description": "Kick syncopation increases",
        "duration": "4:00",
        "clips": [
            (4, 4),  # Kick: Syncopated
            (5, 3),  # Bass: Rising
            (6, 4),  # Hi-hat: 16ths
            (7, 6),  # Pad: Cm7
            (8, 0),  # FX: Sweep
            (9, 4),  # Delay: Echo Build
        ],
    },
    {
        "name": "Section 25 - Maximum Movement",
        "description": "All elements active",
        "duration": "4:00",
        "clips": [
            (4, 6),  # Kick: Buildup
            (5, 7),  # Bass: Alternating
            (6, 4),  # Hi-hat: 16ths
            (7, 6),  # Pad: Cm7
            (8, 1),  # FX: Impact
            (9, 5),  # Delay: Stutter
        ],
    },
    {
        "name": "Section 26 - Holding Peak",
        "description": "Sustained intensity",
        "duration": "4:00",
        "clips": [
            (4, 2),  # Kick: Emphasized
            (5, 3),  # Bass: Rising
            (6, 4),  # Hi-hat: 16ths
            (7, 6),  # Pad: Cm7
            (8, 0),  # FX: Sweep
            (9, 1),  # Delay: Active
        ],
    },
    {
        "name": "Section 27 - Beginning Release",
        "description": "Starting to thin out",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 2),  # Bass: Syncopated
            (6, 1),  # Hi-hat: Active
            (7, 6),  # Pad: Cm7
            (8, 3),  # FX: Silent
            (9, 0),  # Delay: Regular
        ],
    },
    # PHASE 8: WIND DOWN (1:52 - 2:00) - Sections 28-29
    {
        "name": "Section 28 - Returning to Simplicity",
        "description": "Stripping back to core elements",
        "duration": "4:00",
        "clips": [
            (4, 0),  # Kick: Basic
            (5, 0),  # Bass: Root Drone
            (6, 2),  # Hi-hat: Minimal
            (7, 4),  # Pad: Minimal
            (8, 3),  # FX: Silent
            (9, 2),  # Delay: Minimal
        ],
    },
    {
        "name": "Section 29 - Fading Out",
        "description": "Final breakdown to silence",
        "duration": "4:00",
        "clips": [
            (4, 3),  # Kick: Half
            (5, 5),  # Bass: F Drone (subtle)
            (6, 3),  # Hi-hat: Silent
            (7, 5),  # Pad: Silent
            (8, 6),  # FX: Reverb Tail
            (9, 6),  # Delay: Tail
        ],
    },
]

# ============================================================================
# FIRE CLIPS FOR EACH SECTION
# ============================================================================

total_time = 0
for section_idx, section in enumerate(sections):
    print(f"\n[{section_idx}] {section['name']}")
    print(f"    {section['description']}")
    print(f"    Duration: {section['duration']}")
    print(
        f"    Time: {total_time // 60}:{total_time % 60:02d} - {(total_time + 240) // 60}:{(total_time + 240) % 60:02d}"
    )

    # Fire all clips for this section
    for track_idx, clip_idx in section["clips"]:
        if clip_idx >= 0:
            fire_clip(track_idx, clip_idx)
        else:
            stop_clip(track_idx)

    total_time += 240  # 4 minutes in seconds

print("\n" + "=" * 80)
print("ARRANGEMENT COMPLETE!")
print("=" * 80)
print(f"Total Sections: {len(sections)}")
print(f"Total Duration: {total_time // 60} minutes ({total_time // 60} hours)")
print("\nStarting playback...")
print("=" * 80)

# Start playback
start_playback()

print("\n" + "=" * 80)
print("2-HOUR DUB TECHNOPO JOURNEY HAS BEGUN!")
print("=" * 80)
print("\nThe track will evolve through 30 sections over the next 2 hours.")
print("Each section lasts 4 minutes with subtle and dramatic changes.")
print("\nENJOY THE TRANCE!")
print("=" * 80)

s.close()
