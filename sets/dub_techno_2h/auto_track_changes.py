#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Dub Techno Automation - Track changes every 40-60 seconds
DJ-style: ONE CLIP CHANGE AT A TIME
"""

import socket
import json
import time
import random
import sys

# Configuration
TCP_HOST = "localhost"
TCP_PORT = 9877
MIN_INTERVAL = 40  # seconds
MAX_INTERVAL = 60  # seconds

# Track configuration
TRACKS = {
    "kick": 0,
    "bass": 1,
    "hats": 2,
    "percs": 3,
    "pad": 4,
    "fx": 5,
    "lead": 6,
    "stabs": 7,
}

# Automation sequence (track, clip_index, clip_name)
# Following DJ rule: one change at a time
AUTOMATION_SEQUENCE = [
    # Phase 1: Build energy (0-5 min)
    ("hats", 4, "Hats_Ghost_Groove"),
    ("bass", 7, "Sub_Walking_F"),
    ("kick", 5, "Kick_Four_Floor"),
    ("stabs", 1, "Stab_Cm7_Skank"),
    ("hats", 2, "Hats_Offbeat_Dub"),
    # Phase 2: Peak energy (5-10 min)
    ("bass", 4, "Sub_Octave_Dub"),
    ("kick", 1, "Kick_Dub_Drive"),
    ("stabs", 3, "Stab_Fm9_Dub"),
    ("hats", 1, "Hats_Rolling_16"),
    ("bass", 6, "Sub_Tremolo"),
    # Phase 3: Variation (10-15 min)
    ("kick", 6, "Kick_Swung"),
    ("hats", 4, "Hats_Ghost_Groove"),
    ("bass", 5, "Sub_Groove_F"),
    ("stabs", 2, "Stab_Bbm7_Syncopated"),
    ("kick", 0, "Kick_Fund"),
    # Phase 4: Return to groove (15-20 min)
    ("hats", 2, "Hats_Offbeat_Dub"),
    ("bass", 7, "Sub_Walking_F"),
    ("kick", 5, "Kick_Four_Floor"),
    ("stabs", 0, "Stab_Fm7_Skank"),
    ("hats", 1, "Hats_Rolling_16"),
    # Phase 5: Deep dub (20-25 min)
    ("kick", 3, "Kick_Sparse"),
    ("bass", 1, "Sub_Heavy_Dub"),
    ("hats", 7, "Hats_None"),
    ("stabs", 5, "Stab_Minimal"),
    ("kick", 5, "Kick_Four_Floor"),
    # Phase 6: Final build (25-30 min)
    ("hats", 4, "Hats_Ghost_Groove"),
    ("bass", 4, "Sub_Octave_Dub"),
    ("kick", 1, "Kick_Dub_Drive"),
    ("stabs", 1, "Stab_Cm7_Skank"),
    ("bass", 5, "Sub_Groove_F"),
]


class AbletonConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_command(self, command_type, params=None):
        if params is None:
            params = {}

        command = {"type": command_type, "params": params}
        self.sock.send(json.dumps(command).encode("utf-8"))
        response = json.loads(self.sock.recv(8192).decode("utf-8"))
        return response

    def fire_clip(self, track_index, clip_index):
        result = self.send_command(
            "fire_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return result.get("status") == "success"

    def close(self):
        if self.sock:
            self.sock.close()


def format_time(seconds):
    """Format seconds as MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def main():
    print("=" * 60)
    print("  DUB TECHNO LIVE AUTOMATION")
    print("  Track changes every 40-60 seconds")
    print("  DJ Rule: ONE CLIP CHANGE AT A TIME")
    print("=" * 60)
    print()

    # Connect to Ableton
    print("Connecting to Ableton...")
    ableton = AbletonConnection(TCP_HOST, TCP_PORT)
    if not ableton.connect():
        print("Failed to connect!")
        return
    print("Connected!\n")

    start_time = time.time()
    change_count = 0

    try:
        while True:
            for i, (track_name, clip_index, clip_name) in enumerate(
                AUTOMATION_SEQUENCE
            ):
                # Random interval between 40-60 seconds
                interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)

                # Calculate elapsed time
                elapsed = time.time() - start_time

                # Print status
                print(f"\n[Change #{change_count + 1}] @ {format_time(elapsed)}")
                print(f"  Track: {track_name.upper()} (Track {TRACKS[track_name]})")
                print(f"  Clip: {clip_name} (Index {clip_index})")
                print(f"  Next change in: {interval} seconds")

                # Fire the clip
                track_index = TRACKS[track_name]
                if ableton.fire_clip(track_index, clip_index):
                    print(f"  Status: FIRED")
                else:
                    print(f"  Status: ERROR")

                change_count += 1

                # Wait for next change
                time.sleep(interval)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\nAutomation stopped after {format_time(elapsed)}")
        print(f"Total changes: {change_count}")
        ableton.close()


if __name__ == "__main__":
    main()
