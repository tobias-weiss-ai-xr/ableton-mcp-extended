#!/usr/bin/env python3
"""
Prepare a 5-minute dub tape version in Ableton Live.

Builds a 7-section dub mix (96 bars @ 75 BPM ≈ 5:07) as session clips
with follow-action chaining: fire scene 0 (INTRO) once and the whole
track plays through INTRO → GROOVE → BUILD → DROP → BREAKDOWN → JUMP → OUTRO.

   python scripts/create_5min_dub.py            # build + follow-action chain
   python scripts/create_5min_dub.py --capture  # ALSO record into Arrangement
                                                 # (~5 min realtime; requires Live playing)

Protocol: TCP JSON {"type": cmd, "params": {...}} to the Remote Script (port 9877).
"""

import argparse
import json
import socket
import sys
import time

# ─── MIDI notes (C minor pentatonic universe) ───────────────────────────────
DRUM_KICK   = 36
DRUM_SNARE  = 38
DRUM_CLAP   = 39
DRUM_RIM    = 37
DRUM_HAT_C  = 42
DRUM_HAT_O  = 46
DRUM_PERC   = 56          # cowbell-ish / woodblock zone on the kit

C1, F1, G1 = 24, 29, 31                       # sub octave roots
C2, F2, G2, C3 = 36, 41, 43, 48
F3 = 53
D4 = 62
Eb3, G3, Bb3 = 51, 55, 58
C4, Eb4, F4, G4, Bb4 = 60, 63, 65, 67, 70
C5 = 72

# Verified browser URIs (resolved live via get_browser_item)
DRUMS_URI   = "query:Drums#FileId_58622"              # 32 Pad Kit Jazz.adg
DRUMS2_URI  = "query:Drums#FileId_58623"              # 32 Pad Kit Rock.adg
BASS_URI    = "query:Sounds#Bass:FileId_49654"        # 101 Essential Bass.adg
PAD_URI     = "query:Sounds#Pad:FileId_45564"         # 5ths Glass Motion Pad.adv
STRINGS_URI = "query:Sounds#Pad:FileId_45565"
LEAD_URI    = "query:Sounds#Synth%20Lead:FileId_50175"  # A Date With Analog.adv

FX_REVERB    = "query:AudioFx#Reverb"
FX_DELAY     = "query:AudioFx#Delay"
FX_ECHO      = "query:AudioFx#Echo"
FX_FDELAY    = "query:AudioFx#Filter%20Delay"
FX_EQ8       = "query:AudioFx#EQ%20Eight"
FX_COMP      = "query:AudioFx#Compressor"
FX_AFILTER   = "query:AudioFx#Auto%20Filter"
FX_DRUMBUSS  = "query:AudioFx#Drum%20Buss"
FX_SATURATOR = "query:AudioFx#Saturator"
FX_UTILITY   = "query:AudioFx#Utility"

# (track name, instrument URI, [effect URIs in chain order])
TRACKS = [
    ("DRUMS",   DRUMS_URI,  [FX_DRUMBUSS]),                  # punch + drive
    ("BASS",    BASS_URI,   [FX_EQ8, FX_COMP]),              # clean low end
    ("SUB",     BASS_URI,   [FX_AFILTER, FX_SATURATOR]),     # dark LP = sub octave feel
    ("CHORDS",  PAD_URI,    [FX_DELAY, FX_UTILITY]),         # dub stab echoes
    ("PADS",    STRINGS_URI, [FX_REVERB]),                   # wash
    ("MELODY",  LEAD_URI,   [FX_DELAY, FX_REVERB]),          # dub delay throws
    ("FX/PERC", DRUMS2_URI, [FX_FDELAY, FX_REVERB]),         # the dub cannon
]

# Post-load device tweaks: track -> [(device_index, param_name_substr, value)]
# Values are set within the device's real [min, max] via get_device_parameters.
DEVICE_TWEAKS = {
    2: [(1, "Frequency", 0.06)],               # SUB Auto Filter: very dark
    3: [(1, "Feedback", 0.62), (1, "Dry/Wet", 0.35)],   # CHORDS Delay: dub repeats
    5: [(1, "Feedback", 0.55), (1, "Dry/Wet", 0.30)],   # MELODY Delay
    6: [(1, "Feedback", 0.72), (1, "Dry/Wet", 0.45)],   # FX Filter Delay: cannon
}


# ─── 5-minute dub structure: (name, bars) — 96 bars @ 75 BPM ≈ 5:07 ────────
SCENES = [
    ("INTRO",     12),   # space, filter opening, echo chamber
    ("GROOVE",    16),   # steppers + bassline roots
    ("BUILD",      8),   # hats 16ths, tension
    ("DROP",      24),   # one-drop binghi, maximum echo
    ("BREAKDOWN", 16),   # drums stripped, dub hole
    ("JUMP",       8),   # groove returns, resonator peak
    ("OUTRO",     12),   # filter down, echo decay, fade
]


def note(pitch, start_beat, dur=1.0, vel=100):
    return {"pitch": pitch, "start": float(start_beat), "duration": float(dur), "velocity": vel}


def loop(bar_pattern, bars, loop_beats=4.0, start_bar=0):
    """Repeat a 1-bar (or N-bar) pattern over `bars` bars of a clip.

    Notes whose tail would exceed the clip length are pruned so every clip
    stays exactly its section length (no overflow past the end).
    """
    out = []
    base = start_bar * 4.0
    clip_end = bars * 4.0
    n_loops = int(bars * 4.0 // loop_beats)
    for L in range(max(n_loops, 1)):
        for n in bar_pattern:
            start = n["start"] + base + L * loop_beats
            if start + n["duration"] > clip_end + 1e-6:
                continue
            d = dict(n)
            d["start"] = start
            out.append(d)
    return out


# ─────────────────────────── per-section music ──────────────────────────────

# (voice, hit-beat, velocity) 1-bar drum schemes keyed by scene name
DRUM_1BAR = {
    "INTRO": [  # sparse one-drop, soft
        (DRUM_KICK, 0.0, 90), (DRUM_SNARE, 2.0, 70), (DRUM_RIM, 3.0, 60),
        (DRUM_HAT_C, 1.0, 45), (DRUM_HAT_C, 3.0, 40),
    ],
    "GROOVE": [  # steppers
        (DRUM_KICK, 0.0, 105), (DRUM_KICK, 2.0, 100),
        (DRUM_SNARE, 1.0, 88), (DRUM_SNARE, 3.0, 84),
        (DRUM_HAT_C, 0.5, 55), (DRUM_HAT_C, 1.5, 55), (DRUM_HAT_C, 2.5, 55), (DRUM_HAT_C, 3.5, 52),
        (DRUM_RIM, 2.5, 45), (DRUM_SNARE, 3.5, 40),  # ghost
    ],
    "BUILD": [  # four-on-floor, hats speed up
        (DRUM_KICK, 0.0, 108), (DRUM_KICK, 1.0, 104), (DRUM_KICK, 2.0, 108), (DRUM_KICK, 3.0, 104),
        (DRUM_RIM, 1.0, 70), (DRUM_RIM, 3.0, 65),
        (DRUM_HAT_C, 0.0, 60), (DRUM_HAT_C, 0.5, 58), (DRUM_HAT_C, 1.0, 60), (DRUM_HAT_C, 1.5, 58),
        (DRUM_HAT_C, 2.0, 60), (DRUM_HAT_C, 2.5, 58), (DRUM_HAT_C, 3.0, 60), (DRUM_HAT_C, 3.5, 62),
        (DRUM_HAT_O, 3.5, 55),
    ],
    "DROP": [  # one-drop binghi with clave
        (DRUM_KICK, 0.0, 118), (DRUM_SNARE, 2.0, 100),
        (DRUM_HAT_C, 0.5, 60), (DRUM_HAT_C, 1.5, 60), (DRUM_HAT_C, 2.5, 60), (DRUM_HAT_C, 3.5, 60),
        (DRUM_CLAP, 2.0, 70), (DRUM_PERC, 2.5, 55), (DRUM_RIM, 3.5, 50),
    ],
    "BREAKDOWN": [  # no drums — rim/shaker ghosts only
        (DRUM_RIM, 1.0, 38), (DRUM_RIM, 3.0, 35),
    ],
    "JUMP": [  # steppers + energy
        (DRUM_KICK, 0.0, 112), (DRUM_KICK, 2.0, 108),
        (DRUM_SNARE, 1.0, 95), (DRUM_SNARE, 3.0, 90),
        (DRUM_HAT_C, 0.0, 62), (DRUM_HAT_C, 0.75, 60), (DRUM_HAT_C, 1.0, 62), (DRUM_HAT_C, 1.75, 60),
        (DRUM_HAT_C, 2.0, 62), (DRUM_HAT_C, 2.75, 60), (DRUM_HAT_C, 3.0, 62), (DRUM_HAT_C, 3.75, 64),
        (DRUM_CLAP, 1.0, 72), (DRUM_CLAP, 3.0, 70),
    ],
    "OUTRO": [  # fade — reduced velocities
        (DRUM_KICK, 0.0, 72), (DRUM_SNARE, 2.0, 55),
        (DRUM_HAT_C, 1.0, 35), (DRUM_HAT_C, 3.0, 32),
    ],
}

# Bass 1-bar (root 8ths, C minor) — pitch, beat, dur, vel
BASS_1BAR = {
    "INTRO":    [(C2, 0.0, 1.0, 78), (C2, 2.0, 1.0, 70)],
    "GROOVE":   [(C2, 0.0, 0.5, 92), (C2, 0.5, 0.5, 80), (C2, 1.5, 0.5, 78),
                 (F2, 2.0, 0.5, 90), (F2, 2.5, 0.5, 78), (G2, 3.5, 0.5, 74)],
    "BUILD":    [(C2, 0.0, 0.5, 100), (C2, 0.5, 0.5, 95), (C2, 1.0, 0.5, 95), (C2, 1.5, 0.5, 90),
                 (G2, 2.0, 0.5, 98), (G2, 2.5, 0.5, 92), (C2, 3.5, 0.5, 96)],
    "DROP":     [(C2, 0.0, 0.5, 104), (C2, 0.5, 0.5, 98), (F2, 1.5, 0.75, 96), (G2, 2.5, 0.5, 98),
                 (C2, 3.0, 0.5, 104), (C2, 3.5, 0.5, 96)],
    "BREAKDOWN": [(F2, 0.0, 3.0, 66), (G2, 2.0, 2.0, 58)],   # sustained drone
    "JUMP":     [(C2, 0.0, 0.5, 100), (C2, 1.0, 0.5, 96), (F2, 2.0, 0.5, 100), (G2, 3.0, 0.5, 96)],
    "OUTRO":    [(C2, 0.0, 4.0, 70)],                       # long root fade
}

# Sub 2-bar (root reinforcement, octave-down feel via pitch)
SUB_2BAR = {
    "INTRO":    [(24, 0.0, 4.0, 62), (24, 4.0, 4.0, 58)],   # C1
    "GROOVE":   [(24, 0.0, 2.0, 70), (29, 2.0, 2.0, 64)],   # F1
    "BUILD":    [(24, 0.0, 2.0, 74), (31, 4.0, 2.0, 70)],   # G1
    "DROP":     [(24, 0.0, 1.0, 80), (24, 2.0, 1.0, 76), (29, 4.0, 1.0, 78), (31, 6.0, 1.0, 72)],
    "BREAKDOWN": [(24, 0.0, 8.0, 56)],
    "JUMP":     [(24, 0.0, 1.5, 76), (29, 4.0, 1.5, 72)],
    "OUTRO":    [(24, 0.0, 8.0, 50)],
}

# Chords: 2-bar harmony (Cm7 / Fm7 / Gm7 / Abmaj?)
CHORD_2BAR = {
    "INTRO":    [(C3, 0.0, 3.5, 62), (Eb3, 0.0, 3.5, 58), (G3, 0.0, 3.5, 55), (Bb3, 0.0, 3.5, 52)],
    "GROOVE":   [(C3, 0.0, 1.0, 68), (Eb3, 0.0, 1.0, 64), (G3, 0.0, 1.0, 60), (Bb3, 0.0, 1.0, 56),
                 (F3, 2.0, 1.0, 66), (51, 2.0, 1.0, 62), (C4, 2.0, 1.0, 58)],
    "BUILD":    [(G3, 0.0, 0.5, 76), (Bb3, 0.0, 0.5, 72), (D4, 0.0, 0.5, 68),
                 (F3, 1.0, 0.5, 74), (51, 1.0, 0.5, 70), (C4, 1.0, 0.5, 66),
                 (G3, 2.0, 0.5, 78), (Bb3, 2.0, 0.5, 74), (D4, 2.0, 0.5, 70),
                 (F3, 3.0, 0.5, 76), (51, 3.0, 0.5, 72), (C4, 3.0, 0.5, 68)],
    "DROP":     [(C3, 0.0, 3.5, 74), (Eb3, 0.0, 3.5, 70), (G3, 0.0, 3.5, 66), (Bb3, 0.0, 3.5, 62),
                 (F3, 4.0, 3.5, 72), (51, 4.0, 3.5, 68), (C4, 4.0, 3.5, 64)],
    "BREAKDOWN": [(F3, 0.0, 3.0, 60), (51, 0.0, 3.0, 56), (C4, 0.0, 3.0, 52),
                  (G3, 4.0, 3.0, 58), (Bb3, 4.0, 3.0, 54), (D4, 4.0, 3.0, 50)],
    "JUMP":     [(C3, 0.0, 1.0, 72), (Eb3, 0.0, 1.0, 68), (G3, 0.0, 1.0, 64), (Bb3, 0.0, 1.0, 60),
                 (F3, 2.0, 1.0, 70), (51, 2.0, 1.0, 66), (C4, 2.0, 1.0, 62)],
    "OUTRO":    [(C3, 0.0, 3.5, 52), (Eb3, 0.0, 3.5, 48), (G3, 0.0, 3.5, 45), (Bb3, 0.0, 3.5, 42)],
}

# Pads: sustained whole-bar chord voicings (air in build/drop = None)
PAD_1BAR = {
    "INTRO":    [(C3, 0.0, 4.0, 40), (G3, 0.0, 4.0, 38), (C4, 0.0, 4.0, 35)],
    "GROOVE":   [(F3, 0.0, 4.0, 42), (C4, 0.0, 4.0, 40), (Eb4, 0.0, 4.0, 36)],
    "BREAKDOWN": [(G3, 0.0, 4.0, 44), (Bb3, 0.0, 4.0, 42), (D4, 0.0, 4.0, 38)],
    "OUTRO":    [(C3, 0.0, 4.0, 34), (G3, 0.0, 4.0, 32), (C4, 0.0, 4.0, 30)],
}

# Melody: pentatonic licks (sparse)
MELODY_2BAR = {
    "GROOVE":   [(G4, 2.5, 0.5, 70), (Bb4, 3.0, 0.5, 66), (C5, 3.5, 0.5, 62),
                 (G4, 6.0, 1.0, 60)],
    "BUILD":    [(Eb4, 3.0, 0.25, 74), (G4, 3.25, 0.25, 70), (Bb4, 3.5, 0.25, 66), (C5, 3.75, 0.5, 64)],
    "DROP":     [(G4, 2.5, 0.5, 78), (Bb4, 3.0, 0.5, 74), (C5, 3.5, 0.75, 70),
                 (Bb4, 6.0, 0.5, 68), (G4, 6.5, 0.5, 66), (F4, 7.0, 0.5, 64)],
    "JUMP":     [(C5, 2.0, 0.5, 76), (Bb4, 2.5, 0.5, 72), (G4, 3.0, 1.0, 68)],
}

# FX: dub echo throws + perc accents at section pivots (loop over section)
FX_2BAR = {
    "INTRO":    [(DRUM_RIM, 7.0, 0.25, 70), (62, 7.25, 0.25, 66)],
    "GROOVE":   [(62, 7.5, 0.25, 64), (DRUM_PERC, 3.5, 0.25, 60)],
    "BUILD":    [(63, 7.0, 0.5, 72)],
    "DROP":     [(62, 7.75, 0.5, 74), (DRUM_PERC, 3.5, 0.25, 66)],
    "BREAKDOWN": [(63, 7.0, 1.0, 68)],
    "JUMP":     [(64, 7.5, 0.5, 70)],
    "OUTRO":    [(62, 7.0, 0.5, 50)],
}


class AbletonClient:
    """TCP client for the Ableton Remote Script."""

    def __init__(self, host="localhost", port=9877):
        self.host, self.port = host, port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERR] cannot connect to {self.host}:{self.port}: {e}")
            return False

    def send(self, cmd, params=None):
        if self.sock is None and not self.connect():
            return {"status": "error"}
        msg = json.dumps({"type": cmd, "params": params or {}}).encode() + b"\n"
        try:
            self.sock.sendall(msg)
            raw = self.sock.recv(262144).decode()
            return json.loads(raw) if raw else {"status": "ok"}
        except Exception as e:
            print(f"[ERR] {cmd}: {e}")
            self.sock = None
            return {"status": "error"}

    def send_checked(self, cmd, params=None, what=""):
        """Send and RAISE on error status - silent failures are how instruments
        get 'forgotten'. Every load/create MUST pass through here."""
        r = self.send(cmd, params)
        status = r.get("status") if isinstance(r, dict) else None
        if status != "success":
            raise RuntimeError(f"{what or cmd} failed: {json.dumps(r)[:220]}")
        return r

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


class DubFiveMin:
    def __init__(self, client):
        self.c = client
        self.n_scenes = len(SCENES)

    # ── track/model helpers ───────────────────────────────────────────────
    def create_track(self, idx, name, instrument_uri, effect_uris):
        print(f"  track {idx}: {name}")
        self.c.send_checked("create_midi_track", {"index": idx}, f"create track {name}")
        time.sleep(0.15)
        self.c.send("set_track_name", {"track_index": idx, "name": name})
        # instrument
        self.c.send_checked("load_browser_item",
                            {"track_index": idx, "item_uri": instrument_uri},
                            f"load instrument {instrument_uri}")
        time.sleep(0.6)
        # effects (appended to device chain in order)
        for fx in effect_uris:
            self.c.send_checked("load_browser_item",
                                {"track_index": idx, "item_uri": fx},
                                f"load effect {fx}")
            time.sleep(0.5)
        # verify device chain
        n_expected = 1 + len(effect_uris)
        n_got = self._device_count(idx)
        if n_got < n_expected:
            raise RuntimeError(
                f"{name}: expected {n_expected} devices, found {n_got} - load failed")
        print(f"    devices: {n_got}/{n_expected} OK")

    def _device_count(self, track_idx):
        r = self.c.send("get_track_info", {"track_index": track_idx})
        devs = r.get("result", {}).get("devices")
        return len(devs) if isinstance(devs, list) else -1

    def _param_map(self, track_idx, device_idx):
        """{lowercase param name: (index, min, max, current)} for a device."""
        r = self.c.send("get_device_parameters",
                      {"track_index": track_idx, "device_index": device_idx})
        params = r.get("result", {}).get("parameters") or []
        out = {}
        for i, p in enumerate(params):
            if isinstance(p, dict):
                nm = str(p.get("name", "")).lower()
                out[nm] = (i, float(p.get("min", 0.0)), float(p.get("max", 1.0)),
                           p.get("value", p.get("real_value", 0.0)))
        return out

    def apply_device_tweaks(self):
        """Set dub-critical device params, mapped into each param's real range."""
        for track_idx, tweaks in DEVICE_TWEAKS.items():
            for device_idx, name_substr, frac in tweaks:
                pmap = self._param_map(track_idx, device_idx)
                if not pmap:
                    print(f"    [warn] no params on track {track_idx} dev {device_idx}")
                    continue
                hit = pmap.get(name_substr.lower())
                if hit is None:
                    for nm, spec in pmap.items():
                        if name_substr.lower() in nm:
                            hit = spec
                            break
                if hit is None:
                    print(f"    [warn] {name_substr!r} not on track {track_idx} "
                          f"dev {device_idx} (has {sorted(pmap)[:6]})")
                    continue
                i, lo, hi, _cur = hit
                value = lo + (hi - lo) * frac
                self.c.send("set_device_parameter",
                            {"track_index": track_idx, "device_index": device_idx,
                             "parameter_index": i, "value": value})
            print(f"  tweaks applied: track {track_idx}")

    def add_clip(self, track_idx, clip_idx, length_beats, notes):
        self.c.send("create_clip", {"track_index": track_idx, "clip_index": clip_idx,
                                    "length": float(length_beats)})
        time.sleep(0.06)
        if notes:
            self.c.send("add_notes_to_clip", {"track_index": track_idx,
                                              "clip_index": clip_idx, "notes": notes})

    # ── music assembly per track ──────────────────────────────────────────
    def drums_notes(self, scene_name, bars):
        pat = DRUM_1BAR.get(scene_name)
        if not pat:
            return []
        return [note(p, b, 0.2 if p >= 40 else 0.35, v) for p, b, v in pat]

    def bass_notes(self, scene_name, bars):
        pat = BASS_1BAR.get(scene_name)
        if not pat:
            return []
        fig = [note(p, b, d, v) for p, b, d, v in pat]
        return loop(fig, bars)

    def sub_notes(self, scene_name, bars):
        pat = SUB_2BAR.get(scene_name)
        if not pat:
            return []
        fig = [note(p, b, d, v) for p, b, d, v in pat]
        return loop(fig, bars, loop_beats=8.0)

    def chords_notes(self, scene_name, bars):
        pat = CHORD_2BAR.get(scene_name)
        if not pat:
            return []
        fig = [note(p, b, d, v) for p, b, d, v in pat]
        return loop(fig, bars, loop_beats=8.0)

    def pads_notes(self, scene_name, bars):
        pat = PAD_1BAR.get(scene_name)
        if not pat:
            return []
        fig = [note(p, b, d, v) for p, b, d, v in pat]
        return loop(fig, bars)

    def melody_notes(self, scene_name, bars):
        pat = MELODY_2BAR.get(scene_name)
        if not pat:
            return []
        fig = [note(p, b, d, v) for p, b, d, v in pat]
        return loop(fig, bars, loop_beats=8.0)

    def fx_notes(self, scene_name, bars):
        pat = FX_2BAR.get(scene_name)
        if not pat:
            return []
        fig = [note(p, b, d, v) for p, b, d, v in pat]
        return loop(fig, bars, loop_beats=8.0)

    # ── build ─────────────────────────────────────────────────────────────
    def build(self):
        c = self.c
        print("Building 5-minute dub tape version…")

        c.send("stop_playback")
        c.send("delete_all_tracks")
        time.sleep(0.6)

        print("[tempo] 75 BPM")
        c.send("set_tempo", {"bpm": 75.0})

        print("[tracks] 7 MIDI tracks + instruments + effects")
        for i, (name, uri, fx) in enumerate(TRACKS):
            self.create_track(i, name, uri, fx)

        print("[devices] dub tweaks (filter darkness, delay feedback)")
        self.apply_device_tweaks()

        print("[scenes] creating %d scenes" % self.n_scenes)
        for i in range(self.n_scenes):
            c.send("create_scene", {"index": i})
            c.send("set_scene_name", {"scene_index": i, "name": SCENES[i][0]})
        time.sleep(0.3)

        # Drums track
        print("[clips] DRUMS")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(0, si, sbars * 4, self.drums_notes(sname, sbars))
        # BASS
        print("[clips] BASS")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(1, si, sbars * 4, self.bass_notes(sname, sbars))
        # SUB
        print("[clips] SUB")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(2, si, sbars * 4, self.sub_notes(sname, sbars))
        # CHORDS
        print("[clips] CHORDS")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(3, si, sbars * 4, self.chords_notes(sname, sbars))
        # PADS
        print("[clips] PADS")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(4, si, sbars * 4, self.pads_notes(sname, sbars))
        # MELODY
        print("[clips] MELODY")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(5, si, sbars * 4, self.melody_notes(sname, sbars))
        # FX
        print("[clips] FX/PERC")
        for si, (sname, sbars) in enumerate(SCENES):
            self.add_clip(6, si, sbars * 4, self.fx_notes(sname, sbars))

        print("[mix] levels, pans, dub sends")
        self._set_mix()

        print("[follow] chaining scenes for auto-play")
        self._chain_follow_actions()

    def _set_mix(self):
        # volume, pan (0=left, .5=center, 1=right)
        mix = {
            0: (0.78, 0.50),   # DRUMS
            1: (0.68, 0.50),   # BASS
            2: (0.55, 0.50),   # SUB
            3: (0.52, 0.56),   # CHORDS
            4: (0.44, 0.44),   # PADS
            5: (0.56, 0.55),   # MELODY
            6: (0.50, 0.46),   # FX
        }
        for t, (vol, pan) in mix.items():
            self.c.send("set_track_volume", {"track_index": t, "volume": vol})
            self.c.send("set_track_pan", {"track_index": t, "pan": pan})
        # send 0 = reverb, send 1 = delay (normalized 0-1)
        sends = {
            0: (0.10, 0.06),   # drums: light verb + tiny delay slap
            1: (0.00, 0.12),   # bass: no verb, some delay
            2: (0.00, 0.00),   # sub: clean
            3: (0.24, 0.10),   # chords
            4: (0.40, 0.14),   # pads (wash)
            5: (0.20, 0.22),   # melody (dub delay)
            6: (0.35, 0.30),   # fx (maximum echo)
        }
        for t, (rv, dl) in sends.items():
            self.c.send("set_send_amount", {"track_index": t, "send_index": 0, "amount": rv})
            self.c.send("set_send_amount", {"track_index": t, "send_index": 1, "amount": dl})

    def _chain_follow_actions(self):
        """Every clip fires the next scene's clip when it ends (Other action).

        On the last scene, stop. Non-strict: best-effort, non-fatal on error.
        """
        for track_idx in range(len(TRACKS)):
            for si in range(self.n_scenes):
                target = si + 1 if si < self.n_scenes - 1 else None
                if target is None:
                    action_type = 1      # stop
                    clip_target = si
                else:
                    action_type = 6      # other/fold → jump to clip_target
                    clip_target = target
                self.c.send("set_clip_follow_action", {
                    "track_index": track_idx,
                    "clip_index": si,
                    "action_slot": 0,
                    "action_type": action_type,
                    "trigger_time": 0,   # when clip ends/loops
                    "clip_index_target": clip_target,
                })

    # ── optional: real-time capture into Arrangement (~5 min) ─────────────
    def capture(self):
        c = self.c
        c.send("set_playhead_position", {"bar": 0, "beat": 0})
        # arm all tracks + record
        c.send("start_recording")
        c.send("start_playback")
        c.send("trigger_scene", {"scene_index": 0})
        bpm = 75.0
        for si, (sname, sbars) in enumerate(SCENES):
            dur = sbars * 4 * (60.0 / bpm)
            pct = (si + 1) / self.n_scenes * 100
            print(f"  [{pct:3.0f}%] {sname}: {dur:.1f}s")
            time.sleep(dur)
            if si < self.n_scenes - 1:
                c.send("trigger_scene", {"scene_index": si + 1})
        time.sleep(1.0)
        c.send("stop_recording")
        c.send("stop_playback")
        print("[arrangement] captured ~5:07")


def main():
    ap = argparse.ArgumentParser(description="Prepare a 5-minute dub tape version")
    ap.add_argument("--capture", action="store_true",
                    help="also real-time record into Arrangement (~5 min, Live must play)")
    args = ap.parse_args()

    c = AbletonClient()
    if not c.connect():
        print("\nStart Ableton Live with the MCP Remote Script (TCP 9877) first.")
        sys.exit(1)

    dub = DubFiveMin(c)
    dub.build()

    total_bars = sum(b for _, b in SCENES)
    print(f"\nReady: {total_bars} bars @ 75 BPM ≈ {total_bars * 4 * 60 / 75 / 60:.2f} min")
    print("Fire scene 0 (INTRO) — follow actions chain through all 7 sections.")
    print("Sections: " + " -> ".join(n for n, _ in SCENES))

    if args.capture:
        print("\nRecording into Arrangement… (let it run, do not touch Live)")
        dub.capture()

    c.close()


if __name__ == "__main__":
    main()
