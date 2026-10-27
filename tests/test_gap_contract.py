"""Contract layer of the gap/bugfix test pyramid.

Source-level analysis only - no Live, no sockets:
  1. Handler existence: every spec command must be in _build_handlers
  2. Bug pattern detection: bugfix handlers must NOT contain the known defect
  3. Handler param extraction: handlers must extract spec-mandated param names

Gaps are xfail until implemented (TDD red).
Bugfixes are xfail until the bug pattern is removed.

Run:  pytest tests/test_gap_contract.py -v
"""
import os
import re
import pytest

from gap_specs import ALL_SPECS, GAPS, FIXES, IMPLEMENTED_GAPS, extract_handler_names

REMOTE_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "AbletonMCP_Remote_Script", "__init__.py"
)

with open(REMOTE_SCRIPT, encoding="utf-8") as f:
    SOURCE = f.read()

HANDLERS = extract_handler_names(SOURCE)


# ---------------------------------------------------------------------------
# 1. Handler existence
# ---------------------------------------------------------------------------

class TestHandlerExistence:
    """Every spec command must have a handler in _build_handlers."""

    @pytest.mark.parametrize("spec", GAPS, ids=[s.name for s in GAPS])
    def test_gap_handler_exists(self, spec):
        if spec.name not in HANDLERS:
            pytest.xfail("gap not yet implemented: " + spec.name)
        assert spec.name in HANDLERS

    @pytest.mark.parametrize("spec", FIXES, ids=[s.name for s in FIXES])
    def test_bugfix_handler_exists(self, spec):
        assert spec.name in HANDLERS, spec.name + ": handler missing"


# ---------------------------------------------------------------------------
# 2. Bug pattern detection (xfail until the bug is fixed)
# ---------------------------------------------------------------------------

class TestBugPatterns:
    """Bugfix handlers must NOT contain the known defect pattern."""

    def test_get_device_parameters_parameters_first(self):
        """The parameters branch must come BEFORE get_notes so Drum Racks
        (which have both) return macro parameters, not pad notes."""
        m = re.search(r'def _get_device_parameters\(self.*?(?=\n    def )', SOURCE, re.DOTALL)
        if not m:
            pytest.skip("_get_device_parameters not found in source")
        body = m.group(0)
        params_pos = body.find('hasattr(device, "parameters")')
        notes_pos = body.find('hasattr(device, "get_notes")')
        if params_pos < 0:
            pytest.skip("no parameters branch found")
        if notes_pos >= 0 and notes_pos < params_pos:
            pytest.xfail("bug unfixed: get_notes branch before parameters branch")
        assert params_pos >= 0, "parameters branch must exist"
        if notes_pos >= 0:
            assert params_pos < notes_pos, "parameters must be checked before get_notes"

    def test_delete_device_no_device_fallback(self):
        """device.delete_device() fails on RackDevice; must use track.delete_device only."""
        if "hasattr(device, 'delete_device')" in SOURCE:
            pytest.xfail("bug unfixed: device.delete_device() fallback still present")
        assert "hasattr(device, 'delete_device')" not in SOURCE

    def test_build_arrangement_defers_duplicates(self):
        """build_arrangement must run on the main thread (via MAIN_THREAD_COMMANDS)
        or defer duplicates via schedule_message, to avoid 'Changes cannot be
        triggered by notifications'."""
        # Check 1: is build_arrangement in MAIN_THREAD_COMMANDS?
        in_main_thread = re.search(
            r'MAIN_THREAD_COMMANDS\s*=\s*frozenset\(\{.*?"build_arrangement".*?\}\)',
            SOURCE, re.DOTALL)
        # Check 2: does _build_arrangement itself use schedule_message?
        m = re.search(r'def _build_arrangement\(self.*?(?=\n    def )', SOURCE, re.DOTALL)
        body = m.group(0) if m else ""
        has_sched = "schedule_message" in body
        has_dup = "duplicate_clip_to_arrangement" in body
        if not has_dup:
            pytest.skip("duplicate_clip_to_arrangement not in _build_arrangement")
        if not in_main_thread and not has_sched:
            pytest.xfail("bug unfixed: no main-thread scheduling and no schedule_message")
        assert has_dup, "duplicate_clip_to_arrangement must be in _build_arrangement"


# ---------------------------------------------------------------------------
# 3. Handler param extraction (implemented handlers only)
# ---------------------------------------------------------------------------

def _handler_extracts_param(source, command_name, param_name):
    """Check if the handler lambda for command_name extracts param_name via p.get()."""
    # Pattern: "command_name": lambda p: ... p.get("param_name" ...
    pattern = r'"' + re.escape(command_name) + r'":\s*lambda\s+p:.*?p\.get\("' + re.escape(param_name) + r'"'
    return bool(re.search(pattern, source, re.DOTALL))


class TestHandlerParamExtraction:
    """For implemented handlers, verify they extract the spec's param names."""

    @pytest.mark.parametrize("spec", FIXES, ids=[s.name for s in FIXES])
    def test_fix_extracts_spec_params(self, spec):
        for p in spec.params:
            if not _handler_extracts_param(SOURCE, spec.name, p.name):
                pytest.xfail(spec.name + ": handler does not extract param " + p.name)
            assert _handler_extracts_param(SOURCE, spec.name, p.name)

    @pytest.mark.parametrize("spec", GAPS, ids=[s.name for s in GAPS])
    def test_gap_param_extraction_skipped(self, spec):
        if spec.name not in HANDLERS:
            pytest.skip("not yet implemented: " + spec.name)
        for p in spec.params:
            assert _handler_extracts_param(SOURCE, spec.name, p.name), \
                spec.name + ": missing param " + p.name


# ---------------------------------------------------------------------------
# 4. Implemented gap handlers (rack macros, drum pads)
# ---------------------------------------------------------------------------

class TestImplementedGapHandlers:
    """Implemented gap commands must have handlers and extract the right params."""

    @pytest.mark.parametrize("spec", IMPLEMENTED_GAPS, ids=[s.name for s in IMPLEMENTED_GAPS])
    def test_handler_exists(self, spec):
        assert spec.name in HANDLERS, spec.name + ": handler missing from _build_handlers"

    @pytest.mark.parametrize("spec", IMPLEMENTED_GAPS, ids=[s.name for s in IMPLEMENTED_GAPS])
    def test_param_extraction(self, spec):
        for p in spec.params:
            assert _handler_extracts_param(SOURCE, spec.name, p.name), \
                spec.name + ": handler does not extract param " + p.name
