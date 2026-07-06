"""
Tests for MCP_Server/als_parser.py — Ableton Live Set (.als) file parser.

Tests the parsing logic (tracks, devices, clips, tempo, time signature, etc.),
issue detection, and suggestion generation.
"""

import json
import os
import gzip
import xml.etree.ElementTree as ET
from unittest.mock import patch

import pytest

from MCP_Server.als_parser import (
    parse_als_file,
    detect_als_issues,
    suggest_als_changes,
)

# ── Fixtures (using the .als files created in the sprint setup) ─────────────


@pytest.fixture
def minimal_als_path():
    return "tests/fixtures/minimal.als"


@pytest.fixture
def three_tracks_als_path():
    return "tests/fixtures/three_tracks.als"


@pytest.fixture
def empty_als_path(tmp_path):
    path = tmp_path / "empty.als"
    root = ET.Element('Ableton', MajorVersion='5', MinorVersion='0')
    ET.SubElement(root, 'LiveSet') # Need at least LiveSet
    data = ET.tostring(root, encoding='unicode')
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        f.write(data)
    return str(path)


@pytest.fixture
def corrupted_als_path(tmp_path):
    path = tmp_path / "corrupted.als"
    with open(path, "wb") as f:
        f.write(b"corrupted data")
    return str(path)


# ── Test 1: parse_als_file(minimal.als) returns dict ────────────────────────


def test_parse_minimal_als_returns_dict(minimal_als_path):
    data = parse_als_file(minimal_als_path)
    assert isinstance(data, dict)
    assert "tracks" in data
    assert "tempo" in data
    assert "time_signature" in data


def test_parse_minimal_als_track_count(minimal_als_path):
    data = parse_als_file(minimal_als_path)
    assert len(data["tracks"]) == 1
    assert data["tracks"][0]["name"] == "Test Track"


def test_parse_minimal_als_tempo_time_signature(minimal_als_path):
    data = parse_als_file(minimal_als_path)
    assert data["tempo"] == 120.0
    assert data["time_signature"] == {"numerator": 4, "denominator": 4}


# ── Test 2: parse_als_file(three_tracks.als) returns 3 tracks ───────────────


def test_parse_three_tracks_als(three_tracks_als_path):
    data = parse_als_file(three_tracks_als_path)
    assert len(data["tracks"]) == 2  # MidiTrack + AudioTrack
    assert len(data["return_tracks"]) == 1  # ReturnTrack
    assert data["tracks"][0]["name"] == "Synth"
    assert data["tracks"][1]["name"] == "Vocals"
    assert data["return_tracks"][0]["name"] == "Reverb"


# ── Test 3: detect_als_issues() finds empty tracks in fixture ───────────────


def test_detect_issues_empty_track(empty_als_path):
    data = parse_als_file(empty_als_path)
    issues = detect_als_issues(data)
    assert any(i["type"] == "no_devices" for i in issues)
    assert any(i["type"] == "naming" for i in issues)


# ── Test 4: suggest_als_changes() returns valid suggestions ─────────────────


def test_suggest_changes_empty_track(empty_als_path):
    data = parse_als_file(empty_als_path)
    suggestions = suggest_als_changes(data)
    assert any("Delete empty track" in s["message"] for s in suggestions)


# ── Test 5: Parse error on invalid file (not .als) ──────────────────────────


def test_parse_error_on_invalid_file(tmp_path):
    invalid_file = tmp_path / "not_als.txt"
    invalid_file.write_text("plain text content")
    with pytest.raises(ValueError, match="Cannot read"):  # It tries gzip and plain text
        parse_als_file(str(invalid_file))


# ── Test 6: Parse error on corrupted gzip ───────────────────────────────────


def test_parse_error_on_corrupted_gzip(corrupted_als_path):
    with pytest.raises(ValueError, match="Cannot read"):  # It tries gzip first
        parse_als_file(corrupted_als_path)


# ── Test 7: Track names extracted correctly from fixture ────────────────────


def test_track_names_extracted_correctly(three_tracks_als_path):
    data = parse_als_file(three_tracks_als_path)
    track_names = [t["name"] for t in data["tracks"]] + [t["name"] for t in data["return_tracks"]]
    assert "Synth" in track_names
    assert "Vocals" in track_names
    assert "Reverb" in track_names


# ── Test 8: Device chain parsed (if present in fixture) ─────────────────────


def test_device_chain_parsed(three_tracks_als_path):
    data = parse_als_file(three_tracks_als_path)
    synth_track = data["tracks"][0]
    assert len(synth_track["devices"]) == 1
    assert synth_track["devices"][0]["name"] == "Wavetable"


# ── Additional: Test empty clip / clips with no notes ───────────────────────


def test_clip_with_no_notes_detected(three_tracks_als_path):
    data = parse_als_file(three_tracks_als_path)
    # Our fixtures currently don't have clips with notes, so they will be detected as empty
    synth_track = data["tracks"][0]
    if synth_track["clips"]:
        for clip in synth_track["clips"]:
            assert not clip["has_notes"]

    issues = detect_als_issues(data)
    assert any(i["type"] == "empty_clip" for i in issues), "Should detect empty clips"


# ── Additional: Test no tracks in file ──────────────────────────────────────


def test_no_tracks_in_file(tmp_path):
    path = tmp_path / "no_tracks.als"
    root = ET.Element('Ableton', MajorVersion='5', MinorVersion='0')
    live_set = ET.SubElement(root, 'LiveSet')
    # No <Tracks> element
    data = ET.tostring(root, encoding='unicode')
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        f.write(data)
    
    parsed_data = parse_als_file(str(path))
    assert len(parsed_data['tracks']) == 0
    issues = detect_als_issues(parsed_data)
    assert any(i['message'] == 'No tracks found in the session.' for i in issues)
