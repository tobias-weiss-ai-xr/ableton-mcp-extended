#!/usr/bin/env python
"""Write 3 x 16-bar dub techno clips onto a 64-Pads kit track, one role per track.

THE INSTRUMENT IS A PAD GRID, NOT A CHROMATIC INSTRUMENT
--------------------------------------------------------
"64 Pads Dub Techno Kit" is an Instrument Rack wrapping a Drum Rack whose 64
chains are Simplers, every one at root key 60 with no transposition. Note N
therefore always plays sample N at its original pitch: the note is an *address*,
not a pitch. Verified against the preset (see scripts/inspect_pad_kit.py):

    notes 29-60  30 x "Chord Dub Chop N"  chops of a dub chord (musical layer)
    notes 61-92  percussion one-shots, listed in PADS below

The same note means something else in every kit - the sibling "64 Pad Kit
Special" puts cymbals where this kit has chord chops - so never assume a
GM-style drum map (36=kick, 42=hat). Read the kit first:

    python scripts/inspect_pad_kit.py --kit ".../64 Pads Dub Techno Kit.adg"

ROLES, one per track (the session loads the same rack three times)
------------------------------------------------------------------
    --set drums  kick, snare/clap, perc accents      (no hats - those are tops)
    --set tops   closed hats, shaker, stick          (no kick, no clap)
    --set chops  chord stabs from the 29-60 slices   (the musical layer)

Keeping the roles disjoint matters: two tracks both playing stick or shaker at
the same beat just doubles it and flams.

    python scripts/fill_dub_techno_percussion.py --track 1 --set drums
    python scripts/fill_dub_techno_percussion.py --track 2 --set tops
    python scripts/fill_dub_techno_percussion.py --track 3 --set chops
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_client import MCPClientTCP  # noqa: E402

CLIP_LEN = 64.0
BARS = 16

# 64 Pads Dub Techno Kit - pad note -> sample. Source of truth:
# scripts/inspect_pad_kit.py (parsed from the .adg, not guessed).
PADS = {
    92: "Kick Dub",
    91: "Snare 606 Dub",
    85: "Snap Impulse Dub",
    90: "Clap Dub Short",
    70: "Clap Dub Long",
    86: "Hihat Closed 808 Dub 1",
    84: "Hihat Closed 808 Dub 2",
    63: "A-Shaker 1",
    61: "Shake-Cabasa Short",
    88: "Perc Metal Tap Dub",
    80: "Stick Dub",
    72: "Tom 808 Mid Dub",
    74: "Tom Lo Dub",
    81: "FX Noise Hit Dub",
    60: "Chord Dub Chop 1",
    48: "Chord Dub Chop 30",
    40: "Chord Dub Chop 3",
    36: "Chord Dub Chop 4",
    32: "Chord Dub Chop 5",
}
KICK, SNARE, SNAP, CLAP = 92, 91, 85, 90
CH, CH2, SHAKER, SHAKER2 = 86, 84, 63, 61
PERC, STICK, TOM, TOM_LO, FX = 88, 80, 72, 74, 81
CHOP_A, CHOP_B, CHOP_C, CHOP_D, CHOP_E = 60, 48, 40, 36, 32

VEL = {KICK: 104, SNARE: 88, SNAP: 58, CLAP: 84, CH: 62, CH2: 56,
       SHAKER: 48, SHAKER2: 52, PERC: 70, STICK: 64, TOM: 82, TOM_LO: 78,
       FX: 60, CHOP_A: 90, CHOP_B: 84, CHOP_C: 86, CHOP_D: 88, CHOP_E: 82}
DUR = {KICK: 0.25, CH: 0.12, CH2: 0.12, SHAKER: 0.10, SHAKER2: 0.12,
       STICK: 0.15, CLAP: 0.20, SNARE: 0.20, TOM: 0.25, TOM_LO: 0.28, FX: 0.50,
       CHOP_A: 0.50, CHOP_B: 0.40, CHOP_C: 0.60, CHOP_D: 0.60, CHOP_E: 0.40}


def _offbeats():
    return [0.5, 1.5, 2.5, 3.5]


def _sixteenths():
    return [b / 4.0 for b in range(16)]


# Each pattern: 4 sections (bars 0-3, 4-7, 8-11, 12-15).
# Positions are beats within the bar (0.0-3.75). Density grows per section so a
# 16-bar clip has an arc instead of 16 identical bars.
PATTERN_SETS = {
    "drums": {
        "01 four-on-floor": [
            {KICK: [0, 1, 2, 3]},
            {KICK: [0, 1, 2, 3], PERC: [1.5]},
            {KICK: [0, 1, 2, 3], PERC: [1.5], CLAP: [2.0]},
            {KICK: [0, 1, 2, 3], PERC: [1.5], CLAP: [2.0], SNAP: [3.75]},
        ],
        "02 half-time": [
            {KICK: [0, 2.5]},
            {KICK: [0, 2.5], SNARE: [2.0]},
            {KICK: [0, 2.5], SNARE: [2.0], PERC: [3.5]},
            {KICK: [0, 2.5], SNARE: [2.0], PERC: [3.5], SNAP: [1.0]},
        ],
        "03 dub dropout": [
            {KICK: [0, 1, 2, 3]},
            {KICK: [0, 1, 2, 3], SNAP: [3.75]},
            {KICK: [0, 1, 2, 3], CLAP: [2.0]},
            {KICK: [0, 1, 2, 3], CLAP: [2.0], PERC: [1.5]},
        ],
        "04 peak": [
            {KICK: [0, 1, 2, 3], CLAP: [2.0]},
            {KICK: [0, 1, 2, 3], CLAP: [2.0], PERC: [1.5]},
            {KICK: [0, 1, 2, 3], CLAP: [2.0], PERC: [1.5], SNAP: [3.75]},
            {KICK: [0, 1, 2, 3], CLAP: [2.0], PERC: [1.5, 3.5], SNAP: [3.75]},
        ],
    },
    "tops": {
        "01 hats-stick": [
            {CH: _offbeats()},
            {CH: _offbeats(), STICK: [1.5, 3.5]},
            {CH: _offbeats(), STICK: [1.5, 3.5], CH2: [1.5]},
            {CH: _offbeats(), STICK: [1.5, 3.5], CH2: [1.5, 3.5],
             SHAKER: _sixteenths()},
        ],
        "02 shaker-swerve": [
            {SHAKER2: _sixteenths()},
            {SHAKER2: _sixteenths(), CH: _offbeats()},
            {SHAKER2: _sixteenths(), CH: _offbeats(), STICK: [3.5]},
            {SHAKER: _sixteenths(), CH: _offbeats(), STICK: [1.5, 3.5],
             CH2: [3.5]},
        ],
        "03 hats-swerve": [
            {CH: _offbeats(), CH2: [1.5]},
            {CH: _offbeats(), CH2: [1.5, 3.5]},
            {CH: _offbeats(), CH2: _offbeats(), STICK: [3.5]},
            {CH: _offbeats(), CH2: _offbeats(), STICK: [1.5, 3.5],
             SHAKER: _sixteenths()},
        ],
        "04 full": [
            {CH: _offbeats(), SHAKER: _sixteenths()},
            {CH: _offbeats(), SHAKER: _sixteenths(), STICK: [1.5, 3.5]},
            {CH: _offbeats(), CH2: [1.5, 3.5], SHAKER: _sixteenths(),
             STICK: [1.5, 3.5]},
            {CH: _offbeats(), CH2: _offbeats(), SHAKER: _sixteenths(),
             STICK: [1.5, 3.5], SHAKER2: [0.0, 2.0]},
        ],
    },
    "chops": {
        # Dub-chord stabs. Long durations - the sample is the chord, the note
        # only chooses which slice of it plays.
        "01 skank": [
            {CHOP_A: [1.5, 3.5]},
            {CHOP_A: [0.0, 1.5], CHOP_B: [3.5]},
            {CHOP_A: [0.0, 2.5], CHOP_B: [1.5, 3.5]},
            {CHOP_A: [0.0, 2.5], CHOP_B: [1.5], CHOP_C: [3.5]},
        ],
        "02 dub-stabs": [
            {CHOP_C: [0.0]},
            {CHOP_C: [0.0], CHOP_D: [2.5]},
            {CHOP_D: [0.0], CHOP_C: [1.5], CHOP_B: [3.0]},
            {CHOP_D: [0.0], CHOP_C: [1.5], CHOP_B: [3.0], CHOP_A: [3.75]},
        ],
        "03 chop-swerve": [
            {CHOP_A: [0.0, 0.25], CHOP_E: [2.5, 2.75]},
            {CHOP_A: [0.0, 0.25], CHOP_B: [1.5, 1.75], CHOP_D: [3.0, 3.25]},
            {CHOP_A: [0.0, 0.25], CHOP_B: [1.5, 1.75], CHOP_D: [3.0, 3.25],
             CHOP_C: [2.5]},
            {CHOP_A: [0.0, 1.5], CHOP_B: [0.5, 2.0], CHOP_D: [1.0, 2.5],
             CHOP_C: [3.0], CHOP_E: [3.5]},
        ],
    },
}

# Bars that thin out or fill, applied on top of the section layer.
DROP_BARS = {8: [0, 2], 9: [0]}       # dub dropout: kick thins to half/one
FILL_BAR = 15


def bar_layers(bar, sections, kind):
    """Pitch -> beat positions for one bar, including drops and the closing fill."""
    beat_map = sections[min(bar // 4, 3)]
    layers = {p: list(pos) for p, pos in beat_map.items() if pos}
    has_kick = KICK in layers

    if bar in DROP_BARS and has_kick:
        layers[KICK] = DROP_BARS[bar]
        for p in (CLAP, SNAP, SNARE, PERC):
            layers.pop(p, None)

    if bar == FILL_BAR:
        if kind == "chops":
            return {CHOP_D: [0.0], CHOP_A: [2.5]}
        if kind == "drums":
            if has_kick:
                layers[KICK] = [0, 1, 2]
            layers[TOM] = [3.0, 3.5]
            layers[TOM_LO] = [3.25]
            layers[FX] = [3.75]
        else:  # tops: hats-only turnaround, no toms (drums owns the tom fill)
            layers[CH] = _offbeats()[:3]
            layers[CH2] = [3.75]
    return layers


def build_clip(sections, kind):
    notes = []
    for bar in range(BARS):
        for pitch, positions in bar_layers(bar, sections, kind).items():
            for i, pos in enumerate(positions):
                t = bar * 4.0 + pos
                if t >= CLIP_LEN:
                    continue
                swing = 1 if (pitch in (CH, CH2, SHAKER, SHAKER2) and i % 2) else 0
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
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--track", type=int,
                    help="track index (default: first track named *Pad Kit*)")
    ap.add_argument("--start-slot", type=int, default=1,
                    help="first clip slot to write (default 1, leaves slot 0 alone)")
    ap.add_argument("--set", choices=sorted(PATTERN_SETS), default="drums",
                    help="drums | tops | chops - one role per kit track")
    args = ap.parse_args()

    patterns = PATTERN_SETS[args.set]
    client = MCPClientTCP()
    track = resolve_track(client, args.track, "Pad Kit")
    print("writing {} clips (set: {}) on track {}".format(
        len(patterns), args.set, track))

    existing = {c["index"]: c for c in client.send_command(
        "get_all_clips_in_track", {"track_index": track})["result"]["clips"]}

    for offset, (name, sections) in enumerate(patterns.items()):
        slot = args.start_slot + offset
        notes = build_clip(sections, args.set)
        if slot in existing:
            old = existing[slot]
            if not old.get("name", "").startswith("Dub Techno"):
                print("  slot {} holds {!r} ({} beats) - overwriting".format(
                    slot, old.get("name"), old.get("length")))
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
                             "name": "Dub Techno {} 16bar {}".format(
                                 args.set, name)})

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
        pitches = {n["pitch"] for n in got}
        assert pitches <= set(PADS), "slot {}: off-kit pitches {}".format(
            slot, sorted(pitches - set(PADS)))
        if any(KICK in layer for layer in sections):
            assert all(KICK in v for v in per_bar.values()), \
                "slot {}: a bar has no kick".format(slot)
        else:
            assert KICK not in pitches, \
                "slot {}: this set must not contain a kick".format(slot)
        print("  slot {} [{}] {:3d} hits, {} bars: {}".format(
            slot, name, len(got), len(per_bar),
            ", ".join(PADS[p] for p in sorted(pitches))))

    print("\nOK - {} clips on track {}".format(len(patterns), track))


if __name__ == "__main__":
    main()
