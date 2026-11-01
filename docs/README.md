# Documentation

Start here. Everything in this folder is either maintained or explicitly marked as
historical.

## Maintained

| Where | What |
|-------|------|
| [`arc42/`](arc42/00_index.md) | Architecture documentation, one file per arc42 section (01–12) |
| [`TOOLS.md`](TOOLS.md) | Generated reference for all 120 MCP tools (regenerate: `python -m MCP_Server.docgen`) |
| [`SCRIPTS.md`](SCRIPTS.md) | What the 100+ scripts do, and which ones are actually maintained |
| [`live_performance_guide.md`](live_performance_guide.md) | Live/DJ-style parameter performance |
| [`generative-music-workflow.md`](generative-music-workflow.md) | MIDI generation workflow |
| [`max-bridge-architecture.md`](max-bridge-architecture.md) | Max for Live bridge (audio export workaround) |
| [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) | Command cheatsheet |

## Topic folders

| Where | What |
|-------|------|
| [`vst-plugins/`](vst-plugins/) | Notes on third-party plugin control |
| [`research/`](research/) | Background research |
| [`superpowers/`](superpowers/) | Internal skill/agent notes |

## Historical — do not trust

| Where | What |
|-------|------|
| [`archive/`](archive/README.md) | Session summaries, milestone write-ups, inventory dumps. Kept for the decision trail only; may contradict current code. |

## The docs outside this folder

- `README.md` (repo root) — what the project is, install, tool overview
- `AGENTS.md` (repo root) — architecture rules, anti-patterns, working commands
- `QUICK_START.md`, `PIPELINEREADME.md`, feature guides — task-oriented, stay at root
  next to the code they describe

## Keeping docs honest

Three doc defects found in a 2026 pass, worth watching for when editing:

1. **Parameter ranges.** Device parameters are *native* (`Hz`, `dB`, `%`, `ms`,
   beats) — `set_device_parameter` assigns to `parameter.value` with no
   normalization. Only track volume/pan/send amounts are 0.0–1.0. Older text
   claiming "everything normalized 0.0–1.0" is wrong.
2. **Counts drift.** `@mcp.tool` tools, handler-map entries and line counts change
   with every feature. Re-derive them (`grep -c '@mcp.tool' MCP_Server/server.py`)
   instead of copying numbers forward.
3. **UDP whitelist.** 11 commands, not 10 — `set_crossfader` was missing from older
   lists. Source of truth: `_build_udp_handlers()` in
   `AbletonMCP_Remote_Script/__init__.py`.
