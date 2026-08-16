#!/usr/bin/env python3
"""Session archive builder: normalizes mix/run JSON artifacts into sessions.yaml.

Analogous to music-research's papers.yaml pipeline — reads raw run artifacts from
exports/runs/ (10min_mix_*.json, smart_mix_*.json, genre_mix_*.json), validates
and normalizes them into a unified schema, and writes exports/archive/sessions.yaml.

Usage:
    python scripts/session_archive.py [EXPORTS_DIR]

If EXPORTS_DIR is omitted, defaults to ./exports.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PATTERNS = [
    r"^10min_mix_.*\.json$",
    r"^smart_mix_.*\.json$",
    r"^genre_mix_.*\.json$",
]

COMPILED_PATTERNS = [re.compile(p) for p in PATTERNS]

KNOWN_GENRES = {
    "dub", "dub_techno", "dub-techno",
    "techno", "house", "deep_house",
    "hip-hop", "hip_hop", "hiphop",
    "dnb", "drum_and_bass", "drum-and-bass",
    "ambient", "reggae", "trip-hop",
}

ALL_GENRES = sorted(KNOWN_GENRES)

SECTION_TYPES = {
    "intro", "verse", "build", "drop", "breakdown", "outro", "finale", "bridge",
}

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

_TIMESTAMP_RE = re.compile(
    r"(\d{4})(\d{2})(\d{2})_?(\d{2})(\d{2})(\d{2})"
)


def _parse_timestamp_from_filename(stem: str) -> str | None:
    """Extract ISO-8601 timestamp from filename stem like '10min_mix_20260728_002030'."""
    match = _TIMESTAMP_RE.search(stem)
    if not match:
        return None
    year, month, day, hour, minute, second = match.groups()
    try:
        dt = datetime(int(year), int(month), int(day),
                       int(hour), int(minute), int(second))
        return dt.isoformat()
    except ValueError:
        return None


def _detect_source(filename: str) -> str:
    """Return the generator type: '10min_mix', 'smart_mix', or 'genre_mix'."""
    if filename.startswith("10min_mix_"):
        return "10min_mix"
    if filename.startswith("smart_mix_"):
        return "smart_mix"
    if filename.startswith("genre_mix_"):
        return "genre_mix"
    return "unknown"


def _detect_genre(data: dict[str, Any], filename: str) -> str:
    """Detect or infer genre from the JSON data or filename."""
    # Explicit genre field (genre_mix files)
    if "genre" in data:
        g = data["genre"].strip().lower().replace(" ", "_")
        return g

    # Check structure descriptions for genre keywords
    descriptions = []
    for section in data.get("structure", []):
        desc = section.get("description", "").lower()
        descriptions.append(desc)
    all_desc = " ".join(descriptions)

    genre_keywords = {
        "dub": ["dub"],
        "techno": ["techno"],
        "house": ["house"],
        "hip-hop": ["hip.hop", "hip hop"],
        "dnb": ["dnb", "drum and bass", "drum & bass"],
        "ambient": ["ambient"],
        "reggae": ["reggae"],
    }

    for genre, keywords in genre_keywords.items():
        for kw in keywords:
            if kw in all_desc:
                return genre

    # Check filename for genre hint
    fn_lower = filename.lower()
    for genre in ALL_GENRES:
        if genre.replace("_", "-") in fn_lower or genre.replace("-", "_") in fn_lower:
            return genre

    return "unknown"


def _extract_tools(data: dict[str, Any]) -> list[str]:
    """Detect which processing tools were used."""
    tools = []
    if "dub_result" in data:
        tools.append("dub")
    if "fat_result" in data:
        tools.append("fat_beatz")
    if "capture_result" in data:
        tools.append("arrangement_capture")
    if "processing" in data:
        tools.append("genre_processing")
    if "polish_score" in data or "polish_result" in data:
        tools.append("polish")
    return sorted(tools)


def _compute_tempo(data: dict[str, Any]) -> dict[str, float | None]:
    """Extract tempo information from the session data."""
    structure = data.get("structure", [])
    if not structure:
        return {"min": None, "max": None, "base": None}

    bpms = [s["bpm"] for s in structure if "bpm" in s]
    if not bpms:
        return {"min": None, "max": None, "base": None}

    base = data.get("base_bpm")
    if base is None:
        base = bpms[0]

    return {
        "min": round(min(bpms), 1),
        "max": round(max(bpms), 1),
        "base": round(float(base), 1),
    }


def _compute_energy(data: dict[str, Any]) -> dict[str, float | None]:
    """Extract energy statistics from section data."""
    structure = data.get("structure", [])
    if not structure:
        return {"min": None, "max": None, "avg": None}

    energies = [s["energy"] for s in structure if "energy" in s]
    if not energies:
        return {"min": None, "max": None, "avg": None}

    return {
        "min": round(min(energies), 2),
        "max": round(max(energies), 2),
        "avg": round(sum(energies) / len(energies), 2),
    }


def _compute_duration(data: dict[str, Any], structure: list[dict]) -> dict[str, float | int | None]:
    """Extract or compute duration information."""
    # Explicit fields
    if "total_time_minutes" in data:
        return {
            "total_bars": data.get("total_bars"),
            "total_bars_computed": sum(s.get("bars", 0) for s in structure),
            "duration_minutes": data["total_time_minutes"],
        }
    if "duration_minutes" in data:
        return {
            "total_bars": data.get("total_bars"),
            "total_bars_computed": sum(s.get("bars", 0) for s in structure),
            "duration_minutes": data["duration_minutes"],
        }

    total_bars = sum(s.get("bars", 0) for s in structure)
    duration_minutes = None
    if total_bars > 0:
        # Estimate duration from first section's BPM
        bpm = structure[0].get("bpm", 120) if structure else 120
        # 4 beats per bar, duration in minutes = bars / (bpm * 4 / 60) = bars * 60 / (bpm * 4)
        duration_minutes = round(total_bars * 60.0 / (bpm * 4.0), 1) if bpm > 0 else None

    return {
        "total_bars": total_bars,
        "total_bars_computed": total_bars,
        "duration_minutes": duration_minutes,
    }


def _extract_sections(data: dict[str, Any]) -> list[dict]:
    """Extract section type distribution."""
    structure = data.get("structure", [])
    return [s.get("section_type", "unknown") for s in structure]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_session(data: dict[str, Any], filename: str) -> list[str]:
    """Validate a raw session JSON. Returns a list of error strings (empty = valid)."""
    errors = []

    if not isinstance(data, dict):
        errors.append(f"{filename}: not a JSON object")
        return errors

    if data.get("status") != "success":
        errors.append(f"{filename}: status is '{data.get('status')}' (expected 'success')")

    structure = data.get("structure", [])
    if not isinstance(structure, list):
        errors.append(f"{filename}: 'structure' is not a list")
    elif len(structure) == 0:
        errors.append(f"{filename}: 'structure' is empty")

    for i, section in enumerate(structure):
        if not isinstance(section, dict):
            errors.append(f"{filename}: structure[{i}] is not an object")
            continue
        for field in ("name", "section_type", "bars", "bpm", "energy"):
            if field not in section:
                errors.append(f"{filename}: structure[{i}].{field} missing")
        if section.get("energy") is not None:
            e = section["energy"]
            if not isinstance(e, (int, float)) or e < 0 or e > 1:
                errors.append(f"{filename}: structure[{i}].energy out of range [0,1]: {e}")
        if section.get("bars") is not None:
            b = section["bars"]
            if not isinstance(b, (int, float)) or b <= 0:
                errors.append(f"{filename}: structure[{i}].bars must be positive: {b}")

    return errors


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize_session(data: dict[str, Any], filename: str) -> dict[str, Any]:
    """Normalize a raw session JSON into the unified archive schema."""
    structure = data.get("structure", [])
    source = _detect_source(filename)
    stem = Path(filename).stem
    timestamp = _parse_timestamp_from_filename(stem)

    tempo = _compute_tempo(data)
    energy = _compute_energy(data)
    duration = _compute_duration(data, structure)
    sections = _extract_sections(data)
    tools = _extract_tools(data)
    genre = _detect_genre(data, filename)

    return {
        "id": stem,
        "source": source,
        "genre": genre,
        "key": None,  # Not available in current data formats
        "tempo": tempo,
        "tracks": data.get("num_tracks"),
        "duration": duration,
        "energy": energy,
        "sections": sections,
        "num_sections": len(sections),
        "tools_used": tools,
        "timestamp": timestamp,
        "processing": data.get("processing"),
        "mood": data.get("mood"),
        "scenes_used": data.get("scenes_used"),
        "elapsed_time": data.get("elapsed_time"),
    }


# ---------------------------------------------------------------------------
# Scanning & archive building
# ---------------------------------------------------------------------------

def scan_runs_dir(runs_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Scan exports/runs/ for matching JSON files and parse them."""
    results = []
    if not runs_dir.is_dir():
        return results

    for json_file in sorted(runs_dir.glob("*.json")):
        if not any(p.match(json_file.name) for p in COMPILED_PATTERNS):
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            results.append((json_file, data))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARN: skipping {json_file.name}: {exc}", file=sys.stderr)
    return results


def build_archive(exports_dir: Path) -> dict[str, Any]:
    """Build the full session archive from the exports directory."""
    runs_dir = exports_dir / "runs"
    archive_dir = exports_dir / "archive"
    sessions_file = archive_dir / "sessions.yaml"

    files = scan_runs_dir(runs_dir)

    sessions = []
    all_errors = []

    for json_path, data in files:
        errors = validate_session(data, json_path.name)
        all_errors.extend(errors)
        # Archive even files with soft warnings (non-status errors), but skip hard parse failures
        if errors and any("not a JSON object" in e for e in errors):
            print(f"WARN: skipping {json_path.name} due to validation errors", file=sys.stderr)
            continue
        session = normalize_session(data, json_path.name)
        sessions.append(session)

    archive = {"sessions": sessions, "metadata": {
        "total_sessions": len(sessions),
        "scanned_files": len(files),
        "validation_errors": all_errors,
    }}

    archive_dir.mkdir(parents=True, exist_ok=True)
    sessions_file.write_text(
        yaml.dump(archive, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    print(f"Archived {len(sessions)} sessions -> {sessions_file}")
    if all_errors:
        print(f"  {len(all_errors)} validation warning(s)", file=sys.stderr)
    for err in all_errors:
        print(f"  ⚠ {err}", file=sys.stderr)

    return archive


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    exports_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("exports")
    exports_dir = Path(exports_dir).resolve()

    if not exports_dir.is_dir():
        print(f"ERROR: {exports_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    build_archive(exports_dir)


if __name__ == "__main__":
    main()
