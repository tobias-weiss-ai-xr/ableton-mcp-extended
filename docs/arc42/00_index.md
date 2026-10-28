# Architecture Documentation — Ableton MCP Extended

**Format:** [arc42](https://arc42.org/) template, one file per section.

**System:** Ableton MCP Extended — control Ableton Live via AI assistants using
the Model Context Protocol, with a dual TCP/UDP transport, agentic mix
generation, and ElevenLabs voice integration.

## Contents

| § | Section | File |
|---|---------|------|
| 1 | Introduction and Goals | [01_introduction_and_goals.md](01_introduction_and_goals.md) |
| 2 | Architecture Constraints | [02_architecture_constraints.md](02_architecture_constraints.md) |
| 3 | Context and Scope | [03_context_and_scope.md](03_context_and_scope.md) |
| 4 | Solution Strategy | [04_solution_strategy.md](04_solution_strategy.md) |
| 5 | Building Block View | [05_building_block_view.md](05_building_block_view.md) |
| 6 | Runtime View | [06_runtime_view.md](06_runtime_view.md) |
| 7 | Deployment View | [07_deployment_view.md](07_deployment_view.md) |
| 8 | Cross-cutting Concepts | [08_cross_cutting_concepts.md](08_cross_cutting_concepts.md) |
| 9 | Architecture Decisions | [09_architecture_decisions.md](09_architecture_decisions.md) |
| 10 | Quality Requirements | [10_quality_requirements.md](10_quality_requirements.md) |
| 11 | Risks and Technical Debt | [11_risks_and_technical_debt.md](11_risks_and_technical_debt.md) |
| 12 | Glossary | [12_glossary.md](12_glossary.md) |

## How to read this

- **Quick orientation:** §1 (goals) → §3 (context) → §5 (building blocks).
- **Operators / integrators:** §7 (deployment) + §8 (cross-cutting) + §12 (glossary).
- **Contributors adding a tool:** §4 (solution strategy) + §5.2 (module map) + §8.1–8.3 (conventions) + ADR-3/ADR-4.
- **Troubleshooting connectivity:** §6.2–6.3 (runtime) + §8.4 (health) + ADR-1.
- **Understanding mix generation:** §5.4 + §6.4 + ADR-6.

## Source files referenced

The documentation reflects the codebase as of the current `main` branch. Key
source locations:

- `MCP_Server/server.py` — core MCP server (~120 tools, FastMCP host)
- `MCP_Server/*_tools.py` — 14 tool-domain modules (250+ tools total)
- `MCP_Server/command_registry.py` — command contract registry
- `MCP_Server/connection_health.py` — connection state machine
- `AbletonMCP_Remote_Script/__init__.py` — Live-embedded Remote Script
- `agentic_mix/` — LangGraph mix-generation pipeline
- `orchestration/agentflow_runner.py` — AgentFlow DAG runner (fallback)
- `elevenlabs_mcp/server.py` — ElevenLabs MCP server
- `config/system.yaml` — ports, UDP whitelist, kits, patterns, presets
- `pyproject.toml` — entry points and dependencies
- `.github/workflows/ci.yml` — CI pipeline
