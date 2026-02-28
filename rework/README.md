# Rework Folder - Integration Analysis

**Status**: Integrated into `scripts/dub_mcp_orchestrator.py`

## Overview

This folder contains experimental dub mixing scripts that were developed using different communication protocols. They have been **superseded** by the unified `scripts/dub_mcp_orchestrator.py` which uses the MCP server's native TCP/UDP protocol.

## Protocol Mismatch (Why These Don't Work)

| File | Protocol | Port | Issue |
|------|----------|------|-------|
| `dub_mix_orchestrator.py` | HTTP | 8080 | Wrong protocol - MCP uses TCP 9877 |
| `dub_controller.py` | Raw OSC | 8000 | Wrong protocol - MCP uses custom JSON |
| `dub_mix_osc.py` | pythonosc | 8000-9001 | Wrong protocol - TouchOSC format |
| `dub_mix_udp.py` | UDP/OSC | 8000 | Wrong protocol - OSC-style messages |

**MCP Server Uses:**
- TCP port 9877 for request/response commands
- UDP port 9878 for high-frequency parameter updates
- JSON message format (not OSC)

## What Was Valuable

The **logic** in these files was good, just the **protocol layer** was incompatible:

| File | Reusable Logic |
|------|---------------|
| `dub_mix_orchestrator.py` | Scene sequencing, filter sweeps, continuous mode |
| `dub_controller.py` | DubController class structure, clip/scene triggers |
| `dub_mix_osc.py` | Multi-port discovery concept |
| `dub_mix_udp.py` | Minimal UDP pattern |

## Integration Result

All valuable logic has been extracted and integrated into:

```
scripts/dub_mcp_orchestrator.py
```

### Features Preserved

- ✅ Scene sequencing
- ✅ Filter sweeps and automation
- ✅ Continuous dub mode
- ✅ Volume dynamics
- ✅ Drop effects
- ✅ Energy curves

### Protocol Fixed

- ✅ Uses MCP TCP (port 9877) for reliable commands
- ✅ Uses MCP UDP (port 9878) for low-latency parameter updates
- ✅ JSON message format (MCP native)

## Usage

**Old (doesn't work):**
```bash
python rework/dub_mix_orchestrator.py  # HTTP on port 8080
python rework/dub_controller.py        # OSC on port 8000
```

**New (works with MCP):**
```bash
# Test connection
python scripts/dub_mcp_orchestrator.py --test

# Build new session
python scripts/dub_mcp_orchestrator.py --build

# Run continuous dub mode (infinite)
python scripts/dub_mcp_orchestrator.py

# Run 5 iterations
python scripts/dub_mcp_orchestrator.py --loop 5

# Custom tempo
python scripts/dub_mcp_orchestrator.py --tempo 90
```

## API Reference

### MCPClient Class

```python
from scripts.dub_mcp_orchestrator import MCPClient

mcp = MCPClient()
mcp.send_tcp("get_session_info")  # TCP command
mcp.send_udp("set_track_volume", {"track_index": 0, "volume": 0.8})  # UDP
```

### DubOrchestrator Class

```python
from scripts.dub_mcp_orchestrator import DubOrchestrator

orchestrator = DubOrchestrator()
orchestrator.check_connection()
orchestrator.set_tempo(75)
orchestrator.start_playback()
orchestrator.continuous_dub_mode(iterations=5)
```

## Recommendation

**Keep this folder for reference only.** The code here documents the exploration process but should not be used directly.

For active dub mixing, use:
- `scripts/dub_mcp_orchestrator.py` - Unified MCP-based orchestrator
- `scripts/bass_dub_forever.py` - Theme-based continuous dub
- `scripts/ultra_dj_loop.py` - Continuous DJ automation

## Historical Notes

These scripts were created while exploring different protocols for Ableton control:
1. First tried HTTP (port 8080) - wrong assumption about MCP server
2. Then tried OSC (port 8000) - different from MCP protocol
3. Finally discovered MCP uses custom TCP/UDP with JSON

The unified script `dub_mcp_orchestrator.py` represents the correct approach using the actual MCP protocol.
