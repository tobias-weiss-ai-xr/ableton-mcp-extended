#!/usr/bin/env python
"""
Utility to reload AbletonMCP Remote Script without requiring Ableton Live restart.

This script sends a reload command to the Remote Script which can:
1. Reload the script module in Ableton Live
2. Signal that new commands are available
3. Fix issues where Remote Script is out of sync

Usage:
    python scripts/util/reload_remote_script.py
"""

import socket
import json
import sys

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = "127.0.0.1"


def reload_remote_script():
    """Send reload command to Ableton Remote Script."""
    try:
        print("Connecting to AbletonMCP Remote Script...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((HOST, PORT))

        # Send reload command
        command = {"type": "reload_script"}
        s.sendall(json.dumps(command).encode("utf-8"))

        # Wait for confirmation
        response_data = s.recv(4096)
        response = json.loads(response_data.decode("utf-8"))
        s.close()

        if response.get("status") == "success":
            print("✅ Success: Remote Script reload command sent")
            print("\n⚠️  Please reload the Remote Script manually in Ableton Live:")
            print("   1. Go to: Preferences → Link/MIDI & MIDI Sync")
            print("   2. Find 'AbletonMCP' in the Control Surface list")
            print("   3. Select it, then click 'Reload'")
            print("\n💡 Alternative: Restart Ableton Live (faster, more reliable)")
        else:
            print(f"❌ Error: {response.get('message', 'Unknown error')}")
            return 1

    except socket.timeout:
        print("❌ Error: Connection timeout - is Ableton Live running?")
        print("   Make sure Ableton Live is open and Remote Script is loaded")
        return 1
    except ConnectionRefusedError:
        print("❌ Error: Connection refused - is AbletonMCP server running?")
        print("   Start the MCP server: python MCP_Server/server.py")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(reload_remote_script())
