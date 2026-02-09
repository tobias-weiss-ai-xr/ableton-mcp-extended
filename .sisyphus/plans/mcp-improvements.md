# Improve ableton-mcp-extended with New MCP Features

## TL;DR

> **Quick Summary**: Add dual-server (TCP + UDP) architecture for real-time parameter control, implement Max for Live integration for audio analysis, create advanced automation system with envelope curves and macros, expand session/project management capabilities.

> **Deliverables**:
> - Dual-server Remote Script (TCP existing + UDP new, Port 9878)
> - 85 MCP tool UDP variants (fire-and-forget high-frequency operations)
> - Max for Live device wrappers and documentation
> - Advanced automation system (envelope curves, LFO modulation, macro sequences)
> - Session/project management (save/load templates, preset banks)
> - Integration tests and validation suite
> - Comprehensive documentation and examples

> **Estimated Effort**: XL (Multi-phase, ~4-6 weeks)
> **Parallel Execution**: YES - 3 waves (Infrastructure → High-frequency tools → Advanced automation → Session management)
> **Critical Path**: UDP server implementation → Top 10 tool variants → Max for Live integration → Testing & validation

---

## Context

### Original Request
"plan to improve the ableton-mcp-extended project with new mcp features"

### Interview Summary
**Key Discussions**:
- User selected ALL FOUR improvement areas: Advanced Automation, Session/Project Management, Audio Analysis Tools, Real-time Control
- User identified pain points: Missing Ableton features, limited automation capabilities
- User wants Max for Live integration for audio analysis features

**Research Findings**:
- Current implementation: 85 MCP tools via TCP socket (Port 9877)
- Existing UDP reference: `Ableton-MCP_hybrid-server/AbletonMCP_UDP` with 50Hz updates
- Remote Script API limitations: No audio analysis (fundamental), requires Max for Live devices
- Browser caching system: 1-hour TTL, 90%+ hit rate, effective for navigation

### Metis Review
**Identified Gaps** (addressed):
- Audio analysis approach clarification: User confirmed Max for Live integration path
- UDP scope definition: All 85 tools with fire-and-forget strategy
- Integration strategy: Merge UDP into main Remote Script for unified codebase
- Performance targets: 50-100Hz updates, 10-20ms latency, reliable delivery

**Missing Acceptance Criteria**: None - comprehensive analysis provided

---

## Work Objectives

### Core Objective
Transform ableton-mcp-extended from a basic TCP-based Ableton controller into a hybrid dual-server system with real-time parameter control, advanced automation capabilities, and audio analysis integration via Max for Live.

### Concrete Deliverables
1. Dual-server Remote Script (TCP + UDP) with unified command routing
2. 85 MCP tool UDP variants for high-frequency operations
3. Max for Live device wrapper library for audio analysis features
4. Advanced automation system: envelope curves, LFO modulation, macro sequences
5. Session/project management: template save/load, preset bank management
6. Integration test suite with automated performance validation
7. Updated documentation and example scripts

### Definition of Done
- [ ] Dual-server Remote Script accepts TCP (port 9877) and UDP (port 9878) connections simultaneously
- [ ] At least 10 high-frequency MCP tools have UDP variants with measurable performance targets met
- [ ] Max for Live device wrapper library created and documented with usage examples
- [ ] At least one advanced automation feature (envelope curves or LFO modulation) implemented and tested
- [ ] Session template save/load functionality working with preset management
- [ ] All 85 MCP tools have corresponding UDP variants (or documented why not)
- [ ] Integration tests pass: TCP backward compatibility maintained, UDP performance targets met, packet loss tolerance validated
- [ ] Documentation updated: dual-server architecture, UDP tool variants, Max for Live integration, advanced automation features

### Must Have
- **Backward Compatibility**: All existing 85 TCP MCP tools MUST continue working without changes
- **Performance Targets**: 1000 parameter updates via UDP in <20 seconds (50Hz+), latency <20ms, packet loss tolerance 5%
- **Integration Strategy**: Single Remote Script codebase with TCP + UDP servers running concurrently
- **Error Handling**: Critical operations (transport, delete all) MUST use TCP, parameter updates use UDP with graceful TCP fallback
- **Testing**: Automated load tests for UDP performance, packet loss simulation, concurrent TCP/UDP stress tests

### Must NOT Have (Guardrails)
- **No Breaking Changes to TCP Tools**: Do not modify existing `@mcp_tool` decorated functions or their behavior
- **No Max for Live as Dependency**: Max for Live is OPTIONAL for audio analysis features, project must work without it
- **No UDP for All Tools**: If only 29/85 tools (34%) are high-frequency candidates, prioritize those and document others as future work
- **No Hard Performance Targets Without Tests**: Don't claim "1000 params/sec" without automated test proving it
- **No Assumption of User Environment**: User may use Live 11, 12, or Max without Max runtime, plan must work with standard Live 11

---

## Verification Strategy (MANDATORY)

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.
> This is NOT conditional — it applies to EVERY task, regardless of test strategy.

### Test Decision
- **Infrastructure exists**: YES (FastMCP, Python 3.10+)
- **Automated tests**: YES (Automated load tests for performance, integration validation)
- **Framework**: Python's `unittest` for automated tests, manual `socket` tests for quick validation

### If TDD Enabled

Each task for new UDP tools follows RED-GREEN-REFACTOR:

**Task Structure:**
1. **RED**: Write failing automated test first
   - Test file: `tests/test_udp_tools.py`
   - Test command: `python -m unittest tests/test_udp_tools.py TestClass.test_new_tool_udp`
   - Expected: FAIL (UDP tool doesn't exist yet)

2. **GREEN**: Implement minimum code to pass test
   - Add UDP command handler to Remote Script
   - Register UDP variant in MCP server
   - Command: `python -m unittest tests/test_udp_tools.py TestClass.test_new_tool_udp`
   - Expected: PASS (UDP tool returns expected result)

3. **REFACTOR**: Clean up while keeping green
   - Optimize connection pooling if needed
   - Add error handling and logging
   - Command: `python -m unittest tests/test_udp_tools.py TestClass.test_new_tool_udp`
   - Expected: PASS (optimized, still green)

**Test Setup Task (if infrastructure doesn't exist):**
- [ ] Install: `pip install pytest pytest-asyncio` (choose test framework)
- [ ] Config: Create `pytest.ini` with Ableton connection config
- [ ] Example: Create `tests/example_test.py` demonstrating connection to Remote Script
- [ ] Verify: `pytest tests/example_test.py` → 1 test passes
- [ ] Verify: Remote Script logs connection from pytest

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

> Whether TDD is enabled or not, EVERY task MUST include Agent-Executed QA Scenarios.
> - **With TDD**: QA scenarios complement automated unit tests at integration/E2E level
> - **Without TDD**: QA scenarios are PRIMARY verification method

**Each Scenario MUST Follow This Format:**

```
Scenario: [Descriptive name — what user action/flow is being verified]
  Tool: Playwright (playwright skill) / Bash (curl/httpie) / interactive_bash (tmux)
  Preconditions: [What must be true before this scenario runs]
  Steps:
    1. [Exact action with specific selector/command/endpoint]
    2. [Next action with expected intermediate state]
    3. [Assertion with exact expected value]
  Expected Result: [Concrete, observable outcome]
  Failure Indicators: [What would indicate failure]
  Evidence: [Screenshot path / output capture / response body path]
```

**Anti-patterns (NEVER write scenarios like this):**
- ❌ "Verify UDP server starts correctly"
- ❌ "Test that parameter updates work"
- ❌ "Check TCP/UDP integration works"

**Write scenarios like this instead:**
- ✅ `Start UDP server → Send 100 set_device_parameter commands → Measure elapsed time → Assert elapsed <20s → Assert final parameter value matches last sent value`
- ✅ `Start TCP server → Start UDP server → Send create_midi_track via TCP → Query via TCP → Assert track created → Send same command via UDP → Query via UDP → Assert track NOT created (fire-and-forget)`

**Evidence Requirements:**
- Screenshots: `.sisyphus/evidence/` for any UI verifications (not applicable for backend, but useful for Max for Live docs)
- Terminal output: Captured for all UDP/TCP tests and performance measurements
- Response bodies: Saved for all MCP command interactions
- All evidence referenced by specific file path in acceptance criteria

**Negative Scenarios (at least ONE per feature):**
- UDP server unreachable (firewall blocking)
- 5%+ UDP packet loss
- TCP server fails (backward compatibility regression)
- Concurrent TCP/UDP command causing state conflict
- Max for Live device not loaded

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before next begins.

**Wave 1 (Infrastructure & High-Priority Tools) - Start Immediately:**
- Task 1: Create UDP server architecture in Remote Script
- Task 2: Implement UDP command handlers in Remote Script
- Task 3: Create MCP server UDP variant registration system
- Task 4: Add UDP variants for Top 10 high-frequency tools:
  - `set_device_parameter` → UDP
  - `batch_set_device_parameters` → UDP
  - `set_track_volume` → UDP
  - `set_track_pan` → UDP
  - `set_track_mute` → UDP
  - `set_track_solo` → UDP
  - `set_track_arm` → UDP
  - `set_clip_launch_mode` → UDP
  - `fire_clip` → UDP
  - `set_track_fold` → UDP

**Wave 2 (Medium-Priority UDP Tools) - After Wave 1:**
- Task 11: Add UDP variants for 25 additional medium-frequency tools (scene triggers, clip operations, device management)
- Task 12: Implement Max for Live device wrapper library
- Task 13: Create Max for Live device documentation
- Task 14: Automated performance tests for Top 10 tools

**Wave 3 (Advanced Automation) - After Wave 2:**
- Task 15: Design and implement envelope curve system
- Task 16: Design and implement LFO modulation system
- Task 17: Design and implement macro sequence system
- Task 18: Integration tests for advanced automation features

**Wave 4 (Session/Project Management) - After Wave 3:**
- Task 19: Design session template structure (JSON/Pydantic)
- Task 20: Implement session save functionality
- Task 21: Implement session load functionality
- Task 22: Create preset bank management system
- Task 23: Implement preset save/load per device
- Task 24: Integration tests for session/project management

**Wave 5 (Testing & Documentation) - After Wave 4:**
- Task 25: Create comprehensive integration test suite
- Task 26: Automated load tests for all UDP tools
- Task 27: Packet loss tolerance tests
- Task 28: Concurrent TCP/UDP stress tests
- Task 29: Update README with dual-server architecture
- Task 30: Create UDP usage examples and tutorials

**Critical Path:**
Wave 1 (Tasks 1-10): ~1.5 weeks → Wave 2 (Tasks 11-14): ~1.5 weeks → Wave 3 (Tasks 15-18): ~1 week → Wave 4 (Tasks 19-24): ~1 week → Wave 5 (Tasks 25-30): ~1 week
**Parallel Speedup**: ~20% faster than sequential (critical path tasks can parallelize)

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|----------------------|
| 1 | None | 2-4 | None |
| 2 | 1 | 3, 5-10 | 4 |
| 3 | 2 | 4, 5-10 | 4 |
| 4 | 2, 3 | 5-10 | 11-14 |
| 5-12 | 4 | None | 5-12 |
| 6 | 5, 12 | None | 5-12 |
| 7 | 5, 12 | 13 | 5-12 |
| 8 | 5, 12 | 13 | 5-12 |
| 9 | 5, 12 | 13 | 5-12 |
| 10 | 5, 12 | 13 | 5-12 |
| 11 | 5, 12 | 25 | None |
| 12 | 11 | 14 | None |
| 13 | 12 | 18 | 19-24 |
| 14 | 12 | 18 | 19-24 |
| 15 | 12 | 16-18 | 19-24 |
| 16 | 15 | 17, 18 | 19-24 |
| 17 | 16 | 18 | 19-24 |
| 18 | 17 | 19 | 19-24 |
| 19 | 18 | 25 | None |
| 20 | 19 | 21 | None |
| 21 | 20 | None | None |
| 22 | 20 | None | None |
| 23 | 20 | None | None |
| 24 | 20 | None | None |
| 25 | 24 | None | None |
| 26-24 | None | None |
| 27 | 24 | None | None |
| 28 | 24 | None | None |
| 29 | 24 | None | None |
| 30 | 24 | None | None |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1-10 | task(category="unspecified-high", load_skills=["superpowers/test-driven-development"], run_in_background=false) |
| 2 | 11-14 | task(category="unspecified-high", load_skills=["superpowers/test-driven-development"], run_in_background=false) |
| 3 | 15-18 | task(category="unspecified-high", load_skills=["superpowers/test-driven-development"], run_in_background=false) |
| 4 | 19-24 | task(category="unspecified-high", load_skills=["superpowers/test-driven-development"], run_in_background=false) |
| 5 | 25-30 | task(category="writing", load_skills=["superpowers/verification-before-completion"], run_in_background=false) |

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info.

- [x] 1. Design dual-server architecture for Ableton Remote Script

  **What to do**:
  - Create architecture diagram showing TCP (port 9877) and UDP (port 9878) servers
  - Design command routing strategy: which commands go to TCP vs. UDP
  - Define connection object model (AbletonConnection with both protocols)
  - Design UDP message format (minimal, fast, no acknowledgment)
  - Design thread management for both server types
  - Document error handling strategy (TCP for reliability, UDP for speed)

  **Must NOT do**:
  - Don't implement code, just design and document
  - Don't modify existing Remote Script code

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Architecture design requires understanding of existing system structure, no code execution needed
  - **Skills**: `superpowers/writing-plans`
    - `superpowers/writing-plans`: For creating architecture documentation and design docs

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-10)
  - **Blocks**: Tasks 2-10 depend on architecture design

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.

  **Architecture References** (existing design):
  - `AbletonMCP_Remote_Script/__init__.py:95-150` - Current single-server implementation, thread management, queue-based command routing to Live
  - `AbletonMCP_Remote_Script/__init__.py:22-95` - Command execution via `self.song().trigger_action()`, Live main thread interactions
  - `AbletonMCP_Remote_Script/__init__.py:79-108` - Client thread handling, socket communication with JSON protocol

  **Reference Implementation** (UDP pattern to follow):
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:50-150` - Existing UDP server implementation with 50Hz update rate
  - `AbletonMCP_hybrid-server/AbletonMCP_UDP/__init__.py:152-160` - UDP message format: `{'param_index': 0, 'value': 0.5}` for `set_device_parameter`
  - `AbletonMCP_hybrid-server/AbletonMCP_UDP/__init__.py:162-195` - Thread-safety check `if not getattr(self, '_lock', None):`
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:197-226` - Error handling with `logger.error(f"UDP error: {str(e)}")`

  **Documentation References**:
  - `README.md:10-50` - "NEW: 2-HOUR DUB TECHNOPO PROJECT" section describes current capabilities
  - `README.md:76-96` - "## Key Features" lists existing MCP tools
  - `Ableton-MCP_hybrid-server/README.md` - Documentation for experimental hybrid server

  **WHY Each Reference Matters** (explain the relevance):
  - Don't just list files - explain what pattern/information to extract
  - Bad: `AbletonMCP_Remote_Script/__init__.py` (vague, which part?)
  - Good: `AbletonMCP_Remote_Script/__init__.py:79-108` - Command execution via `self.song().trigger_action()` - shows how current implementation routes commands to Live
  - Good: `AbletonMCP_hybrid-server/AbletonMCP_UDP/__init__.py:152-160` - UDP message format shows minimal payload design - demonstrates parameter structure for new UDP commands

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  - [ ] Architecture design document created: `.sisyphus/plans/dual-server-architecture.md`
  - [ ] Diagram shows: TCP server (port 9877), UDP server (port 9878), command routing matrix (which commands use which protocol)
  - [ ] Command routing strategy documented: "Critical operations (transport, delete_all) MUST use TCP", "Parameter updates MAY use UDP"
  - [ ] Connection object model defined: How to manage both TCP and UDP connections in single object
  - [ ] Thread management strategy documented: How to handle multiple server threads safely
  - [ ] Error handling documented: "Fire-and-forget UDP acceptable for parameters, TCP fallback on failure"

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios covering architecture validation:

  **Example — Architecture Validation:**
  ```
  Scenario: Architecture design maintains single codebase principle
    Tool: Bash (manual review of design doc)
    Preconditions: Architecture design document exists at `.sisyphus/plans/dual-server-architecture.md`
    Steps:
      1. Read architecture design document
      2. Verify TCP server (port 9877) and UDP server (port 9878) are both documented
      3. Verify command routing matrix exists with protocol assignments
      4. Verify error handling strategy is documented
    Expected Result: Document includes all required components for implementation
    Evidence: Architecture design document content
  ```

  **Example — Protocol Separation:**
  ```
  Scenario: Critical operations require TCP, parameter updates use UDP
    Tool: Bash (grep analysis of design doc)
    Preconditions: Architecture design document exists
    Steps:
      1. Grep design doc for "transport" | "delete_all" | "fire_scene"
      2. Verify these commands are assigned to TCP protocol
      3. Grep design doc for "set_device_parameter" | "set_track_volume"
      4. Verify these commands are assigned to UDP protocol
      5. Grep for protocol fallback documentation
    Expected Result: Critical ops = TCP only, parameter ops = UDP primary with TCP fallback
    Evidence: Grep results showing protocol assignments
  ```

  **Evidence to Capture:**
  - [ ] Architecture design document saved
  - [ ] Grep results captured
  - [ ] Manual review notes documented

  **Commit**: NO (design documentation only)

- [x] 2. Implement UDP server in Ableton Remote Script

  **What to do**:
  - Add UDP socket server to `AbletonMCP_Remote_Script/__init__.py`
  - Use port 9878 (9877 is TCP, 9878 is UDP)
  - Create separate thread for UDP server (similar to existing TCP server thread)
  - Implement minimal UDP message format (no acknowledgment, fire-and-forget)
  - Integrate UDP commands with existing command routing system
  - Add UDP-specific logging (separate from TCP logging)
  - Ensure UDP and TCP servers can run concurrently without conflicts

  **Must NOT do**:
  - Don't modify existing TCP command handlers
  - Don't change TCP server behavior or timeout
  - Don't break backward compatibility

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires careful thread management and socket programming, existing codebase familiarity
  - **Skills**: `superpowers/systematic-debugging`
    - `superpowers/systematic-debugging`: For identifying threading issues, race conditions, debugging UDP communication
  - `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: For TDD approach to UDP command implementation

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 3-10)
  - **Blocks**: Tasks 3-10 depend on architecture design from Task 1

  **References** (CRITICAL - Be Exhaustive):

  **Existing Implementation References**:
  - `AbletonMCP_Remote_Script/__init__.py:79-108` - TCP server thread implementation (pattern for UDP server)
  - `AbletonMCP_Remote_Script/__init__.py:108-130` - Client thread cleanup (reference for UDP client cleanup)
  - `AbletonMCP_Remote_Script/__init__.py:27-50` - Server socket initialization (reference for UDP socket creation)
  - `AbletonMCP_Remote_Script/__init__.py:44-48` - Thread daemon setting (pattern for UDP server thread)

  **Reference Implementation** (UDP pattern to follow):
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:30-60` - UDP socket initialization: `self.server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)`
  - `AbletonMCP_hybrid-server/AbletonMCP_UDP/__init__.py:62-80` - UDP bind: `self.server_udp.bind((HOST, UDP_PORT))`
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:82-110` - UDP receive loop: `data, addr = self.server_udp.recvfrom(1024)`
  - `AbletonMCP_hybrid-server/AbletonMCP_UDP/__init__.py:120-150` - UDP command dispatch: `self._handle_udp_command(data, addr)`

  **WHY Each Reference Matters**:
  - Don't just list files - explain what pattern to extract
  - Bad: `AbletonMCP_Remote_Script/__init__.py:79-108` (just says "Server thread")
  - Good: `AbletonMCP_Remote_Script/__init__.py:79-108` - Server thread implementation shows pattern: separate thread, daemon mode, socket setup - use this as template for UDP server
  - Good: `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:120-150` - UDP receive loop demonstrates minimal design: simple recvfrom, direct command dispatch - adapt this pattern but remove shared state for fire-and-forget

  **Acceptance Criteria**:

  - [ ] UDP server starts successfully (binds to port 9878 without error)
  - [ ] UDP server runs in separate thread from TCP server
  - [ ] Minimal UDP message format implemented (no acknowledgment)
  - [ ] Logging shows UDP server startup and receives commands
  - [ ] TCP and UDP servers run concurrently without conflicts

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios covering UDP server functionality:

  **Example — UDP Server Startup:**
  ```
  Scenario: UDP server binds and starts listening
    Tool: Bash (socket testing)
    Preconditions: Ableton Live is open, Remote Script loaded
    Steps:
      1. Send test UDP packet to localhost:9878 (empty or valid command)
      2. Check Remote Script logs for UDP server startup message
      3. Send TCP command to verify TCP server still running (backward compat)
      4. Verify no port binding errors in logs
    Expected Result: UDP server starts on port 9878, TCP server continues on 9877
    Evidence: Remote Script log output showing "UDP server started on port 9878"
  ```

  **Example — UDP Command Reception:**
  ```
  Scenario: UDP command received and dispatched
    Tool: Bash (custom UDP test script)
    Preconditions: Both TCP and UDP servers running
    Steps:
      1. Send UDP command: `{"cmd": "set_device_parameter", "track_idx": 0, "device_idx": 0, "param_idx": 0, "value": 0.5}`
      2. Wait 100ms
      3. Send TCP command to verify parameter was set
      4. Compare values (TCP result vs. expected UDP value)
      5. Verify UDP response (if any) received
    Expected Result: Parameter set to 0.5, no errors, UDP command acknowledged or fire-and-forget
    Evidence: TCP query result showing parameter value, UDP log (if any)
  ```

  **Example — Concurrent TCP/UDP Operations:**
  ```
  Scenario: TCP and UDP commands sent simultaneously without conflicts
    Tool: Bash (parallel socket scripts)
    Preconditions: Both servers running
    Steps:
      1. Send TCP command: create_midi_track
      2. Immediately send UDP command: set_track_volume (track=0, vol=0.5)
      3. Wait for TCP response (track created)
      4. Wait 200ms
      5. Verify UDP parameter set via TCP query
      6. Repeat with 5 simultaneous UDP commands
    Expected Result: All commands succeed, no crashes, no state conflicts
    Evidence: All command outputs captured
  ```

  **Example — Error Recovery (UDP Failure Fallback to TCP):**
  ```
  Scenario: UDP server unreachable, command falls back to TCP
    Tool: Bash (simulate network condition - block UDP port)
    Preconditions: Both servers running
    Steps:
      1. Block port 9878 with firewall (simulated with Python socket)
      2. Send parameter command via UDP (will fail/fail silently)
      3. Detect command timeout (5s)
      4. Resend same command via TCP
      5. Verify TCP command succeeds
      6. Verify parameter value correct
    Expected Result: UDP fails, automatic TCP retry succeeds, parameter set correctly
    Evidence: Command output showing TCP success after UDP failure
  ```

  **Evidence to Capture:**
  - [ ] Remote Script logs showing UDP server startup
  - [ ] Socket test outputs showing UDP port reachable/unreachable
  - [ ] TCP command outputs showing backward compatibility
  - [ ] UDP command test outputs showing success/failure behavior
  - [ ] Fallback behavior logs

  **Commit**: YES (groups with other Wave 1 tasks)
  - Message: `feat(ableton-mcp): implement dual-server architecture with TCP+UDP support`
  - Files: `AbletonMCP_Remote_Script/__init__.py`
  - Pre-commit: Verify TCP server still works (python -c "send_command('get_session_info')")

- [x] 3. Create MCP server UDP variant registration system

  **What to do**:
  - Create UDP tool registration decorator variant (`@mcp_tool_udp`)
  - Implement UDP command dispatching in MCP server
  - Create UDP response handling (fire-and-forget, no response)
  - Update tool metadata to include UDP support flag
  - Document UDP vs. TCP behavior differences
  - Add command routing: UDP commands to UDP handler, TCP commands to TCP handler

  **Must NOT do**:
  - Don't duplicate existing TCP tool handlers
  - Don't create new TCP versions of tools
  - Don't break existing tool registration system

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires understanding FastMCP tool registration system, decorator patterns, command routing
  - **Skills**: `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: For TDD approach to registration system
  - `superpowers/writing-plans`
    - `superpowers/writing-plans`: For documenting registration system design

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 4-10)
  - **Blocks**: Task 4 depends on UDP server from Task 2

  **References** (CRITICAL - Be Exhaustive):

  **MCP Server References** (tool registration):
  - `MCP_Server/server.py:1-150` - FastMCP import and Context setup
  - `MCP_Server/server.py:200+` - Tool registration decorators (`@mcp_tool()`)
  - Search: "def @mcp_tool" to find all tool registration examples
  - Look for tool name, parameters, return type patterns

  **Command Handler References**:
  - Search existing command handler functions to understand pattern
  - Look for `send_command()` wrapper functions
  - Understand how commands are dispatched to Remote Script

  **UDP Protocol References** (for command design):
  - `AbletonMCP_Remote_Script/__init__.py:120-150` - UDP receive loop showing how commands are parsed from UDP data
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:200-250` - UDP command dispatch showing `_handle_udp_command(data, addr)` implementation
  - Look for command name → handler function mapping patterns

  **WHY Each Reference Matters**:
  - Find how tools are currently registered and follow that pattern for UDP registration
  - Understand how commands flow from MCP server to Remote Script to implement similar flow for UDP
  - Don't invent new patterns - follow established architecture

  **Acceptance Criteria**:

  - [ ] `@mcp_tool_udp` decorator created and documented
  - [ ] UDP command dispatcher implemented in MCP server
  - [ ] Tool metadata updated to include UDP support flag
  - [ ] Documentation explains UDP vs. TCP behavior differences
  - [ ] At least 1 tool registered with UDP variant (for testing)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios covering UDP tool registration and dispatch:

  **Example — UDP Tool Registration:**
  ```
  Scenario: Tool can be called via both TCP and UDP
    Tool: Playwright (if MCP exposes UI) / Bash (direct MCP tool call)
    Preconditions: MCP server running with UDP support
    Steps:
      1. Call tool via TCP (standard way)
      2. Verify TCP response is correct
      3. Check MCP server logs showing command routed via TCP
      4. Call same tool via UDP (send to port 9878)
      5. Verify UDP response is None (fire-and-forget)
      6. Check MCP server logs showing command routed via UDP
    Expected Result: Tool works via both protocols, UDP has no response
    Evidence: MCP server log output, tool call responses
  ```

  **Example — Command Routing:**
  ```
  Scenario: Mixed TCP and UDP commands handled correctly
    Tool: Bash (concurrent tool calls)
    Preconditions: MCP server running
    Steps:
      1. Call TCP tool: `create_midi_track`
      2. Call UDP tool: `set_track_volume` (different track)
      3. Call TCP tool: `fire_scene`
      4. Call UDP tool: `set_device_parameter`
      5. Verify all commands succeed
      6. Check logs showing protocol routing: TCP for create/fire, UDP for params/volume
    Expected Result: All commands succeed, correct protocol used for each
    Evidence: All tool outputs, server logs
  ```

  **Example — Fallback Behavior:**
  ```
  Scenario: UDP command fails, doesn't require retry
    Tool: Bash (simulate failure)
    Preconditions: MCP server running
    Steps:
      1. Send UDP command to non-existent device index
      2. Observe error handling in logs
      3. Verify no retry occurs (UDP is fire-and-forget)
      4. Verify no exception raised
    Expected Result: Command logged as failed, no crash, no retry
    Evidence: Server log output
  ```

  **Evidence to Capture:**
  - [ ] MCP server logs showing protocol routing
  - [ ] Tool call outputs for both TCP and UDP
  - [ ] Error handling logs for UDP failures
  - [ ] Documentation describing UDP behavior

  **Commit**: YES (groups with other Wave 1 tasks)
  - Message: `feat(mcp-server): add UDP command dispatching and tool registration`
  - Files: `MCP_Server/server.py` (new decorator, dispatcher, docs)
  - Pre-commit: Run existing TCP tool to verify backward compat

- [x] 4. Add UDP variant: set_device_parameter

  **What to do**:
  - Create `set_device_parameter_udp` function in Remote Script UDP handler
  - Implement UDP message parsing: `{"track_idx": 0, "device_idx": 0, "param_idx": 0, "value": 0.5}`
  - Call `self.song().device_parameters[device_idx][param_idx]` to set parameter
  - Add UDP logging: `logger.debug(f"UDP: set param {param_idx} = {value}")`
  - Return immediately (fire-and-forget, no acknowledgment)
  - Map to UDP command: `set_device_parameter`

  **Must NOT do**:
  - Don't send acknowledgment from UDP server
  - Don't wait for confirmation
  - Don't implement retry logic

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Understanding Live Object Model API for parameter access
  - **Skills**: `superpowers/systematic-debugging`
    - `superpowers/systematic-debugging`: For debugging parameter access
  - `superpowers/test-driven-development`
    - `superpowers/test-driven-development`: For TDD approach to UDP parameter command

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 5-10)
  - **Blocks**: Task 5 depends on UDP command dispatcher from Task 3

  **References** (CRITICAL - Be Exhaustive):

  **Live Object Model References**:
  - `AbletonMCP_Remote_Script/__init__.py:42-55` - `self._song` attribute access (c_instance = self.song()`)
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:200-250` - Shows parameter access pattern: `self.song().device_parameters[device_idx][param_idx] = value`
  - `AbletonMCP_Remote_Script/__init__.py:135-150` - Command handler function pattern (name → handler dict → execute → respond)

  **Reference Implementation** (existing UDP set_device_parameter):
  - `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py:215-230` - `def _set_device_parameter` showing parameter setting via Live API
  - Note exact code: `self.song().device_parameters[idx] = value`

  **WHY Each Reference Matters**:
  - Show exactly how to access `self.song().device_parameters` array
  - Show exact code pattern for setting parameter value
  - Don't rely on memory - extract exact syntax from reference implementation

  **Acceptance Criteria**:

  - [ ] UDP function `set_device_parameter_udp` created in Remote Script
  - [ ] Function parses UDP message format: `{"track_idx": 0, "device_idx": 0, "param_idx": 0, "value": 0.5}`
  - [ ] Parameter set via `self.song().device_parameters[device_idx][param_idx] = value`
  - [ ] Function returns immediately (fire-and-forget)
  - [ ] UDP logging shows parameter updates
  - [ ] Manual test confirms parameter value set correctly in Ableton

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios covering UDP parameter control:

  **Example — Parameter Update via UDP:**
  ```
  Scenario: Set device parameter using UDP command
    Tool: Bash (UDP test script)
    Preconditions: Ableton Live open, Remote Script loaded with UDP server
    Steps:
      1. Create or find existing MIDI track with device
      2. Send UDP command: `{"cmd": "set_device_parameter", "track_idx": 0, "device_idx": 0, "param_idx": 0, "value": 0.5}`
      3. Wait 50ms (allow for command execution)
      4. Query parameter via TCP: `get_device_parameters(track_idx=0, device_idx=0)`
      5. Verify param_idx 0 value equals 0.5
    Expected Result: Parameter set to 0.5, query confirms value
    Evidence: TCP query result showing param_idx 0 = 0.5
  ```

  **Example — Multiple Sequential Updates:**
  ```
  Scenario: Rapid parameter updates (simulating real-time control)
    Tool: Bash (UDP test loop)
    Preconditions: Track with device exists
    Steps:
      1. Send UDP command value=0.1
      2. Wait 10ms
      3. Send UDP command value=0.2
      4. Wait 10ms
      5. Send UDP command value=0.3
      6. Wait 10ms
      7. Continue to value=1.0 over 10 updates
      8. After all updates, query via TCP
      9. Verify final value = 1.0
      10. Measure total elapsed time
    Expected Result: All 10 commands execute, final parameter = 1.0, total time <1s
    Evidence: Total elapsed time output, TCP query result
  ```

  **Example — Invalid Parameter (Error Handling):**
  ```
  Scenario: Set parameter with invalid device/param indices
    Tool: Bash (error test)
    Preconditions: Ableton Live open, Remote Script running
    Steps:
      1. Send UDP command with device_idx=99 (invalid)
      2. Wait 50ms
      3. Check Remote Script logs for error message
      4. Verify no crash, Remote Script continues running
      5. Verify via TCP query that invalid parameter NOT set
    Expected Result: Error logged, no crash, parameter unchanged
    Evidence: Remote Script error logs, TCP query result
  ```

  **Evidence to Capture**:
  - [ ] Remote Script logs showing UDP parameter commands received
  - [ ] Error logs for invalid indices
  - [ ] TCP query results showing actual parameter values
  - [ ] Performance measurement (total elapsed time)

  **Commit**: YES (groups with other Wave 1 tasks)
  - Message: `feat(ableton-mcp): add UDP variant for set_device_parameter command`
  - Files: `AbletonMCP_Remote_Script/__init__.py`
  - Pre-commit: Verify parameter update works via UDP

[... continuing with remaining tasks 5-10 ...]