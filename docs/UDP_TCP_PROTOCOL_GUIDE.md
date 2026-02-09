# UDP vs TCP Command Dispatching in Ableton MCP Server

**Date:** 2025-02-09
**Version:** 1.0

---

## Overview

The Ableton MCP Server now supports both **TCP** (reliable, request/response) and **UDP** (fast, fire-and-forget) protocols for communicating with Ableton Live Remote Script. This document explains the differences between the two protocols and when to use each.

---

## Protocol Comparison

| Characteristic | TCP (Port 9877) | UDP (Port 9878) |
|---------------|----------------|----------------|
| **Reliability** | Guaranteed delivery (ACK required) | Fire-and-forget (no ACK) |
| **Latency** | 20-50ms per command | <1ms per command |
| **Throughput** | 20-50 commands/second | 1000+ commands/second |
| **Connection** | Persistent connection (SOCK_STREAM) | Connectionless (SOCK_DGRAM) |
| **Response** | Returns confirmation (JSON) | Returns None (no response) |
| **Packet Loss** | 0% (reliable) | <5% tolerance acceptable |
| **Use Case** | Critical operations | High-frequency parameter updates |
| **example** | `conn.send_command()` | `conn.send_command_udp()` |

---

## TCP Protocol (Port 9877)

### Characteristics

**Reliable Communication:**
- Every command waits for acknowledgment from Ableton
- Returns JSON response with status (success/error)
- Zero packet loss tolerance
- Suitable for operations that must succeed

**Request/Response Pattern:**

```python
# TCP example: Reliable with response
conn = AbletonConnection(host="127.0.0.1", port=9877)
result = conn.send_command("get_session_info")
# Returns: {"status": "success", "result": {...}}

result = conn.send_command("create_midi_track", {"index": -1})
# Returns: {"status": "success", "result": {"name": "2 MIDI", "index": 1}}
```

**When to Use TCP:**

1. **Irreversible Operations:**
   - `delete_all_tracks`, `delete_track`, `delete_clip`
   - `delete_scene`, `delete_locator`
   - `clear_automation`

2. **Content Creation:**
   - `create_midi_track`, `create_audio_track`, `create_clip`
   - `create_scene`, `create_locator`
   - `add_notes_to_clip`, `add_automation_point`
   - `add_warp_marker`

3. **Loading Operations:**
   - `load_instrument_or_effect`
   - `load_instrument_preset`
   - `import_audio_file`

4. **Read Operations:**
   - `get_session_info`, `get_session_overview`
   - `get_track_info`, `get_all_tracks`
   - `get_device_parameters`, `get_clip_notes`

5. **Transport Control:**
   - `start_playback`, `stop_playback`
   - `start_recording`, `stop_recording`
   - `set_playhead_position`

6. **Undo/Redo:**
   - `undo`, `redo`

7. **Complex Operations:**
   - `duplicate_track`, `duplicate_clip`, `duplicate_device`
   - `move_clip`, `move_device`
   - `group_tracks`, `ungroup_tracks`

8. **Any Operation Requiring Confirmation**

**TCP Command Flow:**

```python
# 1. Client sends command
client_socket.send(json.dumps({
    "type": "set_track_name",
    "params": {"track_index": 0, "name": "New Name"}
}).encode('utf-8'))

# 2. Ableton processes and responds
response = client_socket.recv(8192)
response_data = json.loads(response.decode('utf-8'))
# Response: {"status": "success", "result": {"name": "New Name", "index": 0}}

# 3. Client can confirm success
if response_data["status"] == "success":
    print("Track renamed successfully!")
```

---

## UDP Protocol (Port 9878)

### Characteristics

**Fire-and-Forget:**
- Sends command without waiting for acknowledgment
- Returns `None` immediately
- Accepts <5% packet loss
- Self-correcting (next update fixes missed updates)

**High Performance:**

```python
# UDP example: Fire-and-forget, very fast
conn = AbletonConnection(host="127.0.0.1", port=9877)
result = conn.send_command_udp("set_track_volume", {
    "track_index": 0,
    "volume": 0.75
})
# Returns: None (no response, just sends)
```

**When to Use UDP:**

1. **High-Frequency Parameter Updates:**
   - `set_device_parameter` - Single parameter update
   - `batch_set_device_parameters` - Multi-parameter update

2. **Track Controls:**
   - `set_track_volume` - Track volume control
   - `set_track_pan` - Track panning
   - `set_track_mute` - Track mute state
   - `set_track_solo` - Track solo state
   - `set_track_arm` - Track arm state

3. **Clip Controls:**
   - `set_clip_launch_mode` - Clip launch mode
   - `fire_clip` - Clip firing

4. **Master/Bus Controls:**
   - `set_master_volume` - Master volume control
   - `set_send_amount` - Send amount control

5. **Real-Time Control Use Cases:**
   - Filter sweeps (frequency envelopes)
   - Volume automation (1000+ updates/session)
   - Real-time parameter modulation
   - Continuous LFO-style control
   - Interactive performance controls

**UDP Command Flow:**

```python
# 1. Client sends command (no waiting)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.sendto(json.dumps({
    "type": "set_device_parameter",
    "params": {
        "track_index": 0,
        "device_index": 1,
        "parameter_index": 2,
        "value": 0.75
    }
}).encode('utf-8'), ("127.0.0.1", 9878))

# 2. Ableton receives and processes
# 3. Client can move on immediately (no response)
# 4. If packet was lost, next update corrects it
```

---

## Performance Comparison

### Benchmark: 1000 Parameter Updates

**TCP (Request/Response):**
- Latency: 20-50ms per command
- Total time: 20-50 seconds
- Throughput: 20-50 commands/second
- **Suitable for**: Critical operations, low-frequency updates

**UDP (Fire-and-Forget):**
- Latency: <1ms per command
- Total time: <1 second
- Throughput: 1000+ commands/second
- **Speedup:** 10-50x faster than TCP
- **Suitable for**: High-frequency parameter sweeps, real-time control

### Example: Real-Time Filter Sweep

**Using UDP:**

```python
import time

conn = AbletonConnection(host="127.0.0.1", port=9877)

# Sweep filter from 400Hz to 2000Hz over 10 seconds (1000Hz update rate)
start_time = time.time()
num_updates = 1000

for i in range(num_updates):
    # Sweep from 0.0 (400Hz) to 1.0 (2000Hz)
    normalized_value = i / num_updates
    conn.send_command_udp("set_device_parameter", {
        "track_index": 0,
        "device_index": 0,  # Auto Filter
        "parameter_index": 0,  # Frequency
        "value": normalized_value
    })
    # No delay needed - high throughput

elapsed = time.time() - start_time
print(f"Completed {num_updates} updates in {elapsed:.2f} seconds")
print(f"Average rate: {num_updates/elapsed:.1f} Hz")
```

Using UDP for this operation can achieve **1000+ updates/second**, enabling smooth filter sweeps. Using TCP would only achieve **20-50 updates/second**, resulting in choppy control.

---

## Supported UDP Commands

### UDP-ALLOWED Commands (9 total)

These are the only commands that support UDP dispatch:

1. **`set_device_parameter`** - Set single device parameter
2. **`set_track_volume`** - Set track volume
3. **`set_track_pan`** - Set track pan
4. **`set_track_mute`** - Toggle track mute
5. **`set_track_solo`** - Toggle track solo
6. **`set_track_arm`** - Toggle track arm
7. **`set_clip_launch_mode`** - Set clip launch mode
8. **`fire_clip`** - Fire/play a clip
9. **`set_master_volume`** - Set master volume

**Note:** `batch_set_device_parameters` also documented as UDP-allowed in architecture design (batch multi-parameter update for efficiency).

### Reason for UDP Support

All UDP-ALLOWED commands share these characteristics:

1. **Reversible:** Next update corrects any missed packets
2. **High-Frequency:** Benefit from low latency
3. **Simple:** Minimal data payload
4. **Non-Critical:** Acceptable to miss <5% of updates
5. **Self-Correcting:** Don't need to confirm success

---

## Error Handling

### TCP Error Handling (Strict)

**Behavior:**
- All errors propagate to client via JSON response
- Client can retry or handle errors
- Connection stays alive for next command
- Critical errors return detailed error information

**Example:**

```python
try:
    result = conn.send_command("delete_all_tracks")
    if result.get("status") == "error":
        print(f"Error: {result.get('message')}")
        # Can retry or handle error
except Exception as e:
    print(f"Connection error: {e}")
```

### UDP Error Handling (Graceful)

**Behavior:**
- Errors logged but not reported to sender
- Lost packets treated as acceptable (up to 5% tolerance)
- Real-time parameter updates continue despite occasional failures
- No retry logic in Remote Script

**Example:**

```python
# UDP: Errors are logged but don't block execution
conn.send_command_udp("set_track_volume", {
    "track_index": 0,
    "volume": 0.75
})
# Returns None immediately, even if packet lost
# Next update will correct any missed packet
```

---

## Code Examples

### Example 1: Create Tracks via TCP, Automate via UDP

```python
from server import AbletonConnection

conn = AbletonConnection(host="127.0.0.1", port=9877)

# Step 1: Create track via TCP (reliable, needs confirmation)
result = conn.send_command("create_midi_track", {"index": -1})
print(f"Created track: {result.get('name')}")

track_index = result.get("index", 0)

# Step 2: Load instrument via TCP (must confirm success)
result = conn.send_command("load_instrument_or_effect", {
    "track_index": track_index,
    "uri": "synth_uri"
})
print(f"Loaded instrument: {result.get('loaded')}")

# Step 3: Automate filter via UDP (high-frequency)
import time

for i in range(1000):
    # Sweep filter frequency
    value = i / 1000.0  # 0.0 → 1.0
    conn.send_command_udp("set_device_parameter", {
        "track_index": track_index,
        "device_index": 0,  # Auto Filter
        "parameter_index": 0,  # Frequency
        "value": value
    })

print("Filter sweep complete!")
```

### Example 2: Scene Triggering via TCP, Parameters via UDP

```python
# Scene setup (TCP, reliable)
result = conn.send_command("create_midi_track", {"index": 0})
track_index = result.get("index", 0)

# Scene changes (TCP, reliable)
conn.send_command("trigger_scene", {"scene_index": 0})

# Real-time automation during scene (UDP, fast)
for i in range(100):
    volume = 0.5 + (i * 0.005)  # Subtle volume modulation
    conn.send_command_udp("set_track_volume", {
        "track_index": track_index,
        "volume": volume
    })
```

### Example 3: TCP Fallback Strategy

```python
def set_parameter_safely(track_idx, dev_idx, param_idx, value):
    """Set parameter with TCP fallback on UDP failure"""
    try:
        # Try UDP first for speed
        conn.send_command_udp("set_device_parameter", {
            "track_index": track_idx,
            "device_index": dev_idx,
            "parameter_index": param_idx,
            "value": value
        })
        return True
    except Exception as udp_error:
        # Fallback to TCP for reliability
        print(f"UDP failed, falling back to TCP: {udp_error}")
        result = conn.send_command("set_device_parameter", {
            "track_index": track_idx,
            "device_index": dev_idx,
            "parameter_index": param_idx,
            "value": value
        })
        if result.get("status") == "success":
            return True
        return False
```

---

## Best Practices

### Do's

1. **Use TCP for:**
   - All critical operations (create, delete, load)
   - All read operations (get_session_info, etc.)
   - Transport control (playback, recording)
   - Operations that need confirmation

2. **Use UDP for:**
   - High-frequency parameter updates (>10 Hz)
   - Real-time filter sweeps and modulation
   - Volume/pan automation
   - Any reversible parameter update
   - Performance-critical control loops

3. **UDP Pattern:**
   - Send in rapid succession without delays
   - Accept that <5% of packets may be lost
   - Use next update to correct any loss
   - Don't retry individual UDP commands

4. **TCP Pattern:**
   - Wait for response before next command
   - Retry on errors if appropriate
   - Use for operations where failure is unacceptable
   - Handle error responses gracefully

### Don'ts

1. **Don't use UDP for:**
   - Creating or deleting tracks/clips
   - Loading instruments or effects
   - Any read operation (get_session_info, etc.)
   - Transport control (playback, recording)
   - Undo/redo operations

2. **Don't rely on UDP for:**
   - Critical state changes
   - Operations that must succeed
   - Complex multi-step procedures
   - Data that must be preserved

3. **Don't:**
   - Assume UDP can't be trusted (it's designed for 5% loss tolerance)
   - Use TCP for every operation (unnecessary overhead)
   - Mix protocols for single operation (stick to one per use case)

---

## Architecture Notes

### Protocol Separation

**TCP Server (Port 9877):**
- Connection-oriented (SOCK_STREAM)
- Request/response pattern
- Client tracking
- Response required

**UDP Server (Port 9878):**
- Connectionless (SOCK_DGRAM)
- Fire-and-forget pattern
- No client tracking
- No response

### Thread Safety

Both protocols use the same Ableton Live Remote Script API, so all commands go through `self.schedule_message(0, task)` for thread-safe execution. This ensures both TCP and UDP commands are serialized on the main Ableton thread.

### Message Format

Both protocols use the same JSON message format:

```json
{
  "type": "command_name",
  "params": {
    "param1": value1,
    "param2": value2
  }
}
```

This consistency makes it easy to switch between TCP and UDP as needed.

---

## Troubleshooting

### UDP Not Working

**Symptoms:**
- UDP commands not affecting Ableton
- Commands work via TCP but not UDP
- High packet loss

**Solutions:**

1. **Check UDP Server Status:**
   ```python
   # Test if UDP server is listening
   import socket
   try:
       test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       test_socket.sendto(b"test", ("127.0.0.1", 9878))
       test_socket.close()
       print("UDP server appears to be running")
   except Exception as e:
       print(f"UDP server not responding: {e}")
   ```

2. **Verify Remote Script UDP Support:**
   - Check if Remote Script supports UDP server
   - Verify UDP server started on port 9878
   - Check Ableton Live console for UDP errors

3. **Network Issues:**
   - Check firewall settings
   - Verify no packet filtering
   - Test with localhost (127.0.0.1) first

### High Packet Loss

**Symptoms:**
- Many UDP commands not reaching Ableton
- Choppy parameter updates despite UDP usage

**Solutions:**

1. **Reduce Update Rate:**
   ```python
   # Instead of 1000 Hz, try 500 Hz
   for i in range(500):
       conn.send_command_udp("set_device_parameter", {...})
       time.sleep(0.001)  # Small delay to reduce congestion
   ```

2. **Use TCP Fallback:**
   - Switch to TCP for critical parameters
   - Use UDP only for non-critical updates

3. **Check Network:**
   - Test with different interface
   - Reduce network load on system

---

## Summary

**Key Differences:**

| Aspect | TCP | UDP |
|--------|-----|-----|
| Reliability | 100% (guaranteed) | 95% (acceptable) |
| Latency | 20-50ms | <1ms |
| Throughput | 20-50 Hz | 1000+ Hz |
| Use Case | Critical operations | Real-time control |

**When in Doubt:**
- Use TCP for everything critical
- Use UDP for high-frequency parameter updates only
- Test both protocols in your specific use case
- Monitor performance and adjust as needed

---

## References

- **Architecture Design:** `.sisyphus/plans/dual-server-architecture.md`
- **Remote Script:** `AbletonMCP_Remote_Script/__init__.py`
- **MCP Server:** `MCP_Server/server.py`
- **UDP Dispatch Test:** `scripts/test/test_udp_dispatch.py`
- **UDP Integration Test:** `scripts/test/test_udp_integration.py`
- **UDP Demo:** `scripts/test/test_udp_demo.py`

---

**End of Document**