# 9. Architecture Decisions

> Format: **Context · Decision · Consequences**. Ordered by significance.

## ADR-1: Dual TCP/UDP transport between MCP server and Remote Script

**Context.** DJ-style live parameter sweeps send dozens of updates per second.
TCP round-trips (~20–50 ms each) make smooth sweeps impossible. Yet state-changing
commands (create/delete/quantize) need reliability and responses.

**Decision.** Run two sockets:
- **TCP 9877** for all reliable, response-returning commands.
- **UDP 9878** for a strict whitelist of 10 high-frequency, reversible updates.

**Consequences.**
- ✅ Sub-millisecond sweeps; reliable ops still get responses.
- ✅ Whitelist enforced on both ends (`config/system.yaml` + Remote Script).
- ⚠️ UDP is fire-and-forget — dropped packets are silent (acceptable for sweeps).
- ⚠️ Two code paths to maintain; `send_command` vs `send_command_udp`.

## ADR-2: Declarative handler maps in the Remote Script

**Context.** The Remote Script had grown to a 6000+ line `if/elif` dispatch chain,
making it unreadable and bug-prone.

**Decision.** `_build_handlers()` and `_build_udp_handlers()` build a
`dict[str, callable]` once at init; `_dispatch_command()` does a single lookup.

**Consequences.**
- ✅ Adding a command = one lambda in the map + one Live API method.
- ✅ Command name collisions surface immediately (dict key).
- ✅ Whitelist (`_allowed_commands`) is a separate `set` for fast validation.
- ⚠️ The file is still large because each handler is a real Live API method.

## ADR-3: Modular tool registration via `register_*(mcp, get_connection)`

**Context.** `server.py` reached 5700+ lines with every tool domain inline.

**Decision.** Each domain lives in its own module (`midi_effects.py`,
`arrangement_tools.py`, `fat_beatz_tools.py`, …) and exports a
`register_*(mcp, get_ableton_connection)` function called from `server.py` at
startup.

**Consequences.**
- ✅ Domains are independently testable and readable.
- ✅ `server.py` stays the connection/transport core.
- ⚠️ Tool count (~250) is spread across 14 files — tool inventory requires
  `docgen.py` or `grep -c "@server.tool"`.

## ADR-4: Command contract registry as single source of truth

**Context.** Command names, parameter types, and transport assignments were
scattered as string literals across server, script, and tests, causing drift.

**Decision.** `command_registry.py` defines frozen `CommandSpec`/`ParamSpec`
dataclasses consumed by all three.

**Consequences.**
- ✅ Tests assert the contract (`tests/test_command_registry.py`).
- ✅ `validate_server.py` can check structural consistency in CI.
- ⚠️ Adding a command now requires editing the registry too (small overhead).

## ADR-5: Three-tier fallback for arrangement capture

**Context.** `capture_to_arrangement()` exists in Live 12 but not 10/11;
`capture_and_insert_midi()` exists in 10/11 but not 12; older versions have
neither.

**Decision.** `capture_and_insert_arrangement` tries, in order:
1. `song.capture_to_arrangement()` (Live 12+)
2. `song.capture_and_insert_midi()` (Live 10/11)
3. Real-time recording fallback (arm → record → play → wait ≤ 10 s → stop)

**Consequences.**
- ✅ Works across Live 10/11/12.
- ⚠️ Fallback caps at 10 s to avoid MCP timeout → captures ~5–8 bars at 120–140 BPM.
- ⚠️ Fallback has audible side effects (recording starts/stops).

## ADR-6: Two orchestrators for agentic mix generation

**Context.** LangGraph gives a clean state-machine graph but is a heavy dep;
some environments can't install it.

**Decision.** `agentic_mix/` uses LangGraph by default; `orchestration/agentflow_runner.py`
is a pure-Python DAG runner with circuit breakers as a fallback, selectable via
`--orchestrator agentflow`.

**Consequences.**
- ✅ No hard dependency on LangGraph for the CLI.
- ✅ Circuit breakers (`orchestration/circuit_breaker.py`) isolate per-task failures.
- ⚠️ Two code paths must be kept behaviorally equivalent.

## ADR-7: Max for Live device for audio export (not the Remote Script API)

**Context.** Live's Remote Script API has no `export_audio()`; pretending
otherwise would be broken.

**Decision.** Ship a Max for Live device (`audio_export_device.maxpat`) that
writes WAV/AIFF/OGG/FLAC to disk when its bang inlet is triggered. Provide
`convert_to_mp3.py` for MP3 conversion.

**Consequences.**
- ✅ Audio export actually works.
- ⚠️ Requires manual trigger (no Remote Script control of Max inlets).
- ⚠️ MP3 requires a post-step.

## ADR-8: ElevenLabs as a separate MCP server

**Context.** Voice/SFX generation is optional, costs money, and has a different
lifecycle (external API key, network) than the DAW control server.

**Decision.** `elevenlabs_mcp/` is a standalone FastMCP server with its own
stdio transport and `ELEVENLABS_API_KEY` env var.

**Consequences.**
- ✅ Ableton MCP works without ElevenLabs configured.
- ✅ Cost-bearing tools are isolated and clearly marked.
- ⚠️ Users must configure two MCP servers in their client.

## ADR-9: Config-driven taxonomy (`config/system.yaml`)

**Context.** Ports, drum-kit FileIds, pattern grids, and preset URIs were
hard-coded across modules.

**Decision.** Centralize them in `config/system.yaml`, loaded by
`system_config.py`.

**Consequences.**
- ✅ Reconfiguration without code changes.
- ✅ Single source of truth for the UDP whitelist and ports.
- ⚠️ `system_config.py` must be imported before any module that reads these values.

## ADR-10: Python 2 compatibility for the Remote Script only

**Context.** Ableton Live embeds Python 2.7 for Remote Scripts; no pip, no
third-party packages.

**Decision.** `AbletonMCP_Remote_Script/__init__.py` is pure stdlib with
`from __future__ import` imports and `try: import Queue / except: import queue`
shims. Everything else (MCP server, agentic pipeline) targets Python ≥ 3.10.

**Consequences.**
- ✅ Remote Script loads in any Live 11/12.
- ⚠️ Two Python dialects in one repo — no shared code between them except the
  JSON protocol contract.
