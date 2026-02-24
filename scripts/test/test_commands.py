#!/usr/bin/env python3
import socket
import json


def test_command(cmd):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9877))
        sock.send(json.dumps({"type": cmd, "params": {}}).encode("utf-8"))
        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()
        print(f"{cmd}: {response.get('status', 'unknown')}")
    except Exception as e:
        print(f"{cmd}: ERROR - {e}")


# Test some commands to see which ones work
print("Testing available commands...")
test_command("get_session_info")
test_command("create_drum_pattern")
test_command("load_drum_kit")
print("\nDone!")
