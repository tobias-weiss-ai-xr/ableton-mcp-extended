# 11. Risks and Technical Debt

## 11.1 Risks

| ID | Risk | Likelihood | Impact | Mitigation / Status |
|----|------|-----------|--------|---------------------|
| R1 | **`server.py` is 5700+ lines** — monolithic core despite modular tool registration | High | Medium | Tool domains already split into `*_tools.py`; further extraction of core transport/connection into a `core.py` is deferred |
| R2 | **Remote Script is 6200+ lines, Python 2** — hard to test, no pip deps | High | High | Declarative handler maps help; no unit-test harness inside Live. Manual testing via `scripts/test/` |
| R3 | **Audio export impossible via API** | Certain | Medium | Max for Live device + `convert_to_mp3.py` workaround; documented in README and §8.9 |
| R4 | **Live version fragmentation** (10/11/12 API differences) | Medium | High | Three-tier capture fallback; `get_arrangement_clips` returns `[]` instead of crashing |
| R5 | **UDP packet loss** during high-frequency sweeps | Medium | Low | Fire-and-forget by design; final value usually lands; acceptable for DJ automation |
| R6 | **MCP server crash** mid-session | Low | High | `server_watchdog.py` auto-restart; `connection_health.py` state machine |
| R7 | **ElevenLabs API costs** | Medium | Low (money) | Tools marked with cost warnings; API key in `.env`, never committed |
| R8 | **Public repo exposure** of local filesystem paths / personal info in docs/scripts | Medium | Medium | `.gitignore` covers `.env`/`.venv`; a manual content review of 443 tracked files is still recommended |
| R9 | **Pre-existing lint debt** in `MCP_Server/` (E402, F821, E722) | High | Low | CI allows these with `\|\| true`; new code (`agentic_mix/`, `tests/`) is strict |
| R10 | **LangGraph / LangChain version drift** — declared `>=0.2.0`/`>=0.3.0` | Medium | Medium | CLI lazy-imports; AgentFlow fallback exists |
| R11 | **Single Live instance / localhost-only** | By design | Low | Documented; multi-host would require a protocol redesign |
| R12 | **`duplicate_clip_to_arrangement` main-thread restriction** | Certain | Low | Deferred to main-thread scheduler; documented in code |

## 11.2 Technical Debt

| Area | Debt | Notes |
|------|------|-------|
| `MCP_Server/server.py` | 5700+ lines, mixed transport + tools | Core transport could be extracted to `core.py`; tool bodies already modularized |
| `AbletonMCP_Remote_Script/__init__.py` | 6200+ lines, Python 2, single file | Could be split into multiple Remote Script modules if Live ever supports it; currently constrained by Live's loader |
| Lint | `MCP_Server/` has pre-existing Ruff warnings (E402, F821, E722) | CI lenient; incremental cleanup possible |
| Tests | Integration tests need a running Live; many `tests/test_legacy_*` excluded from CI | Standalone scripts in `scripts/test/`; no full pytest-of-Live harness |
| Docs sprawl | 20+ top-level `*.md` files (DUB_FEATURES, FAT_BEATZ, etc.) | Root is down to 6 feature guides; session summaries moved to `docs/archive/`, one-off scripts to `scripts/legacy/`. `scripts/check_repo_hygiene.py` now guards the root. |
| Scripts | 60+ files in `scripts/` (plus 24 test, 15 util, 15 legacy) with overlapping mix generators | Multiple `create_*_mix*.py` variants; consolidation deferred. Catalog: `docs/SCRIPTS.md` |
| `agentic_mix` vs `orchestration` | Two orchestrators must be kept behaviorally equivalent | Accepted trade-off (ADR-6) |
| `tests/gap_specs.py` + `tests/test_gap_*` | New contract/e2e tests for gap analysis | Recently added; not yet wired into CI `test` job explicitly |
| Parameter contract lies | `command_registry.py` and `tests/test_command_registry.py` declare `set_device_parameter.value` as `0.0-1.0` "normalized", but `_set_device_parameter` assigns it to `parameter.value` with no scaling, so callers must pass native units (Hz, dB, %, ms, beats). Tests pin `min_value == 0.0`/`max_value == 1.0`, so fixing the contract means changing registry, the two assertions, and regenerating `docs/TOOLS.md`. | Prose is corrected (AGENTS.md, §2.3, §12, docstrings); the machine-readable contract is not. Native values work today because nothing enforces `ParamSpec` bounds. |
| UDP capability vs registry | `_build_udp_handlers()` accepts 11 command types (includes `set_crossfader`), the registry declares 10 UDP commands. `set_crossfader_position` actually sends over TCP, so the extra handler is unreachable from the MCP layer. | Fixed values in `tests/test_command_registry.py` (`len(registry) == 20`, exact UDP set) block a one-line fix. |
| Docs vs code drift | Counts and structures drift silently (152 vs 120 tools, 10 vs 11 UDP, `_allowed_commands`/`_dispatch_command()` that never existed). | Re-derive numbers from code; see the "Keeping docs honest" checklist in `docs/README.md`. |

## 11.3 Deferred / Future Work

- Extract `server.py` transport core into `MCP_Server/core.py`.
- Consolidate the `scripts/create_*_mix*.py` family into a single parameterized generator.
- Add a Live-11 CI matrix (currently only structural validation on Ubuntu headless).
- Full pytest harness with mocked Live for the Remote Script handlers.
- Automatic Max-for-Live bang trigger (currently manual).
- Multi-host Ableton control (would require a redesigned protocol).
