#!/usr/bin/env python3
"""
Simple UDP Dub Mix Controller - Continuous Operation
"""

import socket
import time
import os

SERVER = ("127.0.0.1", 8000)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send(*args):
    """Send OSC-like message"""
    try:
        s.sendto("".join(map(str, args)).encode(), SERVER)
    except:
        pass


print("=== UDP DUB MIX ORCHESTRATOR ===")
print("Running forever... Ctrl+C to stop\n")

try:
    loop = 0
    while True:
        loop += 1
        print("DUB LOOP #%d at %s" % (loop, time.strftime("%H:%M:%S")))

        # Try all common OSC ports
        for port in [8000, 8001, 8002, 9000, 9001]:
            s.setblocking(False)
            try:
                s.sendto("/ping".encode(), ("127.0.0.1", port))
                print("  -> Tested port %d" % port)
            except:
                pass
            s.setblocking(True)

        # Send play trigger if Ableton found
        send("/app/main/part", "/mks", "1037", "1", "1")

        # Dub-specific effects
        send("/mix/track", "/fl", "0", "volume", 0.7)
        send("/mix/track", "/fl", "1", "volume", 0.6)
        send("/mix/track", "/fl", "2", "param", "0.5")
        send("/app/button", "/mks", "1037", "0.5", "1")

        # Wait 1 minute
        time.sleep(60)

except KeyboardInterrupt:
    s.close()
    print("\nDub mix stopped")
