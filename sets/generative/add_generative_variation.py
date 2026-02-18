#!/usr/bin/env python3
"""
Add Generative Variation to 2-Hour Dub Techno Session

This script enhances the existing session with:
1. Random follow actions for self-evolving clips
2. Velocity humanization for more organic feel
3. Micro-timing variation for swing/groove
4. Clip chain configuration for infinite variation

Usage:
    python scripts/add_generative_variation.py

After running, the session will evolve continuously when playing.
"""

import socket
import json
import random
import time
from typing import List, Dict, Optional

# Configuration
TCP_HOST = "localhost"
TCP_PORT = 9877
UDP_HOST = "localhost"
UDP_PORT = 9878

# Session config (matches our 2h session)
NUM_TRACKS = 6
CLIPS_PER_TRACK = 8
TRACK_NAMES = ["Drums", "Bass", "Hats", "Chord", "Pad", "Percussion"]

# Generative parameters
FOLLOW_ACTION_STAY_PROB = 0.5  # 50% stay, 50% transition
VELOCITY_VARIATION = 15  # ± velocity
TIMING_VARIATION = 0.02  # ± beats (micro-timing)
GHOST_NOTE_PROB = 0.15  # 15% chance for ghost notes


class MCPClient:
    """Dual-protocol MCP client."""

    def __init__(self):
        self.tcp = None
        self.udp = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()

    def connect(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.connect((TCP_HOST, TCP_PORT))
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Connected to MCP server")

    def disconnect(self):
        if self.tcp:
            self.tcp.close()
        if self.udp:
            self.udp.close()

    def send_tcp(self, command_type: str, params: dict = None) -> dict:
        msg = {"type": command_type}
        if params:
            msg["params"] = params
        self.tcp.send(json.dumps(msg).encode() + b"\n")
        return json.loads(self.tcp.recv(8192).decode())

    def send_udp(self, command_type: str, params: dict):
        msg = {"type": command_type, "params": params}
        self.udp.sendto(json.dumps(msg).encode(), (UDP_HOST, UDP_PORT))


def get_clip_notes(client: MCPClient, track_index: int, clip_index: int) -> List[dict]:
    """Get all notes from a clip."""
    response = client.send_tcp(
        "get_clip_notes", {"track_index": track_index, "clip_index": clip_index}
    )
    if "result" in response and "notes" in response["result"]:
        return response["result"]["notes"]
    return []


def humanize_notes(
    notes: List[dict], velocity_var: int = 10, timing_var: float = 0.01
) -> List[dict]:
    """Add humanization to notes (velocity and timing variation)."""
    humanized = []
    for note in notes:
        new_note = note.copy()

        # Velocity variation
        if "velocity" in new_note:
            orig_vel = new_note["velocity"]
            new_vel = orig_vel + random.randint(-velocity_var, velocity_var)
            new_note["velocity"] = max(1, min(127, new_vel))

        # Micro-timing variation (only for non-kick drums)
        if timing_var > 0 and note.get("pitch", 60) != 36:  # Don't shift kicks
            if "start_time" in new_note:
                shift = random.uniform(-timing_var, timing_var)
                new_note["start_time"] = max(0, new_note["start_time"] + shift)

        humanized.append(new_note)

    return humanized


def add_ghost_notes(
    notes: List[dict], track_type: str, prob: float = 0.15
) -> List[dict]:
    """Add probabilistic ghost notes to patterns."""
    if track_type != "Drums":
        return notes

    # Find existing kick hits
    kick_times = [n["start_time"] for n in notes if n.get("pitch") == 36]

    # Add ghost kicks between main kicks with probability
    ghost_notes = []
    for i, kick_time in enumerate(kick_times[:-1]):
        next_kick = kick_times[i + 1]
        mid_point = (kick_time + next_kick) / 2

        if random.random() < prob:
            ghost_notes.append(
                {
                    "pitch": 36,  # Ghost kick
                    "start_time": mid_point,
                    "duration": 0.25,
                    "velocity": random.randint(30, 50),
                    "mute": False,
                }
            )

    return notes + ghost_notes


def setup_follow_actions(
    client: MCPClient,
    track_index: int,
    clip_index: int,
    stay_prob: float = 0.5,
    total_clips: int = 8,
):
    """
    Set up follow action for a clip.

    Action types:
    0 = None
    1 = Play again
    2 = Stop
    3 = Play other clip
    """
    if random.random() < stay_prob:
        # Stay on same clip - no follow action
        client.send_tcp(
            "set_clip_follow_action",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "action_slot": 0,
                "action_type": 0,  # None
                "trigger_time": 1.0,
            },
        )
    else:
        # Transition to another clip
        other_clips = [i for i in range(total_clips) if i != clip_index]
        target = random.choice(other_clips)

        client.send_tcp(
            "set_clip_follow_action",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "action_slot": 0,
                "action_type": 3,  # Play other clip
                "trigger_time": 1.0,  # After 1 loop
                "clip_index_target": target,
            },
        )


def apply_variation_to_track(client: MCPClient, track_index: int, track_name: str):
    """Apply generative variation to all clips in a track."""
    print(f"\n  Processing {track_name}...")

    for clip_idx in range(CLIPS_PER_TRACK):
        # Get existing notes
        notes = get_clip_notes(client, track_index, clip_idx)

        if notes:
            # Humanize notes
            humanized = humanize_notes(notes, VELOCITY_VARIATION, TIMING_VARIATION)

            # Add ghost notes for drums
            if track_name == "Drums":
                humanized = add_ghost_notes(humanized, "Drums", GHOST_NOTE_PROB)

            # Delete old notes and add new ones
            # Note: We're updating in place by replacing notes
            if len(humanized) > 0:
                # First delete existing notes
                note_indices = list(range(len(notes)))
                client.send_tcp(
                    "delete_notes_from_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_idx,
                        "note_indices": note_indices,
                    },
                )

                # Add humanized notes
                client.send_tcp(
                    "add_notes_to_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_idx,
                        "notes": humanized,
                    },
                )

        # Set up follow action
        setup_follow_actions(
            client, track_index, clip_idx, FOLLOW_ACTION_STAY_PROB, CLIPS_PER_TRACK
        )


def configure_clip_launch_modes(client: MCPClient):
    """Set varied launch modes for more interesting playback."""
    # Launch modes: 0=Trigger, 1=Gate, 2=Toggle, 3=Repeat

    for track_idx in range(NUM_TRACKS):
        for clip_idx in range(CLIPS_PER_TRACK):
            # Use Toggle mode for most clips (allows follow actions to work)
            # Use Trigger for some drums for tighter response
            if track_idx == 0:  # Drums
                mode = 0  # Trigger
            elif track_idx == 2:  # Hats
                mode = 2 if clip_idx % 2 == 0 else 0  # Mix Toggle/Trigger
            else:
                mode = 2  # Toggle (best for follow actions)

            client.send_tcp(
                "set_clip_launch_mode",
                {"track_index": track_idx, "clip_index": clip_idx, "mode": mode},
            )


def setup_random_parameter_automation(client: MCPClient):
    """Configure initial random parameter states for tracks."""
    # Set slightly different volumes for each track
    base_volumes = [0.8, 0.7, 0.6, 0.75, 0.65, 0.55]

    for track_idx in range(NUM_TRACKS):
        vol = base_volumes[track_idx] + random.uniform(-0.05, 0.05)
        client.send_udp(
            "set_track_volume",
            {"track_index": track_idx, "volume": max(0.3, min(0.9, vol))},
        )


def main():
    print("=" * 60)
    print("GENERATIVE VARIATION SETUP")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Tracks: {NUM_TRACKS}")
    print(f"  Clips per track: {CLIPS_PER_TRACK}")
    print(f"  Follow action stay probability: {FOLLOW_ACTION_STAY_PROB * 100:.0f}%")
    print(f"  Velocity variation: ±{VELOCITY_VARIATION}")
    print(f"  Timing variation: ±{TIMING_VARIATION} beats")
    print(f"  Ghost note probability: {GHOST_NOTE_PROB * 100:.0f}%")

    with MCPClient() as client:
        # Verify connection
        response = client.send_tcp("get_session_info", {})
        print(f"\nConnected to session: {response.get('track_count', '?')} tracks")

        print("\n[1/4] Applying humanization and ghost notes...")
        for track_idx, track_name in enumerate(TRACK_NAMES):
            apply_variation_to_track(client, track_idx, track_name)

        print("\n[2/4] Configuring clip launch modes...")
        configure_clip_launch_modes(client)

        print("\n[3/4] Setting random parameter automation...")
        setup_random_parameter_automation(client)

        print("\n[4/4] Verifying follow actions...")
        # Verify a few clips have follow actions
        verified = 0
        for track_idx in range(NUM_TRACKS):
            for clip_idx in range(CLIPS_PER_TRACK):
                response = client.send_tcp(
                    "get_clip_follow_actions",
                    {"track_index": track_idx, "clip_index": clip_idx},
                )
                if response.get("result", {}).get("follow_actions"):
                    verified += 1

        print(f"  Verified {verified} clips with follow actions")

        print("\n" + "=" * 60)
        print("GENERATIVE VARIATION COMPLETE!")
        print("=" * 60)
        print("\nSession now features:")
        print("  ✓ Self-evolving clips via follow actions")
        print("  ✓ Humanized velocity (+/- 15)")
        print("  ✓ Micro-timing variation (±0.02 beats)")
        print("  ✓ Probabilistic ghost notes (15%)")
        print("  ✓ Varied launch modes")
        print("\nFire any clip to start the evolving journey!")
        print("For continuous automation, run: python scripts/live_dub_automation.py")


if __name__ == "__main__":
    main()
