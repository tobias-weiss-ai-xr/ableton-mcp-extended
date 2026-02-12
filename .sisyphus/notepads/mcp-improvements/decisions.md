# MCP Improvements - Decisions

## Session Context
- Plan: MCP Improvements
- Session ID: ses_3bf0c1c56fferuQ2zr0B1uurJe
- Started: 2026-02-09T05:50:51.357Z

## Architecture & Design Decisions (Append as made)

### Task 1: Dual-Server Architecture Design (2025-02-09)

**Decision 1: Dual-Server Approach**
- **Choice:** Separate TCP and UDP servers in single codebase
- **Rationale:** Maintains backward compatibility (TCP unchanged) while adding UDP for performance
- **Alternative Considered:** Hybrid single-server with protocol negotiation (rejected due to complexity)
- **Impact:** Both servers run independently, share `self._song` via main thread scheduling

**Decision 2: UDP Command Scope**
- **Choice:** Only 9 parameter update commands use UDP (reversible, high-frequency)
- **Rationale:** Minimize risk, focus on proven-safe operations, fire-and-forget acceptable
- **Alternative Considered:** All state modifications use UDP (rejected due to criticality)
- **Impact:** TCP continues handling 76 commands (all critical operations, reads, modifications)

**Decision 3: Fire-and-Forget UDP Pattern**
- **Choice:** UDP server does not send responses, logs errors only
- **Rationale:** Acceptable packet loss (<5%), self-correcting via continuous updates, matches AbletonMCP_UDP pattern
- **Alternative Considered:** Acknowledgment-based UDP (rejected due to complexity overhead)
- **Impact:** Client code uses TCP fallback on critical errors, final state always correct (last update wins)

**Decision 4: Thread Safety Strategy**
- **Choice:** Main thread serialization via `self.schedule_message(0, task)` for all Live API calls
- **Rationale:** Proven pattern in existing code, ensures thread safety, minimal overhead
- **Alternative Considered:** Mutex locks (rejected due to deadlock risk, complexity)
- **Impact:** Both TCP and UDP routes through same main thread executor, no race conditions

**Decision 5: Port Configuration**
- **Choice:** TCP on 9877 (existing), UDP on 9878 (+1 offset)
- **Rationale:** TCP already proven in production, minimal conflict risk with +1 offset
- **Alternative Considered:** Random UDP port (rejected for predictability, configuration complexity)
- **Impact:** Simple, predictable configuration, easy to firewall if needed

**Decision 6: Message Format**
- **Choice:** JSON for both TCP and UDP (identical structure)
- **Rationale:** Consistency with existing code, minimal parsing overhead, easy debugging
- **Alternative Considered:** Binary format for UDP (rejected due to complexity, zero benefit for first implementation)
- **Impact:** Code reuse possible, minimal code changes, easier maintenance

**Decision 7: Error Handling**
- **Choice:** TCP: strict error responses to client; UDP: log errors, no response
- **Rationale:** TCP clients need to handle failures; UDP accepts loss as acceptable
- **Alternative Considered:** Both protocols use same error handling (rejected - needs differ)
- **Impact:** Clean separation of concerns, appropriate to protocol characteristics