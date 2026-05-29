"""
Test generate_melody_clip fix end-to-end.
Sets up basic session, tests the tool, verifies output.
"""
import socket
import json
import time
import sys

TCP_HOST = "localhost"
TCP_PORT = 9877

def tcp_command(cmd, params=None):
    """Send TCP command and return response."""
    if params is None:
        params = {}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((TCP_HOST, TCP_PORT))
        payload = json.dumps({"type": cmd, "params": params}).encode("utf-8")
        s.send(payload)
        response = json.loads(s.recv(102400).decode("utf-8"))
        s.close()
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_result_text(response):
    """Extract result text from response."""
    if isinstance(response, dict):
        return response.get("result", str(response))
    return str(response)

def is_error_result(response):
    """Check if response indicates an error."""
    if isinstance(response, dict):
        result = response.get("result", "")
        if isinstance(result, str) and "Error" in result:
            return True
        return response.get("status") == "error"
    return "Error" in str(response)

# =====================================================================
print("=" * 70)
print("TEST: generate_melody_clip fix")
print("=" * 70)

# Step 1: Create a MIDI track
print("\n[1] Creating MIDI track...")
resp = tcp_command("create_midi_track", {"index": 0})
print(f"  {get_result_text(resp)}")

# Step 2: Load a basic instrument
print("\n[2] Loading instrument...")
resp = tcp_command("load_instrument_or_effect", {
    "track_index": 0,
    "uri": "query:Synths#Instrument%20Rack:Bass:FileId_5116"
})
print(f"  {get_result_text(resp)}")
time.sleep(1)

# Step 3: Set key default to Fm (standard session)
print("\n[3] Setting tempo...")
resp = tcp_command("set_tempo", {"tempo": 126})
print(f"  {get_result_text(resp)}")

# =====================================================================
# Step 4: Test generate_melody_clip with various configurations
# =====================================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

test_cases = [
    # (track, clip, key, scale, length, complexity, range, description)
    (0, 0, "C", "minor", 8.0, "simple", (60, 84), "C minor, simple, default range"),
    (0, 1, "F", "minor", 8.0, "medium", (60, 84), "F minor, medium (was broken!)"),
    (0, 2, "F#", "dorian", 16.0, "medium", (55, 84), "F# dorian, medium"),
    (0, 3, "Am", "phrygian", 12.0, "complex", (60, 84), "Am phrygian, complex"),
    (0, 4, "G", "major", 8.0, "simple", (48, 72), "G major, simple, lower range"),
    (0, 5, "D", "pentatonic minor", 8.0, "medium", (60, 84), "D pentatonic minor"),
    (0, 6, "E", "blues", 8.0, "complex", (60, 84), "E blues"),
    (0, 7, "F", "lydian", 8.0, "simple", (72, 96), "F lydian, upper range"),
]

passed = 0
failed = 0

for track, clip, key, scale, length, complexity, rrange, desc in test_cases:
    print(f"\n  Test: {desc}")
    cmd = "generate_melody_clip"
    params = {
        "track_index": track,
        "clip_index": clip,
        "key": key,
        "scale": scale,
        "length_beats": length,
        "complexity": complexity,
        "range_notes": rrange,
    }
    
    print(f"    Sending: {cmd}({params})")
    resp = tcp_command(cmd, params)
    result = get_result_text(resp)
    
    # Check for success
    is_error = is_error_result(resp)
    
    if is_error:
        error_msg = result if isinstance(result, str) else json.dumps(result)
        print(f"    [FAIL] {error_msg[:200]}")
        failed += 1
    else:
        # Parse the JSON result to check note count
        try:
            result_str = result if isinstance(result, str) else json.dumps(result)
            data = json.loads(result_str)
            note_count = data.get("melody_notes", "?")
            print(f"    [OK] {note_count} notes generated")
            passed += 1
        except (json.JSONDecodeError, TypeError):
            print(f"    [OK] {result}")
            passed += 1

# =====================================================================
print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)

# =====================================================================
# Step 5: Verify notes exist by reading them back
# =====================================================================
print("\n[Final] Reading back notes from clip 0...")
resp = tcp_command("get_clip_notes", {
    "track_index": 0,
    "clip_index": 0,
    "from_time": 0.0,
    "from_pitch": 0,
})
result = get_result_text(resp)
try:
    data_dict = json.loads(result) if isinstance(result, str) else (result if isinstance(result, dict) else {})
    if isinstance(data_dict, dict):
        notes = data_dict.get("notes", [])
        print(f"  Clip 0 has {len(notes)} notes")
        if notes:
            pitches = [n.get("pitch") for n in notes[:5]]
            print(f"  First 5 pitches: {pitches}")
    else:
        print(f"  Response: {result[:200]}")
except Exception as e:
    print(f"  Could not read notes: {e}")

# Clean exit
sys.exit(0 if failed == 0 else 1)
