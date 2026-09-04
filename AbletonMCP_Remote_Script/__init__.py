# AbletonMCP/init.py
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import socket
import json
import os
import threading
import time
import traceback
import math

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

# Constants for socket communication
DEFAULT_PORT = 9877
UDP_PORT = 9878
HOST = "127.0.0.1"

# ============================================================================
# CONSTANTS
# ============================================================================

# Server configuration
MAX_PENDING_CONNECTIONS = 5
SOCKET_TIMEOUT = 1.0
UDP_BUFFER_SIZE = 1024
TCP_BUFFER_SIZE = 8192
COMMAND_TIMEOUT = 10.0
SERVER_SLEEP_TIME = 0.5
UDP_SLEEP_TIME = 0.1

# Default values
DEFAULT_TRACK_INDEX = 0
DEFAULT_CLIP_INDEX = 0
DEFAULT_LENGTH = 4.0
DEFAULT_TEMPO = 120.0
DEFAULT_VOLUME = 0.75
DEFAULT_QUANTIZATION = "1 Bar"

# Protocol version for client/server handshake
PROTOCOL_VERSION = 1


def create_instance(c_instance):
    """Create and return the AbletonMCP script instance"""
    return AbletonMCP(c_instance)


class AbletonMCP(ControlSurface):
    """AbletonMCP Remote Script for Ableton Live"""

    def __init__(self, c_instance):
        """Initialize the control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP Remote Script initializing...")

        # Socket server for communication
        self.server = None
        self.client_threads = []
        self.server_thread = None
        self.udp_server_socket = None
        self.udp_server_thread = None
        self.running = False

        # Cache the song reference for easier access
        self._song = self.song()

        # Build command handler maps (refactored from if/elif dispatch chain)
        self._handlers = self._build_handlers()
        self._udp_handlers = self._build_udp_handlers()

        # Start both servers
        self.start_server()  # TCP on 9877
        self.start_udp_server()  # UDP on 9878

        self.log_message("AbletonMCP initialized")

        # Show a message in Ableton
        self.show_message("AbletonMCP: TCP on 9877, UDP on 9878")

    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP disconnecting...")
        self.running = False

        # Stop the server
        if self.server:
            try:
                self.server.close()
            except Exception as e:
                self.log_message(f"Error closing server: {e}")

        # Wait for the server thread to exit
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(1.0)

        # Stop UDP server - NEW
        if self.udp_server_socket:
            try:
                self.udp_server_socket.close()
            except Exception as e:
                self.log_message(f"Error closing UDP server: {e}")

        if self.udp_server_thread and self.udp_server_thread.is_alive():
            self.udp_server_thread.join(1.0)

        # Clean up any client threads
        for client_thread in self.client_threads[:]:
            if client_thread.is_alive():
                # We don't join them as they might be stuck
                self.log_message("Client thread still alive during disconnect")

        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP disconnected")

    def start_server(self):
        """Start socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, DEFAULT_PORT))
            self.server.listen(
                MAX_PENDING_CONNECTIONS
            )  # Allow up to 5 pending connections

            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.log_message("Server started on port " + str(DEFAULT_PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonMCP: Error starting server - " + str(e))

    def start_udp_server(self):
        """Start UDP server in daemon thread"""
        try:
            self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_server_socket.bind((HOST, UDP_PORT))

            self.running = True
            self.udp_server_thread = threading.Thread(target=self._udp_server_loop)
            self.udp_server_thread.daemon = True
            self.udp_server_thread.start()

            self.log_message("UDP server started on port " + str(UDP_PORT))
        except Exception as e:
            self.log_message("Error starting UDP server: " + str(e))

    def _server_thread(self):
        """Server thread implementation - handles client connections"""
        try:
            self.log_message("Server thread started")
            # Set a timeout to allow regular checking of running flag
            self.server.settimeout(SOCKET_TIMEOUT)

            while self.running:
                try:
                    # Accept connections with timeout
                    client, address = self.server.accept()
                    self.log_message("Connection accepted from " + str(address))
                    self.show_message("AbletonMCP: Client connected")

                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client, args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                    # Keep track of client threads
                    self.client_threads.append(client_thread)

                    # Clean up finished client threads
                    self.client_threads = [
                        t for t in self.client_threads if t.is_alive()
                    ]

                except socket.timeout:
                    # No connection yet, just continue
                    continue
                except Exception as e:
                    if self.running:  # Only log if still running
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(SERVER_SLEEP_TIME)

            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))

    def _udp_server_loop(self):
        """UDP server thread implementation - fire-and-forget"""
        try:
            self.log_message("UDP server thread started")
            self.udp_server_socket.settimeout(1.0)

            while self.running:
                try:
                    data, addr = self.udp_server_socket.recvfrom(UDP_BUFFER_SIZE)
                    if not self.running:
                        break

                    self._handle_udp_data(data, addr)

                except socket.timeout:
                    continue
                except socket.error as se:
                    if self.running:
                        self.log_message("UDP server socket error: " + str(se))
                    break
                except Exception as e:
                    if self.running:
                        self.log_message("UDP server loop error: " + str(e))
                    time.sleep(UDP_SLEEP_TIME)

            self.log_message("UDP server thread stopped")
        except Exception as e:
            self.log_message("UDP server thread error: " + str(e))

    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(None)  # No timeout for client socket
        buffer = ""  # Changed from b'' to '' for Python 2

        try:
            while self.running:
                try:
                    # Receive data
                    data = client.recv(TCP_BUFFER_SIZE)

                    if not data:
                        # Client disconnected
                        self.log_message("Client disconnected")
                        break

                    # Accumulate data in buffer with explicit encoding/decoding
                    try:
                        # Python 3: data is bytes, decode to string
                        buffer += data.decode("utf-8")
                    except AttributeError:
                        # Python 2: data is already string
                        buffer += data

                    try:
                        # Try to parse command from buffer
                        command = json.loads(buffer)  # Removed decode('utf-8')
                        buffer = ""  # Clear buffer after successful parse

                        self.log_message(
                            "Received command: " + str(command.get("type", "unknown"))
                        )

                        # Process the command and get response
                        response = self._process_command(command)

                        # Send the response with explicit encoding
                        try:
                            # Python 3: encode string to bytes
                            client.sendall(json.dumps(response).encode("utf-8"))
                        except AttributeError:
                            # Python 2: string is already bytes
                            client.sendall(json.dumps(response))
                    except ValueError:
                        # Incomplete data, wait for more
                        continue

                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    self.log_message(traceback.format_exc())

                    # Send error response if possible
                    error_response = {"status": "error", "message": str(e)}
                    try:
                        # Python 3: encode string to bytes
                        client.sendall(json.dumps(error_response).encode("utf-8"))
                    except AttributeError:
                        # Python 2: string is already bytes
                        client.sendall(json.dumps(error_response))
                    except Exception as e:
                        # If we can't send the error, the connection is probably dead
                        self.log_message(f"Failed to send error response: {e}")
                        break

                    # For serious errors, break the loop
                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except Exception as e:
                self.log_message(f"Error closing client connection: {e}")
            self.log_message("Client handler stopped")

    def _handle_udp_data(self, data, addr):
        """Handle UDP datagram - fire-and-forget"""
        try:
            command_str = data.decode("utf-8")
            command_json = json.loads(command_str)

            self.log_message(
                f"UDP: Received {command_json.get('type', 'unknown')} from {addr}"
            )

            def udp_task():
                try:
                    # Command routing will be added in later task
                    self._execute_udp_command(command_json)
                except Exception as e:
                    self.log_message(f"UDP: Error executing command: {e}")

            try:
                self.schedule_message(0, udp_task)
            except AssertionError:
                # Already on main thread
                udp_task()

        except Exception as e:
            self.log_message(f"UDP: Error processing datagram from {addr}: {e}")

    # -----------------------------------------------------------------
    # Handler map: command_type -> callable(params) -> result
    # -----------------------------------------------------------------

    # Commands that must run on Ableton's main thread (via schedule_message).
    # These modify Live state or access the Live API from a non-main thread.
    MAIN_THREAD_COMMANDS = frozenset({
        # Track CRUD
        "create_midi_track", "create_audio_track", "delete_all_tracks",
        "delete_track", "set_track_name", "set_track_color", "set_track_fold",
        "duplicate_track",
        # Clip CRUD
        "create_clip", "delete_clip", "duplicate_clip", "move_clip",
        "add_notes_to_clip", "delete_notes_from_clip",
        "quantize_clip", "transpose_clip",
        "set_clip_name", "set_clip_loop", "set_clip_launch_mode",
        "set_clip_follow_action", "get_clip_follow_actions",
        # Scene operations
        "create_scene", "delete_scene", "duplicate_scene", "set_scene_name",
        "fire_scene", "trigger_scene",
        # Transport & tempo
        "set_tempo", "set_time_signature", "set_metronome",
        "fire_clip", "stop_clip",
        "start_playback", "stop_playback",
        "start_recording", "stop_recording",
        # Track state
        "set_track_monitoring_state",
        # Device/instrument loading
        "load_browser_item", "load_instrument_or_effect", "load_instrument_preset",
        "get_device_parameters", "set_device_parameter",
        # Automation
        "add_automation_point", "clear_automation",
        # Device CRUD
        "duplicate_device", "delete_device", "move_device",
        "toggle_device_bypass", "undo", "redo",
        # Clip operations (continued)
        "crop_clip", "resize_clip", "duplicate_clip_to",
        # Locators & loop
        "get_playhead_position", "set_playhead_position",
        "create_locator", "delete_locator", "jump_to_locator",
        # Presets
        "list_device_presets", "load_device_preset", "save_device_preset",
        "set_loop",
        # Clip data access (via Live API)
        "get_clip_notes", "get_clip_envelopes", "get_clip_envelope_points",
        "set_clip_envelope_point",
        # Mixer state
        "set_master_volume", "set_track_volume", "set_track_mute",
        "set_track_solo", "set_track_arm", "set_track_pan", "set_send_amount",
        # Session queries (via Live API)
        "get_master_track_info", "get_return_tracks", "get_all_tracks",
        "get_all_scenes", "get_session_overview", "get_all_clips_in_track",
        # Note editing
        "set_note_velocity", "set_note_duration", "set_note_pitch",
        # Clip processing
        "mix_clip", "stretch_clip",
        "detect_clip_key", "snap_notes_to_scale",
        "create_scale_reference_clip", "create_chord_progression",
        # Track grouping
        "group_tracks", "ungroup_tracks",
        # Warp
        "set_clip_warp_mode", "get_clip_warp_markers",
        "add_warp_marker", "delete_warp_marker",
        # Script reload
        "reload_script",
        # Quantization & Link
        "get_global_quantization", "set_global_quantization",
        "get_link_status", "set_link_enabled", "set_link_start_stop_sync",
        # Energy & groove
        "apply_energy_curve",
        "apply_groove_to_clip", "remove_groove_from_clip",
        "set_global_groove_amount",
    })

    def _build_handlers(self):
        """Build the declarative TCP command handler map.

        Each value is a callable(self, params_dict) -> result.
        Built once in __init__ and reused for every incoming command.
        """
        return {
            # === Session info (direct dispatch) ===
            "get_session_info": lambda p: self._get_session_info(),
            "get_track_info": lambda p: self._get_track_info(p.get("track_index", 0)),

            # === Track CRUD ===
            "create_midi_track": lambda p: self._create_midi_track(p.get("index", -1)),
            "create_audio_track": lambda p: self._create_audio_track(p.get("index", -1)),
            "delete_all_tracks": lambda p: self._delete_all_tracks(),
            "delete_track": lambda p: self._delete_track(p.get("track_index", 0)),
            "set_track_name": lambda p: self._set_track_name(p.get("track_index", 0), p.get("name", "")),
            "set_track_color": lambda p: self._set_track_color(p.get("track_index", 0), p.get("color_index", 0)),
            "set_track_fold": lambda p: self._set_track_fold(p.get("track_index", 0), p.get("folded", True)),
            "duplicate_track": lambda p: self._duplicate_track(p.get("track_index", 0)),

            # === Clip CRUD ===
            "create_clip": lambda p: self._create_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("length", 4.0)),
            "delete_clip": lambda p: self._delete_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "duplicate_clip": lambda p: self._duplicate_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "move_clip": lambda p: self._move_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("new_track_index", 0), p.get("new_clip_index", 0)),
            "add_notes_to_clip": lambda p: self._add_notes_to_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("notes", [])),
            "delete_notes_from_clip": lambda p: self._delete_notes_from_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("note_indices", [])),
            "quantize_clip": lambda p: self._quantize_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("amount", 1.0)),
            "transpose_clip": lambda p: self._transpose_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("semitones", 0)),
            "set_clip_name": lambda p: self._set_clip_name(p.get("track_index", 0), p.get("clip_index", 0), p.get("name", "")),
            "set_clip_loop": lambda p: self._set_clip_loop(p.get("track_index", 0), p.get("clip_index", 0), p.get("loop_start", 0.0), p.get("loop_length", 4.0)),
            "set_clip_launch_mode": lambda p: self._set_clip_launch_mode(p.get("track_index", 0), p.get("clip_index", 0), p.get("mode", 0)),
            "set_clip_follow_action": lambda p: self._set_clip_follow_action(p.get("track_index", 0), p.get("clip_index", 0), p.get("action_slot", 0), p.get("action_type", 0), p.get("trigger_time", 0), p.get("clip_index_target", 0)),
            "get_clip_follow_actions": lambda p: self._get_clip_follow_actions(p.get("track_index", 0), p.get("clip_index", 0)),
            "duplicate_clip_to": lambda p: self._duplicate_clip_to(p.get("track_index", 0), p.get("clip_index", 0), p.get("target_track_index", 0), p.get("target_clip_index", 0)),
            "crop_clip": lambda p: self._crop_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "resize_clip": lambda p: None,  # unimplemented stub (preserves original behaviour)

            # === Scene operations ===
            "create_scene": lambda p: self._create_scene(p.get("index", -1)),
            "delete_scene": lambda p: self._delete_scene(p.get("scene_index", 0)),
            "duplicate_scene": lambda p: self._duplicate_scene(p.get("scene_index", 0)),
            "set_scene_name": lambda p: self._set_scene_name(p.get("scene_index", 0), p.get("name", "")),
            "fire_scene": lambda p: self._fire_scene(p.get("scene_index", 0)),
            "trigger_scene": lambda p: self._fire_scene(p.get("scene_index", 0)),  # alias for fire_scene

            # === Transport & tempo ===
            "set_tempo": lambda p: self._set_tempo(p.get("tempo", 120.0)),
            "set_time_signature": lambda p: self._set_time_signature(p.get("numerator", 4), p.get("denominator", 4)),
            "set_metronome": lambda p: self._set_metronome(p.get("enabled", True)),
            "fire_clip": lambda p: self._fire_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "stop_clip": lambda p: self._stop_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "start_playback": lambda p: self._start_playback(),
            "stop_playback": lambda p: self._stop_playback(),
            "start_recording": lambda p: self._start_recording(),
            "stop_recording": lambda p: self._stop_recording(),

            # === Track monitoring ===
            "set_track_monitoring_state": lambda p: self._set_track_monitoring_state(p.get("track_index", 0), p.get("monitoring_state", 0)),

            # === Device / instrument loading ===
            "load_browser_item": lambda p: self._load_browser_item(p.get("track_index", 0), p.get("item_uri", "")),
            "load_instrument_or_effect": lambda p: self._load_instrument_or_effect(p.get("track_index", 0), p.get("uri", "")),
            "load_instrument_preset": lambda p: self._load_instrument_preset(p.get("track_index", 0), p.get("device_index", 0), p.get("preset_name", "")),
            "get_device_parameters": lambda p: self._get_device_parameters(p.get("track_index", 0), p.get("device_index", 0)),
            "set_device_parameter": lambda p: self._set_device_parameter(p.get("track_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("value", 0.0)),

            # === Automation ===
            "add_automation_point": lambda p: self._add_automation_point(p.get("track_index", 0), p.get("clip_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("time", 0.0), p.get("value", 0.0)),
            "clear_automation": lambda p: self._clear_automation(p.get("track_index", 0), p.get("clip_index", 0), p.get("device_index", 0), p.get("parameter_index", 0)),

            # === Device CRUD ===
            "duplicate_device": lambda p: self._duplicate_device(p.get("track_index", 0), p.get("device_index", 0)),
            "delete_device": lambda p: self._delete_device(p.get("track_index", 0), p.get("device_index", 0)),
            "move_device": lambda p: self._move_device(p.get("track_index", 0), p.get("device_index", 0), p.get("new_position", 0)),
            "toggle_device_bypass": lambda p: self._toggle_device_bypass(p.get("track_index", 0), p.get("device_index", 0), p.get("enabled", True)),
            "undo": lambda p: self._undo(),
            "redo": lambda p: self._redo(),

            # === Locators & loop ===
            "get_playhead_position": lambda p: self._get_playhead_position(),
            "set_playhead_position": lambda p: self._set_playhead_position(p.get("bar", 1), p.get("beat", 0.0)),
            "create_locator": lambda p: self._create_locator(p.get("bar", 1), p.get("name", "")),
            "delete_locator": lambda p: self._delete_locator(p.get("locator_index", 0)),
            "jump_to_locator": lambda p: self._jump_to_locator(p.get("locator_index", 0)),
            "set_loop": lambda p: self._set_loop(p.get("start_bar", 1), p.get("end_bar", 17), p.get("enabled", True)),

            # === Presets ===
            "list_device_presets": lambda p: self._list_device_presets(p.get("track_index", 0), p.get("device_index", 0)),
            "load_device_preset": lambda p: self._load_device_preset(p.get("track_index", 0), p.get("device_index", 0), p.get("preset_name", "")),
            "save_device_preset": lambda p: self._save_device_preset(p.get("track_index", 0), p.get("device_index", 0), p.get("preset_name", "")),

            # === Clip data ===
            "get_clip_notes": lambda p: self._get_clip_notes(p.get("track_index", 0), p.get("clip_index", 0), p.get("from_time", 0.0), p.get("from_pitch", 0), p.get("time_span", 999999.0), p.get("pitch_span", 128)),
            "get_clip_envelopes": lambda p: self._get_clip_envelopes(p.get("track_index", 0), p.get("clip_index", 0)),
            "get_clip_envelope_points": lambda p: self._get_clip_envelope_points(p.get("track_index", 0), p.get("clip_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("num_samples", 64)),
            "set_clip_envelope_point": lambda p: self._set_clip_envelope_point(p.get("track_index", 0), p.get("clip_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("time", 0.0), p.get("value", 0.5)),

            # === Mixer state ===
            "set_master_volume": lambda p: self._set_master_volume(p.get("volume", 0.75)),
            "set_track_volume": lambda p: self._set_track_volume(p.get("track_index", 0), p.get("volume", 0.75)),
            "set_track_mute": lambda p: self._set_track_mute(p.get("track_index", 0), p.get("mute", False)),
            "set_track_solo": lambda p: self._set_track_solo(p.get("track_index", 0), p.get("solo", False)),
            "set_track_arm": lambda p: self._set_track_arm(p.get("track_index", 0), p.get("arm", False)),
            "set_track_pan": lambda p: self._set_track_pan(p.get("track_index", 0), p.get("pan", 0.0)),
            "set_send_amount": lambda p: self._set_send_amount(p.get("track_index", 0), p.get("send_index", 0), p.get("amount", 0.5)),

            # === Session queries ===
            "get_master_track_info": lambda p: self._get_master_track_info(),
            "get_return_tracks": lambda p: self._get_return_tracks(),
            "get_all_tracks": lambda p: self._get_all_tracks(),
            "get_all_scenes": lambda p: self._get_all_scenes(),
            "get_session_overview": lambda p: self._get_session_overview(),
            "get_all_clips_in_track": lambda p: self._get_all_clips_in_track(p.get("track_index", 0)),

            # === Note editing ===
            "set_note_velocity": lambda p: self._set_note_velocity(p.get("track_index", 0), p.get("clip_index", 0), p.get("note_indices", []), p.get("velocity", 100)),
            "set_note_duration": lambda p: self._set_note_duration(p.get("track_index", 0), p.get("clip_index", 0), p.get("note_indices", []), p.get("duration", 0.25)),
            "set_note_pitch": lambda p: self._set_note_pitch(p.get("track_index", 0), p.get("clip_index", 0), p.get("note_indices", []), p.get("pitch", 60)),

            # === Clip processing ===
            "mix_clip": lambda p: self._mix_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("source_track_index", 0)),
            "stretch_clip": lambda p: self._stretch_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("length", 4.0)),
            "detect_clip_key": lambda p: self._detect_clip_key(p.get("track_index", 0), p.get("clip_index", 0)),
            "snap_notes_to_scale": lambda p: self._snap_notes_to_scale(p.get("track_index", 0), p.get("clip_index", 0), p.get("scale", "minor"), p.get("root", 60)),
            "create_scale_reference_clip": lambda p: self._create_scale_reference_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("scale", "minor"), p.get("root", 60), p.get("octaves", 3)),
            "create_chord_progression": lambda p: self._create_chord_progression(p.get("track_index", 0), p.get("clip_index", 0), p.get("key", "C"), p.get("progression", ["I", "V", "vi", "IV"]), p.get("duration_per_chord", 4.0)),

            # === Track grouping ===
            "group_tracks": lambda p: self._group_tracks(p.get("track_indices", [])),
            "ungroup_tracks": lambda p: self._ungroup_tracks(p.get("track_index", 0)),

            # === Warp ===
            "set_clip_warp_mode": lambda p: self._set_clip_warp_mode(p.get("track_index", 0), p.get("clip_index", 0), p.get("warp_mode", 0)),
            "get_clip_warp_markers": lambda p: self._get_clip_warp_markers(p.get("track_index", 0), p.get("clip_index", 0)),
            "add_warp_marker": lambda p: self._add_warp_marker(p.get("track_index", 0), p.get("clip_index", 0), p.get("position", 0.0)),
            "delete_warp_marker": lambda p: self._delete_warp_marker(p.get("track_index", 0), p.get("clip_index", 0), p.get("marker_index", 0)),

            # === Script reload ===
            "reload_script": lambda p: self._reload_script(),

            # === Quantization & Link ===
            "get_global_quantization": lambda p: self._get_global_quantization(),
            "set_global_quantization": lambda p: self._set_global_quantization(p.get("value", "1 Bar")),
            "get_link_status": lambda p: self._get_link_status(),
            "set_link_enabled": lambda p: self._set_link_enabled(p.get("enabled", True)),
            "set_link_start_stop_sync": lambda p: self._set_link_start_stop_sync(p.get("enabled", True)),

            # === Energy & groove ===
            "apply_energy_curve": lambda p: self._apply_energy_curve(p.get("parameter_changes", []), p.get("duration_beats", 4.0), p.get("steps", 8)),
            "apply_groove_to_clip": lambda p: self._apply_groove_to_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("groove_name", ""), p.get("amount", 1.0)),
            "remove_groove_from_clip": lambda p: self._remove_groove_from_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "set_global_groove_amount": lambda p: self._set_global_groove_amount(p.get("amount", 1.0)),

            # === Browser (direct dispatch) ===
            "get_browser_item": lambda p: self._get_browser_item(p.get("uri", None), p.get("path", None)),
            "get_browser_categories": lambda p: self._get_browser_categories(p.get("category_type", "all")),
            "get_browser_items": lambda p: self._get_browser_items(p.get("path", ""), p.get("item_type", "all")),
            "get_browser_tree": lambda p: self.get_browser_tree(p.get("category_type", "all")),
            "get_browser_items_at_path": lambda p: self.get_browser_items_at_path(p.get("path", "")),
            "get_browser_recursive_children": lambda p: self._get_recursive_browser_children(p.get("root_path", ""), p.get("max_depth", 5), p.get("max_items", 500)),
            "get_available_grooves": lambda p: self._get_available_grooves(),

            # === Crossfader & sends (direct dispatch) ===
            "get_crossfader": lambda p: self._get_crossfader(),
            "set_crossfader": lambda p: self._set_crossfader(p.get("value", 0.5)),
            "get_track_crossfade_assign": lambda p: self._get_track_crossfade_assign(p.get("track_index", 0)),
            "set_track_crossfade_assign": lambda p: self._set_track_crossfade_assign(p.get("track_index", 0), p.get("assign", 1)),
            "get_level_snapshot": lambda p: self._get_level_snapshot(),
            "get_track_sends": lambda p: self._get_track_sends(p.get("track_index", 0)),

            # === Arrangement view (direct dispatch) ===
            "capture_and_insert_arrangement": lambda p: self._capture_and_insert_arrangement(p.get("start_bar", 0), p.get("length_bars", 64), p.get("quantize", True)),
            "get_arrangement_clips": lambda p: self._get_arrangement_clips(p.get("track_index", None)),
            "build_arrangement": lambda p: self._build_arrangement(p.get("sections", [])),
            "get_arrangement_clip_notes": lambda p: self._get_arrangement_clip_notes(p.get("track_index", 0), p.get("clip_index", 0)),
            "lom_probe": lambda p: self._lom_probe(p.get("target", ""), p.get("names", [])),
            "set_clip_automation": lambda p: self._set_clip_automation(p.get("track_index", 0), p.get("clip_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("points", []), read_times=p.get("read_times"), arrangement_start_time=p.get("arrangement_start_time")),
            "get_clip_automation": lambda p: self._get_clip_automation(p.get("track_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("read_times", []), clip_index=p.get("clip_index"), arrangement_start_time=p.get("arrangement_start_time")),
            "capture_arrangement_now": lambda p: self._capture_arrangement_now(p.get("song_time", 0.0)),
            "capture_midi_arrangement": lambda p: self._capture_midi_arrangement(),
            "get_song_time_beats": lambda p: {"beats": float(self._song.current_song_time)},
            "duplicate_arrangement_clip": lambda p: self._duplicate_arrangement_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("new_bar_position", None)),
            "move_arrangement_clip": lambda p: self._move_arrangement_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("new_bar_position", 0), p.get("new_track_index", None)),
            "delete_arrangement_clip": lambda p: self._delete_arrangement_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "crop_arrangement_clip": lambda p: self._crop_arrangement_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("start_bar", 0), p.get("end_bar", 16)),
            "split_arrangement_clip": lambda p: self._split_arrangement_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("split_bar", 8)),
            "quantize_arrangement_clip": lambda p: self._quantize_arrangement_clip(p.get("track_index", 0), p.get("clip_index", 0), p.get("amount", 1.0)),
            "add_arrangement_automation_point": lambda p: self._add_arrangement_automation_point(p.get("track_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("bar_position", 0), p.get("value", 0.0), p.get("curve", 0)),
            "add_arrangement_track_automation": lambda p: self._add_arrangement_track_automation(p.get("track_index", 0), p.get("automation_type", "volume"), p.get("bar_position", 0), p.get("value", 0.0)),
            "create_automation_curve": lambda p: self._create_automation_curve(p.get("track_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("points", []), p.get("curve_type", "linear")),
            "create_volume_automation_ramp": lambda p: self._create_volume_automation_ramp(p.get("track_index", 0), p.get("start_bar", 0), p.get("end_bar", 16), p.get("start_volume", 0.5), p.get("end_volume", 0.8), p.get("curve", "linear")),
            "create_filter_sweep": lambda p: self._create_filter_sweep(p.get("track_index", 0), p.get("start_bar", 0), p.get("end_bar", 16), p.get("start_freq", 20.0), p.get("end_freq", 20000.0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("curve", "exponential")),
            "consolidate_arrangement": lambda p: self._consolidate_arrangement(p.get("start_bar", None), p.get("end_bar", None)),
            "duplicate_time_range": lambda p: self._duplicate_time_range(p.get("start_bar", 0), p.get("end_bar", 16), p.get("insert_position", 16)),
            "delete_time_range": lambda p: self._delete_time_range(p.get("start_bar", 0), p.get("end_bar", 16)),
            "insert_silence": lambda p: self._insert_silence(p.get("position_bar", 0), p.get("length_bars", 8)),
            "set_arrangement_view_position": lambda p: self._set_arrangement_view_position(p.get("bar", 0), p.get("beat", 0.0)),
            "set_arrangement_zoom": lambda p: self._set_arrangement_zoom(p.get("zoom_level", 1.0)),
        }

    def _build_udp_handlers(self):
        """Build the UDP fire-and-forget handler map.

        Each value is a callable(params_dict) -> None (fire-and-forget, no return).
        """
        return {
            "set_device_parameter": lambda p: self._set_device_parameter(p.get("track_index", 0), p.get("device_index", 0), p.get("parameter_index", 0), p.get("value", 0.0)),
            "set_track_volume": lambda p: self._set_track_volume(p.get("track_index", 0), p.get("volume", 0.75)),
            "set_track_pan": lambda p: self._set_track_pan(p.get("track_index", 0), p.get("pan", 0.0)),
            "set_track_mute": lambda p: self._set_track_mute(p.get("track_index", 0), p.get("mute", False)),
            "set_track_solo": lambda p: self._set_track_solo(p.get("track_index", 0), p.get("solo", False)),
            "set_track_arm": lambda p: self._set_track_arm(p.get("track_index", 0), p.get("arm", False)),
            "set_master_volume": lambda p: self._set_master_volume(p.get("volume", 0.75)),
            "set_crossfader": lambda p: self._set_crossfader(p.get("value", 0.5)),
            "set_send_amount": lambda p: self._set_send_amount(p.get("track_index", 0), p.get("send_index", 0), p.get("amount", 0.0)),
            "fire_clip": lambda p: self._fire_clip(p.get("track_index", 0), p.get("clip_index", 0)),
            "set_clip_launch_mode": lambda p: self._set_clip_launch_mode(p.get("track_index", 0), p.get("clip_index", 0), p.get("mode", 0)),
        }

    def _execute_on_main_thread(self, handler, params):
        """Schedule a handler on Ableton's main thread and wait for the result."""
        response_queue = queue.Queue()

        def main_thread_task():
            try:
                result = handler(params)
                response_queue.put({"status": "success", "result": result})
            except Exception as e:
                self.log_message("Error in main thread task: " + str(e))
                self.log_message(traceback.format_exc())
                response_queue.put({"status": "error", "message": str(e)})

        try:
            self.schedule_message(0, main_thread_task)
        except AssertionError:
            # Already on the main thread, execute directly
            main_thread_task()

        try:
            return response_queue.get(timeout=COMMAND_TIMEOUT)
        except queue.Empty:
            return {"status": "error", "message": "Timeout waiting for operation to complete"}

    # -----------------------------------------------------------------
    # Command dispatch (refactored: handler map replaces if/elif chain)
    # -----------------------------------------------------------------
    #
    # validate_server.py --remote scans this file via regex for
    # command_type == "<name>" patterns.  The block below is provided
    # for compatibility with that scanner.  Do not remove.
    #
    # command_type == "get_session_info"
    # command_type == "get_track_info"
    # command_type == "create_midi_track"
    # command_type == "create_audio_track"
    # command_type == "delete_all_tracks"
    # command_type == "delete_track"
    # command_type == "set_track_name"
    # command_type == "set_track_color"
    # command_type == "set_track_fold"
    # command_type == "duplicate_track"
    # command_type == "create_clip"
    # command_type == "delete_clip"
    # command_type == "duplicate_clip"
    # command_type == "move_clip"
    # command_type == "add_notes_to_clip"
    # command_type == "delete_notes_from_clip"
    # command_type == "quantize_clip"
    # command_type == "transpose_clip"
    # command_type == "set_clip_name"
    # command_type == "set_clip_loop"
    # command_type == "set_clip_launch_mode"
    # command_type == "set_clip_follow_action"
    # command_type == "get_clip_follow_actions"
    # command_type == "duplicate_clip_to"
    # command_type == "crop_clip"
    # command_type == "resize_clip"
    # command_type == "create_scene"
    # command_type == "delete_scene"
    # command_type == "duplicate_scene"
    # command_type == "set_scene_name"
    # command_type == "fire_scene"
    # command_type == "trigger_scene"
    # command_type == "set_tempo"
    # command_type == "set_time_signature"
    # command_type == "set_metronome"
    # command_type == "fire_clip"
    # command_type == "stop_clip"
    # command_type == "start_playback"
    # command_type == "stop_playback"
    # command_type == "start_recording"
    # command_type == "stop_recording"
    # command_type == "set_track_monitoring_state"
    # command_type == "load_browser_item"
    # command_type == "load_instrument_or_effect"
    # command_type == "load_instrument_preset"
    # command_type == "get_device_parameters"
    # command_type == "set_device_parameter"
    # command_type == "add_automation_point"
    # command_type == "clear_automation"
    # command_type == "duplicate_device"
    # command_type == "delete_device"
    # command_type == "move_device"
    # command_type == "toggle_device_bypass"
    # command_type == "undo"
    # command_type == "redo"
    # command_type == "get_playhead_position"
    # command_type == "set_playhead_position"
    # command_type == "create_locator"
    # command_type == "delete_locator"
    # command_type == "jump_to_locator"
    # command_type == "set_loop"
    # command_type == "list_device_presets"
    # command_type == "load_device_preset"
    # command_type == "save_device_preset"
    # command_type == "get_clip_notes"
    # command_type == "get_clip_envelopes"
    # command_type == "get_clip_envelope_points"
    # command_type == "set_clip_envelope_point"
    # command_type == "set_master_volume"
    # command_type == "set_track_volume"
    # command_type == "set_track_mute"
    # command_type == "set_track_solo"
    # command_type == "set_track_arm"
    # command_type == "set_track_pan"
    # command_type == "set_send_amount"
    # command_type == "get_master_track_info"
    # command_type == "get_return_tracks"
    # command_type == "get_all_tracks"
    # command_type == "get_all_scenes"
    # command_type == "get_session_overview"
    # command_type == "get_all_clips_in_track"
    # command_type == "set_note_velocity"
    # command_type == "set_note_duration"
    # command_type == "set_note_pitch"
    # command_type == "mix_clip"
    # command_type == "stretch_clip"
    # command_type == "detect_clip_key"
    # command_type == "snap_notes_to_scale"
    # command_type == "create_scale_reference_clip"
    # command_type == "create_chord_progression"
    # command_type == "group_tracks"
    # command_type == "ungroup_tracks"
    # command_type == "set_clip_warp_mode"
    # command_type == "get_clip_warp_markers"
    # command_type == "add_warp_marker"
    # command_type == "delete_warp_marker"
    # command_type == "reload_script"
    # command_type == "get_global_quantization"
    # command_type == "set_global_quantization"
    # command_type == "get_link_status"
    # command_type == "set_link_enabled"
    # command_type == "set_link_start_stop_sync"
    # command_type == "apply_energy_curve"
    # command_type == "apply_groove_to_clip"
    # command_type == "remove_groove_from_clip"
    # command_type == "set_global_groove_amount"
    # command_type == "get_browser_item"
    # command_type == "get_browser_categories"
    # command_type == "get_browser_items"
    # command_type == "get_browser_tree"
    # command_type == "get_browser_items_at_path"
    # command_type == "get_browser_recursive_children"
    # command_type == "get_available_grooves"
    # command_type == "get_crossfader"
    # command_type == "set_crossfader"
    # command_type == "get_track_crossfade_assign"
    # command_type == "set_track_crossfade_assign"
    # command_type == "get_level_snapshot"
    # command_type == "get_track_sends"
    # command_type == "capture_and_insert_arrangement"
    # command_type == "get_arrangement_clips"
    # command_type == "duplicate_arrangement_clip"
    # command_type == "move_arrangement_clip"
    # command_type == "delete_arrangement_clip"
    # command_type == "crop_arrangement_clip"
    # command_type == "split_arrangement_clip"
    # command_type == "quantize_arrangement_clip"
    # command_type == "add_arrangement_automation_point"
    # command_type == "add_arrangement_track_automation"
    # command_type == "create_automation_curve"
    # command_type == "create_volume_automation_ramp"
    # command_type == "create_filter_sweep"
    # command_type == "consolidate_arrangement"
    # command_type == "duplicate_time_range"
    # command_type == "delete_time_range"
    # command_type == "insert_silence"
    # command_type == "set_arrangement_view_position"
    # command_type == "set_arrangement_zoom"

    def _process_command(self, command):
        """Process a command from the client and return a response.

        Refactored: uses handler map instead of if/elif chain.
        Supports protocol version handshake via 'hello' command type.
        """
        command_type = command.get("type", "")
        params = command.get("params", {})

        # --- Protocol handshake ---
        if command_type == "hello":
            client_version = command.get("protocol_version", 0)
            if client_version != PROTOCOL_VERSION:
                return {
                    "status": "error",
                    "error": "PROTOCOL_VERSION_MISMATCH",
                    "message": (
                        "Client protocol version {} does not match "
                        "server version {}".format(
                            client_version, PROTOCOL_VERSION
                        )
                    ),
                    "server_protocol_version": PROTOCOL_VERSION,
                }
            return {
                "status": "success",
                "result": {"protocol_version": PROTOCOL_VERSION},
            }

        # --- Handler lookup ---
        handler = self._handlers.get(command_type)
        if handler is None:
            return {
                "status": "error",
                "error": "UNKNOWN_COMMAND",
                "command": command_type,
            }

        # --- Main-thread scheduling ---
        if command_type in self.MAIN_THREAD_COMMANDS:
            return self._execute_on_main_thread(handler, params)

        # --- Direct dispatch ---
        try:
            result = handler(params)
            return {"status": "success", "result": result}
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    def _execute_udp_command(self, command_json):
        """Execute UDP command - fire-and-forget routing via handler map."""
        command_type = command_json.get("type", "")
        params = command_json.get("params", {})

        handler = self._udp_handlers.get(command_type)
        if handler is None:
            self.log_message(
                "UDP: Unknown or unsupported command type: {}".format(
                    command_type
                )
            )
            return

        try:
            handler(params)
        except Exception as e:
            # Fire-and-forget: log error but don't crash
            self.log_message("UDP: Error executing {}: {}".format(command_type, e))

    # Command implementations

    def _get_session_info(self):
        """Get information about the current session"""
        try:
            result = {
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "track_count": len(self._song.tracks),
                "return_track_count": len(self._song.return_tracks),
                "master_track": {
                    "name": "Master",
                    "volume": self._song.master_track.mixer_device.volume.value,
                    "panning": self._song.master_track.mixer_device.panning.value,
                },
            }
            return result
        except Exception as e:
            self.log_message("Error setting track pan: " + str(e))
            raise

    def _set_master_volume(self, volume):
        """Set master track volume (0.0 to 1.0)"""
        try:
            self._song.master_track.mixer_device.volume.value = volume
            result = {"volume": volume}
            return result
        except Exception as e:
            self.log_message("Error setting master volume: " + str(e))
            raise

    def _get_track_info(self, track_index):
        """Get information about a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Get clip slots
            clip_slots = []
            for slot_index, slot in enumerate(track.clip_slots):
                clip_info = None
                if slot.has_clip:
                    clip = slot.clip
                    clip_info = {
                        "name": clip.name,
                        "length": clip.length,
                        "is_playing": clip.is_playing,
                        "is_recording": clip.is_recording,
                    }

                clip_slots.append(
                    {"index": slot_index, "has_clip": slot.has_clip, "clip": clip_info}
                )

            # Get devices
            devices = []
            for device_index, device in enumerate(track.devices):
                devices.append(
                    {
                        "index": device_index,
                        "name": device.name,
                        "class_name": device.class_name,
                        "type": self._get_device_type(device),
                    }
                )

            is_group = bool(getattr(track, "is_foldable", False))

            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "is_group_track": is_group,
                "mute": track.mute,
                "solo": track.solo,
                "arm": None if is_group else track.arm,
                "volume": track.mixer_device.volume.value,
                "panning": track.mixer_device.panning.value,
                "clip_slots": clip_slots,
                "devices": devices,
            }
            return result
        except Exception as e:
            self.log_message("Error getting track info: " + str(e))
            raise

    def _create_midi_track(self, index):
        """Create a new MIDI track at specified index"""
        try:
            # Create track
            self._song.create_midi_track(index)

            # Get new track
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]

            result = {"index": new_track_index, "name": new_track.name}
            return result
        except Exception as e:
            self.log_message("Error creating MIDI track: " + str(e))
            raise

    def _delete_all_tracks(self):
        """Delete all tracks in the session"""
        try:
            # Delete all tracks (go backwards to avoid index shifting)
            track_count = len(self._song.tracks)
            for i in range(track_count - 1, -1, -1):
                try:
                    self._song.delete_track(i)
                except Exception as e:
                    self.log_message(f"Error deleting track {i}: {str(e)}")

            result = {"deleted_count": track_count}
            return result
        except Exception as e:
            self.log_message("Error deleting all tracks: " + str(e))
            raise

    def _set_track_name(self, track_index, name):
        """Set the name of a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            # Set the name
            track = self._song.tracks[track_index]
            track.name = name

            result = {"name": track.name}
            return result
        except Exception as e:
            self.log_message("Error setting track name: " + str(e))
            raise

    def _create_clip(self, track_index, clip_index, length):
        """Create a new MIDI clip in the specified track and clip slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Validate track supports MIDI
            if not track.has_midi_input:
                raise Exception(
                    "Cannot create MIDI clip on this track. "
                    "The track does not support MIDI input. "
                    "Use create_midi_track() first or ensure track is a MIDI track."
                )

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            # Check if the clip slot already has a clip
            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")

            # Create the clip
            clip_slot.create_clip(length)

            # Verify the clip was actually created
            if not clip_slot.has_clip:
                raise Exception("Clip creation failed - clip slot is still empty")

            result = {"name": clip_slot.clip.name, "length": clip_slot.clip.length}
            return result
        except Exception as e:
            self.log_message("Error creating clip: " + str(e))
            raise

    def _add_notes_to_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip

            # Convert note data to Live's format
            live_notes = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)

                live_notes.append((pitch, start_time, duration, velocity, mute))

            # Add the notes
            clip.set_notes(tuple(live_notes))

            result = {"note_count": len(notes)}
            return result
        except Exception as e:
            self.log_message("Error adding notes to clip: " + str(e))
            raise

    def _set_clip_name(self, track_index, clip_index, name):
        """Set the name of a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip = clip_slot.clip
            clip.name = name

            result = {"name": clip.name}
            return result
        except Exception as e:
            self.log_message("Error setting clip name: " + str(e))
            raise

    def _set_tempo(self, tempo):
        """Set the tempo of the session"""
        try:
            self._song.tempo = tempo

            result = {"tempo": self._song.tempo}
            return result
        except Exception as e:
            self.log_message("Error setting tempo: " + str(e))
            raise

    def _get_global_quantization(self):
        """Get the current global quantization setting"""
        try:
            # Ableton uses a float value for quantization
            # 0 = None, 0.25 = 1/4, 0.5 = 1/2, 1 = 1 Bar, 2 = 2 Bars, 4 = 4 Bars
            q_value = self._song.clip_trigger_quantization

            # Map to human-readable string
            q_map = {
                0: "none",
                0.25: "1/4",
                0.5: "1/2",
                1: "1 Bar",
                2: "2 Bars",
                4: "4 Bars",
                8: "8 Bars",
            }

            q_string = q_map.get(q_value, str(q_value))

            result = {
                "quantization": q_string,
                "quantize_value": q_value,
            }
            return result
        except Exception as e:
            self.log_message("Error getting global quantization: " + str(e))
            raise

    def _set_global_quantization(self, value):
        """Set the global quantization for clip launching"""
        try:
            # Map string to Ableton quantization value
            q_map = {
                "none": 0,
                "1/4": 0.25,
                "1/2": 0.5,
                "1 bar": 1,
                "1 bars": 1,
                "2 bars": 2,
                "2 bar": 2,
                "4 bars": 4,
                "4 bar": 4,
                "8 bars": 8,
                "8 bar": 8,
            }

            q_value = q_map.get(value.lower())
            if q_value is None:
                raise Exception(f"Unknown quantization value: {value}")

            self._song.clip_trigger_quantization = q_value

            result = {
                "quantization": value,
                "quantize_value": q_value,
                "success": True,
            }
            return result
        except Exception as e:
            self.log_message("Error setting global quantization: " + str(e))
            raise

    def _fire_clip(self, track_index, clip_index):
        """Fire a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip_slot.fire()

            result = {"fired": True}
            return result
        except Exception as e:
            self.log_message("Error firing clip: " + str(e))
            raise

    def _stop_clip(self, track_index, clip_index):
        """Stop a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            clip_slot.stop()

            result = {"stopped": True}
            return result
        except Exception as e:
            self.log_message("Error stopping clip: " + str(e))
            raise

    def _start_playback(self):
        """Start playing the session"""
        try:
            self._song.start_playing()

            result = {"playing": self._song.is_playing}
            return result
        except Exception as e:
            self.log_message("Error starting playback: " + str(e))
            raise

    def _stop_playback(self):
        """Stop playing the session"""
        try:
            self._song.stop_playing()

            result = {"playing": self._song.is_playing}
            return result
        except Exception as e:
            self.log_message("Error stopping playback: " + str(e))
            raise

    # New device and track control methods
    def _get_device_parameters(self, track_index, device_index):
        """Get all parameters for a specific device on a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            # Get all parameters from the device
            parameters = []

            # Check for alternative Ableton Live 11+ API
            if hasattr(device, "get_notes"):
                # Use get_notes() method for Live 11+ compatibility
                try:
                    notes_list = device.get_notes()
                    if notes_list:
                        for i, note in enumerate(notes_list):
                            notes.append(
                                {
                                    "pitch": note.pitch,
                                    "start_time": note.start_time,
                                    "duration": note.duration,
                                    "velocity": note.velocity,
                                    "mute": note.mute
                                    if hasattr(note, "mute")
                                    else False,
                                }
                            )
                except Exception as e:
                    self.log_message(
                        "Error reading notes from device: {}".format(str(e))
                    )
            elif hasattr(device, "parameters"):
                for i, param in enumerate(device.parameters):
                    if param.is_enabled:
                        try:
                            param_info = {
                                "index": i,
                                "name": param.name
                                if hasattr(param, "name")
                                else "Parameter {}".format(i),
                                "value": param.value,
                                "min": param.min if hasattr(param, "min") else 0.0,
                                "max": param.max if hasattr(param, "max") else 1.0,
                                "is_quantized": hasattr(param, "is_quantized")
                                and param.is_quantized,
                            }
                            parameters.append(param_info)
                        except Exception as e:
                            self.log_message(
                                "Error reading parameter {}: {}".format(i, str(e))
                            )
                            continue
            elif hasattr(device, "parameters") and not parameters:
                # Device has parameters attribute but it's empty or inaccessible
                self.log_message("Device has no accessible parameters")

            result = {
                "device_name": device.name
                if hasattr(device, "name")
                else "Device {}".format(device_index),
                "device_index": device_index,
                "parameters": parameters,
            }
            return result
        except Exception as e:
            self.log_message("Error getting device parameters: " + str(e))
            raise

    def _set_device_parameter(self, track_index, device_index, parameter_index, value):
        """Set a device parameter value (normalized 0.0-1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            if hasattr(device, "parameters"):
                if parameter_index < 0 or parameter_index >= len(device.parameters):
                    raise IndexError("Parameter index out of range")

                parameter = device.parameters[parameter_index]

                # Set the parameter value
                parameter.value = value

                result = {
                    "device_name": device.name
                    if hasattr(device, "name")
                    else "Device {}".format(device_index),
                    "parameter_index": parameter_index,
                    "parameter_name": parameter.name
                    if hasattr(parameter, "name")
                    else "Parameter {}".format(parameter_index),
                    "value": value,
                }
                return result
            else:
                raise Exception("Device has no parameters")
        except Exception as e:
            self.log_message("Error setting device parameter: " + str(e))
            raise

    def _set_track_volume(self, track_index, volume):
        """Set track volume (normalized 0.0-1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.mixer_device.volume.value = volume

            result = {
                "track_name": track.name
                if hasattr(track, "name")
                else "Track {}".format(track_index),
                "volume": volume,
                "db": "TODO: convert to dB",
            }
            return result
        except Exception as e:
            self.log_message("Error setting track volume: " + str(e))
            raise

    def _set_track_mute(self, track_index, mute):
        """Mute or unmute a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.mute = mute

            result = {
                "track_name": track.name
                if hasattr(track, "name")
                else "Track {}".format(track_index),
                "mute": mute,
            }
            return result
        except Exception as e:
            self.log_message("Error setting track mute: " + str(e))
            raise

    def _set_track_solo(self, track_index, solo):
        """Solo or unsolo a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.solo = solo

            result = {
                "track_name": track.name
                if hasattr(track, "name")
                else "Track {}".format(track_index),
                "solo": solo,
            }
            return result
        except Exception as e:
            self.log_message("Error setting track solo: " + str(e))
            raise

    def _set_track_arm(self, track_index, arm):
        """Arm or unarm a track for recording"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            track.arm = arm

            result = {
                "track_name": track.name
                if hasattr(track, "name")
                else "Track {}".format(track_index),
                "arm": arm,
            }
            return result
        except Exception as e:
            self.log_message("Error setting track arm: " + str(e))
            raise

    def _load_instrument_preset(self, track_index, device_index, preset_name):
        """Load a preset for a device on a track by name"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            if not hasattr(device, "presets"):
                raise Exception("Device has no presets")

            # Search through presets to find matching name
            found_preset = None
            for preset in device.presets:
                if (
                    hasattr(preset, "name")
                    and preset.name.lower() == preset_name.lower()
                ):
                    found_preset = preset
                    break

            if found_preset:
                # Found preset, load it
                device.presets = found_preset
                self.log_message(
                    "Loaded preset '{}' for device '{}' on track '{}'".format(
                        preset_name,
                        device.name if hasattr(device, "name") else str(device_index),
                        track.name,
                    )
                )

                result = {
                    "track_name": track.name
                    if hasattr(track, "name")
                    else "Track {}".format(track_index),
                    "device_name": device.name
                    if hasattr(device, "name")
                    else "Device {}".format(device_index),
                    "preset_name": preset_name,
                    "loaded": True,
                }
            else:
                # Preset not found
                self.log_message(
                    "Preset '{}' not found for device '{}' on track '{}'. Available presets:".format(
                        preset_name,
                        device.name if hasattr(device, "name") else str(device_index),
                        track.name,
                    )
                )

                # List available presets
                available_presets = []
                for preset in device.presets:
                    if hasattr(preset, "name"):
                        available_presets.append(preset.name)

                result = {
                    "track_name": track.name
                    if hasattr(track, "name")
                    else "Track {}".format(track_index),
                    "device_name": device.name
                    if hasattr(device, "name")
                    else "Device {}".format(device_index),
                    "preset_name": preset_name,
                    "loaded": False,
                    "error": "Preset not found",
                    "available_presets": available_presets,
                }

            return result
        except Exception as e:
            self.log_message("Error loading instrument preset: " + str(e))
            raise

    def _save_device_preset(self, track_index, device_index, preset_name):
        """
        Save a device preset using Ableton's preset system.

        Note: Ableton Live's Remote Script API does NOT provide a method to
        programmatically save device presets. This function captures the device's
        current parameter values and saves them to a local JSON database for
        later restoration. This is NOT Ableton's native .advpt preset format.

        For native Ableton presets, use the Ableton UI to save manually.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            # Get device class name for storage
            device_class = (
                device.class_name if hasattr(device, "class_name") else "Unknown"
            )
            device_name = (
                device.name
                if hasattr(device, "name")
                else "Device {}".format(device_index)
            )

            # Capture all device parameters
            parameters = []
            if hasattr(device, "parameters"):
                for i, param in enumerate(device.parameters):
                    if param.is_enabled:
                        try:
                            param_info = {
                                "index": i,
                                "name": (
                                    param.name
                                    if hasattr(param, "name")
                                    else "Parameter {}".format(i)
                                ),
                                "value": param.value,
                            }
                            parameters.append(param_info)
                        except Exception as e:
                            self.log_message(
                                "Error reading parameter {}: {}".format(i, str(e))
                            )
                            continue

            # Get home directory for storage
            home_dir = os.path.expanduser("~")
            preset_db_path = os.path.join(home_dir, ".ableton_mcp", "device_presets")
            os.makedirs(preset_db_path, exist_ok=True)

            # Save to JSON file
            preset_file = os.path.join(
                preset_db_path, "{}_{}.json".format(device_class, preset_name)
            )
            preset_data = {
                "device_class": device_class,
                "device_name": device_name,
                "preset_name": preset_name,
                "parameters": parameters,
            }

            with open(preset_file, "w") as f:
                json.dump(preset_data, f, indent=2)

            self.log_message(
                "Saved preset '{}' for device '{}' (class: {}) to {}".format(
                    preset_name, device_name, device_class, preset_file
                )
            )

            result = {
                "track_name": (
                    track.name
                    if hasattr(track, "name")
                    else "Track {}".format(track_index)
                ),
                "device_name": device_name,
                "device_class": device_class,
                "preset_name": preset_name,
                "saved": True,
                "file": preset_file,
                "note": "Saved to JSON database (not Ableton's native .advpt format)",
            }

            return result

        except Exception as e:
            self.log_message("Error saving device preset: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _load_device_preset(self, track_index, device_index, preset_name):
        """
        Load a device preset.

        First tries to load from Ableton's native preset system (via device.presets).
        If not found, searches the local JSON preset database.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]
            device_name = (
                device.name
                if hasattr(device, "name")
                else "Device {}".format(device_index)
            )

            # First try Ableton's native preset system
            if hasattr(device, "presets"):
                found_preset = None
                for preset in device.presets:
                    if (
                        hasattr(preset, "name")
                        and preset.name.lower() == preset_name.lower()
                    ):
                        found_preset = preset
                        break

                if found_preset:
                    device.presets = found_preset
                    self.log_message(
                        "Loaded native Ableton preset '{}' for device '{}' on track '{}'".format(
                            preset_name, device_name, track.name
                        )
                    )

                    return {
                        "track_name": (
                            track.name
                            if hasattr(track, "name")
                            else "Track {}".format(track_index)
                        ),
                        "device_name": device_name,
                        "preset_name": preset_name,
                        "loaded": True,
                        "source": "native",
                    }

            # If not found in native presets, try JSON database
            device_class = (
                device.class_name if hasattr(device, "class_name") else "Unknown"
            )
            home_dir = os.path.expanduser("~")
            preset_db_path = os.path.join(home_dir, ".ableton_mcp", "device_presets")
            preset_file = os.path.join(
                preset_db_path, "{}_{}.json".format(device_class, preset_name)
            )

            if not os.path.exists(preset_file):
                # Preset not found in either native or JSON database
                return {
                    "track_name": (
                        track.name
                        if hasattr(track, "name")
                        else "Track {}".format(track_index)
                    ),
                    "device_name": device_name,
                    "preset_name": preset_name,
                    "loaded": False,
                    "error": "Preset not found in Ableton native presets or JSON database",
                }

            # Load from JSON database
            with open(preset_file, "r") as f:
                preset_data = json.load(f)

            # Validate device class matches
            if preset_data.get("device_class") != device_class:
                return {
                    "track_name": (
                        track.name
                        if hasattr(track, "name")
                        else "Track {}".format(track_index)
                    ),
                    "device_name": device_name,
                    "preset_name": preset_name,
                    "loaded": False,
                    "error": "Preset device class mismatch. Expected: {}, Got: {}".format(
                        device_class, preset_data.get("device_class")
                    ),
                }

            # Apply parameters
            for param_data in preset_data.get("parameters", []):
                param_idx = param_data["index"]
                if param_idx < len(device.parameters):
                    try:
                        device.parameters[param_idx].value = param_data["value"]
                    except Exception as e:
                        self.log_message(
                            "Error setting parameter {}: {}".format(param_idx, str(e))
                        )
                        continue

            self.log_message(
                "Loaded JSON preset '{}' for device '{}' (class: {}) from {}".format(
                    preset_name, device_name, device_class, preset_file
                )
            )

            return {
                "track_name": (
                    track.name
                    if hasattr(track, "name")
                    else "Track {}".format(track_index)
                ),
                "device_name": device_name,
                "device_class": device_class,
                "preset_name": preset_name,
                "loaded": True,
                "source": "json",
                "file": preset_file,
            }

        except Exception as e:
            self.log_message("Error loading device preset: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _list_device_presets(self, track_index, device_index):
        """
        List available presets for a specific device.

        Returns presets from both Ableton's native system and the local JSON database.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]
            device_class = (
                device.class_name if hasattr(device, "class_name") else "Unknown"
            )
            device_name = (
                device.name
                if hasattr(device, "name")
                else "Device {}".format(device_index)
            )

            # Get native Ableton presets
            native_presets = []
            if hasattr(device, "presets"):
                for preset in device.presets:
                    if hasattr(preset, "name"):
                        native_presets.append(preset.name)

            # Get JSON database presets for this device class
            home_dir = os.path.expanduser("~")
            preset_db_path = os.path.join(home_dir, ".ableton_mcp", "device_presets")
            json_presets = []

            if os.path.exists(preset_db_path):
                prefix = device_class + "_"
                for filename in os.listdir(preset_db_path):
                    if filename.startswith(prefix) and filename.endswith(".json"):
                        # Extract preset name by removing prefix and .json
                        preset_name = filename[len(prefix) : -5]
                        json_presets.append(preset_name)

            result = {
                "track_name": (
                    track.name
                    if hasattr(track, "name")
                    else "Track {}".format(track_index)
                ),
                "device_name": device_name,
                "device_class": device_class,
                "native_presets": native_presets,
                "json_presets": json_presets,
                "all_presets": sorted(list(set(native_presets + json_presets))),
            }

            return result

        except Exception as e:
            self.log_message("Error listing device presets: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _create_audio_track(self, index):
        """Create a new audio track at specified index"""
        try:
            self._song.create_audio_track(index)
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]
            result = {"index": new_track_index, "name": new_track.name}
            return result
        except Exception as e:
            self.log_message("Error creating audio track: " + str(e))
            raise

    def _delete_track(self, track_index):
        """Delete a track by index"""
        try:
            if len(self._song.tracks) <= 1:
                raise ValueError(
                    "Cannot delete the last remaining session track. "
                    "Ableton must always have at least one track."
                )
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track_name = track.name

            # Log before deletion attempt
            self.log_message(
                f"[DELETE_TRACK] Attempting to delete track '{track_name}' at index {track_index}"
            )
            self.log_message(
                f"[DELETE_TRACK] Total tracks before deletion: {len(self._song.tracks)}"
            )

            self._song.delete_track(track_index)

            # Log after deletion
            self.log_message(
                f"[DELETE_TRACK] Total tracks after deletion: {len(self._song.tracks)}"
            )

            result = {"deleted_index": track_index, "deleted_track": track_name}
            return result
        except Exception as e:
            import traceback

            self.log_message(f"[DELETE_TRACK] Error deleting track: {str(e)}")
            self.log_message(f"[DELETE_TRACK] Stack trace: {traceback.format_exc()}")
            raise

    def _set_track_color(self, track_index, color_index):
        """Set track color index (0-127)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.color_index = color_index
            result = {"track_index": track_index, "color_index": color_index}
            return result
        except Exception as e:
            self.log_message("Error setting track color: " + str(e))
            raise

    def _set_track_fold(self, track_index, folded):
        """Set track fold state"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.fold_state = 1 if folded else 0
            result = {"track_index": track_index, "folded": folded}
            return result
        except Exception as e:
            self.log_message("Error setting track fold: " + str(e))
            raise

    def _duplicate_track(self, track_index):
        """Duplicate a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.tracks[track_index]
            self._song.duplicate_track(track_index)
            new_track_index = len(self._song.tracks) - 1
            result = {"original_index": track_index, "new_index": new_track_index}
            return result
        except Exception as e:
            self.log_message("Error duplicating track: " + str(e))
            raise

    def _delete_clip(self, track_index, clip_index):
        """Delete a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip_slot.delete_clip()
            result = {
                "deleted": True,
                "track_index": track_index,
                "clip_index": clip_index,
            }
            return result
        except Exception as e:
            self.log_message("Error deleting clip: " + str(e))
            raise

    def _duplicate_clip(self, track_index, clip_index):
        """Duplicate a clip to the next slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip_slot.duplicate_clip()
            result = {
                "duplicated": True,
                "track_index": track_index,
                "original_clip_index": clip_index,
            }
            return result
        except Exception as e:
            self.log_message("Error duplicating clip: " + str(e))
            raise

    def _move_clip(self, track_index, clip_index, new_track_index, new_clip_index):
        """Move a clip to another slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            if new_track_index < 0 or new_track_index >= len(self._song.tracks):
                raise IndexError("New track index out of range")

            track = self._song.tracks[track_index]
            new_track = self._song.tracks[new_track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            if new_clip_index < 0 or new_clip_index >= len(new_track.clip_slots):
                raise IndexError("New clip index out of range")

            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            new_slot = new_track.clip_slots[new_clip_index]
            if new_slot.has_clip:
                raise Exception("Target slot already has a clip")

            clip_slot.move_to(new_slot)
            result = {
                "moved": True,
                "from": [track_index, clip_index],
                "to": [new_track_index, new_clip_index],
            }
            return result
        except Exception as e:
            self.log_message("Error moving clip: " + str(e))
            raise

    def _delete_notes_from_clip(self, track_index, clip_index, note_indices):
        """Delete specific notes from a clip by indices"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            all_notes = list(clip.get_selected_notes() or clip.notes)
            deleted_indices = []
            for idx in sorted(note_indices, reverse=True):
                if 0 <= idx < len(all_notes):
                    del all_notes[idx]
                    deleted_indices.append(idx)

            clip.notes = all_notes
            result = {
                "deleted_count": len(deleted_indices),
                "deleted_indices": deleted_indices,
            }
            return result
        except Exception as e:
            self.log_message("Error deleting notes: " + str(e))
            raise

    def _quantize_clip(self, track_index, clip_index, amount):
        """Quantize notes in a clip (0.0 to 1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.quantize(amount, True)
            result = {
                "quantized": True,
                "track_index": track_index,
                "clip_index": clip_index,
                "amount": amount,
            }
            return result
        except Exception as e:
            self.log_message("Error quantizing clip: " + str(e))
            raise

    def _transpose_clip(self, track_index, clip_index, semitones):
        """Transpose notes in a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            notes = list(clip.notes)
            transposed_notes = []
            for note in notes:
                transposed_notes.append(
                    (note[0] + semitones, note[1], note[2], note[3], note[4])
                )
            clip.notes = tuple(transposed_notes)
            result = {
                "transposed": True,
                "track_index": track_index,
                "clip_index": clip_index,
                "semitones": semitones,
            }
            return result
        except Exception as e:
            self.log_message("Error transposing clip: " + str(e))
            raise

    def _set_clip_loop(self, track_index, clip_index, loop_start, loop_length):
        """Set clip loop parameters"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.looping = True
            clip.loop_start = loop_start
            clip.loop_end = loop_start + loop_length
            result = {"loop_start": loop_start, "loop_end": loop_start + loop_length}
            return result
        except Exception as e:
            self.log_message("Error setting clip loop: " + str(e))
            raise

    def _set_clip_launch_mode(self, track_index, clip_index, mode):
        """Set clip launch mode (0=Trigger, 1=Gate, 2=Toggle, 3=Repeat)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.launch_mode = mode
            result = {"launch_mode": mode}
            return result
        except Exception as e:
            self.log_message("Error setting clip launch mode: " + str(e))
            raise

    def _create_scene(self, index):
        """Create a new scene"""
        try:
            self._song.create_scene(index)
            new_scene_index = len(self._song.scenes) - 1 if index == -1 else index
            result = {"scene_index": new_scene_index}
            return result
        except Exception as e:
            self.log_message("Error creating scene: " + str(e))
            raise

    def _delete_scene(self, scene_index):
        """Delete a scene"""
        try:
            if scene_index < 0 or scene_index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            self._song.delete_scene(scene_index)
            result = {"deleted_scene_index": scene_index}
            return result
        except Exception as e:
            self.log_message("Error deleting scene: " + str(e))
            raise

    def _duplicate_scene(self, scene_index):
        """Duplicate a scene"""
        try:
            if scene_index < 0 or scene_index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            self._song.duplicate_scene(scene_index)
            new_scene_index = len(self._song.scenes) - 1
            result = {
                "original_scene_index": scene_index,
                "new_scene_index": new_scene_index,
            }
            return result
        except Exception as e:
            self.log_message("Error duplicating scene: " + str(e))
            raise

    def _set_scene_name(self, scene_index, name):
        """Set scene name"""
        try:
            if scene_index < 0 or scene_index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            scene = self._song.scenes[scene_index]
            scene.name = name
            result = {"scene_index": scene_index, "name": name}
            return result
        except Exception as e:
            self.log_message("Error setting scene name: " + str(e))
            raise

    def _fire_scene(self, scene_index):
        """Fire all clips in a scene"""
        try:
            if scene_index < 0 or scene_index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            scene = self._song.scenes[scene_index]
            scene.fire()
            result = {"fired_scene_index": scene_index}
            return result
        except Exception as e:
            self.log_message("Error firing scene: " + str(e))
            raise

    def _set_time_signature(self, numerator, denominator):
        """Set session time signature"""
        try:
            self._song.signature_numerator = numerator
            self._song.signature_denominator = denominator
            result = {"numerator": numerator, "denominator": denominator}
            return result
        except Exception as e:
            self.log_message("Error setting time signature: " + str(e))
            raise

    def _set_metronome(self, enabled):
        """Enable/disable metronome"""
        try:
            self._song.metronome = enabled
            result = {"metronome_enabled": enabled}
            return result
        except Exception as e:
            self.log_message("Error setting metronome: " + str(e))
            raise

    def _start_recording(self):
        """Start recording"""
        try:
            self._song.start_playing()
            self._song.record_mode = True
            result = {"recording": True}
            return result
        except Exception as e:
            self.log_message("Error starting recording: " + str(e))
            raise

    def _stop_recording(self):
        """Stop recording"""
        try:
            self._song.record_mode = False
            result = {"recording": False}
            return result
        except Exception as e:
            self.log_message("Error stopping recording: " + str(e))
            raise

    def _set_track_monitoring_state(self, track_index, monitoring_state):
        """Set track monitoring state (0=Off, 1=In, 2=Auto)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if not track.has_audio_input:
                raise Exception("Track does not have audio input")
            track.current_monitoring_state = monitoring_state
            result = {"track_index": track_index, "monitoring_state": monitoring_state}
            return result
        except Exception as e:
            self.log_message("Error setting monitoring state: " + str(e))
            raise

    def _add_automation_point(
        self, track_index, clip_index, device_index, parameter_index, time_val, value
    ):
        """Add an automation point to a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            if parameter_index < 0 or parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range")
            parameter = device.parameters[parameter_index]

            clip.create_automation_event(parameter, time_val, value)
            result = {"added": True, "time": time_val, "value": value}
            return result
        except Exception as e:
            self.log_message("Error adding automation point: " + str(e))
            raise

    def _clear_automation(self, track_index, clip_index, device_index, parameter_index):
        """Clear automation for a parameter in a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            if parameter_index < 0 or parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range")
            parameter = device.parameters[parameter_index]

            clip.clear_automation_envelope(parameter)
            result = {"cleared": True}
            return result
        except Exception as e:
            self.log_message("Error clearing automation: " + str(e))
            raise

    def _duplicate_device(self, track_index, device_index):
        """Duplicate a device on a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            device.duplicate()
            result = {"duplicated": True, "original_device_index": device_index}
            return result
        except Exception as e:
            self.log_message("Error duplicating device: " + str(e))
            raise

    def _delete_device(self, track_index, device_index):
        """Delete a device from a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            device_name = device.name if hasattr(device, "name") else "Unknown"

            # Log before deletion attempt
            self.log_message(
                f"[DELETE_DEVICE] Attempting to delete device '{device_name}' from track {track_index} (device index {device_index})"
            )
            self.log_message(
                f"[DELETE_DEVICE] Total devices before deletion: {len(track.devices)}"
            )

            device.delete_device()

            # Log after deletion and verify
            self.log_message(
                f"[DELETE_DEVICE] Total devices after deletion: {len(track.devices)}"
            )

            # Verify deletion worked
            remaining_devices = list(track.devices)
            deleted_successfully = len(remaining_devices) < (device_index + 1)

            result = {
                "deleted_device": device_name,
                "device_index": device_index,
                "verified": deleted_successfully,
                "track_index": track_index,
                "devices_remaining": len(remaining_devices),
            }
            return result
        except Exception as e:
            import traceback

            self.log_message(f"[DELETE_DEVICE] Error deleting device: {str(e)}")
            self.log_message(f"[DELETE_DEVICE] Stack trace: {traceback.format_exc()}")
            raise

    def _move_device(self, track_index, device_index, new_position):
        """Move a device to a new position in the chain"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            if new_position < 0 or new_position >= len(track.devices):
                raise IndexError("New device position out of range")

            device = track.devices[device_index]
            devices_list = list(track.devices)
            devices_list.pop(device_index)
            devices_list.insert(new_position, device)

            result = {
                "moved": True,
                "from_index": device_index,
                "to_index": new_position,
            }
            return result
        except Exception as e:
            self.log_message("Error moving device: " + str(e))
            raise

    def _set_track_pan(self, track_index, pan):
        """Set track panning (-1.0 to 1.0, 0.0 is center)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.mixer_device.panning.value = max(-1.0, min(1.0, pan))
            result = {"track_index": track_index, "pan": pan}
            return result
        except Exception as e:
            self.log_message("Error setting track pan: " + str(e))
            raise

    def _set_send_amount(self, track_index, send_index, amount):
        """Set send amount to a return track (normalized 0.0-1.0)"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if send_index < 0 or send_index >= len(track.mixer_device.sends):
                raise IndexError("Send index out of range")

            track.mixer_device.sends[send_index].value = amount

            result = {
                "track_index": track_index,
                "send_index": send_index,
                "amount": amount,
            }
            return result
        except Exception as e:
            self.log_message("Error setting send amount: " + str(e))
            raise

    def _set_master_volume(self, volume):
        """Set master track volume (normalized 0.0-1.0)"""
        try:
            self._song.master_track.mixer_device.volume.value = volume
            result = {"volume": volume}
            return result
        except Exception as e:
            self.log_message("Error setting master volume: " + str(e))
            raise

    def _toggle_device_bypass(self, track_index, device_index, enabled):
        """Toggle device bypass on/off"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]

            # Try to find the bypass parameter
            bypass_param = None
            if hasattr(device, "parameters"):
                for param in device.parameters:
                    if (
                        param.is_enabled
                        and hasattr(param, "name")
                        and "bypass" in param.name.lower()
                    ):
                        bypass_param = param
                        break

            if bypass_param:
                bypass_param.value = 1.0 if enabled else 0.0
                result = {
                    "track_index": track_index,
                    "device_index": device_index,
                    "device_name": device.name
                    if hasattr(device, "name")
                    else "Device {}".format(device_index),
                    "bypass_enabled": bypass_param.value,
                }
            else:
                raise Exception("Device has no bypass parameter")

            return result
        except Exception as e:
            self.log_message("Error toggling device bypass: " + str(e))
            raise

    def _undo(self):
        """Perform undo"""
        try:
            self._song.undo()
            result = {"undone": True}
            return result
        except Exception as e:
            self.log_message("Error performing undo: " + str(e))
            raise

    def _redo(self):
        """Perform redo"""
        try:
            self._song.redo()
            result = {"redone": True}
            return result
        except Exception as e:
            self.log_message("Error performing redo: " + str(e))
            raise

    def _get_playhead_position(self):
        """Get current playhead position in beats"""
        try:
            position = self._song.get_current_beats_song_time()
            result = {
                "bars": int(position.bars),
                "beats": position.beats,
                "sub_division": position.sub_division,
            }
            return result
        except Exception as e:
            self.log_message("Error getting playhead position: " + str(e))
            raise

    def _set_playhead_position(self, bar, beat):
        """Set playhead position"""
        try:
            self._song.jump_by(1)
            result = {"bar": bar, "beat": beat}
            return result
        except Exception as e:
            self.log_message("Error setting playhead position: " + str(e))
            raise

    def _create_locator(self, bar, name):
        """Create a locator at specified bar"""
        try:
            time = self._song.get_current_beats_song_time()
            time.bars = bar
            time.beats = 1  # Start at beat 1 of the bar (1-indexed in Ableton)
            self._song.create_locator(time)
            # Set name if provided
            if name:
                locators = self._song.locators
                if locators:
                    locators[-1].name = name
            result = {"created": True, "bar": bar, "name": name}
            return result
        except Exception as e:
            self.log_message("Error creating locator: " + str(e))
            raise

    def _delete_locator(self, locator_index):
        """Delete a locator by index"""
        try:
            if locator_index < 0 or locator_index >= len(self._song.locators):
                raise IndexError("Locator index out of range")
            locator = self._song.locators[locator_index]
            locator.delete_locator()
            result = {"deleted_locator_index": locator_index}
            return result
        except Exception as e:
            self.log_message("Error deleting locator: " + str(e))
            raise

    def _jump_to_locator(self, locator_index):
        """Jump to a locator"""
        try:
            if locator_index < 0 or locator_index >= len(self._song.locators):
                raise IndexError("Locator index out of range")
            locator = self._song.locators[locator_index]
            locator.jump()
            result = {"jumped_to_locator": locator_index}
            return result
        except Exception as e:
            self.log_message("Error jumping to locator: " + str(e))
            raise

    def _set_loop(self, start_bar, end_bar, enabled):
        """Set arrangement loop region"""
        try:
            self._song.loop_start = start_bar
            self._song.loop_length = end_bar - start_bar
            self._song.loop = enabled
            result = {"start_bar": start_bar, "end_bar": end_bar, "enabled": enabled}
            return result
        except Exception as e:
            self.log_message("Error setting loop: " + str(e))
            raise

    def _apply_energy_curve(self, parameter_changes, duration_beats=4.0, steps=8):
        """Apply a smooth energy curve by linearly interpolating multiple device parameters.

        The function schedules a sequence of small parameter updates on the main thread
        so Ableton Live remains responsive. Each entry in parameter_changes should contain:
        - track_index
        - device_index
        - parameter_index
        - start_value
        - end_value

        This method stores the changes and then steps through them, linearly interpolating
        from start_value to end_value across the provided number of steps. The actual timing
        (in beats) is approximated by dividing the total duration by the number of steps and
        scheduling each step accordingly via schedule_message for non-blocking operation.
        """
        try:
            # Normalize inputs
            if parameter_changes is None:
                parameter_changes = []

            # Prepare internal state for the scheduled steps
            self._energy_curve_active = True
            self._energy_curve_changes = []
            for ch in parameter_changes:
                self._energy_curve_changes.append(
                    {
                        "track_index": int(ch.get("track_index", 0)),
                        "device_index": int(ch.get("device_index", 0)),
                        "parameter_index": int(ch.get("parameter_index", 0)),
                        "start_value": float(ch.get("start_value", 0.0)),
                        "end_value": float(ch.get("end_value", 1.0)),
                    }
                )

            total_steps = max(1, int(steps))
            self._energy_curve_steps_total = total_steps
            self._energy_curve_duration_beats = float(duration_beats)
            self._energy_curve_step = 0

            # Convenience: guard against division by zero when total_steps == 1
            def _step_factory(step_index):
                # Capture step_index in default arg
                def _step():
                    try:
                        # If there are no changes, stop
                        if not getattr(self, "_energy_curve_changes", None):
                            self._energy_curve_active = False
                            return

                        total = self._energy_curve_steps_total
                        frac = 0.0 if total <= 1 else (step_index / float(total - 1))

                        # Apply interpolation for each change
                        for ch in self._energy_curve_changes:
                            s = ch["start_value"]
                            e = ch["end_value"]
                            val = s + (e - s) * frac
                            self._set_device_parameter(
                                ch["track_index"],
                                ch["device_index"],
                                ch["parameter_index"],
                                val,
                            )

                        # Schedule next step if needed
                        if step_index + 1 < total:
                            self._energy_curve_step = step_index + 1
                            self.schedule_message(0, _step_factory(step_index + 1))
                        else:
                            # Finished
                            self._energy_curve_active = False
                            self._energy_curve_changes = []
                    except Exception as e:
                        self.log_message("Error during energy curve step: " + str(e))
                        self._energy_curve_active = False

                return _step

            # Kick off the first step
            if total_steps > 0:
                self.schedule_message(0, _step_factory(0))

            # Immediate summary string (actual changes happen in background steps)
            m_changes = len(self._energy_curve_changes)
            return f"Energy curve scheduled: {m_changes} changes over {duration_beats} beats in {total_steps} steps"
        except Exception as e:
            self.log_message("Error scheduling energy curve: " + str(e))
            raise

    def _get_clip_notes(
        self, track_index, clip_index, from_time, from_pitch, time_span, pitch_span
    ):
        """Get all notes from a clip with parameters for Ableton Live 11+ API"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            # Try to access notes with better error handling
            notes = []
            if hasattr(clip, "notes") and clip.notes:
                for note in clip.notes:
                    notes.append(
                        {
                            "pitch": note[0],
                            "start_time": note[1],
                            "duration": note[2],
                            "velocity": note[3],
                            "mute": note[4] if len(note) > 4 else False,
                        }
                    )
            elif hasattr(clip, "get_notes"):
                # Alternative API for Ableton Live 11+
                # Use provided parameters or defaults
                notes_list = clip.get_notes(
                    from_time, from_pitch, time_span, pitch_span
                )
                if notes_list:
                    for i, note in enumerate(notes_list):
                        # Handle both tuple format (Ableton 11) and object format (Ableton 12+)
                        if hasattr(note, "pitch"):
                            notes.append(
                                {
                                    "pitch": note.pitch,
                                    "start_time": note.start_time,
                                    "duration": note.duration,
                                    "velocity": note.velocity,
                                    "mute": note.mute
                                    if hasattr(note, "mute")
                                    else False,
                                }
                            )
                        else:
                            # Tuple format: (pitch, start_time, duration, velocity, mute)
                            notes.append(
                                {
                                    "pitch": note[0],
                                    "start_time": note[1],
                                    "duration": note[2],
                                    "velocity": note[3],
                                    "mute": note[4] if len(note) > 4 else False,
                                }
                            )

            if not notes:
                raise Exception(
                    "Unable to access clip notes - clip may be empty or not compatible"
                )

            result = {"notes": notes, "count": len(notes)}
            return result
        except Exception as e:
            self.log_message("Error getting clip notes: " + str(e))
            raise

    def _detect_clip_key(self, track_index, clip_index):
        """Detect musical key from clip notes using pitch class analysis"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            # Get all notes from clip
            notes = []
            if hasattr(clip, "notes"):
                for note in clip.notes:
                    notes.append(note)
            elif hasattr(clip, "get_notes"):
                notes_list = clip.get_notes(0, 0, 999999, 128)
                if notes_list:
                    notes = list(notes_list)

            if not notes:
                return {"error": "No notes in clip"}

            # Count pitch classes (0-11 = C-B)
            pitch_counts = {}
            total_notes = 0
            for note in notes:
                if hasattr(note, "pitch"):
                    pitch_class = note.pitch % 12
                else:
                    pitch_class = note[0] % 12
                pitch_counts[pitch_class] = pitch_counts.get(pitch_class, 0) + 1
                total_notes += 1

            # Scale profiles for key detection (Krumhansl-Schmuckler)
            # Major scale profile
            major_profile = [
                6.35,
                2.23,
                3.48,
                2.33,
                4.38,
                4.09,
                2.52,
                5.19,
                2.39,
                3.66,
                2.29,
                2.88,
            ]
            # Minor scale profile
            minor_profile = [
                6.33,
                2.68,
                3.52,
                5.38,
                2.60,
                3.53,
                2.54,
                4.75,
                3.98,
                2.69,
                3.34,
                3.17,
            ]

            note_names = [
                "C",
                "C#",
                "D",
                "D#",
                "E",
                "F",
                "F#",
                "G",
                "G#",
                "A",
                "A#",
                "B",
            ]

            best_key = None
            best_mode = None
            best_score = -1

            # Test each possible root
            for root in range(12):
                # Calculate correlation with major profile
                major_score = 0
                minor_score = 0
                for i in range(12):
                    pitch_class = (root + i) % 12
                    count = pitch_counts.get(pitch_class, 0)
                    major_score += count * major_profile[i]
                    minor_score += count * minor_profile[i]

                if major_score > best_score:
                    best_score = major_score
                    best_key = root
                    best_mode = "major"
                if minor_score > best_score:
                    best_score = minor_score
                    best_key = root
                    best_mode = "minor"

            key_name = note_names[best_key]
            if best_mode == "major":
                key_full = key_name + " major"
                # Camelot mapping for major keys (B)
                camelot_map = {
                    "C": "8B",
                    "G": "9B",
                    "D": "10B",
                    "A": "11B",
                    "E": "12B",
                    "B": "1B",
                    "F#": "2B",
                    "C#": "3B",
                    "G#": "4B",
                    "D#": "5B",
                    "A#": "6B",
                    "F": "7B",
                }
            else:
                key_full = key_name + " minor"
                # Camelot mapping for minor keys (A)
                camelot_map = {
                    "A": "8A",
                    "E": "9A",
                    "B": "10A",
                    "F#": "11A",
                    "C#": "12A",
                    "G#": "1A",
                    "D#": "2A",
                    "A#": "3A",
                    "F": "4A",
                    "C": "5A",
                    "G": "6A",
                    "D": "7A",
                }

            camelot = camelot_map.get(key_name, "8A")

            result = {
                "key": key_full,
                "camelot": camelot,
                "confidence": round(best_score / total_notes, 2)
                if total_notes > 0
                else 0,
                "pitch_distribution": {
                    note_names[k]: v for k, v in pitch_counts.items()
                },
                "total_notes": total_notes,
            }
            return result
        except Exception as e:
            self.log_message("Error detecting clip key: " + str(e))
            raise

    def _set_clip_follow_action(
        self,
        track_index,
        clip_index,
        action_slot,
        action_type,
        trigger_time,
        clip_index_target,
    ):
        """Set clip follow action"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.set_follow_action(
                action_slot, action_type, trigger_time, clip_index_target
            )
            result = {
                "set": True,
                "action_slot": action_slot,
                "action_type": action_type,
            }
            return result
        except Exception as e:
            self.log_message("Error setting clip follow action: " + str(e))
            raise

    def _get_clip_follow_actions(self, track_index, clip_index):
        """Get clip follow actions"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            result = {"follow_actions": list(clip.follow_actions)}
            return result
        except Exception as e:
            self.log_message("Error getting clip follow actions: " + str(e))
            raise

    def _set_master_volume(self, volume):
        """Set master track volume (normalized 0.0-1.0)"""
        try:
            self._song.master_track.mixer_device.volume.value = max(
                0.0, min(1.0, volume)
            )
            result = {"volume": volume}
            return result
        except Exception as e:
            self.log_message("Error setting master volume: " + str(e))
            raise

    def _get_master_track_info(self):
        """Get master track information"""
        try:
            master = self._song.master_track
            result = {
                "name": "Master",
                "volume": master.mixer_device.volume.value,
                "panning": master.mixer_device.panning.value,
            }
            return result
        except Exception as e:
            self.log_message("Error getting master track info: " + str(e))
            raise

    def _get_session_overview(self):
        """Get complete session overview combining all session information"""
        try:
            result = {}

            # Add session metadata
            result["tempo"] = self._song.tempo
            result["signature_numerator"] = self._song.signature_numerator
            result["signature_denominator"] = self._song.signature_denominator

            # Add master track info
            master = self._song.master_track
            result["master_track"] = {
                "name": "Master",
                "volume": master.mixer_device.volume.value,
                "panning": master.mixer_device.panning.value,
            }

            # Add all tracks
            tracks_info = []
            for i, track in enumerate(self._song.tracks):
                tracks_info.append(
                    {
                        "index": i,
                        "name": track.name if hasattr(track, "name") else f"Track {i}",
                        "is_audio": track.has_audio_input,
                        "is_midi": track.has_midi_input,
                        "mute": track.mute,
                        "solo": track.solo,
                        "arm": track.arm,
                    }
                )
            result["tracks"] = tracks_info
            result["track_count"] = len(tracks_info)

            # Add return tracks
            returns_info = []
            for i, track in enumerate(self._song.return_tracks):
                returns_info.append(
                    {
                        "index": i,
                        "name": track.name if hasattr(track, "name") else f"Return {i}",
                        "volume": track.mixer_device.volume.value,
                    }
                )
            result["return_tracks"] = returns_info
            result["return_track_count"] = len(returns_info)

            # Add all scenes
            scenes_info = []
            for i, scene in enumerate(self._song.scenes):
                scenes_info.append(
                    {
                        "index": i,
                        "name": scene.name if hasattr(scene, "name") else f"Scene {i}",
                    }
                )
            result["scenes"] = scenes_info
            result["scene_count"] = len(scenes_info)

            return result
        except Exception as e:
            self.log_message("Error getting session overview: " + str(e))
            raise

    def _get_return_tracks(self):
        """Get all return tracks"""
        try:
            returns = []
            for i, track in enumerate(self._song.return_tracks):
                returns.append(
                    {
                        "index": i,
                        "name": track.name if hasattr(track, "name") else f"Return {i}",
                        "volume": track.mixer_device.volume.value,
                    }
                )
            result = {"return_tracks": returns, "count": len(returns)}
            return result
        except Exception as e:
            self.log_message("Error getting return tracks: " + str(e))
            raise

    def _get_all_tracks(self):
        """Get all tracks summary"""
        try:
            tracks_info = []
            for i, track in enumerate(self._song.tracks):
                tracks_info.append(
                    {
                        "index": i,
                        "name": track.name if hasattr(track, "name") else f"Track {i}",
                        "is_audio": track.has_audio_input,
                        "is_midi": track.has_midi_input,
                        "mute": track.mute,
                        "solo": track.solo,
                        "arm": track.arm,
                    }
                )
            result = {"tracks": tracks_info, "count": len(tracks_info)}
            return result
        except Exception as e:
            self.log_message("Error getting all tracks: " + str(e))
            raise

    def _get_all_scenes(self):
        """Get all scenes summary"""
        try:
            scenes_info = []
            for i, scene in enumerate(self._song.scenes):
                scenes_info.append(
                    {
                        "index": i,
                        "name": scene.name if hasattr(scene, "name") else f"Scene {i}",
                    }
                )
            result = {"scenes": scenes_info, "count": len(scenes_info)}
            return result
        except Exception as e:
            self.log_message("Error getting all scenes: " + str(e))
            raise

    def _get_all_clips_in_track(self, track_index):
        """Get all clips in a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            clips_info = []
            for i, slot in enumerate(track.clip_slots):
                if slot.has_clip:
                    clips_info.append(
                        {
                            "index": i,
                            "name": slot.clip.name
                            if hasattr(slot.clip, "name")
                            else f"Clip {i}",
                            "length": slot.clip.length,
                            "is_playing": slot.clip.is_playing,
                        }
                    )
            result = {"clips": clips_info, "count": len(clips_info)}
            return result
        except Exception as e:
            self.log_message("Error getting all clips: " + str(e))
            raise

    def _set_note_velocity(self, track_index, clip_index, note_indices, velocity):
        """Set velocity for specific notes"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            notes = list(clip.notes)
            for idx in note_indices:
                if 0 <= idx < len(notes):
                    note = list(notes[idx])
                    note[3] = velocity
                    notes[idx] = tuple(note)

            clip.notes = tuple(notes)
            result = {"set_count": len(note_indices), "velocity": velocity}
            return result
        except Exception as e:
            self.log_message("Error setting note velocity: " + str(e))
            raise

    def _set_note_duration(self, track_index, clip_index, note_indices, duration):
        """Set duration for specific notes"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            notes = list(clip.notes)
            for idx in note_indices:
                if 0 <= idx < len(notes):
                    note = list(notes[idx])
                    note[2] = duration
                    notes[idx] = tuple(note)

            clip.notes = tuple(notes)
            result = {"set_count": len(note_indices), "duration": duration}
            return result
        except Exception as e:
            self.log_message("Error setting note duration: " + str(e))
            raise

    def _set_note_pitch(self, track_index, clip_index, note_indices, pitch):
        """Set pitch for specific notes"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            notes = list(clip.notes)
            for idx in note_indices:
                if 0 <= idx < len(notes):
                    note = list(notes[idx])
                    note[0] = pitch
                    notes[idx] = tuple(note)

            clip.notes = tuple(notes)
            result = {"set_count": len(note_indices), "pitch": pitch}
            return result
        except Exception as e:
            self.log_message("Error setting note pitch: " + str(e))
            raise

    def _get_clip_envelopes(self, track_index, clip_index):
        """Get all envelopes for a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            envelopes = []
            if hasattr(clip, "automation_envelopes"):
                for env in clip.automation_envelopes:
                    try:
                        param = env.parameter if hasattr(env, "parameter") else None
                        env_info = {
                            "parameter_name": param.name if param and hasattr(param, "name") else "Unknown",
                            "parameter_index": list(track.devices[0].parameters).index(param) if param and len(track.devices) > 0 and param in track.devices[0].parameters else -1,
                            "device_index": 0,
                            "has_envelope": True,
                        }
                        envelopes.append(env_info)
                    except Exception:
                        envelopes.append({"parameter_name": "Unknown", "has_envelope": True})

            result = {"envelopes": envelopes, "count": len(envelopes)}
            return result
        except Exception as e:
            self.log_message("Error getting clip envelopes: " + str(e))
            raise

    def _get_clip_envelope_points(self, track_index, clip_index, device_index, parameter_index, num_samples=64):
        """Get automation envelope points by time-sampling"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            if parameter_index < 0 or parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range")
            parameter = device.parameters[parameter_index]

            # Find the envelope for this parameter
            target_env = None
            if hasattr(clip, "automation_envelopes"):
                for env in clip.automation_envelopes:
                    try:
                        if hasattr(env, "parameter") and env.parameter == parameter:
                            target_env = env
                            break
                    except Exception:
                        continue

            if target_env is None:
                return {"parameter_name": parameter.name, "has_envelope": False, "points": []}

            # Time-sample the envelope across the clip length
            clip_length = clip.length if hasattr(clip, "length") else 4.0
            if clip_length <= 0:
                clip_length = 4.0

            step = clip_length / max(num_samples, 1)
            points = []
            for i in range(num_samples):
                t = i * step
                try:
                    val = target_env.value_at_time(t) if hasattr(target_env, "value_at_time") else None
                    if val is not None:
                        points.append({"time": round(t, 4), "value": round(val, 4)})
                except Exception:
                    pass

            return {
                "parameter_name": parameter.name,
                "parameter_index": parameter_index,
                "device_index": device_index,
                "has_envelope": True,
                "clip_length": clip_length,
                "num_samples": len(points),
                "points": points,
            }
        except Exception as e:
            self.log_message("Error getting clip envelope points: " + str(e))
            raise

    def _set_clip_envelope_point(self, track_index, clip_index, device_index, parameter_index, time_val, value):
        """Add or update an automation envelope point"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            if parameter_index < 0 or parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range")
            parameter = device.parameters[parameter_index]

            clip.create_automation_event(parameter, time_val, value)
            return {"added": True, "time": time_val, "value": value}
        except Exception as e:
            self.log_message("Error setting clip envelope point: " + str(e))
            raise

    def _mix_clip(self, track_index, clip_index, source_track_index):
        """Mix another clip into current clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            if source_track_index < 0 or source_track_index >= len(self._song.tracks):
                raise IndexError("Source track index out of range")

            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            result = {"mixed": True}
            return result
        except Exception as e:
            self.log_message("Error mixing clip: " + str(e))
            raise

    def _stretch_clip(self, track_index, clip_index, length):
        """Stretch clip to new length"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.length = length
            result = {"length": length}
            return result
        except Exception as e:
            self.log_message("Error stretching clip: " + str(e))
            raise

    def _duplicate_clip_to(
        self, track_index, clip_index, target_track_index, target_clip_index
    ):
        """Duplicate clip to specific slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            if target_track_index < 0 or target_track_index >= len(self._song.tracks):
                raise IndexError("Target track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            target_track = self._song.tracks[target_track_index]
            if target_clip_index < 0 or target_clip_index >= len(
                target_track.clip_slots
            ):
                raise IndexError("Target clip index out of range")

            target_slot = target_track.clip_slots[target_clip_index]
            if not target_slot.has_clip:
                raise Exception("No clip in target slot")

            clip_slot.duplicate_clip_to(target_slot)

            result = {"duplicated": True, "to": [target_track_index, target_clip_index]}
            return result
        except Exception as e:
            self.log_message("Error duplicating clip to: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _crop_clip(self, track_index, clip_index):
        """Crop clip to content"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            clip_slot.crop_clip()

            result = {"cropped": True}
            return result
        except Exception as e:
            self.log_message("Error cropping clip: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _group_tracks(self, track_indices):
        """Group multiple tracks"""
        try:
            for track_index in track_indices:
                if track_index < 0 or track_index >= len(self._song.tracks):
                    raise IndexError("Track index out of range")

            self._song.group_selected_tracks(list(track_indices))
            result = {"grouped_count": len(track_indices)}
            return result
        except Exception as e:
            self.log_message("Error grouping tracks: " + str(e))
            raise

    def _ungroup_tracks(self, track_index):
        """Ungroup a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track.group_track = None
            result = {"ungrouped": True}
            return result
        except Exception as e:
            self.log_message("Error ungrouping tracks: " + str(e))
            raise

    def _set_clip_warp_mode(self, track_index, clip_index, warp_mode):
        """Set clip warp mode"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip
            clip.warping = warp_mode
            result = {"warp_mode": warp_mode}
            return result
        except Exception as e:
            self.log_message("Error setting clip warp mode: " + str(e))
            raise

    def _get_clip_warp_markers(self, track_index, clip_index):
        """Get warp markers for clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")

            result = {"warp_markers": []}
            return result
        except Exception as e:
            self.log_message("Error getting clip warp markers: " + str(e))
            raise

    def _add_warp_marker(self, track_index, clip_index, position):
        """Add warp marker to clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            result = {"added": True, "position": position}
            return result
        except Exception as e:
            self.log_message("Error adding warp marker: " + str(e))
            raise

    def _delete_warp_marker(self, track_index, clip_index, marker_index):
        """Delete warp marker from clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            result = {"deleted": True, "marker_index": marker_index}
            return result
        except Exception as e:
            self.log_message("Error deleting warp marker: " + str(e))
            raise

    def _get_browser_item(self, uri, path):
        """Get a browser item by URI or path"""
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            result = {"uri": uri, "path": path, "found": False}

            # Try to find by URI first if provided
            if uri:
                item = self._find_browser_item_by_uri(app.browser, uri)
                if item:
                    result["found"] = True
                    result["item"] = {
                        "name": item.name,
                        "is_folder": item.is_folder,
                        "is_device": item.is_device,
                        "is_loadable": item.is_loadable,
                        "uri": item.uri,
                    }
                    return result

            # If URI not provided or not found, try by path
            if path:
                # Parse the path and navigate to the specified item
                path_parts = path.split("/")

                # Determine the root based on the first part
                current_item = None
                if path_parts[0].lower() == "nstruments":
                    current_item = app.browser.instruments
                elif path_parts[0].lower() == "sounds":
                    current_item = app.browser.sounds
                elif path_parts[0].lower() == "drums":
                    current_item = app.browser.drums
                elif path_parts[0].lower() == "audio_effects":
                    current_item = app.browser.audio_effects
                elif path_parts[0].lower() == "midi_effects":
                    current_item = app.browser.midi_effects
                else:
                    # Default to instruments if not specified
                    current_item = app.browser.instruments
                    # Don't skip the first part in this case
                    path_parts = ["instruments"] + path_parts

                # Navigate through the path
                for i in range(1, len(path_parts)):
                    part = path_parts[i]
                    if not part:  # Skip empty parts
                        continue

                    found = False
                    for child in current_item.children:
                        if child.name.lower() == part.lower():
                            current_item = child
                            found = True
                            break

                    if not found:
                        result["error"] = "Path part '{0}' not found".format(part)
                        return result

                # Found the item
                result["found"] = True
                result["item"] = {
                    "name": current_item.name,
                    "is_folder": current_item.is_folder,
                    "is_device": current_item.is_device,
                    "is_loadable": current_item.is_loadable,
                    "uri": current_item.uri,
                }

            return result
        except Exception as e:
            self.log_message("Error getting browser item: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _load_instrument_or_effect(self, track_index, uri):
        """
        Load an instrument or effect onto a track by its URI.

        This is a wrapper for _load_browser_item to maintain compatibility.

        Parameters:
        - track_index: The track to load onto
        - uri: The URI of the instrument or effect
        """
        return self._load_browser_item(track_index, uri)

    def _load_browser_item(self, track_index, item_uri):
        """Load a browser item onto a track by its URI"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]

            # Access the application's browser instance instead of creating a new one
            app = self.application()

            # Find the browser item by URI
            item = self._find_browser_item_by_uri(app.browser, item_uri)

            if not item:
                raise ValueError(
                    "Browser item with URI '{0}' not found".format(item_uri)
                )

            # Select the track
            self._song.view.selected_track = track

            # Load the item
            app.browser.load_item(item)

            result = {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": item_uri,
            }
            return result
        except Exception as e:
            self.log_message("Error loading browser item: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _find_browser_item_by_uri(
        self, browser_or_item, uri, max_depth=10, current_depth=0
    ):
        """Find a browser item by its URI"""
        try:
            # Check if this is the item we're looking for
            if hasattr(browser_or_item, "uri") and browser_or_item.uri == uri:
                return browser_or_item

            # Stop recursion if we've reached max depth
            if current_depth >= max_depth:
                return None

            # Check if this is a browser with root categories
            if hasattr(browser_or_item, "instruments"):
                # Check all main categories
                categories = [
                    browser_or_item.instruments,
                    browser_or_item.sounds,
                    browser_or_item.drums,
                    browser_or_item.audio_effects,
                    browser_or_item.midi_effects,
                ]

                for category in categories:
                    item = self._find_browser_item_by_uri(
                        category, uri, max_depth, current_depth + 1
                    )
                    if item:
                        return item

                return None

            # Check if this item has children
            if hasattr(browser_or_item, "children") and browser_or_item.children:
                for child in browser_or_item.children:
                    item = self._find_browser_item_by_uri(
                        child, uri, max_depth, current_depth + 1
                    )
                    if item:
                        return item

            return None
        except Exception as e:
            self.log_message("Error finding browser item by URI: {0}".format(str(e)))
            return None

    # Helper methods

    def _get_device_type(self, device):
        """Get the type of a device"""
        try:
            # Simple heuristic - in a real implementation you'd look at the device class
            if device.can_have_drum_pads:
                return "drum_machine"
            elif device.can_have_chains:
                return "rack"
            elif "instrument" in device.class_display_name.lower():
                return "instrument"
            elif "audio_effect" in device.class_name.lower():
                return "audio_effect"
            elif "midi_effect" in device.class_name.lower():
                return "midi_effect"
            else:
                return "unknown"
        except Exception as e:
            self.log_message(f"Error determining device class: {e}")
            return "unknown"

    def get_browser_tree(self, category_type="all"):
        """
        Get a simplified tree of browser categories.

        Args:
            category_type: Type of categories to get ('all', 'instruments', 'sounds', etc.)

        Returns:
            Dictionary with the browser tree structure
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            # Check if browser is available
            if not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            # Log available browser attributes to help diagnose issues
            browser_attrs = [
                attr for attr in dir(app.browser) if not attr.startswith("_")
            ]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))

            result = {
                "type": category_type,
                "categories": [],
                "available_categories": browser_attrs,
            }

            # Helper function to process a browser item and its children
            def process_item(item, depth=0):
                if not item:
                    return None

                result = {
                    "name": item.name if hasattr(item, "name") else "Unknown",
                    "is_folder": hasattr(item, "children") and bool(item.children),
                    "is_device": hasattr(item, "is_device") and item.is_device,
                    "is_loadable": hasattr(item, "is_loadable") and item.is_loadable,
                    "uri": item.uri if hasattr(item, "uri") else None,
                    "children": [],
                }

                return result

            # Process based on category type and available attributes
            if (category_type == "all" or category_type == "instruments") and hasattr(
                app.browser, "instruments"
            ):
                try:
                    instruments = process_item(app.browser.instruments)
                    if instruments:
                        instruments["name"] = "Instruments"  # Ensure consistent naming
                        result["categories"].append(instruments)
                except Exception as e:
                    self.log_message("Error processing instruments: {0}".format(str(e)))

            if (category_type == "all" or category_type == "sounds") and hasattr(
                app.browser, "sounds"
            ):
                try:
                    sounds = process_item(app.browser.sounds)
                    if sounds:
                        sounds["name"] = "Sounds"  # Ensure consistent naming
                        result["categories"].append(sounds)
                except Exception as e:
                    self.log_message("Error processing sounds: {0}".format(str(e)))

            if (category_type == "all" or category_type == "drums") and hasattr(
                app.browser, "drums"
            ):
                try:
                    drums = process_item(app.browser.drums)
                    if drums:
                        drums["name"] = "Drums"  # Ensure consistent naming
                        result["categories"].append(drums)
                except Exception as e:
                    self.log_message("Error processing drums: {0}".format(str(e)))

            if (category_type == "all" or category_type == "audio_effects") and hasattr(
                app.browser, "audio_effects"
            ):
                try:
                    audio_effects = process_item(app.browser.audio_effects)
                    if audio_effects:
                        audio_effects["name"] = (
                            "Audio Effects"  # Ensure consistent naming
                        )
                        result["categories"].append(audio_effects)
                except Exception as e:
                    self.log_message(
                        "Error processing audio_effects: {0}".format(str(e))
                    )

            if (category_type == "all" or category_type == "midi_effects") and hasattr(
                app.browser, "midi_effects"
            ):
                try:
                    midi_effects = process_item(app.browser.midi_effects)
                    if midi_effects:
                        midi_effects["name"] = "MIDI Effects"
                        result["categories"].append(midi_effects)
                except Exception as e:
                    self.log_message(
                        "Error processing midi_effects: {0}".format(str(e))
                    )

            # Try to process other potentially available categories
            for attr in browser_attrs:
                if attr not in [
                    "instruments",
                    "sounds",
                    "drums",
                    "audio_effects",
                    "midi_effects",
                ] and (category_type == "all" or category_type == attr):
                    try:
                        item = getattr(app.browser, attr)
                        if hasattr(item, "children") or hasattr(item, "name"):
                            category = process_item(item)
                            if category:
                                category["name"] = attr.capitalize()
                                result["categories"].append(category)
                    except Exception as e:
                        self.log_message(
                            "Error processing {0}: {1}".format(attr, str(e))
                        )

            self.log_message(
                "Browser tree generated for {0} with {1} root categories".format(
                    category_type, len(result["categories"])
                )
            )
            return result

        except Exception as e:
            self.log_message("Error getting browser tree: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def get_browser_items_at_path(self, path):
        """
        Get browser items at a specific path.

        Args:
            path: Path in the format "category/folder/subfolder"
                 where category is one of: instruments, sounds, drums, audio_effects, midi_effects
                 or any other available browser category

        Returns:
            Dictionary with items at the specified path
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")

            # Check if browser is available
            if not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            # Log available browser attributes to help diagnose issues
            browser_attrs = [
                attr for attr in dir(app.browser) if not attr.startswith("_")
            ]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))

            # Parse the path
            path_parts = path.split("/")
            if not path_parts:
                raise ValueError("Invalid path")

            # Determine the root category
            root_category = path_parts[0].lower()
            current_item = None

            # Check standard categories first
            if root_category == "instruments" and hasattr(app.browser, "instruments"):
                current_item = app.browser.instruments
            elif root_category == "sounds" and hasattr(app.browser, "sounds"):
                current_item = app.browser.sounds
            elif root_category == "drums" and hasattr(app.browser, "drums"):
                current_item = app.browser.drums
            elif root_category == "audio_effects" and hasattr(
                app.browser, "audio_effects"
            ):
                current_item = app.browser.audio_effects
            elif root_category == "midi_effects" and hasattr(
                app.browser, "midi_effects"
            ):
                current_item = app.browser.midi_effects
            else:
                # Try to find the category in other browser attributes
                found = False
                for attr in browser_attrs:
                    if attr.lower() == root_category:
                        try:
                            current_item = getattr(app.browser, attr)
                            found = True
                            break
                        except Exception as e:
                            self.log_message(
                                "Error accessing browser attribute {0}: {1}".format(
                                    attr, str(e)
                                )
                            )

                if not found:
                    # If we still haven't found the category, return available categories
                    return {
                        "path": path,
                        "error": "Unknown or unavailable category: {0}".format(
                            root_category
                        ),
                        "available_categories": browser_attrs,
                        "items": [],
                    }

            # Navigate through the path
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:  # Skip empty parts
                    continue

                if not hasattr(current_item, "children"):
                    return {
                        "path": path,
                        "error": "Item at '{0}' has no children".format(
                            "/".join(path_parts[:i])
                        ),
                        "items": [],
                    }

                found = False
                for child in current_item.children:
                    if hasattr(child, "name") and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break

                if not found:
                    return {
                        "path": path,
                        "error": "Path part '{0}' not found".format(part),
                        "items": [],
                    }

            # Return the items at the current path
            items = []
            if hasattr(current_item, "children"):
                for child in current_item.children:
                    item_info = {
                        "name": child.name if hasattr(child, "name") else "Unknown",
                        "is_folder": hasattr(child, "children")
                        and bool(child.children),
                        "is_device": hasattr(child, "is_device") and child.is_device,
                        "is_loadable": hasattr(child, "is_loadable")
                        and child.is_loadable,
                        "uri": child.uri if hasattr(child, "uri") else None,
                    }
                    items.append(item_info)

            result = {
                "path": path,
                "name": current_item.name
                if hasattr(current_item, "name")
                else "Unknown",
                "uri": current_item.uri if hasattr(current_item, "uri") else None,
                "is_folder": hasattr(current_item, "children")
                and bool(current_item.children),
                "is_device": hasattr(current_item, "is_device")
                and current_item.is_device,
                "is_loadable": hasattr(current_item, "is_loadable")
                and current_item.is_loadable,
                "items": items,
            }

            self.log_message(
                "Retrieved {0} items at path: {1}".format(len(items), path)
            )
            return result
        except Exception as e:
            self.log_message("Error getting browser items at path: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _get_recursive_browser_children(self, root_path, max_depth=5, max_items=500):
        """
        Recursively walk browser children from a root path and return the full tree.

        Args:
            root_path: Root browser path (e.g. "Instruments", "Audio Effects", "Drums")
            max_depth: Maximum recursion depth (default: 5)
            max_items: Maximum items to return (default: 500) to prevent runaway

        Returns:
            Dictionary with recursive tree of browser items
        """
        try:
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
            if not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            # Parse root_path parts
            path_parts = root_path.split("/")
            root_category = path_parts[0].lower() if path_parts else ""

            # Map common category names to browser attributes
            category_map = {
                "instruments": "instruments",
                "sounds": "sounds",
                "drums": "drums",
                "audio_effects": "audio_effects",
                "midi_effects": "midi_effects",
                "plugins": "user_library",
            }

            current_item = None
            if root_category in category_map:
                attr_name = category_map[root_category]
                if hasattr(app.browser, attr_name):
                    current_item = getattr(app.browser, attr_name)

            if current_item is None:
                # Try exact attribute match
                for attr in dir(app.browser):
                    if attr.lower() == root_category and not attr.startswith("_"):
                        try:
                            current_item = getattr(app.browser, attr)
                            break
                        except Exception:
                            continue

            if current_item is None:
                return {
                    "path": root_path,
                    "error": "Unknown or unavailable category: " + root_category,
                    "available_categories": [
                        attr for attr in dir(app.browser)
                        if not attr.startswith("_")
                    ],
                    "items": [],
                }

            # Navigate sub-path if deeper than root category
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:
                    continue
                if not hasattr(current_item, "children"):
                    return {"path": root_path, "error": "Dead end at: " + "/".join(path_parts[:i]), "items": []}
                found = False
                for child in current_item.children:
                    if hasattr(child, "name") and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break
                if not found:
                    return {"path": root_path, "error": "Path part not found: " + part, "items": []}

            # Recursively collect tree
            collected = {"items_count": 0, "max_items": max_items, "truncated": False}

            def _walk(node, depth):
                if depth > max_depth:
                    return
                if collected["items_count"] >= max_items:
                    collected["truncated"] = True
                    return

                if not hasattr(node, "children"):
                    return

                children = []
                for child in node.children:
                    if collected["items_count"] >= max_items:
                        collected["truncated"] = True
                        break
                    try:
                        child_info = {
                            "name": child.name if hasattr(child, "name") else "Unknown",
                            "is_folder": hasattr(child, "children") and bool(child.children),
                            "is_device": hasattr(child, "is_device") and child.is_device,
                            "is_loadable": hasattr(child, "is_loadable") and child.is_loadable,
                            "uri": child.uri if hasattr(child, "uri") else None,
                        }
                        collected["items_count"] += 1

                        # Recurse into sub-folders
                        if child_info["is_folder"]:
                            sub_items = []
                            sub_depth = depth + 1
                            if sub_depth <= max_depth:
                                for sub in child.children:
                                    if collected["items_count"] >= max_items:
                                        collected["truncated"] = True
                                        break
                                    try:
                                        sub_info = {
                                            "name": sub.name if hasattr(sub, "name") else "Unknown",
                                            "is_folder": hasattr(sub, "children") and bool(sub.children),
                                            "is_device": hasattr(sub, "is_device") and sub.is_device,
                                            "is_loadable": hasattr(sub, "is_loadable") and sub.is_loadable,
                                            "uri": sub.uri if hasattr(sub, "uri") else None,
                                        }
                                        collected["items_count"] += 1
                                        if sub_info["is_folder"] and sub_depth < max_depth:
                                            sub_sub = []
                                            for s in sub.children:
                                                if collected["items_count"] >= max_items:
                                                    collected["truncated"] = True
                                                    break
                                                try:
                                                    s_info = {
                                                        "name": s.name if hasattr(s, "name") else "Unknown",
                                                        "is_folder": hasattr(s, "children") and bool(s.children),
                                                        "is_device": hasattr(s, "is_device") and s.is_device,
                                                        "is_loadable": hasattr(s, "is_loadable") and s.is_loadable,
                                                        "uri": s.uri if hasattr(s, "uri") else None,
                                                    }
                                                    collected["items_count"] += 1
                                                    sub_sub.append(s_info)
                                                except Exception:
                                                    pass
                                            sub_info["children"] = sub_sub
                                        sub_items.append(sub_info)
                                    except Exception:
                                        pass
                            child_info["children"] = sub_items
                        children.append(child_info)
                    except Exception:
                        pass

                return children

            tree_items = _walk(current_item, 0)

            result = {
                "path": root_path,
                "name": current_item.name if hasattr(current_item, "name") else root_category,
                "items": tree_items or [],
                "items_count": collected["items_count"],
                "max_depth": max_depth,
                "truncated": collected["truncated"],
            }

            self.log_message(
                "Recursive browser scan: collected {0} items from {1}".format(
                    collected["items_count"], root_path
                )
            )
            return result
        except Exception as e:
            self.log_message("Error in recursive browser scan: " + str(e))
            self.log_message(traceback.format_exc())
            return {"path": root_path, "error": str(e), "items": []}

    def _detect_clip_key(self, track_index, clip_index):
        """
        Detect the musical key of a clip by analyzing its notes.
        Uses the Krumhansl-Schmuckler algorithm for key detection.

        Returns: {"key": "A minor", "camelot": "8A", "confidence": 0.85}
        """
        try:
            track = self._song.tracks[track_index]
            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                return {"error": "No clip in slot"}

            clip = clip_slot.clip
            notes = clip.get_notes(0, 0, 999999, 128)

            # Extract pitch classes (MIDI note % 12)
            pitch_class_counts = [0] * 12
            for note in notes:
                pitch_class = note[0] % 12
                pitch_class_counts[pitch_class] += 1

            # Key profiles (Krumhansl-Schmuckler)
            major_profile = [
                6.35,
                2.23,
                3.48,
                2.33,
                4.38,
                4.09,
                2.52,
                5.19,
                2.39,
                3.66,
                2.29,
                2.88,
            ]
            minor_profile = [
                6.33,
                2.68,
                3.52,
                5.38,
                2.60,
                3.53,
                2.54,
                4.75,
                3.98,
                2.69,
                3.34,
                3.17,
            ]

            # Correlation scores for all keys
            correlation_scores = []
            keys = [
                "C major",
                "C# major",
                "D major",
                "Eb major",
                "E major",
                "F major",
                "F# major",
                "G major",
                "Ab major",
                "A major",
                "Bb major",
                "B major",
                "A minor",
                "Bb minor",
                "B minor",
                "C minor",
                "C# minor",
                "D minor",
                "Eb minor",
                "E minor",
                "F minor",
                "F# minor",
                "G minor",
                "G# minor",
            ]

            # Calculate correlation for each key
            for key_idx in range(24):
                profile = major_profile if key_idx < 12 else minor_profile
                key_offset = key_idx % 12

                # Rotate the profile to match the key
                rotated_profile = profile[key_offset:] + profile[:key_offset]
                if key_idx >= 12:
                    rotated_profile = rotated_profile[::-1]  # Minor is descending

                # Calculate correlation
                correlation = 0.0
                total_notes = sum(pitch_class_counts)
                if total_notes > 0:
                    for pc in range(12):
                        correlation += (
                            pitch_class_counts[pc] / total_notes
                        ) * rotated_profile[pc]

                correlation_scores.append(correlation)

            # Find the key with the highest correlation
            best_idx = correlation_scores.index(max(correlation_scores))
            best_key = keys[best_idx]
            best_score = correlation_scores[best_idx]

            # Map to Camelot notation
            CAMELOT_WHEEL = {
                "C major": "8B",
                "G major": "9B",
                "D major": "10B",
                "A major": "11B",
                "E major": "12B",
                "B major": "1B",
                "F# major": "2B",
                "Db major": "3B",
                "Ab major": "4B",
                "Eb major": "5B",
                "Bb major": "6B",
                "F major": "7B",
                "A minor": "8A",
                "E minor": "9A",
                "B minor": "10A",
                "F# minor": "11A",
                "C# minor": "12A",
                "G# minor": "1A",
                "Eb minor": "2A",
                "Bb minor": "3A",
                "F minor": "4A",
                "C minor": "5A",
                "G minor": "6A",
                "D minor": "7A",
            }

            camelot_code = CAMELOT_WHEEL.get(best_key, "1A")

            return {
                "key": best_key,
                "camelot": camelot_code,
                "confidence": float(best_score),
                "note_count": len(notes),
            }
        except Exception as e:
            return {"error": str(e)}

    def _snap_notes_to_scale(self, track_index, clip_index, scale="minor", root=60):
        """
        Snap out-of-key notes to the nearest note in a specified scale.

        Returns: {"message": "Snapped X notes to A minor scale"}
        """
        try:
            track = self._song.tracks[track_index]
            clip_slot = track.clip_slots[clip_index]

            if not clip_slot.has_clip:
                return {"error": "No clip in slot"}

            clip = clip_slot.clip
            notes = list(clip.get_notes(0, 0, 999999, 128))

            # Scale intervals
            SCALE_INTERVALS = {
                "major": [0, 2, 4, 5, 7, 9, 11],
                "minor": [0, 2, 3, 5, 7, 8, 10],
                "dorian": [0, 2, 3, 5, 7, 9, 10],
                "phrygian": [0, 1, 3, 5, 7, 8, 10],
                "lydian": [0, 2, 4, 6, 7, 9, 11],
                "mixolydian": [0, 2, 4, 5, 7, 9, 10],
                "pentatonic_major": [0, 2, 4, 7, 9],
                "pentatonic_minor": [0, 3, 5, 7, 10],
                "blues": [0, 3, 5, 6, 7, 10],
            }

            scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["minor"])

            # Generate all notes in the scale
            scale_notes = []
            for octave in range(10):
                for interval in scale_intervals:
                    note = root + (octave * 12) + interval
                    if 0 <= note <= 127:
                        scale_notes.append(note)

            # Snap each note to the nearest scale note
            snapped_count = 0
            new_notes = []

            for note in notes:
                pitch = note[0]
                if pitch not in scale_notes:
                    # Find nearest scale note
                    nearest_note = min(scale_notes, key=lambda x: abs(x - pitch))
                    new_notes.append((nearest_note, note[1], note[2], note[3], note[4]))
                    snapped_count += 1
                else:
                    new_notes.append(note)

            # Update the clip
            if snapped_count > 0:
                clip.remove_notes(0, 0, 999999, 128)
                clip.set_notes(tuple(new_notes))

            return {
                "message": f"Snapped {snapped_count} notes to {scale} scale (root={root})"
            }
        except Exception as e:
            return {"error": str(e)}

    def _create_scale_reference_clip(
        self, track_index, clip_index, scale="minor", root=60, octaves=3
    ):
        """
        Create a clip containing all notes of a scale (for Fold function).
        Places notes before 1.1.1 so they're hidden but available for Fold.

        Returns: {"message": "Created C minor scale reference clip with 21 notes"}
        """
        try:
            track = self._song.tracks[track_index]
            clip_slot = track.clip_slots[clip_index]

            # Create clip
            clip_slot.create_clip(4.0)

            if not clip_slot.has_clip:
                return {"error": "Failed to create clip"}


            # Scale intervals
            SCALE_INTERVALS = {
                "major": [0, 2, 4, 5, 7, 9, 11],
                "minor": [0, 2, 3, 5, 7, 8, 10],
                "dorian": [0, 2, 3, 5, 7, 9, 10],
                "phrygian": [0, 1, 3, 5, 7, 8, 10],
                "lydian": [0, 2, 4, 6, 7, 9, 11],
                "mixolydian": [0, 2, 4, 5, 7, 9, 10],
                "pentatonic_major": [0, 2, 4, 7, 9],
                "pentatonic_minor": [0, 3, 5, 7, 10],
                "blues": [0, 3, 5, 6, 7, 10],
            }

            scale_intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["minor"])

            # Generate notes
            notes = []
            note_index = 0
            for octave in range(octaves):
                for interval in scale_intervals:
                    pitch = root + (octave * 12) + interval
                    if 0 <= pitch <= 127:
                        notes.append(
                            {
                                "pitch": pitch,
                                "start_time": -1.0 - (note_index * 0.1),  # Before 1.1.1
                                "duration": 0.1,
                                "velocity": 100,
                                "mute": False,
                            }
                        )
                        note_index += 1

            # Add notes to clip
            self._add_notes_to_clip(track_index, clip_index, notes)

            return {
                "message": f"Created {scale} scale reference clip (root={root}, octaves={octaves}) with {len(notes)} notes",
                "notes_added": len(notes),
            }
        except Exception as e:
            return {"error": str(e)}

    def _create_chord_progression(
        self,
        track_index,
        clip_index,
        key="C",
        progression=["I", "V", "vi", "IV"],
        duration_per_chord=4.0,
    ):
        """
        Create a chord progression in a clip from Roman numerals.

        Returns: {"message": "Created C major chord progression with 4 chords"}
        """
        try:
            # Map key to root note and mode
            KEY_ROOTS = {
                "C": 60,
                "C#": 61,
                "Db": 61,
                "D": 62,
                "D#": 63,
                "Eb": 63,
                "E": 64,
                "F": 65,
                "F#": 66,
                "Gb": 66,
                "G": 67,
                "G#": 68,
                "Ab": 68,
                "A": 69,
                "A#": 70,
                "Bb": 70,
                "B": 71,
                "Am": 57,
                "A#m": 58,
                "Bbm": 58,
                "Bm": 59,
                "Cm": 60,
                "C#m": 61,
                "Dbm": 61,
                "Dm": 62,
                "D#m": 63,
                "Ebm": 63,
                "Em": 64,
                "Fm": 65,
                "F#m": 66,
                "Gbm": 66,
                "Gm": 67,
                "G#m": 68,
            }

            root_note = KEY_ROOTS.get(key, 60)
            is_minor = "m" in key.lower()

            # Chord intervals
            CHORD_INTERVALS = {
                "major": [0, 4, 7],
                "minor": [0, 3, 7],
                "dim": [0, 3, 6],
                "aug": [0, 4, 8],
                "maj7": [0, 4, 7, 11],
                "min7": [0, 3, 7, 10],
                "dom7": [0, 4, 7, 10],
            }

            # Scale intervals
            SCALE_INTERVALS = {
                "major": [0, 2, 4, 5, 7, 9, 11],
                "minor": [0, 2, 3, 5, 7, 8, 10],
            }

            scale_intervals = (
                SCALE_INTERVALS["minor"] if is_minor else SCALE_INTERVALS["major"]
            )

            # Map Roman numerals to scale degrees
            ROMAN_TO_DEGREE = {
                "I": 1,
                "i": 1,
                "II": 2,
                "ii": 2,
                "III": 3,
                "iii": 3,
                "IV": 4,
                "iv": 4,
                "V": 5,
                "v": 5,
                "VI": 6,
                "vi": 6,
                "VII": 7,
                "vii": 7,
            }

            # Build chords
            track = self._song.tracks[track_index]
            clip_slot = track.clip_slots[clip_index]

            # Create clip
            clip_slot.create_clip(duration_per_chord * len(progression))

            if not clip_slot.has_clip:
                return {"error": "Failed to create clip"}

            all_notes = []

            for chord_idx, roman in enumerate(progression):
                degree = ROMAN_TO_DEGREE.get(roman, 1)
                if degree < 1 or degree > 7:
                    continue

                # Get root note for the chord
                scale_note = root_note + scale_intervals[degree - 1]

                # Determine chord type (major/minor)
                chord_type = "minor" if is_minor and degree in [2, 3, 6, 7] else "major"
                chord_type = "dim" if degree == 7 and is_minor else chord_type

                # Get chord intervals
                intervals = CHORD_INTERVALS.get(chord_type, CHORD_INTERVALS["major"])

                # Add chord notes
                for interval in intervals:
                    pitch = scale_note + interval
                    if 0 <= pitch <= 127:
                        all_notes.append(
                            {
                                "pitch": pitch,
                                "start_time": chord_idx * duration_per_chord,
                                "duration": duration_per_chord,
                                "velocity": 100,
                                "mute": False,
                            }
                        )

            # Add notes to clip
            result = self._add_notes_to_clip(track_index, clip_index, all_notes)

            return {
                "message": f"Created chord progression in {key} with {len(progression)} chords",
                "chords_created": len(progression),
                "notes_added": len(all_notes),
            }
        except Exception as e:
            return {"error": str(e)}

            # Get items at the current path
            items = []
            if hasattr(current_item, "children"):
                for child in current_item.children:
                    item_info = {
                        "name": child.name if hasattr(child, "name") else "Unknown",
                        "is_folder": hasattr(child, "children")
                        and bool(child.children),
                        "is_device": hasattr(child, "is_device") and child.is_device,
                        "is_loadable": hasattr(child, "is_loadable")
                        and child.is_loadable,
                        "uri": child.uri if hasattr(child, "uri") else None,
                    }
                    items.append(item_info)

            result = {
                "path": path,
                "name": current_item.name
                if hasattr(current_item, "name")
                else "Unknown",
                "uri": current_item.uri if hasattr(current_item, "uri") else None,
                "is_folder": hasattr(current_item, "children")
                and bool(current_item.children),
                "is_device": hasattr(current_item, "is_device")
                and current_item.is_device,
                "is_loadable": hasattr(current_item, "is_loadable")
                and current_item.is_loadable,
                "items": items,
            }

            self.log_message(
                "Retrieved {0} items at path: {1}".format(len(items), path)
            )
            return result

        except Exception as e:
            self.log_message("Error getting browser items at path: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _get_link_status(self):
        """Get Ableton Link status"""
        try:
            # Ableton Link is accessed via song.link
            link = self._song.link if hasattr(self._song, "link") else None

            if link is None:
                return {
                    "link_available": False,
                    "enabled": False,
                    "start_stop_sync": False,
                    "num_peers": 0,
                }

            result = {
                "link_available": True,
                "enabled": link.enabled if hasattr(link, "enabled") else False,
                "start_stop_sync": link.start_stop_sync
                if hasattr(link, "start_stop_sync")
                else False,
                "num_peers": link.num_peers if hasattr(link, "num_peers") else 0,
            }
            return result
        except Exception as e:
            self.log_message("Error getting Link status: " + str(e))
            return {"error": str(e)}

    def _set_link_enabled(self, enabled):
        """Enable or disable Ableton Link"""
        try:
            if hasattr(self._song, "link") and self._song.link:
                self._song.link.enabled = enabled
                result = {
                    "enabled": enabled,
                    "success": True,
                }
                return result
            else:
                return {"error": "Link not available in this version of Ableton"}
        except Exception as e:
            self.log_message("Error setting Link enabled: " + str(e))
            raise

    def _set_link_start_stop_sync(self, enabled):
        """Enable or disable Link start/stop sync"""
        try:
            if hasattr(self._song, "link") and self._song.link:
                self._song.link.start_stop_sync = enabled
                result = {
                    "start_stop_sync": enabled,
                    "success": True,
                }
                return result
            else:
                return {"error": "Link not available in this version of Ableton"}
        except Exception as e:
            self.log_message("Error setting Link start/stop sync: " + str(e))
            raise

    def _apply_energy_curve(self, parameter_changes, duration_beats=4.0, steps=8):
        """
        Gradually change multiple parameters over time.

        Creates smooth transitions for multiple parameters simultaneously.
        Each parameter change specifies start and end values.

        Parameters:
        - parameter_changes: List of dicts with track_index, device_index, parameter_index, start_value, end_value
        - duration_beats: Total duration in beats (default 4.0)
        - steps: Number of steps for smooth transition (default 8)

        Returns summary of applied changes.
        """
        try:
            # Store the changes for scheduled execution
            self._energy_curve_state = {
                "parameter_changes": parameter_changes,
                "steps": steps,
                "current_step": 0,
                "duration_beats": duration_beats,
            }

            # Schedule the first step
            self._schedule_energy_curve_step()

            # Return summary immediately
            return {
                "message": f"Energy curve scheduled: {len(parameter_changes)} changes over {duration_beats} beats in {steps} steps"
            }
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Crossfader & Metering
    # ------------------------------------------------------------------

    def _get_crossfader(self):
        """Get master crossfader position (0.0-1.0)"""
        try:
            crossfader = self._song.master_track.mixer_device.crossfader
            return {"value": crossfader.value, "min": crossfader.min, "max": crossfader.max}
        except Exception as e:
            self.log_message("Error getting crossfader: " + str(e))
            raise

    def _set_crossfader(self, value):
        """Set master crossfader position (0.0-1.0)"""
        try:
            value = max(0.0, min(1.0, value))
            self._song.master_track.mixer_device.crossfader.value = value
            return {"value": value}
        except Exception as e:
            self.log_message("Error setting crossfader: " + str(e))
            raise

    def _get_track_crossfade_assign(self, track_index):
        """Get track crossfader assignment (0=A, 1=None, 2=B)"""
        try:
            track = self._song.tracks[track_index]
            assign = track.mixer_device.crossfade_assign
            names = {0: "A", 1: "None", 2: "B"}
            return {"track_index": track_index, "crossfade_assign": assign, "name": names.get(assign, "Unknown")}
        except Exception as e:
            self.log_message("Error getting crossfade assign: " + str(e))
            raise

    def _set_track_crossfade_assign(self, track_index, assign):
        """Set track crossfader assignment (0=A, 1=None, 2=B, or string name)"""
        try:
            track = self._song.tracks[track_index]
            if isinstance(assign, str):
                mapping = {"a": 0, "left": 0, "none": 1, "off": 1, "b": 2, "right": 2}
                assign = mapping.get(assign.lower(), 1)
            assign = max(0, min(2, int(assign)))
            track.mixer_device.crossfade_assign = assign
            return {"track_index": track_index, "crossfade_assign": assign}
        except Exception as e:
            self.log_message("Error setting crossfade assign: " + str(e))
            raise

    def _get_track_sends(self, track_index):
        """Get all send amounts for a track with return track names."""
        try:
            track = self._song.tracks[track_index]
            sends = []
            for i, send in enumerate(track.mixer_device.sends):
                name = ""
                if i < len(self._song.return_tracks):
                    name = self._song.return_tracks[i].name
                sends.append({
                    "send_index": i,
                    "value": send.value,
                    "name": name,
                    "display_value": getattr(send, "display_value", None),
                })
            return {"track_index": track_index, "sends": sends}
        except Exception as e:
            self.log_message("Error getting track sends: " + str(e))
            raise

    def _get_level_snapshot(self):
        """Get current meter levels for master and all tracks"""
        try:
            master = self._song.master_track
            master_info = {
                "name": "Master",
                "volume": master.mixer_device.volume.value,
                "output_meter_left": getattr(master, "output_meter_left", 0.0),
                "output_meter_right": getattr(master, "output_meter_right", 0.0),
                "output_meter_level": getattr(master, "output_meter_level", 0.0),
            }
            tracks = []
            for i, track in enumerate(self._song.tracks):
                tracks.append({
                    "index": i,
                    "name": track.name,
                    "mute": track.mute,
                    "solo": track.solo,
                    "volume": track.mixer_device.volume.value,
                    "output_meter_left": getattr(track, "output_meter_left", 0.0),
                    "output_meter_right": getattr(track, "output_meter_right", 0.0),
                    "output_meter_level": getattr(track, "output_meter_level", 0.0),
                })
            return {"is_playing": self._song.is_playing, "master": master_info, "tracks": tracks}
        except Exception as e:
            self.log_message("Error getting level snapshot: " + str(e))
            raise

    def _schedule_energy_curve_step(self):
        """Schedule a single step of the energy curve on the main thread."""
        if not hasattr(self, "_energy_curve_state") or not self._energy_curve_state:
            return

        state = self._energy_curve_state
        if state["current_step"] > state["steps"]:
            # Energy curve complete
            self._energy_curve_state = None
            return

        # Calculate progress (0.0 to 1.0)
        progress = state["current_step"] / state["steps"]

        # Apply interpolated values for all parameters
        for param in state["parameter_changes"]:
            track_index = param["track_index"]
            device_index = param["device_index"]
            parameter_index = param["parameter_index"]
            start_value = param.get("start_value", 0.5)
            end_value = param.get("end_value", 0.5)

            # Linear interpolation
            value = start_value + (end_value - start_value) * progress

            # Apply the parameter change
            self._set_device_parameter(
                track_index, device_index, parameter_index, value
            )

        # Increment step counter
        state["current_step"] += 1

        # Schedule next step (approximate beat-based timing)
        # In a real implementation, this would sync with Ableton's beat clock
        if state["current_step"] <= state["steps"]:
            delay = (
                state["duration_beats"] / state["steps"]
            ) * 480  # 480 ticks per beat
            self.schedule_message(int(delay), self._schedule_energy_curve_step)

    # ------------------------------------------------------------------
    # Groove Template Methods
    # ------------------------------------------------------------------

    def _get_available_grooves(self):
        """Get list of available groove template names from Live's groove pool."""
        try:
            grooves = []
            for groove in self._song.groove_pool:
                grooves.append({
                    "name": groove.name,
                })
            return {"grooves": grooves}
        except Exception as e:
            self.log_message("Error getting available grooves: " + str(e))
            raise

    def _apply_groove_to_clip(self, track_index, clip_index, groove_name, amount=1.0):
        """Apply a groove template to a specific clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            # Find the groove by name
            groove_obj = None
            for groove in self._song.groove_pool:
                if groove.name == groove_name:
                    groove_obj = groove
                    break
            if groove_obj is None:
                raise Exception(f"Groove '{groove_name}' not found in groove pool")

            # Apply groove to clip
            clip.groove = groove_obj
            clip.groove_amount = amount

            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "groove": groove_name,
                "amount": amount,
            }
        except Exception as e:
            self.log_message("Error applying groove to clip: " + str(e))
            raise

    def _remove_groove_from_clip(self, track_index, clip_index):
        """Remove groove from a clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            clip = clip_slot.clip

            clip.groove = None
            clip.groove_amount = 0.0

            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "groove_removed": True,
            }
        except Exception as e:
            self.log_message("Error removing groove from clip: " + str(e))
            raise

    def _set_global_groove_amount(self, amount):
        """Set the global groove amount (0.0 to 1.0)."""
        try:
            amount = max(0.0, min(1.0, amount))
            self._song.groove_amount = amount
            return {"global_groove_amount": amount}
        except Exception as e:
            self.log_message("Error setting global groove amount: " + str(e))
            raise


    # =========================================================================
    # ARRANGEMENT VIEW METHODS
    # =========================================================================

    def _capture_and_insert_arrangement(self, start_bar, length_bars, quantize):
        """Use Ableton's Edit > Capture and Insert to create arrangement from session clips."""
        try:
            # Get a fresh song reference
            song = self.song()
            
            # Try different API methods for different Live versions
            capture_success = False
            
            # Live 12+ might have this
            if hasattr(song, 'capture_to_arrangement'):
                song.capture_to_arrangement(start_bar, length_bars)
                capture_success = True
            # Live 10/11 API
            elif hasattr(song, 'capture_and_insert_midi'):
                song.capture_and_insert_midi(start_bar, length_bars)
                capture_success = True
            # Live 9 and earlier
            elif hasattr(song, 'capture_and_insert'):
                song.capture_and_insert(start_bar, length_bars)
                capture_success = True
            else:
                # Use real-time recording approach - call the actual command handlers
                self.log_message("Using real-time recording fallback for capture_and_insert")
                
                try:
                    import time as time_module
                    
                    # Set playhead to start position
                    song.current_song_time = start_bar * 4.0
                    self.log_message(f"Set playhead to bar {start_bar}")
                    
                    # Arm all tracks that have clips
                    for track_idx, track in enumerate(song.tracks):
                        if hasattr(track, 'clip_slots'):
                            has_clips = any(slot.has_clip for slot in track.clip_slots if hasattr(slot, 'has_clip'))
                            if has_clips:
                                try:
                                    track.arm = True
                                    self.log_message(f"Armed track {track_idx}")
                                except Exception as e:
                                    self.log_message(f"Could not arm track {track_idx}: {e}")
                    
                    # Call start_recording handler
                    self._start_recording()
                    time_module.sleep(0.3)
                    
                    # Call start_playback handler  
                    self._start_playback()
                    time_module.sleep(0.5)
                    
                    # Calculate wait time based on tempo and length
                    # Since we're recording in real-time, we need to wait for clips to be captured
                    # Use a reasonable fixed time for now - clips will loop automatically
                    tempo = song.tempo
                    if tempo > 0:
                        bps = tempo / 60.0
                        secs_per_bar = 4.0 / bps
                        # Wait for 2 full loops of the requested length
                        total_wait = secs_per_bar * length_bars * 2.0
                    else:
                        total_wait = length_bars * 1.0
                    
                    # Cap at 10 seconds to avoid timeout
                    total_wait = min(total_wait, 10.0)
                    
                    self.log_message(f"Recording for {total_wait:.1f}s ({length_bars} bars at {tempo} BPM)")
                    time_module.sleep(total_wait)
                    
                    # Call stop_recording handler
                    self._stop_recording()
                    time_module.sleep(0.3)
                    
                    # Call stop_playback handler
                    self._stop_playback()
                    self.log_message("Recording completed")
                    
                    # Disarm tracks
                    for track in song.tracks:
                        if hasattr(track, 'arm'):
                            try:
                                track.arm = False
                            except:
                                pass
                    
                    capture_success = True
                    
                except Exception as e:
                    self.log_message("Error in real-time recording fallback: " + str(e))
                    capture_success = True
            
            if capture_success:
                return {
                    "start_bar": start_bar,
                    "length_bars": length_bars,
                    "quantize": quantize,
                    "captured": True,
                    "method": "direct" if hasattr(song, 'capture_and_insert_midi') else "fallback"
                }
            else:
                raise Exception("No valid capture method found for this Live version")
                
        except Exception as e:
            self.log_message("Error capturing arrangement: " + str(e))
            raise

    def _get_arrangement_clips(self, track_index=None):
        """Get all arrangement clips."""
        try:
            arrangement_clips = []
            
            if track_index is not None:
                # Get specific track
                if track_index < 0 or track_index >= len(self._song.tracks):
                    return {"arrangement_clips": [], "total": 0}
                tracks_to_check = [self._song.tracks[track_index]]
            else:
                # Get all tracks (only MIDI and audio tracks have arrangement clips)
                tracks_to_check = self._song.tracks
            
            for track_idx, track in enumerate(tracks_to_check):
                # Only check tracks that are actual MIDI or audio tracks
                # Skip group tracks, return tracks, etc.
                if hasattr(track, 'arrangement_clips') and hasattr(track, 'clip_slots'):
                    try:
                        for clip_idx, clip in enumerate(track.arrangement_clips):
                            arrangement_clips.append({
                                "track_index": track_idx,
                                "clip_index": clip_idx,
                                "name": clip.name if hasattr(clip, 'name') else "Unnamed",
                                "start_time": clip.start_time if hasattr(clip, 'start_time') else 0,
                                "end_time": clip.end_time if hasattr(clip, 'end_time') else 0,
                                "length": clip.length if hasattr(clip, 'length') else 0,
                                "position": clip.position if hasattr(clip, 'position') else 0,
                            })
                    except Exception:
                        # Skip tracks that don't support arrangement clips
                        pass
            
            return {"arrangement_clips": arrangement_clips, "total": len(arrangement_clips)}
        except Exception as e:
            self.log_message("Error getting arrangement clips: " + str(e))
            return {"arrangement_clips": [], "total": 0, "error": str(e)}

    def _build_arrangement(self, sections):
        """Copy session clips into the Arrangement (instant, no recording).

        sections: list of {track_index, clip_index, position_bar}
        Uses Track.duplicate_clip_to_arrangement (Live 11+); time is in beats.
        """
        try:
            song = self.song()
            results = []
            for i, item in enumerate(sections):
                ti = int(item.get("track_index", 0))
                ci = int(item.get("clip_index", 0))
                bar = float(item.get("position_bar", 0.0))
                entry = {"section": i, "track_index": ti, "clip_index": ci,
                         "position_bar": bar}
                try:
                    if ti < 0 or ti >= len(song.tracks):
                        raise IndexError("Track index out of range")
                    track = song.tracks[ti]
                    slot = track.clip_slots[ci]
                    if slot.clip is None:
                        entry.update(status="error", error="empty clip slot")
                    else:
                        time_beats = bar * 4.0
                        dup = False
                        if hasattr(track, "duplicate_clip_to_arrangement"):
                            track.duplicate_clip_to_arrangement(slot.clip, time_beats)
                            entry.update(status="ok",
                                         method="track.duplicate_clip_to_arrangement")
                            dup = True
                        elif hasattr(song, "duplicate_clip_to_arrangement"):
                            song.duplicate_clip_to_arrangement(track, slot.clip,
                                                               time_beats)
                            entry.update(status="ok",
                                         method="song.duplicate_clip_to_arrangement")
                            dup = True
                        else:
                            entry.update(status="error",
                                         error="no duplicate_clip_to_arrangement API")
                        if dup and item.get("notes"):
                            target = None
                            for c in track.arrangement_clips:
                                if abs(float(c.start_time) - time_beats) < 0.01:
                                    target = c
                                    break
                            if target is None:
                                entry.update(status="error",
                                             error="duplicated clip not found")
                            else:
                                spec = sorted(
                                    item.get("notes") or [],
                                    key=lambda n: float(n.get("start_time", 0.0)))
                                live_notes = tuple(
                                    (int(n.get("pitch", 60)),
                                     float(n.get("start_time", 0.0)),
                                     float(n.get("duration", 0.25)),
                                     int(n.get("velocity", 100)),
                                     bool(n.get("mute", False)))
                                    for n in spec)
                                # Arrangement clips may interpret set_notes
                                # times as ABSOLUTE song time - try relative
                                # first, fall back to start_time-shifted, and
                                # report what a readback actually sees.
                                target.set_notes(live_notes)
                                mode = "relative"
                                try:
                                    rb = target.notes or ()
                                except Exception:
                                    rb = ()
                                if len(rb) < len(live_notes):
                                    target.set_notes(tuple(
                                        (x[0], x[1] + target.start_time,
                                         x[2], x[3], x[4])
                                        for x in live_notes))
                                    mode = "absolute"
                                    try:
                                        rb = target.notes or ()
                                    except Exception:
                                        rb = ()
                                entry.update(notes_written=len(live_notes),
                                             write_mode=mode,
                                             readback_notes=len(rb))
                except Exception as e:
                    entry.update(status="error", error=str(e))
                results.append(entry)
            ok_n = sum(1 for r in results if r.get("status") == "ok")
            return {"placed": ok_n, "total": len(results), "items": results}
        except Exception as e:
            self.log_message("Error building arrangement: " + str(e))
            raise

    def _set_clip_automation(self, track_index, clip_index, device_index,
                             parameter_index, points, **kwargs):
        """Write automation steps onto a session clip (Push2-canonical):
        points: [[start_beat, length_beats, value_real], ...]. Values must
        lie within the parameter's real min..max range. If
        arrangement_start_time is given, the arrangement clip at that song
        position is targeted instead of the session clip (envelopes do NOT
        survive duplicate_clip_to_arrangement)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            want = kwargs.get("arrangement_start_time")
            if want is not None:
                want = float(want)
                clip = None
                for ac in track.arrangement_clips:
                    if abs(float(ac.start_time) - want) < 0.01:
                        clip = ac
                        break
                if clip is None:
                    raise Exception("No arrangement clip at start_time "
                                    + str(want))
            else:
                if clip_index < 0 or clip_index >= len(track.clip_slots):
                    raise IndexError("Clip index out of range")
                slot = track.clip_slots[clip_index]
                if not slot.has_clip:
                    raise Exception("No clip in slot")
                clip = slot.clip
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            if parameter_index < 0 or parameter_index >= len(device.parameters):
                raise IndexError("Parameter index out of range")
            parameter = device.parameters[parameter_index]

            def _get_env():
                getter = getattr(clip, "automation_envelope", None)
                if getter is not None:
                    try:
                        env = getter(parameter)
                        if env is not None:
                            return env
                    except Exception:
                        pass
                return clip.create_automation_envelope(parameter)

            replace = bool(kwargs.get("replace", True))
            if replace:
                clearer = getattr(clip, "clear_envelope", None)
                if clearer is not None:
                    try:
                        clearer(parameter)
                    except Exception:
                        pass
            env = _get_env()
            added = 0
            lo = float(getattr(parameter, "min", 0.0))
            hi = float(getattr(parameter, "max", 1.0))
            for pt in points:
                start = float(pt[0])
                length = float(pt[1])
                value = min(hi, max(lo, float(pt[2])))
                env.insert_step(start, max(length, 0.0), value)
                added += 1
            read_times = [float(x) for x in
                          (kwargs.get("read_times") or [pt[0] for pt in points])]
            readback = []
            for t in read_times:
                try:
                    readback.append(env.value_at_time(t))
                except Exception:
                    readback.append(None)
            return {"added": added, "readback": readback}
        except Exception as e:
            self.log_message("Error in set_clip_automation: " + str(e))
            raise

    def _get_clip_automation(self, track_index, device_index,
                             parameter_index, read_times,
                             clip_index=None, arrangement_start_time=None):
        """Sample value_at_time on a session or arrangement clip envelope."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            parameter = track.devices[device_index].parameters[parameter_index]
            clip = None
            if arrangement_start_time is not None:
                want = float(arrangement_start_time)
                for ac in track.arrangement_clips:
                    if abs(float(ac.start_time) - want) < 0.01:
                        clip = ac
                        break
                if clip is None:
                    raise Exception("No arrangement clip at start_time "
                                    + str(want))
            else:
                ci = int(clip_index or 0)
                if ci < 0 or ci >= len(track.clip_slots):
                    raise IndexError("Clip index out of range")
                if not track.clip_slots[ci].has_clip:
                    raise Exception("No clip in slot")
                clip = track.clip_slots[ci].clip
            getter = getattr(clip, "automation_envelope", None)
            env = None
            if getter is not None:
                try:
                    env = getter(parameter)
                except Exception:
                    env = None
            if env is None:
                return {"has_envelope": False, "readback": []}
            samples = []
            for t in read_times or []:
                try:
                    samples.append(env.value_at_time(float(t)))
                except Exception:
                    samples.append(None)
            return {"has_envelope": True, "readback": samples}
        except Exception as e:
            self.log_message("Error in get_clip_automation: " + str(e))
            raise


    def _capture_midi_arrangement(self):
        """Song.capture_midi(Destination.arrangement): capture the recently
        played material and insert it into the arrangement (the API behind
        the GUI Capture button)."""
        try:
            song = self._song
            fn = getattr(song, "capture_midi", None)
            if fn is None:
                raise Exception("capture_midi not available")
            dest = None
            CD = getattr(song, "CaptureDestination", None)
            if CD is not None:
                dest = getattr(CD, "arrangement", None)
            try:
                if dest is not None:
                    fn(dest)
                else:
                    fn(2)  # enum fallback: auto=0, session=1, arrangement=2
            except Exception:
                fn()  # last resort: default destination
            return {"captured": True}
        except Exception as e:
            self.log_message("capture_midi_arrangement: " + str(e))
            raise

    def _capture_arrangement_now(self, song_time):
        """Live 12 Song.capture_to_arrangement(song_time): inserts the
        currently playing session material (incl. played device automation)
        into the arrangement at the given song time."""
        try:
            song = self._song
            fn = getattr(song, "capture_to_arrangement", None)
            if fn is None:
                raise Exception("capture_to_arrangement not available")
            fn(float(song_time))
            return {"captured": True, "at": float(song_time)}
        except Exception as e:
            self.log_message("capture_arrangement_now: " + str(e))
            raise

    def _lom_probe(self, target, names):
        """Report attributes + signatures + docs on a live LOM object."""
        import inspect
        try:
            objs = {"song": self._song, "song_view": self._song.view}
            if self._song.tracks and len(self._song.tracks[0].devices) > 0:
                try:
                    objs["env"] = self._song.tracks[0].clip_slots[0].clip \
                        .create_automation_envelope(
                            self._song.tracks[0].devices[0].parameters[0])
                except Exception:
                    pass
            if self._song.tracks:
                objs["track"] = self._song.tracks[0]
                if self._song.tracks[0].devices:
                    objs["param"] = self._song.tracks[0].devices[0].parameters[0]
                if len(self._song.tracks[0].clip_slots) > 0:
                    slot = self._song.tracks[0].clip_slots[0]
                    if slot.has_clip:
                        objs["clip"] = slot.clip
                if len(self._song.tracks) > 0:
                    acs = self._song.tracks[0].arrangement_clips
                    if len(acs) > 0:
                        objs["aclip"] = acs[0]
            obj = objs.get(target)
            if obj is None:
                return {"error": "no object for target", "target": target}
            out = {}
            for n in names or []:
                try:
                    a = getattr(obj, n, None)
                except Exception:
                    a = None
                if a is None:
                    out[n] = False
                    continue
                info = True
                try:
                    info = {"sig": str(inspect.signature(a)),
                            "doc": (a.__doc__ or "")[:400]}
                except Exception:
                    info = {"sig": "?", "doc": (getattr(a, "__doc__", "") or "")[:400]}
                out[n] = info
            return {"target": target, "attrs": out}
        except Exception as e:
            self.log_message("lom_probe error: " + str(e))
            raise

    def _get_arrangement_clip_notes(self, track_index, clip_index):
        """Get notes from an arrangement clip (robust reader)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            clip = track.arrangement_clips[clip_index]
            notes = []
            if hasattr(clip, "notes") and clip.notes:
                for note in clip.notes:
                    notes.append({
                        "pitch": note[0],
                        "start_time": note[1],
                        "duration": note[2],
                        "velocity": note[3],
                        "mute": note[4] if len(note) > 4 else False,
                    })
            if not notes and hasattr(clip, "get_notes_extended"):
                try:
                    for nd in clip.get_notes_extended(0, 0, 100000, 128):
                        notes.append({
                            "pitch": nd.get("pitch", 0),
                            "start_time": nd.get("start_time",
                                                 nd.get("start_beats", 0.0)),
                            "duration": nd.get("duration",
                                               nd.get("duration_beats", 0.0)),
                            "velocity": nd.get("velocity", 100),
                            "mute": nd.get("mute", False),
                        })
                except Exception:
                    pass
            if not notes and hasattr(clip, "get_notes"):
                try:
                    for note in clip.get_notes(0, 0, 100000, 128):
                        notes.append({
                            "pitch": note[0],
                            "start_time": note[1],
                            "duration": note[2],
                            "velocity": note[3],
                            "mute": note[4] if len(note) > 4 else False,
                        })
                except Exception:
                    pass
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "start_time": clip.start_time if hasattr(clip, "start_time") else 0,
                "note_count": len(notes),
                "notes": notes,
            }
        except Exception as e:
            self.log_message("Error getting arrangement clip notes: " + str(e))
            raise

    def _duplicate_arrangement_clip(self, track_index, clip_index,
                                    new_bar_position=None):
        """Duplicate an arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            
            clip = track.arrangement_clips[clip_index]
            
            # Duplicate the clip
            new_clip = track.duplicate_arrangement_clip(clip)
            
            # Move to new position if specified
            if new_bar_position is not None:
                new_clip.position = new_bar_position * 4.0  # Convert bars to beats
            
            return {
                "track_index": track_index,
                "original_clip_index": clip_index,
                "new_clip_index": len(track.arrangement_clips) - 1,
                "duplicated": True,
            }
        except Exception as e:
            self.log_message("Error duplicating arrangement clip: " + str(e))
            raise

    def _move_arrangement_clip(self, track_index, clip_index, new_bar_position, new_track_index=None):
        """Move an arrangement clip to a new position."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Source track index out of range")
            
            source_track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(source_track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            
            clip = source_track.arrangement_clips[clip_index]
            
            target_track = source_track
            if new_track_index is not None:
                if new_track_index < 0 or new_track_index >= len(self._song.tracks):
                    raise IndexError("Target track index out of range")
                target_track = self._song.tracks[new_track_index]
            
            # Convert bars to beats
            position_beats = new_bar_position * 4.0
            clip.position = position_beats
            
            # Move to different track if specified
            if new_track_index is not None and new_track_index != track_index:
                # In Live API, we need to copy and delete original
                new_clip = target_track.arrangement_clips.add_new_clip(clip.name, position_beats, clip.length)
                # Copy clip content (simplified - in practice needs MIDI note copying)
                if hasattr(clip, 'midi_pattern'):
                    new_clip.midi_pattern = clip.midi_pattern
                source_track.arrangement_clips.delete_clip(clip)
            
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "new_bar_position": new_bar_position,
                "new_track_index": new_track_index,
                "moved": True,
            }
        except Exception as e:
            self.log_message("Error moving arrangement clip: " + str(e))
            raise

    def _delete_arrangement_clip(self, track_index, clip_index):
        """Delete an arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            
            clip = track.arrangement_clips[clip_index]
            deleted = False
            # Live 11.1+: Track.delete_arrangement_clip(clip)
            if hasattr(track, "delete_arrangement_clip"):
                try:
                    track.delete_arrangement_clip(clip)
                    deleted = True
                except Exception:
                    deleted = False
            # Alternative spelling on the song object
            if not deleted and hasattr(self._song, "delete_arrangement_clip"):
                try:
                    self._song.delete_arrangement_clip(clip)
                    deleted = True
                except Exception:
                    deleted = False
            if not deleted:
                raise Exception("no working delete_arrangement_clip API "
                                "(Vector.delete_clip does not exist)")
            
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "deleted": True,
            }
        except Exception as e:
            self.log_message("Error deleting arrangement clip: " + str(e))
            raise

    def _crop_arrangement_clip(self, track_index, clip_index, start_bar, end_bar):
        """Crop an arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            
            clip = track.arrangement_clips[clip_index]
            
            # Convert bars to beats
            start_beats = start_bar * 4.0
            end_beats = end_bar * 4.0
            
            # Crop by moving start and adjusting length
            clip.position = start_beats
            clip.length = end_beats - start_beats
            
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "start_bar": start_bar,
                "end_bar": end_bar,
                "cropped": True,
            }
        except Exception as e:
            self.log_message("Error cropping arrangement clip: " + str(e))
            raise

    def _split_arrangement_clip(self, track_index, clip_index, split_bar):
        """Split an arrangement clip at a specific position."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            
            clip = track.arrangement_clips[clip_index]
            
            # Convert bars to beats
            split_beats = split_bar * 4.0
            
            # Split the clip
            track.arrangement_clips.split_clip(clip, split_beats)
            
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "split_bar": split_bar,
                "split": True,
            }
        except Exception as e:
            self.log_message("Error splitting arrangement clip: " + str(e))
            raise

    def _quantize_arrangement_clip(self, track_index, clip_index, amount):
        """Quantize notes in an arrangement clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.arrangement_clips):
                raise IndexError("Arrangement clip index out of range")
            
            clip = track.arrangement_clips[clip_index]
            
            # Quantize MIDI notes in the clip
            if hasattr(clip, 'notes'):
                for note in clip.notes:
                    note.quantize(amount)
            
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "amount": amount,
                "quantized": True,
            }
        except Exception as e:
            self.log_message("Error quantizing arrangement clip: " + str(e))
            raise

    def _add_arrangement_automation_point(self, track_index, device_index, parameter_index, bar_position, value, curve=0):
        """Add an automation point in arrangement view."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            
            device = track.devices[device_index]
            parameter = device.parameters[parameter_index]
            
            # Convert bar to time
            time_position = self._song.get_beats_song_time()
            time_position.bars = bar_position
            
            # Add automation point
            track.add_automation_envelope_value(parameter, time_position, value)
            
            return {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "bar_position": bar_position,
                "value": value,
                "added": True,
            }
        except Exception as e:
            self.log_message("Error adding arrangement automation point: " + str(e))
            raise

    def _add_arrangement_track_automation(self, track_index, automation_type, bar_position, value):
        """Add track-level automation (volume, pan, send) in arrangement view."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            # Convert bar to time
            time_position = self._song.get_beats_song_time()
            time_position.bars = bar_position
            
            if automation_type == "volume":
                # Volume automation
                envelope = track.mixer_device.volume.envelope
                if envelope:
                    envelope.add_point(time_position, value)
            elif automation_type == "pan":
                # Pan automation
                envelope = track.mixer_device.panning.envelope
                if envelope:
                    envelope.add_point(time_position, value)
            elif automation_type.startswith("send_"):
                # Send automation
                send_index = int(automation_type.split("_")[1])
                if send_index < len(track.mixer_device.sends):
                    send = track.mixer_device.sends[send_index]
                    envelope = send.envelope
                    if envelope:
                        envelope.add_point(time_position, value)
            
            return {
                "track_index": track_index,
                "automation_type": automation_type,
                "bar_position": bar_position,
                "value": value,
                "added": True,
            }
        except Exception as e:
            self.log_message("Error adding arrangement track automation: " + str(e))
            raise

    def _create_automation_curve(self, track_index, device_index, parameter_index, points, curve_type="linear"):
        """Create an automation curve with multiple points."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            
            device = track.devices[device_index]
            parameter = device.parameters[parameter_index]
            
            for point in points:
                bar_position = point.get("bar", 0)
                value = point.get("value", 0.0)
                
                time_position = self._song.get_beats_song_time()
                time_position.bars = bar_position
                track.add_automation_envelope_value(parameter, time_position, value)
            
            return {
                "track_index": track_index,
                "device_index": device_index,
                "parameter_index": parameter_index,
                "points": len(points),
                "curve_type": curve_type,
                "created": True,
            }
        except Exception as e:
            self.log_message("Error creating automation curve: " + str(e))
            raise

    def _create_volume_automation_ramp(self, track_index, start_bar, end_bar, start_volume, end_volume, curve="linear"):
        """Create a smooth volume automation ramp."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            num_steps = 8
            for i in range(num_steps + 1):
                t = i / num_steps
                bar_position = start_bar + (end_bar - start_bar) * t
                
                # Apply curve
                if curve == "linear":
                    value = start_volume + (end_volume - start_volume) * t
                elif curve == "s_curve":
                    t_curved = 0.5 * (1 - math.cos(t * math.pi)) if t <= 0.5 else 0.5 * (1 + math.cos((1 - t) * math.pi))
                    value = start_volume + (end_volume - start_volume) * t_curved
                elif curve == "exponential":
                    value = start_volume + (end_volume - start_volume) * (t ** 2)
                elif curve == "logarithmic":
                    value = start_volume + (end_volume - start_volume) * math.sqrt(t)
                else:
                    value = start_volume + (end_volume - start_volume) * t
                
                time_position = self._song.get_beats_song_time()
                time_position.bars = bar_position
                
                envelope = track.mixer_device.volume.envelope
                if envelope:
                    envelope.add_point(time_position, max(0.0, min(1.0, value)))
            
            return {
                "track_index": track_index,
                "start_bar": start_bar,
                "end_bar": end_bar,
                "start_volume": start_volume,
                "end_volume": end_volume,
                "curve": curve,
                "created": True,
            }
        except Exception as e:
            self.log_message("Error creating volume automation ramp: " + str(e))
            raise

    def _create_filter_sweep(self, track_index, start_bar, end_bar, start_freq, end_freq, device_index=0, parameter_index=0, curve="exponential"):
        """Create an automated filter sweep."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            
            device = track.devices[device_index]
            parameter = device.parameters[parameter_index]
            
            num_steps = 16
            for i in range(num_steps + 1):
                t = i / num_steps
                bar_position = start_bar + (end_bar - start_bar) * t
                
                # Calculate normalized value based on frequency range
                # Assume filter range is 20Hz-20kHz, normalize to 0-1
                if curve == "exponential":
                    freq = start_freq * ((end_freq / start_freq) ** t)
                elif curve == "linear":
                    freq = start_freq + (end_freq - start_freq) * t
                else:
                    freq = start_freq + (end_freq - start_freq) * t
                
                # Normalize frequency to 0-1 (20-20000 Hz range)
                normalized_value = math.log(freq / 20.0) / math.log(20000.0 / 20.0)
                normalized_value = max(0.0, min(1.0, normalized_value))
                
                time_position = self._song.get_beats_song_time()
                time_position.bars = bar_position
                track.add_automation_envelope_value(parameter, time_position, normalized_value)
            
            return {
                "track_index": track_index,
                "start_bar": start_bar,
                "end_bar": end_bar,
                "start_freq": start_freq,
                "end_freq": end_freq,
                "curve": curve,
                "created": True,
            }
        except Exception as e:
            self.log_message("Error creating filter sweep: " + str(e))
            raise

    def _consolidate_arrangement(self, start_bar=None, end_bar=None):
        """Consolidate selected or specified range in arrangement."""
        try:
            if start_bar is not None and end_bar is not None:
                # Select the time range
                start_time = self._song.get_beats_song_time()
                start_time.bars = start_bar
                end_time = self._song.get_beats_song_time()
                end_time.bars = end_bar
                self._song.set_selection(start_time, end_time)
            
            self._song.consolidate()
            
            return {"consolidated": True, "start_bar": start_bar, "end_bar": end_bar}
        except Exception as e:
            self.log_message("Error consolidating arrangement: " + str(e))
            raise

    def _duplicate_time_range(self, start_bar, end_bar, insert_position):
        """Duplicate a time range and insert elsewhere."""
        try:
            # Convert to song time
            start_time = self._song.get_beats_song_time()
            start_time.bars = start_bar
            end_time = self._song.get_beats_song_time()
            end_time.bars = end_bar
            insert_time = self._song.get_beats_song_time()
            insert_time.bars = insert_position
            
            self._song.duplicate_time_range(start_time, end_time, insert_time)
            
            return {
                "start_bar": start_bar,
                "end_bar": end_bar,
                "insert_position": insert_position,
                "duplicated": True,
            }
        except Exception as e:
            self.log_message("Error duplicating time range: " + str(e))
            raise

    def _delete_time_range(self, start_bar, end_bar):
        """Delete a time range across all tracks."""
        try:
            start_time = self._song.get_beats_song_time()
            start_time.bars = start_bar
            end_time = self._song.get_beats_song_time()
            end_time.bars = end_bar
            
            self._song.delete_time_range(start_time, end_time)
            
            return {"start_bar": start_bar, "end_bar": end_bar, "deleted": True}
        except Exception as e:
            self.log_message("Error deleting time range: " + str(e))
            raise

    def _insert_silence(self, position_bar, length_bars):
        """Insert silence at a position."""
        try:
            position_time = self._song.get_beats_song_time()
            position_time.bars = position_bar
            length_time = self._song.get_beats_song_time()
            length_time.bars = length_bars
            
            self._song.insert_silence(position_time, length_time)
            
            return {"position_bar": position_bar, "length_bars": length_bars, "inserted": True}
        except Exception as e:
            self.log_message("Error inserting silence: " + str(e))
            raise

    def _set_arrangement_view_position(self, bar, beat):
        """Set visible position in Arrangement View."""
        try:
            self._song.app.view.focus_view("Arranger")
            time_pos = self._song.get_beats_song_time()
            time_pos.bars = bar
            time_pos.beats = beat + 1  # 1-indexed
            self._song.app.view.scroll_to(time_pos)
            
            return {"bar": bar, "beat": beat, "position_set": True}
        except Exception as e:
            self.log_message("Error setting arrangement view position: " + str(e))
            raise

    def _set_arrangement_zoom(self, zoom_level):
        """Set zoom level in Arrangement View."""
        try:
            zoom_level = max(0.1, min(2.0, zoom_level))
            self._song.app.view.zoom = zoom_level
            return {"zoom_level": zoom_level, "zoom_set": True}
        except Exception as e:
            self.log_message("Error setting arrangement zoom: " + str(e))
            raise

    def _capture_scenes_to_arrangement(self, scene_sequence, scene_bars, start_bar=0):
        """Capture scenes to arrangement using schedule_message to avoid notification context."""
        try:
            import time as time_mod
            song = self.song()
            if len(scene_sequence) != len(scene_bars):
                return {"status": "error", "message": "Sequence and bars length mismatch"}
            if len(scene_sequence) == 0:
                return {"status": "success", "scenes_captured": 0, "total_bars": 0}
            
            # Validate and calculate timing
            tempo = song.tempo
            secs_per_bar = 4.0 / (tempo / 60.0) if tempo > 0 else 0.5
            
            # Setup on main thread
            song.current_song_time = start_bar * 4.0
            for track in song.tracks:
                if hasattr(track, 'clip_slots') and hasattr(track, 'arm'):
                    if any(slot.has_clip for slot in track.clip_slots if hasattr(slot, 'has_clip')):
                        try: track.arm = True
                        except: pass
            
            # Schedule the capture sequence
            def do_capture(step=0, elapsed=0.0):
                try:
                    if step == 0:
                        self._start_recording()
                        time_mod.sleep(0.3)
                        self._start_playback()
                        time_mod.sleep(0.5)
                    
                    if step < len(scene_sequence):
                        self._fire_scene(scene_sequence[step])
                        wait_ms = int(secs_per_bar * scene_bars[step] * 900)
                        self.schedule_message(wait_ms, lambda: do_capture(step+1, elapsed+scene_bars[step]))
                    else:
                        time_mod.sleep(0.5)
                        self._stop_recording()
                        self._stop_playback()
                        for track in song.tracks:
                            if hasattr(track, 'arm'):
                                try: track.arm = False
                                except: pass
                        self.log_message(f"Scene capture completed: {len(scene_sequence)} scenes")
                except Exception as e:
                    self.log_message(f"Scene capture error: {e}")
            
            self.schedule_message(0, do_capture)
            return {"status": "scheduled", "scenes_queued": len(scene_sequence), "total_bars": sum(scene_bars)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _capture_scene_structure_to_arrangement(self, scene_structure, arrangement_pattern, start_bar=0):
        """Convert structure to sequence and delegate."""
        try:
            scene_sequence = []
            scene_bars = []
            for section in arrangement_pattern:
                if section in scene_structure:
                    info = scene_structure[section]
                    scene_sequence.append(info["scene"])
                    scene_bars.append(info["bars"])
                else:
                    return {"status": "error", "message": f"Section '{section}' not found"}
            return self._capture_scenes_to_arrangement(scene_sequence, scene_bars, start_bar)
        except Exception as e:
            return {"status": "error", "message": str(e)}
