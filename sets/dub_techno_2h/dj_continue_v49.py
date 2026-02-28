#!/usr/bin/env python3
"""Continue DJ evolution - Variations 33-48."""

import socket
import json
import random
import time

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

    print("\n=== Continuing mix evolution (Variations 33-48) ===")

    # Build phase - slowly increase energy
    print("\n--- BUILD PHASE ---")

    # V33: Push bass forward
    print("V33: Bass push to 0.94...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})
    print(f"  Result: {result}")

    # V34: Lead creeps up (still under 0.5)
    print("V34: Lead rise to 0.46...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.46})
    print(f"  Result: {result}")

    # V35: Hats texture
    print("V35: Hats at 0.62...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.62})
    print(f"  Result: {result}")

    # V36: Bass peak
    print("V36: Bass at peak 0.95...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})
    print(f"  Result: {result}")

    # V37: Lead almost max
    print("V37: Lead near max 0.49...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.49})
    print(f"  Result: {result}")

    print("\n--- DROP PHASE ---")

    # V38: Slight pullback for tension
    print("V38: Bass tension drop to 0.88...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.88})
    print(f"  Result: {result}")

    # V39: Lead backs off
    print("V39: Lead back to 0.42...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.42})
    print(f"  Result: {result}")

    # V40: Hats subtle
    print("V40: Hats subtle 0.58...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.58})
    print(f"  Result: {result}")

    # V41: Stabs finally change (rare)
    print("V41: Stabs shift to 0.44 (rare change)...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.44})
    print(f"  Result: {result}")

    print("\n--- RETURN PHASE ---")

    # V42: Bass returns strong
    print("V42: Bass returns to 0.92...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    print(f"  Result: {result}")

    # V43: Lead creeps back
    print("V43: Lead returns to 0.45...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.45})
    print(f"  Result: {result}")

    # V44: Hats groove
    print("V44: Hats groove 0.60...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})
    print(f"  Result: {result}")

    # V45: Bass holds
    print("V45: Bass holding 0.93...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.93})
    print(f"  Result: {result}")

    # V46: Filter sweep texture
    print("V46: Filter texture adjustment...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 3, "value": 0.35},
    )
    print(f"  Result: {result}")

    # V47: Pad space
    print("V47: Pad space adjustment...")
    result = send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 2, "device_index": 0, "parameter_index": 8, "value": 0.45},
    )
    print(f"  Result: {result}")

    # V48: Final state for this cycle
    print("V48: Final - Bass 0.94, Lead 0.47, Hats 0.61...")
    result = send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})
    result = send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.47})
    result = send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.61})

    sock.close()
    print("\n=== Evolution cycle complete! Variation 48 ===")
    print("Ready for next evolution...")


if __name__ == "__main__":
    main()
