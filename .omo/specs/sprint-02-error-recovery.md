# Sprint 02: Error Recovery + Connection Resilience

**Theme:** Survive network drops, Live crashes, and transient failures.
**Est. days:** 4 | **New tools:** 2-3 | **Risk:** Medium
**Dependencies:** None

## Goal
Make the MCP server resilient to connection failures. Currently, if Ableton Live restarts or the TCP socket drops, the server returns raw tracebacks or hangs. After this sprint, it auto-reconnects, returns structured errors, and surfaces health data via resources.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `MCP_Server/server.py` | Modify | Add reconnection logic to `AbletonConnection` / `get_ableton_connection()` |
| `MCP_Server/connection_health.py` | Create | Health tracking, ping timing, reconnect state |
| `MCP_Server/server_watchdog.py` | Modify | Stale connection detection + restart trigger |
| `MCP_Server/verify.py` | Modify | Integration with connection health |
| `tests/test_connection_health.py` | Create | Unit tests for health/reconnect logic |

## Deliverables

### 2.1 Reconnection Logic
Add auto-reconnect to `AbletonConnection` in `server.py`:
- Detect connection drop (socket error, timeout, empty response)
- Exponential backoff: retry at 1s, 2s, 4s intervals (max 3 retries)
- On reconnect: re-initialize by calling `get_session_info()` to verify
- If all retries fail: mark state as DISCONNECTED, keep trying
- Expose `connection_state: Literal["connected", "disconnected", "reconnecting", "error"]`

**Connection flow:**
```
send_command() → socket error → set state = "reconnecting"
  → wait 1s → retry → success? → set state = "connected" → return result
  → wait 2s → retry → success? → ...
  → wait 4s → retry → success? → set state = "disconnected" → raise ConnectionError
```

### 2.2 Structured Error Responses
All tools must return structured errors instead of tracebacks:
```json
{"error": "Connection to Ableton Live lost", "code": "LIVE_DISCONNECTED", "reconnecting": true}
{"error": "Track index out of range", "code": "INVALID_INDEX", "max_index": 7}
{"error": "Operation timed out after 5s", "code": "TIMEOUT", "retryable": true}
```

Error codes:
| Code | Meaning | Retryable |
|------|---------|-----------|
| `LIVE_DISCONNECTED` | No connection to Live | Yes |
| `LIVE_RECONNECTING` | Reconnecting, try again | Yes |
| `INVALID_INDEX` | Track/clip/device index out of range | No |
| `TIMEOUT` | Command took too long | Yes |
| `UNKNOWN_COMMAND` | Command not recognized by Remote Script | No |
| `INTERNAL_ERROR` | Unexpected error | Depends |
| `FILE_NOT_FOUND` | Path doesn't exist | No |

### 2.3 Connection Health Resource
Enhance `live://status` or add separate resource with:
- `connection_state`: connected | disconnected | reconnecting
- `last_ping_ms`: milliseconds (0 if disconnected)
- `uptime`: seconds since last successful connection
- `reconnect_count`: total reconnections this session
- `last_error`: last error message
- `last_error_timestamp`: ISO 8601

### 2.4 Watchdog Enhancement
Extend `server_watchdog.py`:
- If connection state is "disconnected" for > 30s, restart the entire MCP server process
- Log all reconnection attempts to `MCP_Server/logs/connection.log`
- Expose `watchdog_status()` tool: health check with restart count, uptime, last restart reason

### 2.5 Graceful Degradation
When Live is not running:
- Every tool returns `{"error": "Ableton Live not detected", "code": "LIVE_NOT_RUNNING"}`
- All resource URIs return `{"error": "LIVE_NOT_RUNNING"}` 
- `live://status` still works (returns connection info without Live)

## API Surface

### New Tools
| Tool | Signature | Returns |
|------|-----------|---------|
| `get_connection_health` | `(ctx) -> str` | JSON health + diagnostics |
| `reset_connection` | `(ctx) -> str` | Force reconnect attempt |

### Enhanced Resource
- `live://status` gains fields: `connection_state`, `last_ping_ms`, `uptime`, `reconnect_count`

## Acceptance Criteria
```bash
# Connection resilience
# 1. Start MCP server, verify state = connected
# 2. Kill Ableton Live, call any tool → returns LIVE_DISCONNECTED error
# 3. State transitions to reconnecting, then disconnected
# 4. Restart Live, tool call succeeds again after reconnect

# Structured errors
# 5. get_track_info(999) → INVALID_INDEX with max_tracks
# 6. analyze_als_project("nonexistent.als") → FILE_NOT_FOUND
# 7. query_device_knowledge("Nope") → empty result (NOT an error - valid query)

# Watchdog
# 8. 30s after disconnect without reconnect → server restart logged
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Reconnect loop floods logs | Medium | Exponential backoff + max retry cap |
| Race condition: reconnect + concurrent tool call | Medium | Lock during reconnect; queue pending calls |
| Socket half-open detection | High | Add heartbeat/ping every 30s |
| Watchdog kills healthy server | Low | Only trigger after 3 retries + 30s timeout |

## Must NOT Do
- Do NOT modify the Remote Script (`__init__.py`) — reconnection is server-side only
- Do NOT add new socket protocols or ports
- Do NOT make read-only tools retry (read-only should fail fast)
- Do NOT implement stateful retry queues that could deadlock
