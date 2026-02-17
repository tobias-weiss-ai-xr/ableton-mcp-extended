# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-13 05:28:00
**Commit:** 30c5aa1
**Branch:** main

## OVERVIEW
Control Ableton Live via AI assistants using Model Context Protocol. Python-based MCP server with dual TCP/UDP architecture for real-time control and ElevenLabs voice integration.

## STRUCTURE
```
./
├── MCP_Server/              # Core MCP server (108 TCP + 9 UDP commands)
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
- **Dual TCP/UDP architecture**: 108 TCP commands (request/response) vs 9 UDP commands (fire-and-forget for real-time control)
- **High-performance UDP**: Ultra-low latency (~0.2ms avg, 1.5ms P99), 1386+ Hz throughput for parameter sweeps
- **Manual audio export workflow**: Remote Script can't export audio → requires manual export in Ableton UI or Max for Live device
- **Project-specific UDP eligibility**: 9 commands pre-approved for UDP (set_device_parameter, set_track_*, set_clip_launch_mode, fire_clip, set_master_volume)
- **2-hour automation patterns**: dub_techno_2h uses timer-based scene progression, filter automation, section-based volume changes

## MUSIC THEORY & PERFORMANCE TOOLS (21 Commands)

### Constants
- **CAMELOT_WHEEL**: 24-key mapping for harmonic mixing (Camelot notation)
- **CHORD_INTERVALS**: 12 chord types (major, minor, dim, aug, maj7, min7, dom7, dim7, sus2, sus4, add9, power)
- **SCALE_INTERVALS**: 9 scale types (major, minor, dorian, phrygian, lydian, mixolydian, pentatonic_major, pentatonic_minor, blues)
- **DRUM_PATTERNS**: 6 genre patterns (one_drop, rockers, steppers, house_basic, techno_4x4, dub_techno)

### Harmonic Mixing (2)
- `get_compatible_keys(key)`: Get harmonically compatible keys for DJ transitions
- `suggest_key_transition(from_key, to_key)`: Suggest smooth key transition path

### Scale & Key (3)
- `detect_clip_key(track_index, clip_index)`: Analyze clip notes to detect musical key
- `snap_notes_to_scale(track_index, clip_index, key, scale)`: Quantize notes to scale
- `create_scale_reference_clip(track_index, clip_index, key, scale)`: Create reference clip with scale notes

### Chord Operations (2)
- `create_chord_notes(root_pitch, chord_type)`: Generate chord note intervals
- `create_chord_progression(track_index, clip_index, key, progression_type)`: Build chord progressions

### Batch Operations (3)
- `batch_transpose_clips(transpositions)`: Transpose multiple clips at once
- `transpose_all_playing_clips(semitones)`: Live transpose during performance
- `fire_scene_with_transpose(scene_index, semitones)`: Fire scene with key shift

### Performance Patterns (3)
- `apply_filter_buildup(track_index, device_index, start_freq, end_freq, duration_beats)`: Rising filter sweep
- `apply_drop(track_index, device_index, duration_beats)`: Drop energy transition
- `apply_energy_curve(track_index, device_index, curve_type, duration_beats)`: Apply energy envelope

### Global Settings (5)
- `get_global_quantization()`: Get current quantization setting
- `set_global_quantization(quantization)`: Set global quantization
- `get_link_status()`: Check Ableton Link connection status
- `set_link_enabled(enabled)`: Enable/disable Ableton Link
- `set_link_start_stop_sync(enabled)`: Configure Link start/stop sync

### Rhythm Helpers (1)
- `create_drum_pattern(track_index, clip_index, pattern_name, length)`: Generate genre-specific drum patterns

## NOTES
- **Max for Live device**: Required for audio export, but must be manually triggered (bang inlet) - no Remote Script control
- **Ableton Remote Script limitations**: Cannot export/save audio files, cannot trigger export dialog
- **Dual-server performance**: UDP is 100-250x faster than TCP for parameter updates, but TCP is required for 30 critical operations
- **Cache directories**: .pytest_cache, .ruff_cache, __pycache__, .sisyphus - can be safely excluded from analysis
- **Large files**: MCP_Server/server.py (4,234 lines), AbletonMCP_Remote_Script/__init__.py (3,622 lines)