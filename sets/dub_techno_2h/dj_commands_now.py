#!/usr/bin/env python3
"""Execute DJ commands immediately."""

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
    response = sock.recv(8192).decode()
    return json.loads(response)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")

    # Execute the requested commands
    print("Setting master volume to 0.85...")
    result = send_tcp(sock, "set_master_volume", {"volume": 0.85})
    print(f"  Result: {result}")

    print("Firing clip track 4, clip 1...")
    result = send_tcp(sock, "fire_clip", {"track_index": 4, "clip_index": 1})
    print(f"  Result: {result}")

    print("Firing clip track 6, clip 0...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 0})
    print(f"  Result: {result}")

    print("Firing clip track 6, clip 4...")
    result = send_tcp(sock, "fire_clip", {"track_index": 6, "clip_index": 4})
    print(f"  Result: {result}")

    print("Firing clip track 1, clip 1...")
    result = send_tcp(sock, "fire_clip", {"track_index": 1, "clip_index": 1})
    print(f"  Result: {result}")

    sock.close()
    print("Done!")


if __name__ == "__main__":
    main()
