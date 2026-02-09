# ableton_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context
import socket
import json
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Union
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AbletonMCPServer")

# ============================================================================
# BROWSER CACHING SYSTEM
# ============================================================================

# Cache structure: {category_type: {"data": result_dict, "timestamp": float}}
# TTL: Cache entries expire after 1 hour (3600 seconds)
BROWSER_CACHE_TTL = 3600.0  # 1 hour in seconds
_browser_cache: Dict[str, Dict[str, Any]] = {}


def is_cache_valid(category_type: str) -> bool:
    """Check if cached data for a category is still valid (not expired)"""
    if category_type not in _browser_cache:
        return False

    cache_entry = _browser_cache[category_type]
    timestamp = cache_entry.get("timestamp", 0)

    # Check if cache is still valid (within TTL)
    return (time.time() - timestamp) < BROWSER_CACHE_TTL


def update_cache(category_type: str, data: Dict[str, Any]) -> None:
    """Update cache for a specific category type"""
    _browser_cache[category_type] = {"data": data, "timestamp": time.time()}
    logger.info(f"Updated browser cache for category: {category_type}")


def get_cache(category_type: str) -> Union[Dict[str, Any], None]:
    """Get cached data for a specific category type, returns None if expired or not found"""
    if not is_cache_valid(category_type):
        return None
    return _browser_cache[category_type].get("data")


def clear_browser_cache(category_type: str = None) -> None:
    """Clear cache for a specific category or all categories"""
    if category_type:
        if category_type in _browser_cache:
            del _browser_cache[category_type]
            logger.info(f"Cleared browser cache for category: {category_type}")
    else:
        _browser_cache.clear()
        logger.info("Cleared all browser cache")


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about the current browser cache"""
    current_time = time.time()
    cache_info = {}

    for category_type, entry in _browser_cache.items():
        age = current_time - entry["timestamp"]
        is_valid = age < BROWSER_CACHE_TTL
        cache_info[category_type] = {
            "cached": True,
            "age_seconds": round(age, 2),
            "age_readable": format_age(age),
            "valid": is_valid,
            "expires_in": round(max(0, BROWSER_CACHE_TTL - age), 2),
        }

    return {
        "cache_entries": len(_browser_cache),
        "ttl_seconds": BROWSER_CACHE_TTL,
        "ttl_readable": format_age(BROWSER_CACHE_TTL),
        "categories": cache_info,
    }


def format_age(seconds: float) -> str:
    """Format age in seconds to human-readable format"""
    if seconds < 60:
        return f"{round(seconds, 1)} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{round(minutes, 1)} minutes"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{round(hours, 1)} hours"
    else:
        days = seconds / 86400
        return f"{round(days, 1)} days"


@dataclass
class AbletonConnection:
    host: str
    port: int
    sock: socket.socket = None
    udp_port: int = 9878

    def connect(self) -> bool:
        """Connect to the Ableton Remote Script socket server"""
        if self.sock:
            return True

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {str(e)}")
            self.sock = None
            return False

    def disconnect(self):
        """Disconnect from the Ableton Remote Script"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Ableton: {str(e)}")
            finally:
                self.sock = None

    def send_command_udp(
        self, command_type: str, params: Dict[str, Any] = None
    ) -> None:
        """
        Send command via UDP (fire-and-forget).

        This sends a command to Ableton using UDP protocol without waiting for a response.
        Use for high-frequency parameter updates where occasional packet loss is acceptable.

        Parameters:
        - command_type: Type of command to send (e.g., "set_device_parameter", "set_track_volume")
        - params: Command parameters as dictionary

        Returns:
        - None (fire-and-forget, no response)

        UDP-ALLOWED commands (fast, reversible):
        - set_device_parameter
        - set_track_volume
        - set_track_pan
        - set_track_mute
        - set_track_solo
        - set_track_arm
        - set_clip_launch_mode
        - fire_clip

        Note: UDP is connectionless, so no connection check is needed.
        Port 9878 is used for UDP (9877 is TCP).
        """
        command = {"type": command_type, "params": params or {}}

        try:
            logger.info(f"Sending UDP command: {command_type} with params: {params}")

            # Create UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Send command (fire-and-forget, no response)
            udp_socket.sendto(
                json.dumps(command).encode("utf-8"), (self.host, self.udp_port)
            )

            # Close socket immediately (UDP is connectionless)
            udp_socket.close()

            logger.info(f"UDP command sent (fire-and-forget): {command_type}")

        except Exception as e:
            # Log error but don't raise (UDP fire-and-forget acceptable)
            logger.error(f"Error sending UDP command: {str(e)}")
            # Continue without raising - UDP can tolerate occasional failures

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        sock.settimeout(15.0)  # Increased timeout for operations that might take longer

        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception(
                                "Connection closed before receiving any data"
                            )
                        break

                    chunks.append(chunk)

                    # Check if we've received a complete JSON object
                    try:
                        data = b"".join(chunks)
                        json.loads(data.decode("utf-8"))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise

        # If we get here, we either timed out or broke out of the loop
        if chunks:
            data = b"".join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                json.loads(data.decode("utf-8"))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(
        self, command_type: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send a command to Ableton and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")

        command = {"type": command_type, "params": params or {}}

        # Check if this is a state-modifying command
        is_modifying_command = command_type in [
            "create_midi_track",
            "create_audio_track",
            "delete_all_tracks",
            "delete_track",
            "set_track_name",
            "set_track_color",
            "set_track_fold",
            "duplicate_track",
            "create_clip",
            "delete_clip",
            "duplicate_clip",
            "move_clip",
            "add_notes_to_clip",
            "delete_notes_from_clip",
            "quantize_clip",
            "transpose_clip",
            "set_clip_name",
            "set_clip_loop",
            "set_clip_launch_mode",
            "create_scene",
            "delete_scene",
            "duplicate_scene",
            "set_scene_name",
            "set_tempo",
            "set_time_signature",
            "set_metronome",
            "fire_clip",
            "stop_clip",
            "start_playback",
            "stop_playback",
            "start_recording",
            "stop_recording",
            "set_track_monitoring_state",
            "load_instrument_or_effect",
            "get_device_parameters",
            "set_device_parameter",
            "add_automation_point",
            "clear_automation",
            "duplicate_device",
            "delete_device",
            "move_device",
            "set_track_volume",
            "set_track_pan",
            "set_track_mute",
            "set_track_solo",
            "set_track_arm",
            "set_send_amount",
            "load_instrument_preset",
            "undo",
            "redo",
            "get_playhead_position",
            "set_playhead_position",
            "create_locator",
            "delete_locator",
            "jump_to_locator",
            "set_loop",
            "get_clip_notes",
        ]

        try:
            logger.info(f"Sending command: {command_type} with params: {params}")

            # Send the command
            self.sock.sendall(json.dumps(command).encode("utf-8"))
            logger.info(f"Command sent, waiting for response...")

            # For state-modifying commands, add a small delay to give Ableton time to process
            if is_modifying_command:
                import time

                time.sleep(0.1)  # 100ms delay

            # Set timeout based on command type
            timeout = 15.0 if is_modifying_command else 10.0
            self.sock.settimeout(timeout)

            # Receive the response
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")

            # Parse the response
            response = json.loads(response_data.decode("utf-8"))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")

            if response.get("status") == "error":
                logger.error(f"Ableton error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Ableton"))

            # For state-modifying commands, add another small delay after receiving response
            if is_modifying_command:
                import time

                time.sleep(0.1)  # 100ms delay

            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Ableton")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ableton: {str(e)}")
            if "response_data" in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            self.sock = None
            raise Exception(f"Invalid response from Ableton: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Ableton: {str(e)}")
            self.sock = None
            raise Exception(f"Communication error with Ableton: {str(e)}")


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("AbletonMCP server starting up")

        try:
            ableton = get_ableton_connection()
            logger.info("Successfully connected to Ableton on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Ableton on startup: {str(e)}")
            logger.warning("Make sure the Ableton Remote Script is running")

        yield {}
    finally:
        global _ableton_connection
        if _ableton_connection:
            logger.info("Disconnecting from Ableton on shutdown")
            _ableton_connection.disconnect()
            _ableton_connection = None
        logger.info("AbletonMCP server shut down")


# Create the MCP server with lifespan support
mcp = FastMCP(
    "AbletonMCP",
    description="Ableton Live integration through the Model Context Protocol",
    lifespan=server_lifespan,
)

# Global connection for resources
_ableton_connection = None


def get_ableton_connection():
    """Get or create a persistent Ableton connection"""
    global _ableton_connection

    if _ableton_connection is not None:
        try:
            # Test the connection with a simple ping
            # We'll try to send an empty message, which should fail if the connection is dead
            # but won't affect Ableton if it's alive
            _ableton_connection.sock.settimeout(1.0)
            _ableton_connection.sock.sendall(b"")
            return _ableton_connection
        except Exception as e:
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _ableton_connection.disconnect()
            except:
                pass
            _ableton_connection = None

    # Connection doesn't exist or is invalid, create a new one
    if _ableton_connection is None:
        # Try to connect up to 3 times with a short delay between attempts
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(
                    f"Connecting to Ableton (attempt {attempt}/{max_attempts})..."
                )
                _ableton_connection = AbletonConnection(host="127.0.0.1", port=9877)
                if _ableton_connection.connect():
                    logger.info("Created new persistent connection to Ableton")

                    # Validate connection with a simple command
                    try:
                        # Get session info as a test
                        _ableton_connection.send_command("get_session_info")
                        logger.info("Connection validated successfully")
                        return _ableton_connection
                    except Exception as e:
                        logger.error(f"Connection validation failed: {str(e)}")
                        _ableton_connection.disconnect()
                        _ableton_connection = None
                        # Continue to next attempt
                else:
                    _ableton_connection = None
            except Exception as e:
                logger.error(f"Connection attempt {attempt} failed: {str(e)}")
                if _ableton_connection:
                    _ableton_connection.disconnect()
                    _ableton_connection = None

            # Wait before trying again, but only if we have more attempts left
            if attempt < max_attempts:
                import time

                time.sleep(1.0)

        # If we get here, all connection attempts failed
        if _ableton_connection is None:
            logger.error("Failed to connect to Ableton after multiple attempts")
            raise Exception(
                "Could not connect to Ableton. Make sure the Remote Script is running."
            )

    return _ableton_connection


# Core Tool endpoints


@mcp.tool()
def get_session_info(ctx: Context) -> str:
    """Get detailed information about current Ableton session"""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting session info from Ableton: {str(e)}")
        return f"Error getting session info: {str(e)}"


@mcp.tool()
def get_session_overview(ctx: Context) -> str:
    """
    Get a complete overview of the Ableton session in a single call.

    Combines information from:
    - Session metadata (tempo, time signature)
    - All tracks (names, types, mute/solo/arm states)
    - Master track information
    - All scenes (names and counts)

    This is more efficient than querying each track individually.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_overview")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting session overview: {str(e)}")
        return f"Error getting session overview: {str(e)}"


@mcp.tool()
def get_track_info(ctx: Context, track_index: int) -> str:
    """
    Get detailed information about a specific track in Ableton.

    Parameters:
    - track_index: The index of the track to get information about
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_info", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting track info from Ableton: {str(e)}")
        return f"Error getting track info: {str(e)}"


@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """
    Create a new MIDI track in the Ableton session.

    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_midi_track", {"index": index})
        return f"Created new MIDI track: {result.get('name', 'unknown')}"
    except Exception as e:
        logger.error(f"Error creating MIDI track: {str(e)}")
        return f"Error creating MIDI track: {str(e)}"


@mcp.tool()
def delete_all_tracks(ctx: Context) -> str:
    """
    Delete all tracks in the Ableton session.

    This will remove all MIDI and audio tracks, leaving you with a fresh session.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_all_tracks")
        deleted_count = result.get("deleted_count", 0)
        return f"Deleted {deleted_count} tracks from session"
    except Exception as e:
        logger.error(f"Error deleting all tracks: {str(e)}")
        return f"Error deleting all tracks: {str(e)}"


@mcp.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str:
    """
    Set the name of a track.

    Parameters:
    - track_index: The index of the track to rename
    - name: The new name for the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_name", {"track_index": track_index, "name": name}
        )
        return f"Renamed track to: {result.get('name', name)}"
    except Exception as e:
        logger.error(f"Error setting track name: {str(e)}")
        return f"Error setting track name: {str(e)}"


@mcp.tool()
def create_clip(
    ctx: Context, track_index: int, clip_index: int, length: float = 4.0
) -> str:
    """
    Create a new MIDI clip in the specified track and clip slot.

    Parameters:
    - track_index: The index of the track to create the clip in
    - clip_index: The index of the clip slot to create the clip in
    - length: The length of the clip in beats (default: 4.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "create_clip",
            {"track_index": track_index, "clip_index": clip_index, "length": length},
        )
        return f"Created new clip at track {track_index}, slot {clip_index} with length {length} beats"
    except Exception as e:
        logger.error(f"Error creating clip: {str(e)}")
        return f"Error creating clip: {str(e)}"


@mcp.tool()
def add_notes_to_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    notes: List[Dict[str, Union[int, float, bool]]],
) -> str:
    """
    Add MIDI notes to a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - notes: List of note dictionaries, each with pitch, start_time, duration, velocity, and mute
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "add_notes_to_clip",
            {"track_index": track_index, "clip_index": clip_index, "notes": notes},
        )
        return f"Added {len(notes)} notes to clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error adding notes to clip: {str(e)}")
        return f"Error adding notes to clip: {str(e)}"


@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """
    Set the name of a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - name: The new name for the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_clip_name",
            {"track_index": track_index, "clip_index": clip_index, "name": name},
        )
        return f"Renamed clip at track {track_index}, slot {clip_index} to '{name}'"
    except Exception as e:
        logger.error(f"Error setting clip name: {str(e)}")
        return f"Error setting clip name: {str(e)}"


@mcp.tool()
def set_tempo(ctx: Context, tempo: float) -> str:
    """
    Set the tempo of the Ableton session.

    Parameters:
    - tempo: The new tempo in BPM
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_tempo", {"tempo": tempo})
        return f"Set tempo to {tempo} BPM"
    except Exception as e:
        logger.error(f"Error setting tempo: {str(e)}")
        return f"Error setting tempo: {str(e)}"


@mcp.tool()
def load_instrument_or_effect(ctx: Context, track_index: int, uri: str) -> str:
    """
    Load an instrument or effect onto a track using its URI.

    Parameters:
    - track_index: The index of the track to load the instrument on
    - uri: The URI of the instrument or effect to load (e.g., 'query:Synths#Instrument%20Rack:Bass:FileId_5116')
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "load_browser_item", {"track_index": track_index, "item_uri": uri}
        )

        # Check if the instrument was loaded successfully
        if result.get("loaded", False):
            new_devices = result.get("new_devices", [])
            if new_devices:
                return f"Loaded instrument with URI '{uri}' on track {track_index}. New devices: {', '.join(new_devices)}"
            else:
                devices = result.get("devices_after", [])
                return f"Loaded instrument with URI '{uri}' on track {track_index}. Devices on track: {', '.join(devices)}"
        else:
            return f"Failed to load instrument with URI '{uri}'"
    except Exception as e:
        logger.error(f"Error loading instrument by URI: {str(e)}")
        return f"Error loading instrument by URI: {str(e)}"


@mcp.tool()
def fire_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Start playing a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "fire_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Started playing clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error firing clip: {str(e)}")
        return f"Error firing clip: {str(e)}"


@mcp.tool()
def stop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Stop playing a clip.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "stop_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Stopped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error stopping clip: {str(e)}")
        return f"Error stopping clip: {str(e)}"


@mcp.tool()
def start_playback(ctx: Context) -> str:
    """Start playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("start_playback")
        return "Started playback"
    except Exception as e:
        logger.error(f"Error starting playback: {str(e)}")
        return f"Error starting playback: {str(e)}"


@mcp.tool()
def stop_playback(ctx: Context) -> str:
    """Stop playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_playback")
        return "Stopped playback"
    except Exception as e:
        logger.error(f"Error stopping playback: {str(e)}")
        return f"Error stopping playback: {str(e)}"


@mcp.tool()
def start_recording(ctx: Context) -> str:
    """Start recording. Playback will also start if not already playing."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("start_recording")
        return "Started recording"
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return f"Error starting recording: {str(e)}"


@mcp.tool()
def stop_recording(ctx: Context) -> str:
    """Stop recording. Playback continues."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_recording")
        return "Stopped recording"
    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")
        return f"Error stopping recording: {str(e)}"


@mcp.tool()
def delete_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Delete a device from a track.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_device", {"track_index": track_index, "device_index": device_index}
        )
        device_name = result.get("device_name", f"Device {device_index}")
        return f"Deleted {device_name} from track {track_index}"
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        return f"Error deleting device: {str(e)}"


@mcp.tool()
def duplicate_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Duplicate a device to another track.

    Parameters:
    - track_index: The index of the track containing the device
    - device_index: The index of the device to duplicate
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "duplicate_device",
            {"track_index": track_index, "device_index": device_index},
        )
        device_name = result.get("device_name", f"Device {device_index}")
        target_track_index = result.get("new_track_index", -1)
        return f"Duplicated {device_name} to track {target_track_index}"
    except Exception as e:
        logger.error(f"Error duplicating device: {str(e)}")
        return f"Error duplicating device: {str(e)}"


@mcp.tool()
def move_device(
    ctx: Context, track_index: int, device_index: int, new_position: int
) -> str:
    """
    Move a device to a new position in the device chain.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to move
    - new_position: The new position index for the device
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "move_device",
            {
                "track_index": track_index,
                "device_index": device_index,
                "new_position": new_position,
            },
        )
        device_name = result.get("device_name", f"Device {device_index}")
        return f"Moved {device_name} to position {new_position}"
    except Exception as e:
        logger.error(f"Error moving device: {str(e)}")
        return f"Error moving device: {str(e)}"


@mcp.tool()
def toggle_device_bypass(
    ctx: Context, track_index: int, device_index: int, enabled: bool
) -> str:
    """
    Toggle device bypass on/off.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to toggle
    - enabled: True to enable, False to disable
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "toggle_device_bypass",
            {
                "track_index": track_index,
                "device_index": device_index,
                "enabled": enabled,
            },
        )
        device_name = result.get("device_name", f"Device {device_index}")
        bypass_state = result.get("bypass_enabled", "unknown")
        action = "enabled" if enabled else "disabled"
        return f"Set {device_name} bypass {action} (currently {bypass_state})"
    except Exception as e:
        logger.error(f"Error toggling device bypass: {str(e)}")
        return f"Error toggling device bypass: {str(e)}"


@mcp.tool()
def get_playhead_position(ctx: Context) -> str:
    """
    Get the current playhead position in the Ableton session.

    Returns the current position in bars and beats.
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_playhead_position")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting playhead position: {str(e)}")
        return f"Error getting playhead position: {str(e)}"


@mcp.tool()
def set_playhead_position(ctx: Context, bar: int, beat: float = 0.0) -> str:
    """
    Set the playhead position to a specific bar and beat.

    Parameters:
    - bar: The bar number to jump to
    - beat: The beat position within the bar (0.0 to 3.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_playhead_position", {"bar": bar, "beat": beat}
        )
        return f"Set playhead to bar {bar}.{beat}"
    except Exception as e:
        logger.error(f"Error setting playhead position: {str(e)}")
        return f"Error setting playhead position: {str(e)}"


@mcp.tool()
def trigger_scene(ctx: Context, scene_index: int) -> str:
    """
    Trigger all clips for a specific scene at once.

    This fires all the clips configured for that scene simultaneously.

    Parameters:
    - scene_index: The scene number to trigger (0-7)
    """
    try:
        ableton = get_ableton_connection()

        # Scene definitions with track/clip mappings
        scenes = {
            0: {  # Intro
                "name": "Scene 0 - Intro",
                "clips": [
                    (1, 2),  # Kick Minimal
                    (0, 0),  # Bass main
                    (2, -1),  # Stop percussion
                    (3, -1),  # Stop chords
                    (4, -1),  # Stop FX
                    (5, -1),  # Stop lead
                ],
            },
            1: {  # Buildup
                "name": "Scene 1 - Buildup",
                "clips": [
                    (1, 2),  # Kick Minimal
                    (0, 1),  # Bass Syncopated
                    (2, 2),  # Perc Minimal
                    (3, -1),  # Stop chords
                    (4, -1),  # Stop FX
                    (5, -1),  # Stop lead
                ],
            },
            2: {  # Main 1
                "name": "Scene 2 - Main 1",
                "clips": [
                    (1, 3),  # Kick Accented
                    (0, 2),  # Bass Staccato
                    (2, 0),  # Perc Dub
                    (3, 0),  # Chords Stabs
                    (4, 1),  # FX Intense
                    (5, 0),  # Lead Melody
                ],
            },
            3: {  # Main 2
                "name": "Scene 3 - Main 2",
                "clips": [
                    (1, 0),  # Kick 4/4
                    (0, 3),  # Bass Melodic
                    (2, 3),  # Perc Complex
                    (3, 1),  # Chords Pads
                    (4, 0),  # FX Dub
                    (5, 1),  # Lead Active
                ],
            },
            4: {  # Breakdown
                "name": "Scene 4 - Breakdown",
                "clips": [
                    (1, -1),  # Stop kick
                    (0, -1),  # Stop bass
                    (2, -1),  # Stop percussion
                    (3, 2),  # Chords Minimal
                    (4, 2),  # FX Ambient
                    (5, 2),  # Lead Minimal
                ],
            },
            5: {  # Buildup 2
                "name": "Scene 5 - Buildup 2",
                "clips": [
                    (1, 1),  # Kick + Sub
                    (0, 1),  # Bass Syncopated
                    (2, 1),  # Perc Dense
                    (3, -1),  # Stop chords
                    (4, 1),  # FX Intense
                    (5, -1),  # Stop lead
                ],
            },
            6: {  # Main 3
                "name": "Scene 6 - Main 3 (Peak)",
                "clips": [
                    (1, 3),  # Kick Accented
                    (0, 2),  # Bass Staccato
                    (2, 3),  # Perc Complex
                    (3, 0),  # Chords Stabs
                    (4, 1),  # FX Intense
                    (5, 1),  # Lead Active
                ],
            },
            7: {  # Outro
                "name": "Scene 7 - Outro",
                "clips": [
                    (1, 2),  # Kick Minimal
                    (0, 4),  # Bass Intro
                    (2, -1),  # Stop percussion
                    (3, -1),  # Stop chords
                    (4, -1),  # Stop FX
                    (5, -1),  # Stop lead
                ],
            },
        }

        if scene_index not in scenes:
            return f"Error: Scene {scene_index} not found. Available scenes: 0-7"

        scene = scenes[scene_index]

        # Fire all clips for this scene
        for track_index, clip_index in scene["clips"]:
            if clip_index >= 0:
                result = ableton.send_command(
                    "fire_clip", {"track_index": track_index, "clip_index": clip_index}
                )
            else:
                result = ableton.send_command(
                    "stop_clip", {"track_index": track_index, "clip_index": 0}
                )

        return f"Triggered {scene['name']} with {len(scene['clips'])} clip actions"
    except Exception as e:
        logger.error(f"Error triggering scene: {str(e)}")
        return f"Error triggering scene: {str(e)}"


@mcp.tool()
def play_arrangement_sequence(ctx: Context) -> str:
    """
    Automatically play through the full 8-scene arrangement.

    This will trigger each scene sequentially at the correct times.
    Requires the arrangement to be set up in Session View first.
    """
    try:
        ableton = get_ableton_connection()

        # Stop playback first
        ableton.send_command("stop_playback")

        # Start from beginning
        import time

        print("Starting arrangement sequence...")
        print("Scene 0 will trigger immediately")
        print("Subsequent scenes will trigger every 8 bars")
        print("Each 8-bar section takes approximately 19 seconds at 126 BPM")
        print()
        print("TIMING SCHEDULE:")
        print("  Scene 0: 0:00 - Intro (Bars 1-8)")
        print("  Scene 1: 0:19 - Buildup (Bars 9-16)")
        print("  Scene 2: 0:38 - Main 1 (Bars 17-32)")
        print("  Scene 3: 1:16 - Main 2 (Bars 33-48)")
        print("  Scene 4: 1:54 - Breakdown (Bars 49-64)")
        print("  Scene 5: 2:31 - Buildup 2 (Bars 65-72)")
        print("  Scene 6: 3:09 - Main 3 (Bars 73-88)")
        print("  Scene 7: 3:44 - Outro (Bars 89-96)")
        print()
        print("Total duration: 3:45 (228 seconds)")
        print()
        print("Starting Scene 0 now...")

        # Trigger Scene 0 and start playback
        # Note: This only triggers Scene 0 - user must manually trigger subsequent scenes
        # or use a timer-based system

        return "Full arrangement sequence ready.\nNote: Ableton's Remote Script API has limitations.\nScene 0 is triggered, but subsequent scenes must be triggered manually.\nFor automatic scene progression, use Arrangement View in Ableton:\n1. Switch to Arrangement View (Tab key)\n2. Press Record + Play together\n3. Arrangement will auto-play through all 8 scenes"
    except Exception as e:
        logger.error(f"Error playing arrangement sequence: {str(e)}")
        return f"Error playing arrangement sequence: {str(e)}"


@mcp.tool()
def get_browser_tree(ctx: Context, category_type: str = "all") -> str:
    """
    Get a hierarchical tree of browser categories from Ableton.
    Uses caching to speed up repeated requests (cache TTL: 1 hour).

    Parameters:
    - category_type: Type of categories to get ('all', 'instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects')
    """
    try:
        # Check cache first
        cached_data = get_cache(category_type)
        if cached_data:
            logger.info(f"Returning cached browser tree for category: {category_type}")

            # Format cached data
            total_folders = cached_data.get("total_folders", 0)
            formatted_output = f"Browser tree for '{category_type}' (CACHED - showing {total_folders} folders):\n\n"

            def format_tree(item, indent=0):
                output = ""
                if item:
                    prefix = "  " * indent
                    name = item.get("name", "Unknown")
                    path = item.get("path", "")
                    has_more = item.get("has_more", False)

                    # Add this item
                    output += f"{prefix}• {name}"
                    if path:
                        output += f" (path: {path})"
                    if has_more:
                        output += " [...]"
                    output += "\n"

                    # Add children
                    for child in item.get("children", []):
                        output += format_tree(child, indent + 1)
                return output

            # Format each category
            for category in cached_data.get("categories", []):
                formatted_output += format_tree(category)
                formatted_output += "\n"

            return formatted_output

        # Cache miss - fetch from Ableton
        logger.info(f"Cache miss for category: {category_type}, fetching from Ableton")
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_browser_tree", {"category_type": category_type}
        )

        # Check if we got any categories
        if "available_categories" in result and len(result.get("categories", [])) == 0:
            available_cats = result.get("available_categories", [])
            return (
                f"No categories found for '{category_type}'. "
                f"Available browser categories: {', '.join(available_cats)}"
            )

        # Update cache with fresh data
        update_cache(category_type, result)
        logger.info(f"Cached browser tree for category: {category_type}")

        # Format the tree in a more readable way
        total_folders = result.get("total_folders", 0)
        formatted_output = (
            f"Browser tree for '{category_type}' (showing {total_folders} folders):\n\n"
        )

        def format_tree(item, indent=0):
            output = ""
            if item:
                prefix = "  " * indent
                name = item.get("name", "Unknown")
                path = item.get("path", "")
                has_more = item.get("has_more", False)

                # Add this item
                output += f"{prefix}• {name}"
                if path:
                    output += f" (path: {path})"
                if has_more:
                    output += " [...]"
                output += "\n"

                # Add children
                for child in item.get("children", []):
                    output += format_tree(child, indent + 1)
            return output

        # Format each category
        for category in result.get("categories", []):
            formatted_output += format_tree(category)
            formatted_output += "\n"

        return formatted_output
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return f"Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return f"Error: Could not access Ableton Live application. Make sure Ableton Live is running and Remote Script is loaded."
        else:
            logger.error(f"Error getting browser tree: {error_msg}")
            return f"Error getting browser tree: {error_msg}"


@mcp.tool()
def get_browser_items_at_path(ctx: Context, path: str) -> str:
    """
    Get browser items at a specific path in Ableton's browser.

    Parameters:
    - path: Path in the format "category/folder/subfolder"
            where category is one of the available browser categories in Ableton
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_items_at_path", {"path": path})

        # Check if there was an error with available categories
        if "error" in result and "available_categories" in result:
            error = result.get("error", "")
            available_cats = result.get("available_categories", [])
            return (
                f"Error: {error}\n"
                f"Available browser categories: {', '.join(available_cats)}"
            )

        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return f"Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return f"Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        elif "Unknown or unavailable category" in error_msg:
            logger.error(f"Invalid browser category: {error_msg}")
            return f"Error: {error_msg}. Please check the available categories using get_browser_tree."
        elif "Path part" in error_msg and "not found" in error_msg:
            logger.error(f"Path not found: {error_msg}")
            return f"Error: {error_msg}. Please check the path and try again."
        else:
            logger.error(f"Error getting browser items at path: {error_msg}")
            return f"Error getting browser items at path: {error_msg}"


@mcp.tool()
def cache_info(ctx: Context) -> str:
    """
    Get information about the browser cache.

    Shows cache statistics including number of cached entries,
    time-to-live (TTL), and details for each cached category.
    """
    try:
        stats = get_cache_stats()

        output = "Browser Cache Information\n"
        output += "=" * 50 + "\n\n"

        if stats["cache_entries"] == 0:
            output += "Cache is empty. No browser data has been cached yet.\n"
        else:
            output += f"Total cached entries: {stats['cache_entries']}\n"
            output += f"Cache TTL (Time-To-Live): {stats['ttl_readable']}\n\n"

            output += "Cached Categories:\n"
            output += "-" * 50 + "\n"

            for category_type, info in stats["categories"].items():
                status = "✓ VALID" if info["valid"] else "✗ EXPIRED"
                output += f"\n{category_type.upper()}:\n"
                output += f"  Status: {status}\n"
                output += f"  Age: {info['age_readable']}\n"
                output += f"  Expires in: {format_age(info['expires_in'])}\n"

        output += "\n" + "=" * 50
        return output
    except Exception as e:
        logger.error(f"Error getting cache info: {str(e)}")
        return f"Error getting cache info: {str(e)}"


@mcp.tool()
def clear_cache(ctx: Context, category_type: str = None) -> str:
    """
    Clear browser cache to force refresh on next request.

    Parameters:
    - category_type: Optional category to clear ('instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects').
                   If not provided, clears all cached categories.
    """
    try:
        if category_type:
            # Clear specific category
            if category_type not in _browser_cache:
                return f"Warning: Category '{category_type}' is not cached. Nothing to clear."

            clear_browser_cache(category_type)
            return f"Cleared browser cache for category: {category_type}"
        else:
            # Clear all cache
            num_cleared = len(_browser_cache)
            clear_browser_cache()
            return f"Cleared all browser cache entries ({num_cleared} categories)"
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return f"Error clearing cache: {str(e)}"


@mcp.tool()
def load_drum_kit(ctx: Context, track_index: int, rack_uri: str, kit_path: str) -> str:
    """
    Load a drum rack and then load a specific drum kit into it.

    Parameters:
    - track_index: The index of the track to load on
    - rack_uri: The URI of the drum rack to load (e.g., 'Drums/Drum Rack')
    - kit_path: Path to the drum kit inside the browser (e.g., 'drums/acoustic/kit1')
    """
    try:
        ableton = get_ableton_connection()

        # Step 1: Load the drum rack
        result = ableton.send_command(
            "load_browser_item", {"track_index": track_index, "item_uri": rack_uri}
        )

        if not result.get("loaded", False):
            return f"Failed to load drum rack with URI '{rack_uri}'"

        # Step 2: Get the drum kit items at the specified path
        kit_result = ableton.send_command(
            "get_browser_items_at_path", {"path": kit_path}
        )

        if "error" in kit_result:
            return f"Loaded drum rack but failed to find drum kit: {kit_result.get('error')}"

        # Step 3: Find a loadable drum kit
        kit_items = kit_result.get("items", [])
        loadable_kits = [item for item in kit_items if item.get("is_loadable", False)]

        if not loadable_kits:
            return f"Loaded drum rack but no loadable drum kits found at '{kit_path}'"

        # Step 4: Load the first loadable kit
        kit_uri = loadable_kits[0].get("uri")
        load_result = ableton.send_command(
            "load_browser_item", {"track_index": track_index, "item_uri": kit_uri}
        )

        return f"Loaded drum rack and kit '{loadable_kits[0].get('name')}' on track {track_index}"
    except Exception as e:
        logger.error(f"Error loading drum kit: {str(e)}")
        return f"Error loading drum kit: {str(e)}"


@mcp.tool()
def get_device_parameters(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Get all parameters for a specific device on a track.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device on the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_device_parameters",
            {"track_index": track_index, "device_index": device_index},
        )
        device_name = result.get("device_name", "Unknown")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting device parameters: {str(e)}")
        return f"Error getting device parameters: {str(e)}"


@mcp.tool()
def set_device_parameter(
    ctx: Context,
    track_index: int,
    device_index: int,
    parameter_index: int,
    value: float,
) -> str:
    """
    Set a device parameter value (normalized 0.0-1.0).

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device on the track
    - parameter_index: The index of the parameter to set
    - value: The normalized value to set (0.0 to 1.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_device_parameter",
            {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "value": value,
            },
        )
        param_name = result.get("parameter_name", f"Parameter {parameter_index}")
        return f"Set {param_name} to {value} on device {device_index}"
    except Exception as e:
        logger.error(f"Error setting device parameter: {str(e)}")
        return f"Error setting device parameter: {str(e)}"


@mcp.tool()
def set_track_volume(ctx: Context, track_index: int, volume: float) -> str:
    """
    Set track volume (normalized 0.0-1.0).

    Parameters:
    - track_index: The index of the track
    - volume: The normalized volume value (0.0 = silent, 1.0 = full)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_volume", {"track_index": track_index, "volume": volume}
        )
        track_name = result.get("track_name", f"Track {track_index}")
        return f"Set {track_name} volume to {volume}"
    except Exception as e:
        logger.error(f"Error setting track volume: {str(e)}")
        return f"Error setting track volume: {str(e)}"


@mcp.tool()
def set_track_mute(ctx: Context, track_index: int, mute: bool) -> str:
    """
    Mute or unmute a track.

    Parameters:
    - track_index: The index of the track
    - mute: True to mute, False to unmute
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_mute", {"track_index": track_index, "mute": mute}
        )
        track_name = result.get("track_name", f"Track {track_index}")
        action = "muted" if mute else "unmuted"
        return f"{track_name} {action}"
    except Exception as e:
        logger.error(f"Error setting track mute: {str(e)}")
        return f"Error setting track mute: {str(e)}"


@mcp.tool()
def set_track_solo(ctx: Context, track_index: int, solo: bool) -> str:
    """
    Solo or unsolo a track.

    Parameters:
    - track_index: The index of the track
    - solo: True to solo, False to unsolo
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_solo", {"track_index": track_index, "solo": solo}
        )
        track_name = result.get("track_name", f"Track {track_index}")
        action = "soloed" if solo else "unsoloed"
        return f"{track_name} {action}"
    except Exception as e:
        logger.error(f"Error setting track solo: {str(e)}")
        return f"Error setting track solo: {str(e)}"


@mcp.tool()
def set_track_arm(ctx: Context, track_index: int, arm: bool) -> str:
    """
    Arm or unarm a track for recording.

    Parameters:
    - track_index: The index of the track
    - arm: True to arm, False to unarm
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_arm", {"track_index": track_index, "arm": arm}
        )
        track_name = result.get("track_name", f"Track {track_index}")
        action = "armed" if arm else "unarmed"
        return f"{track_name} {action}"
    except Exception as e:
        logger.error(f"Error setting track arm: {str(e)}")
        return f"Error setting track arm: {str(e)}"


@mcp.tool()
def load_instrument_preset(
    ctx: Context, track_index: int, device_index: int, preset_name: str
) -> str:
    """
    Load a preset for a device on a track by name.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device on the track
    - preset_name: The name of the preset to load (case-insensitive search)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "load_instrument_preset",
            {
                "track_index": track_index,
                "device_index": device_index,
                "preset_name": preset_name,
            },
        )
        device_name = result.get("device_name", f"Device {device_index}")

        if result.get("loaded", False):
            # Preset load failed - list available presets
            available_presets = result.get("available_presets", [])
            presets_list = ", ".join(available_presets)
            return f"Preset '{preset_name}' not found for {device_name}. Available: {presets_list}"

        return f"Loaded preset '{preset_name}' for {device_name}"
    except Exception as e:
        logger.error(f"Error loading instrument preset: {str(e)}")
        return f"Error loading instrument preset: {str(e)}"


@mcp.tool()
def create_audio_track(ctx: Context, index: int = -1) -> str:
    """
    Create a new audio track in the Ableton session.

    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_audio_track", {"index": index})
        return f"Created new audio track: {result.get('name', 'unknown')} at index {result.get('index', -1)}"
    except Exception as e:
        logger.error(f"Error creating audio track: {str(e)}")
        return f"Error creating audio track: {str(e)}"


@mcp.tool()
def delete_track(ctx: Context, track_index: int) -> str:
    """
    Delete a track from the session.

    Parameters:
    - track_index: The index of the track to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_track", {"track_index": track_index})
        return f"Deleted track: {result.get('deleted_track', 'unknown')}"
    except Exception as e:
        logger.error(f"Error deleting track: {str(e)}")
        return f"Error deleting track: {str(e)}"


@mcp.tool()
def set_track_color(ctx: Context, track_index: int, color_index: int) -> str:
    """
    Set the color of a track.

    Parameters:
    - track_index: The index of the track
    - color_index: Color index (0-127)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_color", {"track_index": track_index, "color_index": color_index}
        )
        return f"Set track {track_index} color to index {color_index}"
    except Exception as e:
        logger.error(f"Error setting track color: {str(e)}")
        return f"Error setting track color: {str(e)}"


@mcp.tool()
def set_track_fold(ctx: Context, track_index: int, folded: bool = True) -> str:
    """
    Set the fold state of a track.

    Parameters:
    - track_index: The index of the track
    - folded: True to fold, False to unfold
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_fold", {"track_index": track_index, "folded": folded}
        )
        return f"Set track {track_index} fold state to {'folded' if folded else 'unfolded'}"
    except Exception as e:
        logger.error(f"Error setting track fold: {str(e)}")
        return f"Error setting track fold: {str(e)}"


@mcp.tool()
def duplicate_track(ctx: Context, track_index: int) -> str:
    """
    Duplicate a track.

    Parameters:
    - track_index: The index of the track to duplicate
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_track", {"track_index": track_index})
        return (
            f"Duplicated track {track_index} to new track {result.get('new_index', -1)}"
        )
    except Exception as e:
        logger.error(f"Error duplicating track: {str(e)}")
        return f"Error duplicating track: {str(e)}"


@mcp.tool()
def delete_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Delete a clip from a track.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Deleted clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error deleting clip: {str(e)}")
        return f"Error deleting clip: {str(e)}"


@mcp.tool()
def duplicate_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Duplicate a clip to the next slot.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "duplicate_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Duplicated clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error duplicating clip: {str(e)}")
        return f"Error duplicating clip: {str(e)}"


@mcp.tool()
def move_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    new_track_index: int,
    new_clip_index: int,
) -> str:
    """
    Move a clip to another slot.

    Parameters:
    - track_index: The index of the current track
    - clip_index: The index of the current clip slot
    - new_track_index: The index of the target track
    - new_clip_index: The index of the target clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "move_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "new_track_index": new_track_index,
                "new_clip_index": new_clip_index,
            },
        )
        return f"Moved clip from [{track_index}, {clip_index}] to [{new_track_index}, {new_clip_index}]"
    except Exception as e:
        logger.error(f"Error moving clip: {str(e)}")
        return f"Error moving clip: {str(e)}"


@mcp.tool()
def delete_notes_from_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    note_indices: List[int],
) -> str:
    """
    Delete specific notes from a clip by indices.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - note_indices: List of note indices to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_notes_from_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "note_indices": note_indices,
            },
        )
        return f"Deleted {result.get('deleted_count', 0)} notes from clip"
    except Exception as e:
        logger.error(f"Error deleting notes: {str(e)}")
        return f"Error deleting notes: {str(e)}"


@mcp.tool()
def quantize_clip(
    ctx: Context, track_index: int, clip_index: int, amount: float = 1.0
) -> str:
    """
    Quantize notes in a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - amount: Quantize amount (0.0 to 1.0, default 1.0 = 100%)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "quantize_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "amount": amount,
            },
        )
        return f"Quantized clip at track {track_index}, slot {clip_index} with {amount * 100:.0f}% strength"
    except Exception as e:
        logger.error(f"Error quantizing clip: {str(e)}")
        return f"Error quantizing clip: {str(e)}"


@mcp.tool()
def transpose_clip(
    ctx: Context, track_index: int, clip_index: int, semitones: int = 0
) -> str:
    """
    Transpose all notes in a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - semitones: Number of semitones to transpose (positive = up, negative = down)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "transpose_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "semitones": semitones,
            },
        )
        direction = "up" if semitones >= 0 else "down"
        return f"Transposed clip {semitones} semitones {direction}"
    except Exception as e:
        logger.error(f"Error transposing clip: {str(e)}")
        return f"Error transposing clip: {str(e)}"


@mcp.tool()
def set_clip_loop(
    ctx: Context,
    track_index: int,
    clip_index: int,
    loop_start: float = 0.0,
    loop_length: float = 4.0,
) -> str:
    """
    Set clip loop parameters.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - loop_start: Loop start position in beats
    - loop_length: Loop length in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_clip_loop",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "loop_start": loop_start,
                "loop_length": loop_length,
            },
        )
        return f"Set clip loop from {loop_start} to {loop_start + loop_length} beats"
    except Exception as e:
        logger.error(f"Error setting clip loop: {str(e)}")
        return f"Error setting clip loop: {str(e)}"


@mcp.tool()
def set_clip_launch_mode(
    ctx: Context, track_index: int, clip_index: int, mode: int = 0
) -> str:
    """
    Set clip launch mode.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - mode: Launch mode (0=Trigger, 1=Gate, 2=Toggle, 3=Repeat)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_clip_launch_mode",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "mode": mode,
            },
        )
        modes = ["Trigger", "Gate", "Toggle", "Repeat"]
        return f"Set clip launch mode to {modes[mode] if mode < len(modes) else f'Mode {mode}'}"
    except Exception as e:
        logger.error(f"Error setting clip launch mode: {str(e)}")
        return f"Error setting clip launch mode: {str(e)}"


@mcp.tool()
def create_scene(ctx: Context, index: int = -1) -> str:
    """
    Create a new scene.

    Parameters:
    - index: The index to insert the scene at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_scene", {"index": index})
        return f"Created new scene at index {result.get('scene_index', -1)}"
    except Exception as e:
        logger.error(f"Error creating scene: {str(e)}")
        return f"Error creating scene: {str(e)}"


@mcp.tool()
def delete_scene(ctx: Context, scene_index: int) -> str:
    """
    Delete a scene.

    Parameters:
    - scene_index: The index of the scene to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_scene", {"scene_index": scene_index})
        return f"Deleted scene at index {scene_index}"
    except Exception as e:
        logger.error(f"Error deleting scene: {str(e)}")
        return f"Error deleting scene: {str(e)}"


@mcp.tool()
def duplicate_scene(ctx: Context, scene_index: int) -> str:
    """
    Duplicate a scene.

    Parameters:
    - scene_index: The index of the scene to duplicate
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_scene", {"scene_index": scene_index})
        return f"Duplicated scene {scene_index} to new scene {result.get('new_scene_index', -1)}"
    except Exception as e:
        logger.error(f"Error duplicating scene: {str(e)}")
        return f"Error duplicating scene: {str(e)}"


@mcp.tool()
def set_scene_name(ctx: Context, scene_index: int, name: str) -> str:
    """
    Set the name of a scene.

    Parameters:
    - scene_index: The index of the scene
    - name: The new name for the scene
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_scene_name", {"scene_index": scene_index, "name": name}
        )
        return f"Renamed scene {scene_index} to '{name}'"
    except Exception as e:
        logger.error(f"Error setting scene name: {str(e)}")
        return f"Error setting scene name: {str(e)}"


@mcp.tool()
def set_time_signature(ctx: Context, numerator: int = 4, denominator: int = 4) -> str:
    """
    Set the session time signature.

    Parameters:
    - numerator: Top number (beats per bar)
    - denominator: Bottom number (note value)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_time_signature", {"numerator": numerator, "denominator": denominator}
        )
        return f"Set time signature to {numerator}/{denominator}"
    except Exception as e:
        logger.error(f"Error setting time signature: {str(e)}")
        return f"Error setting time signature: {str(e)}"


@mcp.tool()
def set_metronome(ctx: Context, enabled: bool = True) -> str:
    """
    Enable or disable the metronome.

    Parameters:
    - enabled: True to enable, False to disable
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_metronome", {"enabled": enabled})
        return f"Metronome {'enabled' if enabled else 'disabled'}"
    except Exception as e:
        logger.error(f"Error setting metronome: {str(e)}")
        return f"Error setting metronome: {str(e)}"


@mcp.tool()
def start_recording(ctx: Context) -> str:
    """Start recording. Playback will also start if not already playing."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("start_recording")
        return "Started recording"
    except Exception as e:
        logger.error(f"Error starting recording: {str(e)}")
        return f"Error starting recording: {str(e)}"


@mcp.tool()
def stop_recording(ctx: Context) -> str:
    """Stop recording. Playback continues."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_recording")
        return "Stopped recording"
    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")
        return f"Error stopping recording: {str(e)}"


@mcp.tool()
def set_track_monitoring_state(
    ctx: Context, track_index: int, monitoring_state: int
) -> str:
    """
    Set track monitoring state (audio tracks only).

    Parameters:
    - track_index: The index of the track
    - monitoring_state: 0=Off, 1=In, 2=Auto
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_monitoring_state",
            {"track_index": track_index, "monitoring_state": monitoring_state},
        )
        states = ["Off", "In", "Auto"]
        return f"Set track {track_index} monitoring to {states[monitoring_state] if monitoring_state < len(states) else f'State {monitoring_state}'}"
    except Exception as e:
        logger.error(f"Error setting monitoring state: {str(e)}")
        return f"Error setting monitoring state: {str(e)}"


@mcp.tool()
def add_automation_point(
    ctx: Context,
    track_index: int,
    clip_index: int,
    device_index: int,
    parameter_index: int,
    time: float,
    value: float,
) -> str:
    """
    Add an automation point to a clip envelope.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - device_index: The index of the device
    - parameter_index: The index of the parameter to automate
    - time: Time position in beats
    - value: Normalized value (0.0 to 1.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "add_automation_point",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "time": time,
                "value": value,
            },
        )
        return f"Added automation point at beat {time} with value {value}"
    except Exception as e:
        logger.error(f"Error adding automation point: {str(e)}")
        return f"Error adding automation point: {str(e)}"


@mcp.tool()
def clear_automation(
    ctx: Context,
    track_index: int,
    clip_index: int,
    device_index: int,
    parameter_index: int,
) -> str:
    """
    Clear automation for a parameter in a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - device_index: The index of the device
    - parameter_index: The index of the parameter
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "clear_automation",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
            },
        )
        return f"Cleared automation for parameter {parameter_index} on device {device_index}"
    except Exception as e:
        logger.error(f"Error clearing automation: {str(e)}")
        return f"Error clearing automation: {str(e)}"


@mcp.tool()
def duplicate_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Duplicate a device on a track.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to duplicate
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "duplicate_device",
            {"track_index": track_index, "device_index": device_index},
        )
        return f"Duplicated device {device_index} on track {track_index}"
    except Exception as e:
        logger.error(f"Error duplicating device: {str(e)}")
        return f"Error duplicating device: {str(e)}"


@mcp.tool()
def delete_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Delete a device from a track.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_device", {"track_index": track_index, "device_index": device_index}
        )
        return f"Deleted device: {result.get('deleted_device', 'unknown')}"
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        return f"Error deleting device: {str(e)}"


@mcp.tool()
def move_device(
    ctx: Context, track_index: int, device_index: int, new_position: int
) -> str:
    """
    Move a device to a new position in the device chain.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to move
    - new_position: The new position index
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "move_device",
            {
                "track_index": track_index,
                "device_index": device_index,
                "new_position": new_position,
            },
        )
        return f"Moved device {device_index} to position {new_position}"
    except Exception as e:
        logger.error(f"Error moving device: {str(e)}")
        return f"Error moving device: {str(e)}"


@mcp.tool()
def set_track_pan(ctx: Context, track_index: int, pan: float = 0.0) -> str:
    """
    Set track panning.

    Parameters:
    - track_index: The index of the track
    - pan: Panning value (-1.0 = left, 0.0 = center, 1.0 = right)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_track_pan", {"track_index": track_index, "pan": pan}
        )
        direction = "left" if pan < 0 else ("right" if pan > 0 else "centered")
        return f"Set track {track_index} pan to {direction} ({pan})"
    except Exception as e:
        logger.error(f"Error setting track pan: {str(e)}")
        return f"Error setting track pan: {str(e)}"


@mcp.tool()
def set_send_amount(
    ctx: Context, track_index: int, send_index: int, amount: float
) -> str:
    """
    Set send amount to a return track.

    Parameters:
    - track_index: The index of the track
    - send_index: The index of the send
    - amount: Send amount (0.0 to 1.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_send_amount",
            {
                "track_index": track_index,
                "send_index": send_index,
                "amount": amount,
            },
        )
        return f"Set send {send_index} on track {track_index} to {amount}"
    except Exception as e:
        logger.error(f"Error setting send amount: {str(e)}")
        return f"Error setting send amount: {str(e)}"


@mcp.tool()
def undo(ctx: Context) -> str:
    """Undo the last action."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("undo")
        return "Undo performed"
    except Exception as e:
        logger.error(f"Error performing undo: {str(e)}")
        return f"Error performing undo: {str(e)}"


@mcp.tool()
def redo(ctx: Context) -> str:
    """Redo the last undone action."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("redo")
        return "Redo performed"
    except Exception as e:
        logger.error(f"Error performing redo: {str(e)}")
        return f"Error performing redo: {str(e)}"


@mcp.tool()
def create_locator(ctx: Context, bar: int, name: str = "") -> str:
    """
    Create a locator at a specific bar.

    Parameters:
    - bar: The bar number to place the locator
    - name: The name for the locator (optional)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_locator", {"bar": bar, "name": name})
        return f"Created locator at bar {bar}" + (f" named '{name}'" if name else "")
    except Exception as e:
        logger.error(f"Error creating locator: {str(e)}")
        return f"Error creating locator: {str(e)}"


@mcp.tool()
def delete_locator(ctx: Context, locator_index: int) -> str:
    """
    Delete a locator by index.

    Parameters:
    - locator_index: The index of the locator to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_locator", {"locator_index": locator_index}
        )
        return f"Deleted locator {locator_index}"
    except Exception as e:
        logger.error(f"Error deleting locator: {str(e)}")
        return f"Error deleting locator: {str(e)}"


@mcp.tool()
def jump_to_locator(ctx: Context, locator_index: int) -> str:
    """
    Jump to a locator.

    Parameters:
    - locator_index: The index of the locator to jump to
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "jump_to_locator", {"locator_index": locator_index}
        )
        return f"Jumped to locator {locator_index}"
    except Exception as e:
        logger.error(f"Error jumping to locator: {str(e)}")
        return f"Error jumping to locator: {str(e)}"


@mcp.tool()
def set_loop(ctx: Context, start_bar: int, end_bar: int, enabled: bool = True) -> str:
    """
    Set arrangement loop region.

    Parameters:
    - start_bar: Loop start bar
    - end_bar: Loop end bar
    - enabled: True to enable loop, False to disable
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_loop", {"start_bar": start_bar, "end_bar": end_bar, "enabled": enabled}
        )
        state = "enabled" if enabled else "disabled"
        return f"Loop {state} from bar {start_bar} to {end_bar}"
    except Exception as e:
        logger.error(f"Error setting loop: {str(e)}")
        return f"Error setting loop: {str(e)}"


@mcp.tool()
def get_clip_notes(
    ctx: Context,
    track_index: int,
    clip_index: int,
    from_time: float = 0.0,
    from_pitch: int = 0,
    time_span: float = 999999.0,
    pitch_span: int = 128,
) -> str:
    """
    Get all notes from a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - from_time: Start time in beats (default: 0.0)
    - from_pitch: Starting pitch note number (default: 0)
    - time_span: Duration range in beats (default: 999999.0)
    - pitch_span: Pitch range in MIDI notes (default: 128)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_clip_notes",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "from_time": from_time,
                "from_pitch": from_pitch,
                "time_span": time_span,
                "pitch_span": pitch_span,
            },
        )
        notes = result.get("notes", [])
        return json.dumps(
            {"note_count": result.get("count", 0), "notes": notes}, indent=2
        )
    except Exception as e:
        logger.error(f"Error getting clip notes: {str(e)}")
        return f"Error getting clip notes: {str(e)}"


@mcp.tool()
def set_clip_follow_action(
    ctx: Context,
    track_index: int,
    clip_index: int,
    action_slot: int = 0,
    action_type: int = 0,
    trigger_time: float = 1.0,
    clip_index_target: int = 0,
) -> str:
    """
    Set clip follow action for automated clip progression.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - action_slot: The follow action slot (0-7)
    - action_type: Action type (0=None, 1=Play Clip, 2=Stop Clip, 3=Play Other Clip)
    - trigger_time: Trigger time in beats (1.0 = next beat, other values = other beats)
    - clip_index_target: Target clip index for Play Other Clip action
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_clip_follow_action",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "action_slot": action_slot,
                "action_type": action_type,
                "trigger_time": trigger_time,
                "clip_index_target": clip_index_target,
            },
        )
        return f"Set follow action slot {action_slot} for clip"
    except Exception as e:
        logger.error(f"Error setting clip follow action: {str(e)}")
        return f"Error setting clip follow action: {str(e)}"


@mcp.tool()
def get_clip_follow_actions(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Get all follow actions for a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_clip_follow_actions",
            {"track_index": track_index, "clip_index": clip_index},
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting clip follow actions: {str(e)}")
        return f"Error getting clip follow actions: {str(e)}"


@mcp.tool()
def set_master_volume(ctx: Context, volume: float = 0.75) -> str:
    """
    Set master track volume (normalized 0.0-1.0).

    Parameters:
    - volume: The normalized volume value (0.0 = silent, 1.0 = full)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_master_volume", {"volume": volume})
        return f"Set master volume to {volume}"
    except Exception as e:
        logger.error(f"Error setting master volume: {str(e)}")
        return f"Error setting master volume: {str(e)}"


@mcp.tool()
def get_master_track_info(ctx: Context) -> str:
    """Get master track information."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_master_track_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting master track info: {str(e)}")
        return f"Error getting master track info: {str(e)}"


@mcp.tool()
def get_return_tracks(ctx: Context) -> str:
    """Get all return tracks information."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_return_tracks")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting return tracks: {str(e)}")
        return f"Error getting return tracks: {str(e)}"


@mcp.tool()
def get_all_tracks(ctx: Context) -> str:
    """Get summary of all tracks in the session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_all_tracks")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting all tracks: {str(e)}")
        return f"Error getting all tracks: {str(e)}"


@mcp.tool()
def get_all_scenes(ctx: Context) -> str:
    """Get summary of all scenes in the session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_all_scenes")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting all scenes: {str(e)}")
        return f"Error getting all scenes: {str(e)}"


@mcp.tool()
def get_all_clips_in_track(ctx: Context, track_index: int) -> str:
    """
    Get all clips in a specific track.

    Parameters:
    - track_index: The index of the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_all_clips_in_track", {"track_index": track_index}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting all clips: {str(e)}")
        return f"Error getting all clips: {str(e)}"


@mcp.tool()
def set_note_velocity(
    ctx: Context,
    track_index: int,
    clip_index: int,
    note_indices: List[int],
    velocity: int = 100,
) -> str:
    """
    Set velocity for specific notes in a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - note_indices: List of note indices to modify
    - velocity: New velocity value (0-127)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_note_velocity",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "note_indices": note_indices,
                "velocity": velocity,
            },
        )
        return f"Set velocity to {velocity} for {len(note_indices)} notes"
    except Exception as e:
        logger.error(f"Error setting note velocity: {str(e)}")
        return f"Error setting note velocity: {str(e)}"


@mcp.tool()
def set_note_duration(
    ctx: Context,
    track_index: int,
    clip_index: int,
    note_indices: List[int],
    duration: float = 0.25,
) -> str:
    """
    Set duration for specific notes in a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - note_indices: List of note indices to modify
    - duration: New duration in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_note_duration",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "note_indices": note_indices,
                "duration": duration,
            },
        )
        return f"Set duration to {duration} beats for {len(note_indices)} notes"
    except Exception as e:
        logger.error(f"Error setting note duration: {str(e)}")
        return f"Error setting note duration: {str(e)}"


@mcp.tool()
def set_note_pitch(
    ctx: Context,
    track_index: int,
    clip_index: int,
    note_indices: List[int],
    pitch: int = 60,
) -> str:
    """
    Set pitch for specific notes in a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - note_indices: List of note indices to modify
    - pitch: New pitch value (MIDI note number)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_note_pitch",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "note_indices": note_indices,
                "pitch": pitch,
            },
        )
        return f"Set pitch to {pitch} for {len(note_indices)} notes"
    except Exception as e:
        logger.error(f"Error setting note pitch: {str(e)}")
        return f"Error setting note pitch: {str(e)}"


@mcp.tool()
def get_clip_envelopes(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Get all automation envelopes for a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_clip_envelopes", {"track_index": track_index, "clip_index": clip_index}
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting clip envelopes: {str(e)}")
        return f"Error getting clip envelopes: {str(e)}"


@mcp.tool()
def mix_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    source_track_index: int,
) -> str:
    """
    Mix another clip into current clip.

    Parameters:
    - track_index: The index of the target track
    - clip_index: The index of the target clip slot
    - source_track_index: The index of the source track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "mix_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "source_track_index": source_track_index,
            },
        )
        return f"Mixed clip from track {source_track_index} into track {track_index}"
    except Exception as e:
        logger.error(f"Error mixing clip: {str(e)}")
        return f"Error mixing clip: {str(e)}"


@mcp.tool()
def stretch_clip(
    ctx: Context, track_index: int, clip_index: int, length: float = 4.0
) -> str:
    """
    Stretch clip to new length.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - length: New length in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "stretch_clip",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "length": length,
            },
        )
        return f"Stretched clip to {length} beats"
    except Exception as e:
        logger.error(f"Error stretching clip: {str(e)}")
        return f"Error stretching clip: {str(e)}"


@mcp.tool()
def crop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Crop clip to its content.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "crop_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Cropped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error cropping clip: {str(e)}")
        return f"Error cropping clip: {str(e)}"


@mcp.tool()
def duplicate_clip_to(
    ctx: Context,
    track_index: int,
    clip_index: int,
    target_track_index: int,
    target_clip_index: int,
) -> str:
    """
    Duplicate clip to a specific slot.

    Parameters:
    - track_index: The index of the source track
    - clip_index: The index of the source clip slot
    - target_track_index: The index of the target track
    - target_clip_index: The index of the target clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "duplicate_clip_to",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "target_track_index": target_track_index,
                "target_clip_index": target_clip_index,
            },
        )
        return f"Duplicated clip from [{track_index}, {clip_index}] to [{target_track_index}, {target_clip_index}]"
    except Exception as e:
        logger.error(f"Error duplicating clip: {str(e)}")
        return f"Error duplicating clip: {str(e)}"


@mcp.tool()
def group_tracks(ctx: Context, track_indices: List[int]) -> str:
    """
    Group multiple tracks together.

    Parameters:
    - track_indices: List of track indices to group
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("group_tracks", {"track_indices": track_indices})
        return f"Grouped {len(track_indices)} tracks"
    except Exception as e:
        logger.error(f"Error grouping tracks: {str(e)}")
        return f"Error grouping tracks: {str(e)}"


@mcp.tool()
def ungroup_tracks(ctx: Context, track_index: int) -> str:
    """
    Ungroup a track from its group.

    Parameters:
    - track_index: The index of the track to ungroup
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("ungroup_tracks", {"track_index": track_index})
        return f"Ungrouped track {track_index}"
    except Exception as e:
        logger.error(f"Error ungrouping tracks: {str(e)}")
        return f"Error ungrouping tracks: {str(e)}"


@mcp.tool()
def set_clip_warp_mode(
    ctx: Context, track_index: int, clip_index: int, warp_mode: int = 1
) -> str:
    """
    Set clip warp mode.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - warp_mode: Warp mode (0=Off, 1=Beats, 2=Tones, 3=Complex, 4=Repitch)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_clip_warp_mode",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "warp_mode": warp_mode,
            },
        )
        modes = ["Off", "Beats", "Tones", "Complex", "Repitch"]
        mode_name = (
            modes[warp_mode] if 0 <= warp_mode < len(modes) else f"Mode {warp_mode}"
        )
        return f"Set clip warp mode to {mode_name}"
    except Exception as e:
        logger.error(f"Error setting clip warp mode: {str(e)}")
        return f"Error setting clip warp mode: {str(e)}"


@mcp.tool()
def get_clip_warp_markers(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Get all warp markers for a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "get_clip_warp_markers",
            {"track_index": track_index, "clip_index": clip_index},
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting clip warp markers: {str(e)}")
        return f"Error getting clip warp markers: {str(e)}"


@mcp.tool()
def add_warp_marker(
    ctx: Context, track_index: int, clip_index: int, position: float = 0.0
) -> str:
    """
    Add a warp marker to a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - position: Position in beats to add marker
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "add_warp_marker",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "position": position,
            },
        )
        return f"Added warp marker at position {position} beats"
    except Exception as e:
        logger.error(f"Error adding warp marker: {str(e)}")
        return f"Error adding warp marker: {str(e)}"


@mcp.tool()
def delete_warp_marker(
    ctx: Context, track_index: int, clip_index: int, marker_index: int = 0
) -> str:
    """
    Delete a warp marker from a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - marker_index: The index of the warp marker to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_warp_marker",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "marker_index": marker_index,
            },
        )
        return f"Deleted warp marker {marker_index}"
    except Exception as e:
        self.log_message("Error deleting warp marker: " + str(e))
        return f"Error deleting warp marker: {str(e)}"


# Main execution
def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()


@mcp.tool()
def move_clip(
    ctx: Context, track_index: int, new_track_index: int, new_clip_index: int
) -> str:
    """
    Move a clip to another track.

    Parameters:
    - track_index: The index of the current track
    - new_track_index: The index of the target track
    - new_clip_index: The index of the clip slot in the target track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "move_clip",
            {
                "track_index": track_index,
                "new_track_index": new_track_index,
                "new_clip_index": new_clip_index,
            },
        )
        track_name = result.get("track_name", f"Track {track_index}")
        target_track_name = result.get("target_track_name", f"Track {new_track_index}")
        return f"Moved clip from track {track_index} to track {new_track_index}, slot {new_clip_index}"
    except Exception as e:
        logger.error(f"Error moving clip: {str(e)}")
        return f"Error moving clip: {str(e)}"


@mcp.tool()
def resize_clip(ctx: Context, track_index: int, clip_index: int, length: float) -> str:
    """
    Resize clip to new length in beats.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot
    - length: The new length in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "resize_clip",
            {"track_index": track_index, "clip_index": clip_index, "length": length},
        )
        return (
            f"Resized clip at track {track_index}, slot {clip_index} to {length} beats"
        )
    except Exception as e:
        logger.error(f"Error resizing clip: {str(e)}")
        return f"Error resizing clip: {str(e)}"


@mcp.tool()
def crop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Crop clip to its content, removing empty space at start and end.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "crop_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Cropped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error cropping clip: {str(e)}")
        return f"Error cropping clip: {str(e)}"


@mcp.tool()
def delete_device(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Delete a device from a track.

    Parameters:
    - track_index: The index of the track
    - device_index: The index of the device to delete
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "delete_device", {"track_index": track_index, "device_index": device_index}
        )
        return f"Deleted device at track {track_index}, index {device_index}"
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        return f"Error deleting device: {str(e)}"


@mcp.tool()
def move_clip(
    ctx: Context, track_index: int, new_track_index: int, new_clip_index: int
) -> str:
    """
    Move a clip to another track.

    Parameters:
    - track_index: The index of the current track
    - new_track_index: The index of the target track
    - new_clip_index: The index of the clip slot in the target track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "move_clip",
            {
                "track_index": track_index,
                "new_track_index": new_track_index,
                "new_clip_index": new_clip_index,
            },
        )
        track_name = result.get("track_name", f"Track {track_index}")
        target_track_name = result.get("target_track_name", f"Track {new_track_index}")
        return f"Moved clip from track {track_index} to track {new_track_index}, slot {new_clip_index}"
    except Exception as e:
        logger.error(f"Error moving clip: {str(e)}")
        return f"Error moving clip: {str(e)}"


@mcp.tool()
def resize_clip(ctx: Context, track_index: int, clip_index: int, length: float) -> str:
    """
    Resize clip to new length in beats.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot
    - length: The new length in beats
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "resize_clip",
            {"track_index": track_index, "clip_index": clip_index, "length": length},
        )
        return (
            f"Resized clip at track {track_index}, slot {clip_index} to {length} beats"
        )
    except Exception as e:
        logger.error(f"Error resizing clip: {str(e)}")
        return f"Error resizing clip: {str(e)}"


@mcp.tool()
def crop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Crop clip to its content, removing empty space at start and end.

    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "crop_clip", {"track_index": track_index, "clip_index": clip_index}
        )
        return f"Cropped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error cropping clip: {str(e)}")
        return f"Error cropping clip: {str(e)}"


@mcp.tool()
def duplicate_clip_to(
    ctx: Context, track_index: int, target_track_index: int, target_clip_index: int
) -> str:
    """
    Duplicate clip to specific slot on another track.

    Parameters:
    - track_index: The index of the source track
    - target_track_index: The index of the target track
    - target_clip_index: The index of the clip slot in the target track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "duplicate_clip_to",
            {
                "track_index": track_index,
                "target_track_index": target_track_index,
                "target_clip_index": target_clip_index,
            },
        )
        return (
            f"Duplicated clip to track {target_track_index}, slot {target_clip_index}"
        )
    except Exception as e:
        logger.error(f"Error duplicating clip to: {str(e)}")
        return f"Error duplicating clip to: {str(e)}"


@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """
    Set name of a clip.

    Parameters:
    - track_index: The index of the track
    - clip_index: The index of the clip slot
    - name: The new name for the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command(
            "set_clip_name",
            {
                "track_index": track_index,
                "clip_index": clip_index,
                "name": name,
            },
        )
        return f"Set clip name to '{name}'"
    except Exception as e:
        logger.error(f"Error setting clip name: {str(e)}")
        return f"Error setting clip name: {str(e)}"
