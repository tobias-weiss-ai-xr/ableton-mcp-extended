# AGENTS.md - Ableton MCP Extended

Control Ableton Live via AI assistants using Model Context Protocol. Dual TCP/UDP architecture.

## KEY FILES
| Task | Location |
|------|----------|
| MCP server (6411 lines) | `MCP_Server/server.py` |
| Remote Script (4706 lines) | `AbletonMCP_Remote_Script/__init__.py` |
| Entry point | `MCP_Server/__init__.py` → `ableton-mcp-extended` |
| Install | `pip install -e .` |

## ARCHITECTURE

### Dual-Server Design
| Server | Port | Protocol | Commands | Latency |
|--------|------|----------|----------|---------|
| TCP | 9877 | Request/response | 100+ commands | ~20-50ms |
| UDP | 9878 | Fire-and-forget | 10 commands | ~0.2ms |

### TCP Commands (port 9877)
All critical operations - `get_*`, `delete_*`, `create_*`, `quantize`, `undo/redo`, recording, transport.

### UDP Commands (port 9878) - ONLY these 10:
`set_device_parameter`, `set_track_volume`, `set_track_pan`, `set_track_mute`, `set_track_solo`, `set_track_arm`, `set_master_volume`, `set_send_amount`, `fire_clip`, `set_clip_launch_mode`

## CRITICAL RULES

### ANTI-PATTERNS (violations cause hard failures)
- **NEVER** use absolute parameter values - always normalize to 0.0-1.0
- **NEVER** use UDP for `get_*`, `delete_*`, `quantize`, `undo/redo`, recording
- **NEVER** create MIDI clips on audio tracks (must use `create_midi_track()` first)
- **NEVER** load empty Drum Rack - must load a kit preset with specific FileId
- **NEVER** attempt direct audio export (impossible via Remote Script API)
- **NEVER** modify LSP server configuration

### Audio Export
Remote Script cannot export audio. Use:
1. Manual export in Ableton UI (File → Export)
2. Max for Live device (`max_devices/audio_export_device.maxpat`) - must manually trigger bang inlet

## SESSION SETUP WORKFLOW

Required order when creating Ableton session from scratch:

```
1. delete_all_tracks()                    # Clean slate - remove ALL tracks first
2. create_midi_track(0), create_midi_track(1), ...  # Create MIDI tracks
3. set_track_name(0, "Drums"), ...        # Name tracks
4. load_instrument_or_effect(0, "query:Drums#FileId_58622")  # Load instruments (CRITICAL)
5. set_tempo(75)                          # Set tempo
6. create_drum_pattern(0, 0, "one_drop", 4)  # Create patterns
7. create_clip(1, 0, 4), add_notes_to_clip(1, 0, [...])  # Add MIDI notes
```

### Loading Instruments
```python
# CORRECT - specific drum kit with FileId
load_instrument_or_effect(0, "query:Drums#FileId_58622")

# WRONG - empty Drum Rack (128 unassigned pads, silent)
load_instrument_or_effect(0, "query:Drums#Drum%20Rack")
```

### Drum Pattern Variants (for `create_drum_pattern`)
| Pattern | Description | Grid |
|---------|-------------|------|
| `one_drop` | Classic dub techno - kick on 1, delayed snare | `|X---|----|--X-|----|` |
| `rockers` | Jamaican skank - kick/hat offbeat emphasis | `|X-X-|---|X-X-|---|` |
| `steppers` | Steppers rhythm - even kick distribution | `|X---|X---|X---|X---|` |
| `house_basic` | Four-on-the-floor with clap | `|X---|---|X---|---|` |
| `techno_4x4` | Driving techno - continuous kick | `|X---|X---|X---|X---|` |
| `dub_techno` | Syncopated dub - offbeat accents | `|X---|----|--X-|----|` |

## WHERE TO LOOK
| Task | Location |
|------|----------|
| Protocol handlers | `MCP_Server/server.py` |
| Tool registration | `MCP_Server/advanced_tools.py` |
| Remote Script API | `AbletonMCP_Remote_Script/__init__.py` |
| Browser cache | `MCP_Server/browser_cache.py` |
| DJ automation | `dub/enhanced_dj_performance.py`, `scripts/ultra_dj_loop.py` |
| Tests | `tests/debug/`, `tests/integration/`, `tests/test_music_theory/` |
| Test scripts | `scripts/test/test_connection.py`, `scripts/test/test_performance_udp.py` |
| Analysis tools | `scripts/analysis/` |

## RUNNING TESTS
No pytest.ini or test discovery. Tests are standalone scripts:
```bash
python scripts/test/test_connection.py          # Basic connectivity
python scripts/test/test_performance_udp.py     # UDP throughput benchmarks
python scripts/test/test_clip_firing.py         # Clip trigger verification
python scripts/util/check_session_state.py      # Session state query
```

## NOTES
- Cache dirs safe to exclude: `.pytest_cache`, `.ruff_cache`, `__pycache__`, `.sisyphus`
- `configs/analysis/*.yml` - YAML config files for audio analysis rules
- Max for Live device requires manual bang trigger - no Remote Script control