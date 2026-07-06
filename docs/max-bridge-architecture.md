# Max Bridge Architecture

> **Status:** Prototype / Design Document
> **Scope:** OSC-based bridge between ableton-mcp-extended and Max for Live

---

## 1. Overview

The **Max Bridge** provides a bidirectional communication channel between the ableton-mcp-extended MCP server and Max for Live patchers running inside Ableton Live. It bridges the gap left by the Remote Script API — which cannot send commands **into** Max devices — by using Open Sound Control (OSC) over UDP as the transport layer.

### Why a Bridge Is Needed

The existing `AbletonMCP_Remote_Script` (`AbletonMCP_Remote_Script/__init__.py`) communicates with Ableton Live via the Live Object Model (LOM) exposed through the Remote Script API. While this provides extensive control over tracks, clips, devices, and transport, it has a **critical blind spot**:

| Direction | Supported? | Mechanism |
|-----------|-----------|-----------|
| MCP → Remote Script → Live API | ✅ Yes | TCP port 9877 |
| Live → Remote Script → MCP | ✅ Yes | TCP response |
| MCP → Max for Live device | ❌ **No** | No Remote Script → Max path |
| Max for Live device → MCP | ⚠️ Partial | Via Live API `observer` + OSC sender in Max |

The Max Bridge solves the **unidirectional gap** by placing a lightweight OSC relay in the Max patcher that listens on a dedicated UDP port and forwards messages to the Max device's inlets using `receive` objects.

---

## 2. Communication Protocol: OSC (Recommended)

### Why OSC over Alternatives

| Approach | Latency | Bidirectional | Reliability | Complexity | Eval |
|----------|---------|---------------|-------------|------------|------|
| **OSC (python-osc)** | ~1-5ms | ✓ | ✓ ack-on-change | Low | **Best fit** |
| Named Pipes (FIFO) | ~0.5ms | ✓ | ✓ blocking I/O | High | Over-engineered |
| Raw UDP (JSON) | ~0.2ms | △ one-way | ✗ fire-and-forget | Low | Lost messages |
| Live API observer | ~10-50ms | △ one-way | ✓ reliable | Medium | Cant send to Max |

**OSC wins** because:
- python-osc is a pure-Python library, zero native dependencies
- OSC is natively understood by Max (`udpreceive` / `udpsend` objects)
- Structured message format (address pattern + typed arguments) avoids parsing bugs
- UDP transport keeps latency low (~1-5ms localhost round-trip)
- Max patcher can both **receive** and **send** OSC, enabling bidirectional flow

### python-osc Details

- **Library:** [python-osc](https://pypi.org/project/python-osc/) (BSD license)
- **Install:** `pip install python-osc`
- **Usage:** `from pythonosc.udp_client import SimpleUDPClient`
- **Fallback:** `MaxBridgeClient` works without python-osc; sends are no-ops with a logged warning

### Port Allocation

| Service | Port | Protocol | Direction |
|---------|------|----------|-----------|
| MCP → Remote Script | 9877 | TCP | Request/response |
| Remote Script → MCP | 9877 | TCP | Response |
| MCP → Max Bridge (OSC) | 9000 | UDP | Fire-and-forget |
| Max Bridge → MCP (OSC) | 9001 | UDP | Event/message |
| Remote Script → Max Bridge | 9002 | UDP (future) | Parameter sync |

**Port 9000** is the default for the Max bridge OSC sender. It is configurable via the `MAX_BRIDGE_PORT` environment variable or `max_bridge_port` parameter in `MaxBridgeClient`.

---

## 3. Security Model

### Localhost-Only Binding

The OSC server and client bind **exclusively** to `127.0.0.1` (localhost). No external network access.

```
MaxBridgeClient(host="127.0.0.1", port=9000)
```

The Max patcher's `udpreceive` must also bind to `127.0.0.1` — not `0.0.0.0` — to prevent external actors from sending OSC to the bridge.

### Configurable Port

Users can override the port via environment variable:

```bash
export MAX_BRIDGE_PORT=9000
```

Port values are validated at construction time (1024–65535, to avoid privileged ports).

### Command Allowlist

The bridge maintains an **explicit allowlist** of OSC address patterns that the MCP server is permitted to send. Any address not on the allowlist is silently dropped. The allowlist is defined in `MaxBridgeClient.ALLOWED_ADDRESSES`.

Default allowlist:
- `/max/device/load` — Load a Max for Live device onto a track
- `/max/device/info` — Query device metadata
- `/max/device/message` — Send a message to a device inlet
- `/max/device/parameter` — Set a device parameter
- `/max/open` — Open a patcher window in Max
- `/max/presentation` — Toggle presentation mode
- `/max/ping` — Health check (used by `test_max_bridge`)
- `/max/bang` — Trigger a bang on a device inlet

### Authentication

Not required. The bridge is localhost-only and the allowlist provides sufficient protection. Adding authentication would introduce key-management overhead with no practical benefit for a local-only connection.

---

## 4. Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MCP Client (AI Assistant)                       │
│  send_max_message(track=0, device=0, message="bang")                │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ MCP (stdin/stdio or SSE)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  ableton-mcp-extended (server.py)                     │
│                                                                      │
│  ┌──────────────────────────────────────────────┐                    │
│  │           max_bridge.py                       │                   │
│  │  MaxBridgeClient.send_osc("/max/device/       │                   │
│  │    message", [0, 0, "bang"])                  │                   │
│  │                                              │                   │
│  │  Uses: pythonosc.udp_client.SimpleUDPClient  │                   │
│  │  Sends to: 127.0.0.1:9000                    │                   │
│  └──────────────────────┬───────────────────────┘                    │
│                         │                                            │
│  ┌──────────────────────┴───────────────────────┐                    │
│  │          TCP Remote Script                    │                    │
│  │  (AbletonMCP_Remote_Script/__init__.py)       │                    │
│  │  For comparison: TCP→UDP hybrid is not used  │                    │
│  │  here — OSC goes directly to Max.            │                    │
│  └──────────────────────────────────────────────┘                    │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ OSC over UDP (127.0.0.1:9000)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Max for Live Runtime                             │
│                                                                      │
│  ┌──────────────────────────────────────────────┐                    │
│  │       mcp_bridge.maxpat  (relay patcher)      │                   │
│  │                                               │                   │
│  │  [udpreceive 9000] → [route /max] → [select]  │                   │
│  │       │                                        │                   │
│  │       ├── /max/device/message → [send devmsg]  │                   │
│  │       ├── /max/bang          → [send bang]     │                   │
│  │       ├── /max/ping          → [send pong]     │                   │
│  │       └── ...                                  │                   │
│  │                                               │                   │
│  │  Forwarded via [send] / [receive] to:         │                   │
│  └──────────────────────┬───────────────────────┘                    │
│                         │                                            │
│  ┌──────────────────────┴───────────────────────┐                    │
│  │        Target Max for Live Device              │                   │
│  │  (e.g., audio_export_device.maxpat)            │                   │
│  │  Receives bangs, messages, parameters         │                   │
│  └──────────────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step (send_max_message example)

1. AI assistant calls `send_max_message(track_index=0, device_index=0, message="bang")`
2. `max_bridge.py` forms OSC address `/max/device/message` with args `[0, 0, "bang"]`
3. OSC client on `127.0.0.1:9000` sends the message (fire-and-forget UDP)
4. `mcp_bridge.maxpat` receives via `udpreceive 9000`
5. `route /max` splits the address
6. `select device/message` matches and forwards to `[send devmsg]`
7. Target Max device receives via `[receive devmsg]` and processes

### Return Path (Max → MCP)

For events originating in Max (parameter changes, notifications):

1. Max device sends OSC via `[udpsend 127.0.0.1 9001]` with address `/max/event`
2. A future `MaxBridgeListener` (UDP server on port 9001) receives the event
3. Event is logged and optionally reported to the MCP client

The return path is **future work** and is not implemented in the prototype.

---

## 5. Required Max Patcher: `max_devices/mcp_bridge.maxpat`

### Purpose

`mcp_bridge.maxpat` is a lightweight **OSC-to-Max relay** that runs inside Ableton Live as a Max for Live device. It must be loaded on a track (or the master) for the Max Bridge to function.

### OSC Address Map

| OSC Address | Arguments | Max Action |
|-------------|-----------|------------|
| `/max/ping` | `int id` | Bounces the ping — sends `/pong` with same id |
| `/max/device/load` | `int track, string query` | Loads a Max device by browser query |
| `/max/device/info` | `int track, int device` | Prints device info to Max console |
| `/max/device/message` | `int track, int device, string message` | Sends a message to the device stdin inlet |
| `/max/device/parameter` | `int track, int device, int param, float value` | Sets a device parameter |
| `/max/bang` | `int track, int device` | Sends a bang to device inlet 0 |
| `/max/open` | `int track, int device` | Opens the device patcher window |
| `/max/presentation` | `int track, int device` | Toggles presentation mode |

### Max patcher file

**File:** `max_devices/mcp_bridge.maxpat`

The file is a standard `.maxpat` JSON/XML document. See the file itself for the concrete implementation.

### Installation

1. Copy `max_devices/mcp_bridge.maxpat` to Ableton's Max for Live Devices folder
2. Load it onto the master track (recommended) or any audio/MIDI track
3. The bridge will start listening on UDP port 9000 automatically

---

## 6. Planned Tool Surface

| MCP Tool | Description | Parameters | Status |
|----------|-------------|------------|--------|
| `test_max_bridge` | Ping the OSC endpoint to verify connectivity | `port` (optional, default 9000) | ✅ **Prototype** |
| `send_max_message` | Send a raw message to a Max device inlet | `track_index`, `device_index`, `message` | 🔲 Planned |
| `load_max_device` | Load a Max for Live device onto a track | `track_index`, `device_name` (browser query) | 🔲 Planned |
| `get_max_device_info` | Query Max device metadata | `track_index`, `device_index` | 🔲 Planned |
| `open_in_max` | Open a Max device's patcher window | `track_index`, `device_index` | 🔲 Planned |
| `toggle_presentation` | Toggle Max device presentation mode | `track_index`, `device_index` | 🔲 Planned |

The full tool surface is **not implemented** in the prototype. Only `test_max_bridge` is provided.

---

## 7. Capabilities Unlocked

The Max Bridge opens capabilities that are **impossible or impractical** via the Remote Script API alone:

### Audio Rendering
- Real-time audio capture via `sfrecord~` (as in `audio_export_device.maxpat`)
- Multi-track stem export
- Custom fade-in/out, crossfade logic
- Audio file manipulation (trim, normalize, reverse)

### Custom Device Creation
- Dynamic device parameter mapping
- Custom signal chains with `gen~` patches
- Real-time audio analysis (pitch tracking, onset detection)
- Spectral processing (fft~, pfft~)

### Signal Processing
- Custom DSP algorithms in `gen~`
- Multi-band compression with user-defined crossover
- Convolution reverb with custom IRs
- Granular synthesis and time-stretching

### UI Manipulation
- Toggle presentation mode dynamically
- Resize and reposition Max windows
- Expose device parameters as named controls
- Create custom automation lanes

### Hybrid MCP + Max Workflows

```
┌─────────────────────────────────────────────────────────────────┐
│                    New Hybrid Capabilities                       │
├─────────────────────────────────────────────────────────────────┤
│  MCP sets up session → Max Bridge triggers export →             │
│  Audio file appears on disk → MCP continues processing          │
├─────────────────────────────────────────────────────────────────┤
│  MCP selects parameters → Max Bridge updates DSP →              │
│  Real-time audio processing applies immediately                 │
├─────────────────────────────────────────────────────────────────┤
│  MCP fires clips → Max Bridge captures output →                │
│  Captured audio loaded into new session track                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Reference: Existing Projects

### AbletonOSC

[AbletonOSC](https://github.com/ideoforms/AbletonOSC) is an established project that exposes Ableton Live's LOM via OSC. Its architecture:

- Python bridge script running inside Max for Live via `js` object
- Exposes Live API methods as OSC address patterns
- Fully bidirectional: OSC → Live API and Live API → OSC

**Key insights for Max Bridge:**
- The `js` object approach (embedding Python in Max) is powerful but fragile — it ties the bridge to Max's internal Python runtime
- OSC → `route` → `select` → `receive` pattern is the idiomatic Max way to dispatch messages
- AbletonOSC uses port **11000** by default; our bridge uses **9000** to avoid conflicts

### livemcp

[livemcp](https://github.com/2KAbhishek/livemcp) is an MCP server for Ableton Live that uses a combined approach:

- Max for Live device with `js` for Live API access
- WebSocket for MCP communication
- Custom patcher exposing device control endpoints

**Key insights for Max Bridge:**
- livemcp's Max bridge uses a similar `udpreceive` + `route` pattern
- WebSocket transport adds complexity; OSC/UDP is simpler for a local-only bridge
- livemcp embeds all logic in a single `.amxd` device; our design separates the relay (`mcp_bridge.maxpat`) from target devices

### audio_export_device.maxpat (Existing)

This project already ships a Max for Live device at `max_devices/audio_export_device.maxpat`. It provides:

- Audio recording via `sfrecord~`
- Format selection (WAV/AIFF/OGG/FLAC)
- Sample rate and bit depth control
- Manual bang inlet for recording toggle

**Limitation:** It cannot be controlled from Remote Scripts (see `max_devices/README.md`). The Max Bridge solves this by allowing OSC-triggered bangs and messages to reach the device.

To use `audio_export_device.maxpat` with the Max Bridge:

1. Load both `mcp_bridge.maxpat` and `audio_export_device.maxpat` on tracks
2. Bridge relays OSC → sends bangs to named `receive` objects
3. `audio_export_device.maxpat` needs a `[receive bridge_bang]` object connected to its bang inlet

---

## 9. Failure Modes

| Failure | Symptom | Cause | Resolution |
|---------|---------|-------|------------|
| python-osc not installed | "Install python-osc to use Max bridge" error | Missing `pip install python-osc` | Install the package |
| Max patcher not loaded | No response to OSC pings | Bridge not loaded in Ableton | Load `mcp_bridge.maxpat` on a track |
| Port conflict | Connection refused on port 9000 | Another app using the port | Set `MAX_BRIDGE_PORT` to a different value |
| Firewall blocking | UDP packets silently dropped | Local firewall rules | Allow UDP on 127.0.0.1:9000 |
| Max device not found | OSC message sent but no effect | `receive` name mismatch | Verify `[receive]` name in target device |
| UDP packet loss | Intermittent missed messages | Congested system | Retry or increase send interval |

### Graceful Degradation

The `MaxBridgeClient` is designed for graceful degradation:

- **python-osc missing:** All `send_osc` calls become no-ops, logging a warning. The `test_max_bridge` tool reports the bridge as unreachable with a clear install hint.
- **Max patcher not running:** OSC packets are sent to a silent port. No error on the sender side. `test_max_bridge` will report a timeout.
- **Partial allowlist match:** Unknown OSC addresses are rejected with a log message at `DEBUG` level before any network activity.

---

## 10. Security Implications

| Concern | Mitigation |
|---------|-----------|
| External network access to OSC | Bind to `127.0.0.1` only, never `0.0.0.0` |
| Unauthorized commands | Command allowlist in Python + `route` filter in Max |
| Privilege escalation | No privileged operations exposed via OSC |
| Information disclosure | Allowlist prevents reading arbitrary device state |
| Denial of service | UDP is fire-and-forget; Max `udpreceive` has internal buffer limits |

### Recommended Setup for Production Use

1. Set a non-default OSC port per session
2. Load `mcp_bridge.maxpat` on a dedicated utility track (not an instrument track)
3. Keep `audio_export_device.maxpat` and similar devices separate from the bridge

---

## 11. Future Work

- **Bidirectional OSC listener** on port 9001 — allows Max to push events back to MCP
- **Parameter sync** — Remote Script forwards parameter changes to Max via OSC
- **Device discovery** — Auto-detect Max for Live devices loaded in the session
- **Preset management** — Load/save Max device presets via OSC
- **Error reporting** — Max patcher sends error messages back on `/max/error`

---

## Appendix: Quick Start

```bash
# 1. Install python-osc
pip install python-osc

# 2. Copy bridge patcher to Ableton
cp max_devices/mcp_bridge.maxpat ~/Music/Ableton/User\ Library/Packs/

# 3. In Ableton Live:
#    - Load mcp_bridge.maxpat on master track
#    - Optionally load audio_export_device.maxpat on a track

# 4. Verify connectivity
python -c "
from MCP_Server.max_bridge import MaxBridgeClient
client = MaxBridgeClient()
print(client.ping())  # Should print True/False
"

# 5. Use MCP tools (once connected)
# test_max_bridge()
```

---

*Last updated: July 2026*
*Compatible with Ableton Live 11+, Max for Live, Python 3.10+*
