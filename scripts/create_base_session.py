#!/usr/bin/env python3
"""
Create a solid dub/techno base session in Ableton Live.

Sets up 6 tracks with instruments, a 4-scene structure, drum patterns,
bass line, chords, pad, and effects — ready for you to jam on or extend
into a full mix.

Usage:
    python scripts/create_base_session.py

Requirements:
    - Ableton Live running with MCP Remote Script (TCP port 9877)
    - Suite edition recommended (instruments + effects)
"""

import json
import socket
import sys
import time

# ─── MIDI note numbers ────────────────────────────────────────────────────
# C minor pentatonic across two octaves (good for dub/techno)
NOTES = {
    "C2": 36, "D2": 38, "Eb2": 39, "F2": 41, "G2": 43,
    "C3": 48, "D3": 50, "Eb3": 51, "F3": 53, "G3": 55, "Bb3": 58,
    "C4": 60, "D4": 62, "Eb4": 63, "F4": 65, "G4": 67, "Bb4": 70,
    "C5": 72, "Eb5": 75, "G5": 79,
}

CHORD_SETS = [
    [48, 51, 55, 58],   # Cm7  — C Eb G Bb
    [53, 56, 60, 63],   # Fm7  — F Ab C Eb
    [55, 58, 62, 65],   # Gm7  — G Bb D F
    [56, 60, 63, 67],   # Abmaj — Ab C Eb G
]

PAD_NOTES = [60, 63, 67, 72]  # Cm spread across octaves


class AbletonClient:
    """TCP client for the Ableton Remote Script."""

    def __init__(self, host="localhost", port=9877):
        self.host, self.port = host, port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(15)
            self.sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERR] Cannot connect to {self.host}:{self.port}: {e}")
            return False

    def send(self, cmd, params=None):
        if self.sock is None and not self.connect():
            return {"status": "error"}
        msg = json.dumps({"type": cmd, "params": params or {}}).encode() + b"\n"
        try:
            self.sock.sendall(msg)
            raw = self.sock.recv(8192).decode()
            return json.loads(raw) if raw else {"status": "ok"}
        except Exception as e:
            print(f"[ERR] {cmd}: {e}")
            self.sock = None
            return {"status": "error"}

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


# ─── UDP sender (fire-and-forget for fast parameter changes) ──────────────

def udp_send(cmd, params=None):
    """Send a single UDP command (no response expected)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(json.dumps({"type": cmd, "params": params or {}}).encode(),
                 ("localhost", 9878))
        s.close()
    except Exception:
        pass


def set_volume(track, vol):
    """Set track volume (0.0-1.0 normalized)."""
    udp_send("set_track_volume", {"track_index": track, "volume": vol})


def set_pan(track, pan):
    """Set track pan (0=left, 0.5=center, 1.0=right)."""
    udp_send("set_track_pan", {"track_index": track, "pan": pan})


def set_send(track, send_idx, amount):
    """Set send amount (0.0-1.0)."""
    udp_send("set_send_amount", {"track_index": track, "send_index": send_idx, "amount": amount})


# ─── Build functions ───────────────────────────────────────────────────────

def note(pitch, start_beat, duration_beats=1.0, velocity=100):
    """Shorthand for a MIDI note dict."""
    return {"pitch": pitch, "start": float(start_beat), "duration": float(duration_beats), "velocity": velocity}


def create_track(c, index, name, instrument_uri=None):
    """Create a MIDI track, name it, optionally load an instrument."""
    print(f"  Track {index}: {name}")
    c.send("create_midi_track", {"index": index})
    time.sleep(0.15)
    c.send("set_track_name", {"track_index": index, "name": name})
    if instrument_uri:
        c.send("load_instrument_or_effect", {"track_index": index, "uri": instrument_uri})
        time.sleep(0.4)  # instrument loading takes a moment
    return index


def create_clip_with_notes(c, track_idx, clip_idx, length, notes, quantize=True):
    """Create a clip and add notes to it."""
    c.send("create_clip", {"track_index": track_idx, "clip_index": clip_idx, "length": length})
    time.sleep(0.08)
    c.send("add_notes_to_clip", {
        "track_index": track_idx,
        "clip_index": clip_idx,
        "notes": notes,
    })


def build_drum_patterns():
    """Return dict of scene_idx -> drum note list for 1-bar patterns."""
    # Drum Rack: slot 0=kick, 1=snare, 2=hat_closed, 3=hat_open, 4=perc, 5=clap
    patterns = {
        0: [  # Scene 0: "Root" — sparse one-drop
            note(36, 0.0, 0.25, 110),    # kick on 1
            note(38, 1.0, 0.2, 85),      # snare ghost
            note(36, 2.0, 0.25, 105),    # kick on 3
            note(38, 3.0, 0.15, 75),     # snare ghost
            # hi-hats — sparse
            note(42, 0.0, 0.1, 60),
            note(42, 1.0, 0.1, 55),
            note(42, 2.0, 0.1, 60),
            note(42, 3.0, 0.1, 55),
        ],
        1: [  # Scene 1: "Steppers" — four-on-floor
            note(36, 0.0, 0.2, 105),
            note(36, 1.0, 0.2, 100),
            note(36, 2.0, 0.2, 105),
            note(36, 3.0, 0.2, 100),
            note(38, 1.0, 0.15, 90),     # snare on 2
            note(38, 3.0, 0.15, 85),     # snare on 4
            note(42, 0.5, 0.08, 50),
            note(42, 1.5, 0.08, 50),
            note(42, 2.5, 0.08, 50),
            note(42, 3.5, 0.08, 50),
        ],
        2: [  # Scene 2: "Half-time" — open, dub feel
            note(36, 0.0, 0.3, 115),     # heavy kick
            note(38, 2.0, 0.25, 95),     # snare on 3
            note(46, 2.5, 0.15, 70),    # rim accent
            note(42, 0.0, 0.08, 45),
            note(42, 1.0, 0.08, 40),
            note(42, 2.0, 0.08, 45),
            note(42, 3.0, 0.08, 40),
        ],
        3: [  # Scene 3: "Build" — busy hats, syncopated
            note(36, 0.0, 0.2, 100),
            note(36, 1.5, 0.2, 95),
            note(36, 2.0, 0.2, 105),
            note(36, 3.5, 0.2, 100),
            note(38, 1.0, 0.12, 80),
            note(38, 3.0, 0.12, 75),
            note(42, 0.0, 0.06, 55),
            note(42, 0.25, 0.06, 50),
            note(42, 0.5, 0.06, 55),
            note(42, 0.75, 0.06, 45),
            note(42, 1.0, 0.06, 50),
            note(42, 1.5, 0.06, 55),
            note(42, 2.0, 0.06, 50),
            note(42, 2.5, 0.06, 55),
            note(42, 2.75, 0.06, 45),
            note(42, 3.0, 0.06, 50),
            note(42, 3.5, 0.06, 55),
        ],
    }
    return patterns


def build_bass_lines():
    """Root-note bass lines per scene (1 bar each)."""
    lines = {
        0: [note(36, 0.0, 1.5, 95), note(43, 1.5, 0.5, 70),
            note(36, 2.0, 1.5, 90), note(48, 3.5, 0.5, 65)],
        1: [note(36, 0.0, 0.5, 90), note(36, 1.0, 0.5, 85),
            note(43, 2.0, 0.5, 85), note(43, 3.0, 0.5, 80)],
        2: [note(36, 0.0, 2.0, 100), note(41, 2.0, 1.0, 80),
            note(43, 3.0, 1.0, 75)],
        3: [note(36, 0.0, 0.25, 95), note(36, 0.5, 0.25, 90),
            note(43, 1.0, 0.25, 85), note(43, 1.5, 0.25, 80),
            note(36, 2.0, 0.25, 90), note(41, 2.5, 0.25, 85),
            note(43, 3.0, 0.5, 80)],
    }
    return lines


def build_chord_stabs():
    """Stab chords per scene (half-bar or whole-bar)."""
    stabs = {
        0: [note(p, 0.0, 2.0, v) for p, v in zip(CHORD_SETS[0], [70, 65, 60, 55])],
        1: [note(p, 0.0, 1.0, v) for p, v in zip(CHORD_SETS[0], [65, 60, 55, 50])]
           + [note(p, 2.0, 1.0, v) for p, v in zip(CHORD_SETS[1], [65, 60, 55, 50])],
        2: [note(p, 1.0, 2.0, v) for p, v in zip(CHORD_SETS[2], [60, 55, 50, 45])],
        3: [note(p, 0.0, 0.5, v) for p, v in zip(CHORD_SETS[0], [75, 70, 65, 60])]
           + [note(p, 2.0, 0.5, v) for p, v in zip(CHORD_SETS[3], [70, 65, 60, 55])],
    }
    return stabs


def build_pad_layer():
    """Sustained pad chord per scene (whole bar)."""
    pads = {
        0: [note(p, 0.0, 4.0, v) for p, v in zip(CHORD_SETS[0], [45, 40, 38, 35])],
        1: [note(p, 0.0, 4.0, v) for p, v in zip(CHORD_SETS[1], [42, 38, 35, 32])],
        2: [note(p, 0.0, 4.0, v) for p, v in zip(CHORD_SETS[2], [40, 36, 33, 30])],
        3: [note(p, 0.0, 4.0, v) for p, v in zip(CHORD_SETS[3], [42, 38, 35, 32])],
    }
    return pads


def build_melody_fragments():
    """Simple melodic fragments per scene — pentatonic licks."""
    melodies = {
        0: [note(67, 2.5, 0.5, 80), note(70, 3.0, 0.75, 75), note(72, 3.75, 0.25, 70)],
        1: [note(63, 0.5, 0.25, 75), note(67, 0.75, 0.5, 70), note(72, 1.5, 0.5, 65)],
        2: [note(72, 2.0, 1.0, 70), note(75, 3.0, 1.0, 65)],
        3: [note(63, 0.0, 0.25, 80), note(67, 0.25, 0.25, 75),
            note(70, 1.0, 0.25, 80), note(75, 1.25, 0.5, 70),
            note(79, 2.5, 0.25, 75), note(75, 2.75, 0.25, 70),
            note(72, 3.0, 0.5, 65), note(67, 3.5, 0.5, 60)],
    }
    return melodies


def build_sub_bass():
    """Sub-bass reinforcement per scene (simple root)."""
    # Pitch 24 = C1, 29 = F1, 31 = G1
    subs = {
        0: [note(24, 0.0, 2.0, 80), note(24, 2.0, 2.0, 75)],
        1: [note(24, 0.0, 1.0, 78), note(24, 2.0, 1.0, 75)],
        2: [note(24, 0.0, 4.0, 82)],
        3: [note(24, 0.0, 0.5, 80), note(24, 2.0, 0.5, 78)],
    }
    return subs


def build_fx_risers():
    """FX/perc hits per scene."""
    fx = {
        0: [],  # Root scene — clean
        1: [note(60, 3.75, 0.1, 100)],  # conga hit before scene change
        2: [note(60, 3.5, 0.08, 95)],   # percussion accent
        3: [note(60, 3.25, 0.06, 90), note(60, 3.5, 0.06, 95), note(60, 3.75, 0.1, 100)],
    }
    return fx


# ─── Main build ────────────────────────────────────────────────────────────

def build_base_session():
    c = AbletonClient()
    if not c.connect():
        print("\nMake sure Ableton Live is running with the MCP Remote Script.")
        print("Check that TCP port 9877 is active.")
        sys.exit(1)

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Building dub/techno base session                        ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # 1. Clean slate
    print("[1/7] Clearing existing tracks...")
    c.send("delete_all_tracks")
    time.sleep(0.5)

    # 2. Tempo
    print("[2/7] Setting tempo to 75 BPM...")
    c.send("set_tempo", {"tempo": 75.0})
    c.send("set_global_quantization", {"value": "1 Bar"})

    # 3. Create tracks (order matters — these become track indices 0-6)
    print("[3/7] Creating tracks...")
    drum_kit = "query:Drums#FileId_58622"

    create_track(c, 0, "DRUMS", drum_kit)
    create_track(c, 1, "BASS", "query:Instruments#Wavetable")
    create_track(c, 2, "SUB BASS", "query:Instruments#Operator")
    create_track(c, 3, "CHORDS", "query:Instruments#Wavetable")
    create_track(c, 4, "PADS", "query:Instruments#Analog")
    create_track(c, 5, "MELODY", "query:Instruments#Wavetable")
    create_track(c, 6, "FX/PERC", drum_kit)  # second drum rack for percussion

    # 4. Create clips for 4 scenes
    print("[4/7] Creating 4 scenes with clips...")
    clips = {
        "drums":    build_drum_patterns(),
        "bass":     build_bass_lines(),
        "sub":      build_sub_bass(),
        "chords":   build_chord_stabs(),
        "pads":     build_pad_layer(),
        "melody":   build_melody_fragments(),
        "fx":       build_fx_risers(),
    }

    for scene in range(4):
        for track_idx, key in enumerate(["drums", "bass", "sub", "chords", "pads", "melody", "fx"]):
            notes = clips[key][scene]
            if notes:
                create_clip_with_notes(c, track_idx, scene, 4.0, notes)
        print(f"  Scene {scene}: ✓")

    # 5. Load effects on return tracks (sends)
    print("[5/7] Setting up return-track effects...")
    c.send("load_instrument_or_effect", {"track_index": 0, "uri": "query:Audio Effects#Reverb"})
    time.sleep(0.3)
    c.send("load_instrument_or_effect", {"track_index": 1, "uri": "query:Audio Effects#Delay"})
    time.sleep(0.3)
    c.send("load_instrument_or_effect", {"track_index": 2, "uri": "query:Audio Effects#EQ Eight"})
    time.sleep(0.3)
    # Note: load_instrument_or_effect loads on track devices, not returns.
    # For a clean base, we'll set send levels per-track below.

    # 6. Mix balance
    print("[6/7] Setting mix levels...")
    # Volume (0.0=silent, 0.75=unity-ish, 1.0=max)
    set_volume(0, 0.72)   # Drums — slightly hot
    set_volume(1, 0.65)   # Bass — present
    set_volume(2, 0.58)   # Sub bass — felt not heard
    set_volume(3, 0.50)   # Chords — background
    set_volume(4, 0.42)   # Pads — atmosphere
    set_volume(5, 0.55)   # Melody — foreground
    set_volume(6, 0.48)   # FX/perc — textural

    # Panning — stereo spread
    set_pan(0, 0.50)    # Drums — center
    set_pan(1, 0.50)    # Bass — center (always!)
    set_pan(2, 0.50)    # Sub — center (always!)
    set_pan(3, 0.58)    # Chords — slight right
    set_pan(4, 0.42)    # Pads — slight left
    set_pan(5, 0.55)    # Melody — slight right
    set_pan(6, 0.45)    # FX — slight left

    # Send levels (reverb=send 0, delay=send 1)
    # Drums → tiny reverb, no delay
    set_send(0, 0, 0.08)
    set_send(0, 1, 0.00)
    # Bass → no reverb (muddies low end), tiny delay
    set_send(1, 0, 0.00)
    set_send(1, 1, 0.05)
    # Sub → nothing (keep it clean)
    set_send(2, 0, 0.00)
    set_send(2, 1, 0.00)
    # Chords → moderate reverb, no delay
    set_send(3, 0, 0.22)
    set_send(3, 1, 0.00)
    # Pads → heavy reverb, some delay for depth
    set_send(4, 0, 0.40)
    set_send(4, 1, 0.15)
    # Melody → moderate reverb + delay
    set_send(5, 0, 0.20)
    set_send(5, 1, 0.18)
    # FX/perc → heavy reverb, moderate delay (washy)
    set_send(6, 0, 0.35)
    set_send(6, 1, 0.25)

    # 7. Summary
    print("[7/7] Done!\n")
    print("┌─────────────────────────────────────────────────────┐")
    print("│  BASE SESSION READY                                   │")
    print("│                                                     │")
    print("│  Track layout:                                       │")
    print("│   0  DRUMS     — one-drop / steppers / build          │")
    print("│   1  BASS      — Wavetable, root notes               │")
    print("│   2  SUB BASS  — Operator, sub reinforcement          │")
    print("│   3  CHORDS    — Wavetable, stab triads              │")
    print("│   4  PADS      — Analog, sustained atmosphere          │")
    print("│   5  MELODY    — Wavetable, pentatonic licks          │")
    print("│   6  FX/PERC   — Drum Rack, textural hits           │")
    print("│                                                     │")
    print("│  4 Scenes:                                           │")
    print("│   Scene 0 — ROOT   (sparse, one-drop groove)         │")
    print("│   Scene 1 — STEP   (four-on-floor, steady)             │")
    print("│   Scene 2 — HALF   (open, dub feel, space)           │")
    print("│   Scene 3 — BUILD  (busy hats, syncopated energy)    │")
    print("│                                                     │")
    print("│  BPM: 75  |  Quantize: 1 Bar                         │")
    print("│  Key: C minor pentatonic                             │")
    print("│                                                     │")
    print("│  Tips:                                              │")
    print("│  • Fire scenes 0→1→2→3 for a natural progression    │")
    print("│  • Duplicate scenes to extend to 8/16 bars each     │")
    print("│  • Swap chord stabs to try different voicings        │")
    print("│  • Add a return-track reverb and route sends there  │")
    print("│  • Record arm melody track and jam over the top     │")
    print("│  • Use the delay send (send 1) for dub echoes         │")
    print("└─────────────────────────────────────────────────────┘")

    c.close()


if __name__ == "__main__":
    build_base_session()
