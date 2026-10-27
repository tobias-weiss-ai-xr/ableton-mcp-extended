#!/usr/bin/env python3
"""
Prepare a STOIC-90: 90-minute minimal dub techno in Ableton Live.

90-minute dub techno structure: 2700 bars @ 120 BPM = 90:00
and follow-action chaining: fire scene 0 (INTRO) once and the whole track
plays through: INTRO → GROOVE → BUILD → DROP → BREAKDOWN → JUMP → OUTRO.

Musical features baked in:
  * Section-final drum fills (16th snare-roll crescendos)
  * Pre-drop dropout: BUILD last bar is silent in BASS/SUB/CHORDS/PADS
  * Offbeat skank chords in GROOVE/JUMP, layered skank in DROP
  * 8-bar A/B bass phrases with walk-ups C→D→Eb→F→G
  * Melody call-and-answer phrasing + BUILD pentatonic riser run
  * Deterministic velocity jitter for humanisation
  * Optional randomness: velocity variation, microtiming, note skipping

Modes:
  (default)        auto: reuse existing 7 dub tracks if present; else full build
  --fresh          force full rebuild (delete all tracks + reload instruments)
  --clips-only     refuse to touch tracks/devices; rebuild clips, names,
                   mix, tweaks, follow actions only
  --arrange        ALSO lay the whole Arrangement out into Ableton's
                   Arrangement View via fast duplicate-to-arrangement
  --random         Add subtle randomness: velocity, timing, note prob

Protocol: TCP JSON {"type": cmd, "params": {...}} to the Remote Script (port 9877).
"""

import argparse
import json
import random
import socket
import sys
import time


# ─── Global randomness ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RANDOM_SEED = None  # Set to integer for reproducible randomness


def __init_random(seed=None):
    """Seed the RNG if a seed is provided."""
    global RANDOM_SEED
    if seed is not None:
        RANDOM_SEED = seed
        random.seed(seed)
    return bool(seed)


def r_vel(base, spread=0.10):
    """Random velocity around base (±spread). Returns int 1-127."""
    if RANDOM_SEED is None:
        return int(base)
    spread_v = spread * 127
    return max(1, min(127, int(base + random.uniform(-spread_v, spread_v))))


def r_skip(prob=0.05):
    """Randomly skip with probability. Returns True if should skip."""
    if RANDOM_SEED is None:
        return False
    return random.random() < prob


def r_time(base, jitter=0.01):
    """Random timing jitter around base (±jitter in beats)."""
    if RANDOM_SEED is None:
        return round(base, 6)
    jittered = base + random.uniform(-jitter, jitter)
    return round(max(0, jittered), 6)


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
C1, D1, Eb1, F1, G1, Ab1 = 24, 26, 27, 29, 31, 32
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
C4, D4, Eb4, F4, G4, A4, Bb4 = 60, 62, 63, 65, 67, 69, 70
C5, D5, Eb5, F5, G5, A5 = 72, 74, 75, 77, 79, 81

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
BASS_URI    = "query:Sounds#Bass:FileId_49654"  # 101 Essential Bass           # 101 Essential Bass
PAD_URI     = "query:Sounds#Pad:FileId_45564"            # 5ths Glass Motion Pad
STRINGS_URI = "query:Sounds#Pad:FileId_45565"  # Keep strings for pads            # Analog Slow Sweep
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
    ("FX/PERC", DRUMS_URI, [FX_DELAY, FX_REVERB]),
]

# Post-load device tweaks: track -> [(device_index, param_name_substr, fraction)]
DEVICE_TWEAKS = {
    2: [(1, "Frequency", 0.06)],                # SUB Auto Filter: very dark
    3: [(1, "Feedback", 0.62), (1, "Dry/Wet", 0.35)],  # CHORDS Delay
    5: [(1, "Feedback", 0.55), (1, "Dry/Wet", 0.30)],  # MELODY Delay
    6: [(1, "Feedback", 0.72), (1, "1 Filter Freq", 0.45)],  # FX Filter Delay
}

# Clip automation: classic dub arcs. Track -> (param_substr, device_substr,
# {section: [(beat, value_frac), ...]}). VALUE SEMANTICS SOLVED (see commit
# 79d34c7 + Ableton's own Push2 automation_component.py):
#   clip.automation_envelope(param) -> existing envelope (METHOD taking param)
#   clip.create_automation_envelope(param) -> new envelope
#   clip.clear_envelope(param) / clear_all_envelopes() -> wipe
#   envelope.insert_step(start_beat, length_beats, value_REAL_UNITS)
#   envelope.value_at_time(beat) -> real value (boundary reads pre-step)
# Ramp segments become interpolated 2-beat staircases (_staircase). Written
# directly onto ARRANGEMENT clips after arrange() - duplicate_clip_to_
# arrangement copies NOTES but NOT envelopes (verify_automation checks).
# Dub techno automations: SUB filter sweeps, CHORDS echo, FX delay
# Each scene gets its own automation arc for evolution
# Format: [(track_idx, param_name_substring, device_name_substring, {"scene": [(time_in_beats, normalized_value), ...]})]
AUTOMATION = [
    # SUB track: Auto Filter Frequency - SLOW dub sweeps
    # Base: 20% -> INTRO rises to 30%, GROOVE oscillates 30-40%, BUILD rises to 60%, 
    #        DROP sits at 45%, BREAKDOWN drops to 25%, JUMP rises to 55%, OUTRO fades to 15%
    (2, "Frequency", "Auto Filter", {
        "INTRO":   [(0.0, 0.20),(96.0, 0.30),(179.9, 0.30)],
        "GROOVE":  [(0.0, 0.30),(180.0, 0.40),(359.9, 0.35)],
        "BUILD":   [(0.0, 0.35),(90.0, 0.50),(179.9, 0.60)],
        "DROP":    [(0.0, 0.45),(360.0, 0.40),(719.9, 0.45)],
        "BREAKDOWN": [(0.0, 0.45),(180.0, 0.25),(359.9, 0.20)],
        "JUMP":    [(0.0, 0.40),(180.0, 0.55),(359.9, 0.50)],
        "OUTRO":   [(0.0, 0.35),(270.0, 0.20),(539.9, 0.15)],
    }),
    # CHORDS track: Delay Feedback - Classic dub echo
    # INTRO: subtle (20%), GROOVE: modest (40-50%), BUILD: rising (50-65%), 
    #        DROP: max (75%), BREAKDOWN: reduced (25%), JUMP: moderate (55%), OUTRO: minimal (10%)
    (3, "Feedback", "Delay", {
        "INTRO":   [(0.0, 0.20),(179.9, 0.25)],
        "GROOVE":  [(0.0, 0.40),(180.0, 0.50),(359.9, 0.45)],
        "BUILD":   [(0.0, 0.50),(90.0, 0.60),(179.9, 0.65)],
        "DROP":    [(0.0, 0.70),(360.0, 0.75),(719.9, 0.70)],
        "BREAKDOWN": [(0.0, 0.65),(90.0, 0.25),(359.9, 0.20)],
        "JUMP":    [(0.0, 0.50),(180.0, 0.55),(359.9, 0.50)],
        "OUTRO":   [(0.0, 0.40),(270.0, 0.15),(539.9, 0.10)],
    }),
    # CHORDS track: Delay Dry/Wet - Echo intensity
    (3, "Dry/Wet", "Delay", {
        "INTRO":   [(0.0, 0.25),(179.9, 0.30)],
        "GROOVE":  [(0.0, 0.35),(359.9, 0.40)],
        "BUILD":   [(0.0, 0.40),(179.9, 0.55)],
        "DROP":    [(0.0, 0.60),(719.9, 0.65)],
        "BREAKDOWN": [(0.0, 0.30),(359.9, 0.20)],
        "JUMP":    [(0.0, 0.50),(359.9, 0.55)],
        "OUTRO":   [(0.0, 0.30),(539.9, 0.15)],
    }),
    # FX/PERC track: Delay Feedback - Adding FX movement
    # INTRO: minimal (15%), GROOVE: subtle (20-30%), BUILD: rising (30-45%),
    #        DROP: max echo (50-65%), BREAKDOWN: reduced (20%), JUMP: active (35-50%), OUTRO: fading (10%)  
    (6, "Feedback", "Delay", {
        "INTRO":   [(0.0, 0.15),(179.9, 0.20)],
        "GROOVE":  [(0.0, 0.20),(180.0, 0.30),(359.9, 0.25)],
        "BUILD":   [(0.0, 0.30),(90.0, 0.45),(179.9, 0.40)],
        "DROP":    [(0.0, 0.50),(180.0, 0.65),(360.0, 0.60),(719.9, 0.55)],
        "BREAKDOWN": [(0.0, 0.45),(180.0, 0.20),(359.9, 0.15)],
        "JUMP":    [(0.0, 0.35),(180.0, 0.50),(359.9, 0.40)],
        "OUTRO":   [(0.0, 0.25),(270.0, 0.10),(539.9, 0.08)],
    }),
]

# 90-minute dub techno structure: 2700 bars @ 120 BPM = 90:00
SCENES = [
    ("INTRO",     180),   # 15:00 - filter opening, hiss, sub emergence
    ("GROOVE",    360),   # 12:00 - 4/4 kick + hats, chords enter, bass pulse
    ("BUILD",     180),   # 06:00 - hats intensify, delay feedback rises
    ("DROP",      720),   # 24:00 - full dub cannon: chords layer, filter sweeps
    ("BREAKDOWN", 360),   # 12:00 - stripped: kick sparse, dub hole, echoes
    ("JUMP",      360),   # 12:00 - groove returns, intensity peaks
    ("OUTRO",     540),   # 18:00 - long dissolve, filter closes, fade to silence
]


# ──────────────────────────── Helpers ──────────────────────────────────

def note(pitch, start_beat, duration, velocity):
    return {"pitch": int(pitch), "start_time": float(start_beat),
            "duration": float(duration), "velocity": int(velocity)}


# Deterministic velocity jitter cylinder (16 values so short loops still vary)
_JITTER = (3, -2, 4, -1, 2, -4, 1, 3, -3, 2, 5, -1, 2, -3, 4, -2)

def _j(v, idx):
    """Jitter a velocity value deterministically, or random if seeded."""
    if RANDOM_SEED is not None:
        return r_vel(v, spread=0.08)
    return max(1, min(126, int(v + _JITTER[idx % len(_JITTER)])))


def bar_hits(hits, bar=0):
    """Convert hits (beat, pitch, vel, dur) into note dicts with randomness.
    
    When RANDOM_SEED is set:
      - Velocities get ±10% random spread
      - Notes have 5% chance to be skipped
      - Timing gets ±32nd note (±0.0625 beat) jitter
    Deterministic otherwise.
    Notes that would end after bar+1 are clipped."""
    out = []
    clip_end = (bar + 1) * 4.0
    for k, (b, p, v, d) in enumerate(hits):
        # Random skip
        if RANDOM_SEED is not None and r_skip(prob=0.05):
            continue
        # Random timing jitter (±1/16 beat ≈ 0.0625)
        s = bar * 4.0 + (r_time(b, jitter=0.0625) if RANDOM_SEED else b)
        if s + d > clip_end + 1e-9:
            d = clip_end - s
            if d <= 0:
                continue
        # Velocity with jitter
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
            s = n["start_time"] + offset
            if s + n["duration"] > clip_end + 1e-6:
                continue
            d = dict(n)
            d["start_time"] = s
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
# Dub techno: root notes in sub-octave (C1, F1), sliding 5ths
BA_A = [(0.0, C1, 2.0, 78), (2.0, G1, 1.5, 72), (3.0, C1, 1.0, 70)]
BA_B = [(0.0, D1, 2.0, 80), (2.0, G1, 1.5, 74), (3.0, C1, 1.0, 68)]
BA_W = [(0.0, C1, 1.5, 76), (1.0, F1, 1.5, 78), (2.5, G1, 1.5, 74)]
BA_DRIVE = [(0.0, C1, 0.5, 80), (0.5, C1, 0.5, 70), (1.0, C1, 0.5, 76),
            (2.0, G1, 0.5, 82), (2.5, G1, 0.5, 72), (3.0, C1, 0.5, 78), (3.5, C1, 0.5, 74)]
BA_BUILD    = [(0.0, C1, 3.0, 84), (3.0, F1, 1.0, 76)]
BA_JUMP    = [(0.0, C1, 1.0, 80), (1.0, C2, 1.0, 70), (2.0, G1, 1.0, 78), (3.0, C1, 1.0, 74)]
# INTRO: simple walking root
BA_INTRO   = [(0.0, C1, 2.0, 70), (2.0, G1, 2.0, 68)]
# OUTRO: slow fade with root and fifth
BA_OUTRO   = [(0.0, C1, 2.0, 60), (2.0, G1, 2.0, 55)]

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
    """Build drum track notes for (scene, bars) — with random ghost notes and variations."""
    out = []
    
    def add_random_ghosts(base_hits, ghost_prob=0.20):
        """Add random ghost notes (snare/hat/rim) with probability."""
        if RANDOM_SEED is None:
            return base_hits
        extended = list(base_hits)
        ghost_positions = [0.5, 1.5, 2.5, 3.5]  # Off-beat 16th positions
        for pos in ghost_positions:
            if random.random() < ghost_prob:
                # Random ghost note: snare (low vel) or closed hat
                ghost_pitch = random.choice([DRUM_SNARE, DRUM_HAT_C, DRUM_RIM])
                ghost_vel = random.randint(20, 45)  # quiet ghosts
                ghost_dur = 0.125 if ghost_pitch == DRUM_HAT_C else 0.25
                extended.append((pos, ghost_pitch, ghost_vel, ghost_dur))
        return extended
    
    def random_hat_density(base_hits, extra_hat_prob=0.15):
        """Add extra random hi-hat notes."""
        if RANDOM_SEED is None:
            return base_hits
        extended = list(base_hits)
        # Try adding hats at 16th note positions
        for pos in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
            if random.random() < extra_hat_prob:
                # Only add if position doesn't already have a hat-like note
                has_hat = any(p == b for b, p, v, d in extended if p in (DRUM_HAT_C, DRUM_HAT_O))
                if not has_hat:
                    extended.append((pos, DRUM_HAT_C, random.randint(50, 70), 0.125))
        return extended
    
    for b in range(bars):
        if scene == "INTRO":
            hits = add_random_ghosts(DR_SPARSE, ghost_prob=0.10)
            hits = random_hat_density(hits, extra_hat_prob=0.08)
        elif scene == "GROOVE":
            hits = add_random_ghosts(DR_GROOVE, ghost_prob=0.20)
            hits = random_hat_density(hits, extra_hat_prob=0.12)
        elif scene == "BUILD":
            # Progressive intensity: ghost prob increases from 15% to 45% over scene
            progress = b / max(bars - 1, 1)
            ghost_p = 0.15 + 0.30 * progress
            hat_p = 0.10 + 0.20 * progress
            hits = add_random_ghosts(DR_FOUR, ghost_prob=ghost_p)
            hits = random_hat_density(hits, extra_hat_prob=hat_p)
        elif scene == "DROP":
            # Add ghost snares and extra hats for energy
            # Vary density over the long DROP scene (720 bars)
            progress = min(1.0, b / max(bars // 3, 1))  # fast progression in first third
            ghost_p = 0.25 + 0.15 * progress
            hat_p = 0.15 + 0.10 * progress
            hits = add_random_ghosts(DR_ONEDROP, ghost_prob=ghost_p)
            hits = random_hat_density(hits, extra_hat_prob=hat_p)
        elif scene == "BREAKDOWN":
            pattern = DR_RIM_GHOST if b % 4 < 2 else DR_BD_HATS
            hits = add_random_ghosts(pattern, ghost_prob=0.10)
        elif scene == "JUMP":
            hits = add_random_ghosts(DR_JUMP, ghost_prob=0.20)
        elif scene == "OUTRO":
            vs = 1.0 - 0.55 * b / max(bars - 1, 1)
            hits = [(bt, p, int(v * vs), d) for bt, p, v, d in DR_SPARSE]
            hits = add_random_ghosts(hits, ghost_prob=0.05)
        else:
            hits = []
        out.append(bar_hits(hits, b))
    
    return [n for bar in out for n in bar]


def bass_for(scene, bars):
    """Stoic: simple looping bass phrases for any bar count."""
    if scene == "INTRO":
        out = [bar_hits([(0.0, C2, 1.0, 76), (2.0, C2, 1.0, 68)], b) for b in range(bars)]
    elif scene in ("GROOVE", "JUMP", "DROP", "RETURN"):
        # Loop 4-bar pattern infinitely
        out = []
        for b in range(bars):
            phase = b % 4
            if phase in (0, 1):
                pat = BA_A
            elif phase == 2:
                pat = BA_B
            else:
                pat = BA_W
            out.append(bar_hits(pat, b))
    elif scene == "BUILD":
        # Build tension with C1 to F1 slide
        out = [bar_hits(BA_BUILD, b) for b in range(bars)]
    elif scene == "BREAKDOWN":
        # Walking bass continuation
        out = [bar_hits(BA_W, b) for b in range(bars)]
    elif scene == "OUTRO":
        out = []
        for b in range(bars):
            vs = 1.0 - 0.5 * b / max(bars - 1, 1)
            out.append(bar_hits([(0.0, C1, int(68 * vs), 4.0)], b))
    else:
        out = [[] for _ in range(bars)]
    return [n for bar in out for n in bar]


def sub_for(scene, bars):
    """Stoic: looping sub bass for any bar count."""
    if scene == "INTRO":
        out = []
        for b in range(bars):
            vs = 0.75 + 0.25 * b / max(bars - 1, 1)
            out.append(bar_hits([(0.0, C1, int(60 * vs), 4.0)], b))
    elif scene in ("GROOVE", "BUILD", "DROP", "JUMP", "RETURN"):
        out = []
        for b in range(bars):
            phase = b % 4
            if phase in (0, 2):
                pat = SB_GR_A
            else:
                pat = SB_GR_B
            out.append(bar_hits(pat, b))
    elif scene == "BREAKDOWN":
        out = [bar_hits([(0.0, C1, 60, 4.0)], b) for b in range(bars)]
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
            out.extend(long_chor(CM7, b, 60 + int(5 * (b % 8) / 4)))
    elif scene == "GROOVE":
        for b in range(bars):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 74))
    elif scene == "BUILD":
        for b in range(bars):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 78 + int(b / 10)))
    elif scene == "DROP":
        for b in range(bars):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 80 + int(b / 20)))
    elif scene == "BREAKDOWN":
        for b in range(bars):
            out.extend(long_chor(CM7, b, 62 + int(b / 5)))
    elif scene == "JUMP":
        for b in range(bars):
            out.extend(skank(CM7 if b % 2 == 0 else FM7, b, 82 + int(b / 15)))
    elif scene == "OUTRO":
        for b in range(bars):
            vs = 1.0 - 0.7 * b / max(bars - 1, 1)
            if vs > 0.1:
                out.extend(long_chor(CM7, b, int(56 * vs)))
    return out


def pads_for(scene, bars):
    out = []

    def long_pad(voicing, bar, vel):
        return bar_hits([(0.0, p, vel, 4.0) for p in voicing], bar)

    if scene == "INTRO":
        out = [long_pad(PAD_CM, b, 42 + int(b / 10)) for b in range(bars)]
    elif scene in ("GROOVE", "BUILD", "DROP", "JUMP", "RETURN"):
        for b in range(bars):
            out.append(long_pad(PAD_FM if b % 4 < 2 else PAD_GM, b, 44 + int(b / 15)))
    elif scene == "BREAKDOWN":
        out = [long_pad(PAD_GM, b, 44 + int(b / 20)) for b in range(bars)]
    elif scene == "OUTRO":
        for b in range(bars):
            vs = 1.0 - 0.6 * b / max(bars - 1, 1)
            if vs > 0.1:
                out.append(long_pad(PAD_CM, b, int(36 * vs)))
    return [n for bar in out for n in bar]


def melody_for(scene, bars):
    out = []
    
    def random_octave(pitch, octave_range=1):
        """Add random octave variation (±octave_range)."""
        if RANDOM_SEED is None:
            return pitch
        oct_shift = random.randint(-octave_range, octave_range)
        return max(0, min(127, pitch + oct_shift * 12))
    
    def random_pitch_from(pitches):
        """Randomly select from a list of pitches."""
        if RANDOM_SEED is None or not pitches:
            return pitches[0] if pitches else 60
        return random.choice(pitches)
    
    if scene == "INTRO":
        pass  # silent
    elif scene == "GROOVE":
        # Sparse sonar pings every 16 bars with randomization
        for bb in range(8, bars, 16):
            out.extend(hits_at(MEL_CALL, bb * 4.0, bb))
            ans_notes = [(b, random_pitch_from([p-12, p, p+12]), v, d) 
                        for b, p, v, d in MEL_ANS]
            out.extend(hits_at(ans_notes, (bb + 4) * 4.0, bb + 4))
    elif scene == "BUILD":
        pass  # silent for stoic
    elif scene == "DROP":
        # Sparse pings every 32 bars with more variation
        for bb in range(8, bars, 32):
            hook_variations = [(b, random_pitch_from([p, p+2, p+7]), v, d) 
                              for b, p, v, d in MEL_HOOK]
            out.extend(hits_at(hook_variations, bb * 4.0, bb))
            out.extend(hits_at(MEL_ANS2, (bb + 8) * 4.0, bb + 8))
            tail_pitch = random_pitch_from([Bb4, A4, C5]) if RANDOM_SEED else Bb4
            out.extend(hits_at([(3.5, tail_pitch, 64, 0.5)], (bb + 16) * 4.0, bb + 16))
    elif scene == "BREAKDOWN":
        pass  # silent
    elif scene == "JUMP":
        # More frequent pings with randomness
        for bb in range(4, bars, 16):
            out.extend(hits_at(MEL_ANS2, bb * 4.0, bb))
    elif scene == "OUTRO":
        for bb in range(0, min(bars, 16), 8):
            outro_pitches = [
                (2.5, random_pitch_from([G4, A4, Bb4]), 48, 0.5),
                (3.0, random_pitch_from([C5, D5]), 42, 0.5)
            ] if RANDOM_SEED else [(2.5, G4, 48, 0.5), (3.0, C5, 42, 0.5)]
            out.extend(hits_at(outro_pitches, bb * 4.0, bb))
    return out


def fx_for(scene, bars):
    out = []
    def throw(bar, vel):
        return bar_hits([(3.75, DRUM_PERC, vel, 0.25), (3.5, D4, max(50, vel - 8), 0.40)], bar)
    if scene == "INTRO":
        for b in range(4, bars, 8):
            out.extend(throw(b, 68))
    elif scene in ("GROOVE", "BUILD", "DROP", "JUMP", "RETURN"):
        for b in range(1, bars, 2):
            out.extend(bar_hits([(3.75, DRUM_PERC, 54, 0.20)], b))
        for b in range(8, bars, 16):
            out.extend(throw(b, 70))
    elif scene == "BREAKDOWN":
        for b in range(0, bars, 8):
            out.extend(bar_hits([(0.0, DRUM_PERC, 72, 0.40)], b))
    elif scene == "OUTRO":
        for b in range(4, bars, 12):
            out.extend(throw(b, max(40, 52 + int(b / 3))))
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

    def _resolve_param_all_devices(self, track_idx, name_substr, dev_sub=None):
        """Scan every device on the track; return (dev_idx, p_idx, lo, hi)
        for the first device matching dev_sub whose parameter contains
        name_substr."""
        key = name_substr.lower()
        dk = (dev_sub or "").lower()
        for d in range(max(1, self._device_count(track_idx))):
            r = self.c.send("get_device_parameters",
                            {"track_index": track_idx, "device_index": d})
            res = (r or {}).get("result") or {}
            if dk and dk not in str(res.get("device_name", "")).lower():
                continue
            for p in res.get("parameters") or []:
                if key in str(p.get("name", "")).lower():
                    return (d, p["index"], float(p.get("min", 0.0)),
                            float(p.get("max", 1.0)))
        return None

    @staticmethod
    def _staircase(pts, clen, lo, hi, step=2.0):
        """Expand breakpoints [(beat, frac), ...] into Push2-canonical
        [start, length, value] step segments; long segments become an
        interpolated staircase (AutomationEnvelope has no ramp API)."""
        bp = {}
        for b, f in pts:
            bp[min(float(b), clen)] = max(0.0, min(1.0, float(f)))
        bp = sorted(bp.items())
        segs = []
        for i, (t0, f0) in enumerate(bp):
            t1 = bp[i + 1][0] if i + 1 < len(bp) else clen
            f1 = bp[i + 1][1] if i + 1 < len(bp) else f0
            n = max(1, int(round((t1 - t0) / step)))
            for k in range(n):
                s0 = t0 + (t1 - t0) * k / n
                s1 = t0 + (t1 - t0) * (k + 1) / n
                frac = f0 + (f1 - f0) * (k + 0.5) / n
                segs.append((s0, max(s1 - s0, 0.25), lo + (hi - lo) * frac))
        return segs

    def _send_retry(self, cmd, params, tries=5, delay=1.5):
        """Send with retries - Live refuses some automation writes with
        'Changes cannot be triggered by notifications' (transient)."""
        r = None
        for _ in range(tries):
            r = self.c.send(cmd, params)
            if (r or {}).get("status") == "success":
                return r
            time.sleep(delay)
        return r

    def automate(self, arrangement=False):
        """Write dub automation arcs onto device params (mixer/sends are not
        clip-automatable). mode: session clips (build_clips must exist) or
        arrangement clips (arrange() must have run) - envelopes do NOT
        survive duplicate_clip_to_arrangement, so arrangement mode is the
        reliable path for the laid-out track."""
        c = self.c
        written = skipped = failed = 0
        pos = 0
        offsets = []
        for _sname, sbars in SCENES:
            offsets.append(pos)
            pos += sbars * 4.0
        for ti, psub, dsub, arcs in AUTOMATION:
            hit = self._resolve_param_all_devices(ti, psub, dsub)
            if hit is None:
                print(f"    [warn] param '{psub}' ({dsub}) not found on "
                      f"track {ti} - skipping lane")
                continue
            dev_idx, p_idx, lo, hi = hit
            for si, (sname, sbars) in enumerate(SCENES):
                pts = arcs.get(sname)
                if not pts:
                    continue
                if not BUILDERS[ti](sname, sbars):
                    skipped += 1
                    continue  # empty section, no clip
                clen = sbars * 4.0
                segs = self._staircase(pts, clen, lo, hi)
                payload = [[round(s, 4), round(l, 4), round(v, 4)]
                           for s, l, v in segs]
                params = {"track_index": ti, "device_index": dev_idx,
                          "parameter_index": p_idx, "points": payload}
                if arrangement:
                    params["arrangement_start_time"] = offsets[si]
                else:
                    params["clip_index"] = si
                r = self._send_retry("set_clip_automation", params)
                if (r or {}).get("status") == "success":
                    written += len(payload)
                else:
                    failed += len(payload)
                    print(f"    [warn] t{ti} '{psub}' {sname}: "
                          f"{(r or {}).get('message', '?')}")
            print(f"  automation lane t{ti} '{psub}' ({dsub}) done")
        print(f"[auto] {written} automation steps written "
              f"({skipped} empty sections skipped, {failed} failed)")

    def verify_automation(self):
        """Spot-check envelopes in the ARRANGEMENT (they must survive
        duplicate_clip_to_arrangement). Informational + [warn] on miss."""
        checks = [
            (2, "Frequency", "Auto Filter", 0.0,   (0.05, 0.09)),
            (2, "Frequency", "Auto Filter", 112.0, (0.15, 0.85)),
            (3, "Feedback",  "Delay",      240.0, (0.62, 0.90)),
            (0, "Drive",     "Drum Buss",   112.0, (0.10, 0.60)),
        ]
        ok = 0
        for ti, psub, dsub, start_beat, (fa, fb) in checks:
            hit = self._resolve_param_all_devices(ti, psub, dsub)
            if not hit:
                continue
            _d, p_idx, lo, hi = hit
            r = self.c.send("get_clip_automation",
                            {"track_index": ti, "device_index": hit[0],
                             "parameter_index": p_idx,
                             "arrangement_start_time": start_beat,
                             "read_times": [start_beat + 2.0,
                                            start_beat + 16.0]})
            res = (r or {}).get("result") or {}
            if not res.get("has_envelope"):
                print(f"    [warn] t{ti} '{psub}' @{start_beat}beats: "
                      "no envelope in arrangement copy")
                continue
            rb = res.get("readback") or []
            va = rb[0] if rb else None
            if va is None or not (lo - 1e-6 <= va <= hi + 1e-6):
                print(f"    [warn] t{ti} '{psub}' @{start_beat}beats: "
                      f"readback {va} outside [{lo}, {hi}]")
                continue
            ok += 1
            print(f"    t{ti} '{psub}' @{start_beat}beats: envelope ok, "
                  f"sample {round(va, 4)} in [{lo}, {hi}]")
        print(f"[auto-verify] {ok}/{len(checks)} arrangement envelopes ok")

    def clear_clip_slots(self, max_track=7, max_slot=8):
        """Delete any clips in slot x track up to max so recreate works."""
        removed = 0
        for ti in range(max_track):
            for ci in range(max_slot):
                r = self.c.send("delete_clip", {"track_index": ti, "clip_index": ci})
                if (r or {}).get("status") == "success":
                    removed += 1
                time.sleep(0.02)  # Ensure Live processes deletions
        print(f"  cleared {removed} clip slots")

    def add_clip(self, track_idx, clip_idx, length_beats, notes):
        self.c.send_checked("create_clip",
                            {"track_index": track_idx, "clip_index": clip_idx,
                             "length": float(length_beats)},
                            f"create_clip t{track_idx} s{clip_idx}")
        time.sleep(0.15)
        if notes:
            self.c.send_checked("add_notes_to_clip",
                                {"track_index": track_idx, "clip_index": clip_idx,
                                 "notes": notes},
                                f"add_notes t{track_idx} s{clip_idx}")
            time.sleep(0.20)

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
        self.clear_clip_slots(max_track=32, max_slot=len(SCENES) + 2)
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
        """Lay the full arrangement out via build_arrangement (instant):
        copy each section's session clips into the Arrangement with
        Track.duplicate_clip_to_arrangement. No real-time recording,
        no tempo changes. Then verify with get_arrangement_clips."""
        c = self.c
        print("[arrange] building arrangement via duplicate-to-arrangement")
        c.send("stop_playback")
        # Delete any extra tracks beyond the 7 main tracks
        r = c.send("get_all_tracks")
        existing_tracks = r.get("result", {}).get("tracks", [])
        for i in range(len(existing_tracks) - 1, len(TRACKS) - 1, -1):
            if i >= len(TRACKS):
                c.send_checked("delete_track", {"track_index": i}, f"delete extra track {i}")
                time.sleep(0.10)
        self.clear_arrangement()
        sections = []
        offset = 0
        for si, (sname, sbars) in enumerate(SCENES):
            for ti in range(len(TRACKS)):
                # No "notes" payload: duplicate_clip_to_arrangement copies
                # the (already correct) session-clip notes natively.
                sections.append({"track_index": ti, "clip_index": si,
                                 "position_bar": float(offset)})
            offset += sbars
        r = c.send_checked("build_arrangement", {"sections": sections},
                           "build_arrangement")
        res = (r or {}).get("result") or {}
        placed, total = res.get("placed"), res.get("total")
        print(f"[arrange] placed {placed}/{total} section-clips")
        for item in (res.get("items") or []):
            if item.get("status") != "ok":
                print(f"  [warn] t{item.get('track_index')} s{item.get('clip_index')}"
                      f" @bar {item.get('position_bar')}: {item.get('error')}")
        # Verify with the repaired reader
        vr = c.send("get_arrangement_clips")
        clips = ((vr or {}).get("result") or {}).get("arrangement_clips") or []
        per_track = {}
        for cl in clips:
            per_track[cl.get("track_index")] = per_track.get(cl.get("track_index"), 0) + 1
        starts = sorted(float(cl.get("start_time", 0)) for cl in clips)
        print(f"[arrange] verification: {len(clips)} arrangement clips "
              f"per-track {dict(sorted(per_track.items()))}")
        print(f"[arrange] start_times(beats): {starts}")
        print(f"[arrange] {offset} bars laid out: "
              + " ".join(f"{n}@{o}" for (n, b), o in
                         zip(SCENES, [0, 12, 28, 36, 60, 76, 84])))

    def capture(self):
        """Legacy real-time capture (~). Start playback, chain through
        scenes with manual triggers, record the result into the arrangement."""
        c = self.c
        c.send("set_playhead_position", {"bar": 0, "beat": 0})
        c.send("start_recording")
        c.send("start_playback")
        c.send("trigger_scene", {"scene_index": 0})
        bpm = 120.0
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
        print("Building STOIC-90: 90-minute minimal dub techno (fresh)")
        c.send("stop_playback")
        c.send_checked("delete_all_tracks", descr="delete_all_tracks")
        time.sleep(0.60)
        # Delete all scenes too
        c.send("stop_playback")
        for i in range(32):
            c.send("delete_scene", {"index": i})
            time.sleep(0.02)
        print("[tempo] 120 BPM")
        c.send_checked("set_tempo", {"tempo": 120.0}, "set_tempo")
        print("[tracks] 7 MIDI tracks + instruments + effects")
        for i, (name, uri, fx) in enumerate(TRACKS):
            self.create_track(i, name, uri, fx)
        self.build_clips()


def main():
    ap = argparse.ArgumentParser(
        description="Prepare a STOIC-90: 90-minute minimal dub techno")
    ap.add_argument("--fresh", action="store_true",
                    help="force full rebuild (delete all tracks + reload instruments)")
    ap.add_argument("--clips-only", action="store_true",
                    help="only rebuild clips, names, mix, tweaks, follow actions")
    ap.add_argument("--arrange", action="store_true",
                    help="also render the full arrangement via fast capture (~)")
    ap.add_argument("--capture", action="store_true",
                    help="also real-time record into Arrangement (~)")
    ap.add_argument("--no-auto", action="store_true",
                    help="skip writing clip automation arcs")
    ap.add_argument("--auto", action="store_true",
                    help="(default on with --arrange; kept for compat)")
    ap.add_argument("--random", action="store_true",
                    help="add subtle randomness: velocity, timing, note skipping")
    ap.add_argument("--seed", type=int, default=None,
                    help="RNG seed for reproducible randomness (requires --random)")
    args = ap.parse_args()

    # Seed RNG if --random or --seed specified
    if args.random or args.seed is not None:
        __init_random(args.seed if args.seed is not None else 42)
        print(f"[random] seeded with {RANDOM_SEED} - adding velocity/timing/skip randomness")

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
    mins = total_bars * 4 * 60 / 120 / 60
    print(f"\nReady: {total_bars} bars @ 120 BPM ~= {mins:.2f} min")
    print("Sections: " + " -> ".join(n for n, _ in SCENES))
    print("Fire scene 0 (INTRO) — follow actions chain all 7 sections for 90:00 of dub techno.")

    if args.arrange:
        dub.clear_arrangement()
        if not args.no_auto:
            print("\n[auto] writing clip automation arcs onto session "
                  "clips (capture route needs them during playback)")
            dub.automate(arrangement=False)
        # Try direct duplicate-to-arrangement (instant method)
        dub.arrange()
        if not args.no_auto:
            dub.verify_automation()
    elif not args.no_auto:
        print("\n[auto] writing clip automation arcs onto session clips")
        dub.automate(arrangement=False)
    if args.capture:
        print("\nRecording into Arrangement in real time (do not touch Live)")
        dub.capture()

    c.close()


if __name__ == "__main__":
    main()
