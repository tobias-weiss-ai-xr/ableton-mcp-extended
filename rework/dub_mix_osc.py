#!/usr/bin/env python3
"""
OSC-Based Continuous Dub Mix Controller
Directly controls Ableton via OSC for reliable operation
"""

import time
import random
from pythonosc.udp_client import SimpleUDPSender, SimpleUDPClient

# Ableton OSC default ports (typically 8000 or 9000)
SERVER_ADDRESS = ("127.0.0.1", 8000)
CLIENT = SimpleUDPClient(*SERVER_ADDRESS)

OSC_MESSAGES = [
    ("/app/main/part", "/mks", "1038", "1", "1"),  # Play
    ("/app/main/part2", "/mks", "1038", "1", "1"),
    ("/app/main/part3", "/mks", "1038", "1", "1"),
    ("/app/main/part4", "/mks", "1038", "1", "1"),
]


def osc(msg):
    """Send OSC message"""
    try:
        CLIENT.send_message(msg)
    except:
        pass


def send_dub_element(params):
    """Send dub-specific OSC control"""
    try:
        addr, *args = params
        CLIENT.send_message((addr,) + tuple(map(str, args)))
        return True
    except:
        return False


def trigger_dub_sequence():
    """Trigger dub sequence"""
    for msg in OSC_MESSAGES:
        send_dub_element(msg)
        time.sleep(0.1)


def main_loop():
    """Run infinite dub mix"""
    print("=== OSC DUB MIX STARTED ===")
    print("Target: /127.0.0.1:8000")
    print("Press Ctrl+C to stop\n")

    i = 0
    while True:
        i += 1
        print("Dub Loop #%d" % i)

        # Try different ports
        for port in [8000, 8001, 8002, 9000, 9001]:
            test_addr = ("127.0.0.1", port)
            client = SimpleUDPClient(*test_addr)
            client.send_message(("/app/button", "/mks", "1037", "1", "1"))
            time.sleep(0.1)
            print("  -> Tested port %d" % port)

        # If Ableton is running, send continuous triggers
        try:
            osc(("/app/main/part", "/mks", "1037", "1", "1"))
        except:
            print("  No Ableton OSC response")

        # Wait and repeat
        time.sleep(60)  # 1 minute between sequences


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nDub mix stopped")
