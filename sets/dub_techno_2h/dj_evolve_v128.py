#!/usr/bin/env python3
"""Continue DJ evolution - Variations 113-128 - Final Push Phase."""

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

    print("\n=== FINAL PUSH PHASE (Variations 113-128) ===")

    print("\n--- CLIMB ---")

    # V113: Bass climbs
    print("V113: Bass climbs 0.94...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})

    # V114: Lead rises
    print("V114: Lead rises 0.46...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.46})

    # V115: Hats lift
    print("V115: Hats lift 0.63...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.63})

    # V116: Bass peak
    print("V116: Bass peak 0.95...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.95})

    print("\n--- APEX ---")

    # V117: Lead apex
    print("V117: Lead apex 0.48...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.48})

    # V118: Hats apex
    print("V118: Hats apex 0.65...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.65})

    # V119: Bass holds
    print("V119: Bass holds 0.94...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})

    # V120: Lead max
    print("V120: Lead max 0.49...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.49})

    print("\n--- CONTROLLED DESCENT ---")

    # V121: Bass eases
    print("V121: Bass eases 0.92...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})

    # V122: Lead settles
    print("V122: Lead settles 0.46...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.46})

    # V123: Hats relax
    print("V123: Hats relax 0.62...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.62})

    # V124: Stabs rare
    print("V124: Stabs to 0.44...")
    send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.44})

    print("\n--- STABLE GROOVE ---")

    # V125: Bass grooves
    print("V125: Bass grooves 0.91...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.91})

    # V126: Lead grooves
    print("V126: Lead grooves 0.44...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.44})

    # V127: Hats pocket
    print("V127: Hats pocket 0.60...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})

    # V128: Final state
    print("V128: FINAL - Bass 0.92, Lead 0.45, Hats 0.61...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.45})
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.61})

    # Final texture
    send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 0, "device_index": 0, "parameter_index": 2, "value": 0.48},
    )

    sock.close()
    print("\n=== Final push complete! Variation 128 ===")
    print("Mix ready for next cycle...")
    print("Bass: 0.92 | Lead: 0.45 | Hats: 0.61 | Stabs: 0.44")


if __name__ == "__main__":
    main()
