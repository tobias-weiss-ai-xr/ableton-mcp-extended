#!/usr/bin/env python3
"""
INDEFINITE LIVE PERFORMANCE SCRIPT
Forever mode: Rapid parameter automation across all tracks

Based on the ableton-dj-performance skill:
- Mode 2: Rapid Automation (Live Tweaking)
- Focus on device parameters, NOT clip switching
- Create evolving textures through constant automation
"""

import socket
import json
import time
import random
import signal
import sys

# TCP connection for reliable commands
TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(cmd_type, params):
    """Send command via TCP and get response"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_HOST, TCP_PORT))
    s.send(json.dumps({"type": cmd_type, "params": params}).encode("utf-8"))
    response = s.recv(4096).decode("utf-8")
    s.close()
    try:
        return json.loads(response)
    except:
        return {"status": "error", "error": "Response issue"}


def send_udp(cmd_type, params):
    """Send fire-and-forget command via UDP (ultra-low latency)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(
        json.dumps({"type": cmd_type, "params": params}).encode("utf-8"),
        (TCP_HOST, 9878),
    )
    s.close()


# Track configuration based on session assessment
TRACKS = {
    0: {"name": "Drums", "type": "drums"},
    1: {"name": "Bass", "type": "bass"},
    2: {"name": "FX_Risers", "type": "fx"},
    3: {"name": "Pad_Atmos", "type": "pad"},
    4: {"name": "Rhythm_Skank", "type": "keys"},
    5: {"name": "Horns_Melody", "type": "melody"},
    6: {"name": "Percussion", "type": "perc"},
    7: {"name": "Vocal_Chops", "type": "vocals"},
    8: {"name": "9-Wood Flute", "type": "melody"},
}

# Safe parameter ranges for different track types
PARAM_RANGES = {
    "drums": {
        "filter": (2, 0.3, 0.9),  # param_index, min, max
        "reverb": (4, 0.0, 0.6),
        "drive": (6, 0.0, 0.6),
    },
    "bass": {
        "filter": (2, 0.3, 0.8),
        "drive": (6, 0.0, 0.5),
    },
    "pad": {
        "filter": (2, 0.3, 0.8),
        "reverb": (4, 0.2, 0.7),
    },
    "keys": {
        "filter": (2, 0.3, 0.8),
        "reverb": (4, 0.2, 0.7),
    },
    "melody": {
        "filter": (2, 0.3, 0.8),
        "reverb": (4, 0.2, 0.7),
    },
    "perc": {
        "filter": (2, 0.3, 0.9),
    },
    "fx": {
        "filter": (2, 0.2, 0.9),
    },
    "vocals": {
        "filter": (2, 0.3, 0.8),
        "reverb": (4, 0.2, 0.7),
    },
}

running = True


def signal_handler(sig, frame):
    """Graceful shutdown"""
    global running
    print("\n\nStopping performance...")
    running = False
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def random_value(min_val, max_val):
    """Generate random value in range with smooth transitions"""
    return random.uniform(min_val, max_val)


def cycle_through_tracks():
    """Main performance loop - cycle through tracks and parameters"""
    print("\n" + "=" * 60)
    print("INDEFINITE LIVE PERFORMANCE - FOREVER MODE")
    print("=" * 60)
    print("\nPattern: Rapid cycling through tracks and parameters")
    print("Press Ctrl+C to stop\n")

    cycle_count = 0

    while running:
        cycle_count += 1

        # Each cycle: adjust multiple tracks
        for track_idx, track_info in TRACKS.items():
            track_type = track_info["type"]

            # Skip if no params defined for this type
            if track_type not in PARAM_RANGES:
                continue

            # Get available parameters for this track type
            params = PARAM_RANGES[track_type]

            # Randomly select 1-2 parameters to adjust
            num_params = random.randint(1, min(2, len(params)))
            selected_params = random.sample(list(params.keys()), num_params)

            for param_name in selected_params:
                param_info = params[param_name]
                param_idx, min_val, max_val = param_info

                # Generate new value
                new_value = random_value(min_val, max_val)

                # Send via UDP for ultra-low latency
                send_udp(
                    "set_device_parameter",
                    {
                        "track_index": track_idx,
                        "device_index": 0,
                        "parameter_index": param_idx,
                        "value": new_value,
                    },
                )

                # Log the change (less frequent to avoid clutter)
                if cycle_count % 3 == 0:  # Log every 3rd cycle
                    print(
                        f"T{track_idx:2d} [{track_info['name'][:12]:<13}] {param_name:<8} -> {new_value:.2f}"
                    )

        # Wait before next cycle (1-3 seconds for natural feel)
        time.sleep(random.uniform(1.0, 3.0))


def filter_sweep_pattern():
    """Alternative: Filter sweep build and drop pattern"""
    print("\n" + "=" * 60)
    print("FILTER SWEEP PATTERN")
    print("=" * 60)

    while running:
        # BUILD: Open filters
        print("\n--- BUILD: Opening filters ---")
        for track_idx in [0, 1, 3, 4]:  # Drums, Bass, Pad, Keys
            for i in range(10):
                progress = i / 9.0
                value = 0.3 + (progress * 0.5)  # 0.3 → 0.8

                send_udp(
                    "set_device_parameter",
                    {
                        "track_index": track_idx,
                        "device_index": 0,
                        "parameter_index": 2,  # Filter
                        "value": value,
                    },
                )
                time.sleep(0.5)

        # Hold
        print("--- Holding ---")
        time.sleep(8)

        # DROP: Close filters
        print("\n--- DROP: Closing filters ---")
        for track_idx in [0, 1, 3, 4]:
            for i in range(10):
                progress = i / 9.0
                value = 0.8 - (progress * 0.5)  # 0.8 → 0.3

                send_udp(
                    "set_device_parameter",
                    {
                        "track_index": track_idx,
                        "device_index": 0,
                        "parameter_index": 2,  # Filter
                        "value": value,
                    },
                )
                time.sleep(0.3)

        # Hold drop
        print("--- Hold drop ---")
        time.sleep(16)


def main():
    """Main entry point"""
    print("\nInitializing performance...")

    # Ensure playback is running
    result = send_tcp("start_playback", {})
    print(f"Playback: {result['status']}")

    # Set tempo for dub techno
    result = send_tcp("set_tempo", {"tempo": 120})
    print(f"Tempo: {result['result']['tempo']} BPM")

    print("\nStarting automation...")
    print("Mode: Rapid parameter cycling (Forever Mode)")

    # Run the main performance loop
    try:
        cycle_through_tracks()
    except KeyboardInterrupt:
        print("\n\nPerformance stopped.")


if __name__ == "__main__":
    main()
