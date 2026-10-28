# 10. Quality Requirements

## 10.1 Quality Tree

```
                        ┌──────────────────┐
                        │  ableton-mcp-extended │
                        └────────┬─────────┘
          ┌──────────────┬───────┴───────┬──────────────┐
      Functionality   Reliability   Performance   Maintainability
```

## 10.2 Quality Scenarios

| ID | Quality | Scenario | Expectation |
|----|---------|----------|-------------|
| QS-1 | Functionality | AI creates a 4-track dub-techno session from scratch | All tools succeed; session plays in Live |
| QS-2 | Functionality | Agentic pipeline generates a 10-min mix | `langgraph-mix` completes without manual intervention |
| QS-3 | Reliability | Live restarted mid-session | MCP server reconnects within 3 retries (≤ 7 s) |
| QS-4 | Reliability | UDP packet dropped during a sweep | Sweep continues; no crash; final value lands within ≤ 1 missed frame |
| QS-5 | Performance | DJ-style parameter sweep (50 updates/s) | UDP path sustains ≥ 50 updates/s with < 5 ms per update |
| QS-6 | Performance | `get_session_overview` with 50 tracks | TCP response < 100 ms |
| QS-7 | Maintainability | Add a new MCP tool | One handler in Remote Script + one `@server.tool` + one `CommandSpec`; no core refactor |
| QS-8 | Maintainability | Add a new genre template | One entry in `config/system.yaml` + one sound set; no code change |
| QS-9 | Portability | Run on Live 11 vs Live 12 | Capture fallback selects the right API; no hard failure |
| QS-10 | Security | Malicious/typo'd UDP command | Remote Script rejects non-whitelisted commands |
| QS-11 | Operability | MCP server crashes | `server_watchdog.py` restarts within 30 s |
| QS-12 | Interoperability | Any MCP-compatible client (Claude, Cursor, custom) | stdio JSON-RPC works with all; no client-specific code |

## 10.3 Measurable Targets

| Metric | Target | Measured by |
|--------|--------|-------------|
| Tool count | ≥ 100 | `docgen.py` / `grep -c "@server.tool"` (currently ~250) |
| TCP round-trip latency | ≤ 50 ms typical | `scripts/test/test_connection.py` |
| UDP update latency | ≤ 5 ms | `scripts/test/test_performance_udp.py` |
| Reconnect success | ≥ 99 % within 3 retries | `connection_health.py` counters |
| Test coverage (new code) | Ruff-clean + pytest pass | CI `lint` + `test` jobs |
| Capture fallback | Works on Live 10/11/12 | `run_basic_demo.py` |
| Mix generation | Completes 10-min mix end-to-end | `scripts/create_10min_mix*.py` |

## 10.4 Non-functional Constraints

- **Latency-critical path:** UDP parameter updates (DJ sweeps). Must stay fire-and-forget.
- **Correctness-critical path:** TCP structural ops (create/delete/quantize). Must be reliable and idempotent where possible.
- **Determinism:** Given identical Live state + identical tool sequence, the musical result is deterministic (UDP timing jitter aside).
- **Resource:** SQLite browser cache keeps memory flat across long sessions.
