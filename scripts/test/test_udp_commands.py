#!/usr/bin/env python3
"""Quick UDP test for Ableton MCP"""

import socket
import json
import time
import sys

TCP_HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_HOST = "127.0.0.1"
UDP_PORT = 9878


def send_tcp(command_type, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    try:
        sock.connect((TCP_HOST, TCP_PORT))
        msg = json.dumps({"type": command_type, "params": params or {}})
        sock.sendall((msg + "\n").encode())
        response = sock.recv(8192).decode()
        return json.loads(response)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        sock.close()


def send_udp(command_type, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = json.dumps({"type": command_type, "params": params or {}})
    sock.sendto(msg.encode(), (UDP_HOST, UDP_PORT))
    sock.close()


print("=" * 50)
print("UDP COMMAND TEST")
print("=" * 50)

# Test 1: TCP connection
print("\n[1] Testing TCP connection...")
response = send_tcp("get_session_info")
if response.get("status") == "success":
    print(f"[OK] Connected to Ableton")
    print(f"    Tempo: {response['result']['tempo']} BPM")
    print(f"    Tracks: {response['result']['track_count']}")
else:
    print(f"[FAIL] TCP connection failed: {response}")
    sys.exit(1)

# Test 2: Send UDP volume commands
print("\n[2] Sending UDP volume commands...")
for i in range(5):
    vol = 0.5 + (i * 0.1)
    send_udp("set_track_volume", {"track_index": 0, "volume": vol})
    print(f"    Sent: set_track_volume(track=0, vol={vol:.2f})")
    time.sleep(0.1)

# Test 3: Send UDP parameter commands
print("\n[3] Sending UDP parameter commands...")
for i in range(5):
    val = 0.5 + (i * 0.1)
    send_udp(
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 2, "value": val},
    )
    print(f"    Sent: set_device_parameter(track=0, device=0, param=2, val={val:.2f})")
    time.sleep(0.1)

# Test 4: Verify via TCP that parameters changed
print("\n[4] Verifying changes via TCP...")
time.sleep(0.5)

# Get track info to see if volume changed
response = send_tcp("get_track_info", {"track_index": 0})
if response.get("status") == "success":
    track = response.get("result", {})
    print(f"    Track 0 volume: {track.get('volume', 'N/A')}")

print("\n" + "=" * 50)
print("UDP TEST COMPLETE")
print("=" * 50)
