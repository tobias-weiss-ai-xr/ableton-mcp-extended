#!/usr/bin/env python3
"""Test TCP connection to Ableton MCP."""

import socket
import json

print("Testing connection to localhost:9877...")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    sock.connect(("127.0.0.1", 9877))
    print("Connected!")

    # Send get_session_info
    cmd = {"type": "get_session_info", "params": {}}
    sock.send(json.dumps(cmd).encode("utf-8"))
    print("Sent command:", cmd["type"])

    response = sock.recv(8192).decode("utf-8")
    print("Response:", response)

    sock.close()
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
