#!/usr/bin/env python
"""Reproducible dub techno bass channel: instrument + FX chain + 4x 16-bar basslines.

Idempotent: loads the chain only if the track has no devices, re-applies every
parameter value each run, and rewrites the clips from scratch.

    python scripts/build_dub_techno_bass.py                 # track named *MIDI*
    python scripts/build_dub_techno_bass.py --track 0
    python scripts/build_dub_techno_bass.py --skip-chain     # clips only
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_client import MCPClientTCP  # noqa: E402

CLIP_LEN = 64.0  # 16 bars @ 4/4
NAMES = ["Dub Techno Bass 16bar {:02d}".format(i) for i in range(1, 5)]

# Bb minor bass register
Bb1, Ab1, Gb1, Eb2, F2, Bb2 = 34, 32, 30, 39, 41, 46
PALETTE = {Bb1, Ab1, Gb1, Eb2, F2, Bb2}

CHAIN = [
    ("query:Synths#Bass:Bass:FileId_50061", "Sub Bass Drone"),  # Drift sub preset
    ("query:AudioFx#Saturator", "Saturator"),
    ("query:AudioFx#Auto%20Filter", "Auto Filter"),
    ("query:AudioFx#Echo", "Echo"),
    ("query:AudioFx#Reverb", "Reverb"),
]

# (device_index, parameter_index, value) in each device's NATIVE range.
SETTINGS = [
    # Drift sub: deep, punchy, clean
    (0, 19, 0.0), (0, 10, 30.0), (0, 18, 30.0), (0, 2, 6.0), (0, 3, 620.0),
    (0, 4, 130.0), (0, 5, 72.0), (0, 46, 48.0), (0, 48, 30.0), (0, 43, 10.0),
    (0, 35, 0.0), (0, 54, 0.0), (0, 8, 4.0), (0, 12, 24.0), (0, 56, -4.0),
    # Saturator: harmonics so the sub reads on small speakers
    (1, 3, 0.0), (1, 1, 0.28), (1, 11, 0.8), (1, 10, 1.0), (1, 9, 0.0),
    # Auto Filter: the dub lowpass (automation target)
    (2, 4, 0.0), (2, 5, 1.0), (2, 1, 0.42), (2, 2, 0.22), (2, 8, 0.15),
    (2, 28, 0.30), (2, 29, 0.12), (2, 31, 0.50), (2, 36, 1.0),
    # Echo: dotted-8th, dark repeats, lows trimmed
    (3, 4, 3.0), (3, 10, 3.0), (3, 16, 0.45), (3, 29, 0.15), (3, 31, 0.30),
    (3, 42, 0.25), (3, 43, 0.60), (3, 51, 0.35), (3, 52, 0.22),
    # Reverb: low-cut, small amount, bass stays tight
    (4, 2, 1.0), (4, 4, 0.55), (4, 20, 0.55), (4, 1, 0.10), (4, 32, 0.12),
]

# --- bassline cells: name -> [(16th_step, pitch, duration_beats, velocity)] ---
V1_CELLS = {
    "root":    [(0, Bb1, 0.9, 104), (6, Bb1, 0.45, 88), (10, Bb1, 0.45, 92)],
    "octave":  [(0, Bb1, 0.9, 104), (6, Bb1, 0.45, 88), (10, Bb2, 0.45, 96),
                (14, Bb1, 0.4, 84)],
    "fourth":  [(0, Bb1, 0.85, 104), (6, Eb2, 0.45, 90), (10, Bb1, 0.45, 92),
                (14, Bb1, 0.4, 82)],
    "seventh": [(0, Bb1, 0.9, 102), (6, Ab1, 0.5, 88), (10, Bb1, 0.45, 90)],
    "fifth":   [(0, Bb1, 0.9, 104), (6, Bb1, 0.4, 86), (10, F2, 0.5, 94),
                (14, Bb1, 0.4, 84)],
    "drop":    [(0, Bb1, 1.6, 108)],
    "fill":    [(0, Bb1, 0.45, 104), (4, Bb1, 0.3, 88), (7, Bb1, 0.3, 92),
                (10, Ab1, 0.4, 96), (12, Gb1, 0.4, 92), (14, F2, 0.45, 100)],
    "sparse":  [(0, Bb1, 0.9, 100), (10, Bb1, 0.5, 86)],
}
V2_CELLS = {
    "drive":     [(0, Bb1, 0.7, 106), (4, Bb1, 0.35, 86), (8, Bb1, 0.7, 100),
                  (12, Bb1, 0.35, 88), (14, Bb1, 0.3, 92)],
    "drive_oct": [(0, Bb1, 0.7, 106), (4, Bb1, 0.35, 86), (8, Bb2, 0.4, 98),
                  (12, Bb1, 0.35, 88), (14, F2, 0.3, 94)],
    "drive_4th": [(0, Bb1, 0.7, 106), (4, Eb2, 0.35, 90), (8, Bb1, 0.7, 100),
                  (12, Ab1, 0.4, 92)],
    "drive_5th": [(0, Bb1, 0.7, 104), (4, Bb1, 0.35, 86), (8, F2, 0.45, 96),
                  (12, Bb1, 0.35, 88)],
    "drive_fill": [(0, Bb1, 0.4, 104), (2, Bb1, 0.3, 88), (4, Bb1, 0.3, 90),
                   (6, Gb1, 0.3, 92), (8, Ab1, 0.35, 94), (10, Bb1, 0.35, 96),
                   (12, Eb2, 0.4, 98), (14, F2, 0.4, 100)],
}
V3_CELLS = {
    "long":     [(0, Bb1, 3.7, 100)],
    "long_m7":  [(0, Bb1, 1.8, 100), (8, Ab1, 1.7, 88)],
    "long_4th": [(0, Bb1, 1.8, 100), (8, Eb2, 1.7, 90)],
    "long_5th": [(0, Bb1, 1.8, 98), (8, F2, 1.7, 90)],
    "stab":     [(0, Bb1, 0.9, 104), (10, Bb1, 0.6, 84), (14, Bb1, 0.5, 78)],
    "space":    [(0, Bb1, 1.7, 98), (12, Bb1, 0.5, 82)],
    "swell":    [(0, Bb1, 2.4, 102), (10, Gb1, 1.4, 84)],
}
V4_CELLS = {
    "roll":      [(0, Bb1, 0.45, 106), (3, Bb1, 0.3, 86), (6, Bb1, 0.4, 92),
                  (9, Bb1, 0.3, 84), (10, Bb1, 0.4, 96), (13, Bb1, 0.3, 86)],
    "roll_up":   [(0, Bb1, 0.45, 106), (3, Bb1, 0.3, 86), (6, Eb2, 0.4, 92),
                  (8, F2, 0.35, 94), (10, Bb2, 0.4, 98), (13, Bb1, 0.3, 86)],
    "roll_7":    [(0, Bb1, 0.45, 104), (3, Ab1, 0.3, 88), (6, Bb1, 0.4, 92),
                  (10, Gb1, 0.4, 90), (13, Bb1, 0.3, 86)],
    "roll_4th":  [(0, Bb1, 0.45, 104), (3, Bb1, 0.3, 86), (6, Eb2, 0.45, 94),
                  (10, Bb1, 0.4, 92), (13, Ab1, 0.35, 88)],
    "roll_fill": [(0, Bb1, 0.35, 106), (2, Bb1, 0.25, 90), (4, Bb1, 0.3, 92),
                  (6, Gb1, 0.3, 90), (8, Ab1, 0.3, 94), (10, Bb1, 0.3, 96),
                  (11, Eb2, 0.3, 96), (12, F2, 0.35, 98), (14, Bb2, 0.35, 100)],
}

# 16-bar forms: hypnotic build -> drop -> resolve
V1_FORM = ["sparse", "root", "root", "octave", "root", "seventh", "root",
           "fourth", "drop", "root", "fifth", "octave", "root", "seventh",
           "fourth", "fill"]
V2_FORM = ["drive", "drive", "drive_oct", "drive", "drive_4th", "drive",
           "drive_oct", "drive_fill", "drive", "drive_oct", "drive_5th",
           "drive", "drive_4th", "drive_oct", "drive_5th", "drive_fill"]
V3_FORM = ["long", "space", "long_m7", "stab", "long", "long_4th", "space",
           "swell", "long", "long_5th", "stab", "long_m7", "space",
           "long_4th", "swell", "long"]
V4_FORM = ["roll", "roll", "roll_7", "roll_up", "roll", "roll_4th", "roll_7",
           "roll_fill", "roll", "roll_up", "roll_4th", "roll", "roll_7",
           "roll_up", "roll_4th", "roll_fill"]

VARIANTS = [
    ("root-pulse (hypnotic)", V1_CELLS, V1_FORM),
    ("steppers (driving)", V2_CELLS, V2_FORM),
    ("dub wash (sparse)", V3_CELLS, V3_FORM),
    ("rolling peak", V4_CELLS, V4_FORM),
]


def render(cells, form):
    """Expand a 16-bar form into note dicts, pruning past the clip end."""
    assert len(form) == 16, "form must be 16 bars"
    out = []
    for bar, name in enumerate(form):
        for step, pitch, dur, vel in cells[name]:
            t = bar * 4.0 + step * 0.25
            if t >= CLIP_LEN:
                continue
            dur = min(dur, CLIP_LEN - t)
            out.append({"pitch": pitch, "start_time": round(t, 3),
                        "duration": round(dur, 3), "velocity": vel, "mute": False})
    return out


def resolve_track(client, track_arg, markers):
    """Use --track when given, else first track matching any marker (bass before midi)."""
    if track_arg is not None:
        return track_arg
    tracks = client.send_command("get_all_tracks", {})["result"]["tracks"]
    for marker in markers:
        for t in tracks:
            if marker in (t.get("name") or "").lower():
                return t["index"]
    sys.exit("No track matching any of {}. Tracks: {}".format(
        markers, [(t["index"], t["name"]) for t in tracks]))


def device_count(client, track):
    n = 0
    while client.send_command("get_device_parameters",
                              {"track_index": track, "device_index": n}).get("status") == "success":
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--track", type=int, help="track index (default: first track named *bass* or *midi*)")
    ap.add_argument("--skip-chain", action="store_true", help="only write the bass clips")
    args = ap.parse_args()

    client = MCPClientTCP()
    track = resolve_track(client, args.track, ("bass", "midi"))

    if not args.skip_chain:
        if device_count(client, track) == 0:
            for uri, label in CHAIN:
                r = client.send_command("load_browser_item",
                                        {"track_index": track, "item_uri": uri})
                print("loaded {:16s} {}".format(label, r.get("status")))
            import time
            time.sleep(1.0)
        else:
            print("chain already present on track {} - leaving devices as-is".format(track))

        for dev, idx, val in SETTINGS:
            client.send_command("set_device_parameter",
                                {"track_index": track, "device_index": dev,
                                 "parameter_index": idx, "value": val})
        print("applied {} parameter values".format(len(SETTINGS)))

    for slot, (label, cells, form) in enumerate(VARIANTS):
        notes = render(cells, form)
        assert notes, "{}: no notes".format(label)
        bad = {n["pitch"] for n in notes} - PALETTE
        assert not bad, "{}: pitches outside Bb minor palette {}".format(label, bad)

        slots = client.send_command("get_all_clips_in_track",
                                    {"track_index": track})["result"]["clips"]
        if any(c["index"] == slot for c in slots):
            client.send_command("delete_clip", {"track_index": track, "clip_index": slot})
        client.send_command("create_clip",
                            {"track_index": track, "clip_index": slot, "length": CLIP_LEN})
        client.send_command("add_notes_to_clip",
                            {"track_index": track, "clip_index": slot, "notes": notes})
        client.send_command("set_clip_name",
                            {"track_index": track, "clip_index": slot, "name": NAMES[slot]})

        got = client.send_command("get_clip_notes",
                                  {"track_index": track, "clip_index": slot})["result"]["notes"]
        assert len(got) == len(notes), "clip {}: readback {} != {}".format(
            slot, len(got), len(notes))
        print("clip {:02d} {:22s} {:3d} notes  {}".format(
            slot + 1, label, len(got), dict(sorted(Counter(n["pitch"] for n in got).items()))))

    print("\nOK - 4 clips on track {}".format(track))


if __name__ == "__main__":
    main()
