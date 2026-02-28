#!/usr/bin/env python3
"""Get current session state."""

import socket
import json

TCP_HOST = "localhost"
TCP_PORT = 9877


def send_tcp(sock, command_type: str, params: dict = None) -> dict:
    message = {"type": command_type}
    if params:
        message["params"] = params
    sock.send(json.dumps(message).encode() + b"\n")
    response = sock.recv(8192).decode()
    return json.loads(response)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))

    # Get track info for all tracks
    for i in range(12):
        result = send_tcp(sock, "get_track_info", {"track_index": i})
        if result.get("status") == "success":
            track = result.get("result", {})
            name = track.get("name", f"Track {i}")
            volume = track.get("volume", "N/A")
            clips = track.get("clips", [])
            playing_clips = [
                j for j, c in enumerate(clips) if c.get("is_playing", False)
            ]
            print(f"Track {i} ({name}): Vol={volume}, Playing clips: {playing_clips}")

    sock.close()


if __name__ == "__main__":
    main()
