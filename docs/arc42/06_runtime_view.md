# 6. Runtime View

## 6.1 Startup Sequence

```
1. pip install -e .                          # installs ableton-mcp-extended, langgraph-mix
2. AI client launches MCP server via stdio:
      ableton-mcp-extended                   # entry point → MCP_Server.server:main
3. FastMCP lifespan (server_lifespan) runs:
      ├─ AbletonConnection(host=127.0.0.1, port=9877) created (lazy connect)
      └─ module tool registrations execute (register_* for 14 modules)
4. Remote Script already running inside Live (loaded at Live startup):
      ├─ AbletonMCP.__init__()
      ├─ _build_handlers() / _build_udp_handlers()
      ├─ start_server()  → TCP listener on 127.0.0.1:9877
      └─ start_udp_server() → UDP listener on 127.0.0.1:9878
5. First tool call → send_command() → connect → JSON over TCP → response
```

## 6.2 TCP Command Lifecycle (reliable)

```
MCP client
    │  @server.tool("create_midi_track")
    ▼
FastMCP dispatches → tool function in MCP_Server
    │
    ▼
get_ableton_connection()  (singleton, reconnects on failure)
    │
    ▼
AbletonConnection.send_command(command_type, params)
    │  JSON: {"type": <cmd>, "params": {...}}
    │  length-prefixed TCP frame
    ▼
Remote Script _handle_client() → _dispatch_command()
    │
    ▼
_handlers[cmd](params) → Live API call
    │
    ▼
JSON result: {"status": "success"|"error", ...}
    │
    ▼
tool function returns dict → FastMCP → MCP client
```

### Connection health & retry

- `connection_health.py` tracks state: `disconnected → connecting → connected → reconnecting → error`.
- `send_command` retries up to `MAX_RETRIES = 3` with backoff `[1.0, 2.0, 4.0]` s.
- `server_watchdog.py` restarts the MCP server after 30 s disconnected.

## 6.3 UDP Command Lifecycle (low-latency)

```
tool function (e.g. set_device_parameter for a sweep)
    │
    ▼
AbletonConnection.send_command_udp(cmd, params)
    │  JSON datagram, no response expected
    ▼
Remote Script _udp_server_loop() → _udp_handlers[cmd]
    │
    ▼
Live API call (must be fast & reversible)
```

**Only 10 commands** are UDP-eligible (see §3 / `config/system.yaml`):
`set_device_parameter`, `set_track_volume`, `set_track_pan`, `set_track_mute`,
`set_track_solo`, `set_track_arm`, `set_master_volume`, `set_send_amount`,
`fire_clip`, `set_clip_launch_mode`.

## 6.4 Agentic Mix Generation Runtime

```
python -m agentic_mix.cli --genre dub_techno --tempo 126 --duration 120
    │
    ▼
parse_args() → Config
    │
    ├─ if --orchestrator agentflow: AgentFlowRunner.run(config_dict)
    │      └─ sequential DAG: configure → setup → generate → construct → execute_loop → adapt
    │          per-task circuit breakers (orchestration/circuit_breaker.py)
    │
    └─ else (default): LangGraph run_pipeline(config)
           └─ StateGraph nodes (see §5.4)
                 each node calls MCP tools → TCP → Live
                 analyze_section receives audio feedback → adapts next section
```

The pipeline calls MCP tools the same way any MCP client would (over TCP to the
Remote Script). Audio analysis feeds back into `GraphState` to adjust energy,
variation, and instrument choices for subsequent sections.

## 6.5 Arrangement Capture (three-tier fallback)

```
capture_and_insert_arrangement(track_index, clip_index, ...):
  1. Try song.capture_to_arrangement()           # Live 12+
  2. elif song.capture_and_insert_midi():         # Live 10/11
  3. else: real-time recording fallback:
        arm track → start recording → start playback
        → wait up to 10 s for clip to record → stop
```

The 10-second cap prevents MCP server timeouts; it captures ~5–8 bars at
120–140 BPM.

## 6.6 ElevenLabs Runtime (separate server)

```
elevenlabs-mcp (separate stdio MCP server)
    │  loads .env → ELEVENLABS_API_KEY
    ▼
FastMCP with ~20 TTS/SFX/voice tools
    │
    ▼
httpx → https://api.elevenlabs.com
    │
    ▼
audio files written to ELEVENLABS_OUTPUT_DIR (default ~/Documents/Ableton/User Library/eleven_labs_audio)
```

Independent lifecycle from the Ableton MCP server.

## 6.7 Concurrency Model

| Component | Threading |
|-----------|-----------|
| MCP server (FastMCP) | asyncio event loop (stdio) |
| Remote Script TCP | One thread per client + main accept loop |
| Remote Script UDP | Dedicated UDP thread |
| Live API mutations | Deferred to main thread via scheduler (notifications cannot trigger mutations) |
| Agentic pipeline | Synchronous sequential node execution |
| ElevenLabs server | asyncio (httpx async) |

The Remote Script is the critical concurrency boundary: Live's API is not
thread-safe for mutations, so `duplicate_clip_to_arrangement` and similar
ops are scheduled onto the main thread rather than executed inline from the
socket handler.
