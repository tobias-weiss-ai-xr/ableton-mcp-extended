# SCRIPTS KNOWLEDGE

**Parent:** ../AGENTS.md
**Purpose:** Utilities, test scripts, and helper functions

## OVERVIEW
## OVERVIEW
Organized utilities for testing, analysis, and common operations. Python files across 4 main subdirectories plus performance scripts.

## STRUCTURE
```
scripts/
├── test/                    # Test scripts
│   ├── test_connection.py
│   ├── test_clip_firing.py
│   ├── test_playback_1min.py
│   ├── test_session_integration.py
│   ├── test_performance_udp.py
│   ├── test_device_presets.py
│   └── ...
├── util/                     # Utility functions
│   ├── check_session_state.py
│   ├── check_tracks.py
│   ├── create_percussion.py
│   ├── get_effects.py
│   ├── record_dub_song_automated.py
│   └── ...
├── analysis/                # Analysis tools
│   └── benchmark.py
├── test_analysis/           # Test analysis utilities
├── live_dj_performance.py   # Real-time DJ with audio analysis
├── live_dj_bass_heavy.py    # Bass-heavy DJ performance
├── ultra_dj_loop.py         # Continuous DJ automation loop
├── bass_dub_forever.py      # Theme-based continuous dub mixer
└── dub_mcp_orchestrator.py  # Unified dub orchestrator (MCP protocol)
```
```
scripts/
├── test/                    # Test scripts
│   ├── test_connection.py
│   ├── test_clip_firing.py
│   ├── test_playback_1min.py
│   ├── test_session_integration.py
│   ├── test_performance_udp.py
│   ├── test_device_presets.py
│   └── ...
├── util/                     # Utility functions
│   ├── check_session_state.py
│   ├── check_tracks.py
│   ├── create_percussion.py
│   ├── get_effects.py
│   ├── record_dub_song_automated.py
│   └── ...
├── analysis/                # Analysis tools
│   └── benchmark.py
└── test_analysis/           # Test analysis utilities
```

## WHERE TO LOOK
| Task                    | Location              |
|-------------------------|-----------------------|
| Session utilities      | util/check_*.py      |
| Track utilities        | util/check_tracks.py   |
| Recording utilities     | util/record_*.py      |
| Test integration       | test/test_*.py        |
| Performance testing    | test/test_performance_udp.py |
| **DJ performance**     | live_dj_*.py, ultra_dj_loop.py |
| **Dub orchestration**  | dub_mcp_orchestrator.py |
| Task                    | Location              |
|-------------------------|-----------------------|
| Session utilities      | util/check_*.py      |
| Track utilities        | util/check_tracks.py   |
| Recording utilities     | util/record_*.py      |
| Test integration       | test/test_*.py        |
| Performance testing    | test/test_performance_udp.py |

## KEY UTILITIES
- **check_session_state.py**: Verify Ableton connection and session state
- **check_tracks.py**: Query track information, verify track counts
- **record_dub_song_automated.py**: Auto-record dub songs with automation
- **create_percussion.py**: Generate percussion patterns
- **live_dj_performance.py**: Real-time DJ with audio analysis (RMS via Voicemeeter)
- **ultra_dj_loop.py**: Continuous DJ automation with 7 patterns
- **dub_mcp_orchestrator.py**: Unified dub controller using MCP TCP/UDP protocol
- **check_session_state.py**: Verify Ableton connection and session state
- **check_tracks.py**: Query track information, verify track counts
- **record_dub_song_automated.py**: Auto-record dub songs with automation
- **create_percussion.py**: Generate percussion patterns

## CONVENTIONS
- **Socket-based communication**: Connect to TCP server (localhost:9877) or UDP (localhost:9878)
- **Test isolation**: Each test script is self-contained
- **Performance testing**: test_performance_udp.py measures UDP throughput and latency

## TEST SCRIPTS
- **test_connection.py**: Basic TCP/UDP connection tests
- **test_clip_firing.py**: Verify clip playback triggers
- **test_playback_1min.py**: Play for 1 minute, verify state
- **test_session_integration.py**: Full session control flow test
- **test_performance_udp.py**: 1000-command load test, latency benchmarks
- **test_device_presets.py**: Preset loading and management

## ANTI-PATTERNS
- DO NOT assume server is running → always check connection first
- DO NOT modify Ableton session unexpectedly → tests should be idempotent
- DO NOT leave tracks playing after tests → always stop playback

## USAGE PATTERNS
```python
# Typical test script structure
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9877))
command = {'type': 'get_session_info', 'params': {}}
sock.send(json.dumps(command).encode('utf-8'))
response = json.loads(sock.recv(8192).decode('utf-8'))
print(response)
sock.close()
```

## PERFORMANCE METRICS (from test_performance_udp.py)
- UDP throughput: 4536.1 Hz (1000 commands / 220.43ms)
- Average latency: 0.20ms
- P99 latency: 1.50ms
- Baseline speedup vs TCP: 582.8x faster


## DJ PERFORMANCE SCRIPTS
- **live_dj_performance.py**: Real-time DJ with RMS audio analysis
  - Uses AudioAnalyzer with device 109 (Voicemeeter Out 6)
  - Pattern-based clip triggering
  - Filter sweeps and volume automation
- **live_dj_bass_heavy.py**: Bass-heavy variant with sub-bass emphasis
- **ultra_dj_loop.py**: Continuous loop with 7 automation patterns
- **bass_dub_forever.py**: Theme-based continuous dub mixer
- **dub_mcp_orchestrator.py**: Unified dub controller (MCP protocol)
  - Replaces rework/ folder scripts (HTTP/OSC protocols)
  - Uses TCP 9877 for reliable commands
  - Uses UDP 9878 for low-latency parameter updates
  - Classes: MCPClient, DubOrchestrator

## USAGE EXAMPLES
```bash
# Test MCP connection
python scripts/dub_mcp_orchestrator.py --test

# Run continuous dub mode (infinite)
python scripts/dub_mcp_orchestrator.py

# Run 5 iterations at 90 BPM
python scripts/dub_mcp_orchestrator.py --loop 5 --tempo 90

# Run live DJ with real-time audio analysis
python scripts/live_dj_performance.py
```
