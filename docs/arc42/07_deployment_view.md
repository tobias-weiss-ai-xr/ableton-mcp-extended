# 7. Deployment View

## 7.1 Deployment Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     Developer Machine (Windows)              │
│                                                              │
│  ┌───────────────┐   stdio   ┌───────────────────────────┐  │
│  │  AI Client    │◀─────────▶│  MCP_Server (FastMCP)     │  │
│  │  (Claude /    │           │  ableton-mcp-extended     │  │
│  │   Cursor)     │           │  Python ≥ 3.10            │  │
│  └───────────────┘           └──────────┬────────────────┘  │
│                                         │ TCP 9877 / UDP 9878│
│  ┌─────────────────────────────────────┐│                    │
│  │  elevenlabs_mcp (optional, separate)││                    │
│  │  Python ≥ 3.10, needs API key       ││ HTTPS              │
│  └─────────────────────────────────────┘│                    │
│                                         ▼                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Ableton Live 12 Suite                                   ││
│  │  ┌─────────────────────────────────────────────────┐    ││
│  │  │  AbletonMCP_Remote_Script (Python 2.7)          │    ││
│  │  │  ControlSurface subclass, socket server          │    ││
│  │  └─────────────────────────────────────────────────┘    ││
│  │  Audio engine + Max for Live devices                    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
        │
        │ HTTPS (ElevenLabs)
        ▼
┌──────────────────┐
│ api.elevenlabs.com│
└──────────────────┘
```

## 7.2 Installation

```bash
git clone <repo>
cd ableton-mcp-extended
pip install -e ".[dev]"          # core + dev/test deps
# Optional XY controller:
pip install -e ".[xy_controller]"
```

### Remote Script installation

The `AbletonMCP_Remote_Script/` folder is copied (or symlinked) into Ableton's
User Library `Remote Scripts/` directory:

- **Windows:** `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\AbletonMCP\`
- **macOS:** `~/Music/Ableton/User Library/Remote Scripts/AbletonMCP/`

Then enable **AbletonMCP** in Live's Link/Tempo/MIDI preferences (Control Surface).

## 7.3 MCP Client Configuration

The AI client (e.g. Claude Desktop `claude_desktop_config.json`) points at the
server entry points:

```jsonc
{
  "mcpServers": {
    "ableton": {
      "command": "ableton-mcp-extended",      // from pyproject [project.scripts]
      "transport": "stdio"
    },
    "elevenlabs": {                            // optional, separate server
      "command": "elevenlabs-mcp",
      "transport": "stdio",
      "env": { "ELEVENLABS_API_KEY": "..." }
    }
  }
}
```

## 7.4 Ports & Endpoints

| Service | Bind | Protocol | Notes |
|---------|------|----------|-------|
| Remote Script TCP | `127.0.0.1:9877` | TCP, length-prefixed JSON | All reliable commands |
| Remote Script UDP | `127.0.0.1:9878` | UDP, JSON datagrams | 10-command whitelist only |
| MCP server ↔ client | stdio | JSON-RPC | No network port |
| ElevenLabs API | `api.elevenlabs.com:443` | HTTPS | External |

All Local-loopback — no external inbound ports are opened.

## 7.5 CI/CD

`.github/workflows/ci.yml` runs on push/PR to `main`:

| Job | Steps |
|-----|-------|
| `lint` | Ruff (strict on `agentic_mix/`, `tests/`; lenient on `MCP_Server/`) + `compileall` |
| `validate` | `python MCP_Server/validate_server.py` (structural gate) |
| `test` | `pytest tests/` (excludes `test_integration_test.py`, `test_sounddevice_loopback.py`) |

No CD pipeline — deployment is local (`pip install -e .` + manual Ableton setup).

## 7.6 Deliverables / Entry Points

| Entry point | Module | Purpose |
|-------------|--------|---------|
| `ableton-mcp-extended` | `MCP_Server.server:main` | Core Ableton MCP server |
| `langgraph-mix` | `agentic_mix.cli:main` | Agentic mix generator CLI |
| `elevenlabs-mcp` | `elevenlabs_mcp.__main__` | Voice/SFX MCP server |
| `python -m orchestration.agentflow_runner` | `orchestration.agentflow_runner` | AgentFlow DAG runner (fallback) |
