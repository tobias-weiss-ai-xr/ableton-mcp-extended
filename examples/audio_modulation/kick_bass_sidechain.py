#!/usr/bin/env python3
"""
Kick → Bass Sidechain Example
-----------------------------

Classic electronica sidechaining: kick triggers duck bass volume.

Usage:
  python kick_bass_sidechain.py
"""

import socket
import json

# Configuration
TCP_PORT = 9877
HOST = "localhost"
KICK_TRACK = 3  # Source: Kick drum track
BASS_TRACK = 1  # Target: Bass track
UTILITY_DEVICE = 0  # Utility (for volume control)
VOLUME_PARAM = 6  # Utility Volume parameter
DUCK_AMOUNT = 0.8  # How much to duck (0.0-1.0)


def tcp_command(cmd_type: str, params: dict) -> dict:
    """Send command via TCP and return response."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((HOST, TCP_PORT))

        cmd = {"type": cmd_type, "params": params}
        sock.send(json.dumps(cmd).encode("utf-8"))
        response = sock.recv(8192).decode("utf-8")
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}
    finally:
        if sock:
            sock.close()


def main():
    print("🔄 Kick → Bass Sidechain Example")
    print("⭐ Classic pumping bass effect")
    print("🎛️  Track 3 (kick) triggers → Track 1 (bass) ducking\n")

    # Setup: ensure Utility device is on bass track
    # Verify bass track exists
    bass_info = tcp_command("get_track_info", {"track_index": BASS_TRACK})
    if "error" in bass_info:
        print(f"❌ Bass track ({BASS_TRACK}) not available")
        return False

    # Verify Utility device (or load if missing)
    utility_present = False
    if "devices" in bass_info:
        for device in bass_info["devices"]:
            if "Utility" in device.get("name", ""):
                utility_present = True
                print(f"✅ Found Utility device on bass track")
                break

    if not utility_present:
        print("ℹ️  Loading Utility device on bass track...")
        load_result = tcp_command(
            "load_instrument_or_effect",
            {"track_index": BASS_TRACK, "uri": "query:Audio/Effects#Utility"},
        )
        if "error" in load_result:
            print(f"❌ Failed to load Utility: {load_result['error']}")
            return False
        print("✅ Utility device loaded")

    # Create Sidechain Modulator
    print("🔁 Creating sidechain modulator...")
    sc_result = tcp_command(
        "create_sidechain_modulator",
        {
            "track_index": BASS_TRACK,
            "device_index": UTILITY_DEVICE,
            "parameter_index": VOLUME_PARAM,  # Volume parameter
            "source_track_index": KICK_TRACK,  # Source = kick track
            "amount": DUCK_AMOUNT,  # 80% duck
        },
    )

    if "modulator_id" in sc_result:
        mod_id = sc_result["modulator_id"]
        print(f"✅ Sidechain created (ID: {mod_id}) 🎉")
        print(f"📊 Parameters:")
        print(f"   • Source: Track {KICK_TRACK} (kick)")
        print(f"   • Target: Track {BASS_TRACK} (bass)")
        print(f"   • Duck Amount: {DUCK_AMOUNT * 100}% volume reduction")
        print(f"   • Active: ON")
        print("\n🎧 Listen to the bass pump when kick plays! ")
        print("Kick → Bass volume ducks → Music swells fill space")
        print("\n🔊 Pro tip: adjust DUCK_AMOUNT (0.1–0.95) for different styles")
        print("0.7+ = classic house, 0.95 = aggressive EDM, 0.3 = subtle groove")
    else:
        print(
            f"❌ Sidechain creation failed: {sc_result.get('error', 'Unknown error')}"
        )
        return False

    return True


if __name__ == "__main__":
    main()
