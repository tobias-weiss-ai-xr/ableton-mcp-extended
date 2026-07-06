---
slug: ableton-mcp-comprehensive-upgrade
status: awaiting-approval
intent: clear
pending-action: write .omo/plans/ableton-mcp-comprehensive-upgrade.md
approach: Multi-wave upgrade adding MCP resources, device knowledge base, verify loop, automation envelope support, offline .als parsing, browser deep scan, groove tools, and Max bridge architecture
---

# Draft: ableton-mcp-comprehensive-upgrade

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
| id | outcome | status | evidence path |
|----|---------|--------|---------------|
| S1 | MCP Resources (live:// track/scene/device/status) | active | `MCP_Server/server.py:747` FastMCP instance; `@mcp.resource` decorator on existing get_* returners |
| S2 | Device knowledge base (55+ Live devices) | active | New `MCP_Server/knowledge/devices/` dir with JSON schemas; ref: Pantani/ableton-mind knowledge base pattern |
| S3 | Verify loop (post-action snapshot + diff) | active | New `MCP_Server/verify.py` wrapping tool calls with snapshot/diff; ref: ableton-mind verify loop |
| S4 | Automation envelope support | active | New handlers in `AbletonMCP_Remote_Script/__init__.py` + new `MCP_Server/automation_tools.py` |
| S5 | Offline .als parsing | active | New self-contained `MCP_Server/als_parser.py` or standalone module; .als = gzipped XML |
| S6 | Browser recursive deep scan | active | Extend `MCP_Server/server.py:2759` get_browser_items_at_path; ref: livemcp recursive crawl |
| S7 | Groove template tools | active | New handlers in `__init__.py` + new `MCP_Server/groove_tools.py`; ref: livemcp groove support |
| S8 | Max for Live bridge architecture | deferred | Requires research on IPC via OSC/named pipes; defer to post-S1-S7 |

## Open assumptions (announced defaults)
| assumption | adopted default | rationale | reversible? |
|-----------|----------------|-----------|-------------|
| Resource URI scheme | `live://{track,scene,device,clip,session}/{indices}` matching livemcp convention | Interop with existing MCP clients; URI scheme well-proven | Yes - can rename |
| Device knowledge format | JSON array per device with `{name, parameters: [{name, range, default, unit}]}` | ableton-mind uses same pattern; LLMs parse structured JSON best | Yes |
| Verify behaviour | Wrap every modifying tool in try/except with post-call state read + diff | ableton-mind pattern proven; reliability improvement with 0 LLM overhead | Yes |
| .als parsing library | Python `gzip` + `xml.etree.ElementTree` (stdlib only) | .als is gzipped XML; no deps needed | Yes - can switch to lxml |
| Groove API surface | List/apply/remove groove templates by name (matching Live's groove pool) | livemcp has this and it's the standard Live workflow | Yes |
| Max bridge approach | OSC via python-osc (pip dep) connecting to Max's UDP receive | Several AbletonOSC-based MCPs use this; no patcher-side mod needed | Yes - can switch to named pipes |

## Findings (cited - path:lines)
- Current tool count: 124 in server.py, 56 in advanced_tools.py, 18 in midi_effects.py, 8 in mixer_tools.py, 5 in audio_analysis_tools.py = 211 total (`server.py:979+` decorators)
- Zero MCP resources exist: `grep -c @mcp.resource` = 0 (`MCP_Server/server.py`)
- Zero MCP prompts exist: `grep -c @mcp.prompt` = 0
- FastMCP instance at `MCP_Server/server.py:747` - livespan at `server.py:723`
- Remote Script at `AbletonMCP_Remote_Script/__init__.py` (4831 lines, 200KB)
- Submodule registration pattern: functions `register_*_tools(mcp, get_ableton_connection)` called from server.py:761-765
- Connection pattern: `AbletonConnection` dataclass at server.py:51; `get_ableton_connection()` at server.py:311
- Remote Script command dispatch: dict-based handler in `__init__.py` reading `command["type"]` and `command["params"]`
- Competitor analysis: livemcp (220 tools, 11 resources, Max bridge, grooves), ableton-mind (36 tools, 55 device schemas, verify loop), ABLE-MCP (offline .als), teamallnighter/cookbook (.als project version control)

## Decisions (with rationale)
1. **Prioritize MCP Resources (S1) first** - they touch the most existing code and unblock the verify loop.
2. **Device knowledge extracted in JSON not scraped** - Live's Default.adv XML is version-specific and undocumented; manual extraction ensures correctness.
3. **Groove tools before Max bridge** - grooves have well-defined Live API (groove_amount, groove_pool); Max bridge requires IPC research.
4. **Verify loop wraps existing tools instead of rewriting** - add post-call decorator in verify.py, don't modify 211 existing tool bodies.
5. **.als parser as standalone module** - no dependency on Ableton connection; usable offline and testable with fixture files.
6. **Each project = its own file/module** - following existing submodule pattern (advanced_tools.py, mixer_tools.py, midi_effects.py).

## Scope IN
1. MCP Resource URIs: live://status, live://session/current, live://track/{idx}, live://scene/{idx}, live://device/{ti}/{di}, live://clip/{ti}/{ci}
2. Device knowledge base: Top 30 Live 12 native devices with full parameter schemas
3. Verify loop: Decorator-based post-call verification for all 211 tools
4. Automation envelope: read envelope points, write automation points on clip + track parameters (read only for now for arrangement)
5. Offline .als parsing: open, read track/clip/device structure, detect issues, suggest changes
6. Browser deep scan: recursive walk of browser tree to discover all instruments/effects/presets
7. Groove tools: list grooves, apply groove, remove groove, set groove amount
8. Max bridge: architecture spec (deferred to implementation wave)

## Scope OUT (Must NOT have)
- Do NOT rewrite any existing tool body - verify wraps externally
- Do NOT add new pip dependencies for device knowledge or .als parsing (stdlib only)
- Do NOT attempt audio render/export (impossible via Remote Script API)
- Do NOT add Push hardware support (no physical hardware to test against)
- Do NOT create new `@mcp.tool()` entries that duplicate existing get_* functionality
- Do NOT add new UDP commands (10-command limit is architectural)
- Do NOT modify LSP server configuration

## Open questions
None at this point - all preferences adopted as defaults (see Open assumptions). Verified against AGENTS.md constraints.

## Approval gate
status: awaiting-approval
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
