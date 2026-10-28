# 8. Cross-cutting Concepts

## 8.1 Parameter Normalization

**Rule:** Every device and track parameter is expressed as a float in **0.0–1.0**,
never the raw Live API value. This is the most important convention in the project.

- Enforced in `command_registry.py` (`ParamSpec.min_value`/`max_value`).
- Violations are listed as anti-patterns in `AGENTS.md`.
- The Remote Script normalizes on the Live side; the MCP server normalizes on input.

## 8.2 Transport Selection (TCP vs UDP)

A command's transport is determined by its contract in `command_registry.py`:

- **TCP** (default): anything that returns data, mutates structure, or is
  irreversible — `get_*`, `create_*`, `delete_*`, `quantize`, `undo/redo`,
  recording, browser loading, arrangement ops.
- **UDP** (whitelist of 10): high-frequency, reversible parameter updates —
  `set_device_parameter`, `set_track_volume`, `set_track_pan`, `set_track_mute`,
  `set_track_solo`, `set_track_arm`, `set_master_volume`, `set_send_amount`,
  `fire_clip`, `set_clip_launch_mode`.

The whitelist is enforced on **both** ends (`config/system.yaml` +
`_udp_allowed_commands` in the Remote Script).

## 8.3 Command Contract Registry

`MCP_Server/command_registry.py` is the single source of truth:

- `CommandSpec(name, params, transport)` for every command.
- `ParamSpec(type, min_value, max_value, description)`.
- Consumed by the MCP server (for validation), the Remote Script (for dispatch),
  and tests (for contract assertions — `tests/test_command_registry.py`).

## 8.4 Connection Health & Resilience

- **State machine** (`connection_health.py`): `disconnected → connecting →
  connected → reconnecting → error`.
- **Retry:** `MAX_RETRIES = 3`, backoff `[1.0, 2.0, 4.0]` s.
- **Ping window:** rolling 5 samples for latency tracking.
- **Watchdog** (`server_watchdog.py`): restarts the MCP server after
  `WATCHDOG_DISCONNECT_TIMEOUT = 30 s`.
- **Error codes:** `LIVE_DISCONNECTED`, `LIVE_RECONNECTING`, etc., each marked
  `retryable`.

## 8.5 Main-Thread Scheduling (Live API constraint)

Live's API cannot be mutated from notification callbacks. The Remote Script
defers mutation-heavy commands (e.g. `duplicate_clip_to_arrangement`,
`build_arrangement`) to a main-thread scheduler. This is why the comment in
`_allowed_commands` reads: *"must run on main thread: duplicate_clip_to_arrangement
fails with 'Changes cannot be triggered by notifications' when called directly
from the socket notification handler."*

## 8.6 Browser & Instrument Caching

`browser_cache.py` is a **SQLite** persistent cache for Ableton browser queries
(instruments, effects, samples). Avoids repeated expensive browser enumeration on
every `load_instrument_or_effect` call. URIs use the form
`query:<Category>#<FileId>` (e.g. `query:Drums#FileId_58622`).

## 8.7 Music Theory Engine

`music_theory/` provides reusable, pure-Python music primitives used by both the
MCP tools and the agentic pipeline:

- `scales.py`, `modes.py`, `exotic_scales.py` — scale/mode definitions
- `chord.py`, `voicing.py`, `harmonization.py` — chord construction & voicing
- `progression.py` — Roman-numeral progressions
- `arpeggiator.py` — arp patterns
- `polyrhythm.py`, `rhythm.md` — rhythmic primitives
- `expectation_model.py`, `mert_analyzer.py` — musical expectation modeling
- Markdown docs (`*.md`) accompany each module

## 8.8 Genre Templates & Recipes

- `config/system.yaml` defines drum-pattern grids (`one_drop`, `rockers`,
  `steppers`, `house_basic`, `techno_4x4`, `dub_techno`) with BPM ranges.
- `MCP_Server/recipe_library/` holds reusable genre recipes.
- `agentic_mix/sound_sets.py` maps genres to instrument/sound selections.

## 8.9 Audio Export Workaround

Because the Remote Script API cannot export audio:

1. **Max for Live device** (`max_devices/audio_export_device.maxpat`) — records to
   WAV/AIFF/OGG/FLAC; must be triggered manually (bang inlet).
2. **Manual UI export** — File → Export in Ableton.
3. **`convert_to_mp3.py`** — converts the Max device's WAV to MP3.

## 8.10 Observability & Validation

- `MCP_Server/validate_server.py` — CI-time structural validator (imports, tool
  registration, command-registry consistency).
- `MCP_Server/docgen.py` — generates `docs/TOOLS.md` from registered tools.
- Logging throughout (`logging` module) with `mcp.log`, `mcp_server.log`.
- `connection_health` exposes structured state for diagnostics.

## 8.11 Security Boundaries

- **Localhost only:** Remote Script binds `127.0.0.1`; no remote exposure.
- **UDP whitelist:** prevents unsafe fire-and-forget mutations.
- **`.env` for secrets:** `ELEVENLABS_API_KEY` loaded via `python-dotenv`; never
  committed (`.gitignore` covers `.env`/`.env.*`).
- **No arbitrary code execution:** tools operate on Live objects only; no shell,
  eval, or file-write outside known directories.
