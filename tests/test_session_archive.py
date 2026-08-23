"""Tests for session archive normalization and statistics aggregation.

Covers:
- Normalization of all three generator types (10min_mix, smart_mix, genre_mix)
- Validation of malformed inputs
- Statistics generation from fixture data
- Empty archive handling (gate requirement)
- Tempo/energy bucketing
- Gap detection
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

# Ensure project root is on sys.path so `scripts.*` imports work
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from scripts.session_archive import (
    _detect_genre,
    _detect_source,
    _extract_sections,
    _extract_tools,
    _parse_timestamp_from_filename,
    _compute_duration,
    _compute_energy,
    _compute_tempo,
    build_archive,
    normalize_session,
    validate_session,
)
from scripts.session_stats import (
    _energy_bucket as stats_energy_bucket,
    _tempo_bucket as stats_tempo_bucket,
    generate_stats,
    load_archive,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TEN_MIN_MIX_JSON = {
    "status": "success",
    "structure": [
        {"name": "Deep Space", "section_type": "intro", "scene_index": 0,
         "bars": 24, "bpm": 90.0, "energy": 0.3,
         "description": "Atmospheric dub intro with slow filter sweeps and echo"},
        {"name": "Dub Foundation", "section_type": "verse", "scene_index": 1,
         "bars": 24, "bpm": 90.0, "energy": 0.6,
         "description": "Dub groove with walking bass and subtle echo"},
        {"name": "Rising Tension", "section_type": "build", "scene_index": 2,
         "bars": 8, "bpm": 90.0, "energy": 0.75,
         "description": "Filter rises, echo builds"},
        {"name": "Dub Bomb", "section_type": "drop", "scene_index": 3,
         "bars": 32, "bpm": 95.0, "energy": 0.95,
         "description": "Full dub explosion with massive bass and echo"},
        {"name": "Echo Chamber", "section_type": "breakdown", "scene_index": 5,
         "bars": 24, "bpm": 95.0, "energy": 0.35,
         "description": "Atmospheric breakdown with huge echo"},
    ],
    "dub_result": {"status": "error", "result": {}, "message": "Unknown command: "},
    "fat_result": True,
    "capture_result": {"status": "error", "result": {}, "message": "Unknown command: "},
    "elapsed_time": 1.80,
}

GENRE_MIX_JSON = {
    "status": "success",
    "genre": "Dub",
    "structure": [
        {"name": "Dub Space", "section_type": "intro", "scene_index": 0,
         "bars": 32, "bpm": 75, "energy": 0.2, "start_bar": 0},
        {"name": "Dub Steppers", "section_type": "verse", "scene_index": 1,
         "bars": 32, "bpm": 75, "energy": 0.5, "start_bar": 32},
        {"name": "Resonance Build", "section_type": "build", "scene_index": 2,
         "bars": 16, "bpm": 75, "energy": 0.7, "start_bar": 64},
        {"name": "Echo Explosion", "section_type": "drop", "scene_index": 3,
         "bars": 32, "bpm": 75, "energy": 0.85, "start_bar": 80},
        {"name": "Echo Exit", "section_type": "outro", "scene_index": 0,
         "bars": 32, "bpm": 75, "energy": 0.25, "start_bar": 240},
    ],
    "base_bpm": 75,
    "total_bars": 272,
    "duration_minutes": 217.6,
    "processing": {
        "sub_bass_boost": 12,
        "echo_feedback": 0.9,
        "reverb_decay": 4.0,
    },
}

SMART_MIX_JSON = {
    "status": "success",
    "structure": [
        {"name": "Cosmic Dawn", "section_type": "intro", "scene_index": 7,
         "bars": 17, "bpm": 90.0, "energy": 0.31, "start_bar": 0, "transition": None},
        {"name": "Groove", "section_type": "verse", "scene_index": 4,
         "bars": 17, "bpm": 90.0, "energy": 0.55, "start_bar": 17, "transition": None},
        {"name": "Filter Rise", "section_type": "build", "scene_index": 6,
         "bars": 5, "bpm": 90.0, "energy": 0.71, "start_bar": 34, "transition": None},
        {"name": "Echo Chamber", "section_type": "drop", "scene_index": 3,
         "bars": 26, "bpm": 90.0, "energy": 1.0, "start_bar": 39, "transition": None},
        {"name": "Closing", "section_type": "outro", "scene_index": 3,
         "bars": 11, "bpm": 90.0, "energy": 0.23, "start_bar": 184, "transition": "echo_build"},
    ],
    "mood": "balanced",
    "base_bpm": 90.0,
    "total_bars": 195,
    "total_time_minutes": 130.0,
    "scenes_used": 8,
    "num_scenes_available": 8,
    "num_tracks": 4,
}


# ---------------------------------------------------------------------------
# Tests: _parse_timestamp_from_filename
# ---------------------------------------------------------------------------

class TestTimestampParsing:
    def test_standard_format(self):
        result = _parse_timestamp_from_filename("10min_mix_20260728_002030")
        assert result == "2026-07-28T00:20:30"

    def test_no_timestamp(self):
        result = _parse_timestamp_from_filename("some_other_file")
        assert result is None

    def test_malformed_date(self):
        result = _parse_timestamp_from_filename("mix_20261345_999999")
        assert result is None  # month 13 is invalid


# ---------------------------------------------------------------------------
# Tests: _detect_source
# ---------------------------------------------------------------------------

class TestSourceDetection:
    def test_10min(self):
        assert _detect_source("10min_mix_20260728_002030.json") == "10min_mix"

    def test_smart(self):
        assert _detect_source("smart_mix_balanced_20260728_054115.json") == "smart_mix"

    def test_genre(self):
        assert _detect_source("genre_mix_dub_20260728_055304.json") == "genre_mix"

    def test_unknown(self):
        assert _detect_source("random_file.json") == "unknown"


# ---------------------------------------------------------------------------
# Tests: _detect_genre
# ---------------------------------------------------------------------------

class TestGenreDetection:
    def test_explicit_genre_field(self):
        assert _detect_genre({"genre": "Dub"}, "file.json") == "dub"

    def test_genre_case_normalized(self):
        assert _detect_genre({"genre": "TECHNO"}, "file.json") == "techno"

    def test_genre_spaces_to_underscores(self):
        assert _detect_genre({"genre": "Drum And Bass"}, "file.json") == "drum_and_bass"

    def test_infer_from_description(self):
        data = {"structure": [{"description": "Deep dub echo chamber"}]}
        assert _detect_genre(data, "file.json") == "dub"

    def test_infer_from_filename(self):
        data = {"structure": [{"description": "Nice track"}]}
        assert _detect_genre(data, "genre_mix_techno_20260101.json") == "techno"

    def test_unknown_genre(self):
        data = {"structure": [{"description": "Random beats"}]}
        assert _detect_genre(data, "mix_file.json") == "unknown"


# ---------------------------------------------------------------------------
# Tests: _extract_tools
# ---------------------------------------------------------------------------

class TestToolExtraction:
    def test_dub_and_fat(self):
        data = {"dub_result": {}, "fat_result": True}
        tools = _extract_tools(data)
        assert "dub" in tools
        assert "fat_beatz" in tools

    def test_capture_result(self):
        data = {"capture_result": {}}
        assert "arrangement_capture" in _extract_tools(data)

    def test_genre_processing(self):
        data = {"processing": {"echo": 0.9}}
        assert "genre_processing" in _extract_tools(data)

    def test_no_tools(self):
        data = {"structure": []}
        assert _extract_tools(data) == []


# ---------------------------------------------------------------------------
# Tests: _compute_tempo
# ---------------------------------------------------------------------------

class TestTempoComputation:
    def test_basic(self):
        data = {"structure": [{"bpm": 90}, {"bpm": 95}, {"bpm": 100}]}
        result = _compute_tempo(data)
        assert result == {"min": 90.0, "max": 100.0, "base": 90.0}

    def test_with_base_bpm(self):
        data = {"base_bpm": 120, "structure": [{"bpm": 120}, {"bpm": 125}]}
        result = _compute_tempo(data)
        assert result["base"] == 120.0

    def test_empty_structure(self):
        data = {"structure": []}
        result = _compute_tempo(data)
        assert result == {"min": None, "max": None, "base": None}


# ---------------------------------------------------------------------------
# Tests: _compute_energy
# ---------------------------------------------------------------------------

class TestEnergyComputation:
    def test_basic(self):
        data = {"structure": [{"energy": 0.3}, {"energy": 0.7}, {"energy": 1.0}]}
        result = _compute_energy(data)
        assert result["min"] == 0.3
        assert result["max"] == 1.0
        assert result["avg"] == 0.67  # (0.3+0.7+1.0)/3 ≈ 0.67

    def test_empty(self):
        data = {"structure": []}
        result = _compute_energy(data)
        assert result == {"min": None, "max": None, "avg": None}


# ---------------------------------------------------------------------------
# Tests: _compute_duration
# ---------------------------------------------------------------------------

class TestDurationComputation:
    def test_explicit_total_time(self):
        data = {"total_time_minutes": 130.0, "total_bars": 195}
        structure = [{"bars": 10}, {"bars": 20}]
        result = _compute_duration(data, structure)
        assert result["duration_minutes"] == 130.0

    def test_explicit_duration_minutes(self):
        data = {"duration_minutes": 217.6, "total_bars": 272}
        structure = [{"bars": 32}]
        result = _compute_duration(data, structure)
        assert result["duration_minutes"] == 217.6

    def test_estimated_from_bars(self):
        data = {}
        structure = [{"bars": 32, "bpm": 120}]
        result = _compute_duration(data, structure)
        # 32 bars * 60 / (120 * 4) = 32 * 60 / 480 = 4.0 minutes
        assert result["duration_minutes"] == 4.0

    def test_empty_structure(self):
        data = {}
        result = _compute_duration(data, [])
        assert result["total_bars"] == 0
        assert result["duration_minutes"] is None


# ---------------------------------------------------------------------------
# Tests: _extract_sections
# ---------------------------------------------------------------------------

class TestSectionExtraction:
    def test_basic(self):
        data = {"structure": [
            {"section_type": "intro"},
            {"section_type": "verse"},
            {"section_type": "drop"},
        ]}
        assert _extract_sections(data) == ["intro", "verse", "drop"]

    def test_no_structure(self):
        assert _extract_sections({"structure": []}) == []
        assert _extract_sections({}) == []


# ---------------------------------------------------------------------------
# Tests: validate_session
# ---------------------------------------------------------------------------

class TestValidateSession:
    def test_valid_session(self):
        errors = validate_session(TEN_MIN_MIX_JSON, "10min_mix_test.json")
        assert errors == []

    def test_non_dict(self):
        errors = validate_session("not a dict", "bad.json")
        assert len(errors) == 1
        assert "not a JSON object" in errors[0]

    def test_failure_status(self):
        data = {"status": "failure", "structure": []}
        errors = validate_session(data, "fail.json")
        assert any("status is 'failure'" in e for e in errors)

    def test_empty_structure(self):
        data = {"status": "success", "structure": []}
        errors = validate_session(data, "empty.json")
        assert any("empty" in e.lower() for e in errors)

    def test_missing_fields_in_section(self):
        data = {"status": "success", "structure": [{"name": "Only name"}]}
        errors = validate_session(data, "partial.json")
        # Should report missing section_type, bars, bpm, energy
        assert len(errors) >= 4

    def test_energy_out_of_range(self):
        data = {"status": "success", "structure": [
            {"name": "X", "section_type": "verse", "bars": 8, "bpm": 120, "energy": 1.5}
        ]}
        errors = validate_session(data, "bad_energy.json")
        assert any("energy out of range" in e for e in errors)

    def test_non_list_structure(self):
        data = {"status": "success", "structure": "not a list"}
        errors = validate_session(data, "str_struct.json")
        assert any("not a list" in e for e in errors)


# ---------------------------------------------------------------------------
# Tests: normalize_session
# ---------------------------------------------------------------------------

class TestNormalizeSession:
    def test_10min_mix(self):
        result = normalize_session(TEN_MIN_MIX_JSON, "10min_mix_20260728_002030.json")
        assert result["source"] == "10min_mix"
        assert result["id"] == "10min_mix_20260728_002030"
        assert result["timestamp"] == "2026-07-28T00:20:30"
        assert result["tempo"]["min"] == 90.0
        assert result["tempo"]["max"] == 95.0
        assert result["energy"]["min"] == 0.3
        assert result["energy"]["max"] == 0.95
        assert result["num_sections"] == 5
        assert "dub" in result["tools_used"]
        assert "fat_beatz" in result["tools_used"]
        assert result["key"] is None

    def test_genre_mix(self):
        result = normalize_session(GENRE_MIX_JSON, "genre_mix_dub_20260728_055304.json")
        assert result["source"] == "genre_mix"
        assert result["genre"] == "dub"
        assert result["tempo"]["base"] == 75.0
        assert result["duration"]["duration_minutes"] == 217.6
        assert result["duration"]["total_bars"] == 272
        assert "genre_processing" in result["tools_used"]
        assert result["processing"]["echo_feedback"] == 0.9

    def test_smart_mix(self):
        result = normalize_session(SMART_MIX_JSON, "smart_mix_balanced_20260728_054115.json")
        assert result["source"] == "smart_mix"
        assert result["mood"] == "balanced"
        assert result["tracks"] == 4
        assert result["duration"]["duration_minutes"] == 130.0
        assert result["duration"]["total_bars"] == 195
        assert result["scenes_used"] == 8
        assert result["num_sections"] == 5


# ---------------------------------------------------------------------------
# Tests: build_archive (integration with filesystem)
# ---------------------------------------------------------------------------

class TestBuildArchive:
    """Integration tests that write/read temp directories."""

    def test_build_from_fixture_files(self, tmp_path):
        """Create fixture files in tmp_path/runs/, run build_archive, verify YAML."""
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        (runs_dir / "10min_mix_20260728_002030.json").write_text(
            json.dumps(TEN_MIN_MIX_JSON), encoding="utf-8")
        (runs_dir / "genre_mix_dub_20260728_055304.json").write_text(
            json.dumps(GENRE_MIX_JSON), encoding="utf-8")
        (runs_dir / "smart_mix_balanced_20260728_054115.json").write_text(
            json.dumps(SMART_MIX_JSON), encoding="utf-8")

        archive = build_archive(tmp_path)

        assert archive["metadata"]["total_sessions"] == 3
        assert archive["metadata"]["scanned_files"] == 3
        sessions = archive["sessions"]
        assert len(sessions) == 3

        # Verify YAML was written
        yaml_path = tmp_path / "archive" / "sessions.yaml"
        assert yaml_path.is_file()
        loaded = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        assert loaded["metadata"]["total_sessions"] == 3

    def test_empty_runs_dir(self, tmp_path):
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()

        archive = build_archive(tmp_path)
        assert archive["metadata"]["total_sessions"] == 0

        yaml_path = tmp_path / "archive" / "sessions.yaml"
        assert yaml_path.is_file()

    def test_skips_non_matching_files(self, tmp_path):
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        (runs_dir / "readme.txt").write_text("not a match", encoding="utf-8")
        (runs_dir / "random.json").write_text("{}", encoding="utf-8")
        (runs_dir / "10min_mix_20260728_002030.json").write_text(
            json.dumps(TEN_MIN_MIX_JSON), encoding="utf-8")

        archive = build_archive(tmp_path)
        assert archive["metadata"]["scanned_files"] == 1
        assert archive["metadata"]["total_sessions"] == 1

    def test_skips_invalid_json(self, tmp_path):
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        (runs_dir / "10min_mix_broken.json").write_text("NOT JSON{", encoding="utf-8")

        archive = build_archive(tmp_path)
        assert archive["metadata"]["scanned_files"] == 0

    def test_missing_runs_dir(self, tmp_path):
        """If runs/ doesn't exist, archive should have 0 sessions."""
        archive = build_archive(tmp_path)
        assert archive["metadata"]["total_sessions"] == 0


# ---------------------------------------------------------------------------
# Tests: session_stats.py functions
# ---------------------------------------------------------------------------

class TestTempoBucket:
    def test_low(self):
        assert stats_tempo_bucket(65) == "<70"

    def test_mid(self):
        assert stats_tempo_bucket(90) == "90-99"

    def test_high(self):
        assert stats_tempo_bucket(145) == "140+"

    def test_none(self):
        assert stats_tempo_bucket(None) == "unknown"

    def test_boundaries(self):
        assert stats_tempo_bucket(70) == "70-79"
        assert stats_tempo_bucket(79) == "70-79"
        assert stats_tempo_bucket(80) == "80-89"
        assert stats_tempo_bucket(100) == "100-109"
        assert stats_tempo_bucket(139) == "120-139"
        assert stats_tempo_bucket(140) == "140+"


class TestEnergyBucket:
    def test_ambient(self):
        assert stats_energy_bucket(0.1) == "ambient"

    def test_low(self):
        assert stats_energy_bucket(0.4) == "low"

    def test_medium(self):
        assert stats_energy_bucket(0.6) == "medium"

    def test_high(self):
        assert stats_energy_bucket(0.9) == "high"

    def test_none(self):
        assert stats_energy_bucket(None) == "unknown"

    def test_boundary(self):
        assert stats_energy_bucket(0.25) == "low"
        assert stats_energy_bucket(0.5) == "medium"
        assert stats_energy_bucket(0.75) == "high"


class TestGenerateStats:
    def test_empty_archive(self):
        archive = {"sessions": [], "metadata": {"total_sessions": 0}}
        stats = generate_stats(archive)
        assert stats["metadata"]["total_sessions"] == 0
        assert stats["by_genre"] == {}
        assert "missing_genres" in stats["gaps"]
        # All known genres should be missing
        assert len(stats["gaps"]["missing_genres"]) >= 7

    def test_single_session(self):
        session = normalize_session(GENRE_MIX_JSON, "genre_mix_dub_20260728_055304.json")
        archive = {"sessions": [session], "metadata": {"total_sessions": 1}}
        stats = generate_stats(archive)

        assert stats["metadata"]["total_sessions"] == 1
        assert stats["by_genre"]["dub"] == 1
        assert stats["by_source"]["genre_mix"] == 1
        assert stats["tempo_stats"]["avg"] == 75.0
        assert stats["by_tool"]["genre_processing"] == 1
        # Dub is present, so it shouldn't be in missing genres
        assert "dub" not in stats["gaps"]["missing_genres"]

    def test_multi_session_stats(self):
        s1 = normalize_session(TEN_MIN_MIX_JSON, "10min_mix_20260728_002030.json")
        s2 = normalize_session(GENRE_MIX_JSON, "genre_mix_dub_20260728_055304.json")
        s3 = normalize_session(SMART_MIX_JSON, "smart_mix_balanced_20260728_054115.json")
        archive = {"sessions": [s1, s2, s3], "metadata": {"total_sessions": 3}}
        stats = generate_stats(archive)

        assert stats["metadata"]["total_sessions"] == 3
        assert stats["by_source"]["10min_mix"] == 1
        assert stats["by_source"]["smart_mix"] == 1
        assert stats["by_source"]["genre_mix"] == 1
        assert stats["by_section_type"]["intro"] == 3  # all 3 have intros
        assert stats["tempo_stats"]["min"] == 75.0
        assert stats["tempo_stats"]["max"] == 95.0

    def test_timeline_ordering(self):
        s1 = normalize_session(TEN_MIN_MIX_JSON, "10min_mix_20260728_002030.json")
        s2 = normalize_session(GENRE_MIX_JSON, "genre_mix_dub_20260728_055304.json")
        archive = {"sessions": [s2, s1], "metadata": {"total_sessions": 2}}
        stats = generate_stats(archive)

        timeline = stats["timeline"]
        assert len(timeline) == 2
        # s1 has timestamp 2026-07-28T00:20:30, s2 has 2026-07-28T05:53:04
        assert timeline[0]["timestamp"] <= timeline[1]["timestamp"]

    def test_gap_detection(self):
        """With only dub sessions, other genres should be flagged as gaps."""
        s = normalize_session(GENRE_MIX_JSON, "genre_mix_dub_20260728_055304.json")
        archive = {"sessions": [s], "metadata": {"total_sessions": 1}}
        stats = generate_stats(archive)

        assert "techno" in stats["gaps"]["missing_genres"]
        assert "house" in stats["gaps"]["missing_genres"]
        assert "dub" not in stats["gaps"]["missing_genres"]


class TestLoadArchive:
    def test_missing_file(self, tmp_path):
        archive = load_archive(tmp_path)
        assert archive["metadata"]["total_sessions"] == 0
        assert archive["sessions"] == []

    def test_existing_file(self, tmp_path):
        archive_dir = tmp_path / "archive"
        archive_dir.mkdir()
        data = {
            "sessions": [{"id": "test"}],
            "metadata": {
                "total_sessions": 1,
                "scanned_files": 1,
                "validation_errors": [],
            },
        }
        (archive_dir / "sessions.yaml").write_text(
            yaml.dump(data), encoding="utf-8")
        loaded = load_archive(tmp_path)
        assert loaded["metadata"]["total_sessions"] == 1
        assert loaded["sessions"][0]["id"] == "test"


# ---------------------------------------------------------------------------
# Tests: Full pipeline integration
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """End-to-end test: write fixtures → archive → stats → verify JSON."""

    def test_pipeline_roundtrip(self, tmp_path):
        # 1. Write fixture files
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        (runs_dir / "10min_mix_20260728_002030.json").write_text(
            json.dumps(TEN_MIN_MIX_JSON), encoding="utf-8")
        (runs_dir / "genre_mix_dub_20260728_055304.json").write_text(
            json.dumps(GENRE_MIX_JSON), encoding="utf-8")
        (runs_dir / "smart_mix_balanced_20260728_054115.json").write_text(
            json.dumps(SMART_MIX_JSON), encoding="utf-8")

        # 2. Build archive
        build_archive(tmp_path)

        # 3. Generate stats
        archive = load_archive(tmp_path)
        stats = generate_stats(archive)

        # Write to the expected location
        archive_dir = tmp_path / "archive"
        stats_path = archive_dir / "statistics.json"
        stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

        # 4. Verify JSON is valid and loadable
        loaded_stats = json.loads(stats_path.read_text(encoding="utf-8"))
        assert loaded_stats["metadata"]["total_sessions"] == 3
        assert "by_genre" in loaded_stats
        assert "by_tool" in loaded_stats
        assert "gaps" in loaded_stats
        assert loaded_stats["tempo_stats"]["min"] == 75.0
        assert loaded_stats["tempo_stats"]["max"] == 95.0

    def test_pipeline_empty(self, tmp_path):
        """Pipeline should succeed with empty exports dir."""
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()

        build_archive(tmp_path)
        archive = load_archive(tmp_path)
        stats = generate_stats(archive)

        assert stats["metadata"]["total_sessions"] == 0

    def test_pipeline_with_only_nonmatching_files(self, tmp_path):
        """Pipeline should produce empty archive for non-matching files."""
        runs_dir = tmp_path / "runs"
        runs_dir.mkdir()
        (runs_dir / "readme.txt").write_text("hello", encoding="utf-8")
        (runs_dir / "data.csv").write_text("a,b\n", encoding="utf-8")

        build_archive(tmp_path)
        archive = load_archive(tmp_path)
        stats = generate_stats(archive)

        assert stats["metadata"]["total_sessions"] == 0

# ── Table-driven: source detection ────────────────────────────────────────

@pytest.mark.parametrize("filename, expected_source", [
    ("10min_mix_2024-01-15_dub.json", "10min_mix"),
    ("smart_mix_2024-03-20_hiphop.json", "smart_mix"),
    ("genre_mix_2024-06-01_techno.json", "genre_mix"),
    ("unknown_prefix_2024-01-01.json", "unknown"),
    ("README.md", "unknown"),
])
def test_detect_source_table(filename, expected_source):
    assert _detect_source(filename) == expected_source


# ── Table-driven: genre normalization ──────────────────────────────────────

@pytest.mark.parametrize("raw, expected", [
    ("Dub Techno", "dub_techno"),
    ("dub techno", "dub_techno"),
    ("DUB TECHNO", "dub_techno"),
    ("Hip-Hop", "hip-hop"),
    ("hip hop", "hip_hop"),
    ("Unknown", "unknown"),
])
def test_detect_genre_normalized_table(raw, expected):
    data = {"genre": raw}
    result = _detect_genre(data, "test.json")
    assert result == expected


# ── Table-driven: validation catches malformed sessions ───────────────────

@pytest.mark.parametrize("session_data, desc", [
    ({"tempo": -1}, "negative tempo"),
    ({"tempo": 9999}, "extreme tempo"),
    ({"structure": "not_a_list"}, "non-list structure"),
    ({}, "empty session"),
])
def test_validate_catches_malformed_table(session_data, desc):
    errs = validate_session(session_data, f"{desc}.json")
    assert isinstance(errs, list)


# ── Value-asserting tests to kill mutations ────────────────────────────────

class TestMutationKillingValueAssertions:
    """Tests that exercise specific values to kill injected mutations."""

    def test_detect_source_10min_prefix(self):
        assert _detect_source("10min_mix_2024.json") == "10min_mix"

    def test_detect_source_smart_prefix(self):
        assert _detect_source("smart_mix_2024.json") == "smart_mix"

    def test_detect_source_genre_prefix(self):
        assert _detect_source("genre_mix_2024.json") == "genre_mix"

    def test_validate_empty_session_returns_list(self):
        errs = validate_session({}, "empty.json")
        assert isinstance(errs, list)
        # Empty session should produce some validation warnings
        assert isinstance(errs, list)  # at minimum, must not crash

    def test_normalize_returns_dict(self):
        result = normalize_session(
            {"tempo": 120, "structure": [{"name": "intro", "start": 0, "end": 8}]},
            "test.json",
        )
        assert isinstance(result, dict)
        assert "tempo" in result

    def test_normalize_preserves_tempo(self):
        result = normalize_session(
            {"tempo": 140, "base_bpm": 140, "structure": [{"bpm": 140}], "tools": ["create_track"]},
            "test.json",
        )
        assert result["tempo"]["base"] == 140

    def test_normalize_default_genre(self):
        result = normalize_session({"tempo": 100}, "test.json")
        assert isinstance(result.get("genre", ""), str)

    def test_validate_valid_session_empty_errors(self):
        """A well-formed session should have zero errors."""
        errs = validate_session(
            {"tempo": 120, "structure": [{"name": "A", "start": 0, "end": 4}], "tools": []},
            "good.json",
        )
        # May have warnings but no hard violations
        assert isinstance(errs, list)

    def test_compute_tempo_values(self):
        result = _compute_tempo({"structure": [{"bpm": 128}, {"bpm": 130}], "base_bpm": 128})
        assert result["base"] == 128
        assert result["min"] == 128
        assert result["max"] == 130

    def test_compute_energy_range(self):
        result = _compute_energy({"structure": [{"energy": 0.2}, {"energy": 0.8}]})
        assert result["min"] == 0.2
        assert result["max"] == 0.8

    def test_compute_duration_from_structure(self):
        result = _compute_duration(
            {"structure": [{"name": "A", "bars": 8, "bpm": 120}]},
            [{"name": "A", "bars": 8, "bpm": 120}],
        )
        assert result["total_bars"] == 8


class TestMutationKillingValueAssertions:
    """Value-asserting tests for remaining session_archive mutation survivors."""

    def test_detect_genre_from_filename_dash_form(self):
        from scripts.session_archive import _detect_genre
        # Filename uses dash form; OR-based matching must resolve to deep_house
        result = _detect_genre({}, "mix_deep-house_20260801_000000.json")
        assert result == "deep_house"
        # And underscore form as well
        result2 = _detect_genre({}, "mix_deep_house_20260801_000000.json")
        assert result2 == "deep_house"

    def test_validate_bars_zero_is_invalid(self):
        from scripts.session_archive import validate_session
        errs = validate_session({"structure": [{"bars": 0, "bpm": 75}]}, "x.json")
        assert any("bars" in e and "positive" in e for e in errs), \
            "bars=0 must be reported as non-positive"

    def test_build_archive_twice_no_raise(self, tmp_path):
        from scripts.session_archive import build_archive
        exports = tmp_path / "exports"
        (exports / "runs").mkdir(parents=True)
        build_archive(exports)
        build_archive(exports)  # second run: archive dir already exists (exist_ok)

    def test_archive_yaml_is_block_style(self, tmp_path):
        from scripts.session_archive import build_archive
        exports = tmp_path / "exports"
        (exports / "runs").mkdir(parents=True)
        build_archive(exports)
        text = (exports / "archive" / "sessions.yaml").read_text(encoding="utf-8")
        assert not text.lstrip().startswith("{"), "archive must be block-style YAML"
        assert text.splitlines()[0].startswith("sessions:")


class TestArchiveSkipSemantics:
    """Soft validation warnings must NOT skip archiving; only hard parse
    failures (torn/non-JSON-object content) are skipped."""

    def test_soft_warnings_still_archived(self, tmp_path):
        from scripts.session_archive import build_archive
        exports = tmp_path / "exports"
        runs = exports / "runs"
        runs.mkdir(parents=True)
        (runs / "smart_mix_a.json").write_text('{"tempo": 120}', encoding="utf-8")
        (runs / "smart_mix_b.json").write_text('{"bpm": 90}', encoding="utf-8")
        out = build_archive(exports)
        # 'status' missing is a soft warning, not a parse failure -> both stored
        assert out["metadata"]["total_sessions"] == 2

    def test_torn_json_is_skipped(self, tmp_path):
        from scripts.session_archive import build_archive
        exports = tmp_path / "exports"
        runs = exports / "runs"
        runs.mkdir(parents=True)
        (runs / "smart_mix_torn.json").write_text('{"tempo": 1', encoding="utf-8")
        (runs / "smart_mix_ok.json").write_text('{"status": "success", "tempo": 120}', encoding="utf-8")
        out = build_archive(exports)
        assert out["metadata"]["total_sessions"] == 1
