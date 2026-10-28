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
| Docs sprawl | 20+ top-level `*.md` files (DUB_FEATURES, FAT_BEATZ, BREAKTHROUGH_SUMMARY, etc.) | Historical; `docs/arc42/` (this set) provides the canonical architecture view |
| Scripts | 135 files in `scripts/` with overlapping mix generators | Multiple `create_*_mix*.py` variants; consolidation deferred |
| `agentic_mix` vs `orchestration` | Two orchestrators must be kept behaviorally equivalent | Accepted trade-off (ADR-6) |
| `tests/gap_specs.py` + `tests/test_gap_*` | New contract/e2e tests for gap analysis | Recently added; not yet wired into CI `test` job explicitly |

## 11.3 Deferred / Future Work

- Extract `server.py` transport core into `MCP_Server/core.py`.
- Consolidate the `scripts/create_*_mix*.py` family into a single parameterized generator.
- Add a Live-11 CI matrix (currently only structural validation on Ubuntu headless).
- Full pytest harness with mocked Live for the Remote Script handlers.
- Automatic Max-for-Live bang trigger (currently manual).
- Multi-host Ableton control (would require a redesigned protocol).
