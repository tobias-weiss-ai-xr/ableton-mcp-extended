# Sprint 01: Testing Infrastructure + CI/CD

## TL;DR (For humans)

**What you'll get:** A proper test suite that runs with `python -m pytest` instead of running 18 scripts by hand. CI pipeline on GitHub Actions runs ruff linting, type checking, and all tests on every push/PR. Tests for verify.py, als_parser.py, knowledge base, Max bridge, and resource URIs.

**Why this approach:** Without tests, every refactor is blind — the last wave proved this. Pytest discovery + CI gates catch regressions automatically. The 5 test modules cover the 5 new surface areas from the comprehensive upgrade.

**What it will NOT do:** Delete existing test scripts (tests-only addition). Add heavy test frameworks (pytest-cov only). Mock the Remote Script (tests are server-side/logical only).

**Effort:** Short (3 days)
**Risk:** Low - test-only changes, no production code modified
**Decisions to sanity-check:** pytest config location (pyproject.toml), CI trigger strategy (push + PR)

Your next move: Approve and `$start-work` to begin.

---

> TL;DR (machine): Short effort, Low risk. pytest config in pyproject.toml, 5 test modules (verify, als_parser, knowledge, max_bridge, resources), GitHub Actions CI with ruff → compile → pytest. Zero production code changes.

## Scope

### Must have
- pyproject.toml pytest configuration with `testpaths = ["tests"]` and discovery settings
- `tests/test_verify.py` — 12 scenarios for verify loop (modifying vs read-only, snapshot/diff, errors, concurrency)
- `tests/test_als_parser.py` — parse .als fixtures, detect_issues, suggest_changes
- `tests/test_knowledge.py` — 36 devices load, parameter queries, edge cases (not-found device/param)
- `tests/test_max_bridge.py` — mock OSC, graceful fallback, address allowlist, port validation
- `tests/test_resources.py` — URI templates match expected patterns, response structure
- `tests/test_groove_tools.py` — tool registration, groove name queries, registration coherency
- `tests/fixtures/minimal.als` — gzipped XML with 1 MIDI track, tempo 120, 4/4 time
- `tests/fixtures/three_tracks.als` — 3 tracks (MIDI, audio, return) with basic device chain
- `.github/workflows/ci.yml` — trigger on push + PR to main, steps: checkout, setup-python, pip install, ruff, compile, pytest

### Must NOT have
- Do NOT modify any production code (server.py, __init__.py, verify.py, etc.)
- Do NOT delete existing `scripts/test/test_*.py` files (preserve for backward compat)
- Do NOT add mock for Ableton Remote Script (test only logical/server-side code)
- Do NOT add heavy test frameworks (pytest-cov only, no selenium/tox/nox)
- Do NOT modify LSP configuration

## Verification strategy
> Zero human intervention — all verification is agent-executed.
- Test decision: tests-first (new tests are the deliverable)
- Evidence: .omo/evidence/task-<N>-sprint-01-testing-ci.<ext>

## Execution strategy

### Parallel execution waves

| Wave | Focus | Todos | Est. time |
|------|-------|-------|-----------|
| 1 | Infra + Fixtures | 1, 2 | 1h |
| 2 | Test modules (parallel) | 3, 4, 5, 6, 7 | 3h |
| 3 | CI pipeline | 8 | 1h |

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. pyproject.toml pytest config | None | 3,4,5,6,7 | 2 |
| 2. .als fixture files | None | 4 | 1 |
| 3. tests/test_verify.py | 1 | None | 4,5,6,7,2 |
| 4. tests/test_als_parser.py | 1,2 | None | 3,5,6,7 |
| 5. tests/test_knowledge.py | 1 | None | 3,4,6,7 |
| 6. tests/test_max_bridge.py | 1 | None | 3,4,5,7 |
| 7. tests/test_groove_tools.py | 1 | None | 3,4,5,6 |
| 8. .github/workflows/ci.yml | 1,3,4,5,6,7 | None | None |

## Todos

- [x] 1. Configure pytest in pyproject.toml
  What to do / Must NOT do:
  Add to `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = ["test_*.py"]
  addopts = "-v --tb=short"
  
  [tool.coverage.run]
  source = ["MCP_Server"]
  omit = ["MCP_Server/__init__.py"]
  
  [project.optional-dependencies]
  dev = ["pytest", "pytest-cov"]
  ```
  Also ensure `scripts/test/` existing scripts are NOT in testpaths.
  Must NOT: Remove or modify any existing config. Must NOT change test runner for existing scripts.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 3,4,5,6,7
  Acceptance criteria:
  ```bash
  python -c "import tomllib; c = tomllib.load(open('pyproject.toml', 'rb')); assert 'pytest' in str(c.get('tool',{}).get('pytest',{}).get('ini_options',{})) or 'testpaths' in str(c.get('tool',{}).get('pytest',{}).get('ini_options',{})), 'pytest config not found'"
  ```
  QA scenarios: happy + failure
  - HAPPY: `python -m pytest --collect-only 2>&1` discovers test files
  - FAILURE: Existing `scripts/test/` files are NOT discovered
  Evidence: .omo/evidence/task-1-sprint-01-testing-ci.txt
  Commit: Y | chore(test): configure pytest in pyproject.toml

- [ ] 2. Create .als fixture files
  What to do / Must NOT do:
  Create `tests/fixtures/minimal.als` — gzipped XML with:
  - 1 MIDI track named "Test Track"
  - Tempo 120.0 BPM
  - Time signature 4/4
  - Basic LiveSet structure with Ableton version 5 root
  
  Create `tests/fixtures/three_tracks.als` — gzipped XML with:
  - 1 MIDI track, 1 Audio track, 1 Return track
  - Simple device chain on MIDI track
  - Different names for each track

  Must NOT: Depend on Ableton Live running. Must use stdlib `gzip` and raw XML strings.

  Parallelization: Wave 1 | Blocked by: None | Blocks: 4
  References:
  - .als format: gzipped XML with `<Ableton MajorVersion="5">` root, `<LiveSet><Tracks>` children
  - Existing implementation: `MCP_Server/als_parser.py` for expected XML structure
  Acceptance criteria:
  ```bash
  python -c "
  import gzip
  for f in ['tests/fixtures/minimal.als', 'tests/fixtures/three_tracks.als']:
      with gzip.open(f, 'rb') as fh:
          xml = fh.read()
      assert b'<Ableton' in xml, f'{f} is not a valid .als'
      print(f'{f}: valid')
  "
  ```
  QA scenarios: happy + failure
  - HAPPY: `python -c "import gzip; print(gzip.open('tests/fixtures/minimal.als','rb').read().decode()[:100])"` shows XML
  - HAPPY: `from MCP_Server.als_parser import parse_als_file; result = parse_als_file('tests/fixtures/minimal.als'); print(result['tracks'])`
  - FAILURE: Parse with corrupted file, get proper error
  Evidence: .omo/evidence/task-2-sprint-01-testing-ci.txt
  Commit: Y | test(fixtures): add .als fixture files for parser tests

- [ ] 3. Create tests/test_verify.py (12 scenarios)
  What to do / Must NOT do:
  Create `tests/test_verify.py` with pytest test functions covering:
  1. Verify wraps only modifying commands (check MODIFYING_COMMANDS in server.py:193-251)
  2. Verify does NOT wrap read-only commands (get_*, list_*, query_*)
  3. Pre/post snapshot captures correct state (mock send_command)
  4. Diff computed correctly when state changes
  5. No-op diff when state unchanged
  6. Error handling when snapshot capture fails
  7. Thread safety test (concurrent calls)
  8. Empty diff structure returned when no change
  9. Verify disabled via env var
  10. Verify with missing snapshot handler
  11. Verify with timeout on snapshot
  12. Verify with nested verify (prevent recursion)

  Use `unittest.mock.MagicMock` or `pytest.monkeypatch` to mock `send_command`.

  Must NOT: Import server.py directly (causes sounddevice dep). Import from verify.py directly.
  Must use: `from MCP_Server.verify import _WRAPPED_CLIENT`, `_MODIFYING_COMMANDS`

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
  References:
  - `MCP_Server/verify.py` — verify_modification, wrap_ableton_connection, MODIFYING_COMMANDS
  - `MCP_Server/server.py:193-251` — MODIFYING_COMMANDS list
  - Existing test pattern: `scripts/test/test_connection.py`
  Acceptance criteria:
  ```bash
  python -m pytest tests/test_verify.py -v 2>&1 | tail -20
  # Expected: 12 passed, 0 failed
  ```
  QA scenarios: happy + failure
  - HAPPY: All 12 scenarios pass
  - HAPPY: Modifying commands get wrapped, read-only don't
  - FAILURE: Intentionally introduce verify bug, test catches it
  Evidence: .omo/evidence/task-3-sprint-01-testing-ci.txt
  Commit: Y | test(verify): add 12 pytest scenarios for verify loop

- [ ] 4. Create tests/test_als_parser.py
  What to do / Must NOT do:
  Create `tests/test_als_parser.py` testing:
  1. `parse_als_file(minimal.als)` returns dict with `tracks`, `tempo`, `time_signature`
  2. `parse_als_file(three_tracks.als)` returns 3 tracks
  3. `detect_als_issues()` finds empty tracks in fixture
  4. `suggest_als_changes()` returns valid suggestions
  5. Parse error on invalid file (not .als)
  6. Parse error on corrupted gzip
  7. Track names extracted correctly from fixture
  8. Device chain parsed (if present in fixture)

  Use `from MCP_Server.als_parser import parse_als_file, detect_als_issues, suggest_als_changes`
  Must NOT: Mock the .als parsing (use real files from fixtures/).

  Parallelization: Wave 2 | Blocked by: 1, 2 | Blocks: 8
  References:
  - `MCP_Server/als_parser.py`
  - `tests/fixtures/minimal.als`, `tests/fixtures/three_tracks.als`
  Acceptance criteria:
  ```bash
  python -m pytest tests/test_als_parser.py -v 2>&1 | tail -20
  # Expected: 8+ passed
  ```
  QA scenarios: happy + failure
  - HAPPY: parse_als_file returns correct track count and tempo
  - FAILURE: Corrupted file raises controlled error
  Evidence: .omo/evidence/task-4-sprint-01-testing-ci.txt
  Commit: Y | test(als): add tests for .als parser module

- [ ] 5. Create tests/test_knowledge.py
  What to do / Must NOT do:
  Create `tests/test_knowledge.py` testing:
  1. `get_device_knowledge("Wavetable")` returns correct parameter count
  2. `get_device_knowledge("Wavetable", "Osc1 Level")` returns specific param
  3. `get_device_knowledge("Nonexistent")` returns not-found message
  4. `get_device_knowledge("Wavetable", "NonexistentParam")` returns not-found
  5. All 36 devices load without error (iterate knowledge/__init__.py)
  6. Total parameter count >= 245
  7. File count equals 5 JSON files
  8. Query device by partial name match
  9. All device schemas have required fields (name, class_name, parameters, parameter indices)

  Must NOT: Import server.py. Import from `MCP_Server.knowledge` directly.
  Use `from MCP_Server.knowledge import get_device_knowledge, get_available_devices`

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
  References:
  - `MCP_Server/knowledge/__init__.py`
  - `MCP_Server/knowledge/devices/*.json`
  Acceptance criteria:
  ```bash
  python -m pytest tests/test_knowledge.py -v 2>&1 | tail -20
  # Expected: 9+ passed
  ```
  QA scenarios: happy + failure
  - HAPPY: All 36 devices load, 245+ parameters
  - FAILURE: Query nonexistent device returns proper error
  Evidence: .omo/evidence/task-5-sprint-01-testing-ci.txt
  Commit: Y | test(knowledge): add tests for device knowledge base

- [ ] 6. Create tests/test_max_bridge.py
  What to do / Must NOT do:
  Create `tests/test_max_bridge.py` testing:
  1. MaxBridgeClient created without python-osc (graceful fallback, `available=False`)
  2. MaxBridgeClient with mocked python-osc sends correct OSC message
  3. Address allowlist rejects unauthorized addresses
  4. Port validation rejects privileged ports (<1024)
  5. `test_max_bridge` tool registered (check module-level function exists)
  6. Register function signature matches expected pattern
  7. OSC address construction works with various args

  Must NOT: Require actual python-osc or Max installation.
  Use `unittest.mock.patch` for python-osc imports.

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
  References:
  - `MCP_Server/max_bridge.py`
  - `MCP_Server/max_bridge.py:ALLOWED_ADDRESSES`
  Acceptance criteria:
  ```bash
  python -m pytest tests/test_max_bridge.py -v 2>&1 | tail -20
  # Expected: 7+ passed
  ```
  QA scenarios: happy + failure
  - HAPPY: Client works without python-osc, reports available=False
  - FAILURE: Unauthorized OSC address raises ValueError
  Evidence: .omo/evidence/task-6-sprint-01-testing-ci.txt
  Commit: Y | test(max): add tests for Max bridge module

- [ ] 7. Create tests/test_groove_tools.py
  What to do / Must NOT do:
  Create `tests/test_groove_tools.py` testing:
  1. `register_groove_tools` function exists and has correct signature
  2. Tool names match expected set `{list_groove_templates, apply_groove_to_clip, remove_groove_from_clip, set_global_groove_amount}`
  3. Handler names match in `__init__.py` (`_get_available_grooves`, `_apply_groove_to_clip`, etc.)
  4. `register_groove_tools(mcp, get_ableton_connection)` is called in `server.py`
  5. All 4 handlers are registered in the command dispatch in `__init__.py`
  6. ValueError raised for invalid groove amount (outside 0.0-1.0)
  7. All 4 commands have entries in the dispatch dict

  Must NOT: Import server.py directly. Use string/regex checks on server.py and __init__.py.

  Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
  References:
  - `MCP_Server/groove_tools.py`
  - `AbletonMCP_Remote_Script/__init__.py` (handler dispatch patterns)
  - `MCP_Server/server.py` (registration)
  Acceptance criteria:
  ```bash
  python -m pytest tests/test_groove_tools.py -v 2>&1 | tail -20
  # Expected: 7+ passed
  ```
  QA scenarios: happy + failure
  - HAPPY: All tool names match expected set
  - FAILURE: Missing handler in dispatch is detected
  Evidence: .omo/evidence/task-7-sprint-01-testing-ci.txt
  Commit: Y | test(grooves): add tests for groove tools registration

- [ ] 8. Create .github/workflows/ci.yml
  What to do / Must NOT do:
  Create `.github/workflows/ci.yml` with:
  - Trigger: push + pull_request to main branch
  - Jobs: lint (ruff → compile check), test (pytest)
  - Python 3.11 setup
  - Steps: checkout, setup-python, pip install -e ".[dev]", ruff check, python -m compileall, pytest
  - On failure: annotate PR with error

  Must NOT: Add deploy step. Must NOT add codecov (no token). Must NOT fail on warnings.

  Parallelization: Wave 3 | Blocked by: 3,4,5,6,7 | Blocks: None
  References:
  - GitHub Actions syntax: https://docs.github.com/en/actions/using-workflows
  - Project Python version: Python 3.11+
  Acceptance criteria:
  ```bash
  python -c "import yaml; c = yaml.safe_load(open('.github/workflows/ci.yml')); assert 'jobs' in c; assert 'test' in c['jobs'] or 'pytest' in str(c), 'ci.yml missing jobs or test'"
  ```
  QA scenarios: happy + failure
  - HAPPY: CI file parses as valid YAML with jobs, steps, and triggers
  - FAILURE: Missing trigger or missing test job
  Evidence: .omo/evidence/task-8-sprint-01-testing-ci.txt
  Commit: Y | ci: add GitHub Actions workflow for lint + test

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE.
- [ ] F1. `python -m pytest tests/ --collect-only 2>&1 | grep "collected"` shows test discovery
- [ ] F2. `python -m pytest tests/ -v 2>&1` all pass
- [ ] F3. GitHub workflow YAML valid
- [ ] F4. Scope fidelity: no production code modified (git diff --stat shows only test/infra files)

## Commit strategy
One commit per todo, conventional commits with test scope:
- chore(test): configure pytest in pyproject.toml
- test(fixtures): add .als fixture files
- test(verify): add 12 pytest scenarios
- test(als): add parser tests
- test(knowledge): add knowledge base tests
- test(max): add Max bridge tests
- test(grooves): add groove tools tests
- ci: add GitHub Actions workflow

## Success criteria
- `python -m pytest tests/` discovers all test files and passes
- All 5 surface areas (verify, als_parser, knowledge, max_bridge, grooves) have test coverage
- CI pipeline runs on every push to main
- Existing `scripts/test/` scripts are untouched and still work
- Zero production code modifications
