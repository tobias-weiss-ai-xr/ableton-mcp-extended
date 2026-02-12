# Dual-Server Architecture Design for Ableton Remote Script

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Design dual TCP/UDP server architecture for high-performance Ableton Live control while maintaining 100% backward compatibility.

**Architecture:** Hybrid approach with separate TCP (reliable, request/response) and UDP (fast, fire-and-forget) servers running in a single Remote Script codebase.

**Tech Stack:** Python 2/3 compatible socket programming, Ableton Live Remote Script API, threading with daemon mode, JSON protocols.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ableton Live Remote Script                   │
│                    (AbletonMCP/__init__.py)                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Class: AbletonMCP(ControlSurface)                      │   │
│  │                                                          │   │
│  │  Shared State:                                          │   │
│  │  - self._song = self.song()                             │   │
│  │  - self.running = False → True                           │   │
│  │                                                          │   │
│  │  TCP Server (Port 9877):                                │   │
│  │  - self.tcp_server_socket                               │   │
│  │  - self.tcp_client_threads = []                         │   │
│  │  - self.tcp_server_thread                               │   │
│  │  - _tcp_server_loop()                                   │   │
│  │  - _handle_tcp_client(client_socket)                    │   │
│  │                                                          │   │
│  │  UDP Server (Port 9878):                                │   │
│  │  - self.udp_server_socket                               │   │
│  │  - self.udp_server_thread                               │   │
│  │  - _udp_server_loop()                                   │   │
│  │  - _handle_udp_data(data, addr)                         │   │
│  │                                                          │   │
│  │  Command Execution:                                     │   │
│  │  - self.schedule_message(0, task) → Main Thread         │   │
│  │  - _process_command(command) → TCP routing              │   │
│  │  - _process_udp_command(command) → UDP routing          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
┌──────────────────▼─────────┐ ┌─────────▼──────────────────┐
│     TCP Server (9877)      │ │     UDP Server (9878)      │
│                            │ │                            │
│  ‣ Reliable connections    │ │  ‣ Connectionless          │
│  ‣ Request/response        │ │  ‣ Fire-and-forget         │
│  ‣ JSON protocol           │ │  ‣ JSON protocol (minimal) │
│  ‣ Client tracking         │ │  ‣ No client tracking      │
│  ‣ Response required       │ │  ‣ No response             │
└──────────┬─────────────────┘ └──────────┬─────────────────┘
           │                               │
           │                               │
    ┌──────▼──────┐                  ┌─────▼──────┐
    │   MCP TCP   │                  │   MCP UDP  │
    │   Commands  │                  │   Commands │
    │  (85 tools) │                  │  (subset)   │
    └──────┬──────┘                  └─────┬──────┘
           │                               │
           └───────────┬───────────────────┘
                       │
            ┌──────────▼──────────┐
            │ Ableton Live API     │
            │ (self._song)         │
            └─────────────────────┘
```

---

## Component Architecture

### 1. Unified Connection Object Model

```python
class AbletonMCP(ControlSurface):
    def __init__(self, c_instance):
        """Initialize dual-server control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP Remote Script initializing...")

        # Shared state
        self._song = self.song()
        self.running = False  # Shared flag for both servers

        # TCP Server State (existing pattern from __init__.py:36-38)
        self.tcp_server_socket = None
        self.tcp_client_threads = []
        self.tcp_server_thread = None

        # UDP Server State (new, following __init__.py:35-36 pattern)
        self.udp_server_socket = None
        self.udp_server_thread = None

        # Start both servers
        self.start_tcp_server()   # Existing: __init__.py:45
        self.start_udp_server()   # New: must add

        self.show_message(
            f"AbletonMCP: TCP on {str(DEFAULT_PORT)}, UDP on {str(DEFAULT_PORT + 1)}"
        )
```

### 2. Socket Initialization Patterns

**TCP Socket Setup (Pattern from __init__.py:82-85):**
```python
def start_tcp_server(self):
    """Start TCP server in daemon thread"""
    try:
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_server_socket.bind((HOST, DEFAULT_PORT))  # DEFAULT_PORT = 9877
        self.tcp_server_socket.listen(5)

        self.running = True
        self.tcp_server_thread = threading.Thread(target=self._tcp_server_loop)
        self.tcp_server_thread.daemon = True  # Pattern from __init__.py:89
        self.tcp_server_thread.start()

        self.log_message("Server started on port " + str(DEFAULT_PORT))
    except Exception as e:
        self.log_message("Error starting server: " + str(e))
```

**UDP Socket Setup (Pattern from AbletonMCP_UDP/__init__.py:160-161):**
```python
def start_udp_server(self):
    """Start UDP server in daemon thread"""
    try:
        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server_socket.bind((HOST, DEFAULT_PORT + 1))  # UDP on 9878

        self.running = True
        self.udp_server_thread = threading.Thread(target=self._udp_server_loop)
        self.udp_server_thread.daemon = True
        self.udp_server_thread.start()

        self.log_message("UDP server started on port " + str(DEFAULT_PORT + 1))
    except Exception as e:
        self.log_message("Error starting UDP server: " + str(e))
```

### 3. Thread Management Strategy

**Thread Daemon Pattern (from __init__.py:88-89, 115-116):**
```python
# TCP server thread
self.tcp_server_thread = threading.Thread(target=self._tcp_server_loop)
self.tcp_server_thread.daemon = True
self.tcp_server_thread.start()

# UDP server thread
self.udp_server_thread = threading.Thread(target=self._udp_server_loop)
self.udp_server_thread.daemon = True
self.udp_server_thread.start()
```

**Key Principles:**
1. **Both servers use daemon mode** to ensure clean shutdown
2. **Independent loops**: `_tcp_server_loop()` and `_udp_server_loop()` run concurrently
3. **Shared running flag**: `self.running` controls both server loops
4. **Client tracking**: TCP tracks client threads, UDP has no clients (connectionless)

### 4. Server Loop Patterns

**TCP Server Loop (from __init__.py:97-136):**
```python
def _tcp_server_loop(self):
    """TCP server thread implementation"""
    try:
        self.log_message("Server thread started")
        self.tcp_server_socket.settimeout(1.0)  # Check running flag regularly

        while self.running:
            try:
                client, address = self.tcp_server_socket.accept()
                self.log_message("Connection accepted from " + str(address))
                self.show_message("AbletonMCP: Client connected")

                # Handle client in separate thread (pattern from __init__.py:112-119)
                client_thread = threading.Thread(
                    target=self._handle_tcp_client, args=(client,)
                )
                client_thread.daemon = True
                client_thread.start()
                self.tcp_client_threads.append(client_thread)

                # Clean up finished threads (pattern from __init__.py:121-124)
                self.tcp_client_threads = [
                    t for t in self.tcp_client_threads if t.is_alive()
                ]
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.log_message("Server accept error: " + str(e))
                time.sleep(0.5)

        self.log_message("Server thread stopped")
    except Exception as e:
        self.log_message("Server thread error: " + str(e))
```

**UDP Server Loop (based on AbletonMCP_UDP/__init__.py:171-194):**
```python
def _udp_server_loop(self):
    """UDP server thread implementation"""
    try:
        self.log_message("UDP server thread started")

        while self.running:
            try:
                data, addr = self.udp_server_socket.recvfrom(1024)
                if not self.running:
                    break

                # Process datagram (fire-and-forget, no response)
                self._handle_udp_data(data, addr)

            except socket.error as se:
                if self.running:
                    self.log_message("UDP server socket error: " + str(se))
                break
            except Exception as e:
                if self.running:
                    self.log_message("UDP server loop error: " + str(e))
                time.sleep(0.1)

        self.log_message("UDP server thread stopped")
    except Exception as e:
        self.log_message("UDP server thread critical error: " + str(e))
```

### 5. Disconnect Logic

```python
def disconnect(self):
    """Called when Ableton closes or control surface is removed"""
    self.log_message("AbletonMCP disconnecting...")
    self.running = False

    # Stop TCP server (pattern from __init__.py:59-68)
    if self.tcp_server_socket:
        try:
            self.tcp_server_socket.close()
        except:
            pass

    if self.tcp_server_thread and self.tcp_server_thread.is_alive():
        self.tcp_server_thread.join(1.0)

    # Clean up client threads (pattern from __init__.py:70-74)
    for client_thread in self.tcp_client_threads[:]:
        if client_thread.is_alive():
            self.log_message("Client thread still alive during disconnect")

    # Stop UDP server (new)
    if self.udp_server_socket:
        try:
            self.udp_server_socket.close()
        except:
            pass

    if self.udp_server_thread and self.udp_server_thread.is_alive():
        self.udp_server_thread.join(1.0)

    ControlSurface.disconnect(self)
    self.log_message("AbletonMCP disconnected")
```

---

## Message Formats

### TCP Message (Existing Format - Unchanged)

**Request:**
```json
{
  "type": "set_device_parameter",
  "params": {
    "track_index": 0,
    "device_index": 1,
    "parameter_index": 2,
    "value": 0.75
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "device_name": "Operator",
    "parameter_name": "Cutoff",
    "value": 0.75
  }
}
```

### UDP Message (Minimal Format - Fire-and-Forget)

**Same JSON structure for consistency:**
```json
{
  "type": "set_device_parameter",
  "params": {
    "track_index": 0,
    "device_index": 1,
    "parameter_index": 2,
    "value": 0.75
  }
}
```

**No response sent** (fire-and-forget pattern)

**Rationale:**
- Minimal overhead: Keep JSON for compatibility with existing code
- Fire-and-forget: No acknowledgment needed for real-time parameters
- Acceptable loss: Packet loss <5% is tolerable for continuous updates
- Self-correcting: Next update corrects any missed updates

---

## Command Routing Matrix

### TCP-ONLY Commands (Critical Operations - MUST use TCP)

**Category: Irreversible State Changes**

| Command | Reason |
|---------|--------|
| `delete_all_tracks` | Cannot be undone easily |
| `delete_track` | Permanent deletion |
| `delete_clip` | Cannot be undone easily |
| `delete_scene` | Permanent deletion |
| `delete_locator` | Permanent deletion |
| `delete_warp_marker` | Permanent deletion |
| `clear_automation` | Cannot be undone easily |
| `delete_device` | Permanent deletion |

**Category: Content Creation**

| Command | Reason |
|---------|--------|
| `create_midi_track` | Requires confirmation |
| `create_audio_track` | Requires confirmation |
| `create_clip` | Requires confirmation |
| `create_scene` | Requires confirmation |
| `create_locator` | Requires confirmation |
| `add_notes_to_clip` | Content is valuable, must be reliable |
| `add_automation_point` | Automation is valuable, must be reliable |
| `add_warp_marker` | Requires confirmation |

**Category: Loading Operations**

| Command | Reason |
|---------|--------|
| `load_instrument_or_effect` | Loading requires success confirmation |
| `load_browser_item` | Loading requires success confirmation |
| `load_instrument_preset` | Preset loading requires confirmation |
| `import_audio_file` | File I/O must be reliable |

**Category: Transport Control**

| Command | Reason |
|---------|--------|
| `start_playback` | Critical for timing |
| `stop_playback` | Critical for timing |
| `start_recording` | Critical for capturing audio |
| `stop_recording` | Critical for capturing audio |
| `set_playhead_position` | Must be accurate |

**Category: Undo/Redo**

| Command | Reason |
|---------|--------|
| `undo` | Critical for workflow |
| `redo` | Critical for workflow |

**Category: Complex Modifications**

| Command | Reason |
|---------|--------|
| `duplicate_track` | Complex operation, must succeed |
| `duplicate_clip` | Complex operation, must succeed |
| `duplicate_clip_to` | Complex operation, must succeed |
| `duplicate_device` | Complex operation, must succeed |
| `move_clip` | Complex operation, must succeed |
| `move_device` | Position changes must be reliable |
| `group_tracks` | Complex operation, must succeed |
| `ungroup_tracks` | Complex operation, must succeed |
| `set_track_name` | Metadata must be preserved |
| `set_scene_name` | Metadata must be preserved |
| `set_clip_name` | Metadata must be preserved |
| `set_clip_loop` | Loop structure must be preserved |
| `set_clip_follow_action` | Automation behavior must be reliable |
| `get_clip_follow_actions` | Must return complete data |
| `set_clip_launch_mode` | Mode changes must be reliable |
| `set_clip_warp_mode` | Mode changes must be reliable |
| `set_tempo` | Tempo changes must be reliable |
| `set_time_signature` | Time signature must be reliable |
| `set_metronome` | Metronome state must be reliable |
| `trigger_scene` | Scene triggering must be reliable |
| `fire_scene` | Scene firing must be reliable |
| `set_loop` | Loop region must be precise |
| `set_track_color` | Color changes must be preserved |
| `set_track_fold` | Fold state must be preserved |
| `set_track_monitoring_state` | Monitoring state must be reliable |
| `toggle_device_bypass` | Bypass state must be reliable |
| `set_monitor_volume` | Volume must be reliable |

**Category: Note Modifications**

| Command | Reason |
|---------|--------|
| `delete_notes_from_clip` | Content is valuable |
| `set_note_velocity` | Note data is valuable |
| `set_note_duration` | Note data is valuable |
| `set_note_pitch` | Note data is valuable |
| `quantize_clip` | Quantization is valuable |
| `transpose_clip` | Transposition is valuable |
| `mix_clip` | Complex mixing operation |
| `stretch_clip` | Time changes must be reliable |
| `crop_clip` | Content must be reliable |

### UDP-ALLOWED Commands (Real-Time Parameters - MAY use UDP)

**Category: Parameter Updates**

| Command | Reason |
|---------|--------|
| `set_device_parameter` | High-frequency, reversible |
| `batch_set_device_parameters` | High-frequency, reversible, efficiency |
| `set_track_volume` | High-frequency, reversible |
| `set_track_pan` | High-frequency, reversible |
| `set_track_mute` | High-frequency, reversible |
| `set_track_solo` | High-frequency, reversible |
| `set_track_arm` | High-frequency, reversible |
| `set_master_volume` | High-frequency, reversible |
| `set_send_amount` | High-frequency, reversible |

**Rationale:** All UDP commands are:
1. **Reversible**: Next update corrects any loss
2. **High-frequency**: Benefit from low latency
3. **Simple**: Minimal data payload
4. **Non-critical**: Acceptable to miss <5% of updates

### TCP-Requested Commands (Read Operations - MUST use TCP)

**Category: Information Retrieval**

| Command | Reason |
|---------|--------|
| `get_session_info` | Must return data to client |
| `get_session_overview` | Must return data to client |
| `get_track_info` | Must return data to client |
| `get_all_tracks` | Must return data to client |
| `get_all_scenes` | Must return data to client |
| `get_all_clips_in_track` | Must return data to client |
| `get_master_track_info` | Must return data to client |
| `get_return_tracks` | Must return data to client |
| `get_device_parameters` | Must return data to client |
| `get_clip_notes` | Must return data to client |
| `get_clip_envelopes` | Must return data to client |
| `get_clip_warp_markers` | Must return data to client |
| `get_playhead_position` | Must return data to client |

**Category: Browser Operations**

| Command | Reason |
|---------|--------|
| `get_browser_tree` | Must return hierarchical data |
| `get_browser_categories` | Must return data to client |
| `get_browser_items_at_path` | Must return data to client |
| `get_browser_item` | Must return data to client |

---

## Command Execution Flow

### TCP Request/Response Flow

```python
def _handle_tcp_client(self, client_socket):
    """Handle TCP client communication"""
    buffer = ""
    try:
        while self.running:
            data = client_socket.recv(8192)
            if not data:
                self.log_message("TCP Client disconnected")
                break

            # Accumulate buffer (pattern from __init__.py:155-161)
            try:
                buffer += data.decode("utf-8")
            except AttributeError:
                buffer += data

            try:
                # Parse command
                command = json.loads(buffer)
                buffer = ""

                self.log_message("Received command: " + str(command.get("type", "unknown")))

                # Process command with response queue (pattern from __init__.py:311-323)
                response_queue = queue.Queue()

                def main_thread_task():
                    try:
                        result = self._execute_command(command)
                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        self.log_message("Error in main thread task: " + str(e))
                        self.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})

                # Schedule on main thread (pattern from __init__.py:584-589)
                try:
                    self.schedule_message(0, main_thread_task)
                except AssertionError:
                    main_thread_task()

                # Wait for response (pattern from __init__.py:591-603)
                try:
                    task_response = response_queue.get(timeout=10.0)
                    if task_response.get("status") == "error":
                        response = task_response
                    else:
                        response = {"status": "success", "result": task_response.get("result", {})}
                except queue.Empty:
                    response = {"status": "error", "message": "Timeout waiting for operation to complete"}

                # Send response (pattern from __init__.py:176-181)
                try:
                    client_socket.sendall(json.dumps(response).encode("utf-8"))
                except AttributeError:
                    client_socket.sendall(json.dumps(response))

            except ValueError:
                # Incomplete JSON, wait for more
                continue

    except Exception as e:
        self.log_message("Error in client handler: " + str(e))
    finally:
        try:
            client_socket.close()
        except:
            pass
```

### UDP Fire-and-Forget Flow

```python
def _handle_udp_data(self, data, addr):
    """Handle UDP datagram (fire-and-forget)"""
    try:
        # Parse JSON
        command_str = data.decode('utf-8')
        command_json = json.loads(command_str)

        self.log_message(f"UDP: Received {command_json.get('type', 'unknown')} from {addr}")

        # Execute without response queue
        def udp_task():
            try:
                self._execute_udp_command(command_json)
            except Exception as e:
                # Log but don't block (fire-and-forget acceptable)
                self.log_message(f"UDP: Error executing {command_json.get('type', 'unknown')}: {e}")

        # Schedule on main thread
        self.schedule_message(0, udp_task)
        # No response, no timeout

    except Exception as e:
        self.log_message(f"UDP: Error processing datagram from {addr}: {e}")
        # Continue processing, don't crash
```

---

## Thread Safety Strategy

### Main Thread Scheduling Pattern

**Pattern:** Use `self.schedule_message(0, task)` for all Live API modifications (from __init__.py:311-323, 584-589)

```python
response_queue = queue.Queue()

def main_thread_task():
    try:
        result = self._set_device_parameter(track_index, device_index,
                                           parameter_index, value)
        response_queue.put({"status": "success", "result": result})
    except Exception as e:
        self.log_message("Error in main thread task: " + str(e))
        self.log_message(traceback.format_exc())
        response_queue.put({"status": "error", "message": str(e)})

# Schedule on main thread
try:
    self.schedule_message(0, main_thread_task)
except AssertionError:
    # Already on main thread, execute directly
    main_thread_task()

# Wait for response (TCP only)
response = response_queue.get(timeout=10.0)
```

**UDP-Specific Pattern (No response queue needed):**

```python
def udp_task():
    try:
        # Fire-and-forget: execute without response tracking
        self._set_device_parameter(track_index, device_index,
                                   parameter_index, value)
    except Exception as e:
        # Log but don't block
        self.log_message(f"UDP: Error setting parameter: {e}")

# Schedule on main thread
self.schedule_message(0, udp_task)
# No response queue needed for UDP
```

### Thread Safety Principles

**Key Principles:**

1. **All Live API calls go through main thread**
   - `self.schedule_message(0, task)` ensures thread-safe execution
   - Both TCP and UDP use this pattern
   - No direct API calls from server threads

2. **Shared state access**
   - Threads never modify `self._song` directly
   - All modifications go through `schedule_message()`
   - Reads are atomic in Live Object Model

3. **No locking required**
   - Main thread serialization prevents race conditions
   - Ableton Live API is thread-safe for parameter access
   - Only state-changing operations need serialization

---

## Error Handling

### TCP Error Handling (Strict)

**Pattern:** Return error response to client (from __init__.py:186-200)

```python
try:
    response = self._process_command(command)
    client.sendall(json.dumps(response).encode("utf-8"))
except Exception as e:
    self.log_message("Error handling client data: " + str(e))
    self.log_message(traceback.format_exc())

    # Send error response if possible
    error_response = {"status": "error", "message": str(e)}
    try:
        client.sendall(json.dumps(error_response).encode("utf-8"))
    except:
        # If we can't send the error, the connection is probably dead
        break
```

**Behavior:**
- All errors propagate to client via JSON response
- Client can retry or handle errors
- Connection stays alive for next command
- Critical errors don't disconnect client immediately

### UDP Error Handling (Graceful)

**Pattern:** Log only, no response (based on AbletonMCP_UDP/__init__.py:197-226)

```python
def _handle_udp_data(self, data, addr):
    try:
        command_str = data.decode('utf-8')
        command_json = json.loads(command_str)
        self._execute_udp_command(command_json)
    except Exception as e:
        # Log but don't respond (fire-and-forget acceptable)
        self.log_message(f"UDP error: {e}")
        # Continue processing, don't crash
```

**Behavior:**
- Errors logged but not reported to sender
- Lost packets treated as acceptable (up to 5% tolerance)
- Real-time parameter updates continue despite occasional failures
- No retry logic in Remote Script

### TCP Fallback Strategy

**When UDP is unreliable for critical parameters:**

```python
# MCP Server-side logic (not Remote Script)
def set_parameter_safely(track_idx, dev_idx, param_idx, value):
    """Set parameter with TCP fallback on UDP failure"""
    try:
        # Try UDP first for speed
        send_udp_command("set_device_parameter", {
            "track_index": track_idx,
            "device_index": dev_idx,
            "parameter_index": param_idx,
            "value": value
        })
        return True
    except Exception as e:
        # Fallback to TCP for reliability
        self.log_message(f"UDP failed, falling back to TCP: {e}")
        send_tcp_command("set_device_parameter", {
            "track_index": track_idx,
            "device_index": dev_idx,
            "parameter_index": param_idx,
            "value": value
        })
        return True
```

---

## Performance Targets

| Metric                  | TCP           | UDP           | Target            |
|-------------------------|---------------|---------------|-------------------|
| Parameter Updates/sec   | 10-20         | 50-100        | **1000 in <20s**  |
| Latency                 | 20-50ms       | 5-20ms        | **<20ms**         |
| Packet Loss Tolerance   | 0% (retry)    | 5% (fire+forget) | **<5%**          |
| Throughput              | Reliability   | Speed         | **Balanced**      |

### Benchmark Scenarios

**Scenario 1: 1000 Parameter Updates**
- TCP: ~50-100 seconds
- UDP: ~10-20 seconds (50-100Hz)
- **Target: <20 seconds**

```python
# Benchmark test
def test_1000_parameter_updates():
    update_count = 1000
    start_time = time.time()

    for i in range(update_count):
        # Via UDP
        send_udp_command("set_device_parameter", {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 0,
            "value": 0.5 + (i * 0.001)  # Sweep 0.5 → 1.5
        })

    elapsed = time.time() - start_time
    updates_per_second = update_count / elapsed

    print(f"UDP: {updates_per_second:.1f} updates/second")
    print(f"Target: 50-100 updates/second")
    print(f"Status: {'PASS' if updates_per_second >= 50 else 'FAIL'}")

    return updates_per_second >= 50
```

**Scenario 2: Real-Time Filter Automation**
- TCP: Choppy updates (10-20Hz)
- UDP: Smooth sweeps (50-100Hz)
- **Target: 50Hz+ for smooth sweeps**

**Scenario 3: Batch Operations**
- TCP: Reliable but slow
- UDP: Fast but accepts 5% loss
- **Target: Use TCP for critical, UDP for non-critical**

---

## Command Classification Rules

### TCP-Required (Immutable)

A command MUST use TCP if it meets ANY of these criteria:

1. **Irreversible State Change**
   - Deletes tracks, clips, scenes
   - Modifies clip content permanently
   - Operations that cannot be easily undone

2. **Requires Confirmation**
   - Browser item loading
   - Instrument/effect loading
   - Preset loading
   - Any "create" operation

3. **Returns Complex Data**
   - Multi-object queries (get_all_tracks, etc.)
   - Large data structures (clip notes, envelopes)
   - Hierarchical data (browser tree)
   - All "get" operations

4. **Undo/Redo Affected**
   - Operations that add to Ableton's undo stack
   - Requires explicit acknowledgment

5. **Low Frequency Operations**
   - Song creation/destruction
   - Track management
   - Scene management
   - Device loading

### UDP-Allowed (Optional)

A command MAY use UDP if it meets ALL of these criteria:

1. **Reversible State Change**
   - Parameter updates (volume, pan, device parameters)
   - Can be corrected by next update
   - No permanent data loss

2. **Fire-and-Forget Acceptable**
   - Lost packet = temporarily stale value
   - Honored but not critical if failed
   - Next update fixes any missed updates

3. **Simple Data Structure**
   - Minimal payload (single float or small array)
   - No nested objects
   - Validateable without server response

4. **High Frequency Operations**
   - Real-time filter sweeps
   - Volume envelopes
   - Continuous parameter modulation

---

## Implementation Guidelines

### 1. Proof of Concept Command Set (UDP Phase 1)

**Minimal Viable UDP Commands (9 commands):**

1. `set_device_parameter` - Single parameter update
2. `batch_set_device_parameters` - Multi-parameter update
3. `set_track_volume` - Track volume control
4. `set_track_pan` - Track panning
5. `set_track_mute` - Track mute state
6. `set_track_solo` - Track solo state
7. `set_track_arm` - Track arm state
8. `set_master_volume` - Master volume control
9. `set_send_amount` - Send amount control

**Testing priority:**
1. Start with `set_device_parameter` (most common use case)
2. Add `batch_set_device_parameters` (efficiency)
3. Add track-level controls (volume, pan, mute, solo, arm)
4. Add send/master controls
5. Expand to other parameter types as needed

### 2. Command Routing Implementation

```python
def _process_command(self, command):
    """Process TCP command (existing pattern)"""
    command_type = command.get("type", "")
    # ... full routing of all 85 commands
    # Returns response dict

def _process_udp_command(self, command):
    """Process UDP command (new limited routing)"""
    command_type = command.get("type", "")
    params = command.get("params", {})

    def task():
        try:
            if command_type == "set_device_parameter":
                track_index = params.get("track_index", 0)
                device_index = params.get("device_index", 0)
                parameter_index = params.get("parameter_index", 0)
                value = params.get("value", 0.0)
                self._set_device_parameter(track_index, device_index,
                                          parameter_index, value)

            elif command_type == "batch_set_device_parameters":
                track_index = params.get("track_index", 0)
                device_index = params.get("device_index", 0)
                parameter_indices = params.get("parameter_indices", [])
                values = params.get("values", [])
                self._batch_set_device_parameters(track_index, device_index,
                                                 parameter_indices, values)

            elif command_type == "set_track_volume":
                track_index = params.get("track_index", 0)
                volume = params.get("volume", 0.75)
                self._set_track_volume(track_index, volume)

            elif command_type == "set_track_pan":
                track_index = params.get("track_index", 0)
                pan = params.get("pan", 0.0)
                self._set_track_pan(track_index, pan)

            # ... other UDP-allowed commands

            else:
                self.log_message(f"UDP: Unknown or unsupported command type: {command_type}")

        except Exception as e:
            self.log_message(f"UDP: Error executing {command_type}: {e}")

    self.schedule_message(0, task)
    # No response for UDP
```

### 3. Backward Compatibility

**Guaranteed Compatibility:**

**Existing Workflow:**
- All 85 MCP tools continue working via TCP
- No changes to MCP server tool implementations
- Client code automatically uses TCP (existing behavior)

**New Capability:**
- MCP server can optionally use UDP for parameter updates
- Automatic TCP fallback on UDP errors
- Transparent to end user

---

## Testing Strategy

### Unit Tests (MCP Server Side)

```python
def test_tcp_reliability():
    """Verify all 85 commands work over TCP"""
    for tool in all_85_tools:
        result = call_tcp_tool(tool, params)
        assert result["status"] == "success"
        # Compare results before/after state

def test_udp_parameter_updates():
    """Verify UDP parameter updates match TCP"""
    for command in udp_allowed_commands:
        # Set initial value via TCP
        tcp_result = call_tcp_command(command, params)
        assert tcp_result["status"] == "success"

        # Update via UDP
        send_udp_command(command, params)

        # Verify final state matches
        final_value = get_parameter_value(...)
        assert final_value == params["value"]

def test_udp_packet_loss():
    """Test system tolerance to packet loss"""
    # Send 100 updates with 5% artificial drop
    update_count = 100
    loss_rate = 0.05

    for i in range(update_count):
        if random.random() >= loss_rate:
            send_udp_command("set_device_parameter", {...})

    # Verify final state is correct (last update wins)
    final_value = get_parameter_value(...)
    assert final_value == expected_final_value

def test_tcp_fallback():
    """Test TCP fallback on UDP errors"""
    # Simulate UDP failure
    with patch('socket.sendto', side_effect=ConnectionError):
        # Should fallback to TCP
        result = set_parameter_safely(...)
        assert result["status"] == "success"

    # Verify parameter was set correctly
    final_value = get_parameter_value(...)
    assert final_value == expected_value
```

### Integration Tests

```python
def test_hybrid_session():
    """Real-world scenario with mixed TCP/UDP operations"""
    # 1. Create tracks via TCP
    result = call_tcp_command("create_midi_track", {"index": -1})
    assert result["status"] == "success"
    track_index = result["result"]["index"]

    # 2. Load instruments via TCP
    result = call_tcp_command("load_instrument_or_effect", {
        "track_index": track_index,
        "uri": "synth_uri"
    })
    assert result["status"] == "success"

    # 3. Set initial parameters via TCP
    result = call_tcp_command("set_device_parameter", {
        "track_index": track_index,
        "device_index": 0,
        "parameter_index": 0,
        "value": 0.5
    })
    assert result["status"] == "success"

    # 4. Run automation via UDP (1000 updates)
    for i in range(1000):
        send_udp_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": 0,
            "parameter_index": 0,
            "value": 0.5 + (i * 0.001)
        })

    # 5. Verify final state matches expectations
    final_value = get_parameter_value(track_index, 0, 0)
    assert final_value == 1.5  # Last update value
```

### Performance Benchmarks

```python
def benchmark_tcp_vs_udp():
    """Compare TCP and UDP performance"""
    update_count = 1000

    # TCP benchmark
    tcp_start = time.time()
    for i in range(update_count):
        call_tcp_command("set_device_parameter", {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 0,
            "value": 0.5 + (i * 0.001)
        })
    tcp_elapsed = time.time() - tcp_start

    # UDP benchmark
    udp_start = time.time()
    for i in range(update_count):
        send_udp_command("set_device_parameter", {
            "track_index": 0,
            "device_index": 0,
            "parameter_index": 0,
            "value": 0.5 + (i * 0.001)
        })
    udp_elapsed = time.time() - udp_start

    speedup = tcp_elapsed / udp_elapsed
    print(f"TCP: {tcp_elapsed:.2f}s for {update_count} updates")
    print(f"UDP: {udp_elapsed:.2f}s for {update_count} updates")
    print(f"Speedup: {speedup:.1f}x")

    assert speedup >= 10  # At least 10x better
```

---

## Risks and Mitigations

### Risk 1: Thread Safety Violations

**Risk:** Both threads accessing `self._song` concurrently could cause race conditions

**Mitigation:**
- Follow existing `schedule_message()` pattern strictly
- No direct Live API calls from server threads
- All commands go through main thread executor

**Testing:**
- Create concurrent access test to verify thread safety

### Risk 2: Port Conflicts

**Risk:** TCP (9877) and UDP (9878) might conflict with other applications

**Mitigation:**
- TCP: Port 9877 (existing, proven)
- UDP: Port 9878 (+1 offset, unlikely conflict)
- Bind with `SO_REUSEADDR` for both

**Testing:**
- Verify both servers start without conflicts
- Test with Ableton Live running

### Risk 3: Packet Loss Impact

**Risk:** High-frequency UDP updates might lose packets

**Mitigation:**
- Accept 5% loss for non-critical parameters
- TCP fallback for critical operations
- Continuous updates self-correct transient losses
- Final state is correct (last update wins)

**Testing:**
- Packet loss simulation with various rates (1%, 5%, 10%)
- Verify system still works at 5% loss

### Risk 4: Code Complexity

**Risk:** Dual-server adds complexity (two threads, two protocols)

**Mitigation:**
- Maintain single codebase (no separate Remote Script)
- Limit UDP routing to proven-safe commands
- Clear separation of TCP vs UDP logic
- Comprehensive documentation

**Testing:**
- Code review for clarity
- Manual testing of edge cases

---

## Success Criteria

### Functional Requirements

- [x] Architecture design documented
- [x] UDP server skeleton implemented
- [ ] UDP routing implemented for parameter commands (9 commands)
- [ ] MCP server UDP client implemented
- [ ] All 85 TCP commands continue working
- [ ] UDP parameter commands match TCP behavior

### Performance Requirements

- [ ] 1000 parameter updates via UDP in <20 seconds (50Hz+)
- [ ] Latency <20ms for UDP parameter updates
- [ ] System tolerates <5% UDP packet loss

### Quality Requirements

- [ ] Thread safety verified (no race conditions)
- [ ] Error handling tested (TCP fallback works)
- [ ] Backward compatibility maintained
- [ ] Documentation complete

---

## References

### Pattern Sources

**TCP Thread Management:** `AbletonMCP_Remote_Script/__init__.py:79-108`
- Separate thread, daemon mode
- Socket timeout loop with `self.running` flag
- Client thread tracking and cleanup

**Command Execution:** `AbletonMCP_Remote_Script/__init__.py:214-631`
- Command routing via `self._process_command()`
- Main thread scheduling with `self.schedule_message(0, task)`
- Response queue pattern for synchronous commands

**UDP Socket Setup:** `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:160-161`
- `socket.socket(socket.AF_INET, socket.SOCK_DGRAM)`
- Simple `bind()` without `listen()`

**UDP Message Loop:** `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:171-194`
- `recvfrom(1024)` for datagrams
- Fire-and-forget processing
- Error logging without response

**Thread Safety:** `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:196-218`
- `schedule_message(0, task)` pattern
- No response queue for UDP commands
- Error handling: log only, no client notification

### Command Inventory

**Total Commands:** 85
- **TCP-Required (Critical):** ~76 commands
- **UDP-Allowed (Parameters):** 9 commands
- **Pure Read (TCP):** ~15 commands

---

**End of Architecture Design**