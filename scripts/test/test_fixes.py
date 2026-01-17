#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for verifying fixes:
1. get_session_overview works
2. get_clip_notes has better error handling
3. get_device_parameters has better error handling
"""

import socket
import json
import sys

HOST = "127.0.0.1"
PORT = 9877


def send_command(cmd_type, params=None):
    """Send a command to Ableton and get response"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30.0)

    try:
        sock.connect((HOST, PORT))
        command = {"type": cmd_type, "params": params or {}}
        sock.sendall(json.dumps(command).encode("utf-8"))

        # Receive response
        data = b""
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
            try:
                json.loads(data.decode("utf-8"))
                break
            except json.JSONDecodeError:
                continue

        sock.close()
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        sock.close()
        raise Exception(f"Failed to send command: {str(e)}")


def test_get_session_overview():
    """Test the new get_session_overview command"""
    print("=" * 70)
    print("Test: get_session_overview")
    print("=" * 70)
    print()

    try:
        result = send_command("get_session_overview")

        print("[PASS] Command executed successfully")
        print()
        print("Response:")
        print(json.dumps(result, indent=2))
        print()
        return True
    except Exception as e:
        print(f"[FAIL] Command failed: {str(e)}")
        print()
        return False


def test_get_clip_notes(track_index=0, clip_index=0):
    """Test get_clip_notes with improved error handling"""
    print("=" * 70)
    print(f"Test: get_clip_notes (track={track_index}, clip={clip_index})")
    print("=" * 70)
    print()

    try:
        result = send_command(
            "get_clip_notes", {"track_index": track_index, "clip_index": clip_index}
        )

        print("[PASS] Command executed successfully")
        print()
        print(f"Notes retrieved: {result.get('count', 0)}")
        print()
        return True
    except Exception as e:
        print(f"[FAIL] Command failed: {str(e)}")
        print()
        return False


def test_get_device_parameters(track_index=0, device_index=0):
    """Test get_device_parameters with improved error handling"""
    print("=" * 70)
    print(f"Test: get_device_parameters (track={track_index}, device={device_index})")
    print("=" * 70)
    print()

    try:
        result = send_command(
            "get_device_parameters",
            {"track_index": track_index, "device_index": device_index},
        )

        print("[PASS] Command executed successfully")
        print()
        print(f"Device: {result.get('device_name', 'Unknown')}")
        print(f"Parameters retrieved: {len(result.get('parameters', []))}")
        print()
        return True
    except Exception as e:
        print(f"[FAIL] Command failed: {str(e)}")
        print()
        return False


if __name__ == "__main__":
    results = []

    # Test 1: get_session_overview
    results.append(test_get_session_overview())

    # Wait a moment
    import time

    time.sleep(1.0)

    # Test 2: get_clip_notes (basic test)
    print()
    print(
        "Note: get_clip_notes may still fail for empty clips or older Ableton versions"
    )
    print()
    results.append(test_get_clip_notes())

    # Wait a moment
    time.sleep(1.0)

    # Test 3: get_device_parameters (basic test)
    results.append(test_get_device_parameters())

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")
    print()

    if passed == total:
        print("[SUCCESS] All tests passed!")
        print()
        print("Fixes applied:")
        print("  1. Added get_session_overview command")
        print("  2. Improved get_clip_notes error handling (Live 11+ compatibility)")
        print(
            "  3. Improved get_device_parameters error handling (check for empty parameters)"
        )
        print()
        sys.exit(0)
    else:
        print("[WARNING] Some tests failed")
        print()
        print("Check:")
        print("  - Ableton Live is running")
        print("  - AbletonMCP Remote Script is loaded")
        print("  - MCP server is running")
        print()
        sys.exit(1)
