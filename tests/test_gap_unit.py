"""Unit layer of the gap/bugfix test pyramid.

Pure logic only - no Live, no sockets:
  1. spec well-formedness (all 20 specs)
  2. accept/reject matrix for every param validator
  3. source-analysis helpers against the real Remote Script source

Run:  pytest tests/test_gap_unit.py -v
"""
import pytest

from gap_specs import (
    ALL_SPECS, GAPS, FIXES, BY_CATEGORY,
    HANDLER_RE, extract_handler_names, missing_handlers,
    norm01, nonneg, track_index, macro_index, pad_index,
    device_index, view_name, str_nonempty, file_path,
    IMPLEMENTED_GAPS,
)

import os

REMOTE_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "AbletonMCP_Remote_Script", "__init__.py"
)

KNOWN_CATEGORIES = {
    "gap-rack", "gap-pads", "gap-view", "gap-fades",
    "gap-mix", "gap-problems", "gap-midi", "bugfix",
}


# ---------------------------------------------------------------------------
# 1. Spec well-formedness
# ---------------------------------------------------------------------------

class TestSpecWellFormed:

    def test_counts(self):
        assert len(ALL_SPECS) == 20
        assert len(GAPS) == 10
        assert len(IMPLEMENTED_GAPS) == 7
        assert len(FIXES) == 3

    def test_names_unique(self):
        names = [s.name for s in ALL_SPECS]
        assert len(names) == len(set(names)), "duplicate spec names"

    def test_categories_known(self):
        assert set(BY_CATEGORY) <= KNOWN_CATEGORIES

    def test_implemented_flag_consistent(self):
        for s in ALL_SPECS:
            if s.category == "bugfix":
                assert s.implemented, s.name + ": bugfixes must be implemented=True"
                assert s.bug, s.name + ": bugfix must describe the defect"
            else:
                # Gaps may be implemented later; if so, they must have no bug text
                if s.implemented:
                    assert not s.bug, s.name + ": implemented gap must have no bug text"
                else:
                    assert not s.bug, s.name + ": gap must have no bug text"

    def test_params_have_names_and_types(self):
        for s in ALL_SPECS:
            pnames = [p.name for p in s.params]
            assert len(pnames) == len(set(pnames)), s.name + ": duplicate params"
            for p in s.params:
                assert p.name
                assert p.type in (int, float, str, bool, dict, list)
                if p.validate is not None:
                    assert callable(p.validate)

    def test_returns_is_dict(self):
        for s in ALL_SPECS:
            assert isinstance(s.returns, dict) and s.returns, s.name


# ---------------------------------------------------------------------------
# 2. Validator accept/reject matrix
# ---------------------------------------------------------------------------

class TestValidatorContract:
    """Every validator returns (ok: bool, reason: str)."""

    def test_reject_returns_reason(self):
        ok, reason = norm01(2.0)
        assert ok is False
        assert isinstance(reason, str) and reason

    def test_accept_returns_true(self):
        ok, _ = norm01(0.5)
        assert ok is True


class TestNorm01:
    @pytest.mark.parametrize("v", [0.0, 1.0, 0.5, 0, 1])
    def test_accept(self, v):
        assert norm01(v)[0]

    @pytest.mark.parametrize("v", [-0.01, 1.01, 2, "0.5", None, True, False])
    def test_reject(self, v):
        assert not norm01(v)[0]


class TestNonNeg:
    @pytest.mark.parametrize("v", [0.0, 0.5, 3])
    def test_accept(self, v):
        assert nonneg(v)[0]

    @pytest.mark.parametrize("v", [-0.001, -5, "1", None])
    def test_reject(self, v):
        assert not nonneg(v)[0]


class TestIndexValidators:
    @pytest.mark.parametrize("fn", [track_index, device_index])
    @pytest.mark.parametrize("v", [0, 1, 100])
    def test_accept(self, fn, v):
        assert fn(v)[0]

    @pytest.mark.parametrize("fn", [track_index, device_index])
    @pytest.mark.parametrize("v", [-1, 1.5, "0", True])
    def test_reject(self, fn, v):
        assert not fn(v)[0]

    @pytest.mark.parametrize("fn", [macro_index, pad_index])
    @pytest.mark.parametrize("v", [0, 36, 127])
    def test_accept_0_127(self, fn, v):
        assert fn(v)[0]

    @pytest.mark.parametrize("fn", [macro_index, pad_index])
    @pytest.mark.parametrize("v", [-1, 128, 1.5, "36", False])
    def test_reject_0_127(self, fn, v):
        assert not fn(v)[0]


class TestViewName:
    @pytest.mark.parametrize("v", ["Session", "Arranger", "Clip", "Device",
                                   "Browser", "Detail/Clip", "Detail/Device"])
    def test_accept(self, v):
        assert view_name(v)[0]

    @pytest.mark.parametrize("v", ["session", "SESSION", "Bogus", "", None, 1])
    def test_reject(self, v):
        assert not view_name(v)[0]


class TestStrNonEmpty:
    @pytest.mark.parametrize("v", ["Kick", "x", " "])
    def test_accept(self, v):
        assert str_nonempty(v)[0]

    @pytest.mark.parametrize("v", ["", None, 5, []])
    def test_reject(self, v):
        assert not str_nonempty(v)[0]


class TestFilePath:
    @pytest.mark.parametrize("v", ["out.mid", "C:/x/pattern.MIDI", "a/b/c.mid"])
    def test_accept(self, v):
        assert file_path(v)[0]

    @pytest.mark.parametrize("v", ["out.wav", "out.txt", ".mid", "", None])
    def test_reject(self, v):
        assert not file_path(v)[0]


# ---------------------------------------------------------------------------
# 3. Source-analysis helpers vs the real Remote Script
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def source():
    with open(REMOTE_SCRIPT, encoding="utf-8") as f:
        return f.read()


class TestSourceAnalysis:

    def test_finds_all_153_handlers(self, source):
        names = extract_handler_names(source)
        assert len(names) == 153

    def test_known_handlers_present(self, source):
        names = extract_handler_names(source)
        for known in ("get_session_info", "set_tempo", "create_clip",
                      "get_device_parameters", "delete_device", "build_arrangement"):
            assert known in names

    def test_no_false_positives_from_garbage(self):
        assert extract_handler_names('"not_a_cmd": lambda x: x') == set()

    def test_missing_lists_all_gaps(self, source):
        missing = missing_handlers(source)
        gap_names = {s.name for s in GAPS}
        assert set(missing) == gap_names
        assert len(missing) == 10

    def test_no_bugfix_missing(self, source):
        missing = set(missing_handlers(source))
        for s in FIXES:
            assert s.name not in missing
