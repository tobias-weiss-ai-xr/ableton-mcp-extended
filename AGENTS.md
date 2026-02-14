# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-13 05:28:00
**Commit:** 30c5aa1
**Branch:** main

## OVERVIEW
Control Ableton Live via AI assistants using Model Context Protocol. Python-based MCP server with dual TCP/UDP architecture for real-time control and ElevenLabs voice integration.

## STRUCTURE
```
./
├── MCP_Server/              # Core MCP server (76 TCP + 9 UDP commands)
├── AbletonMCP_Remote_Script/ # Ableton Remote Script (socket server)
├── dub_techno_2h/           # 2-hour automation project
├── scripts/                  # Utilities and tests
├── tests/                     # Test suite
├── elevenlabs_mcp/            # Voice generation integration
└── max_devices/               # Max for Live audio export device
```

## WHERE TO LOOK
| Task                  | Location                         |
|-----------------------|----------------------------------|
| Protocol handlers      | MCP_Server/server.py              |
| Remote Script API    | AbletonMCP_Remote_Script/__init__.py |
| Automation scripts    | dub_techno_2h/                 |
| Test utilities       | scripts/ (test/, util/, analysis/) |
| Integration tests     | tests/integration/                  |
| Voice generation      | elevenlabs_mcp/                   |
| Audio export          | max_devices/                      |

## CONVENTIONS
- **Parameter normalization**: All device/track parameters use 0.0-1.0 normalized values
- **Dual-server architecture**: TCP (port 9877) for reliable operations, UDP (port 9878) for high-frequency parameter updates
- **NEVER-UDP protocol**: 30 critical operations (get_*, delete_*, quantize, mix, crop, undo/redo, recording) MUST use TCP only
- **Telegraphic documentation**: Sectioned by functional domain, minimal verbosity
- **pyproject.toml**: Modern Python packaging with setuptools build backend
- **Entry points**: MCP_Server/__init__.py (main), AbletonMCP_Remote_Script/__init__.py

## ANTI-PATTERNS (THIS PROJECT)
- NEVER attempt direct audio export (fundamentally impossible via Remote Script API)
- NEVER modify Ableton's Remote Script API
- NEVER use absolute parameter values (always normalize to 0.0-1.0)
- NEVER use UDP for Category D operations (30 critical commands: all get_*, delete_*, quantize, mix, crop, undo/redo, recording, heavy operations)
- NEVER modify LSP server configuration

## UNIQUE STYLES
- **Dual TCP/UDP architecture**: 76 TCP commands (request/response) vs 9 UDP commands (fire-and-forget for real-time control)
- **High-performance UDP**: Ultra-low latency (~0.2ms avg, 1.5ms P99), 1386+ Hz throughput for parameter sweeps
- **Manual audio export workflow**: Remote Script can't export audio → requires manual export in Ableton UI or Max for Live device
- **Project-specific UDP eligibility**: 9 commands pre-approved for UDP (set_device_parameter, set_track_*, set_clip_launch_mode, fire_clip, set_master_volume)
- **2-hour automation patterns**: dub_techno_2h uses timer-based scene progression, filter automation, section-based volume changes

## COMMANDS
```bash
# Install and run MCP server
pip install -e .
python MCP_Server/server.py

# Run 2-hour automation
cd dub_techno_2h
python create_2h_dub_techno_fixed.py
python load_instruments_and_effects.py
python auto_play_2h_dub_techno.py

# Run tests
pytest tests/
```

## NOTES
- **Max for Live device**: Required for audio export, but must be manually triggered (bang inlet) - no Remote Script control
- **Ableton Remote Script limitations**: Cannot export/save audio files, cannot trigger export dialog
- **Dual-server performance**: UDP is 100-250x faster than TCP for parameter updates, but TCP is required for 30 critical operations
- **Cache directories**: .pytest_cache, .ruff_cache, __pycache__, .sisyphus - can be safely excluded from analysis
- **Large files**: MCP_Server/server.py (4,234 lines), AbletonMCP_Remote_Script/__init__.py (3,622 lines)