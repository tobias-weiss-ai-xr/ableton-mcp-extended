# PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-24 18:46:31
**Commit:** ee4f99a
**Branch:** master

## OVERVIEW
Control Ableton Live via AI assistants using Model Context Protocol. Python-based MCP server with UDP integration for real-time control.

## STRUCTURE
```
./
├── MCP_Server/      # Core protocol implementation
├── dub_techno_2h/     # 2-hour automation project
├── scripts/test/    # Integration tests
├── elevenlabs_mcp/  # Voice generation integration
└── max_devices/     # Max for Live audio export
```

## WHERE TO LOOK
| Task              | Location               |
|-------------------|------------------------|
| Protocol handlers | MCP_Server/            |
| Test automation   | scripts/test/          |
| Audio export      | max_devices/           |
| Voice generation  | elevenlabs_mcp/        |

## CONVENTIONS
- 0.0-1.0 normalized parameter values
- UDP protocol for real-time control
- Manual audio export required (no API)

## ANTI-PATTERNS
- NEVER attempt direct audio export (fundamentally impossible)
- NEVER modify Ableton's Remote Script API

## UNIQUE STYLES
- Telegraphic documentation
- Sectioned by functional domain

## COMMANDS
```bash
pip install -e .
python MCP_Server/server.py
cd dub_techno_2h && python auto_play_2h_dub_techno.py
```

## NOTES
- Max for Live device required for audio export
- Manual setup needed for 2-hour automation