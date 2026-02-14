# MCP_Server AGENTS.md

**Core protocol implementation** (score 12)

## WHERE TO LOOK
| Task                | Location                     |
|---------------------|------------------------------|
| Protocol handlers   | server.py                    |
| Tool registration   | advanced_tools.py            |
| Device management   | new_device_methods.py        |

## CONVENTIONS
- Agent protocol handlers use normalized values (0.0-1.0)
- Error recovery continues execution despite failures
- Parameter indices used instead of names

## ANTI-PATTERNS
- NEVER use absolute parameter values (always normalized)
- NEVER modify LSP server configuration
- NEVER use UDP for critical operations (get_*, delete_*, quantize, undo/redo)

## DUAL-SERVER ARCHITECTURE

| Server | Port | Pattern | Use Case |
|--------|------|---------|----------|
| TCP | 9877 | Request/response | Reliable operations, feedback required |
| UDP | 9878 | Fire-and-forget | High-frequency parameter updates |

### Protocol Patterns

**TCP (Port 9877)**: All operations requiring reliability
- Creating tracks, clips, scenes
- Loading instruments/effects
- Getting session/track/device info
- Transport control (play, stop, record)
- All `get_*`, `delete_*`, `quantize_*`, `undo`, `redo`

**UDP (Port 9878)**: High-frequency reversible operations
- Ultra-low latency (~0.2ms avg, 1.5ms P99)
- 290x faster than TCP for parameter sweeps
- Throughput: 1386+ Hz
- Packet loss tolerance (<5% acceptable)

## UDP-ALLOWED COMMANDS (10 commands)

These commands are pre-approved for UDP due to reversible nature:

| Command | Purpose |
|---------|---------|
| `set_device_parameter` | Update device parameters in real-time |
| `set_track_volume` | Track volume control |
| `set_track_pan` | Track panning |
| `set_track_mute` | Track mute state |
| `set_track_solo` | Track solo state |
| `set_track_arm` | Track arm state (recording) |
| `set_master_volume` | Master volume control |
| `set_send_amount` | Send level to return tracks |
| `fire_clip` | Trigger clip playback |
| `set_clip_launch_mode` | Clip launch mode (Trigger/Gate/Toggle/Repeat) |

### UDP Usage Rules

1. Only use UDP for the 10 allowed commands
2. Never send `get_*`, `delete_*`, or critical operations via UDP
3. Accept occasional packet loss (<5%)
4. Next parameter update corrects missed packets