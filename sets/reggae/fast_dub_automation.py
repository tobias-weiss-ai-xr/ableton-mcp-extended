#!/usr/bin/env python3
"""
Fast Dub Reggae Automation - BASS HEAVY + ACTIVE FX
====================================================

Features:
- Clip changes every 8-15 seconds
- FX triggers every 20-30 seconds
- Bass always prominent (35% of changes)
- Organ/Mallet reduced
- Press Ctrl+C to stop

Usage:
    python sets/reggae/fast_dub_automation.py
"""

import socket
import json
import time
import random
import signal
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

TCP_HOST = "localhost"
TCP_PORT = 9877

# Global state
running = True
start_time = 0
variation_count = 0


def send_cmd(cmd_type, params=None):
    """Send command to MCP server"""
    if params is None:
        params = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
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
    except Exception as e:
        return {"status": "error", "message": str(e)}


def fire(track, clip):
    """Fire a clip"""
    return send_cmd("fire_clip", {"track_index": track, "clip_index": clip})


def set_vol(track, vol):
    """Set track volume"""
    return send_cmd("set_track_volume", {"track_index": track, "volume": vol})


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n\n[STOP] Stopping automation...")
    running = False


def print_header():
    print("=" * 60)
    print("  FAST DUB REGGAE AUTOMATION")
    print("  BASS HEAVY + ACTIVE FX")
    print("=" * 60)
    print()
    print("  Mix Settings:")
    print("    Bass:   95% (MAXIMUM)")
    print("    Drums:  75%")
    print("    Guitar: 55%")
    print("    Organ:  40% (reduced mallet)")
    print("    Pad:    45%")
    print("    FX:     65% (active)")
    print()
    print("  Clip change: every 8-15 seconds")
    print("  FX trigger:  every 20-30 seconds")
    print()
    print("  Press Ctrl+C to stop")
    print("=" * 60)
    print()


def apply_bass_heavy_mix():
    """Set the bass-heavy mix"""
    print("[MIX] Applying bass-heavy mix...")
    set_vol(0, 0.75)  # Drums
    set_vol(1, 0.95)  # BASS - MAXIMUM
    set_vol(2, 0.55)  # Guitar
    set_vol(3, 0.40)  # Organ - reduced
    set_vol(4, 0.45)  # Pad
    set_vol(5, 0.65)  # FX - boosted
    print("[MIX] Bass at 95%, Organ at 40%")
    print()


def main():
    global running, start_time, variation_count

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print_header()

    # Apply mix
    apply_bass_heavy_mix()

    # Start playback
    print("[PLAYBACK] Starting...")
    send_cmd("start_playback")

    # Fire initial clips
    print("[INIT] Firing initial clips...")
    fire(0, 0)  # Drums - One Drop
    fire(1, 0)  # Bass - Drone C
    print("[INIT] Drums + Bass started")
    print()

    start_time = time.time()
    last_fx_time = 0

    print("[RUNNING] Automation active...")
    print()

    while running:
        # Wait 8-15 seconds between changes
        wait = random.randint(8, 15)
        time.sleep(wait)

        if not running:
            break

        elapsed = time.time() - start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)

        # Every 20-30 seconds, trigger FX
        if elapsed - last_fx_time > random.randint(20, 30):
            fx_clip = random.choice([0, 1, 2, 3, 4, 5])
            fire(5, fx_clip)
            print(f"[{mins:02d}:{secs:02d}] >>> FX C{fx_clip}!")
            last_fx_time = elapsed
            time.sleep(2)  # Let FX breathe

        # Pick track with bass-heavy weights
        # Bass gets 35% of all changes
        track_weights = [0.20, 0.35, 0.15, 0.10, 0.10, 0.10]
        track = random.choices([0, 1, 2, 3, 4, 5], weights=track_weights)[0]
        clip = random.randint(0, 7)

        variation_count += 1
        result = fire(track, clip)

        if result.get("status") == "success":
            print(f"[{mins:02d}:{secs:02d}] V{variation_count}: T{track}C{clip}")

            # Bass always LOUD
            if track == 1:
                bass_vol = random.uniform(0.90, 1.0)
                set_vol(1, bass_vol)
                print(f"           >> BASS BOOST: {bass_vol:.0%}")

    # Final summary
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print("  AUTOMATION STOPPED")
    print("=" * 60)
    print(f"  Total Variations: {variation_count}")
    print(f"  Total Time: {int(elapsed // 60)}:{int(elapsed % 60):02d}")
    print("=" * 60)


if __name__ == "__main__":
    main()
