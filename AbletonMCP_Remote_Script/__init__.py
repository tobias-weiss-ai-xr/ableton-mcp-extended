# AbletonMCP/init.py
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import socket
import json
import threading
import time
import traceback

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = "127.0.0.1"


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
        self.running = False

        # Cache the song reference for easier access
        self._song = self.song()

        # Start the socket server
        self.start_server()

        self.log_message("AbletonMCP initialized")

        # Show a message in Ableton
        self.show_message(
            "AbletonMCP: Listening for commands on port " + str(DEFAULT_PORT)
        )

    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP disconnecting...")
        self.running = False

        # Stop the server
        if self.server:
            try:
                self.server.close()
            except:
                pass

        # Wait for the server thread to exit
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(1.0)

        # Clean up any client threads
        for client_thread in self.client_threads[:]:
            if client_thread.is_alive():
                # We don't join them as they might be stuck
                self.log_message("Client thread still alive during disconnect")

        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP disconnected")

    def start_server(self):
        """Start the socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, DEFAULT_PORT))
            self.server.listen(5)  # Allow up to 5 pending connections

            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()

            self.log_message("Server started on port " + str(DEFAULT_PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonMCP: Error starting server - " + str(e))

    def _server_thread(self):
        """Server thread implementation - handles client connections"""
        try:
            self.log_message("Server thread started")
            # Set a timeout to allow regular checking of running flag
            self.server.settimeout(1.0)

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
                    time.sleep(0.5)

            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))

    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(None)  # No timeout for client socket
        buffer = ""  # Changed from b'' to '' for Python 2

        try:
            while self.running:
                try:
                    # Receive data
                    data = client.recv(8192)

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
                    except:
                        # If we can't send the error, the connection is probably dead
                        break

                    # For serious errors, break the loop
                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except:
                pass
            self.log_message("Client handler stopped")

    def _process_command(self, command):
        """Process a command from the client and return a response"""
        command_type = command.get("type", "")
        params = command.get("params", {})

        # Initialize response
        response = {"status": "success", "result": {}}

        try:
            # Route the command to the appropriate handler
            if command_type == "get_session_info":
                response["result"] = self._get_session_info()
            elif command_type == "get_track_info":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_info(track_index)
            # Commands that modify Live's state should be scheduled on the main thread
            elif command_type in [
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
                "set_clip_follow_action",
                "get_clip_follow_actions",
                "create_scene",
                "delete_scene",
                "duplicate_scene",
                "set_scene_name",
                "fire_scene",
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
                "load_browser_item",
                "get_device_parameters",
                "set_device_parameter",
                "add_automation_point",
                "clear_automation",
                "duplicate_device",
                "delete_device",
                "move_device",
                "toggle_device_bypass",
                "undo",
                "redo",
                "crop_clip",
                "resize_clip",
                "duplicate_clip_to",
                "undo",
                "redo",
                "get_playhead_position",
                "set_playhead_position",
                "create_locator",
                "delete_locator",
                "jump_to_locator",
                "set_loop",
                "get_clip_notes",
                "set_master_volume",
                "get_master_track_info",
                "get_return_tracks",
                "get_all_tracks",
                "get_all_scenes",
                "get_session_overview",
                "get_all_clips_in_track",
                "set_note_velocity",
                "set_note_duration",
                "set_note_pitch",
                "get_clip_envelopes",
                "mix_clip",
                "stretch_clip",
                "crop_clip",
                "duplicate_clip_to",
                "group_tracks",
                "ungroup_tracks",
                "set_clip_warp_mode",
                "get_clip_warp_markers",
                "add_warp_marker",
                "delete_warp_marker",
                "reload_script",
            ]:
                # Use a thread-safe approach with a response queue
                response_queue = queue.Queue()

                # Define a function to execute on the main thread
                def main_thread_task():
                    try:
                        result = None
                        if command_type == "create_midi_track":
                            index = params.get("index", -1)
                            result = self._create_midi_track(index)
                        elif command_type == "delete_all_tracks":
                            result = self._delete_all_tracks()
                        elif command_type == "set_track_name":
                            track_index = params.get("track_index", 0)
                            name = params.get("name", "")
                            result = self._set_track_name(track_index, name)
                        elif command_type == "create_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            length = params.get("length", 4.0)
                            result = self._create_clip(track_index, clip_index, length)
                        elif command_type == "add_notes_to_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            notes = params.get("notes", [])
                            result = self._add_notes_to_clip(
                                track_index, clip_index, notes
                            )
                        elif command_type == "set_clip_name":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            name = params.get("name", "")
                            result = self._set_clip_name(track_index, clip_index, name)
                        elif command_type == "set_tempo":
                            tempo = params.get("tempo", 120.0)
                            result = self._set_tempo(tempo)
                        elif command_type == "fire_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._fire_clip(track_index, clip_index)
                        elif command_type == "stop_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._stop_clip(track_index, clip_index)
                        elif command_type == "start_playback":
                            result = self._start_playback()
                        elif command_type == "stop_playback":
                            result = self._stop_playback()
                        elif command_type == "load_instrument_or_effect":
                            track_index = params.get("track_index", 0)
                            uri = params.get("uri", "")
                            result = self._load_instrument_or_effect(track_index, uri)
                        elif command_type == "load_browser_item":
                            track_index = params.get("track_index", 0)
                            item_uri = params.get("item_uri", "")
                            result = self._load_browser_item(track_index, item_uri)
                        elif command_type == "get_device_parameters":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            result = self._get_device_parameters(
                                track_index, device_index
                            )
                        elif command_type == "set_device_parameter":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            parameter_index = params.get("parameter_index", 0)
                            value = params.get("value", 0.0)
                            result = self._set_device_parameter(
                                track_index, device_index, parameter_index, value
                            )
                        elif command_type == "set_track_volume":
                            track_index = params.get("track_index", 0)
                            volume = params.get("volume", 0.75)
                            result = self._set_track_volume(track_index, volume)
                        elif command_type == "set_track_mute":
                            track_index = params.get("track_index", 0)
                            mute = params.get("mute", False)
                            result = self._set_track_mute(track_index, mute)
                        elif command_type == "set_track_solo":
                            track_index = params.get("track_index", 0)
                            solo = params.get("solo", False)
                            result = self._set_track_solo(track_index, solo)
                        elif command_type == "set_track_arm":
                            track_index = params.get("track_index", 0)
                            arm = params.get("arm", False)
                            result = self._set_track_arm(track_index, arm)
                        elif command_type == "load_instrument_preset":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            preset_name = params.get("preset_name", "")
                            result = self._load_instrument_preset(
                                track_index, device_index, preset_name
                            )
                        elif command_type == "toggle_device_bypass":
                            track_index = params.get("track_index", 0)
                            device_index = params.get("device_index", 0)
                            enabled = params.get("enabled", True)
                            result = self._toggle_device_bypass(
                                track_index, device_index, enabled
                            )
                        elif command_type == "undo":
                            result = self._undo()
                        elif command_type == "redo":
                            result = self._redo()
                        elif command_type == "get_playhead_position":
                            result = self._get_playhead_position()
                        elif command_type == "set_playhead_position":
                            bar = params.get("bar", 1)
                            beat = params.get("beat", 0.0)
                            result = self._set_playhead_position(bar, beat)
                        elif command_type == "create_locator":
                            bar = params.get("bar", 1)
                            name = params.get("name", "")
                            result = self._create_locator(bar, name)
                        elif command_type == "delete_locator":
                            locator_index = params.get("locator_index", 0)
                            result = self._delete_locator(locator_index)
                        elif command_type == "jump_to_locator":
                            locator_index = params.get("locator_index", 0)
                            result = self._jump_to_locator(locator_index)
                        elif command_type == "set_loop":
                            start_bar = params.get("start_bar", 1)
                            end_bar = params.get("end_bar", 17)
                            enabled = params.get("enabled", True)
                            result = self._set_loop(start_bar, end_bar, enabled)
                        elif command_type == "get_clip_notes":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            from_time = params.get("from_time", 0.0)
                            from_pitch = params.get("from_pitch", 0)
                            time_span = params.get("time_span", 999999.0)
                            pitch_span = params.get("pitch_span", 128)
                            result = self._get_clip_notes(
                                track_index,
                                clip_index,
                                from_time,
                                from_pitch,
                                time_span,
                                pitch_span,
                            )
                        elif command_type == "set_clip_follow_action":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            action_slot = params.get("action_slot", 0)
                            action_type = params.get("action_type", 0)
                            trigger_time = params.get("trigger_time", 0)
                            clip_index_target = params.get("clip_index_target", 0)
                            result = self._set_clip_follow_action(
                                track_index,
                                clip_index,
                                action_slot,
                                action_type,
                                trigger_time,
                                clip_index_target,
                            )
                        elif command_type == "get_clip_follow_actions":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._get_clip_follow_actions(
                                track_index, clip_index
                            )
                        elif command_type == "set_master_volume":
                            volume = params.get("volume", 0.75)
                            result = self._set_master_volume(volume)
                        elif command_type == "get_master_track_info":
                            result = self._get_master_track_info()
                        elif command_type == "get_return_tracks":
                            result = self._get_return_tracks()
                        elif command_type == "get_all_tracks":
                            result = self._get_all_tracks()
                        elif command_type == "get_all_scenes":
                            result = self._get_all_scenes()
                        elif command_type == "get_session_overview":
                            result = self._get_session_overview()
                        elif command_type == "get_all_clips_in_track":
                            track_index = params.get("track_index", 0)
                            result = self._get_all_clips_in_track(track_index)
                        elif command_type == "set_note_velocity":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            note_indices = params.get("note_indices", [])
                            velocity = params.get("velocity", 100)
                            result = self._set_note_velocity(
                                track_index, clip_index, note_indices, velocity
                            )
                        elif command_type == "set_note_duration":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            note_indices = params.get("note_indices", [])
                            duration = params.get("duration", 0.25)
                            result = self._set_note_duration(
                                track_index, clip_index, note_indices, duration
                            )
                        elif command_type == "set_note_pitch":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            note_indices = params.get("note_indices", [])
                            pitch = params.get("pitch", 60)
                            result = self._set_note_pitch(
                                track_index, clip_index, note_indices, pitch
                            )
                        elif command_type == "get_clip_envelopes":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._get_clip_envelopes(track_index, clip_index)
                        elif command_type == "mix_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            source_track_index = params.get("source_track_index", 0)
                            result = self._mix_clip(
                                track_index, clip_index, source_track_index
                            )
                        elif command_type == "stretch_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            length = params.get("length", 4.0)
                            result = self._stretch_clip(track_index, clip_index, length)
                        elif command_type == "crop_clip":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._crop_clip(track_index, clip_index)
                        elif command_type == "duplicate_clip_to":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            target_track_index = params.get("target_track_index", 0)
                            target_clip_index = params.get("target_clip_index", 0)
                            result = self._duplicate_clip_to(
                                track_index,
                                clip_index,
                                target_track_index,
                                target_clip_index,
                            )
                        elif command_type == "group_tracks":
                            track_indices = params.get("track_indices", [])
                            result = self._group_tracks(track_indices)
                        elif command_type == "ungroup_tracks":
                            track_index = params.get("track_index", 0)
                            result = self._ungroup_tracks(track_index)
                        elif command_type == "reload_script":
                            result = self._reload_script()
                            result = self._reload_script()
                        elif command_type == "set_clip_warp_mode":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            warp_mode = params.get("warp_mode", 0)
                            result = self._set_clip_warp_mode(
                                track_index, clip_index, warp_mode
                            )
                        elif command_type == "get_clip_warp_markers":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            result = self._get_clip_warp_markers(
                                track_index, clip_index
                            )
                        elif command_type == "add_warp_marker":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            position = params.get("position", 0.0)
                            result = self._add_warp_marker(
                                track_index, clip_index, position
                            )
                        elif command_type == "delete_warp_marker":
                            track_index = params.get("track_index", 0)
                            clip_index = params.get("clip_index", 0)
                            marker_index = params.get("marker_index", 0)
                            result = self._delete_warp_marker(
                                track_index, clip_index, marker_index
                            )

                        # Put result in queue
                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        self.log_message("Error in main thread task: " + str(e))
                        self.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})

                # Schedule the task to run on the main thread
                try:
                    self.schedule_message(0, main_thread_task)
                except AssertionError:
                    # If we're already on the main thread, execute directly
                    main_thread_task()

                # Wait for the response with a timeout
                try:
                    task_response = response_queue.get(timeout=10.0)
                    if task_response.get("status") == "error":
                        response["status"] = "error"
                        response["message"] = task_response.get(
                            "message", "Unknown error"
                        )
                    else:
                        response["result"] = task_response.get("result", {})
                except queue.Empty:
                    response["status"] = "error"
                    response["message"] = "Timeout waiting for operation to complete"
            elif command_type == "get_browser_item":
                uri = params.get("uri", None)
                path = params.get("path", None)
                response["result"] = self._get_browser_item(uri, path)
            elif command_type == "get_browser_categories":
                category_type = params.get("category_type", "all")
                response["result"] = self._get_browser_categories(category_type)
            elif command_type == "get_browser_items":
                path = params.get("path", "")
                item_type = params.get("item_type", "all")
                response["result"] = self._get_browser_items(path, item_type)
            # Add the new browser commands
            elif command_type == "get_browser_tree":
                category_type = params.get("category_type", "all")
                response["result"] = self.get_browser_tree(category_type)
            elif command_type == "get_browser_items_at_path":
                path = params.get("path", "")
                response["result"] = self.get_browser_items_at_path(path)
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            response["status"] = "error"
            response["message"] = str(e)

        return response

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
            self.log_message("Error getting session info: " + str(e))
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

            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "mute": track.mute,
                "solo": track.solo,
                "arm": track.arm,
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

            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]

            # Check if the clip slot already has a clip
            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")

            # Create the clip
            clip_slot.create_clip(length)

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
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            track_name = track.name
            self._song.delete_track(track_index)
            result = {"deleted_index": track_index, "deleted_track": track_name}
            return result
        except Exception as e:
            self.log_message("Error deleting track: " + str(e))
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
            track = self._song.tracks[track_index]
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
            device.delete_device()
            result = {"deleted_device": device_name, "device_index": device_index}
            return result
        except Exception as e:
            self.log_message("Error deleting device: " + str(e))
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

            if send_index < 0 or send_index >= len(self._song.return_tracks):
                raise IndexError("Send index out of range")

            send = self._song.return_tracks[send_index]
            send.amount = amount

            result = {
                "track_index": track_index,
                "send_index": send_index,
                "amount": amount,
            }
            return result
        except Exception as e:
            self.log_message("Error setting send amount: " + str(e))
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
            time.beats = beat
            self._song.create_locator(time)
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
                        notes.append(
                            {
                                "pitch": note.pitch,
                                "start_time": note.start_time,
                                "duration": note.duration,
                                "velocity": note.velocity,
                                "mute": note.mute if hasattr(note, "mute") else False,
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

            result = {"envelopes": []}
            return result
        except Exception as e:
            self.log_message("Error getting clip envelopes: " + str(e))
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

            clip_slot.crop_clip()
            result = {"cropped": True}
            return result
        except Exception as e:
            self.log_message("Error stretching clip: " + str(e))
            self.log_message(traceback.format_exc())
            raise

    def _resize_clip(self, track_index, clip_index, length):
        """Resize clip to new length"""
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
            result = {"resized": True, "length": length}
            return result
        except Exception as e:
            self.log_message("Error resizing clip: " + str(e))
            self.log_message(traceback.format_exc())
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

            clip_slot.duplicate_clip_to(target_slot)
            result = {"duplicated": True, "to": [target_track_index, target_clip_index]}
            return result
        except Exception as e:
            self.log_message("Error duplicating clip to: " + str(e))
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
            clip = clip_slot.clip

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
            clip = clip_slot.clip
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
            clip = clip_slot.clip
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
        except:
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
