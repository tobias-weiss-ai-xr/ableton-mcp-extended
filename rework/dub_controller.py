#!/usr/bin/env python3
"""
Dub Mix - Direct OSC Controller for Ableton Live
"""

import socket
import time
import threading
import random


class DubController:
    def __init__(self, host="127.0.0.1", port=8000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.running = False

    def osc_send(self, address, values):
        """Send OSC message"""
        try:
            msg = f"{address}\0"
            for v in values:
                if isinstance(v, int):
                    msg += struct.pack(">i", v)
                elif isinstance(v, float):
                    msg += struct.pack(">f", v)
                else:
                    msg += str(v)
                msg += "\0" * (4 - len(str(v)) % 4 if len(str(v)) % 4 else 0)
            self.sock.sendto(msg.encode("utf-8"), (self.host, self.port))
        except:
            pass

    def trigger_scene(self, scene_num):
        """Trigger a scene by number"""
        self.osc_send("/app/main/part", [scene_num + 1, 1, 1])

    def fire_clip(self, track, clip):
        """Fire a clip"""
        self.osc_send("/app/main/part", [track * 10 + clip + 1, 1, 1])

    def set_send_amount(self, track, send, amount):
        """Set send amount"""
        self.osc_send("/mix/track", [track, "send", send, amount])

    def set_volume(self, track, volume):
        """Set track volume"""
        self.osc_send("/mix/track", [track, "volume", volume])

    def start(self):
        """Start continuous dub mode"""
        self.running = True
        print("=== DUB MIX CONTROLLER STARTED ===")
        print(f"Target: {self.host}:{self.port}")

        loop = 0
        while self.running:
            loop += 1
            print(f"\n[Dub Loop {loop} - {time.strftime('%H:%M:%S')}]")

            # Trigger scene transitions
            print("  -> Triggering scenes...")
            for s in range(8):
                self.trigger_scene(s)
                print(f"     Scene {s}")
                time.sleep(4)

            # Apply dub effects
            print("  -> Effects...")
            self.set_send_amount(0, 0, 0.7)
            self.set_send_amount(1, 0, 0.6)
            self.set_volume(2, 0.8)
            time.sleep(4)

            # Continue indefinitely
            time.sleep(10)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    import struct

    controller = DubController()
    try:
        controller.start()
    except KeyboardInterrupt:
        print("\nDub mix stopped")
