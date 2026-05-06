#!/usr/bin/env python3
"""Aggressive connection attempt with various socket options."""

import socket
import json
import time


def try_connection():
    print("Attempting connection with various options...")

    # Try 1: Standard connection
    print("\n1. Standard TCP connection:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("127.0.0.1", 9877))
        print("   SUCCESS!")
        sock.send(b'{"type":"get_session_info","params":{}}')
        print("   Response:", sock.recv(8192).decode())
        sock.close()
        return True
    except Exception as e:
        print(f"   FAILED: {e}")

    # Try 2: With SO_REUSEADDR
    print("\n2. With SO_REUSEADDR:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(2)
        sock.connect(("127.0.0.1", 9877))
        print("   SUCCESS!")
        sock.close()
        return True
    except Exception as e:
        print(f"   FAILED: {e}")

    # Try 3: With linger
    print("\n3. With SO_LINGER:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_LINGER, b"\x01\x00\x00\x00\x00\x00\x00\x00"
        )
        sock.settimeout(2)
        sock.connect(("127.0.0.1", 9877))
        print("   SUCCESS!")
        sock.close()
        return True
    except Exception as e:
        print(f"   FAILED: {e}")

    # Try 4: Non-blocking then select
    print("\n4. Non-blocking with timeout:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        try:
            sock.connect(("127.0.0.1", 9877))
        except BlockingIOError:
            pass
        import select

        ready = select.select([], [sock], [], 2)
        if ready[1]:
            print("   SUCCESS!")
            sock.setblocking(True)
            sock.send(b'{"type":"get_session_info","params":{}}')
            print("   Response:", sock.recv(8192).decode())
            sock.close()
            return True
        else:
            print("   FAILED: Timeout")
    except Exception as e:
        print(f"   FAILED: {e}")

    # Try 5: Different host
    print("\n5. Using 'localhost' instead of 127.0.0.1:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("localhost", 9877))
        print("   SUCCESS!")
        sock.close()
        return True
    except Exception as e:
        print(f"   FAILED: {e}")

    return False


if __name__ == "__main__":
    success = try_connection()
    print(f"\nFinal result: {'SUCCESS' if success else 'ALL ATTEMPTS FAILED'}")
    print("\nThe Remote Script's TCP server appears to be in a zombie state.")
    print("You need to reload the Remote Script in Ableton:")
    print("  1. Preferences > Link, Tempo & MIDI")
    print("  2. Change Control Surface to 'None'")
    print("  3. Change back to 'AbletonMCP'")
