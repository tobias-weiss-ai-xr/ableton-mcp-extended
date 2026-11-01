#!/usr/bin/env python
"""Write 3 x 16-bar dub techno percussion clips onto a 64-Pad-Kit track.

Slow dub techno at session tempo: 4-on-the-floor kick, offbeat hats, sparse
rim/clap, dub dropouts. Patterns evolve every 4 bars so a 16-bar clip has an
arc instead of 16 identical bars.

Two sets: ``full`` (with kick) for the main kit track, ``tops`` (hats/perc, no
kick) for a second kit track playing alongside it.

    python scripts/fill_dub_techno_percussion.py                 # autodetect *Pad Kit*
    python scripts/fill_dub_techno_percussion.py --track 1 --start-slot 1
    python scripts/fill_dub_techno_percussion.py --track 2 --set tops
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp_client import MCPClientTCP  # noqa: E402
from fill_64pad_percussion import (  # noqa: E402  shared 64-Pad map
    CH, CLAP, KICK, OH, RIM, SHK, SNARE, TOM1, TOM2,
)

CLIP_LEN = 64.0
BARS = 16
VEL = {KICK: 100, SNARE: 86, CLAP: 82, CH: 64, OH: 76,
       RIM: 62, SHK: 50, TOM1: 80, TOM2: 78}
DUR = {KICK: 0.25, CH: 0.12, SHK: 0.10, OH: 0.30}


def _offbeats():
    return [0.5, 1.5, 2.5, 3.5]


def _sixteenths():
    return [b / 4.0 for b in range(0, 16, 1)]


# Each pattern: 4 sections (bars 0-3, 4-7, 8-11, 12-15).
# Positions are beats within the bar (0.0-3.75).
# "full" carries the kick; "tops" is the complementary hat/perc layer for a second
# kit track playing at the same time (no kick, so the low end is not doubled).
PATTERN_SETS = {
    "full": {
        "01 four-on-floor": [
            {KICK: [0, 1, 2, 3], CH: _offbeats()},
            {KICK: [0, 1, 2, 3], CH: _offbeats(), RIM: [1.5, 3.5]},
            {KICK: [0, 1, 2, 3], CH: _offbeats(), RIM: [1.5, 3.5], CLAP: [2.0]},
            {KICK: [0, 1, 2, 3], CH: _offbeats(), RIM: [1.5, 3.5], CLAP: [2.0],
             SHK: _sixteenths()},
        ],
        "02 half-time": [
            {KICK: [0, 2.5], CH: _offbeats()},
            {KICK: [0, 2.5], CH: _offbeats(), RIM: [2.0]},
            {KICK: [0, 2.5], CH: _offbeats(), RIM: [2.0], OH: [3.5]},
            {KICK: [0, 2.5], CH: _offbeats(), RIM: [2.0], OH: [3.5], SNARE: [2.0],
             SHK: [b / 2.0 for b in range(8)]},
        ],
        "03 dub dropout": [
            {KICK: [0, 1, 2, 3], CH: _offbeats()},
            {KICK: [0, 1, 2, 3], CH: _offbeats(), SHK: _sixteenths()},
            {KICK: [0, 1, 2, 3], CH: _offbeats(), SHK: _sixteenths(), CLAP: [2.0]},
            {KICK: [0, 1, 2, 3], CH: _offbeats(), RIM: [3.5], CLAP: [2.0]},
        ],
    },
    "tops": {
        "01 hats-rim": [
            {CH: _offbeats()},
            {CH: _offbeats(), RIM: [1.5, 3.5]},
            {CH: _offbeats(), RIM: [1.5, 3.5], OH: [1.5]},
            {CH: _offbeats(), RIM: [1.5, 3.5], OH: [1.5, 3.5], SHK: _sixteenths()},
        ],
        "02 shaker-swerve": [
            {SHK: _sixteenths()},
            {SHK: _sixteenths(), CH: _offbeats()},
            {SHK: _sixteenths(), CH: _offbeats(), RIM: [3.5]},
            {SHK: _sixteenths(), CH: _offbeats(), RIM: [3.5], CLAP: [2.0]},
        ],
        "03 perc-accents": [
            {CH: _offbeats(), RIM: [1.5]},
            {CH: _offbeats(), RIM: [1.5, 3.5], OH: [3.5]},
            {CH: _offbeats(), RIM: [1.5, 3.5], OH: [3.5], CLAP: [2.0]},
            {CH: _offbeats(), RIM: [1.5, 3.5], OH: [3.5], CLAP: [2.0],
             SHK: _sixteenths()},
        ],
    },
}

# Bars that thin out or fill, applied on top of the section layer.
DROP_BARS = {8: [0, 2], 9: [0]}       # dub dropout: kick thins to half/one
FILL_BAR = 15


def bar_layers(bar, sections):
    """Pitch -> beat positions for one bar, including drops and the closing fill."""
    beat_map = sections[min(bar // 4, 3)]
    layers = {p: list(pos) for p, pos in beat_map.items() if pos}
    has_kick = KICK in layers

    if bar in DROP_BARS and has_kick:
        layers[KICK] = DROP_BARS[bar]
        for p in (RIM, CLAP, SHK, SNARE):
            layers.pop(p, None)

    if bar == FILL_BAR:
        if has_kick:
            layers[KICK] = [0, 1, 2]
        layers[CH] = _offbeats()[:3]
        layers[TOM1] = [3.0, 3.5]
        layers[TOM2] = [3.25]
    return layers


def build_clip(sections):
    notes = []
    for bar in range(BARS):
        for pitch, positions in bar_layers(bar, sections).items():
            for i, pos in enumerate(positions):
                t = bar * 4.0 + pos
                if t >= CLIP_LEN:
                    continue
                swing = 1 if (pitch in (CH, SHK) and i % 2) else 0
                notes.append({
                    "pitch": pitch,
                    "start_time": round(t, 3),
                    "duration": DUR.get(pitch, 0.20),
                    "velocity": VEL.get(pitch, 72) + swing - (bar % 3),
                    "mute": False,
                })
    return notes


def resolve_track(client, track_arg, marker):
    if track_arg is not None:
        return track_arg
    tracks = client.send_command("get_all_tracks", {})["result"]["tracks"]
    for t in tracks:
        if marker.lower() in (t.get("name") or "").lower():
            return t["index"]
    sys.exit("No track matching {!r}. Tracks: {}".format(
        marker, [(t["index"], t.get("name")) for t in tracks]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--track", type=int,
                    help="track index (default: first track named *Pad Kit*)")
    ap.add_argument("--start-slot", type=int, default=1,
                    help="first clip slot to write (default 1, leaves slot 0 alone)")
    ap.add_argument("--set", choices=sorted(PATTERN_SETS), default="full",
                    help="full = with kick; tops = hat/perc layer for a second kit track")
    args = ap.parse_args()

    patterns = PATTERN_SETS[args.set]
    client = MCPClientTCP()
    track = resolve_track(client, args.track, "Pad Kit")
    print("writing {} dub techno clips (set: {}) on track {}".format(
        len(patterns), args.set, track))

    existing = {c["index"] for c in client.send_command(
        "get_all_clips_in_track", {"track_index": track})["result"]["clips"]}

    for offset, (name, sections) in enumerate(patterns.items()):
        slot = args.start_slot + offset
        notes = build_clip(sections)
        expects_kick = any(KICK in layer for layer in sections)
        if slot in existing:
            client.send_command("delete_clip",
                                {"track_index": track, "clip_index": slot})
        client.send_command("create_clip",
                            {"track_index": track, "clip_index": slot,
                             "length": CLIP_LEN})
        client.send_command("add_notes_to_clip",
                            {"track_index": track, "clip_index": slot,
                             "notes": notes})
        client.send_command("set_clip_name",
                            {"track_index": track, "clip_index": slot,
                             "name": "Dub Techno Perc 16bar {}".format(name)})

        got = client.send_command("get_clip_notes",
                                  {"track_index": track,
                                   "clip_index": slot})["result"]["notes"]
        assert len(got) == len(notes), "slot {}: wrote {} notes, read back {}".format(
            slot, len(notes), len(got))
        per_bar = defaultdict(set)
        for n in got:
            per_bar[int(n["start_time"] // 4)].add(n["pitch"])
        assert len(per_bar) == BARS, "slot {}: {} bars of {}".format(
            slot, len(per_bar), BARS)
        if expects_kick:
            assert all(KICK in v for v in per_bar.values()), \
                "slot {}: a bar has no kick".format(slot)
        else:
            assert KICK not in {n["pitch"] for n in got}, \
                "slot {}: tops set must not contain a kick".format(slot)
        print("  slot {} [{}] {:3d} hits, {} bars, pitches {}".format(
            slot, name, len(got), len(per_bar), sorted({n["pitch"] for n in got})))

    print("\nOK - {} clips on track {}".format(len(patterns), track))


if __name__ == "__main__":
    main()
