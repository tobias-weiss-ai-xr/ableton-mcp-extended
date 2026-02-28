#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Dub Effects to 2-Hour Reggae Dub Session
=============================================

Adds classic dub effects to all tracks:
- Reverb (long tails, space)
- Delay (tape echo, dub delays)
- Phaser (sweeping movement)
- Chorus (thickness)
- Compressor (punch)
- EQ/Filter (tone shaping)
- Saturation (warmth)

MIDI Effects:
- Arpeggiator (on synths)
- Scale (C Minor constraint)
- Random (subtle variation)

Usage:
    python add_dub_effects.py
"""

import socket
import json
import time
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_cmd(cmd_type, params=None):
    """Send command to MCP server"""
    if params is None:
        params = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((TCP_HOST, TCP_PORT))
    sock.send(json.dumps({"type": cmd_type, "params": params}).encode("utf-8"))

    data = b""
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except:
            continue

    sock.close()
    return json.loads(data.decode("utf-8"))


def load_effect(track_index, effect_uri):
    """Load an audio effect onto a track"""
    result = send_cmd(
        "load_browser_item", {"track_index": track_index, "item_uri": effect_uri}
    )
    return result


def load_midi_effect(track_index, effect_uri):
    """Load a MIDI effect onto a track"""
    result = send_cmd(
        "load_browser_item", {"track_index": track_index, "item_uri": effect_uri}
    )
    return result


def set_parameter(track_index, device_index, param_index, value):
    """Set a device parameter"""
    result = send_cmd(
        "set_device_parameter",
        {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": param_index,
            "value": value,
        },
    )
    return result


def get_track_devices(track_index):
    """Get devices on a track"""
    result = send_cmd("get_track_info", {"track_index": track_index})
    if result.get("status") == "success":
        return result.get("result", {}).get("devices", [])
    return []


print("=" * 70)
print("  ADDING DUB EFFECTS TO REGGAE DUB SESSION")
print("=" * 70)
print()

# =============================================================================
# AUDIO EFFECTS - Load onto each track
# =============================================================================
# Effect URIs (from Ableton browser)
EFFECTS = {
    "reverb": "query:Audio%20Effects#Reverb",
    "hybrid_reverb": "query:Audio%20Effects#Hybrid%20Reverb",
    "delay": "query:Audio%20Effects#Simple%20Delay",
    "ping_pong_delay": "query:Audio%20Effects#Ping%20Pong%20Delay",
    "phaser": "query:Audio%20Effects#Phaser",
    "chorus": "query:Audio%20Effects#Chorus",
    "compressor": "query:Audio%20Effects#Compressor",
    "glue_compressor": "query:Audio%20Effects#Glue%20Compressor",
    "eq Eight": "query:Audio%20Effects#EQ%20Eight",
    "auto_filter": "query:Audio%20Effects#Auto%20Filter",
    "saturator": "query:Audio%20Effects#Saturator",
    "overdrive": "query:Audio%20Effects#Overdrive",
    "corpus": "query:Audio%20Effects#Corpus",
    "echo": "query:Audio%20Effects#Echo",
    "drift": "query:Audio%20Effects#Drift",
}

MIDI_EFFECTS = {
    "arpeggiator": "query:MIDI%20Effects#Arpeggiator",
    "scale": "query:MIDI%20Effects#Scale",
    "chord": "query:MIDI%20Effects#Chord",
    "random": "query:MIDI%20Effects#Random",
    "velocity": "query:MIDI%20Effects#Velocity",
}

# Track-specific effect chains
TRACK_EFFECTS = {
    0: {  # Drums
        "name": "Drums",
        "audio": ["compressor", "eq Eight", "phaser", "reverb"],
        "midi": [],
        "settings": {
            "compressor": {"ratio": 0.3, "threshold": 0.4},
            "reverb": {"size": 0.6, "decay": 0.5, "dry_wet": 0.3},
            "phaser": {"amount": 0.3, "rate": 0.2},
        },
    },
    1: {  # Dub Bass
        "name": "Dub Bass",
        "audio": ["saturator", "auto_filter", "delay", "compressor"],
        "midi": ["scale"],
        "settings": {
            "saturator": {"drive": 0.4, "dry_wet": 0.5},
            "delay": {"time": 0.25, "feedback": 0.6, "dry_wet": 0.4},
            "auto_filter": {"freq": 0.7, "resonance": 0.3},
            "scale": {"root": 0, "scale_type": "minor"},  # C Minor
        },
    },
    2: {  # Guitar Chop
        "name": "Guitar Chop",
        "audio": ["chorus", "delay", "reverb", "eq Eight"],
        "midi": [],
        "settings": {
            "chorus": {"rate": 0.3, "depth": 0.5, "dry_wet": 0.4},
            "delay": {"time": 0.33, "feedback": 0.5, "dry_wet": 0.5},
            "reverb": {"size": 0.7, "decay": 0.6, "dry_wet": 0.4},
        },
    },
    3: {  # Organ Bubble
        "name": "Organ Bubble",
        "audio": ["rotary", "delay", "reverb", "overdrive"],
        "midi": ["scale"],
        "settings": {
            "delay": {"time": 0.5, "feedback": 0.4, "dry_wet": 0.35},
            "reverb": {"size": 0.8, "decay": 0.7, "dry_wet": 0.3},
            "overdrive": {"drive": 0.3, "dry_wet": 0.4},
        },
    },
    4: {  # Synth Pad
        "name": "Synth Pad",
        "audio": ["chorus", "phaser", "delay", "reverb", "auto_filter"],
        "midi": ["arpeggiator", "scale"],
        "settings": {
            "chorus": {"rate": 0.2, "depth": 0.6, "dry_wet": 0.5},
            "phaser": {"amount": 0.4, "rate": 0.15},
            "delay": {"time": 0.66, "feedback": 0.7, "dry_wet": 0.6},
            "reverb": {"size": 0.9, "decay": 0.8, "dry_wet": 0.5},
            "auto_filter": {"freq": 0.5, "resonance": 0.4},
        },
    },
    5: {  # FX
        "name": "FX",
        "audio": ["reverb", "delay", "phaser", "saturator"],
        "midi": ["random"],
        "settings": {
            "reverb": {"size": 1.0, "decay": 0.9, "dry_wet": 0.7},
            "delay": {"time": 0.75, "feedback": 0.8, "dry_wet": 0.6},
            "phaser": {"amount": 0.6, "rate": 0.1},
        },
    },
}

# =============================================================================
# PHASE 1: LOAD AUDIO EFFECTS
# =============================================================================
print("=" * 70)
print("  PHASE 1: LOADING AUDIO EFFECTS")
print("=" * 70)
print()

for track_idx, config in TRACK_EFFECTS.items():
    track_name = config["name"]
    print(f"\n[Track {track_idx}] {track_name}")

    # Get current devices to know where to load
    devices = get_track_devices(track_idx)
    print(f"  Current devices: {len(devices)}")

    # Load audio effects
    for effect_name in config.get("audio", []):
        effect_uri = EFFECTS.get(effect_name)
        if not effect_uri:
            print(f"    [SKIP] {effect_name} - URI not found")
            continue

        print(f"    Loading {effect_name}...")
        result = load_effect(track_idx, effect_uri)

        if result.get("status") == "success":
            print(f"    [OK] {effect_name} loaded")
        else:
            print(f"    [ERROR] {result.get('message')}")

        time.sleep(0.5)

    # Load MIDI effects (before instrument)
    for effect_name in config.get("midi", []):
        effect_uri = MIDI_EFFECTS.get(effect_name)
        if not effect_uri:
            print(f"    [SKIP] {effect_name} - URI not found")
            continue

        print(f"    Loading MIDI: {effect_name}...")
        result = load_midi_effect(track_idx, effect_uri)

        if result.get("status") == "success":
            print(f"    [OK] {effect_name} loaded")
        else:
            print(f"    [ERROR] {result.get('message')}")

        time.sleep(0.5)

# =============================================================================
# PHASE 2: CONFIGURE EFFECT PARAMETERS
# =============================================================================
print("\n" + "=" * 70)
print("  PHASE 2: CONFIGURING EFFECT PARAMETERS")
print("=" * 70)
print()

for track_idx, config in TRACK_EFFECTS.items():
    track_name = config["name"]
    print(f"\n[Track {track_idx}] {track_name}")

    # Get updated device list
    devices = get_track_devices(track_idx)

    # Configure each effect
    for device in devices:
        device_name = device.get("name", "").lower()
        device_idx = device.get("index")

        # Find matching effect settings
        for effect_name, settings in config.get("settings", {}).items():
            if effect_name.lower() in device_name:
                print(f"  Configuring {device.get('name')}...")

                # Get parameters for this device
                params_result = send_cmd(
                    "get_device_parameters",
                    {"track_index": track_idx, "device_index": device_idx},
                )

                if params_result.get("status") == "success":
                    params = params_result.get("result", [])

                    # Apply settings based on parameter names
                    for param in params:
                        param_name = param.get("name", "").lower()
                        param_idx = param.get("index")

                        # Match common parameter names
                        if "size" in param_name and "size" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["size"]
                            )
                            print(f"    Size: {settings['size']}")
                        elif "decay" in param_name and "decay" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["decay"]
                            )
                            print(f"    Decay: {settings['decay']}")
                        elif "dry" in param_name and "dry_wet" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["dry_wet"]
                            )
                            print(f"    Dry/Wet: {settings['dry_wet']}")
                        elif "drive" in param_name and "drive" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["drive"]
                            )
                            print(f"    Drive: {settings['drive']}")
                        elif "feedback" in param_name and "feedback" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["feedback"]
                            )
                            print(f"    Feedback: {settings['feedback']}")
                        elif "time" in param_name and "time" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["time"]
                            )
                            print(f"    Time: {settings['time']}")
                        elif "rate" in param_name and "rate" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["rate"]
                            )
                            print(f"    Rate: {settings['rate']}")
                        elif "depth" in param_name and "depth" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["depth"]
                            )
                            print(f"    Depth: {settings['depth']}")
                        elif "amount" in param_name and "amount" in settings:
                            set_parameter(
                                track_idx, device_idx, param_idx, settings["amount"]
                            )
                            print(f"    Amount: {settings['amount']}")

                time.sleep(0.2)
                break

# =============================================================================
# COMPLETE
# =============================================================================
print("\n" + "=" * 70)
print("  DUB EFFECTS LOADED!")
print("=" * 70)
print("""
Effects added per track:

  Track 0 (Drums):     Compressor → EQ Eight → Phaser → Reverb
  Track 1 (Dub Bass):  Saturator → Auto Filter → Delay → Compressor
  Track 2 (Guitar):    Chorus → Delay → Reverb → EQ Eight  
  Track 3 (Organ):     Rotary* → Delay → Reverb → Overdrive
  Track 4 (Synth Pad): Chorus → Phaser → Delay → Reverb → Auto Filter
  Track 5 (FX):        Reverb → Delay → Phaser → Saturator

MIDI Effects:
  - Scale (C Minor) on Bass, Organ, Synth Pad
  - Arpeggiator on Synth Pad
  - Random on FX

* Rotary may not be available - will fallback to Chorus

Next steps:
  1. Fine-tune effect parameters in Ableton UI
  2. Set up send routing (A=Reverb, B=Delay)
  3. Run: python automate_2h_dub_reggae.py
""")
print("=" * 70)
