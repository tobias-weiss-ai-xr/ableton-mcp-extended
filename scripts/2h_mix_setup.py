#!/usr/bin/env python3
"""Build 8-track × 24-clip session for 2-hour automated mixing demo.

Creates session at 126 BPM in Fm with 24 scenes across energy arc:
Intro → Groove A → Build/Drop → Break → Groove B → Outro

Usage: python scripts/2h_mix_setup.py
Requires: Ableton Live with MCP Remote Script running on port 9877
"""

import socket
import json
import time
import sys

HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_PORT = 9878

BPM = 126
BAR = 4.0  # beats per bar at 4/4
CLIP_LEN = 32.0  # bars per clip

# Fm key notes
F2, G2, Ab2, C3, D3, Eb3 = 41, 43, 44, 48, 50, 51
F3, G3, Ab3, C4, D4, Eb4, E4 = 53, 55, 56, 60, 62, 63, 64
Bb3 = 58
F4, G4, Ab4, C5, D5, Eb5 = 65, 67, 68, 72, 74, 75
F5, G5 = 77, 79

# Beat positions (in beats, 0-indexed within clip)
B0, B1, B2, B3 = 0.0, 1.0, 2.0, 3.0


def tcp(cmd, params=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((HOST, TCP_PORT))
    msg = json.dumps({"type": cmd, "params": params or {}})
    sock.sendall((msg + "\n").encode())
    data = b""
    while True:
        try:
            chunk = sock.recv(262144)
        except socket.timeout:
            break
        if not chunk:
            break
        data += chunk
        sock.settimeout(0.5)  # Subsequent reads are quick
    sock.close()
    return json.loads(data.decode())


def udp(cmd, params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps({"type": cmd, "params": params}).encode(), (HOST, UDP_PORT))
    sock.close()


# ── Note pattern factories ──────────────────────────────────────────

def _kick_notes(clip_beats=CLIP_LEN):
    """4-on-the-floor kick pattern."""
    notes = []
    for b in range(0, int(clip_beats), 4):
        notes.append({"pitch": 36, "start_time": float(b), "duration": 0.5, "velocity": 110, "mute": False})
        notes.append({"pitch": 36, "start_time": float(b + 2.5), "duration": 0.25, "velocity": 85, "mute": False})
    return notes


def _kick_sparse(clip_beats=CLIP_LEN):
    """Sparse kick - dub style."""
    notes = []
    for b in range(0, int(clip_beats), 8):
        notes.append({"pitch": 36, "start_time": float(b), "duration": 0.5, "velocity": 100, "mute": False})
        notes.append({"pitch": 36, "start_time": float(b + 5.0), "duration": 0.25, "velocity": 80, "mute": False})
    return notes


def _kick_steppers(clip_beats=CLIP_LEN):
    """Steppers kick - even distribution."""
    notes = []
    for b in range(0, int(clip_beats), 4):
        notes.append({"pitch": 36, "start_time": float(b), "duration": 0.5, "velocity": 115, "mute": False})
    return notes


def _kick_half(clip_beats=CLIP_LEN):
    """Half-time kick."""
    notes = []
    for b in range(0, int(clip_beats), 8):
        notes.append({"pitch": 36, "start_time": float(b), "duration": 0.75, "velocity": 100, "mute": False})
    return notes


def _kick_minimal(clip_beats=CLIP_LEN):
    """Minimal kick - very sparse."""
    return [
        {"pitch": 36, "start_time": 0.0, "duration": 0.5, "velocity": 90, "mute": False},
        {"pitch": 36, "start_time": 12.0, "duration": 0.5, "velocity": 95, "mute": False},
        {"pitch": 36, "start_time": 24.0, "duration": 0.5, "velocity": 85, "mute": False},
    ]


# Snare patterns
def _snare_on_drop(clip_beats=CLIP_LEN):
    """One drop snare - 3rd beat emphasis."""
    notes = []
    for b in range(0, int(clip_beats), 8):
        notes.append({"pitch": 40, "start_time": float(b + 2.5), "duration": 0.25, "velocity": 105, "mute": False})
        notes.append({"pitch": 40, "start_time": float(b + 6.5), "duration": 0.25, "velocity": 105, "mute": False})
    return notes


def _snare_steppers(clip_beats=CLIP_LEN):
    """Steppers snare - on 2 and 4."""
    notes = []
    for b in range(0, int(clip_beats), 4):
        notes.append({"pitch": 40, "start_time": float(b + 2.0), "duration": 0.25, "velocity": 110, "mute": False})
    return notes


def _snare_sparse(clip_beats=CLIP_LEN):
    """Sparse snare."""
    notes = []
    for b in range(0, int(clip_beats), 12):
        notes.append({"pitch": 40, "start_time": float(b + 2.0), "duration": 0.25, "velocity": 95, "mute": False})
    return notes


def _snare_silent(clip_beats=CLIP_LEN):
    """No snare."""
    return []


# Hi-hat patterns
def _hat_8th(clip_beats=CLIP_LEN):
    """8th note hi-hats."""
    notes = []
    vel = 80
    for b in range(0, int(clip_beats) * 2):
        t = b * 0.5
        v = vel - 15 if b % 4 == 0 else vel  # accent every quarter
        notes.append({"pitch": 42, "start_time": t, "duration": 0.125, "velocity": v, "mute": False})
    return notes


def _hat_16th(clip_beats=CLIP_LEN):
    """16th note hi-hats."""
    notes = []
    for b in range(0, int(clip_beats) * 4):
        t = b * 0.25
        v = 85 if b % 4 == 0 else 70
        notes.append({"pitch": 42, "start_time": t, "duration": 0.1, "velocity": v, "mute": False})
    return notes


def _hat_off(clip_beats=CLIP_LEN):
    """Open hat on off-beats."""
    notes = []
    for b in range(0, int(clip_beats) * 4):
        t = b * 0.25
        if b % 2 == 1:
            notes.append({"pitch": 46, "start_time": t, "duration": 0.15, "velocity": 65, "mute": False})
    return notes


def _hat_sparse(clip_beats=CLIP_LEN):
    """Sparse hi-hats."""
    notes = []
    for b in range(0, int(clip_beats), 4):
        notes.append({"pitch": 42, "start_time": float(b + 0.5), "duration": 0.125, "velocity": 60, "mute": False})
        notes.append({"pitch": 42, "start_time": float(b + 2.5), "duration": 0.125, "velocity": 60, "mute": False})
    return notes


# Clap patterns
def _clap_four(clip_beats=CLIP_LEN):
    """Clap on 2 and 4."""
    notes = []
    for b in range(0, int(clip_beats)):
        if b % 2 == 1:
            notes.append({"pitch": 39, "start_time": float(b) + 0.9, "duration": 0.2, "velocity": 95, "mute": False})
    return notes


def _clap_sparse(clip_beats=CLIP_LEN):
    """Sparse claps."""
    notes = []
    for b in range(0, int(clip_beats), 4):
        if random_chance(0.6):
            notes.append({"pitch": 39, "start_time": float(b + 1.0), "duration": 0.2, "velocity": 85, "mute": False})
    return notes


def _clap_off(clip_beats=CLIP_LEN):
    return []


# Bass patterns (Fm - root F3)
def _bass_deep(clip_beats=CLIP_LEN):
    """Deep sustained bass - root notes."""
    notes = []
    for b in range(0, int(clip_beats), 8):
        notes.append({"pitch": F2, "start_time": float(b), "duration": 3.0, "velocity": 100, "mute": False})
        notes.append({"pitch": C3, "start_time": float(b + 4.0), "duration": 3.0, "velocity": 95, "mute": False})
    return notes


def _bass_walking(clip_beats=CLIP_LEN):
    """Walking bassline in Fm."""
    pattern = [F2, Ab2, C3, Eb3, F3, Eb3, C3, Ab2]
    notes = []
    for b in range(0, int(clip_beats)):
        i = b % len(pattern)
        notes.append({"pitch": pattern[i], "start_time": float(b), "duration": 0.75, "velocity": 105, "mute": False})
    return notes


def _bass_syncopated(clip_beats=CLIP_LEN):
    """Syncopated bass - offbeat emphasis."""
    pattern = [F2, 0, F2, 0, G2, Ab2, 0, C3]
    notes = []
    for b in range(0, int(clip_beats) // 2):
        for i, p in enumerate(pattern):
            if p:
                notes.append({"pitch": p, "start_time": float(b * 2 + i * 0.25), "duration": 0.5, "velocity": 100, "mute": False})
    return notes


def _bass_drone(clip_beats=CLIP_LEN):
    """Low drone bass."""
    return [
        {"pitch": F2, "start_time": 0.0, "duration": float(clip_beats), "velocity": 90, "mute": False},
    ]


def _bass_minimal(clip_beats=CLIP_LEN):
    """Very sparse bass."""
    notes = []
    for b in range(0, int(clip_beats), 8):
        notes.append({"pitch": F2, "start_time": float(b), "duration": 2.0, "velocity": 85, "mute": False})
    return notes


# Chord patterns (Fm voicings)
def _chords_sustain(clip_beats=CLIP_LEN):
    """Sustained Fm chords."""
    # Fm: F3-Ab3-C4, later Cm: C4-Eb4-G4, later Gm: G3-Bb3-D4
    chords = [
        [F3, Ab3, C4],
        [C4, Eb4, G4],
        [G3, Bb3, D4],
        [Ab3, C4, Eb4],
    ]
    notes = []
    bar_len = 8
    num_chords = int(clip_beats) // bar_len
    for i in range(num_chords):
        ch = chords[i % len(chords)]
        t = float(i * bar_len)
        for p in ch:
            notes.append({"pitch": p, "start_time": t, "duration": float(bar_len) * 0.9, "velocity": 85, "mute": False})
    return notes


def _chords_rhythmic(clip_beats=CLIP_LEN):
    """Rhythmic chord stabs."""
    chords = [
        [F3, Ab3, C4],
        [C4, Eb4, G4],
        [G3, Bb3, D4],
    ]
    notes = []
    bar_len = 8
    num_chords = int(clip_beats) // bar_len
    for i in range(num_chords):
        ch = chords[i % len(chords)]
        base = float(i * bar_len)
        # Stab on beat 0 and 3
        for offset in [0.0, 3.0]:
            for p in ch:
                notes.append({"pitch": p, "start_time": base + offset, "duration": 0.5, "velocity": 90, "mute": False})
    return notes


def _chords_arp(clip_beats=CLIP_LEN):
    """Arpeggiated chords."""
    arp = [F3, Ab3, C4, Ab3]
    notes = []
    for b in range(0, int(clip_beats)):
        p = arp[b % len(arp)]
        notes.append({"pitch": p, "start_time": float(b), "duration": 0.25, "velocity": 75, "mute": False})
    return notes


def _chords_sparse(clip_beats=CLIP_LEN):
    """Sparse sustained pads."""
    return [
        {"pitch": F3, "start_time": 0.0, "duration": 16.0, "velocity": 70, "mute": False},
        {"pitch": C4, "start_time": 8.0, "duration": 16.0, "velocity": 70, "mute": False},
        {"pitch": Ab3, "start_time": 16.0, "duration": 16.0, "velocity": 65, "mute": False},
    ]


# Melody patterns (Fm pentatonic scale)
PENTA = [F4, G4, Ab4, C5, D5, Eb5]

def _melody_phrase(clip_beats=CLIP_LEN):
    """Melodic phrase in Fm pentatonic."""
    phrase = [F4, Ab4, C5, D5, C5, Ab4, G4, F4]
    notes = []
    bar_len = 4
    num_phrases = int(clip_beats) // bar_len
    for i in range(num_phrases):
        base = float(i * bar_len)
        for j, p in enumerate(phrase):
            notes.append({"pitch": p, "start_time": base + j * 0.5, "duration": 0.4, "velocity": 85, "mute": False})
    return notes


def _melody_atmospheric(clip_beats=CLIP_LEN):
    """Atmospheric sustained melody notes."""
    pattern = [F5, Eb5, C5, Ab4, G4, Ab4, C5, F5]
    notes = []
    for b in range(0, int(clip_beats), 8):
        p = pattern[(b // 8) % len(pattern)]
        notes.append({"pitch": p, "start_time": float(b), "duration": 6.0, "velocity": 70, "mute": False})
    return notes


def _melody_rising(clip_beats=CLIP_LEN):
    """Rising melodic pattern."""
    notes = []
    rise = [F4, G4, Ab4, C5, D5, Eb5, F5, G5]
    for b in range(0, int(clip_beats)):
        i = (b // 2) % len(rise)
        p = rise[i]
        notes.append({"pitch": p, "start_time": float(b), "duration": 0.5, "velocity": 75, "mute": False})
    return notes


def _melody_sparse(clip_beats=CLIP_LEN):
    """Sparse melody - atmospheric highs."""
    notes = []
    for b in range(0, int(clip_beats), 4):
        if b % 8 == 0:
            notes.append({"pitch": F5, "start_time": float(b), "duration": 2.0, "velocity": 65, "mute": False})
        elif b % 8 == 4:
            notes.append({"pitch": Eb5, "start_time": float(b), "duration": 1.0, "velocity": 60, "mute": False})
    return notes


def _melody_empty(clip_beats=CLIP_LEN):
    return []


# FX/Texture patterns
def _fx_shimmer(clip_beats=CLIP_LEN):
    """High shimmer textures."""
    notes = []
    for b in range(0, int(clip_beats), 2):
        if b % 8 == 0:
            notes.append({"pitch": 80, "start_time": float(b), "duration": 0.5, "velocity": 50, "mute": False})
    return notes


def _fx_noise(clip_beats=CLIP_LEN):
    """Noise/sweep textures."""
    return [
        {"pitch": 84, "start_time": 0.0, "duration": 2.0, "velocity": 40, "mute": False},
        {"pitch": 86, "start_time": 8.0, "duration": 1.0, "velocity": 45, "mute": False},
        {"pitch": 83, "start_time": 16.0, "duration": 3.0, "velocity": 35, "mute": False},
    ]


def _fx_empty(clip_beats=CLIP_LEN):
    return []


import random
random_chance = lambda p: random.random() < p

# ── Instrument loading ───────────────────────────────────────────────

def _browse_category(category, max_level=3, max_per_level=4):
    """BFS for loadable items in a browser category via TCP.
    
    Returns list of (uri, name) tuples found.
    Makes at most ~(max_per_level^max_level) TCP calls.
    """
    found = []
    queue = [(category, 0)]
    visited = set()

    while queue and len(found) < 10:
        path, depth = queue.pop(0)
        if path in visited or depth > max_level:
            continue
        visited.add(path)

        try:
            resp = tcp("get_browser_items_at_path", {"path": path})
        except Exception:
            continue

        if not isinstance(resp, dict):
            continue

        result = resp.get("result") if resp.get("status") == "success" else resp
        if not isinstance(result, dict):
            continue

        for i, item in enumerate(result.get("items", [])):
            if i >= max_per_level:
                break
            if item.get("is_loadable") and item.get("uri"):
                found.append((item["uri"], item["name"]))
            if item.get("is_folder") and depth < max_level:
                queue.append((f"{path}/{item['name']}", depth + 1))

    return found


def _load_instruments():
    """Load instruments + effects onto all 8 tracks via browser discovery."""
    DRUM_TRACKS = [0, 1, 2, 3]
    MELODIC_TRACKS = [4, 5, 6, 7]

    print("\n[SETUP] Loading instruments via browser discovery...")

    # ── Drums ──────────────────────────────────────────────────────
    print("  Discovering drums…")
    drum_kits = _browse_category("drums", max_level=0, max_per_level=100)
    # Filter out empty Drum Rack and single-hit items
    drum_kits = [k for k in drum_kits if "Drum Rack" not in k[1] and "DS " not in k[1]]
    # Prefer genre-appropriate kit
    DUM_PREFS = ["Dub Techno", "808 Core", "909 Core", "Techno", "AG Techno", "House", "Standard"]
    kit_pick = None
    for pref in DUM_PREFS:
        for uri, n in drum_kits:
            if pref.lower() in n.lower():
                kit_pick = (uri, n)
                break
        if kit_pick:
            break
    if not kit_pick and drum_kits:
        kit_pick = drum_kits[0]

    if kit_pick:
        kit_uri, kit_name = kit_pick
        print(f"  Found drum kit: {kit_name}")
        for ti in DRUM_TRACKS:
            try:
                tcp("load_browser_item", {"track_index": ti, "item_uri": kit_uri})
                print(f"    Track {ti} ({TRACK_NAMES[ti]}): loaded {kit_name}")
                time.sleep(0.3)
            except Exception as e:
                print(f"    Track {ti} ({TRACK_NAMES[ti]}): FAILED - {e}")
    else:
        print("  WARNING: No drum kits found — drum tracks will be silent")

    # ── Melodic instruments ────────────────────────────────────────
    print("  Discovering melodic instruments…")
    # Only root-level instruments (not sub-folder presets) for clean selection
    inst_items = _browse_category("instruments", max_level=0, max_per_level=32)

    # Prefer specific instrument types per track (searched in order of preference)
    # Each track gets a DIFFERENT instrument by consuming from the pool
    INST_PREFS = {
        4: ["Analog", "Drift", "Operator", "Bass"],
        5: ["Electric", "Poli", "Meld", "Analog"],
        6: ["Emit", "Poli", "Drift", "Analog", "Meld"],
        7: ["Granulator III", "Emit", "Analog", "Operator"],
    }

    if inst_items:
        available = list(inst_items)
        for ti in MELODIC_TRACKS:
            prefs = INST_PREFS[ti]
            pick = None
            for pref in prefs:
                for uri, n in available:
                    if pref.lower() in n.lower():
                        pick = (uri, n)
                        break
                if pick:
                    break
            if not pick and available:
                pick = available[0]
            if pick:
                available = [p for p in available if p[0] != pick[0]]
                uri, name = pick
            else:
                print(f"    Track {ti} ({TRACK_NAMES[ti]}): NO INSTRUMENTS AVAILABLE")
                continue
            try:
                tcp("load_browser_item", {"track_index": ti, "item_uri": uri})
                print(f"    Track {ti} ({TRACK_NAMES[ti]}): loaded {name}")
                time.sleep(0.3)
            except Exception as e:
                print(f"    Track {ti} ({TRACK_NAMES[ti]}): FAILED - {e}")
    else:
        print("  WARNING: No instruments found — melodic tracks will be silent")

    # ── Audio effects (reverb / delay on melodic tracks) ───────────
    print("  Discovering audio effects…")
    fx_items = _browse_category("audio_effects", max_level=0, max_per_level=50)

    reverb = None
    delay = None
    for uri, name in fx_items:
        low = name.lower()
        if "reverb" in low and not reverb:
            reverb = (uri, name)
        if "delay" in low and not delay:
            delay = (uri, name)

    if reverb:
        uri, name = reverb
        for ti in MELODIC_TRACKS:
            try:
                tcp("load_browser_item", {"track_index": ti, "item_uri": uri})
                print(f"    Track {ti}: added reverb")
                time.sleep(0.2)
            except Exception:
                pass

    if delay:
        uri, name = delay
        for ti in MELODIC_TRACKS:
            try:
                tcp("load_browser_item", {"track_index": ti, "item_uri": uri})
                print(f"    Track {ti}: added delay")
                time.sleep(0.2)
            except Exception:
                pass

    print("[SETUP] Instrument loading complete")


# ── Scene definitions ────────────────────────────────────────────────

SCENES = [
    # (name, energy) - 24 scenes
    ("Intro", 1),
    ("Intro_2", 2),
    ("Intro_3", 3),
    ("Intro_4", 3),
    ("Groove_A", 4),
    ("Groove_A2", 5),
    ("Groove_A3", 5),
    ("Groove_A4", 6),
    ("Build", 6),
    ("Build_2", 7),
    ("Drop", 8),
    ("Drop_Recover", 5),
    ("Break", 2),
    ("Break_2", 3),
    ("Break_3", 3),
    ("Break_4", 4),
    ("Groove_B", 5),
    ("Groove_B2", 6),
    ("Groove_B3", 7),
    ("Groove_B4", 8),
    ("Outro", 4),
    ("Outro_2", 3),
    ("Outro_3", 2),
    ("Outro_4", 1),
]

# Clip patterns per track per scene (index → note factory function)
# Track 0=Kick, 1=Snare, 2=HiHat, 3=Clap, 4=Bass, 5=Chords, 6=Melody, 7=FX

CLIP_PATTERNS = {
    0: [  # Kick
        _kick_minimal, _kick_minimal, _kick_sparse, _kick_sparse,
        _kick_notes, _kick_notes, _kick_notes, _kick_steppers,
        _kick_steppers, _kick_steppers, _kick_steppers, _kick_notes,
        _kick_sparse, _kick_sparse, _kick_notes, _kick_notes,
        _kick_notes, _kick_steppers, _kick_steppers, _kick_steppers,
        _kick_half, _kick_sparse, _kick_sparse, _kick_minimal,
    ],
    1: [  # Snare
        _snare_silent, _snare_silent, _snare_sparse, _snare_sparse,
        _snare_on_drop, _snare_on_drop, _snare_on_drop, _snare_steppers,
        _snare_steppers, _snare_steppers, _snare_steppers, _snare_on_drop,
        _snare_sparse, _snare_sparse, _snare_on_drop, _snare_on_drop,
        _snare_on_drop, _snare_steppers, _snare_steppers, _snare_steppers,
        _snare_on_drop, _snare_sparse, _snare_sparse, _snare_silent,
    ],
    2: [  # HiHat
        _hat_sparse, _hat_off, _hat_off, _hat_8th,
        _hat_8th, _hat_8th, _hat_16th, _hat_16th,
        _hat_16th, _hat_16th, _hat_16th, _hat_8th,
        _hat_sparse, _hat_off, _hat_8th, _hat_8th,
        _hat_8th, _hat_16th, _hat_16th, _hat_16th,
        _hat_8th, _hat_off, _hat_sparse, _hat_sparse,
    ],
    3: [  # Clap
        _clap_off, _clap_off, _clap_sparse, _clap_sparse,
        _clap_four, _clap_four, _clap_four, _clap_four,
        _clap_four, _clap_four, _clap_four, _clap_four,
        _clap_sparse, _clap_sparse, _clap_four, _clap_four,
        _clap_four, _clap_four, _clap_four, _clap_four,
        _clap_four, _clap_sparse, _clap_off, _clap_off,
    ],
    4: [  # Bass
        _bass_drone, _bass_minimal, _bass_deep, _bass_deep,
        _bass_walking, _bass_walking, _bass_walking, _bass_syncopated,
        _bass_syncopated, _bass_syncopated, _bass_walking, _bass_deep,
        _bass_minimal, _bass_drone, _bass_deep, _bass_deep,
        _bass_walking, _bass_syncopated, _bass_syncopated, _bass_walking,
        _bass_deep, _bass_minimal, _bass_drone, _bass_drone,
    ],
    5: [  # Chords
        _chords_sparse, _chords_sparse, _chords_sustain, _chords_sustain,
        _chords_rhythmic, _chords_rhythmic, _chords_rhythmic, _chords_arp,
        _chords_arp, _chords_arp, _chords_rhythmic, _chords_sustain,
        _chords_sparse, _chords_sparse, _chords_sustain, _chords_sustain,
        _chords_rhythmic, _chords_arp, _chords_arp, _chords_rhythmic,
        _chords_sustain, _chords_sparse, _chords_sparse, _chords_sparse,
    ],
    6: [  # Melody
        _melody_empty, _melody_sparse, _melody_sparse, _melody_atmospheric,
        _melody_phrase, _melody_phrase, _melody_phrase, _melody_rising,
        _melody_rising, _melody_rising, _melody_phrase, _melody_atmospheric,
        _melody_sparse, _melody_sparse, _melody_atmospheric, _melody_atmospheric,
        _melody_phrase, _melody_rising, _melody_rising, _melody_phrase,
        _melody_atmospheric, _melody_sparse, _melody_sparse, _melody_empty,
    ],
    7: [  # FX
        _fx_empty, _fx_empty, _fx_shimmer, _fx_shimmer,
        _fx_noise, _fx_noise, _fx_shimmer, _fx_shimmer,
        _fx_noise, _fx_noise, _fx_shimmer, _fx_empty,
        _fx_empty, _fx_empty, _fx_shimmer, _fx_shimmer,
        _fx_noise, _fx_shimmer, _fx_noise, _fx_shimmer,
        _fx_shimmer, _fx_empty, _fx_empty, _fx_empty,
    ],
}

TRACK_NAMES = ["Kick", "Snare", "HiHat", "Clap", "Bass", "Chords", "Melody", "FX"]
NUM_TRACKS = len(TRACK_NAMES)
NUM_SCENES = len(SCENES)


def create_session():
    """Build the complete session."""
    print(f"[SETUP] Building {NUM_TRACKS} tracks × {NUM_SCENES} scenes at {BPM} BPM in Fm")

    # Clean slate
    print("[SETUP] Deleting all tracks...")
    tcp("delete_all_tracks")

    # Set tempo
    tcp("set_tempo", {"tempo": BPM})
    time.sleep(0.5)

    # Create MIDI tracks
    print("[SETUP] Creating MIDI tracks...")
    for i in range(NUM_TRACKS):
        tcp("create_midi_track", {"index": i})
        time.sleep(0.2)

    # Name tracks
    for i, name in enumerate(TRACK_NAMES):
        tcp("set_track_name", {"track_index": i, "name": name})
    time.sleep(0.5)

    # Load instruments and effects on all tracks
    _load_instruments()
    time.sleep(0.5)

    # Create scenes and name them
    print("[SETUP] Creating scenes...")
    for i in range(NUM_SCENES):
        tcp("create_scene", {"index": i})
    time.sleep(0.3)

    for i, (name, _) in enumerate(SCENES):
        tcp("set_scene_name", {"scene_index": i, "name": f"{i}_{name}"})

    # Create all clips
    print("[SETUP] Creating clips and populating patterns...")
    for track_idx in range(NUM_TRACKS):
        patterns = CLIP_PATTERNS[track_idx]
        for clip_idx in range(NUM_SCENES):
            scene_name, energy = SCENES[clip_idx]
            clip_len = CLIP_LEN

            # Create clip
            tcp("create_clip", {"track_index": track_idx, "clip_index": clip_idx, "length": clip_len})
            time.sleep(0.05)

            # Generate notes
            note_factory = patterns[clip_idx]
            notes = note_factory(clip_len)

            if notes:
                tcp("add_notes_to_clip", {
                    "track_index": track_idx,
                    "clip_index": clip_idx,
                    "notes": notes,
                })
                print(f"  Track {track_idx} ({TRACK_NAMES[track_idx]}) clip {clip_idx} ({scene_name}): {len(notes)} notes")
            else:
                print(f"  Track {track_idx} ({TRACK_NAMES[track_idx]}) clip {clip_idx} ({scene_name}): EMPTY")

            time.sleep(0.03)

    print(f"[SETUP] Done - created {NUM_TRACKS} tracks × {NUM_SCENES} clips = {NUM_TRACKS * NUM_SCENES} total clips")
    print(f"[SETUP] Session ready at {BPM} BPM in Fm")


if __name__ == "__main__":
    create_session()
