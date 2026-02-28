#!/usr/bin/env python3
"""Continue DJ evolution - Variations 65-80 - Deep Atmospheric Phase."""

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
    print(f"Connected to {TCP_HOST}:{TCP_PORT}")

    print("\n=== DEEP ATMOSPHERIC PHASE (Variations 65-80) ===")

    print("\n--- PULLBACK ---")

    # V65: Bass pulls back slightly
    print("V65: Bass pulls to 0.89...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.89})

    # V66: Lead goes deep
    print("V66: Lead deep 0.36...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.36})

    # V67: Hats soften
    print("V67: Hats soften 0.55...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.55})

    print("\n--- SPACE ---")

    # V68: More space
    print("V68: Bass space 0.87...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.87})

    # V69: Lead minimal
    print("V69: Lead minimal 0.32...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.32})

    # V70: Hats whisper
    print("V70: Hats whisper 0.52...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.52})

    # V71: Stabs rare change
    print("V71: Stabs drift to 0.43...")
    send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.43})

    print("\n--- REBUILD ---")

    # V72: Bass starts return
    print("V72: Bass returns 0.90...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.90})

    # V73: Lead grows
    print("V73: Lead grows 0.40...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.40})

    # V74: Hats rise
    print("V74: Hats rise 0.58...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.58})

    # V75: Bass stronger
    print("V75: Bass strong 0.93...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.93})

    print("\n--- PEAK ---")

    # V76: Lead peak
    print("V76: Lead peak 0.47...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.47})

    # V77: Hats bright
    print("V77: Hats bright 0.64...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.64})

    # V78: Bass max
    print("V78: Bass max 0.95...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})

    # V79: Lead max
    print("V79: Lead max 0.49...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.49})

    # V80: Resolution
    print("V80: Resolution - Bass 0.92, Lead 0.45, Hats 0.61...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.45})
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.61})

    sock.close()
    print("\n=== Deep atmospheric phase complete! Variation 80 ===")
    print("Ready for next evolution cycle...")


if __name__ == "__main__":
    main()
