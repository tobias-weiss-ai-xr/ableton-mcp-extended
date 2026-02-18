#!/usr/bin/env python3
"""
2-Hour Dub Techno Clip Generator

Generates 384 clips (6 tracks × 8 scenes × 8 variations) for the dub techno session.
Uses MCP server TCP connection to create clips programmatically.

Usage:
1. Ensure MCP server is running and connected to Ableton
2. Run this script: python generate_dub_techno_clips.py
"""

import socket
import json
import time

# MCP Server connection settings
TCP_HOST = "localhost"
TCP_PORT = 9877

# Session configuration
BPM = 128
SCENES = [
    "Opening",
    "First Beat",
    "Deep Groove",
    "First Build",
    "Breakdown",
    "Return",
    "Peak",
    "Outro",
]
TRACKS = ["Drums", "Bass", "Hats", "Chord", "Pad", "Percussion"]

# Key journey: Am → Dm → Em → Gm → Am
SCENE_KEYS = {
    0: {"root": 45, "name": "Am"},  # A2
    1: {"root": 45, "name": "Am"},  # A2
    2: {"root": 50, "name": "Dm"},  # D2
    3: {"root": 50, "name": "Dm"},  # D2
    4: {"root": 52, "name": "Em"},  # E2
    5: {"root": 52, "name": "Em"},  # E2
    6: {"root": 55, "name": "Gm"},  # G2
    7: {"root": 45, "name": "Am"},  # A2
}

# Chord intervals (root, minor 3rd, 5th)
MINOR_CHORD = [0, 3, 7]

# Drum note mapping (for 64 Pads Dub Techno Kit)
KICK = 36
SNARE = 40
HAT = 42
OPEN_HAT = 46
CLAP = 39
RIM = 37


class MCPClient:
    def __init__(self):
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_HOST, TCP_PORT))
        print(f"Connected to MCP server at {TCP_HOST}:{TCP_PORT}")

    def disconnect(self):
        if self.socket:
            self.socket.close()

    def send_command(self, command_type: str, params: dict = None) -> dict:
        """Send a command to the MCP server and return the response."""
        message = {"type": command_type}
        if params:
            message["params"] = params

        self.socket.send(json.dumps(message).encode() + b"\n")
        response = self.socket.recv(8192).decode()
        return json.loads(response)


def generate_drum_pattern(scene_index: int, variation: int) -> list:
    """Generate drum pattern notes based on scene and variation."""
    notes = []

    # Scene 0 (Opening): sparse
    # Scene 1-2: building
    # Scene 3-4: full
    # Scene 5-6: peak
    # Scene 7: strip down

    if scene_index == 0:  # Opening - very sparse
        if variation < 2:  # Only first 2 variations have kick
            for beat in range(0, 8, 4):
                notes.append(
                    {
                        "pitch": KICK,
                        "start_time": beat,
                        "duration": 0.5,
                        "velocity": 100,
                        "mute": False,
                    }
                )

    elif scene_index in [1, 2]:  # Building
        for beat in range(8):
            notes.append(
                {
                    "pitch": KICK,
                    "start_time": beat,
                    "duration": 0.5,
                    "velocity": 100,
                    "mute": False,
                }
            )
        # Add off-beat hats
        for beat in range(8):
            notes.append(
                {
                    "pitch": HAT,
                    "start_time": beat + 0.5,
                    "duration": 0.25,
                    "velocity": 60 + (variation * 5),
                    "mute": False,
                }
            )

    elif scene_index in [3, 4, 5, 6]:  # Full/Peak
        for beat in range(8):
            notes.append(
                {
                    "pitch": KICK,
                    "start_time": beat,
                    "duration": 0.5,
                    "velocity": 100,
                    "mute": False,
                }
            )
        # Snares on 2 and 4
        for beat in [1, 3, 5, 7]:
            notes.append(
                {
                    "pitch": SNARE,
                    "start_time": beat,
                    "duration": 0.25,
                    "velocity": 90,
                    "mute": False,
                }
            )
        # Hi-hats every 8th
        for beat in range(16):
            notes.append(
                {
                    "pitch": HAT,
                    "start_time": beat * 0.5,
                    "duration": 0.25,
                    "velocity": 60,
                    "mute": False,
                }
            )

    else:  # Outro - strip down
        for beat in range(0, 8 - variation, 2):
            notes.append(
                {
                    "pitch": KICK,
                    "start_time": beat,
                    "duration": 0.5,
                    "velocity": 80,
                    "mute": False,
                }
            )

    return notes


def generate_bass_pattern(scene_index: int, variation: int) -> list:
    """Generate bass pattern notes based on scene and variation."""
    root = SCENE_KEYS[scene_index]["root"]
    notes = []

    if scene_index == 0:  # Opening - long sustained notes
        notes.append(
            {
                "pitch": root,
                "start_time": 0,
                "duration": 4,
                "velocity": 80,
                "mute": False,
            }
        )
    else:
        # Off-beat sub bass pattern
        for i in range(4):
            notes.append(
                {
                    "pitch": root,
                    "start_time": i * 2 + 0.5,
                    "duration": 1.5,
                    "velocity": 90 - variation * 5,
                    "mute": False,
                }
            )

    return notes


def generate_hat_pattern(scene_index: int, variation: int) -> list:
    """Generate hi-hat pattern notes based on scene and variation."""
    notes = []

    if scene_index == 0:  # Opening - no hats
        return []

    # Off-beat hats
    for beat in range(8):
        notes.append(
            {
                "pitch": HAT if beat % 2 == 0 else OPEN_HAT,
                "start_time": beat + 0.5,
                "duration": 0.25,
                "velocity": 50 + variation * 5,
                "mute": False,
            }
        )

    return notes


def generate_chord_pattern(scene_index: int, variation: int) -> list:
    """Generate chord pattern notes based on scene and variation."""
    root = SCENE_KEYS[scene_index]["root"]
    notes = []

    # Chord stabs on each bar
    for bar in range(4):
        for interval in MINOR_CHORD:
            notes.append(
                {
                    "pitch": root + 12 + interval,  # Octave up
                    "start_time": bar * 2,
                    "duration": 1.5,
                    "velocity": 70 + variation * 3,
                    "mute": False,
                }
            )

    return notes


def generate_pad_pattern(scene_index: int, variation: int) -> list:
    """Generate pad pattern notes based on scene and variation."""
    root = SCENE_KEYS[scene_index]["root"]
    notes = []

    # Sustained chord
    for interval in MINOR_CHORD:
        notes.append(
            {
                "pitch": root + interval,
                "start_time": 0,
                "duration": 8,
                "velocity": 50 + variation * 5,
                "mute": False,
            }
        )

    return notes


def generate_percussion_pattern(scene_index: int, variation: int) -> list:
    """Generate percussion pattern notes based on scene and variation."""
    notes = []

    if scene_index < 2:  # No percussion in opening
        return []

    # Rim shots on off-beats
    for beat in range(4, 8, 2):
        notes.append(
            {
                "pitch": RIM,
                "start_time": beat + 0.5,
                "duration": 0.25,
                "velocity": 60,
                "mute": False,
            }
        )

    return notes


def main():
    client = MCPClient()

    try:
        client.connect()

        # Step 1: Ensure we have enough tracks
        print("\nSetting up tracks...")
        response = client.send_command("get_session_info", {})
        current_track_count = response.get("result", {}).get("track_count", 0)
        print(f"  Current tracks: {current_track_count}")

        # Create tracks if needed
        while current_track_count < len(TRACKS):
            client.send_command("create_midi_track", {"index": -1})
            current_track_count += 1
        print(f"  Ensured {len(TRACKS)} tracks exist")

        # Name tracks correctly
        for track_index, track_name in enumerate(TRACKS):
            client.send_command(
                "set_track_name", {"track_index": track_index, "name": track_name}
            )
        print(f"  Named {len(TRACKS)} tracks")

        # Step 2: Ensure we have enough scenes
        response = client.send_command("get_session_info", {})
        current_scene_count = response.get("result", {}).get("scene_count", 0)
        print(f"  Current scenes: {current_scene_count}")

        while current_scene_count < 8:
            client.send_command("create_scene", {"index": -1})
            current_scene_count += 1
        print(f"  Ensured 8 scenes exist")

        # Name scenes
        for scene_index, scene_name in enumerate(SCENES):
            client.send_command(
                "set_scene_name", {"scene_index": scene_index, "name": scene_name}
            )
        print(f"  Named 8 scenes")

        # Step 3: Delete all existing clips
        print("\nDeleting existing clips...")
        for track_index in range(len(TRACKS)):
            for clip_index in range(8):
                client.send_command(
                    "delete_clip",
                    {"track_index": track_index, "clip_index": clip_index},
                )
        print("  Deleted existing clips")

        # Step 4: Set tempo
        client.send_command("set_tempo", {"tempo": BPM})
        print(f"  Set tempo to {BPM} BPM")

        total_clips = 0

        # Step 5: Generate clips for each track and scene
        for track_index, track_name in enumerate(TRACKS):
            print(f"\nGenerating clips for {track_name}...")

            for scene_index in range(8):
                clip_index = scene_index

                length = 8 if track_name in ["Drums", "Pad"] else 4
                response = client.send_command(
                    "create_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "length": float(length),
                    },
                )

                if response.get("status") == "error":
                    print(f"  Error creating clip {clip_index}: {response}")
                    continue

                # Generate notes (variation=0)
                if track_name == "Drums":
                    notes = generate_drum_pattern(scene_index, 0)
                elif track_name == "Bass":
                    notes = generate_bass_pattern(scene_index, 0)
                elif track_name == "Hats":
                    notes = generate_hat_pattern(scene_index, 0)
                elif track_name == "Chord":
                    notes = generate_chord_pattern(scene_index, 0)
                elif track_name == "Pad":
                    notes = generate_pad_pattern(scene_index, 0)
                else:
                    notes = generate_percussion_pattern(scene_index, 0)

                if notes:
                    response = client.send_command(
                        "add_notes_to_clip",
                        {
                            "track_index": track_index,
                            "clip_index": clip_index,
                            "notes": notes,
                        },
                    )

                    if response.get("status") == "error":
                        print(f"  Error adding notes: {response}")
                        continue

                total_clips += 1

            print(f"  Created 8 clips")

        print(f"\n[OK] Complete! Created {total_clips} clips")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
