#!/usr/bin/env python3
"""
Prepare a 5-minute dub tape version in Ableton Live.

Builds a 7-section dub mix (96 bars @ 75 BPM ≈ 5:07) with structured clips
and follow-action chaining: fire scene 0 (INTRO) once and the whole track
plays through: INTRO → GROOVE → BUILD → DROP → BREAKDOWN → JUMP → OUTRO.

Musical features baked in:
  * section-final drum fills (16th snare-roll crescendos)
  * pre-drop dropout: BUILD last bar is silent in BASS/SUB/CHORDS/PADS so
    only drums roll and the MELODY/FX riser keeps climbing into the drop
  * offbeat skank chords in GROOVE/JUMP, layered skank in DROP
  * 8-bar A/B bass phrases with walk-ups C→D→Eb→F→G
  * melody call-and-answer phrasing + BUILD pentatonic riser run
  * deterministic velocity jitter for humanisation

Modes:
  (default)        auto: reuse existing 7 dub tracks if present; else full build
  --fresh          force full rebuild (delete all tracks + reload instruments)
  --clips-only     refuse to touch tracks/devices; rebuild clips, names,
                   mix, tweaks, follow actions only
  --arrange        ALSO lay the whole Arrangement out into Ableton's
                   Arrangement View via fast per-section capture (~45 s)
  --capture        ALSO real-time record into Arrangement (~5:07)

Protocol: TCP JSON {"type": cmd, "params": {...}} to the Remote Script (port 9877).
"""

import argparse
import json
import socket
import sys
import time


# ─── MIDI pitch constants ────────────────────────────────────────────────
DRUM_KICK   = 36
DRUM_SNARE  = 38
DRUM_CLAP   = 39
DRUM_RIM    = 37
DRUM_HAT_C  = 42
DRUM_HAT_O  = 46
DRUM_PERC   = 56          # cowbell / woodblock zone on the drum kits
D4 = 62

# Bass / sub octave
C1, F1, G1 = 24, 29, 31
C2 = 36
D2 = 38
Eb2 = 39
F2 = 41
G2 = 43
Ab2 = 44

# Mid chords / pads
C3 = 48
Eb3 = 51
F3 = 53
G3 = 55
Bb3 = 58
Ab3 = 56  # needed for FM7 voicing
D4 = 62

# Melody / FX
C4, Eb4, F4, G4, Bb4 = 60, 63, 65, 67, 70
C5, Eb5, F5, G5 = 72, 75, 77, 79

# Chord voicings
CM7 = (C3, Eb3, G3, Bb3)
FM7 = (F3, Ab3, C4, Eb4)
GM7 = (G3, Bb3, D4, F4)
ABMJ = (Ab3, C4, Eb4)        # Ab major triad
PAD_CM = (C3, G3, C4)
PAD_FM = (F3, C4, Eb4)
PAD_GM = (G3, Bb3, D4)

# Verified browser URIs (resolved live via get_browser_item)
DRUMS_URI   = "query:Drums#FileId_58622"                 # 32 Pad Kit Jazz
DRUMS2_URI  = "query:Drums#FileId_58623"                 # 32 Pad Kit Rock
BASS_URI    = "query:Sounds#Bass:FileId_49654"           # 101 Essential Bass
PAD_URI     = "query:Sounds#Pad:FileId_45564"            # 5ths Glass Motion Pad
STRINGS_URI = "query:Sounds#Pad:FileId_45565"            # Analog Slow Sweep
LEAD_URI    = "query:Sounds#Synth%20Lead:FileId_50175"   # A Date With Analog

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

# Track specification: (name, instrument URI, [effect URIs in chain order])
TRACKS = [
    ("DRUMS",   DRUMS_URI,  [FX_DRUMBUSS]),
    ("BASS",    BASS_URI,   [FX_EQ8, FX_COMP]),
    ("SUB",     BASS_URI,   [FX_AFILTER, FX_SATURATOR]),
    ("CHORDS",  PAD_URI,    [FX_DELAY, FX_UTILITY]),
    ("PADS",    STRINGS_URI, [FX_REVERB]),
    ("MELODY",  LEAD_URI,   [FX_DELAY, FX_REVERB]),
    ("FX/PERC", DRUMS2_URI, [FX_FDELAY, FX_REVERB]),
]

# Post-load device tweaks: track -> [(device_index, param_name_substr, fraction)]
DEVICE_TWEAKS = {
    2: [(1, "Frequency", 0.06)],                # SUB Auto Filter: very dark
    3: [(1, "Feedback", 0.62), (1, "Dry/Wet", 0.35)],  # CHORDS Delay
    5: [(1, "Feedback", 0.55), (1, "Dry/Wet", 0.30)],  # MELODY Delay
    6: [(1, "Feedback", 0.72), (1, "1 Filter Freq", 0.45)],  # FX Filter Delay
}

# ─── 5-minute dub structure: (name, bars) — 96 bars @ 75 BPM ≈ 5:07 ───── 
SCENES = [
    ("INTRO",     12),   # space, filter opening, echo chamber
    ("GROOVE",    16),   # steppers + skank chords + call/response melody
    ("BUILD",      8),   # hats double-time, bass drive, riser climax
    ("DROP",      24),   # one-drop, layered skank, melodic hook, fills
    ("BREAKDOWN", 16),   # stripped percussion, dub hole, evolving texturing
    ("JUMP",       8),   # groove returns, energetic skank, melodic answer
    ("OUTRO",     12),   # fade-out: velocities descrescendo into silence
]


# ──────────────────────────── Helpers ──────────────────────────────────

def note(pitch, start_beat, duration, velocity):
    return {"pitch": int(pitch), "start": float(start_beat),
            "duration": float(duration), "velocity": int(velocity)}


# Deterministic velocity jitter cylinder (16 values so short loops still vary)
_JITTER = (3, -2, 4, -1, 2, -4, 1, 3, -3, 2, 5, -1, 2, -3, 4, -2)

def _j(v, idx):
    """Jitter a velocity value ±max(4) deterministically."""
    return max(1, min(126, int(v + _JITTER[idx % len(_JITTER)])))


def bar_hits(hits, bar=0):
    """Convert hits (beat, pitch, vel, dur) inside a single bar into note
    dicts offset by `bar` (in bars) and with jitter applied.
    Notes that would end after bar+1 are clipped to the bar boundary so
    every clip stays exactly its section length (guaranteedfit)."""
    out = []
    clip_end = (bar + 1) * 4.0
    for k, (b, p, v, d) in enumerate(hits):
        s = bar * 4.0 + b
        if s + d > clip_end + 1e-9:
            # Trim duration instead of skipping so we keep the rhythm
            d = clip_end - s
            if d <= 0:
                continue
        jv = _j(v, k + bar * 7)
        out.append(note(p, s, d, jv))
    return out


def hits_at(hits, start_beat, seed=0):
    """Stamps a sequence of (beat, pitch, vel, dur) hits so that their
    first beat lands at `start_beat` (absolute, in beats).
    Use for motifs that span multiple bars."""
    return [note(p, start_beat + b, d, _j(v, seed + int(b * 3)))
            for b, p, v, d in hits
            if d > 0]


def loop_clip(bar_pattern, bars, loop_beats=4.0):
    """Repeat a pattern that fits in `loop_beats` over `bars` bars
    (destructively inverted to not clip at ends).
    Falls back to a single bar if the pattern is shorter.
    No jitter – caller or pattern builder must randomise."""
    out = []
    clip_end = bars * 4.0
    n_loops = max(int(bars * 4.0 // loop_beats), 1)
    for L in range(n_loops):
        offset = L * loop_beats
        for n in bar_pattern:
            s = n["start"] + offset
            if s + n["duration"] > clip_end + 1e-6:
                continue
            d = dict(n)
            d["start"] = s
            out.append(d)
    return out


# ──────────────────── Phrase / motif patterns ───────────────────────────

DR_SPARSE = [               # INTRO / OUTRO base groove - sparse one-drop
    (0.0, DRUM_KICK, 90, 0.35), (2.0, DRUM_SNARE, 70, 0.2),
    (1.0, DRUM_HAT_C, 45, 0.1), (3.0, DRUM_HAT_C, 40, 0.1),
]

DR_GROOVE = [                 # Steppers, ghost snare, skank hats
    (0.0, DRUM_KICK, 105, 0.35), (2.0, DRUM_KICK, 100, 0.35),
    (1.0, DRUM_SNARE, 88, 0.2), (3.0, DRUM_SNARE, 84, 0.2),
    (0.5, DRUM_HAT_C, 55, 0.1), (1.5, DRUM_HAT_C, 55, 0.1),
    (2.5, DRUM_HAT_C, 55, 0.1), (3.5, DRUM_HAT_C, 52, 0.1),
    (2.5, DRUM_RIM, 45, 0.1), (3.5, DRUM_SNARE, 40, 0.1),
]

DR_ONEDROP = [                # Binghi one-drop
    (0.0, DRUM_KICK, 118, 0.35), (2.0, DRUM_SNARE, 100, 0.2),
    (0.5, DRUM_HAT_C, 60, 0.1), (1.5, DRUM_HAT_C, 60, 0.1),
    (2.5, DRUM_HAT_C, 60, 0.1), (3.5, DRUM_HAT_C, 60, 0.1),
    (2.0, DRUM_CLAP, 70, 0.20), (2.5, DRUM_PERC, 55, 0.15),
    (3.5, DRUM_RIM, 50, 0.10),
]

DR_FOUR = [                   # BUILD: four-on-floor with heavy hats
    (0.0, DRUM_KICK, 108, 0.35), (1.0, DRUM_KICK, 104, 0.35),
    (2.0, DRUM_KICK, 108, 0.35), (3.0, DRUM_KICK, 104, 0.35),
    (1.0, DRUM_RIM, 70, 0.10), (3.0, DRUM_RIM, 65, 0.10),
    (0.0,  DRUM_HAT_C, 58, 0.08), (0.5, DRUM_HAT_C, 55, 0.08),
    (1.0,  DRUM_HAT_C, 58, 0.08), (1.5, DRUM_HAT_C, 55, 0.08),
    (2.0,  DRUM_HAT_C, 58, 0.08), (2.5, DRUM_HAT_C, 55, 0.08),
    (3.0,  DRUM_HAT_C, 58, 0.08), (3.5, DRUM_HAT_O, 55, 0.10),
]

DR_BD_HATS = [                # BREAKDOWN mids (8th-note hats layered)
    (1.0, DRUM_RIM, 38, 0.1), (3.0, DRUM_RIM, 35, 0.1),
    (0.0, DRUM_HAT_C, 45, 0.08), (0.5, DRUM_HAT_C, 48, 0.08),
    (1.0, DRUM_HAT_C, 45, 0.08), (1.5, DRUM_HAT_C, 48, 0.08),
    (2.0, DRUM_HAT_C, 50, 0.08), (2.5, DRUM_HAT_C, 52, 0.08),
    (3.0, DRUM_HAT_C, 50, 0.08), (3.5, DRUM_HAT_C, 52, 0.08),
]

DR_BD_FULL = [                # BREAKDOWN fuller (kick + snare rejoin)
    (0.0, DRUM_KICK, 95, 0.35), (2.0, DRUM_SNARE, 77, 0.20),
    (0.0, DRUM_HAT_C, 52, 0.08), (0.5, DRUM_HAT_C, 55, 0.08),
    (1.0, DRUM_HAT_C, 52, 0.08), (1.5, DRUM_HAT_C, 55, 0.08),
    (2.0, DRUM_HAT_C, 52, 0.08), (2.5, DRUM_HAT_C, 55, 0.08),
    (3.0, DRUM_HAT_C, 52, 0.08), (3.5, DRUM_HAT_C, 54, 0.08),
]

DR_JUMP = [                   # Energetic steppers with triplets feel
    (0.0, DRUM_KICK, 112, 0.35), (2.0, DRUM_KICK, 108, 0.35),
    (1.0, DRUM_SNARE, 95, 0.20), (3.0, DRUM_SNARE, 90, 0.20),
    (0.75, DRUM_HAT_C, 60, 0.10), (1.75, DRUM_HAT_C, 60, 0.10),
    (2.75, DRUM_HAT_C, 60, 0.10), (3.75, DRUM_HAT_O, 64, 0.12),
    (1.0, DRUM_CLAP, 72, 0.15), (3.0, DRUM_CLAP, 70, 0.15),
    (3.75, DRUM_PERC, 52, 0.10),
]

DR_RIM_GHOST = [              # BREAKDOWN sparsest rim rhythms
    (1.0, DRUM_RIM, 38, 0.10), (3.0, DRUM_RIM, 35, 0.10),
]


def drum_fill(kind, bar=0, v0=45, v1=115):
    """One-bar fill Strategy.
    - kind='big':   16 sixteenth-note snare roll + kick on beat 3
    - kind='mini':  4 eighth-note snare roll @ beats 3.0–3.75 + kick on beat 3
    Each hit is individually jittered by bar_hits."""
    hits = []
    if kind == "big":
        for k in range(16):
            hits.append((k * 0.25, DRUM_SNARE, v0 + (v1 - v0) * k / 15.0, 0.10))
        hits.append((3.0, DRUM_KICK, 110, 0.35))
    else:  # mini
        for k in range(4):
            hits.append((3.0 + k * 0.25, DRUM_SNARE, v0 + (v1 - v0) * k / 3.0, 0.10))
        hits.append((3.0, DRUM_KICK, 108, 0.35))
    return bar_hits(hits, bar)


# ── Bass phrase patterns------------------------------ (beat, pitch, vel, dur)
BA_A = [(0.0, C2, 92, 0.5), (0.5, C2, 82, 0.5), (1.5, C2, 80, 0.5),
        (2.0, F2, 90, 0.5), (2.5, F2, 80, 0.5), (3.0, G2, 80, 0.5), (3.5, G2, 86, 0.5)]
BA_B = [(0.0, F2, 90, 0.5), (0.5, F2, 80, 0.5), (1.5, F2, 78, 0.5),
        (2.0, Ab2, 86, 0.5), (2.5, F2, 80, 0.5), (3.0, G2, 82, 0.5), (3.5, G2, 84, 0.5)]
BA_W = [(0.0, C2, 90, 0.5), (0.5, C2, 80, 0.5), (1.0, C2, 78, 0.5),
        (2.0, D2, 84, 0.5), (2.5, Eb2, 86, 0.5), (3.0, F2, 88, 0.5), (3.5, G2, 92, 0.5)]
BA_DRIVE = [(0.0, C2, 102, 0.5), (0.5, C2, 94, 0.5), (1.0, C2, 94, 0.5), (1.5, C2, 90, 0.5),
            (2.0, G2, 100, 0.5), (2.5, G2, 92, 0.5), (3.0, C2, 96, 0.5), (3.5, C2, 92, 0.5)]
BA_X = [(0.0, C2, 104, 0.5), (0.5, C2, 94, 0.5), (1.5, C2, 92, 0.5),
        (3.0, C2, 100, 0.5), (3.5, C2, 94, 0.5)]
BA_Y = [(0.0, F2, 100, 0.5), (0.5, F2, 90, 0.5), (1.5, F2, 88, 0.5),
        (2.0, G2, 96, 0.5), (3.0, F2, 99, 0.5), (3.5, G2, 92, 0.5)]
# Sub bass
SB_INTRO = [(0.0, C1, 60, 4.0)]
SB_GR_A  = [(0.0, C1, 70, 2.0), (2.0, C1, 68, 2.0)]
SB_GR_B  = [(0.0, F1, 68, 2.0), (2.0, G1, 66, 2.0)]
SB_BD    = [(0.0, C1, 76, 2.0), (2.0, G1, 72, 2.0)]
SB_DP1   = [(0.0, C1, 82, 1.0), (2.0, C1, 78, 1.0)]
SB_DP2   = [(0.0, F1, 80, 1.0), (2.0, G1, 76, 1.0)]
SB_DP3   = [(0.0, C1, 84, 2.0), (2.0, G1, 80, 2.0)]

# Melody motifs (beat-relative)
MEL_CALL = [(2.5, G4, 72, 0.5), (3.0, Bb4, 68, 0.5), (3.5, C5, 64, 0.75)]
MEL_ANS = [(1.5, C5, 70, 0.5), (2.0, Bb4, 66, 0.5), (2.5, G4, 64, 0.5), (3.0, F4, 60, 0.75)]
MEL_HOOK = [(2.5, G4, 80, 0.5), (3.0, Bb4, 76, 0.5), (3.5, C5, 72, 0.75),
            (6.0, Bb4, 70, 0.5), (6.5, G4, 68, 0.5), (7.0, F4, 66, 0.75)]
MEL_ANS2 = [(0.5, C5, 78, 0.5), (1.0, Bb4, 74, 0.5), (1.5, G4, 70, 1.0)]
P_RISE1 = [(k * 0.5, p, 55 + int(23 * k / 7), 0.22)
           for k, p in enumerate((C4, Eb4, F4, G4, Bb4, C5, Eb5, C5))]
P_RISE2 = [(k * 0.5, p, 68 + int(42 * k / 7), 0.22)
           for k, p in enumerate((C5, Eb5, G5, F5, Eb5, G5, F5, G5))]

# ───────── Music builders: return list of note dicts for a scene/bar-length

def drums_for(scene, bars):
    """Build drum track notes for (scene, bars)."""
    if scene == "INTRO":
        out = [bar_hits(DR_SPARSE, b) for b in range(bars)]
        # Final bar gets a tiny fill into GROOVE
        if bars:
            out[-1] += drum_fill("mini", bars - 1, 48, 85)
        return [n for bar in out for n in bar]

    elif scene == "GROOVE":
        out = [bar_hits(DR_GROOVE, b) for b in range(bars - 1)]
        out.append(bar_hits(DR_GROOVE, bars - 1) + drum_fill("big", bars - 1, 42, 118))
        return [n for bar in out for n in bar]

    elif scene == "BUILD":
        out = [bar_hits(DR_FOUR, b) for b in range(6)]
        # bar 6: four-on-floor + snare 8th-note roll 2nd half
        h6 = [(0.0, DRUM_KICK, 108, 0.35), (1.0, DRUM_KICK, 106, 0.35),
              (2.0, DRUM_KICK, 110, 0.35), (3.0, DRUM_KICK, 108, 0.35)]
        for k in range(4):
            h6.append((2.0 + k * 0.5, DRUM_SNARE, 70 + 25 * k / 3.0, 0.12))
        out.append(bar_hits(h6, 6))
        out.append(drum_fill("big", 7, 52, 120))  # bar 7 == last
        return [n for bar in out for n in bar]

    elif scene == "DROP":
        out = [bar_hits(DR_ONEDROP, b) for b in range(bars)]
        # Extra rim every bar >= 16 (except fills)
        for b in range(16, bars):
            out[b] += bar_hits([(2.75, DRUM_PERC, 62, 0.12)], b)
        # mini-fills at bar 7 and 15 (end of the first/second 8-bar phrase)
        for b in (7, 15):
            mf = bar_hits(DR_ONEDROP[:2] + \
                          [(3.0 + k * 0.25, DRUM_SNARE, 75 + 8 * k, 0.10) for k in range(4)] +
                          [(3.5, DRUM_CLAP, 80, 0.15)], b)
            out[b] = mf
        # Final bar: big fill into OUTRO
        out[-1] += drum_fill("big", bars - 1, 50, 122)
        return [n for bar in out for n in bar]

    elif scene == "BREAKDOWN":
        out = []
        for b in range(bars):
            if b < 8:
                out.append(bar_hits(DR_RIM_GHOST, b))
            elif b < 12:
                out.append(bar_hits(DR_BD_HATS, b))
            elif b < bars - 1:
                out.append(bar_hits(DR_BD_FULL, b))
            else:
                out.append(bar_hits(DR_BD_FULL, b) + drum_fill("mini", b, 40, 82))
        return [n for bar in out for n in bar]

    elif scene == "JUMP":
        out = [bar_hits(DR_JUMP, b) for b in range(bars - 1)]
        out.append(bar_hits(DR_JUMP, bars - 1) + drum_fill("mini", bars - 1, 68, 116))
        return [n for bar in out for n in bar]

    elif scene == "OUTRO":
        out = []
        for b in range(bars):
            vs = 1.0 - 0.55 * b / max(bars - 1, 1)
            hits = [(bt, p, int(v * vs), d) for bt, p, v, d in DR_SPARSE]
            out.append(bar_hits(hits, b))
        return [n for bar in out for n in bar]
    else:
        return []


def bass_for(scene, bars):
    if scene == "INTRO":
        out = [bar_hits([(0.0, C2, 1.0, 76), (2.0, C2, 1.0, 68)], b) for b in range(bars)]
    elif scene == "GROOVE" or scene == "JUMP":
        out = []
        for ph in range(bars // 4):
            base = ph * 4
            for k, pat in enumerate((BA_A, BA_A, BA_B, BA_W)):
                out.append(bar_hits(pat, base + k))
    elif scene == "BUILD":
        # BUILD always 8 bars; bar 7 silent = dropout
        out = [bar_hits(BA_DRIVE, b) for b in range(7)]
        if bars > 7:
            out.append([])
    elif scene == "DROP":
        out = []
        for ph in range(bars // 4):
            base = ph * 4
            for k, pat in enumerate((BA_X, BA_X, BA_Y, BA_W)):
                out.append(bar_hits(pat, base + k))
    elif scene == "BREAKDOWN":
        out = []
        for b in range(bars):
            if b < 8:
                out.append(bar_hits([(0.0, F2, 3.5, 64)], b))
            elif b < 12:
                out.append(bar_hits([(0.0, C2, 3.5, 68)], b))
            else:
                out.append(bar_hits([(0.0, G2, 2.0, 66), (2.0, C2, 2.0, 64)], b))
    elif scene == "OUTRO":
        out = []
        for b in range(bars):
            vs = 1.0 - 0.5 * b / max(bars - 1, 1)
            out.append(bar_hits([(0.0, C2, int(68 * vs), 4.0)], b))
    else:
        out = [[] for _ in range(bars)]
    return [n for bar in out for n in bar]


def sub_for(scene, bars):
    if scene == "INTRO":
        out = []
        for b in range(bars):
            vs = 0.75 + 0.25 * b / max(bars - 1, 1)
            out.append(bar_hits([(0.0, C1, int(60 * vs), 4.0)], b))
    elif scene == "GROOVE":
        out = [bar_hits(SB_GR_A if b % 2 == 0 else SB_GR_B, b) for b in range(bars)]
    elif scene == "BUILD":
        out = [bar_hits(SB_BD, b) for b in range(7)]
        # bar 7 silent = pre-drop dropout
    elif scene == "DROP":
        out = []
        for b in range(bars):
            k = b % 4
            if k in (0, 1):
                pat = SB_DP1
            elif k == 2:
                pat = SB_DP2
            else:
                pat = SB_DP3
            out.append(bar_hits(pat, b))
    elif scene == "BREAKDOWN":
        out = []
        for b in range(bars):
            if b < 8 and b % 2 == 0:
                out.append(bar_hits([(0.0, C1, 54, 8.0)], b))
            else:
                out.append(bar_hits([(0.0, C1, 60, 4.0)], b))
    elif scene == "JUMP":
        out = [bar_hits(SB_GR_A if b % 2 == 0 else SB_GR_B, b) for b in range(bars)]
    elif scene == "OUTRO":
        out = []
        for b in range(bars):
            vs = 1.0 - 0.4 * b / max(bars - 1, 1)
            out.append(bar_hits([(0.0, C1, int(58 * vs), 4.0)], b))
    else:
        out = [[] for _ in range(bars)]
    return [n for bar in out for n in bar]


def chords_for(scene, bars):
    out = []

    def long_chor(voicing, bar, vel):
        return bar_hits([(0.0, p, vel, 3.8) for p in voicing], bar)

    def skank(voicing, bar, vel):
        return bar_hits([(bt, p, vel, 0.22) for bt in (0.5, 1.5, 2.5, 3.5) for p in voicing], bar)

    if scene == "INTRO":
        for b in range(bars):
            out.extend(long_chor(CM7, b, 60 + int(1.2 * b)))
    elif scene == "GROOVE":
        for b in range(bars):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 74))
    elif scene == "BUILD":
        for b in range(7):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 78))
        # bar 7 silent = dropout -> nothing
    elif scene == "DROP":
        for b in range(bars):
            if b < 8:
                out.extend(long_chor(CM7 if b % 2 == 0 else FM7, b, 76))
            elif b < 16:
                v = CM7 if b % 2 == 0 else FM7
                out.extend(long_chor(v, b, 72) + skank(v, b, 66))
            else:
                v = GM7 if b % 2 == 0 else ABMJ
                out.extend(long_chor(v, b, 74) + skank(v, b, 68))
    elif scene == "BREAKDOWN":
        for b in range(bars):
            out.extend(long_chor(GM7 if b < 8 else ABMJ, b, 58 + int(0.6 * b)))
    elif scene == "JUMP":
        for b in range(bars):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 80))
    elif scene == "OUTRO":
        for b in range(bars):
            vs = 1.0 - 0.5 * b / max(bars - 1, 1)
            out.extend(long_chor(CM7, b, int(56 * vs)))
    return out


def pads_for(scene, bars):
    out = []

    def long_pad(voicing, bar, vel):
        return bar_hits([(0.0, p, vel, 4.0) for p in voicing], bar)

    if scene == "INTRO":
        out = [long_pad(PAD_CM, b, 42) for b in range(bars)]
    elif scene == "GROOVE":
        out = [long_pad(PAD_FM, b, 44) for b in range(bars)]
    elif scene == "BUILD":
        out = []   # air = no pads
    elif scene == "DROP":
        for b in range(bars):
            if b < 8:
                out.append([])
            elif b < 16:
                out.append(long_pad(PAD_FM, b, 40))
            else:
                out.append(long_pad(PAD_GM, b, 42))
    elif scene == "BREAKDOWN":
        out = [long_pad(PAD_GM, b, 44) for b in range(bars)]
    elif scene == "JUMP":
        out = [[]] * bars   # air
    elif scene == "OUTRO":
        out = []
        for b in range(bars):
            vs = 1.0 - 0.5 * b / max(bars - 1, 1)
            out.append(long_pad(PAD_CM, b, int(36 * vs)))
    return [n for bar in out for n in bar]


def melody_for(scene, bars):
    out = []
    if scene == "INTRO":
        pass  # silent
    elif scene == "GROOVE":
        for ph in range(bars // 4):
            base_beats = ph * 16.0
            lift = 4 * ph
            if ph % 2 == 0:
                motif = [(x + base_beats, p, min(126, vf + lift), d)
                         for x, p, vf, d in MEL_CALL]
            else:
                motif = [(x + base_beats, p, min(126, vf + lift), d)
                         for x, p, vf, d in MEL_ANS]
            out.extend([note(p, s, d, _j(v, ph + int(s))) for s, p, v, d in motif])
    elif scene == "BUILD":
        out = bar_hits(P_RISE1, 6) + bar_hits(P_RISE2, 7)
    elif scene == "DROP":
        # Hook bars 8 and 12; answer bars 16 and 20; tag bar 23
        for b in (8, 12):
            out.extend(hits_at(MEL_HOOK, b * 4.0, b))
        for b in (16, 20):
            out.extend(hits_at(MEL_ANS2, b * 4.0, b))
        out.extend(hits_at([(3.5, Bb4, 64, 0.5)], 23 * 4.0, 23))
    elif scene == "BREAKDOWN":
        out = hits_at([(0.0, Bb4, 58, 2.0)], 4 * 4.0, 0)
        out += hits_at([(0.0, C5, 62, 2.0)], 12 * 4.0, 4)
    elif scene == "JUMP":
        out = hits_at(MEL_ANS2, 0, 0) + hits_at(MEL_ANS2, 4 * 4.0, 4)
    elif scene == "OUTRO":
        out = hits_at([(2.5, G4, 48, 0.5), (3.0, C5, 42, 0.5)], 0, 0)
    return out


def fx_for(scene, bars):
    out = []

    def throw(bar, vel):
        return bar_hits([(3.75, DRUM_PERC, vel, 0.25), (3.5, D4, max(50, vel - 8), 0.40)], bar)

    if scene == "INTRO":
        for b in (3, 7, 11):
            out.extend(throw(b, 72))
    elif scene == "GROOVE":
        for b in range(1, bars, 2):
            out.extend(bar_hits([(3.5, DRUM_PERC, 62, 0.25)], b))
        out.extend(throw(bars - 1, 70))
    elif scene == "BUILD":
        for b in range(4):
            out.extend(bar_hits([(3.5, DRUM_PERC, 64, 0.25)], b))
        # 8th-note rim dadadada
        r8 = [(0.5 + k * 0.5, DRUM_RIM, 58 + 3 * k, 0.08) for k in range(7)]
        out.extend(bar_hits(r8, 4))
        out.extend(bar_hits(r8, 5))
        r8_6 = [(0.5 + k * 0.5, DRUM_RIM, 70 + 3 * k, 0.08) for k in range(7)]
        r16 = [(k * 0.25, DRUM_RIM, 78 + int(2.7 * k), 0.08) for k in range(16)]
        out.extend(bar_hits(r8_6, 6) + bar_hits(r16 + [(3.75, DRUM_PERC, 110, 0.25)], 7))
    elif scene == "DROP":
        for b in range(bars):
            if b % 2 == 0 and b < 16:
                out.extend(bar_hits([(3.5, DRUM_PERC, 66, 0.25)], b))
            if b >= 16:
                out.extend(bar_hits([(1.75, DRUM_PERC, 66, 0.12), (3.75, DRUM_PERC, 70, 0.12)], b))
        for b in (7, 15, 23):
            out.extend(throw(b, 74))
    elif scene == "BREAKDOWN":
        for b in (0, 8):
            out.extend(bar_hits([(0.0, DRUM_PERC, 88, 0.50), (0.0, DRUM_RIM, 72, 0.25)], b))
        out.extend(throw(bars - 1, 68))
    elif scene == "JUMP":
        for b in range(bars):
            out.extend(bar_hits([(1.75, DRUM_PERC, 70, 0.12), (3.5, DRUM_PERC, 68, 0.25)], b))
        out.extend(throw(bars - 1, 72))
    elif scene == "OUTRO":
        for b, v_fac in ((3, 60), (7, 52), (11, 44)):
            out.extend(throw(b, v_fac))
    return out


BUILDERS = (drums_for, bass_for, sub_for, chords_for, pads_for, melody_for, fx_for)


# ───────────────────── Ableton TCP Client ──────────────────────────────

class AbletonClient:
    """TCP client for Ableton Live's MCP Remote Script (port 9877)."""

    TCP_PORT = 9877

    def __init__(self, host="localhost", port=None):
        self.host = host
        self.port = port or self.TCP_PORT
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERR] socket connect: {e}")
            self.sock = None
            return False

    def send(self, cmd, params=None):
        """Send a JSON command and return the raw response dict."""
        if self.sock is None and not self.connect():
            return {"status": "error", "details": "not connected"}
        payload = json.dumps({"type": cmd, "params": params or {}}).encode() + b"\n"
        try:
            self.sock.sendall(payload)
            raw = self.sock.recv(262_144).decode()
            return json.loads(raw) if raw else {"status": "ok"}
        except Exception as e:
            print(f"[ERR] {cmd}: {e}")
            self.sock = None
            return {"status": "error", "details": str(e)}

    def send_checked(self, cmd, params=None, descr=""):
        """Send and raise RuntimeError on any status != 'success'."""
        r = self.send(cmd, params)
        status = r.get("status") if isinstance(r, dict) else None
        if status != "success":
            snip = json.dumps(r)[:220] if r else "empty"
            raise RuntimeError(f"{descr or cmd} failed: {snip}")
        return r

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


# ──────────────────────── DubFiveMin ─────────────────────────────────

class DubFiveMin:
    def __init__(self, client):
        self.c = client
        self.n_scenes = len(SCENES)

    # ── Track / device helpers ──

    def create_track(self, idx, name, instrument_uri, effect_uris):
        """Create a MIDI track, load an instrument, then a chain of effects."""
        print(f"  track {idx}: {name}")
        self.c.send_checked("create_midi_track", {"index": idx}, f"create track {name}")
        time.sleep(0.15)
        self.c.send_checked("set_track_name", {"track_index": idx, "name": name},
                            f"name track {name}")
        # Instrument
        self.c.send_checked("load_browser_item",
                            {"track_index": idx, "item_uri": instrument_uri},
                            f"load instrument {instrument_uri}")
        time.sleep(0.60)
        # Effects
        for fx in effect_uris:
            self.c.send_checked("load_browser_item",
                                {"track_index": idx, "item_uri": fx},
                                f"load fx {fx}")
            time.sleep(0.50)
        # Verify device chain length
        n_expected = 1 + len(effect_uris)
        n_got = self._device_count(idx)
        if n_got < n_expected:
            raise RuntimeError(
                f"{name}: expected {n_expected} devices, found {n_got} — load failed")
        print(f"    devices: {n_got}/{n_expected} OK")

    def _device_count(self, track_idx):
        r = self.c.send("get_track_info", {"track_index": track_idx})
        devs = (r.get("result") or {}).get("devices")
        return len(devs) if isinstance(devs, list) else -1

    def _param_map(self, track_idx, device_idx):
        """Return {lower_name: (index, min, max, current)} for device params."""
        r = self.c.send("get_device_parameters",
                        {"track_index": track_idx, "device_index": device_idx})
        params = (r.get("result") or {}).get("parameters") or []
        out = {}
        for i, p in enumerate(params):
            if isinstance(p, dict):
                nm = str(p.get("name", "")).lower()
                out[nm] = (i, float(p.get("min", 0.0)),
                           float(p.get("max", 1.0)),
                           p.get("value", p.get("real_value", 0.0)))
        return out

    def apply_device_tweaks(self):
        """Set dub-critical device parameters within each device's real range."""
        for track_idx, tweaks in DEVICE_TWEAKS.items():
            for device_idx, name_substr, frac in tweaks:
                pmap = self._param_map(track_idx, device_idx)
                if not pmap:
                    print(f"    [warn] no params on t{track_idx} d{device_idx}")
                    continue
                hit = None
                key_lower = name_substr.lower()
                for nm, spec in pmap.items():
                    if key_lower in nm:
                        hit = spec
                        break
                if hit is None:
                    print(f"    [warn] '{name_substr}' not on t{track_idx} d{device_idx} "
                          f"(has {sorted(pmap.keys())[:6]})")
                    continue
                i, lo, hi, _cur = hit
                value = lo + (hi - lo) * frac
                self.c.send("set_device_parameter",
                            {"track_index": track_idx,
                             "device_index": device_idx,
                             "parameter_index": i,
                             "value": value})
            print(f"  tweaks applied: track {track_idx}")

    def clear_clip_slots(self, max_track=7, max_slot=8):
        """Delete any clips in slot × track up to max so recreate works."""
        removed = 0
        for ti in range(max_track):
            for ci in range(max_slot):
                r = self.c.send("delete_clip", {"track_index": ti, "clip_index": ci})
                if (r or {}).get("status") == "success":
                    removed += 1
        print(f"  cleared {removed} clip slots")

    def add_clip(self, track_idx, clip_idx, length_beats, notes):
        self.c.send_checked("create_clip",
                            {"track_index": track_idx, "clip_index": clip_idx,
                             "length": float(length_beats)},
                            f"create_clip t{track_idx} s{clip_idx}")
        time.sleep(0.03)
        if notes:
            self.c.send_checked("add_notes_to_clip",
                                {"track_index": track_idx, "clip_index": clip_idx,
                                 "notes": notes},
                                f"add_notes t{track_idx} s{clip_idx}")
            time.sleep(0.03)

    def detect_existing(self):
        """Return (True, [names]) if the 7 expected dub tracks exist with
        matching names and at least one device each."""
        r = self.c.send("get_all_tracks")
        res = r.get("result", {})
        tracks = res.get("tracks") if isinstance(res, dict) else res
        names = []
        ok = True
        for i, (name, _uri, _fx) in enumerate(TRACKS):
            if i >= len(tracks) or not isinstance(tracks[i], dict):
                ok = False
                names.append("?")
            else:
                nm = str(tracks[i].get("name", ""))
                names.append(nm)
                if nm != name:
                    ok = False
        if ok:
            for i in range(len(TRACKS)):
                if self._device_count(i) < 1:
                    ok = False
                    break
        return ok, names

    TRACK_NAMES = [t[0] for t in TRACKS]

    def ensure_scenes(self):
        """Ensure the 7 scenes exist and set their names."""
        r = self.c.send("get_all_scenes")
        res = r.get("result", {})
        scenes = res.get("scenes") if isinstance(res, dict) else res
        n_have = len(scenes) if isinstance(scenes, list) else 0
        for i in range(self.n_scenes):
            if i >= n_have:
                self.c.send_checked("create_scene", {"index": i}, f"create scene {i}")
                time.sleep(0.05)
            self.c.send_checked("set_scene_name",
                                {"scene_index": i, "name": SCENES[i][0]},
                                f"name scene {i}")
        print(f"  scenes: {self.n_scenes} ready")

    def build_clips(self):
        """Create all session clips with improved notes, mix, tweaks, follow."""
        c = self.c
        self.ensure_scenes()
        print("[clips] clearing any pre-existing clip slots")
        self.clear_clip_slots(max_slot=len(SCENES) + 2)
        total = 0
        for ti, builder in enumerate(BUILDERS):
            name = TRACKS[ti][0]
            print(f"[clips] {name}")
            for si, (sname, sbars) in enumerate(SCENES):
                notes = builder(sname, sbars)
                total += len(notes)
                self.add_clip(ti, si, sbars * 4.0, notes)
        print(f"  {total} notes")
        print("[mix] levels, pans, dub sends")
        self._set_mix()
        print("[devices] dub tweaks")
        self.apply_device_tweaks()
        print("[follow] chaining scenes")
        self._chain_follow_actions()

    def _set_mix(self):
        mix = {
            0: (0.78, 0.50),   # DRUMS
            1: (0.68, 0.50),   # BASS
            2: (0.55, 0.50),   # SUB
            3: (0.52, 0.56),   # CHORDS
            4: (0.44, 0.44),   # PADS
            5: (0.56, 0.55),   # MELODY
            6: (0.50, 0.46),   # FX/PERC
        }
        for t, (vol, pan) in mix.items():
            self.c.send("set_track_volume", {"track_index": t, "volume": vol})
            self.c.send("set_track_pan",   {"track_index": t, "pan": pan})
        # send 0 = reverb, send 1 = delay (amount 0-1)
        sends = {
            0: (0.10, 0.06),   # drums: light verb + tiny slap
            1: (0.00, 0.12),   # bass: no verb, delay tail
            2: (0.00, 0.00),   # sub: clean
            3: (0.24, 0.10),   # chords: delay into verb
            4: (0.40, 0.14),   # pads: maximum wash
            5: (0.20, 0.22),   # melody: dub centrepiece
            6: (0.35, 0.30),   # fx: cannon echo
        }
        for t, (rv, dl) in sends.items():
            self.c.send("set_send_amount", {"track_index": t, "send_index": 0, "amount": rv})
            self.c.send("set_send_amount", {"track_index": t, "send_index": 1, "amount": dl})

    def _chain_follow_actions(self):
        """Chain every clip to the matching clip in the next scene via
        follow action ('Other' -> jump to next scene's slot).
        Last scene stops."""
        for track_idx in range(len(TRACKS)):
            for si in range(self.n_scenes):
                target = si + 1 if si < self.n_scenes - 1 else None
                action_type = 1 if target is None else 6  # 1=stop, 6=Other
                clip_target = si if target is None else target
                self.c.send("set_clip_follow_action", {
                    "track_index": track_idx,
                    "clip_index": si,
                    "action_slot": 0,
                    "action_type": action_type,
                    "trigger_time": 0,
                    "clip_index_target": clip_target,
                })

    ARRANGE_BPM = 600.0

    def clear_arrangement(self):
        """Remove any pre-existing arrangement clips on tracks 0-6 so
        our captures can start cleanly."""
        c = self.c
        removed = 0
        # Delete clips descending so indices do not change
        for t in range(len(TRACKS)):
            for idx in range(40, -1, -1):
                r = c.send("delete_arrangement_clip",
                           {"track_index": t, "clip_index": idx})
                st = (r or {}).get("status")
                if st == "success":
                    removed += 1
        # Disarm all tracks as well (safe)
        for t in range(8):
            c.send("set_track_arm", {"track_index": t, "arm": False})
        print(f"[arrange] cleared {removed} stray arrangement clips")

    def arrange(self):
        """Fast layout of the arrangement via per-section capture at 600 BPM.
        Detects if the captured method uses BEATS (Live 12 direct) vs BARS
        (real-time fallback) and adapts `start_bar` units accordingly."""
        c = self.c
        print("[arrange] laying out 96 bars via fast capture")
        c.send("stop_playback")
        c.send_checked("set_tempo", {"tempo": self.ARRANGE_BPM}, "set tempo 600")
        time.sleep(0.20)
        c.send_checked("start_playback", descr="start_playback")
        time.sleep(0.15)
        beats_mode = True
        offset = 0
        sections_tab = ""
        for si, (sname, sbars) in enumerate(SCENES):
            c.send_checked("trigger_scene", {"scene_index": si}, f"trigger {sname}")
            time.sleep(0.1 if si == 0 else 0.08)
            pos = offset * 4.0 if beats_mode else float(offset)
            r = c.send_checked("capture_and_insert_arrangement",
                               {"start_bar": pos, "length_bars": sbars,
                                "quantize": True},
                               f"capture {sname}")
            res = (r or {}).get("result") or {}
            method = res.get("method")
            if method:
                if si == 0:
                    beats_mode = (method == "direct")
                    unit = "beats" if beats_mode else "bars"
                    print(f"  capture API: {method} -> start_bar unit = {unit}")
                sections_tab = "  "
            sec_disp = f"{sname}:{offset}-{offset + sbars}"
            print(f"{sections_tab}{sec_disp:>12s} ok [{method or 'n/a'}]")
            # let the section play through at 600 BPM before the next trigger
            time.sleep(sbars * 4 * 60.0 / self.ARRANGE_BPM + 0.10)
            offset += sbars
        c.send("stop_playback")
        c.send_checked("set_tempo", {"tempo": 75.0}, "restore tempo 75")
        print(f"[arrange] {offset} bars laid into Arrangement")

    def capture(self):
        """Legacy real-time capture (~5:07). Start playback, chain through
        scenes with manual triggers, record the result into the arrangement."""
        c = self.c
        c.send("set_playhead_position", {"bar": 0, "beat": 0})
        c.send("start_recording")
        c.send("start_playback")
        c.send("trigger_scene", {"scene_index": 0})
        bpm = 75.0
        for si, (sname, sbars) in enumerate(SCENES):
            dur = sbars * 4 * (60.0 / bpm)
            pct = (si + 0.9) / self.n_scenes * 100
            print(f"  [{pct:4.1f}%] {sname:10s} {dur:5.1f}s")
            time.sleep(dur)
            if si < self.n_scenes - 1:
                c.send("trigger_scene", {"scene_index": si + 1})
        time.sleep(0.8)
        c.send("stop_recording")
        c.send("stop_playback")
        print("[arrangement] real-time capture finished")

    def build(self):
        """Full destructive build: delete all tracks, recreate, build clips."""
        c = self.c
        print("Building 5-minute dub tape version (fresh)")
        c.send("stop_playback")
        c.send_checked("delete_all_tracks", descr="delete_all_tracks")
        time.sleep(0.60)
        print("[tempo] 75 BPM")
        c.send_checked("set_tempo", {"tempo": 75.0}, "set_tempo")
        print("[tracks] 7 MIDI tracks + instruments + effects")
        for i, (name, uri, fx) in enumerate(TRACKS):
            self.create_track(i, name, uri, fx)
        self.build_clips()


def main():
    ap = argparse.ArgumentParser(
        description="Prepare a 5-minute dub tape version")
    ap.add_argument("--fresh", action="store_true",
                    help="force full rebuild (delete all tracks + reload instruments)")
    ap.add_argument("--clips-only", action="store_true",
                    help="only rebuild clips, names, mix, tweaks, follow actions")
    ap.add_argument("--arrange", action="store_true",
                    help="also render the full arrangement via fast capture (~45 s)")
    ap.add_argument("--capture", action="store_true",
                    help="also real-time record into Arrangement (~5:07)")
    args = ap.parse_args()

    c = AbletonClient()
    if not c.connect():
        print("\nStart Ableton Live with the MCP Remote Script (TCP 9877) first.")
        sys.exit(1)

    dub = DubFiveMin(c)

    if args.fresh:
        dub.build()
    elif args.clips_only:
        ok, names = dub.detect_existing()
        if not ok:
            print("[ERR] --clips-only requires intact dub tracks:")
            print("      " + "; ".join(f"{i}:{n or '?'}" for i, n in enumerate(names)))
            c.close()
            sys.exit(2)
        print("[tracks] reusing existing dub tracks + devices")
        dub.build_clips()
    else:
        ok, names = dub.detect_existing()
        if ok:
            print("[tracks] reusing existing dub tracks + devices")
            dub.build_clips()
        else:
            print("[tracks] not intact — fresh build")
            dub.build()

    total_bars = sum(b for _, b in SCENES)
    mins = total_bars * 4 * 60 / 75 / 60
    print(f"\nReady: {total_bars} bars @ 75 BPM ~= {mins:.2f} min")
    print("Sections: " + " -> ".join(n for n, _ in SCENES))
    print("Fire scene 0 (INTRO) — follow actions chain all 7 sections.")

    if args.arrange:
        dub.clear_arrangement()
        dub.arrange()
    if args.capture:
        print("\nRecording into Arrangement in real time (do not touch Live)")
        dub.capture()

    c.close()


if __name__ == "__main__":
    main()
