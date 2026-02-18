import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    return json.loads(data.decode("utf-8"))


def get_track_count():
    result = send_command("get_session_info")
    return result["result"]["track_count"]


print("=" * 80)
print("FIXING MISSING TRACKS")
print("=" * 80)

# Create missing "Dub Delays" audio track
print("\nCreating Dub Delays audio track...")
send_command("create_audio_track", {"index": -1})
new_count = get_track_count()
delay_track = new_count - 1
send_command("set_track_name", {"track_index": delay_track, "name": "Dub Delays"})
print(f"   [OK] Created Dub Delays at Track {delay_track}")

time.sleep(0.5)

# Create missing "Reverb Send" audio track (it should go before Delay Send)
print("\nCreating Reverb Send audio track...")
send_command("create_audio_track", {"index": -1})
new_count = get_track_count()
reverb_track = new_count - 1
send_command("set_track_name", {"track_index": reverb_track, "name": "Reverb Send"})
print(f"   [OK] Created Reverb Send at Track {reverb_track}")

print("\n" + "=" * 80)
print("TRACK CREATION COMPLETE")
print("=" * 80)
print(f"\nTotal tracks now: {get_track_count()}")
print("\nExpected tracks:")
print("  - Track 4: Kick")
print("  - Track 5: Snare")
print("  - Track 6: Hi-hats")
print("  - Track 7: Dub Bass")
print("  - Track 8: Guitar Chop")
print("  - Track 9: Organ Bubble")
print("  - Track 10: FX")
print("  - Track 11: Dub Delays")
print("  - Track 12: Reverb Send")
print("  - Track 13: Delay Send")

print("\nAll tracks created. Ready for automation!")
s.close()
