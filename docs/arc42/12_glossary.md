# 12. Glossary

## 12.1 Domain Terms

| Term | Definition |
|------|------------|
| **Ableton Live** | Digital audio workstation (DAW) by Ableton. The system controls Live 11+. |
| **Session View** | Live's clip-grid view for loop-based composition. Most MCP tools operate here. |
| **Arrangement View** | Live's linear timeline view. `arrangement_tools.py` handles capture/clip/automation here. |
| **Remote Script** | A Python 2.7 `ControlSurface` plugin loaded by Live to control the DAW externally. This project's is `AbletonMCP_Remote_Script/`. |
| **ControlSurface** | Ableton's base class for remote-control scripts (`from _Framework.ControlSurface import ControlSurface`). |
| **Lom** | Live Object Model — the Python API Live exposes to Remote Scripts (`song`, `track`, `clip`, etc.). |
| **Clip** | A container for MIDI or audio on a track, in a session slot or arrangement timeline. |
| **Scene** | A column of clip slots in Session View, fired together. |
| **Device** | An instrument or effect on a track (e.g. Reverb, Drum Rack). Parameters are normalized 0.0–1.0. |
| **Drum Rack** | A Live instrument hosting pad-based drum samples. Must be loaded with a specific kit `FileId`, never empty. |
| **FileId** | Ableton browser URI fragment identifying a specific preset/sample (e.g. `FileId_58622`). |
| **Send / Return** | Auxiliary routing for shared effects (reverb, delay). |
| **Capture** | Recording the current session state into the arrangement. `capture_to_arrangement` (Live 12) vs `capture_and_insert_midi` (Live 10/11). |
| **Max for Live** | Visual programming environment inside Live; used here for the audio-export device. |

## 12.2 Protocol & Architecture Terms

| Term | Definition |
|------|------------|
| **MCP** | Model Context Protocol — JSON-RPC over stdio between an AI client and a server exposing `@tool`-decorated functions. |
| **FastMCP** | The Python MCP SDK class (`mcp.server.fastmcp.FastMCP`) used to build the server. |
| **TCP channel** | Port 9877, length-prefixed JSON, request/response — reliable commands. |
| **UDP channel** | Port 9878, fire-and-forget JSON datagrams — 10-command whitelist for low-latency updates. |
| **UDP whitelist** | The 10 commands allowed over UDP: `set_device_parameter`, `set_track_volume`, `set_track_pan`, `set_track_mute`, `set_track_solo`, `set_track_arm`, `set_master_volume`, `set_send_amount`, `fire_clip`, `set_clip_launch_mode`. |
| **Command contract** | `CommandSpec`/`ParamSpec` in `command_registry.py` defining name, params, transport, and normalized ranges. |
| **Normalized parameter** | A float in 0.0–1.0 representing a device/track value, independent of Live's raw range. |
| **Main-thread scheduling** | Deferring Live API mutations off the notification thread (Live disallows mutations from notifications). |
| **Handler map** | `dict[str, callable]` built once at init in the Remote Script, replacing a giant `if/elif` chain. |
| **Watchdog** | `server_watchdog.py` — monitors connection health and restarts the MCP server after 30 s disconnected. |

## 12.3 Agentic / Generation Terms

| Term | Definition |
|------|------------|
| **Agentic mix** | Autonomous generation of a complete multi-section mix via `agentic_mix`. |
| **LangGraph** | Graph-based state-machine framework; `agentic_mix/graph.py` defines the node flow. |
| **AgentFlow** | Pure-Python DAG runner in `orchestration/agentflow_runner.py`; fallback when LangGraph is unavailable. |
| **GraphState** | The shared state dict passed between `agentic_mix` nodes (config, tracks, clips, arrangement, metrics). |
| **Section** | A timed segment of an arrangement (e.g. 4 minutes); the pipeline loops over sections. |
| **Sound set** | Genre-to-instrument mapping in `agentic_mix/sound_sets.py`. |
| **Circuit breaker** | `orchestration/circuit_breaker.py` — per-task failure isolation with open/half-open/closed states. |
| **Energy curve** | Per-section loudness/intensity trajectory applied via `apply_energy_curve`. |
| **Groove** | Timing/velocity humanization applied to clips (`groove_tools.py`). |
| **Fat Beatz** | A suite of mastering/processing tools (bass enhance, drum fatten, stereo widen, sidechain). |

## 12.4 Music Theory Terms

| Term | Definition |
|------|------------|
| **Scale / Mode** | Set of notes defining a key's flavor (major, minor, dorian, phrygian, etc.). |
| **Roman numeral progression** | Chord progression notation (I–V–vi–IV) resolved by `progression.py`. |
| **Voicing** | How chord notes are distributed across octaves (`voicing.py`). |
| **Arpeggiator** | Pattern that turns chords into sequenced notes (`arpeggiator.py`). |
| **Follow action** | Live clip property that auto-triggers another clip; `setup_harmonic_follow_actions` makes transitions musically coherent. |
| **One drop / Rockers / Steppers** | Jamaican/reggae/dub drum patterns (see `config/system.yaml`). |
| **Dub techno** | Genre characterized by sparse kicks, echo, filter sweeps, sub-bass. |
| **Four-on-the-floor** | House/techno kick pattern (kick every quarter note). |

## 12.5 File / Module Conventions

| Convention | Meaning |
|------------|---------|
| `*_tools.py` in `MCP_Server/` | A tool domain module exporting `register_*(mcp, get_connection)`. |
| `scripts/test/` | Standalone test scripts (no pytest discovery). |
| `scripts/util/` | Utility scripts (session inspection, recording helpers). |
| `MCP_Server/recipe_library/` | Reusable genre/processing recipes. |
| `MCP_Server/knowledge/` | Knowledge-base data for generative helpers. |
| `config/system.yaml` | Single source of truth for ports, UDP whitelist, kits, patterns, presets. |
| `configs/analysis/*.yml` | Audio-analysis rule definitions. |
| `max_devices/*.maxpat` | Max for Live patches (audio export, MCP bridge). |
| `music_theory/*.md` | Prose docs accompanying each music-theory module. |

## 12.6 External Services

| Service | Used by | Purpose |
|---------|---------|---------|
| ElevenLabs API (`api.elevenlabs.com`) | `elevenlabs_mcp` | TTS, SFX, voice cloning, conversational AI |
| Ableton Live (local) | `MCP_Server` via Remote Script | DAW control |
| Max for Live (local, inside Live) | `max_devices/` | Audio export workaround |

---

*End of arc42 documentation. See `00_index.md` for the table of contents.*
