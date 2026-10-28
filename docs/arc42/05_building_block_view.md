# 5. Building Block View

## 5.1 Level 0 — System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ableton-mcp-extended                             │
│                                                                         │
│  ┌──────────────┐   ┌───────────────┐   ┌───────────────────────────┐  │
│  │  MCP_Server  │   │ elevenlabs_mcp│   │       agentic_mix         │  │
│  │  (core DAW)  │   │  (voice/SFX)  │   │   (generative pipeline)   │  │
│  └──────┬───────┘   └───────┬───────┘   └────────────┬──────────────┘  │
│         │                   │                        │                  │
│         │ TCP/UDP           │ HTTPS                  │ tool calls       │
│         ▼                   ▼                        ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              AbletonMCP_Remote_Script  (inside Live)             │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  ▼
                          Ableton Live 12
```

## 5.2 Level 1 — `MCP_Server` Module Map

`MCP_Server/server.py` is the FastMCP host. Tool domains live in sibling modules
and register themselves at import time via `register_*(mcp, get_ableton_connection)`.

| Module | Tools | Responsibility |
|--------|------:|----------------|
| `server.py` | ~120 | Core: connection, transport, session/track/clip/scene/transport/browser, recording |
| `advanced_tools.py` | ~56 | Generation: drum patterns, chord progressions, melodies, generative chains, follow actions |
| `midi_effects.py` | 25 | MIDI effect presets (arp, chord, scale, velocity, pitch, random) |
| `arrangement_tools.py` | 5 | Arrangement view: capture, clip editing, automation |
| `arrangement_performance.py` | 6 | Batch/cached arrangement ops, benchmarking |
| `fat_beatz_tools.py` | 10 | Bass enhancement, drum fattening, stereo widen, sidechain, mastering, one-shot beats |
| `optimization_tools.py` | 9 | Mix optimization, analysis, adaptive timing |
| `mixer_tools.py` | 8 | Volume/pan/send/mute/solo batch operations |
| `automation_tools.py` | 3 | Clip envelope automation add/clear |
| `audio_analysis_tools.py` | 5 | LUFS, spectral, dynamics analysis |
| `server_audio_analysis.py` | 5 | Server-side audio analysis wrappers |
| `max_bridge.py` | 1 | Max for Live device communication |
| `recipe_library/` | varies | Preset recipes (genre templates) |
| **Support (no tools)** | | |
| `connection_health.py` | — | Connection state machine, ping window, reconnect |
| `command_registry.py` | — | Command contracts (names, params, transport, ranges) |
| `browser_cache.py` | — | SQLite cache for browser/instrument queries |
| `system_config.py` | — | Loads `config/system.yaml` |
| `als_parser.py` | — | Parses `.als` (Live project) XML |
| `graphiti_memory.py` | — | Optional cross-session knowledge graph |
| `groove_tools.py` | 0 (helpers) | Groove extraction/application |
| `music_generation.py` | 0 (helpers) | Scale/progression helpers used by tools |
| `effect_management.py` | 0 (helpers) | Effect chain helpers |
| `validate_server.py` | — | CI structural validation gate |
| `docgen.py` | — | Generates `docs/TOOLS.md` |

### Supporting subsystems outside `MCP_Server`

| Path | Purpose |
|------|---------|
| `AbletonMCP_Remote_Script/__init__.py` | The Live-embedded socket server + Live API bridge (~6200 lines) |
| `elevenlabs_mcp/` | Standalone FastMCP server for ElevenLabs TTS/SFX/voice/conversational AI |
| `agentic_mix/` | LangGraph pipeline: `configure → setup_session → generate_clips → construct_arrangement → execute_section ⇄ analyze_section` |
| `agentic_mix/nodes/` | One file per graph node |
| `agentic_mix/tools/` | Tool wrappers calling MCP server |
| `orchestration/` | AgentFlow DAG runner + circuit breakers (pure-Python fallback for LangGraph) |
| `music_theory/` | Scales, chords, progressions, arpeggiators, voicing, rhythm, modes, harmonic mixing |
| `max_devices/` | Max for Live patches (`audio_export_device.maxpat`, `mcp_bridge.maxpat`) |
| `scripts/` | 135 standalone scripts: demos, mix generators, tests, utilities |
| `configs/` + `config/` | YAML analysis rules + `system.yaml` taxonomy |
| `MCP_Server/audio_analysis/` | Audio analysis engine modules |
| `MCP_Server/knowledge/` + `recipe_library/` | Knowledge base + recipe presets |

## 5.3 Level 2 — Remote Script Internal Structure

`AbletonMCP_Remote_Script/__init__.py` defines `AbletonMCP(ControlSurface)`:

```
AbletonMCP
├── start_server()              # TCP server on 9877 (threaded, request/response)
├── start_udp_server()          # UDP server on 9878 (fire-and-forget)
├── _handlers: dict             # ~200 TCP command → callable lambdas
├── _udp_handlers: dict         # 10 UDP command → callable lambdas
├── _allowed_commands: set      # TCP command whitelist (~150)
├── _udp_allowed_commands: set  # UDP whitelist (10)
├── _main_thread_scheduler      # Defers Live mutations off the notify thread
├── _song                       # Cached Live Song object
└── Live API bridge methods     # _get_session_info, _create_track, _fire_clip, ...
```

### Command dispatch

```
TCP packet ──▶ _handle_client() ──▶ _dispatch_command()
                                     │
                                     ├─ _handlers[name](params)   # TCP
                                     └─ _udp_handlers[name](params)  # UDP
                                              │
                                              ▼
                                     Live API call (song.tracks[i].clip_slots[j]...)
```

## 5.4 Level 2 — `agentic_mix` Graph

```
START
  │
  ▼
configure ──▶ setup_session ──▶ generate_clips ──▶ construct_arrangement
                                                          │
                                                          ▼
                                              ┌── execute_section
                                              │          │
                                              │          ▼
                                              │     analyze_section
                                              │          │
                                              └── more_sections? ──no──▶ END
```

`GraphState` carries: config, tracks, clips, arrangement (list of sections),
`current_section_index`, playback metrics, and audio-analysis feedback.

## 5.5 Level 2 — `elevenlabs_mcp`

Standalone FastMCP server (`elevenlabs_mcp/server.py`) exposing ~20 tools:
`text_to_speech`, `speech_to_text`, `text_to_sound_effects`, `search_voices`,
`voice_clone`, `isolate_audio`, `create_agent`, conversational AI, telephony.
Runs as a **separate** MCP server (its own stdio transport), independent of the
Ableton MCP server. Requires `ELEVENLABS_API_KEY`.
