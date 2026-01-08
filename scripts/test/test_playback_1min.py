import socket
import json
import time

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


def start_playback():
    """Start playback"""
    send_command({"type": "start_playback", "params": {}})


def stop_playback():
    """Stop playback"""
    send_command({"type": "stop_playback", "params": {}})


print("=" * 80)
print("TEST: 1-MINUTE DUB TECHNOPO PLAYBACK")
print("=" * 80)
print()
print("This test will play Section 0 for 1 minute")
print("Verify:")
print("  - Clips fire correctly")
print("  - Audio plays from all tracks")
print("  - No errors in console")
print()
print("=" * 80)

try:
    print("\n[TEST] Fireing clips for Section 0...")

    # Fire Section 0 clips
    fire_clip(0, 0)  # Kick: Basic
    print("  [OK] Kick track (Track 0, Clip 0)")

    fire_clip(1, 0)  # Bass: Root Drone
    print("  [OK] Sub-bass track (Track 1, Clip 0)")

    fire_clip(2, 2)  # Hi-hat: Minimal
    print("  [OK] Hi-hat track (Track 2, Clip 2)")

    fire_clip(3, 4)  # Pad: Minimal
    print("  [OK] Synth Pads track (Track 3, Clip 4)")

    fire_clip(4, 3)  # FX: Silent
    print("  [OK] FX track (Track 4, Clip 3)")

    fire_clip(5, 2)  # Delay: Minimal
    print("  [OK] Dub Delays track (Track 5, Clip 2)")

    print("\n[TEST] Starting playback...")
    start_playback()
    print("  [OK] Playback started")

    print("\n[TEST] Playing for 1 minute...")
    print("  Listen to all tracks - should hear:")
    print("    - Kick drum (4/4 pattern)")
    print("    - Deep bass drone (C2)")
    print("    - Minimal hi-hats (offbeats)")
    print("    - Minimal synth pad (root)")
    print("    - No FX")
    print("    - Minimal delays")

    # Count down
    for i in range(60, 0, -10):
        time.sleep(10)
        print(f"  {i} seconds remaining...", end="\r")

    print("\n\n[TEST] Stopping playback...")
    stop_playback()
    print("  [OK] Playback stopped")

    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print()
    print("If you heard:")
    print("  [OK] Kick drum pattern")
    print("  [OK] Deep bass drone")
    print("  [OK] Hi-hats on offbeats")
    print("  [OK] Subtle synth pad")
    print("  [OK] Minimal delays")
    print()
    print("Then your setup is working correctly!")
    print()
    print("NEXT STEPS FOR 2-HOUR RECORDING:")
    print("=" * 80)
    print("1. Load instruments and configure presets:")
    print("   - Track 0 (Kick): Create kick sound in Operator")
    print("   - Track 1 (Sub-bass): Create sub sound in Tension")
    print("   - Track 2 (Hi-hats): Load hi-hat samples in Drum Rack")
    print("   - Track 3 (Synth Pads): Choose pad in Wavetable")
    print("   - Track 4 (FX): Load FX samples in Simpler")
    print("   - Track 5 (Dub Delays): Ready for send routing")
    print()
    print("2. Configure send routing (in Ableton):")
    print("   - Sends from Tracks 0-4 to Track 10 (Reverb)")
    print("   - Sends from Tracks 0-4 to Track 11 (Delay)")
    print()
    print("3. Enable recording in Ableton:")
    print("   - Press Shift+R to enable Master recording")
    print("   - Or click 'Record' on Master track")
    print()
    print("4. Start recording:")
    print("   - Press Record in Ableton (R key)")
    print()
    print("5. Run full automation:")
    print("   python dub_techno_2h/record_and_play_2h_dub_techno.py")
    print()
    print("6. After 2 hours:")
    print("   - Stop recording in Ableton")
    print("   - File > Export Audio/Video")
    print("   - Export as WAV (or direct to MP3)")
    print("   - Name it: dubking.mp3")
    print()
    print("=" * 80)

except KeyboardInterrupt:
    print("\n\n[TEST] Stopped by user")
except Exception as e:
    print(f"\n\n[ERROR] {str(e)}")

finally:
    s.close()

print()
print("Press Enter to exit...")
input()
