#!/usr/bin/env python3
"""Session statistics aggregator: sessions.yaml → statistics.json.

Analogous to music-research's standard_stats.py — reads the normalized session
archive (exports/archive/sessions.yaml) and aggregates into structured
statistics covering genre distribution, tempo ranges, tool usage, energy
profiles, section analysis, and gap detection.

Usage:
    python scripts/session_stats.py [EXPORTS_DIR]

If EXPORTS_DIR is omitted, defaults to ./exports.
Exits 0 on success (even with an empty archive).
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def _tempo_bucket(bpm: float | None) -> str:
    """Classify a BPM into a human-readable bucket."""
    if bpm is None:
        return "unknown"
    if bpm < 70:
        return "<70"
    if bpm < 80:
        return "70-79"
    if bpm < 90:
        return "80-89"
    if bpm < 100:
        return "90-99"
    if bpm < 110:
        return "100-109"
    if bpm < 120:
        return "110-119"
    if bpm < 140:
        return "120-139"
    return "140+"


def _energy_bucket(e: float | None) -> str:
    """Classify energy into descriptive bucket."""
    if e is None:
        return "unknown"
    if e < 0.25:
        return "ambient"
    if e < 0.5:
        return "low"
    if e < 0.75:
        return "medium"
    return "high"


def load_archive(exports_dir: Path) -> dict[str, Any]:
    """Load the sessions.yaml archive. Returns empty dict if not found."""
    archive_path = exports_dir / "archive" / "sessions.yaml"
    if not archive_path.is_file():
        return {"sessions": [], "metadata": {"total_sessions": 0, "scanned_files": 0, "validation_errors": []}}
    with open(archive_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"sessions": [], "metadata": {"total_sessions": 0, "scanned_files": 0, "validation_errors": []}}


def generate_stats(archive: dict[str, Any]) -> dict[str, Any]:
    """Generate aggregated statistics from the session archive."""
    sessions = archive.get("sessions", [])
    total = len(sessions)

    if total == 0:
        empty_stats = {
            "metadata": {
                "total_sessions": 0,
                "generated_date": datetime.now().isoformat(),
                "note": "Empty archive — no sessions to analyze",
            },
            "by_genre": {},
            "by_source": {},
            "by_tempo_bucket": {},
            "by_energy_bucket": {},
            "by_section_type": {},
            "by_tool": {},
            "tempo_stats": {"min": None, "max": None, "avg": None},
            "energy_stats": {"min": None, "max": None, "avg": None},
            "duration_stats": {"min_minutes": None, "max_minutes": None, "avg_minutes": None},
            "section_type_counts": {},
            "tracks_used": {},
            "mood_distribution": {},
            "timeline": [],
            "gaps": {
                "missing_genres": sorted(
                    g for g in ["dub", "techno", "house", "hip-hop", "dnb", "ambient", "reggae"]
                ),
                "missing_keys": ["all"],
                "tempo_range_gaps": [],
                "underrepresented_tools": [],
            },
        }
        return empty_stats

    # --- Counters ---
    genre_counter = Counter()
    source_counter = Counter()
    tempo_base_counter = Counter()
    tempo_bucket_counter = Counter()
    energy_bucket_counter = Counter()
    section_counter = Counter()
    tool_counter = Counter()
    mood_counter = Counter()
    tracks_counter = Counter()

    # --- Tempo / energy aggregates ---
    base_tempos = []
    all_tempos = []  # includes min and max from each session
    energy_avgs = []
    durations = []

    # --- Timeline ---
    timeline_entries = []

    # --- Per-genre tempo data ---
    genre_tempos: dict[str, list[float]] = defaultdict(list)

    ALL_KNOWN_GENRES = ["dub", "techno", "house", "hip-hop", "dnb", "ambient", "reggae"]

    for session in sessions:
        # Source
        source = session.get("source", "unknown")
        source_counter[source] += 1

        # Genre
        genre = session.get("genre", "unknown")
        genre_counter[genre] += 1

        # Tempo
        tempo = session.get("tempo", {})
        base_bpm = tempo.get("base") if isinstance(tempo, dict) else None
        min_bpm = tempo.get("min") if isinstance(tempo, dict) else None
        max_bpm = tempo.get("max") if isinstance(tempo, dict) else None

        if base_bpm is not None:
            base_tempos.append(base_bpm)
            genre_tempos[genre].append(base_bpm)
            tempo_bucket_counter[_tempo_bucket(base_bpm)] += 1

        if min_bpm is not None:
            for b in [min_bpm, max_bpm]:
                if b is not None:
                    all_tempos.append(b)
                    tempo_bucket_counter[_tempo_bucket(b)] += 1

        # Energy
        energy = session.get("energy", {})
        e_avg = energy.get("avg") if isinstance(energy, dict) else None
        if e_avg is not None:
            energy_avgs.append(e_avg)
            energy_bucket_counter[_energy_bucket(e_avg)] += 1

        # Sections
        for sec_type in session.get("sections", []):
            section_counter[sec_type] += 1

        # Tools
        for tool in session.get("tools_used", []):
            tool_counter[tool] += 1

        # Mood
        mood = session.get("mood")
        if mood:
            mood_counter[mood] += 1

        # Tracks
        n_tracks = session.get("tracks")
        if n_tracks is not None:
            tracks_counter[n_tracks] += 1

        # Duration
        dur_info = session.get("duration", {})
        if isinstance(dur_info, dict) and dur_info.get("duration_minutes") is not None:
            durations.append(dur_info["duration_minutes"])

        # Timeline
        ts = session.get("timestamp")
        if ts:
            timeline_entries.append({
                "id": session.get("id"),
                "source": source,
                "genre": genre,
                "timestamp": ts,
            })

    # --- Compute aggregates ---
    tempo_stats = {}
    if all_tempos:
        tempo_stats = {
            "min": round(min(all_tempos), 1),
            "max": round(max(all_tempos), 1),
            "avg": round(sum(base_tempos) / len(base_tempos), 1) if base_tempos else None,
            "median": round(sorted(base_tempos)[len(base_tempos) // 2], 1) if base_tempos else None,
        }

    energy_stats = {}
    if energy_avgs:
        energy_stats = {
            "min": round(min(energy_avgs), 2),
            "max": round(max(energy_avgs), 2),
            "avg": round(sum(energy_avgs) / len(energy_avgs), 2),
        }

    duration_stats = {}
    if durations:
        duration_stats = {
            "min_minutes": round(min(durations), 1),
            "max_minutes": round(max(durations), 1),
            "avg_minutes": round(sum(durations) / len(durations), 1),
        }

    # --- By-genre tempo breakdown ---
    by_genre_tempos = {}
    for genre, tempos in sorted(genre_tempos.items()):
        by_genre_tempos[genre] = {
            "count": len(tempos),
            "min": round(min(tempos), 1),
            "max": round(max(tempos), 1),
            "avg": round(sum(tempos) / len(tempos), 1),
        }

    # --- Gaps ---
    observed_genres = set(genre_counter.keys())
    missing_genres = sorted(g for g in ALL_KNOWN_GENRES if g not in observed_genres)

    # Tempo range gaps: buckets not covered by any session
    all_tempo_buckets = ["<70", "70-79", "80-89", "90-99", "100-109", "110-119", "120-139", "140+"]
    covered_tempo_buckets = set(tempo_bucket_counter.keys())
    tempo_range_gaps = [b for b in all_tempo_buckets if b not in covered_tempo_buckets]

    # Underrepresented tools (tools never used)
    all_known_tools = [
        "dub", "fat_beatz", "arrangement_capture",
        "genre_processing", "polish",
    ]
    underrepresented_tools = sorted(t for t in all_known_tools if tool_counter.get(t, 0) == 0)

    stats = {
        "metadata": {
            "total_sessions": total,
            "generated_date": datetime.now().isoformat(),
            "generators_used": dict(source_counter),
        },
        "by_genre": dict(sorted(genre_counter.items(), key=lambda x: -x[1])),
        "by_source": dict(sorted(source_counter.items(), key=lambda x: -x[1])),
        "by_tempo_bucket": dict(sorted(tempo_bucket_counter.items())),
        "by_energy_bucket": dict(sorted(energy_bucket_counter.items())),
        "by_section_type": dict(sorted(section_counter.items(), key=lambda x: -x[1])),
        "by_tool": dict(sorted(tool_counter.items(), key=lambda x: -x[1])),
        "tempo_stats": tempo_stats,
        "energy_stats": energy_stats,
        "duration_stats": duration_stats,
        "by_genre_tempo": by_genre_tempos,
        "section_type_counts": dict(sorted(section_counter.items(), key=lambda x: -x[1])),
        "tracks_used": dict(sorted(tracks_counter.items())),
        "mood_distribution": dict(sorted(mood_counter.items(), key=lambda x: -x[1])),
        "timeline": sorted(timeline_entries, key=lambda x: x.get("timestamp", "")),
        "gaps": {
            "missing_genres": missing_genres,
            "missing_keys": ["all"],  # Key detection not yet available
            "tempo_range_gaps": tempo_range_gaps,
            "underrepresented_tools": underrepresented_tools,
        },
    }

    return stats


def main():
    exports_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("exports")
    exports_dir = Path(exports_dir).resolve()

    if not exports_dir.is_dir():
        print(f"ERROR: {exports_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    archive = load_archive(exports_dir)
    stats = generate_stats(archive)

    # Write statistics.json
    archive_dir = exports_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stats_path = archive_dir / "statistics.json"

    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"Wrote {stats_path} ({stats['metadata']['total_sessions']} sessions)")
    if stats["metadata"]["total_sessions"] == 0:
        print("NOTE: Empty archive — statistics file created with zero counts")
    else:
        print(f"  Genres: {len(stats['by_genre'])} distinct")
        print(f"  Tempo range: {stats['tempo_stats']}")
        print(f"  Tools used: {stats['by_tool']}")

    sys.exit(0)


if __name__ == "__main__":
    main()
