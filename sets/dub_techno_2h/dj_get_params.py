#!/usr/bin/env python3
"""Get device parameters for key tracks."""

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
    # Read larger response in chunks
    response = b""
    while True:
        chunk = sock.recv(32768)
        if not chunk:
            break
        response += chunk
        if b"\n" in chunk:
            break
    return json.loads(response.decode())


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}\n")

    # Get parameters for key tracks
    tracks_to_check = [0, 1, 4, 6, 7]

    for track_idx in tracks_to_check:
        print(f"=== Track {track_idx} Device 0 Parameters ===")
        result = send_tcp(
            sock, "get_device_parameters", {"track_index": track_idx, "device_index": 0}
        )
        if result.get("status") == "success":
            params = result.get("result", {}).get("parameters", [])
            for i, p in enumerate(params[:15]):  # First 15 params
                print(f"  [{i:2d}] {p.get('name', 'Unknown')}: {p.get('value', 'N/A')}")
        else:
            print(f"  Error: {result}")
        print()

    sock.close()


if __name__ == "__main__":
    main()
