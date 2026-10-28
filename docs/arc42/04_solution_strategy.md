# 4. Solution Strategy

## 4.1 Fundamental Approach

The system is a **translator + orchestrator**:

1. **Translate** AI intent (MCP tool calls) into Ableton Live API calls.
2. **Orchestrate** multi-step musical workflows (mix generation, arrangement,
   mastering) across hundreds of low-level tool calls.

Two translation layers keep concerns separated:

- **Wire layer** — `MCP_Server` ⇄ `AbletonMCP_Remote_Script` over TCP/UDP.
- **Semantic layer** — high-level tools (e.g. `create_drum_pattern`,
  `build_arrangement`, `generate_melody_clip`) compose many low-level calls.

## 4.2 Key Decisions

| Decision | Rationale | Alternatives considered |
|----------|-----------|-------------------------|
| **Dual TCP/UDP transport** | TCP gives reliability for state-changing ops; UDP gives ~0.2 ms latency for high-frequency parameter sweeps (DJ-style automation) | Single TCP only (too slow for live sweeps); WebSocket (Live script can't host one) |
| **Declarative handler maps** in the Remote Script | Replaces a 6000-line `if/elif` chain; `_build_handlers()` and `_build_udp_handlers()` map command names → callables once at init | Giant dispatch function (unreadable, error-prone) |
| **Command contract registry** (`command_registry.py`) | Single source of truth for names, params, transport, and normalized ranges; shared by server, script, and tests | Scattered string literals (drift bugs) |
| **Modular tool registration** — each domain in its own `*_tools.py` with a `register_*(mcp, get_connection)` entry point | Keeps `server.py` from ballooning further; each module is independently testable | One monolithic `server.py` (already 5700+ lines) |
| **Three-tier arrangement capture fallback** | Live 12 has `capture_to_arrangement`; Live 10/11 has `capture_and_insert_midi`; older versions need real-time recording | Single API call (fails on older Live) |
| **Two orchestrators for mix generation** | LangGraph gives graph-based state machines; AgentFlow gives a pure-Python DAG runner with circuit breakers when LangGraph is unavailable | Single orchestrator (would force a hard dependency) |
| **Max for Live device for audio export** | The Remote Script API cannot export audio; a Max device can write WAV files | Pretend export works (broken); require manual export only (poor UX) |
| **UDP whitelist enforced on both ends** | Defense in depth: server only sends whitelisted commands; script only accepts whitelisted commands | Trust the sender (unsafe) |
| **Config-driven taxonomy** (`config/system.yaml`) | Ports, kits, patterns, presets live in one versioned file | Hard-coded constants (drift, can't reconfigure) |

## 4.3 Architectural Style

- **MCP server**: modular monolith — `server.py` is the core; `*_tools.py` modules
  register tools into the same `FastMCP` instance at startup.
- **Remote Script**: single-file embedded component with internal logical sections
  (handlers, UDP loop, main-thread scheduler, browser cache, Live API bridge).
- **Agentic pipeline**: directed graph (LangGraph `StateGraph`) or linear DAG
  (AgentFlow) over a shared `GraphState`.
- **Observability**: `connection_health.py` state machine + `server_watchdog.py`
  auto-restart; `validate_server.py` is a CI-time structural gate.

## 4.4 Top-Level Data Flow (a single tool call)

```
AI client ──MCP──▶ MCP_Server.send_command() ──TCP/UDP──▶ Remote Script
                                                              │
                                                              ▼
                                                      Live API (Lom)
                                                              │
                              ◀──JSON response── ────────────┘
MCP_Server returns result to AI client via FastMCP
```

For agentic generation, the flow is higher-level:

```
agentic_mix CLI ──▶ LangGraph/AgentFlow nodes ──▶ MCP tools ──▶ Live
        ▲                                                    │
        └──────────── audio analysis feedback ◀──────────────┘
```
