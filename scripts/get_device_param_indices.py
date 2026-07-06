#!/usr/bin/env python
<arg_value>Helper script: query device parameters for all instruments.
Returns device indices and parameter indices for filter, reverb, delay automation.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP

def get_device_parameter_indices(params):
    """Extract parameter indices for key automation targets."""
    critical = {}
    for idx, param in enumerate(params):
        if "frequency" in param["name"].lower() or "cutoff" in param["name"].lower():
            critical["filter"] = idx
        elif "resonance" in param["name"].lower():
            critical["resonance"] = idx
        elif "reverb" in param["name"].lower() or "wet" in param["name"].lower() and param.get("max_value", 0) > 1000:
            critical["reverb"] = idx
        elif "delay" in param["name"].lower() or "time" in param["name"].lower():
            critical["delay_time"] = idx
        elif "feedback" in param["name"].lower():
            critical["delay_feedback"] = idx
        elif "drive" in param["name"].lower() or "distortion" in param["name"].lower():
            critical["overdrive"] = idx
        elif "volume" in param["name"].lower() and idx > 0:
            critical["volume"] = idx
        elif "decay" in param["name"].lower() and "release" not in param["name"].lower():
            critical["decay"] = idx

    return critical

def main():
    """Query device parameters for Tracks 0-4 (MIDI tracks)."""

    print("Querying device parameters for Tracks 0-4...")

    client = MCPClientTCP()

    track_devices = {}

    for track_idx in range(5): # Drums (0), Bass (1), Pads (2), Percussion (3), Dub FX (4)
        print(f"\nTrack {track_idx}:")
        track_info = client.send_command("get_track_info", {"track_index": track_idx})

        if not track_info or len(track_info.get("devices", [])) == 0:
            print(f"  No devices loaded")
            continue

        for device_idx, device in enumerate(track_info["devices"]):
            print(f"  Device {device_idx}: {device['name']}")

            params = client.send_command("get_device_parameters", {
                "track_index": track_idx,
                "device_index": device_idx
            })

            if params:
                critical = get_device_parameter_indices(params)
                print(f"    Critical params: {critical}")

                track_devices[f"track_{track_idx}_device_{device_idx}"] = critical

    print("\n" + "="*60)
    print("Device Parameter Index Summary")
    print("="*60)

    for key, values in track_devices.items():
        print(f"\n{key}:")
        for param_name, param_idx in values.items():
            print(f"  {param_name}: parameter_index = {param_idx}")

    print("\nFor automation, use:\n")
    print("  set_device_parameter(track_index, device_index, parameter_index, value)")
    print("  or set_device_parameter_udp(...) for low-latency sweeps\n")

    return 0

if __name__ == "__main__":
    exit(main() or 0)