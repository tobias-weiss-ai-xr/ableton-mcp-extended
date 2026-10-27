#!/usr/bin/env python3
"""DUB LIVE ROOM - 8-lane dub techno session for live recording."""

import argparse, json, socket, sys, time

HOST, PORT = "127.0.0.1", 9877
TEMPO = 120.0
CLIP_BEATS = 16.0

class Live:
    def __init__(self, host=HOST, port=PORT):
        self.sock = socket.socket()
        self.sock.settimeout(30)
        self.sock.connect((host, port))
    def send(self, cmd, params=None):
        payload = json.dumps(dict(type=cmd, params=params or dict())).encode() + b"\n"
        self.sock.sendall(payload)
        raw = self.sock.recv(262144).decode()
        return json.loads(raw) if raw else dict(status="ok")
    def send_checked(self, cmd, params=None, descr=""):
        r = self.send(cmd, params)
        if r.get("status") != "success":
            raise RuntimeError(str(descr or cmd) + " failed: " + json.dumps(r)[:200])
        return r
    def close(self):
        self.sock.close()

# Browser URIs (proven working)
DRUMS   = "query:Drums#FileId_58622"
BASS    = "query:Sounds#Bass:FileId_49654"
PAD     = "query:Sounds#Pad:FileId_45564"
STRINGS = "query:Sounds#Pad:FileId_45565"
LEAD    = "query:Sounds#Synth%20Lead:FileId_50175"

FX_REVERB    = "query:AudioFx#Reverb"
FX_DELAY     = "query:AudioFx#Delay"
FX_EQ8       = "query:AudioFx#EQ%20Eight"
FX_COMP      = "query:AudioFx#Compressor"
FX_AFILTER   = "query:AudioFx#Auto%20Filter"
FX_DRUMBUSS  = "query:AudioFx#Drum%20Buss"
FX_SATURATOR = "query:AudioFx#Saturator"
FX_UTILITY   = "query:AudioFx#Utility"

# (name, instrument_uri, effects, volume 0-1, pan -1..1)
TRACKS = [
    ("KICK", DRUMS,   [FX_DRUMBUSS, FX_EQ8],                   0.85,  0.00),
    ("HATS", DRUMS,   [FX_DRUMBUSS, FX_REVERB, FX_DELAY],      0.68,  0.15),
    ("BASS", BASS,    [FX_EQ8, FX_AFILTER, FX_COMP],           0.80,  0.00),
    ("SUB",  BASS,    [FX_AFILTER, FX_SATURATOR, FX_UTILITY],  0.78,  0.00),
    ("STAB", PAD,     [FX_DELAY, FX_AFILTER, FX_REVERB],       0.62, -0.22),
    ("PAD",  STRINGS, [FX_REVERB, FX_DELAY, FX_EQ8],           0.58,  0.18),
    ("LEAD", LEAD,    [FX_DELAY, FX_AFILTER, FX_REVERB],       0.60,  0.28),
    ("FX",   DRUMS,   [FX_DELAY, FX_AFILTER, FX_REVERB],       0.52, -0.30),
]

SCENES = ["EMERGE", "PULSE", "GROOVE", "DROP", "BREAK", "DISSOLVE"]

def n(pitch, start, dur, vel):
    return dict(pitch=pitch, start_time=float(start),
                duration=float(dur), velocity=int(vel))

def chord(pitches, start, dur, vel):
    return [n(p, start, dur, vel) for p in pitches]

# C minor pitches
KICK_NOTE, C1, F1, G1 = 36, 24, 29, 31
CM = (48, 51, 55)   # C minor
FM = (53, 56, 60)   # F minor
CLAP, COWBELL, TOM = 39, 56, 50  # drum rack perc

def offbeat_stabs(root, starts, vel):
    out = []
    for s in starts:
        out += chord(root, s, 0.5, vel)
    return out

def hats(base_vel, ghost_16ths=False, open_accents=False):
    out = []
    for bar in range(4):
        b = bar * 4
        out.append(n(42, b + 2, 0.25, base_vel))
        out.append(n(42, b + 2.5, 0.125, base_vel - 12))
        out.append(n(42, b + 3, 0.25, base_vel - 6))
        if ghost_16ths:
            out.append(n(42, b + 3.75, 0.125, 55))
            out.append(n(42, b + 1.5, 0.125, 58))
        if open_accents:
            out.append(n(46, b + 1.75, 0.5, base_vel + 6))
    return out


# CLIPS[(scene_idx, track_idx)] -> notes. Empty slots = lane silent in scene.
CLIPS = dict([
    # 0 EMERGE - pads + sub drone, no beat
    ((0, 5), chord(CM, 0, 16, 68)),
    ((0, 3), [n(C1, 0, 16, 75)]),
    ((0, 7), [n(TOM, 0, 1, 55), n(TOM, 8, 1, 50)]),
    # 1 PULSE - beat enters
    ((1, 0), [n(KICK_NOTE, b, 0.5, 112) for b in (0, 4, 8, 12)]),
    ((1, 1), hats(78)),
    ((1, 5), chord(CM, 0, 16, 72)),
    ((1, 3), [n(C1, 0, 16, 80)]),
    ((1, 7), [n(CLAP, 4, 0.5, 68), n(CLAP, 12, 0.5, 64)]),
    # 2 GROOVE - full rhythm section
    ((2, 0), [n(KICK_NOTE, b, 0.5, 115) for b in (0, 4, 8, 12)]
             + [n(KICK_NOTE, b, 0.25, 78) for b in (3, 11)]),
    ((2, 1), hats(82, ghost_16ths=True)),
    ((2, 2), [n(C1, 0, 3.5, 100), n(C1, 4, 3.5, 95),
              n(G1, 8, 3.5, 100), n(F1, 12, 3.5, 95)]),
    ((2, 4), offbeat_stabs(CM, (2, 6, 10, 14), 88)),
    ((2, 5), chord(FM, 0, 8, 75) + chord(CM, 8, 8, 75)),
    ((2, 3), [n(C1, 0, 8, 88), n(G1, 8, 8, 88)]),
    ((2, 7), [n(CLAP, 2, 0.5, 74), n(CLAP, 6, 0.5, 70),
              n(CLAP, 10, 0.5, 74), n(CLAP, 14, 0.5, 70)]),
    # 3 DROP - everything, maximum dub
    ((3, 0), [n(KICK_NOTE, b, 0.5, 118) for b in (0, 4, 8, 12)]
             + [n(KICK_NOTE, b, 0.25, 82) for b in (2.5, 6.5, 10.5, 14.5)]),
    ((3, 1), hats(85, ghost_16ths=True, open_accents=True)),
    ((3, 2), [n(C1, 0, 1.5, 110), n(C1, 2, 1.5, 102),
              n(C1, 4, 1.5, 110), n(G1, 6, 1.5, 102),
              n(G1, 8, 1.5, 110), n(G1, 10, 1.5, 102),
              n(F1, 12, 1.5, 110), n(F1, 14, 1.5, 102)]),
    ((3, 4), offbeat_stabs(CM, (2, 10), 92) + offbeat_stabs(FM, (4, 12), 85)
             + offbeat_stabs(CM, (6, 14), 80)),
    ((3, 5), chord(CM, 0, 4, 80) + chord(FM, 4, 4, 80)
             + chord(CM, 8, 4, 80) + chord(FM, 12, 4, 80)),
    ((3, 3), [n(C1, 0, 4, 92), n(G1, 4, 4, 92),
              n(F1, 8, 4, 92), n(C1, 12, 4, 92)]),
    ((3, 6), [n(60, 0, 0.75, 100), n(63, 1, 0.75, 95), n(65, 2, 1.25, 100),
              n(63, 3.5, 0.5, 88), n(60, 4, 0.75, 98), n(58, 5, 0.75, 92),
              n(60, 6, 1.5, 100), n(67, 8, 0.75, 100), n(65, 9, 0.75, 95),
              n(63, 10, 1.25, 98), n(65, 11.5, 0.5, 88), n(60, 12, 0.75, 98),
              n(62, 13, 0.75, 92), n(60, 14, 1.5, 100)]),
    ((3, 7), [n(CLAP, 2, 0.5, 80), n(COWBELL, 3.5, 0.5, 72),
              n(CLAP, 6, 0.5, 80), n(TOM, 9, 0.5, 74),
              n(CLAP, 10, 0.5, 80), n(COWBELL, 13.5, 0.5, 72),
              n(CLAP, 14, 0.5, 80)]),
    # 4 BREAK - strip back
    ((4, 2), [n(C1, 0, 7, 90), n(G1, 8, 7, 90)]),
    ((4, 5), chord(CM, 0, 16, 62)),
    ((4, 3), [n(C1, 0, 16, 82)]),
    ((4, 6), [n(60, 0, 2, 75), n(63, 4, 2, 72),
              n(65, 8, 2, 75), n(63, 12, 2, 70)]),
    ((4, 7), [n(TOM, 0, 1, 62), n(TOM, 8, 1, 58)]),
    # 5 DISSOLVE - fade out
    ((5, 5), chord(CM, 0, 16, 42)),
    ((5, 3), [n(C1, 0, 16, 55)]),
    ((5, 7), [n(TOM, 0, 1, 48)]),
])


def cleanup(c):
    print("[clean] clearing session")
    c.send("stop_playback")
    for _ in range(3):
        c.send("delete_all_tracks")
        time.sleep(0.3)
    r = c.send("get_all_tracks")
    tracks = (r.get("result") or dict()).get("tracks", [])
    for ti in range(len(tracks) - 1, 0, -1):
        c.send("delete_track", dict(track_index=ti))
        time.sleep(0.05)
    time.sleep(0.2)


def load_with_retry(c, track_idx, uri, what, tries=3):
    for attempt in range(tries):
        r = c.send("load_browser_item",
                   dict(track_index=track_idx, item_uri=uri))
        if (r or dict()).get("status") == "success":
            return True
        print("    retry %d/%d for %s" % (attempt + 1, tries, what))
        time.sleep(2.0)
    return False


def build_tracks(c):
    print("[tracks] building %d MIDI tracks" % len(TRACKS))
    for idx, (name, inst, fx, vol, pan) in enumerate(TRACKS):
        print("  track %d: %s" % (idx, name))
        c.send_checked("create_midi_track", dict(index=idx), "create " + name)
        time.sleep(0.15)
        c.send_checked("set_track_name",
                       dict(track_index=idx, name=name), "name " + name)
        if not load_with_retry(c, idx, inst, "instrument"):
            raise RuntimeError("instrument load failed on " + name)
        time.sleep(1.5)
        for fx_uri in fx:
            if not load_with_retry(c, idx, fx_uri, fx_uri):
                print("    [warn] " + fx_uri + " failed - continuing")
            time.sleep(1.2)
        c.send_checked("set_track_volume", dict(track_index=idx, volume=vol))
        c.send_checked("set_track_pan", dict(track_index=idx, pan=pan))
    # drop leftover track(s) from cleanup (Live keeps >=1 track on delete)
    r = c.send("get_all_tracks")
    all_tracks = (r.get("result") or dict()).get("tracks", [])
    for ti in range(len(all_tracks) - 1, len(TRACKS) - 1, -1):
        c.send("delete_track", dict(track_index=ti))
        time.sleep(0.05)
    if len(all_tracks) > len(TRACKS):
        print("  deleted %d leftover track(s)" % (len(all_tracks) - len(TRACKS)))


def build_scenes(c):
    print("[scenes] %d scenes" % len(SCENES))
    for _ in range(12):  # trim extras
        r = c.send("get_all_scenes")
        count = (r.get("result") or dict()).get("count", 0)
        if count <= len(SCENES):
            break
        c.send("delete_scene", dict(index=count - 1))
        time.sleep(0.05)
    for _ in range(12):  # add if short
        r = c.send("get_all_scenes")
        count = (r.get("result") or dict()).get("count", 0)
        if count >= len(SCENES):
            break
        c.send("create_scene", dict(index=-1))
        time.sleep(0.05)
    for si, name in enumerate(SCENES):
        c.send_checked("set_scene_name", dict(scene_index=si, name=name))


def build_clips(c):
    print("[clips] %d clips (%s beats = 4 bars each)" % (len(CLIPS), CLIP_BEATS))
    for (si, ti), notes in sorted(CLIPS.items()):
        c.send_checked("create_clip",
                       dict(track_index=ti, clip_index=si, length=CLIP_BEATS),
                       "clip t%d s%d" % (ti, si))
        time.sleep(0.15)
        c.send_checked("add_notes_to_clip",
                       dict(track_index=ti, clip_index=si, notes=notes),
                       "notes t%d s%d" % (ti, si))
        time.sleep(0.2)
    total = 0
    for v in CLIPS.values():
        total += len(v)
    print("  %d notes written" % total)


def verify(c):
    r = c.send("get_all_tracks")
    tracks = (r.get("result") or dict()).get("tracks", [])
    print("[verify] %d tracks" % len(tracks))
    for t in tracks:
        print("  %s: %s" % (t.get("index"), t.get("name")))
    ok = True
    for (si, ti) in sorted(CLIPS):
        r = c.send("get_track_info", dict(track_index=ti))
        slots = (r.get("result") or dict()).get("clip_slots", [])
        has = si < len(slots) and slots[si].get("has_clip")
        if not has:
            print("  [MISS] track %d scene %d" % (ti, si))
            ok = False
    if ok:
        print("[verify] clips: ALL OK")
    else:
        print("[verify] clips: MISSING SLOTS")
    return ok


def main():
    ap = argparse.ArgumentParser(description="8-lane dub techno live session")
    ap.add_argument("--no-clean", action="store_true",
                    help="skip session cleanup")
    args = ap.parse_args()

    c = Live()
    try:
        if not args.no_clean:
            cleanup(c)
        c.send_checked("set_tempo", dict(tempo=TEMPO))
        print("[tempo] %s BPM" % TEMPO)
        build_tracks(c)
        build_scenes(c)
        build_clips(c)
        if not verify(c):
            sys.exit(1)

        bar = "=" * 60
        print("")
        print(bar)
        print(" DUB LIVE ROOM ready - 8 lanes x 6 scenes @ %s BPM" % TEMPO)
        print(bar)
        print(" 0 KICK   1 HATS   2 BASS   3 SUB")
        print(" 4 STAB   5 PAD    6 LEAD   7 FX")
        print("")
        print(" Scenes: EMERGE > PULSE > GROOVE > DROP > BREAK > DISSOLVE")
        print(" (empty slots = that lane stays silent in the scene)")
        print("")
        print(" LIVE RECORD:")
        print("   1. Arm master + Arrangement record (or arm tracks)")
        print("   2. Hit record, fire scene 0 (EMERGE)")
        print("   3. Chain scenes by ear: 1 > 2 > 3 > 4 > 2 > 3 ... > 5")
        print("   4. Stop - your take is in the Arrangement View")
        print(bar)
    finally:
        c.close()


if __name__ == "__main__":
    main()
