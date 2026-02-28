#!/usr/bin/env python3
"""
Direct OSC test for AbletonOSC
Tests connection to common AbletonOSC ports
"""

import socket
import struct

import time


# Test packet builder
def build_osc_message(address, *args):
    """Build a proper OSC message"""
    # OSC address pattern (null-padded to 4-byte boundary)
    addr = address.encode("utf-8")
    addr += b"\x00" * ((4 - len(addr) % 4) or 0)

    # Type tag string
    types = b","  # comma indicates all arguments are floats
    for _ in args:
        types += b"f"
    types += b"\x00" * ((4 - len(types) % 4) or 0)

    # Arguments
    msg = addr + types
    for arg in args:
        msg += struct.pack(">f", float(arg))

    return msg


# Test different ports
ports_to_try = [8000, 9000, 8553, 8001, 9001]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for port in ports_to_try:
    try:
        # Send a ping message to /live/osc/server
        msg = build_osc_message("/live/osc/server")
        sock.sendto(msg, ("127.0.0.1", port))
        print(f"Sent OSC ping to port {port}")

        # Wait briefly for response
        time.sleep(0.5)

        # Try non-blocking receive
        sock.setblocking(False)
        try:
            data, addr = sock.recvfrom(1024)
            print(f"  Response from {addr}: {data}")
        except BlockingIOError:
            print(f"  No response from port {port}")
        sock.setblocking(True)

    except Exception as e:
        print(f"  Error on port {port}: {e}")

# Try /session/tempo
for port in ports_to_try:
    try:
        msg = build_osc_message("/session/tempo")
        sock.sendto(msg, ("127.0.0.1", port))
        print(f"Sent /session/tempo to port {port}")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone testing OSC ports.")
