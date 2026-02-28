#!/usr/bin/env python3
"""Get device parameters for key tracks - simple version."""

import socket
import json

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
    """Send command via TCP and wait for response."""
    message = {"type": command_type}
    if params:
        message["params"] = params

    sock.send(json.dumps(message).encode() + b"\n")
    sock.settimeout(5.0)
    response = sock.recv(65536)
    return json.loads(response.decode())


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}\n")

    # Get parameters for track 0 (drums)
    print("=== Track 0 (Drums) Device 0 Parameters ===")
    result = send_tcp(
        sock, "get_device_parameters", {"track_index": 0, "device_index": 0}
    )
    if result.get("status") == "success":
        params = result.get("result", {}).get("parameters", [])
        for i, p in enumerate(params[:12]):  # First 12 params
            print(f"  [{i:2d}] {p.get('name', 'Unknown')}: {p.get('value', 'N/A')}")
    else:
        print(f"  Error: {result}")

    sock.close()


if __name__ == "__main__":
    main()
