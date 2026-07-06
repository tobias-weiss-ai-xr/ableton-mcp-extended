# sprint-02-error-recovery - Work Plan

## TL;DR (For humans)

**What you'll get:** The MCP server stops returning raw tracebacks and hanging when Ableton Live crashes, restarts, or the network drops. After this sprint, the server auto-reconnects with exponential backoff (1s→2s→4s), returns clean structured JSON errors with typed codes instead of Python exceptions, and surfaces real-time health data via MCP resources.

**Why this approach:** Currently, a Live restart during a session causes every subsequent tool call to return an unhandled traceback or hang indefinitely. That's unusable in production. The fix is server-side only — no changes to the Remote Script. The core insight is a health state machine (`connected → reconnecting → disconnected`) that all connection code routes through, with a watchdog that only intervenes after 3 retries + 30s of dead air.

**What it will NOT do:** Modify the Remote Script (`AbletonMCP_Remote_Script/__init__.py`), add new socket protocols or ports, make read-only tools retry (they fail fast), or implement stateful retry queues that could deadlock.

**Effort:** Small-Medium (4 days, 5 todos)
**Risk:** Medium — socket half-open detection is tricky; race conditions between reconnect and concurrent tool calls
**Decisions to sanity-check:** State machine lock strategy during reconnect; which errors are retryable vs fail-fast

---

> TL;DR (machine): SM effort, Medium risk (socket half-open, reconnect concurrency). 5 deliverables across 2 waves. Wave 1: connection health module + reconnect logic + structured errors (foundation). Wave 2: health resource/tools + watchdog/graceful degradation (polish).

## Scope
### Must have
- Connection state machine: `connected | reconnecting | disconnected | error` with proper transitions
- Exponential backoff reconnect: 1s, 2s, 4s intervals, max 3 retries, then DISCONNECTED state
- On reconnect: call `get_session_info()` to verify the connection is valid
- Structured error responses: all tools return `{"error": "...", "code": "LIVE_DISCONNECTED", ...}` instead of tracebacks
- Error codes: `LIVE_DISCONNECTED`, `LIVE_RECONNECTING`, `INVALID_INDEX`, `TIMEOUT`, `UNKNOWN_COMMAND`, `INTERNAL_ERROR`, `FILE_NOT_FOUND`, `LIVE_NOT_RUNNING`
- Connection health resource fields: `connection_state`, `last_ping_ms`, `uptime`, `reconnect_count`, `last_error`, `last_error_timestamp`
- New tools: `get_connection_health` (health + diagnostics JSON), `reset_connection` (force reconnect)
- Watchdog: restart MCP server after 30s of DISCONNECTED state, log to `MCP_Server/logs/connection.log`
- Graceful degradation: all tools return `LIVE_NOT_RUNNING` when Live absent, `live://status` still works

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do NOT modify the Remote Script (`AbletonMCP_Remote_Script/__init__.py`) — reconnection is server-side only
- Do NOT add new socket protocols or ports
- Do NOT make read-only tools retry (read-only should fail fast)
- Do NOT implement stateful retry queues that could deadlock
- Do NOT add new pip dependencies
- Do NOT modify existing tool signatures

## Verification strategy
> Zero human intervention — all verification is agent-executed.
- Test decision: tests-after + code inspection for each todo
- Evidence: `.omo/evidence/task-<N>-sprint-02-error-recovery.<ext>`

## Execution strategy
### Parallel execution waves
| Wave | Focus | Todos | Est. days |
|------|-------|-------|-----------|
| 1 | Core state machine + reconnect + structured errors | 1, 2, 3 | 2 |
| 2 | Health resource/tools + watchdog/graceful degradation | 4, 5 | 2 |

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. connection_health.py | None | 2, 3, 4, 5 | None (foundation) |
| 2. Reconnection logic | 1 | 4, 5 | 3 |
| 3. Structured errors | 1 | None | 2 |
| 4. Health resource + tools | 1, 2 | 5 | None |
| 5. Watchdog + graceful degradation | 1, 2, 4 | None | None |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Create `MCP_Server/connection_health.py` — connection state machine + health tracking
  What to do / Must NOT do:
  Create `MCP_Server/connection_health.py` with a thread-safe `ConnectionHealth` class:
  - State machine: `connection_state: Literal["connected", "disconnected", "reconnecting", "error"]`
  - `set_state(state, error_msg=None)` — transitions with validation (can't go from "connected" to "connected")
  - `record_reconnect()` — increments `reconnect_count`, resets uptime
  - `record_ping(latency_ms)` — updates `last_ping_ms` with rolling window of last 5 pings
  - `record_error(message)` — sets `last_error` and `last_error_timestamp` (ISO 8601)
  - `get_health()` — returns dict: `connection_state`, `last_ping_ms`, `uptime`, `reconnect_count`, `last_error`, `last_error_timestamp`
  - `start_time` — set on first successful connection, used for `uptime` calculation
  - Thread safety: use `threading.Lock` for all state mutations
  - Expose module-level singleton `connection_health = ConnectionHealth()` and a getter
  - New constants module or dict: `RECONNECT_DELAYS = [1, 2, 4]`, `MAX_RETRIES = 3`, `WATCHDOG_TIMEOUT = 30`

  Must NOT: Import from `server.py` (creates circular dep). Must NOT do file I/O. Must NOT have any socket code.

  Parallelization: Wave 1 | Blocked by: None | Blocks: Todos 2, 3, 4, 5
  References:
  - State machine design: spec section 2.1 lines 22-35 (connection flow diagram)
  - Error codes: spec section 2.2 lines 46-55
  - Health fields: spec section 2.3 lines 58-63
  - Watchdog timeout: spec section 2.4 line 67
  - AbletonConnection current code: `MCP_Server/server.py:53-306`
  - Thread safety: `threading.Lock` pattern in existing codebase (check advanced_tools.py for examples)

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  from MCP_Server.connection_health import ConnectionHealth, connection_state, connected, disconnected, reconnecting, error
  # Create instance and test state machine
  ch = ConnectionHealth()
  assert ch.state == 'disconnected', f'Expected disconnected, got {ch.state}'
  ch.set_state('connected')
  assert ch.state == 'connected', f'Expected connected, got {ch.state}'
  ch.record_ping(5.0)
  ch.record_reconnect()
  health = ch.get_health()
  assert health['connection_state'] == 'connected'
  assert health['reconnect_count'] == 1
  assert health['last_ping_ms'] == 5.0
  assert 'uptime' in health
  ch.set_state('error', 'test error')
  assert ch.state == 'error'
  health = ch.get_health()
  assert health['last_error'] == 'test error'
  assert health['last_error_timestamp'] is not None
  print('connection_health.py state machine OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Create ConnectionHealth, transition disconnected→connected→reconnecting→disconnected, verify state sequence valid
  - HAPPY: Record 3 pings (5ms, 10ms, 7ms), verify last_ping_ms = most recent
  - HAPPY: Record 3 reconnects, verify reconnect_count = 3
  - FAILURE: Try set_state('connected') when already 'connected', should be a no-op or log warning (not crash)
  - FAILURE: get_health() when never connected, uptime should be 0, last_ping_ms should be 0.0
  Evidence: .omo/evidence/task-1-sprint-02-error-recovery.txt
  Commit: Y | feat(resilience): add ConnectionHealth state machine module

- [ ] 2. Add reconnection logic to `AbletonConnection` in `MCP_Server/server.py`
  What to do / Must NOT do:
  Modify `AbletonConnection` class and `get_ableton_connection()` in `MCP_Server/server.py`:
  - Import `connection_health` singleton from `MCP_Server.connection_health`
  - Modify `send_command()`:
    - Before sending: if state is "reconnecting", raise `ConnectionError("Reconnecting...")` immediately (concurrent call guard)
    - On `socket.timeout`: set state → "error" with "Socket timeout waiting for Ableton response", raise ConnectionError
    - On `ConnectionError / BrokenPipeError / ConnectionResetError`: trigger reconnect flow
    - On `json.JSONDecodeError`: set state → "error" with "Invalid JSON response", raise ConnectionError (not retryable)
    - On generic `Exception`: set state → "error", raise ConnectionError
  - New method `_attempt_reconnect()`:
    - Set state → "reconnecting"
    - Retry loop: delays [1s, 2s, 4s] (from spec 2.1)
    - Each attempt: create fresh socket, connect, send `get_session_info()`, verify response
    - If success: set state → "connected", call `connection_health.record_reconnect()`, return True
    - If all fail: set state → "disconnected", call `connection_health.set_state("disconnected", "All reconnection attempts failed")`, return False
  - Modify `get_ableton_connection()`:
    - Use connection_health state check instead of raw socket probe
    - On first connect success: `connection_health.set_state("connected")`
    - Call `connection_health.record_ping(latency)` after successful `get_session_info()`
  - Modify `send_command_udp()`: UDP fire-and-forget should NOT trigger reconnect (connectionless by design)
  - On `reconnect` from error state in `send_command()`: call `_attempt_reconnect()` in-line (blocking), if it returns True, retry the original command once; if it fails, raise `ConnectionError` with `LIVE_DISCONNECTED` code

  Must NOT: Import `server.py` from `connection_health.py` (circular dep). Must NOT: Make UDP commands retry. Must NOT: Add threading/locking beyond what's needed for state checks. Must NOT: Block for more than ~10s total (1+2+4+retry = ~8s max).

  Parallelization: Wave 1 | Blocked by: Todo 1 | Blocks: Todos 4, 5
  References:
  - `AbletonConnection` class: `MCP_Server/server.py:53-306`
  - `send_command()`: `MCP_Server/server.py:185-306`
  - `get_ableton_connection()`: `MCP_Server/server.py:313-370`
  - `send_command_udp()`: `MCP_Server/server.py:84-134`
  - Reconnect flow: spec section 2.1 lines 29-35
  - Exponential backoff: spec section 2.1 lines 23-24
  - Connection validation: spec section 2.1 line 25 (get_session_info to verify)

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify the reconnection logic structure is present
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'connection_health' in content, 'connection_health import missing'
  assert '_attempt_reconnect' in content or 'attempt_reconnect' in content, 'reconnect method missing'
  # Verify RECONNECT_DELAYS or equivalent is referenced
  assert 'RECONNECT_DELAYS' in content or '[1, 2, 4]' in content or '1, 2, 4' in content.replace(' ', ''), 'exponential backoff delays missing'
  print('Reconnection logic structure verified')
  "
  python -c "
  # Compile check
  compile(open('MCP_Server/server.py').read(), 'MCP_Server/server.py', 'exec')
  print('server.py compiles OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Normal `send_command()` with live Ableton, no reconnect triggered, state stays connected
  - HAPPY: After socket drops, `send_command()` triggers reconnect, connects on retry 2 (after 2s), retries original command, returns result
  - HAPPY: After reconnect, `connection_health.reconnect_count` increments
  - FAILURE: All 3 reconnect attempts fail, state set to "disconnected", `ConnectionError` raised
  - FAILURE: Tool call during "reconnecting" state (concurrent call), raises immediately with LIVE_RECONNECTING error
  - FAILURE: UDP command during disconnect, does NOT trigger reconnect (logs and returns)
  Evidence: .omo/evidence/task-2-sprint-02-error-recovery.txt
  Commit: Y | feat(resilience): add exponential-backoff reconnection logic to AbletonConnection

- [ ] 3. Add structured error responses to all MCP tools
  What to do / Must NOT do:
  Add error-handling infrastructure so all tools return structured JSON errors instead of raw tracebacks:
  - Create error code constants: `ERROR_CODES` dict mapping code strings to `{"retryable": bool, "description": str}` in `connection_health.py` or new `MCP_Server/error_codes.py`
  - Error codes (from spec):
    - `LIVE_DISCONNECTED`: No connection to Live | retryable=True
    - `LIVE_RECONNECTING`: Reconnecting, try again | retryable=True
    - `LIVE_NOT_RUNNING`: Ableton Live not detected | retryable=True
    - `INVALID_INDEX`: Track/clip/device index out of range | retryable=False
    - `TIMEOUT`: Command took too long | retryable=True
    - `UNKNOWN_COMMAND`: Command not recognized | retryable=False
    - `INTERNAL_ERROR`: Unexpected error | retryable=False
    - `FILE_NOT_FOUND`: Path doesn't exist | retryable=False
  - Add function `make_error_response(code, message, extra=None) -> dict` that returns:
    ```json
    {"error": "<human message>", "code": "<ERROR_CODE>", "retryable": true/false, ...extra}
    ```
  - Modify all `@server.tool` decorated functions and tool registration wrappers in `server.py` to catch exceptions and return `make_error_response(...)` instead of letting them propagate
  - How: Create a wrapper/decorator `@handle_errors` that wraps each tool function's body:
    - Catches `ConnectionError` → maps to LIVE_DISCONNECTED or LIVE_RECONNECTING based on current state
    - Catches `IndexError` / `ValueError` from bad indices → LIVE_RECONNECTING... wait, actually:
    - Pattern match errors: Connection error → LIVE_DISCONNECTED. Timeout → TIMEOUT. IndexError → INVALID_INDEX. FileNotFound → FILE_NOT_FOUND. Everything else → INTERNAL_ERROR
    - Log the full traceback before returning the clean error response

  - The modification approach:
    - Add `handle_errors` decorator function in `server.py` (or import from `connection_health.py`)
    - Apply `@handle_errors` to every registered `@server.tool` function
    - For submodule tools (advanced_tools, midi_effects, etc.), the submodule registration functions already wrap tool creation; add error handling there

  - Graceful degradation integration: when `get_ableton_connection()` detects Live is not running (initial connection fails), tools should return `LIVE_NOT_RUNNING` instead of a generic connection error

  Must NOT: Suppress tracebacks from logs (log the full traceback, return clean error to client). Must NOT: Change any tool's return format for successful calls. Must NOT: Add error handling to read-only tools differently than modifying tools (same decorator, same behavior — they just shouldn't encounter most errors).

  Parallelization: Wave 1 | Blocked by: Todo 1 | Blocks: None
  References:
  - Error codes table: spec section 2.2 lines 46-55
  - Graceful degradation: spec section 2.5 lines 71-75
  - Tool registration pattern: `MCP_Server/server.py:747-765` (mcp = FastMCP(...))
  - Example submodule pattern: `MCP_Server/advanced_tools.py:48` register_advanced_tools
  - Connection error handling pattern: spec section 2.2 lines 38-43 (structured error JSON examples)

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  # Verify error handling infrastructure exists
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'make_error_response' in content or 'handle_errors' in content or 'error_response' in content, 'error handling functions missing'
  assert 'LIVE_DISCONNECTED' in content or 'DISCONNECTED' in content, 'error codes missing'
  assert 'INVALID_INDEX' in content or 'INVALID' in content, 'INVALID_INDEX error code missing'
  assert 'INTERNAL_ERROR' in content or 'INTERNAL' in content, 'INTERNAL_ERROR code missing'
  print('Structured error handling infrastructure verified')
  "
  python -c "
  # Verify Python compiles
  compile(open('MCP_Server/server.py').read(), 'MCP_Server/server.py', 'exec')
  print('server.py compiles OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call tool with valid args, returns normal result (no error wrapper)
  - HAPPY: Call tool while disconnected, returns `{"error": "Connection to Ableton Live lost", "code": "LIVE_DISCONNECTED", "retryable": true}`
  - HAPPY: Call `get_track_info(999)`, returns `{"error": "Track index out of range", "code": "INVALID_INDEX", "max_index": 7}`
  - FAILURE: Query device knowledge for "Nope" returns empty result (NOT an error — spec AC #7)
  - FAILURE: Error during error handling itself, logs full traceback and returns INTERNAL_ERROR
  Evidence: .omo/evidence/task-3-sprint-02-error-recovery.txt
  Commit: Y | feat(resilience): add structured JSON error responses to all MCP tools

- [ ] 4. Add connection health tools + enhance `live://status` resource
  What to do / Must NOT do:
  Add new MCP tools and enhance the existing `live://status` MCP resource:

  New tool `get_connection_health(ctx) -> str`:
  - Returns `json.dumps(connection_health.get_health())` — full health + diagnostics
  - Always works, even when Live is not connected (returns current state with Live not running)
  - Register in `server.py` using `@server.tool` pattern

  New tool `reset_connection(ctx) -> str`:
  - Forces `get_ableton_connection()` to disconnect and reconnect
  - Sets state to "reconnecting" → attempts fresh connection
  - Returns current health state after attempt
  - If already disconnected, attempts a fresh `connect()`
  - Register in `server.py` using `@server.tool` pattern

  Enhanced `live://status` resource:
  - Locate the existing `live://status` resource registration (likely in `server.py`)
  - Add extra fields from `connection_health.get_health()`:
    - `connection_state`: connected | disconnected | reconnecting | error
    - `last_ping_ms`: milliseconds (0.0 if disconnected)
    - `uptime`: seconds since last successful connection
    - `reconnect_count`: total reconnections this session
  - When Live is not running: `live://status` still works, returns connection info without Live session data
  - The resource should merge existing session info with health data

  Must NOT: Add new TCP commands to the Remote Script. Must NOT: Create new files (add to server.py). Must NOT: Add new pip dependencies.

  Parallelization: Wave 2 | Blocked by: Todos 1, 2 | Blocks: Todo 5
  References:
  - Existing resource pattern: `MCP_Server/server.py` `@mcp.resource` decorators (search for "live://status")
  - get_session_info wrapper pattern: existing tool functions in `server.py`
  - Health data: `connection_health` from `MCP_Server.connection_health` (Todo 1)
  - Connection state spec: section 2.3 lines 57-63
  - New tools spec: section "API Surface" lines 79-85
  - Graceful degradation: section 2.5 lines 71-75 (live://status still works without Live)

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'get_connection_health' in content, 'get_connection_health tool not found'
  assert 'reset_connection' in content, 'reset_connection tool not found'
  # Verify live://status has health fields
  assert 'connection_state' in content or 'connection_health' in content or 'last_ping_ms' in content, 'health fields not in live://status'
  print('Health tools + resource enhancement verified')
  "
  python -c "
  compile(open('MCP_Server/server.py').read(), 'MCP_Server/server.py', 'exec')
  print('server.py compiles OK')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Call `get_connection_health()` while connected, returns full health with state=connected, ping ms, uptime
  - HAPPY: Call `get_connection_health()` while disconnected, returns state=disconnected, uptime=0
  - HAPPY: Call `reset_connection()` while connected, disconnects and reconnects, returns new health state
  - HAPPY: Read `live://status` resource, verify it includes connection_state, last_ping_ms, uptime, reconnect_count
  - FAILURE: Call `get_connection_health()` when Live never started, returns LIVE_NOT_RUNNING but still returns health structure
  - FAILURE: `live://status` resource accessible even when Live is not running
  Evidence: .omo/evidence/task-4-sprint-02-error-recovery.txt
  Commit: Y | feat(resilience): add get_connection_health, reset_connection tools + enhance live://status resource

- [ ] 5. Enhance watchdog + graceful degradation
  What to do / Must NOT do:
  Modify `MCP_Server/server_watchdog.py`:
  - Import `connection_health` from `MCP_Server.connection_health`
  - In the main monitoring loop: check `connection_health.state` periodically (every ~5s instead of 60s for faster failure detection)
  - If state is "disconnected" for > 30s (track using `disconnected_since` from `connection_health.last_error_timestamp` or a separate timer):
    - Log to `MCP_Server/logs/connection.log` (create this directory/file if needed)
    - Trigger `restart_server()` to restart the MCP server process
    - Log restart count, reason, and timestamp to connection.log
  - Add new function `watchdog_status() -> dict` (callable from main) that returns:
    - `restart_count`: total server restarts
    - `uptime`: seconds since last watchdog start
    - `last_restart_reason`: string reason for last restart
    - `last_restart_timestamp`: ISO 8601
    - `connection_state`: delegated from `connection_health.state`
  - Log all reconnection attempts to `MCP_Server/logs/connection.log` with format:
    `[ISO_TIMESTAMP] RECONNECT_ATTEMPT <n>/<max> - <result>`
    `[ISO_TIMESTAMP] RECONNECT_SUCCESS - after <n> attempt(s)`
    `[ISO_TIMESTAMP] RECONNECT_FAILED - All <max> attempts exhausted`
    `[ISO_TIMESTAMP] SERVER_RESTART - reason: <reason>`
  - Add logging handler: `logging.FileHandler("MCP_Server/logs/connection.log")`

  Graceful degradation in `server.py`:
  - When Ableton Live is not detected (all initial connection attempts fail):
    - Every `@server.tool` function returns `{"error": "Ableton Live not detected", "code": "LIVE_NOT_RUNNING"}`
    - This is handled by the `@handle_errors` decorator from Todo 3: when `get_ableton_connection()` raises because no Live is available at all (not just disconnected), the handler catches it and returns LIVE_NOT_RUNNING
    - `live://status` resource: returns connection info (state=disconnected, reconnect_count=0) without session data
  - `get_ableton_connection()` should distinguish between "was connected but dropped" (LIVE_DISCONNECTED) and "never was connected" (LIVE_NOT_RUNNING) — add this distinction

  Must NOT: Use creationflags on Linux (causes AttributeError — already handled with `sys.platform == "win32"` check, verify same pattern). Must NOT: Periodically kill a healthy server (only restart after 3 retries + 30s timeout). Must NOT: Modify the main loop interval for health checks to be faster than 5s (avoid busy-looping).

  Parallelization: Wave 2 | Blocked by: Todos 1, 2, 4 | Blocks: None
  References:
  - Watchdog current code: `MCP_Server/server_watchdog.py` (200 lines)
  - `is_server_running()`: `server_watchdog.py:36-46`
  - `restart_server()`: `server_watchdog.py:49-70`
  - Graceful degradation: spec section 2.5 lines 71-75
  - Watchdog spec: spec section 2.4 lines 66-69
  - `connection_health` module: `MCP_Server/connection_health.py` (Todo 1)
  - `handle_errors` decorator: `MCP_Server/server.py` (Todo 3)

  Acceptance criteria (agent-executable):
  ```bash
  python -c "
  with open('MCP_Server/server_watchdog.py') as f:
      content = f.read()
  assert 'connection_health' in content or 'ConnectionHealth' in content, 'connection_health import missing'
  assert 'watchdog_status' in content or 'def watchdog_status' in content, 'watchdog_status function missing'
  assert 'connection.log' in content or 'connection_log' in content, 'connection.log logging missing'
  assert 'MCP_Server/logs' in content or 'logs/connection' in content, 'logs directory reference missing'
  print('Watchdog enhancement verified')
  "
  python -c "
  compile(open('MCP_Server/server_watchdog.py').read(), 'MCP_Server/server_watchdog.py', 'exec')
  print('server_watchdog.py compiles OK')
  "
  python -c "
  with open('MCP_Server/server.py') as f:
      content = f.read()
  assert 'LIVE_NOT_RUNNING' in content, 'LIVE_NOT_RUNNING error code missing'
  print('Graceful degradation verified')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: Live disconnected for >30s, watchdog triggers restart, connection.log records the restart
  - HAPPY: Call `watchdog_status()`, returns restart_count, uptime, last_restart_reason
  - HAPPY: During disconnect, all tools return LIVE_DISCONNECTED or LIVE_RECONNECTING
  - HAPPY: When Ableton never started (initial connect failed), tools return LIVE_NOT_RUNNING
  - HAPPY: `live://status` resource accessible without Live, returns connection info sans session data
  - FAILURE: Watchdog triggers restart while server is processing a command — server process is cleanly terminated
  - FAILURE: Reconnection succeeds before 30s watchdog timeout, no unnecessary restart
  Evidence: .omo/evidence/task-5-sprint-02-error-recovery.txt
  Commit: Y | feat(resilience): enhance watchdog with disconnect detection + graceful degradation on Live absence

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: Verify all 5 deliverables exist, all scope boundaries respected, no Remote Script modifications
- [ ] F2. Code quality review: All `.py` files pass `python -c "compile(open(f).read(), f, 'exec')"`, no syntax errors
- [ ] F3. Unit tests pass: Run `MCP_Server/connection_health.py` state machine tests from AC of Todo 1
- [ ] F4. Scope fidelity: grep for Must NOT have violations (no Remote Script changes, no new ports/protocols, no new pip deps)

## Commit strategy
One commit per todo, conventional commits format with scope prefix:
- feat(resilience): add ConnectionHealth state machine module
- feat(resilience): add exponential-backoff reconnection logic to AbletonConnection
- feat(resilience): add structured JSON error responses to all MCP tools
- feat(resilience): add get_connection_health, reset_connection tools + enhance live://status resource
- feat(resilience): enhance watchdog with disconnect detection + graceful degradation on Live absence

No squashing — each commit is independently testable. Tags: none.

## Success criteria
- Connection state machine correctly transitions through all states
- Reconnection with exponential backoff completes within ~8s max
- All tools return structured JSON errors (no raw tracebacks)
- Connection health resource returns real-time state, ping, uptime, reconnect count
- Watchdog restarts server after 30s of disconnect, logs all attempts
- All tools return LIVE_NOT_RUNNING when Ableton is absent; `live://status` still works
- No changes to Remote Script (`AbletonMCP_Remote_Script/__init__.py`)
