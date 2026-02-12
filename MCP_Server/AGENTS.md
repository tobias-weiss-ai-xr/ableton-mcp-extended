# MCP_Server AGENTS.md

**Core protocol implementation** (score 12)

## WHERE TO LOOK
| Task                | Location                     |
|---------------------|------------------------------|
| Protocol handlers   | server.py                    |
| Tool registration   | advanced_tools.py            |
| Device management   | new_device_methods.py        |

## CONVENTIONS
- Agent protocol handlers use normalized values (0.0-1.0)
- Error recovery continues execution despite failures
- Parameter indices used instead of names

## ANTI-PATTERNS
- NEVER use absolute parameter values (always normalized)
- NEVER modify LSP server configuration