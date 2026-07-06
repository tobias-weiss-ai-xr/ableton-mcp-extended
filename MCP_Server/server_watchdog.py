#!/usr/bin/env python3
"""
Server Watchdog for Ableton MCP

Automatically restarts the MCP server if it crashes or becomes unresponsive.
Monitors TCP port 9877 availability and connection_health state.
Triggers restart if connection state is "disconnected" for > 30s.

Logs all reconnection attempts to MCP_Server/logs/connection.log.
"""

import os
import subprocess
import sys
import time
import socket
import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

# Configure connection.log (separate from main watchdog log)
_CONNECTION_LOG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "logs"
)
_CONNECTION_LOG_PATH = os.path.join(_CONNECTION_LOG_DIR, "connection.log")

os.makedirs(_CONNECTION_LOG_DIR, exist_ok=True)

_connection_logger = logging.getLogger("AbletonMCP_ConnectionLog")
_connection_logger.setLevel(logging.INFO)
_connection_handler = RotatingFileHandler(
    _CONNECTION_LOG_PATH, maxBytes=1024 * 1024, backupCount=3
)
_connection_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
_connection_logger.addHandler(_connection_handler)
# Prevent propagation to root logger (avoids duplicate logs)
_connection_logger.propagate = False


def log_connection_event(message: str) -> None:
    """Write a reconnection or restart event to connection.log with ISO timestamp."""
    _connection_logger.info(message)


# Configure main watchdog logging
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
HEALTHCHECK_INTERVAL = 5  # Seconds between health checks (reduced for faster failure detection)
WATCHDOG_DISCONNECT_TIMEOUT = 30  # Seconds in DISCONNECTED state before restart

# Track restarts
restart_count = 0
last_restart_time: datetime | None = None
last_restart_reason: str = ""
watchdog_start_time = time.time()
_last_was_disconnected = False
_disconnected_start_time: float | None = None


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


def get_connection_state_from_server() -> str:
    """Try to read connection_health state from the running MCP server.

    Returns one of: "connected", "disconnected", "reconnecting", or "unknown".
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect(("127.0.0.1", 9877))
        command = json.dumps({
            "type": "get_connection_health",
            "params": {},
        }).encode("utf-8")
        sock.sendall(command)
        sock.settimeout(3.0)
        chunks = []
        while True:
            try:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                chunks.append(chunk)
                data = json.loads(b"".join(chunks).decode("utf-8"))
                sock.close()
                # The server wraps responses in {"status": "success", "result": ...}
                if isinstance(data, dict):
                    result = data.get("result", data)
                    if isinstance(result, dict):
                        return result.get("connection_state", "unknown")
                elif isinstance(data, dict):
                    return data.get("connection_state", "unknown")
                return "unknown"
            except json.JSONDecodeError:
                continue
            except socket.timeout:
                break
        sock.close()
    except Exception:
        pass
    return "unknown"


def restart_server(server_script, reason: str = ""):
    """Restart the MCP server process."""
    global restart_count, last_restart_time, last_restart_reason

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
        last_restart_reason = reason or "unknown"
        msg = f"SERVER_RESTART #{restart_count} - reason: {reason or 'unknown'}"
        logger.info(msg)
        log_connection_event(msg)
        return process
    except Exception as e:
        logger.error(f"Failed to restart server: {e}")
        return None


def watchdog_status() -> dict:
    """Return health check status with restart count, uptime, last restart reason."""
    global restart_count, last_restart_time, last_restart_reason, watchdog_start_time
    uptime = time.time() - watchdog_start_time
    return {
        "restart_count": restart_count,
        "uptime_seconds": round(uptime, 2),
        "last_restart_reason": last_restart_reason,
        "last_restart_timestamp": (
            last_restart_time.isoformat() if last_restart_time else None
        ),
        "connection_state": get_connection_state_from_server(),
    }


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
    global restart_count, _last_was_disconnected, _disconnected_start_time

    logger.info("=" * 60)
    logger.info("AbletonMCP Watchdog Started")
    logger.info("=" * 60)
    log_connection_event("WATCHDOG_STARTED")

    # Start the server
    server_process = restart_server(SERVER_SCRIPT, reason="initial_startup")

    if server_process is None:
        logger.error("Failed to start server. Exiting.")
        sys.exit(1)

    # Main monitoring loop
    last_healthcheck = time.time()
    _last_was_disconnected = False
    _disconnected_start_time = None

    try:
        while True:
            time.sleep(HEALTHCHECK_INTERVAL)

            # Check if server process is still running
            if server_process is not None and server_process.poll() is not None:
                # Process has exited - restart
                exit_code = server_process.poll()
                logger.warning(f"Server process exited (code: {exit_code})")
                log_connection_event(f"PROCESS_EXITED - code: {exit_code}")
                server_process = None

            # Check connection state from server
            conn_state = get_connection_state_from_server()

            if conn_state == "disconnected":
                if not _last_was_disconnected:
                    _disconnected_start_time = time.time()
                    _last_was_disconnected = True
                    logger.warning(
                        "Connection state is DISCONNECTED — starting watchdog timer"
                    )
                    log_connection_event(
                        "CONNECTION_DISCONNECTED - watchdog timer started"
                    )

                disconnected_duration = time.time() - _disconnected_start_time
                remaining = WATCHDOG_DISCONNECT_TIMEOUT - disconnected_duration

                if disconnected_duration >= WATCHDOG_DISCONNECT_TIMEOUT:
                    logger.error(
                        "Connection DISCONNECTED for %.0fs (limit: %ds) — "
                        "triggering server restart",
                        disconnected_duration,
                        WATCHDOG_DISCONNECT_TIMEOUT,
                    )
                    log_connection_event(
                        f"WATCHDOG_TRIGGER - disconnected for "
                        f"{disconnected_duration:.0f}s (>= {WATCHDOG_DISCONNECT_TIMEOUT}s)"
                    )
                    if server_process is not None:
                        try:
                            server_process.terminate()
                            time.sleep(1)
                        except Exception:
                            pass
                    server_process = restart_server(
                        SERVER_SCRIPT,
                        reason=f"disconnected_{WATCHDOG_DISCONNECT_TIMEOUT}s",
                    )
                    _last_was_disconnected = False
                    _disconnected_start_time = None
                elif remaining > 0 and int(disconnected_duration) % 10 == 0:
                    # Log every 10s while in disconnected state
                    logger.warning(
                        "Connection DISCONNECTED for %.0fs — restart in %.0fs",
                        disconnected_duration,
                        remaining,
                    )
            else:
                if _last_was_disconnected:
                    logger.info(
                        "Connection state recovered to: %s", conn_state
                    )
                    log_connection_event(
                        f"CONNECTION_RECOVERED - state: {conn_state}"
                    )
                    _last_was_disconnected = False
                    _disconnected_start_time = None

            # Check if server is responding to TCP connections
            if not is_server_running():
                logger.warning("Server is not responding on port 9877")

                if server_process is None or server_process.poll() is not None:
                    # Process has died or isn't running
                    server_process = restart_server(
                        SERVER_SCRIPT, reason="port_unreachable"
                    )
                    if server_process is None:
                        delay = 30
                        logger.error(f"Failed to restart server, retry in {delay}s")
                        time.sleep(delay)
                    else:
                        delay = MIN_RESTART_DELAY
                        logger.info(f"Server restarted, waiting {delay}s for startup")
                        time.sleep(delay)
                        _last_was_disconnected = False
                        _disconnected_start_time = None
                else:
                    # Process exists but not responding - wait brief then restart
                    logger.warning("Server process exists but not responding")
                    time.sleep(2)
                    try:
                        server_process.terminate()
                    except Exception:
                        pass
                    time.sleep(1)
                    server_process = restart_server(
                        SERVER_SCRIPT, reason="unresponsive"
                    )
                    _last_was_disconnected = False
                    _disconnected_start_time = None

            # Periodic health check
            if time.time() - last_healthcheck > 60:
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
        log_connection_event("WATCHDOG_STOPPED")

    logger.info("Watchdog stopped")


if __name__ == "__main__":
    main()
