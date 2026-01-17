# -*- coding: utf-8 -*-

"""
Reload remote script utility for AbletonMCP.

This module provides a direct interface to reload the Remote Script
without requiring manual Ableton Live restart.
"""

import socket
import json
from typing import Dict, Any

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = "127.0.0.1"


def send_reload_command() -> Dict[str, Any]:
    """
    Send reload command to Ableton Remote Script.

    Returns:
        Dict with status and result/error message
    """
    try:
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

        return response
    except socket.timeout:
        return {
            "status": "error",
            "message": "Connection timeout - is Ableton Live running?",
        }
    except ConnectionRefusedError:
        return {
            "status": "error",
            "message": "Connection refused - is MCP server running?",
        }
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}


if __name__ == "__main__":
    result = send_reload_command()
    print(json.dumps(result, indent=2))
