#!/usr/bin/env python3
"""Continue DJ evolution - Variations 81-96 - Driving Techno Phase."""

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

    print("\n=== DRIVING TECHNO PHASE (Variations 81-96) ===")

    print("\n--- ENERGY BUILD ---")

    # V81: Bass drives
    print("V81: Bass drives 0.94...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})

    # V82: Lead pushes
    print("V82: Lead pushes 0.46...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.46})

    # V83: Hats energy
    print("V83: Hats energy 0.63...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.63})

    # V84: Bass peak
    print("V84: Bass peak 0.95...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})

    print("\n--- SUSTAIN ---")

    # V85: Lead holds
    print("V85: Lead holds 0.47...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.47})

    # V86: Hats sustain
    print("V86: Hats sustain 0.64...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.64})

    # V87: Bass sustained
    print("V87: Bass sustained 0.94...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})

    # V88: Lead max
    print("V88: Lead max 0.49...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.49})

    print("\n--- RELEASE ---")

    # V89: Slight release
    print("V89: Bass release 0.91...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.91})

    # V90: Lead breathes
    print("V90: Lead breathes 0.43...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.43})

    # V91: Hats relax
    print("V91: Hats relax 0.60...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})

    # V92: Stabs rare
    print("V92: Stabs to 0.45...")
    send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.45})

    print("\n--- GROOVE ---")

    # V93: Bass groove
    print("V93: Bass groove 0.93...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.93})

    # V94: Lead groove
    print("V94: Lead groove 0.44...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.44})

    # V95: Hats pocket
    print("V95: Hats pocket 0.61...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.61})

    # V96: Final state
    print("V96: Final - Bass 0.92, Lead 0.45, Hats 0.62...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.45})
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.62})

    # Texture
    print("V96b: Texture sweep...")
    send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 2, "value": 0.50},
    )

    sock.close()
    print("\n=== Driving techno phase complete! Variation 96 ===")
    print("Mix: Bass 0.92 | Lead 0.45 | Hats 0.62 | Stabs 0.45")


if __name__ == "__main__":
    main()
