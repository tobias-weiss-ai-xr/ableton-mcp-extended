#!/usr/bin/env python
"""Show what a pad-based Ableton instrument actually contains.

A "pad kit" rack (64 Pads Dub Techno Kit, 64 Pad Kit Special, ...) is not a
chromatic instrument: it is a grid of one-shot samples, each triggered by a
fixed MIDI note. Every chain in the rack is a Simpler whose root key is 60 and
which is *not* transposed, so note N always plays sample N at its original
pitch. The note number is an address, not a pitch - note 36 is a chord chop in
one kit and a cymbal in another.

The preset file (.adg, gzipped XML) is the source of truth, so this reads it
directly instead of guessing from a drum-map convention.

    python scripts/inspect_pad_kit.py --list
    python scripts/inspect_pad_kit.py --kit "C:/.../64 Pads Dub Techno Kit.adg"
    python scripts/inspect_pad_kit.py --kit ... --search kick,clap
    python scripts/inspect_pad_kit.py --kit ... --python     # dict for reuse
"""

import argparse
import gzip
import re
import sys
from pathlib import Path
from xml.sax.saxutils import unescape

FACTORY = Path.home() / "Documents/Ableton/Factory Packs"
USER_PRESETS = Path.home() / "Documents/Ableton/User Library/Presets"


def find_kits(pattern="*.adg"):
    """Every pad-kit preset on disk (drum racks with 64 pad chains)."""
    out = []
    for root in (FACTORY, USER_PRESETS):
        if not root.is_dir():
            continue
        for p in root.rglob(pattern):
            try:
                xml = gzip.open(p, "rb").read(4096 * 1024).decode("utf-8", "replace")
            except OSError:
                continue
            if "<DrumBranchPreset" in xml:
                out.append(p)
    return sorted(out)


def read_pads(path):
    """[(note, sample_name)] read from the preset's pad chains."""
    xml = gzip.open(path, "rb").read().decode("utf-8", "replace")
    pads = {}
    for block in re.split(r'<DrumBranchPreset Id="\d+">', xml)[1:]:
        note = re.search(r'<ReceivingNote Value="(\d+)" />', block)
        part = re.search(
            r'<MultiSamplePart[^>]*>\s*<LomId Value="0" />\s*<Name Value="([^"]*)"',
            block)
        send = re.search(r'<SendingNote Value="(\d+)" />', block)
        root = re.search(r'<RootKey Value="(\d+)" />', block)
        if not note:
            continue
        pads[int(note.group(1))] = {
            "name": unescape(part.group(1)) if part else "",
            "sending_note": int(send.group(1)) if send else None,
            "root_key": int(root.group(1)) if root else None,
        }
    return pads


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kit", help="path to a .adg pad-kit preset")
    ap.add_argument("--list", action="store_true", help="list pad kits found on disk")
    ap.add_argument("--search", help="comma-separated terms to filter sample names")
    ap.add_argument("--python", action="store_true",
                    help="emit a plain dict literal to paste into a script")
    args = ap.parse_args()

    if args.list or not args.kit:
        kits = find_kits()
        print("{} pad kits found:".format(len(kits)))
        for k in kits:
            print("  ", k)
        if not args.kit:
            return
    kitt = Path(args.kit)
    if not kitt.exists():
        sys.exit("no such file: {}".format(kitt))

    pads = read_pads(kitt)
    if not pads:
        sys.exit("{} has no pad chains - not a drum-rack pad kit".format(kitt.name))

    terms = [t.strip().lower() for t in (args.search or "").split(",") if t.strip()]
    rows = [(n, v) for n, v in sorted(pads.items())
            if not terms or any(t in v["name"].lower() for t in terms)]

    shifted = [n for n, v in pads.items()
               if v["root_key"] not in (None, 60) or v["sending_note"] not in (None, 60)]

    if args.python:
        print("PADS = {")
        for n, v in rows:
            print('    {:3d}: {!r},'.format(n, v["name"]))
        print("}")
        return

    print("{}: {} pads, notes {}..{}".format(
        kitt.name, len(pads), min(pads), max(pads)))
    print("transposed pads: {}{}".format(
        len(shifted), " (note is a pitch for these)" if shifted else
        " - every note maps 1:1 to one sample at original pitch"))
    print()
    for n, v in rows:
        print("  {:<4} {}".format(n, v["name"] or "<empty>"))
    if terms:
        print("\n{} of {} pads match {}".format(len(rows), len(pads), terms))


if __name__ == "__main__":
    main()
