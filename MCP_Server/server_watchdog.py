#!/usr/bin/env python3
"""
Server Watchdog for Ableton MCP

Automatically restarts the MCP server if it crashes or becomes unresponsive.
Monitors TCP port 9877 availability and restarts on failure.
"""

import subprocess
import sys
import time
import socket
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("server_watchdog.log"), logging.StreamHandler()],
)
logger = logging.getLogger("AbletonMCP_Watchdog")

# Configuration
SERVER_SCRIPT = "MCP_Server/server.py"
MAX_RESTART_DELAY = 30  # Maximum delay between restarts (seconds)
MIN_RESTART_DELAY = 5  # Minimum delay between restarts (seconds)
DEFAULT_RESTART_DELAY = 10  # Default delay between restarts (seconds)
HEALTHCHECK_INTERVAL = 60  # Seconds between health checks

# Track restarts for exponential backoff
restart_count = 0
last_restart_time = None


def is_server_running(host="127.0.0.1", port=9877, timeout=2.0):
    """Check if the MCP server is running by attempting to connect."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.debug(f"Server check failed: {e}")
        return False


def restart_server(server_script):
    """Restart the MCP server process."""
    global restart_count, last_restart_time

    logger.info("Restarting MCP server...")
    try:
        # Launch server in background
        process = subprocess.Popen(
            [sys.executable, server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
            if sys.platform == "win32"
            else 0,
        )
        restart_count += 1
        last_restart_time = datetime.now()
        logger.info(f"MCP server restarted (attempt #{restart_count})")
        return process
    except Exception as e:
        logger.error(f"Failed to restart server: {e}")
        return None


def calculate_restart_delay():
    """Calculate restart delay with exponential backoff."""
    global restart_count

    # Exponential backoff: 5s, 10s, 20s, 30s, 30s...
    base_delay = MIN_RESTART_DELAY
    multiplier = min(2 ** (restart_count - 1), MAX_RESTART_DELAY // MIN_RESTART_DELAY)
    delay = min(base_delay * multiplier, MAX_RESTART_DELAY)

    return delay


def send_health_report(server_script):
    """Send a health report via MCP server."""
    try:
        import socket
        import json

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect(("127.0.0.1", 9877))

        command = {"type": "get_session_info", "params": {}}
        sock.send(json.dumps(command).encode("utf-8"))

        response = b""
        while True:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                response += chunk
                try:
                    json.loads(response.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    continue
            except socket.timeout:
                break

        sock.close()

        result = json.loads(response.decode("utf-8"))
        if result.get("status") == "success":
            logger.info(
                f"Server health OK - Session: {result.get('result', {}).get('track_count', 0)} tracks"
            )
            return True
        else:
            logger.warning("Server returned error status")
            return False

    except Exception as e:
        logger.debug(f"Health report failed: {e}")
        return False


def main():
    """Main watchdog loop."""
    global restart_count

    logger.info("=" * 60)
    logger.info("AbletonMCP Watchdog Started")
    logger.info("=" * 60)

    # Start the server
    server_process = restart_server(SERVER_SCRIPT)

    if server_process is None:
        logger.error("Failed to start server. Exiting.")
        sys.exit(1)

    # Main monitoring loop
    last_healthcheck = time.time()

    try:
        while True:
            time.sleep(HEALTHCHECK_INTERVAL)

            # Check if server process is still running
            if server_process is not None and server_process.poll() is not None:
                # Process has exited - restart
                logger.warning(f"Server process exited (code: {server_process.poll()})")
                server_process = None

            # Check if server is responding to connections
            if not is_server_running():
                logger.warning("Server is not responding on port 9877")

                if server_process is None or server_process.poll() is not None:
                    # Process has died or isn't running
                    server_process = restart_server(SERVER_SCRIPT)
                    if server_process is None:
                        delay = 30
                        logger.error(f"Failed to restart server, retry in {delay}s")
                        time.sleep(delay)
                    else:
                        delay = MIN_RESTART_DELAY
                        logger.info(f"Server restarted, waiting {delay}s for startup")
                        time.sleep(delay)
                else:
                    # Process exists but not responding - wait brief then restart
                    logger.warning("Server process exists but not responding")
                    time.sleep(2)
                    server_process.terminate()
                    time.sleep(1)
                    server_process = restart_server(SERVER_SCRIPT)

            # Periodic health check
            if time.time() - last_healthcheck > HEALTHCHECK_INTERVAL * 2:
                if send_health_report(SERVER_SCRIPT):
                    last_healthcheck = time.time()

    except KeyboardInterrupt:
        logger.info("Watchdog interrupted by user")
        if server_process is not None:
            try:
                server_process.terminate()
                logger.info("Server process terminated")
            except Exception:
                pass

    logger.info("Watchdog stopped")


if __name__ == "__main__":
    main()
