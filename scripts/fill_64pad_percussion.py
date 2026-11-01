#!/usr/bin/env python
"""Fill 10 x 16-bar reggae/dub PERCUSSION clips on a 64-Pad-Kit track.

The 64-Pad-Kit racks are percussion instruments (macros: Kick/Snare/HH/Cym/
Toms/Percussion Vol) - not chord instruments.

WARNING: the note map below is NOT read from a kit. Pad racks are grids of
one-shot samples addressed by MIDI note, so a note means whatever that kit puts
there - on the Dub Techno kit these numbers are chord chops (36 = "Chord Dub
Chop 4"), and on 64 Pad Kit Special they are cymbals. Verify before trusting:

    python scripts/inspect_pad_kit.py --kit <preset>.adg

See scripts/fill_dub_techno_percussion.py for a map that is verified, and
skills/ableton-pad-instruments for the full explanation.

    python scripts/fill_64pad_percussion.py            # track named *Pad Kit*
    python scripts/fill_64pad_percussion.py --track 2
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_client import MCPClientTCP  # noqa: E402

CLIP_LEN = 64.0
KICK, SNARE, CLAP, RIM = 36, 38, 39, 56
CH, OH = 42, 46
SKANK, SHK = 60, 74
TOM1, TOM2 = 68, 70

VEL = {KICK: 96, SNARE: 88, CLAP: 84, CH: 66, OH: 78,
       SKANK: 70, SHK: 52, TOM1: 80, TOM2: 78, RIM: 64}

# style 0..3 = sparse -> full percussion
STYLES = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3]


def bar_layers(bar, style):
    """Instrument -> half-beat positions (0-7) inside one bar."""
    layers = {
        KICK: [0, 5],          # beat 1 + delayed drop (one-drop feel)
        SNARE: [4],            # backbeat
        CH: [1, 3, 5, 7],      # offbeat hats
    }
    if style >= 1:
        layers[SKANK] = [1, 3, 5, 7]
    if style >= 2:
        layers[SHK] = [1, 3, 5, 7]
        layers[CLAP] = [4] if bar % 4 == 2 else []
    if style >= 3:
        layers[OH] = [7]
        layers[RIM] = [3, 7]

    if bar == 9:  # dub dropout: kick + hats only
        layers = {KICK: [0], CH: [1, 3, 5, 7]}
        if style >= 2:
            layers[SKANK] = [1, 5]
    if bar in (7, 15):  # tom fills
        layers = {KICK: [0, 6], SNARE: [5, 6, 7] if bar == 15 else [4],
                  CH: [1, 3, 5, 6, 7] if bar == 15 else [1, 3, 5, 7],
                  OH: [7], TOM1: [5, 7], TOM2: [6]}
        if style >= 2:
            layers[RIM] = [3]
    return {k: [p for p in v if p < 8] for k, v in layers.items()}


def build_clip(style):
    notes = []
    for bar in range(16):
        for pitch, positions in bar_layers(bar, style).items():
            for p in positions:
                t = bar * 4.0 + p * 0.5
                if t >= CLIP_LEN:
                    continue
                notes.append({"pitch": pitch, "start_time": round(t, 3),
                              "duration": 0.22, "velocity": VEL.get(pitch, 72),
                              "mute": False})
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
    ap.add_argument("--track", type=int, help="track index (default: first track named *Pad Kit*)")
    args = ap.parse_args()

    client = MCPClientTCP()
    track = resolve_track(client, args.track, "Pad Kit")
    print("filling 10 percussion clips on track {}".format(track))
    print("WARNING: note map is generic, not read from this kit - verify with "
          "scripts/inspect_pad_kit.py (see module docstring)")

    for slot, style in enumerate(STYLES):
        notes = build_clip(style)
        existing = {c["index"] for c in client.send_command(
            "get_all_clips_in_track", {"track_index": track})["result"]["clips"]}
        if slot in existing:
            client.send_command("delete_clip", {"track_index": track, "clip_index": slot})
        client.send_command("create_clip",
                            {"track_index": track, "clip_index": slot, "length": CLIP_LEN})
        client.send_command("add_notes_to_clip",
                            {"track_index": track, "clip_index": slot, "notes": notes})
        client.send_command("set_clip_name",
                            {"track_index": track, "clip_index": slot,
                             "name": "Pad Kit Clip {:02d}".format(slot + 1)})

        got = client.send_command("get_clip_notes",
                                  {"track_index": track, "clip_index": slot})["result"]["notes"]
        assert len(got) == len(notes), "clip {}: readback {} != {}".format(
            slot, len(got), len(notes))
        per_bar = defaultdict(set)  # sanity: every bar has a kick
        for n in got:
            per_bar[int(n["start_time"] // 4)].add(n["pitch"])
        assert all(KICK in v for v in per_bar.values()), "clip {}: bar without kick".format(slot)
        print("  clip {:02d} [style {}] {:3d} hits  notes {}".format(
            slot + 1, style, len(got), sorted({n["pitch"] for n in got})))

    print("\nOK - 10 clips on track {}".format(track))


if __name__ == "__main__":
    main()
