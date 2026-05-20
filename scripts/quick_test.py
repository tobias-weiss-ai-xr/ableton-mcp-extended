#!/usr/bin/env python3
"""
Quick diagnostic to check Ableton session state.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import MCPClientTCP

print("Connecting to Ableton...")
client = MCPClientTCP()

# Get session info
print("\n1. Session Info:")
session = client.send_command("get_session_info", {})
if 'result' in session:
    result = session['result']
    print(f"  Tempo: {result.get('tempo')} BPM")
    print(f"  Time Signature: {result.get('time_signature')}")

# Get track count
print("\n2. All Tracks:")
all_tracks = client.send_command("get_all_tracks", {})
print(f"  Raw response: {all_tracks}")
print(f"  Type: {type(all_tracks)}")

# Get first track info
print("\n3. Track 0 Info:")
try:
    track_0 = client.send_command("get_track_info", {"track_index": 0})
    print(f"  Raw response: {track_0}")
    print(f"  Type: {type(track_0)}")
except Exception as e:
    print(f"  Error: {e}")

# Get track 1 info
print("\n4. Track 1 Info:")
try:
    track_1 = client.send_command("get_track_info", {"track_index": 1})
    print(f"  Raw response: {track_1}")
    print(f"  Type: {type(track_1)}")
except Exception as e:
    print(f"  Error: {e}")

# Test synthesize function
print("\n5. Test Setup:")
try:
    import session_setup
    print("  session_setup module imported OK")
    if hasattr(session_setup, 'create_dub_techno_session'):
        print("  create_dub_techno_session function found")
    if hasattr(session_setup, 'setup_tracks'):
        print("  setup_tracks function found")
except Exception as e:
    print(f"  Import error: {e}")

print("\nDone.")