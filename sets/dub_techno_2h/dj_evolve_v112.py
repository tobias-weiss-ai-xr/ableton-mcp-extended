#!/usr/bin/env python3
"""Continue DJ evolution - Variations 97-112 - Deep Dub Journey."""

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

    print("\n=== DEEP DUB JOURNEY (Variations 97-112) ===")

    print("\n--- DUB DESCENT ---")

    # V97: Bass deepens
    print("V97: Bass deepens 0.90...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.90})

    # V98: Lead subsides
    print("V98: Lead subsides 0.40...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.40})

    # V99: Hats mellow
    print("V99: Hats mellow 0.58...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.58})

    # V100: Milestone - deep dub
    print("V100: MILESTONE - Bass 0.88, Lead 0.38, Hats 0.56...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.88})
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.38})
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.56})

    print("\n--- ECHO CHAMBER ---")

    # V101: Bass echoes
    print("V101: Bass echoes 0.86...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.86})

    # V102: Lead minimal
    print("V102: Lead minimal 0.35...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.35})

    # V103: Hats distant
    print("V103: Hats distant 0.54...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.54})

    # V104: Stabs rare
    print("V104: Stabs to 0.42...")
    send_tcp(sock, "set_track_volume", {"track_index": 4, "volume": 0.42})

    print("\n--- RESURGENCE ---")

    # V105: Bass returns
    print("V105: Bass returns 0.89...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.89})

    # V106: Lead emerges
    print("V106: Lead emerges 0.42...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.42})

    # V107: Hats brighten
    print("V107: Hats brighten 0.59...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.59})

    # V108: Bass stronger
    print("V108: Bass stronger 0.92...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.92})

    print("\n--- DUB PEAK ---")

    # V109: Lead rises
    print("V109: Lead rises 0.46...")
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.46})

    # V110: Hats groove
    print("V110: Hats groove 0.62...")
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.62})

    # V111: Bass peak
    print("V111: Bass peak 0.94...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.94})

    # V112: Resolution
    print("V112: Resolution - Bass 0.93, Lead 0.44, Hats 0.60...")
    send_tcp(sock, "set_track_volume", {"track_index": 1, "volume": 0.93})
    send_tcp(sock, "set_track_volume", {"track_index": 3, "volume": 0.44})
    send_tcp(sock, "set_track_volume", {"track_index": 2, "volume": 0.60})

    # Texture adjustment
    send_tcp(
        sock,
        "set_device_parameter",
        {"track_index": 1, "device_index": 0, "parameter_index": 10, "value": 0.52},
    )

    sock.close()
    print("\n=== Deep dub journey complete! Variation 112 ===")
    print("Mix: Bass 0.93 | Lead 0.44 | Hats 0.60 | Stabs 0.42")


if __name__ == "__main__":
    main()
