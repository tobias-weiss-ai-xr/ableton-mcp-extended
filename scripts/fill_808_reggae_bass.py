#!/usr/bin/env python
"""Fill 10 x 16-bar reggae/dub bassline clips on a MIDI track (Bb minor pentatonic).

Creates each clip when missing and rewrites its notes, so re-running is safe.

    python scripts/fill_808_reggae_bass.py            # track named *808*
    python scripts/fill_808_reggae_bass.py --track 1
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_client import MCPClientTCP  # noqa: E402

CLIP_LEN = 64.0  # 16 bars
BB1, GB1, AB1 = 34, 30, 32
DB2, F2, AB2, BB2 = 37, 41, 44, 46

# cells: (pitch, start_in_bar, duration, velocity)
CELLS = {
    "foundation": [(BB1, 0.0, 1.5, 92), (BB1, 2.5, 0.75, 78), (F2, 3.5, 0.5, 84)],
    "skank":      [(BB1, 0.5, 0.5, 80), (BB1, 1.5, 0.5, 88), (F2, 2.5, 0.5, 80),
                   (AB1, 3.0, 0.5, 76), (BB1, 3.5, 0.5, 88)],
    "dub_sparse": [(BB1, 0.0, 2.0, 90), (BB1, 3.5, 0.5, 80)],
    "octave_pop": [(BB1, 0.0, 1.0, 90), (BB2, 1.5, 0.25, 96), (BB1, 2.0, 0.5, 78),
                   (F2, 3.0, 0.5, 84), (BB1, 3.5, 0.5, 88)],
    "walk":       [(BB1, 0.0, 1.0, 88), (BB1, 1.5, 0.5, 76), (DB2, 2.0, 0.5, 80),
                   (F2, 2.5, 0.5, 84), (AB2, 3.0, 0.5, 80), (F2, 3.5, 0.5, 86)],
    "steppers":   [(BB1, 0.0, 0.75, 90), (BB1, 1.0, 0.75, 84), (BB1, 2.0, 0.75, 84),
                   (BB1, 3.0, 0.5, 80), (AB2, 3.5, 0.5, 86)],
    "fill":       [(BB1, 0.0, 1.5, 92), (F2, 2.0, 0.5, 82), (BB2, 2.5, 0.25, 96),
                   (AB2, 3.0, 0.25, 90), (F2, 3.5, 0.5, 86)],
    "deep_drop":  [(BB1, 0.0, 3.5, 94)],
}

# per clip: (base cell, alt cell, use dropouts)
CLIPS = [
    ("foundation", "foundation", False),
    ("skank", "foundation", False),
    ("dub_sparse", "foundation", False),
    ("octave_pop", "foundation", False),
    ("walk", "foundation", False),
    ("steppers", "skank", False),
    ("foundation", "dub_sparse", True),
    ("skank", "octave_pop", True),
    ("octave_pop", "walk", True),
    ("steppers", "walk", True),
]


def build_clip_notes(base, alt, use_dropout):
    notes = []
    for bar in range(16):
        if use_dropout and bar in (7, 10):
            cell = CELLS["deep_drop"] if bar == 7 else []
        elif bar in (7, 15):
            cell = CELLS["fill"]
        elif bar % 8 in (4, 5, 6):
            cell = CELLS[alt]
        else:
            cell = CELLS[base]
        for pitch, start, dur, vel in cell:
            g = bar * 4.0 + start
            if g >= CLIP_LEN:
                continue
            dur = min(dur, CLIP_LEN - g)  # prune tail overflow
            notes.append({"pitch": pitch, "start_time": round(g, 3),
                          "duration": round(dur, 3), "velocity": vel, "mute": False})
    return notes


def resolve_track(client, track_arg, marker):
    if track_arg is not None:
        return track_arg
    tracks = client.send_command("get_all_tracks", {})["result"]["tracks"]
    for t in tracks:
        if marker.lower() in (t.get("name") or "").lower():
            return t["index"]
    sys.exit("No track matching {!r}. Tracks: {}".format(
        marker, [(t["index"], t["name"]) for t in tracks]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--track", type=int, help="track index (default: first track named *808*)")
    args = ap.parse_args()

    client = MCPClientTCP()
    track = resolve_track(client, args.track, "808")
    print("filling 10 reggae bass clips on track {}".format(track))

    for slot, (base, alt, drop) in enumerate(CLIPS):
        notes = build_clip_notes(base, alt, drop)
        existing = {c["index"] for c in client.send_command(
            "get_all_clips_in_track", {"track_index": track})["result"]["clips"]}
        if slot not in existing:
            client.send_command("create_clip",
                                {"track_index": track, "clip_index": slot,
                                 "length": CLIP_LEN})
        r = client.send_command("add_notes_to_clip",
                                {"track_index": track, "clip_index": slot, "notes": notes})
        if r.get("status") != "success":
            sys.exit("clip {} failed: {}".format(slot, r))

        got = client.send_command("get_clip_notes",
                                  {"track_index": track, "clip_index": slot})["result"]["notes"]
        assert len(got) == len(notes), "clip {}: readback {} != {}".format(
            slot, len(got), len(notes))
        print("  clip {:02d} [{}/{}{}] {:3d} notes".format(
            slot + 1, base, alt, "/dropout" if drop else "", len(got)))

    print("\nOK - 10 clips on track {}".format(track))


if __name__ == "__main__":
    main()
