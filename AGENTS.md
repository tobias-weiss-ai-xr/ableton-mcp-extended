# AGENTS.md - Ableton MCP Extended

Control Ableton Live via AI assistants using Model Context Protocol. Dual TCP/UDP architecture.

## KEY FILES
| Task | Location | Notes |
|------|----------|-------|
| MCP server (6411 lines) | `MCP_Server/server.py` | 152 `@server.tool` decorators, 239 command functions |
| Remote Script (5867 lines) | `AbletonMCP_Remote_Script/__init__.py` | Socket server + Ableton API bridge, **now with full Arrangement View API (15+ new methods)** |
| Arrangement View (NEW) | `MCP_Server/arrangement_tools.py` (**~70KB**) | **30+ arrangement tools** - session-to-arrangement, clip editing, automation, **DUB-SPECIFIC FEATURES (filter sweeps, echo/delay, reverb, sub-bass EQ)** |
| Performance Optimized | `MCP_Server/arrangement_performance.py` (**~38KB**) | **5 optimized tools** - batch processing, caching, adaptive timing, benchmarking |
| Fat Beatz Suite (NEW) | `MCP_Server/fat_beatz_tools.py` (**~53KB**) | **15+ tools** - bass enhancement, drum fattening, stereo widening, sidechain, mastering, one-shot beat creation |
| Production Pipeline (NEW) | `scripts/production_pipeline.py` | **Complete workflow**: mix creation + MP3 conversion + video + YouTube upload (OpenMusic-style) |
| 10-Min Mix Gen (NEW) | `scripts/create_10min_mix.py`, `scripts/create_10min_mix_advanced.py`, `scripts/create_10min_mix_windows.py`, `scripts/create_10min_mix_simple.py` | Generate complete **10-minute dub × fat beatz mixes** with structured arrangement, Windows-compatible versions |
| Smart Mix Gen (NEW) | `scripts/create_smart_mix.py` | **Adaptive** mix generator that intelligently configures based on available Ableton scenes and tracks |
| Genre Mix Gen (NEW) | `scripts/genre_mix_generator_fixed.py` | **Genre-specific** mix templates (dub, hip-hop, techno, house, DnB, ambient) with authentic structure and processing |
| Polish Suite (NEW) | `scripts/polish_suite.py` | **Professional-grade** finalization: analyze, balance, stereo imaging, automation, export preparation with **genre presets** and **polish scoring** (0-100) |
| MIDI effects | `MCP_Server/midi_effects.py` | Arpeggiator, chord, scale, etc. |
| Browser cache | `MCP_Server/browser_cache.py` | SQLite persistent cache for instruments/effects |
| Entry point | `MCP_Server/__init__.py` → `ableton-mcp-extended` | `pip install -e .` |
| Voice integration | `elevenlabs_mcp/server.py` | ElevenLabs TTS MCP server |
| Server watchdog | `MCP_Server/server_watchdog.py` | Auto-restarts MCP server on crash |

Generated tool docs: `docs/TOOLS.md` (run `MCP_Server/docgen.py`)

## ARCHITECTURE

### Dual-Server Design
| Server | Port | Protocol | Commands | Latency |
|--------|------|----------|----------|---------|
| TCP | 9877 | Request/response | 100+ commands | ~20-50ms |
| UDP | 9878 | Fire-and-forget | 10 commands | ~0.2ms |

### Session-to-Arrangement Capture
Three-tier fallback approach for `capture_and_insert_arrangement`:
1. **Direct API** (Live 12+): `song.capture_to_arrangement()` if available
2. **Legacy API** (Live 10/11): `song.capture_and_insert_midi()` if available
3. **Real-time Recording Fallback** (All versions): Arms tracks, starts recording, starts playback, waits for clips to record, then stops

The fallback uses a **10-second maximum wait time** to prevent timeouts, which captures approximately 5-8 bars at typical tempos (120-140 BPM).

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

### Arrangement View Notes
- `capture_and_insert_arrangement` now WORKS in Live 12 Suite using real-time recording fallback
- `get_arrangement_clips` returns empty array instead of crashing when no clips exist
- All arrangement tools tested and functional
- Recording fallback caps at 10 seconds to prevent MCP Server timeouts

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

## STATUS: WORKING ✅
As of July 27 2026:
- ✅**Arrangement View**: Full capture, clip manipulation, automation
- ✅**Real-time Recording**: Session-to-arrangement via fallback
- ✅**MCP Tools**: 20+ arrangement tools + 15+ optimization tools registered
- ✅**Demo Scripts**: `run_basic_demo.py` completes successfully with 4 arrangement clips
- ✅**Command Format**: Fixed `run_basic_demo.py` to use `{"type": cmd}` instead of `{"command": cmd}`

## WHERE TO LOOK
| Task | Location |
|------|----------|
| Protocol handlers | `MCP_Server/server.py` |
| Tool registration | `MCP_Server/advanced_tools.py` (959 lines) |
| Remote Script API | `AbletonMCP_Remote_Script/__init__.py` |
| Browser cache | `MCP_Server/browser_cache.py` |
| MIDI effects | `MCP_Server/midi_effects.py` |
| Voice integration | `elevenlabs_mcp/server.py` |
| Server watchdog | `MCP_Server/server_watchdog.py` |
| Arrangement View | `MCP_Server/arrangement_tools.py` (51KB) |
| Mix Optimization | `MCP_Server/optimization_tools.py` (42KB) | `scripts/e2e_mix_producer.py`|
| DJ automation | `scripts/live_dj_performance.py`, `scripts/ultra_dj_loop.py`, `scripts/dub_mcp_orchestrator.py` |
| E2E Mix Production | `scripts/e2e_mix_producer.py` (48KB), `scripts/quick_arrangement_demo.py` (7KB) |
| Arrangement docs | `ARRANGEMENT_INTEGRATION.md`, `OPTIMIZATION_SUMMARY.md` |
| Tests | `scripts/test/` (18 standalone test scripts - no pytest discovery) |
| Audio analysis | `MCP_Server/audio_analysis/` |
| Config files | `configs/analysis/*.yml` |

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
