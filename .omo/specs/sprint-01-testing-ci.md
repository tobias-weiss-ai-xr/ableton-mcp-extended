# Sprint 01: Testing Infrastructure + CI/CD

**Theme:** Foundation — without tests, nothing is safe to refactor.
**Est. days:** 3 | **New tools:** 0 | **Risk:** Low
**Dependencies:** None

## Goal
Transform the project from 18 standalone test scripts into a proper pytest-based test suite with CI/CD pipeline. No more manual `python scripts/test/test_*.py` invocations.

## Key Files
| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Create/modify | Add `[tool.pytest.ini_options]`, `[tool.coverage]`, `[tool.ruff]` |
| `pytest.ini` | Remove or alias | Consolidate into pyproject.toml |
| `tests/` (dir) | Create | New top-level test directory |
| `tests/test_verify.py` | Create | 12+ scenarios for verify.py logic |
| `tests/test_als_parser.py` | Create | 5 fixture .als files + assertions |
| `tests/test_knowledge.py` | Create | 36 devices load, param queries, edge cases |
| `tests/test_max_bridge.py` | Create | Mock OSC client, graceful fallback, auth |
| `tests/test_resources.py` | Create | Resource URI template matching |
| `tests/fixtures/minimal.als` | Create | Gzipped XML minimal session |
| `tests/fixtures/three_tracks.als` | Create | 3-track session with devices |
| `.github/workflows/ci.yml` | Create | push/PR: ruff → compile → pytest |
| `.github/workflows/lint.yml` | Create | PR only: ruff + mypy |

## Deliverables

### 1.1 pytest Discovery Setup
- Configure `pyproject.toml` with pytest options: `testpaths = ["tests"]`, `python_files = ["test_*.py"]`
- Add `pytest-cov`, `pytest-mock` to dev dependencies (set `[project.optional-dependencies] dev = [...]`)
- Ensure `python -m pytest` discovers all tests

### 1.2 Unit Test Suite

**test_verify.py** (12 scenarios):
- Verify wraps only modifying commands (57 commands from server.py:193-251)
- Verify does NOT wrap read-only commands (get_*, list_*)
- Pre/post snapshot captures correct state
- Diff computed correctly when state changes
- No-op diff when state unchanged
- Error handling when snapshot capture fails
- Thread safety (concurrent calls)
- Empty diff structure
- Verify disabled via env var
- Large state response handling

**test_als_parser.py** (with fixture .als files):
- `parse_als_file(minimal.als)` returns correct structure
- `parse_als_file(three_tracks.als)` returns 3 tracks
- `detect_als_issues()` finds empty tracks
- `detect_als_issues()` finds no-name tracks
- `suggest_als_changes()` returns suggestions
- Error: nonexistent path → `FileNotFoundError`
- Error: invalid .als → clear error
- Error: empty file → clear error

**test_knowledge.py**:
- `get_available_devices()` returns 36 entries
- `get_device_knowledge("Wavetable")` returns 10+ parameters
- `get_device_knowledge("Wavetable", "Osc1 Level")` returns specific param range
- `get_device_knowledge("NonExistent")` returns empty
- All 5 JSON files parse without error
- Every device has >0 parameters

**test_max_bridge.py**:
- `MaxBridgeClient` initializes without python-osc (graceful fallback)
- `MaxBridgeClient` validates port > 1024
- `MaxBridgeClient` rejects unauthorized OSC addresses
- `test_max_bridge()` returns structured response without crash

**test_resources.py**:
- `live://session/current` URI template matches FastMCP pattern
- `live://track/{track_index}` URI template matches
- `live://device/{track_index}/{device_index}` URI template matches
- `live://clip/{track_index}/{clip_index}` URI template matches

### 1.3 CI/CD Pipeline

**`.github/workflows/ci.yml`**:
```yaml
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [checkout, setup-python, pip install -e ".[dev]", ruff check .]
  compile:
    steps: [checkout, setup-python, pip install -e ., python -m compileall MCP_Server]
  test:
    steps: [checkout, setup-python, pip install -e ".[dev]", pytest --cov]
```

### 1.4 Test Readme
- Add `tests/README.md` explaining: how to run tests, add new tests, interpret coverage
- Document fixture generation (how to create .als fixtures using Python gzip + ElementTree)

## Acceptance Criteria
```bash
python -m pytest tests/ -v --tb=short    # All tests pass
python -m pytest tests/ --cov=MCP_Server   # Coverage > 70%
python -m compileall MCP_Server            # All files compile
ruff check MCP_Server/                     # No lint errors
ls .github/workflows/ci.yml                # CI file exists
```

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Third-party deps not installable in CI | Locked | Pin versions; use `pip install -e ".[dev]"` |
| .als fixture format diverges from Live versions | Medium | Test with Live 12 fixtures; add version note |
| verify.py hard to mock (needs Live) | Low | Mock the send_command layer, test logic only |

## Must NOT Do
- Do NOT rewrite any existing test scripts (leave `scripts/test/` as-is)
- Do NOT test tools that require Live connection (unit tests only)
- Do NOT add heavy test runners (pytest-only)
- Do NOT add integration tests that require Ableton to run
