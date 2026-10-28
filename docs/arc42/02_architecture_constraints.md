# 2. Architecture Constraints

## 2.1 Technical Constraints

| Constraint | Detail | Impact |
|------------|--------|--------|
| **Ableton Live Remote Script API** | Python 2.7 runtime inside Live; limited stdlib; no third-party packages available inside the script | Remote Script (`AbletonMCP_Remote_Script/__init__.py`) must be pure-Python-2-compatible, no pip deps |
| **MCP transport** | stdio between MCP client and `MCP_Server`; TCP/UDP between `MCP_Server` and the Remote Script | Two distinct wire layers (see §5) |
| **Python ≥ 3.10** | MCP server, agentic pipeline, scripts | `pyproject.toml` sets floor; uses modern type hints |
| **localhost-only networking** | Remote Script binds `127.0.0.1:9877/9878` | No remote/Distributed control; single Live instance per machine |
| **Single-threaded Live API** | Most Live calls must run on the main thread; notifications cannot trigger mutations | Arrangement ops deferred to main-thread scheduler; `duplicate_clip_to_arrangement` fails from socket handler |
| **No audio export API** | Live's Remote Script API has no `export_audio()` | Export handled by Max for Live device (manual bang) or manual UI export |
| **LangGraph / LangChain optional** | `langgraph` is a declared dep but the CLI degrades to AgentFlow if unavailable | `agentic_mix/cli.py` lazy-imports the pipeline |

## 2.2 Organizational Constraints

- **License:** MIT (upstream + extensions).
- **Upstream lineage:** Forked from `uisato/ableton-mcp`; extended in place. The
  upstream homepage in `pyproject.toml` is preserved.
- **CI:** GitHub Actions on `main` — lint (Ruff), validate (`validate_server.py`),
  pytest. Existing `MCP_Server` code is allowed pre-existing lint warnings
  (`--ignore=E402,F821,E722 || true`); new code (`agentic_mix/`, `tests/`) is strict.
- **No pytest discovery of integration tests:** Several `tests/test_legacy_*` and
  `tests/test_integration_test.py` are excluded in CI; tests are standalone-style.

## 2.3 Conventions

- **Parameter normalization:** All device/track parameters use **0.0–1.0** floats,
  never raw API values. Violations are an anti-pattern (see AGENTS.md).
- **UDP whitelist:** Exactly 10 commands may use UDP; everything else is TCP.
- **Instrument loading:** Never load an empty Drum Rack — always a kit preset with
  a specific `FileId` (e.g. `query:Drums#FileId_58622`).
- **Command contract registry:** `MCP_Server/command_registry.py` is the single
  source of truth for command names, params, and transport assignment.
- **Config-driven taxonomy:** `config/system.yaml` holds ports, UDP whitelist,
  drum kits, pattern grids, and preset URIs.

## 2.4 Platform & Runtime

| Aspect | Value |
|--------|-------|
| OS | Windows (primary; Ableton Live 12 Suite). macOS/Linux partially supported for the MCP server / scripts only — no Live. |
| Ableton version | Live 11+ (Live 12 Suite tested) |
| Python (server side) | ≥ 3.10 |
| Python (Remote Script) | 2.7 (Ableton embedded) |
| MCP SDK | `mcp[cli] ≥ 1.3.0` |
| Optional | `pynput`, `screeninfo` (XY controller); `numpy`, `sounddevice`, `pyyaml` (dev/analysis) |
