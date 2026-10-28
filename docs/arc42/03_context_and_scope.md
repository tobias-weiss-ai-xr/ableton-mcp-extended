# 3. Context and Scope

## 3.1 System Context (External View)

```
                       ┌─────────────────────────────────────────────┐
                       │              AI Assistant / User             │
                       │   (Claude Desktop, Cursor, custom MCP client)│
                       └───────────────────────┬─────────────────────┘
                                               │ MCP (stdio / JSON-RPC)
                                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ableton-mcp-extended (this system)                 │
│                                                                       │
│  ┌──────────────────┐   ┌───────────────────┐   ┌─────────────────┐  │
│  │  MCP_Server      │   │  elevenlabs_mcp   │   │  agentic_mix    │  │
│  │  (FastMCP, 250+  │   │  (FastMCP, ~20    │   │  (LangGraph DAG │  │
│  │   tools)         │   │   TTS/SFX/voice   │   │   + AgentFlow)  │  │
│  └────────┬─────────┘   └─────────┬─────────┘   └────────┬────────┘  │
│           │ TCP 9877 / UDP 9878    │ HTTPS              │ calls MCP  │
│           │                        ▼                     │ tools      │
│           │              ┌──────────────────┐            │            │
│           │              │  ElevenLabs API  │            │            │
│           │              └──────────────────┘            │            │
│           ▼                                               ▼            │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │            AbletonMCP_Remote_Script (inside Live)            │    │
│  │            Python 2.7 ControlSurface; socket server          │    │
│  └──────────────────────────┬───────────────────────────────────┘    │
└─────────────────────────────┼────────────────────────────────────────┘
                              │ Live API (Lom / song / track / clip)
                              ▼
                    ┌─────────────────────┐
                    │   Ableton Live 12    │
                    │   (DAW, audio engine)│
                    └─────────────────────┘
```

## 3.2 External Interfaces

| Interface | Direction | Protocol | Purpose |
|-----------|-----------|----------|---------|
| MCP stdio | AI client ↔ `MCP_Server` | JSON-RPC over stdio | Tool calls, results |
| TCP 9877 | `MCP_Server` ↔ Remote Script | Length-prefixed JSON | Reliable commands + responses |
| UDP 9878 | `MCP_Server` ↔ Remote Script | Fire-and-forget JSON | Low-latency param updates (10 cmds) |
| HTTPS | `elevenlabs_mcp` ↔ api.elevenlabs.com | REST | TTS, SFX, voice clone, conversational AI |
| Max for Live | Remote Script ↔ `.maxpat` device | Live device params + bang | Audio export workaround |
| Filesystem | scripts ↔ `exports/`, `configs/` | local files | Rendered audio, config YAML |

## 3.3 In-Scope

- MCP tool surface for Live (session, arrangement, devices, MIDI, browser, transport).
- Dual-transport socket protocol (TCP/UDP) with a strict UDP whitelist.
- Agentic mix-generation pipeline (`agentic_mix`) with two orchestrators
  (LangGraph, AgentFlow).
- ElevenLabs voice/SFX integration as a separate MCP server.
- Music-theory helpers (scales, chords, progressions, arpeggiators, voicing).
- Production helper modules: arrangement, fat-beatz, optimization, groove, mixer,
  automation, audio analysis.
- Max for Live audio-export device + bridge.
- CI: lint, validation gate, unit/integration tests.

## 3.4 Out-of-Scope

- A graphical front-end / web UI.
- Multi-machine or cloud Ableton orchestration.
- Direct audio render/export via the Remote Script API (impossible — see §11).
- License management for Ableton Live or third-party plugins.
- Real-time audio DSP inside the MCP server (delegated to Live's devices).
