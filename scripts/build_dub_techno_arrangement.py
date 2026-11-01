#!/usr/bin/env python
"""Assemble the 4-scene dub techno arrangement on the four kit tracks, end to end.

Scene layout (one scene per clip slot, top to bottom):

    slot 0  Intro   drums 01 four-on-floor, tops 01 hats-stick, bass 01, no chops
    slot 1  Build   drums 02 half-time,     tops 02 shaker-swerve, bass 02, chops skank
    slot 2  Break   drums 03 dub dropout,   tops 03 hats-swerve,   bass 03, chops dub-stabs
    slot 3  Drop    drums 04 peak,          tops 04 full,         bass 04, chops swerve

Roles stay disjoint per track (see fill_dub_techno_percussion.py) and the clip
variants already carry the density arc, so firing scenes 1 -> 4 plays a track.

Two things make the scenes readable instead of random:

* Stray half-bar loops that ship with the racks (and leftover experiments) are
  not deleted - they are copied up to slot 5+ with an "archived" name, so the
  arrangement window 0-3 is clean but nothing is lost.
* Clip envelopes: the intro opens the rack filter, the break holds it dark, the
  drop opens the bass filter, and the chop stabs get their delay pushed up.

    python scripts/build_dub_techno_arrangement.py
    python scripts/build_dub_techno_arrangement.py --dry-run
"""

import argparse
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS.parent))

import fill_dub_techno_percussion as kit  # noqa: E402  (pattern data lives there)
from mcp_client import MCPClientTCP  # noqa: E402

BASS_TRACK, DRUMS, TOPS, CHOPS = 0, 1, 2, 3
ARRANGE_SLOTS = 4
ARCHIVE_FROM = 5          # stray clips are parked from this slot upwards

# (track, first slot, set name, pattern names in scene order, None = rest)
ROLES = [
    (DRUMS, 0, "drums", ["01 four-on-floor", "02 half-time", "03 dub dropout", "04 peak"]),
    (TOPS, 0, "tops", ["01 hats-stick", "02 shaker-swerve", "03 hats-swerve", "04 full"]),
    (CHOPS, 1, "chops", ["01 skank", "02 dub-stabs", "03 chop-swerve"]),
]
SCENE_NAMES = ["01 Intro", "02 Build", "03 Break", "04 Drop"]

# Clips that ship inside these racks (or leftover experiments) sitting in the
# arrangement window. Each entry is (track, slot, expected name) - the expected
# name is the guard that makes re-runs safe: once the window holds this script's
# own clips, nothing matches and nothing is moved.
PARK = [
    (DRUMS, 0, ""),
    (DRUMS, 4, "Dub Techno Perc 16bar 03 dub dropout"),
    (TOPS, 0, ""),
    (CHOPS, 0, ""),
    (CHOPS, 1, ""),
]

# (track, clip slot, device, param, [[start_beat, length_beats, value], ...])
FILTER = 2   # rack macro "Filter Cutoff" (native 0..127) on every kit track


def _rise(start, end, bars, steps=8):
    """Ramping steps. A step at beat 0 with the low value is required: without
    it the first beat still carries the parameter's current value (fully open)."""
    step = bars * 4.0 / steps
    points = [[0.0, step, start]]
    points += [[i * step, step, start + (end - start) * i / steps]
               for i in range(1, steps)]
    return points


AUTOMATION = [
    (DRUMS, 0, 0, FILTER, _rise(24, 127, 16)),                      # intro opens up
    (DRUMS, 2, 0, FILTER, [[0.0, 64.0, 40.0]]),                     # break stays dark
    (BASS_TRACK, 3, 2, 1, [[0.0, 16.0, 0.28], [16.0, 16.0, 0.5],
                           [32.0, 16.0, 0.72], [48.0, 16.0, 0.9]]),  # bass filter opens
    (CHOPS, 2, 1, 52, [[0.0, 32.0, 0.6], [32.0, 32.0, 0.8]]),        # delay swells
]


def call(client, cmd, **params):
    """Every mutation raises instead of returning a dict we then index blindly."""
    r = client.send_command(cmd, params)
    if r.get("status") != "success":
        raise RuntimeError("{} {} failed: {}".format(cmd, params, r.get("message", r)))
    return r.get("result", {})


def clips_on(client, track):
    return {c["index"]: c for c in client.send_command(
        "get_all_clips_in_track", {"track_index": track})["result"]["clips"]}


def archive_strays(client, dry_run):
    """Copy stray clips out of the arrangement window instead of deleting them."""
    for track, slot, expected in PARK:
        have = clips_on(client, track)
        clip = have.get(slot)
        if clip is None:
            continue
        name = clip.get("name") or ""
        if name != expected:
            print("  track {} slot {} holds {!r}, not a stray - leaving it".format(
                track, slot, name))
            continue
        notes = call(client, "get_clip_notes",
                     track_index=track, clip_index=slot)["notes"]
        parked = ARCHIVE_FROM
        while parked in have:
            parked += 1
        print("  track {} slot {} -> slot {} ({} notes, {} beats)".format(
            track, slot, parked, len(notes), clip["length"]))
        if dry_run:
            continue
        call(client, "create_clip", track_index=track, clip_index=parked,
             length=clip["length"])
        call(client, "add_notes_to_clip", track_index=track, clip_index=parked,
             notes=notes)
        call(client, "set_clip_name", track_index=track, clip_index=parked,
             name="archived (was slot {})".format(slot))
        back = call(client, "get_clip_notes", track_index=track,
                    clip_index=parked)["notes"]
        assert len(back) == len(notes), "archive lost notes on track {}: {} != {}".format(
            track, len(back), len(notes))
        call(client, "delete_clip", track_index=track, clip_index=slot)


def write_role(client, track, first_slot, set_name, names, dry_run):
    patterns = kit.PATTERN_SETS[set_name]
    have = clips_on(client, track)
    written = 0
    for offset, name in enumerate(names):
        slot = first_slot + offset
        notes = kit.build_clip(patterns[name], set_name)
        if dry_run:
            print("  track {} slot {} <- {}".format(track, slot, name))
            written += 1
            continue
        if slot in have:
            call(client, "delete_clip", track_index=track, clip_index=slot)
        call(client, "create_clip", track_index=track, clip_index=slot,
             length=kit.CLIP_LEN)
        call(client, "add_notes_to_clip", track_index=track, clip_index=slot,
             notes=notes)
        call(client, "set_clip_name", track_index=track, clip_index=slot,
             name="Dub Techno {} {} {}".format(set_name, SCENE_NAMES[slot][3:], name))
        got = call(client, "get_clip_notes", track_index=track,
                   clip_index=slot)["notes"]
        assert len(got) == len(notes), "track {} slot {}: {} != {}".format(
            track, slot, len(got), len(notes))
        assert {n["pitch"] for n in got} <= set(kit.PADS), "off-kit pitch written"
        written += 1
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    client = MCPClientTCP()

    print("1. parking stray clips above slot {}".format(ARCHIVE_FROM))
    archive_strays(client, args.dry_run)

    print("2. writing {} scenes x roles".format(ARRANGE_SLOTS))
    for track, first_slot, set_name, names in ROLES:
        n = write_role(client, track, first_slot, set_name, names, args.dry_run)
        print("  track {} [{}]: {} clips from slot {}".format(
            track, set_name, n, first_slot))

    if not args.dry_run:
        # this script's own earlier output outside the window (e.g. an older slot
        # layout) would otherwise fire as an extra scene further down
        for track, _first, _set, _names in ROLES:
            for slot, c in clips_on(client, track).items():
                if slot >= ARRANGE_SLOTS and (c.get("name") or "").startswith("Dub Techno"):
                    call(client, "delete_clip", track_index=track, clip_index=slot)
                    print("  removed stale clip track {} slot {}".format(track, slot))

    if args.dry_run:
        print("3. scenes + automation (skipped, dry run)")
        return

    print("3. naming scenes")
    for i, name in enumerate(SCENE_NAMES):
        call(client, "set_scene_name", scene_index=i, name=name)

    print("4. clip envelopes")
    for track, clip, device, param, points in AUTOMATION:
        r = call(client, "set_clip_automation", track_index=track,
                 clip_index=clip, device_index=device, parameter_index=param,
                 points=points)
        print("  track {} clip {} dev {} param {}: {} steps".format(
            track, clip, device, param, r.get("added")))

    # envelopes only become readable a moment after the write
    time.sleep(1.5)
    print("5. envelope check")
    for track, clip, device, param, points in AUTOMATION:
        times = [0.0, 8.0, 24.0, 40.0, 56.0]
        r = call(client, "get_clip_automation", track_index=track,
                 clip_index=clip, device_index=device, parameter_index=param,
                 read_times=times)
        vals = [round(v, 2) for v in r.get("readback") or [] if v is not None]
        print("  track {} clip {}: {}".format(track, clip, vals))
        assert vals and min(vals) != max(vals), \
            "envelope on track {} clip {} is flat".format(track, clip)

    print("\nverifying")
    ok = True
    for track, first_slot, set_name, names in ROLES:
        have = clips_on(client, track)
        for offset, name in enumerate(names):
            slot = first_slot + offset
            c = have.get(slot)
            if not c:
                print("  MISSING track {} slot {}".format(track, slot))
                ok = False
                continue
            n = client.send_command("get_clip_notes", {
                "track_index": track, "clip_index": slot})["result"]["notes"]
            bars = len({int(x["start_time"] // 4) for x in n})
            if bars != kit.BARS or c["length"] != kit.CLIP_LEN:
                print("  BAD track {} slot {}: {} bars, {} beats".format(
                    track, slot, bars, c["length"]))
                ok = False
    scenes = client.send_command("get_all_scenes", {})["result"]["scenes"]
    print("  scenes:", [(s["index"], s["name"]) for s in scenes[:ARRANGE_SLOTS]])
    print("  arrangement {}".format("OK" if ok else "INCOMPLETE"))


if __name__ == "__main__":
    main()
