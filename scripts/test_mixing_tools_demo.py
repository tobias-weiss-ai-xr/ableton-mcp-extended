#!/usr/bin/env python3
"""Standalone test: build a 6-track session and exercise every mixing tool.

Each mixing test replicates the MCP tool logic via the same TCP/UDP primitives.
Run with MCP server + Remote Script running.
"""

import socket
import json
import time

TCP_HOST = "127.0.0.1"
TCP_PORT = 9877
UDP_PORT = 9878
_tcp = None


# -- protocol helpers ------------------------------------------------------

def tcp(cmd, params=None):
    global _tcp
    if _tcp is None:
        _tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _tcp.connect((TCP_HOST, TCP_PORT))
    msg = json.dumps({"type": cmd, "params": params or {}})
    _tcp.sendall((msg + "\n").encode())
    resp = _tcp.recv(70000).decode().strip()
    return json.loads(resp) if resp else {}


def udp(cmd, params):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(json.dumps({"type": cmd, "params": params}).encode(), (TCP_HOST, UDP_PORT))
    s.close()


def step_param(track, device, param, value):
    udp("set_device_parameter", {
        "track_index": track, "device_index": device,
        "parameter_index": param, "value": value,
    })


def step_vol(track, vol):
    udp("set_track_volume", {"track_index": track, "volume": round(vol, 2)})


def get_tempo():
    r = tcp("get_session_info")
    return float(r.get("tempo", 120))


def bs(b, bpm=None):
    if bpm is None:
        bpm = get_tempo()
    return b * 60.0 / bpm


def section(n, title):
    print(f"\n{'-' * 60}\n  [{n}] {title}\n{'-' * 60}")


# -- step 1: build session ------------------------------------------------

print("=" * 60)
print("  MIXING TOOLS -- FULL DEMONSTRATION")
print("  8 exercises of the new mixing capabilities")
print("=" * 60)

section(1, "Session Setup")
print("Clearing all tracks…")
tcp("delete_all_tracks")

names = ["Kick", "Snare", "HiHat", "Bass", "Chords", "Melody"]
track = {}
for n in names:
    tcp("create_midi_track", {"index": -1})
    i = track.get("_c", 0)
    tcp("set_track_name", {"track_index": i, "name": n})
    track[n] = i
    track["_c"] = i + 1
    print(f"  {i}: {n}")

tcp("set_tempo", {"tempo": 126})
print("  Tempo -> 126 BPM")

# -- drum clips --
for n, pat in [("Kick","techno_4x4"), ("Snare","steppers"), ("HiHat","house_basic")]:
    tcp("create_clip", {"track_index": track[n], "clip_index": 0, "length": 4})
    tcp("create_drum_pattern", {"track_index": track[n], "clip_index": 0, "pattern_name": pat, "length": 4})
print("  Drums: Kick->4×4  Snare->steppers  HiHat->house")

# -- bass --
tcp("create_clip", {"track_index": track["Bass"], "clip_index": 0, "length": 8})
tcp("add_notes_to_clip", {"track_index": track["Bass"], "clip_index": 0, "notes": [
    {"pitch":41,"start_time":0,"duration":3.5,"velocity":100,"mute":False},
    {"pitch":41,"start_time":4,"duration":1,"velocity":90,"mute":False},
    {"pitch":43,"start_time":5,"duration":1,"velocity":90,"mute":False},
    {"pitch":44,"start_time":6,"duration":2,"velocity":95,"mute":False},
]})
print("  Bass -> 4-note Fm line")

# -- chords --
tcp("create_clip", {"track_index": track["Chords"], "clip_index": 0, "length": 8})
chords = []
for bt, rt in [(0,53),(2,51),(4,48),(6,46)]:
    for o in (0,3,7,10):
        chords.append({"pitch":rt+o,"start_time":bt,"duration":1.9,"velocity":78,"mute":False})
tcp("add_notes_to_clip", {"track_index": track["Chords"], "clip_index": 0, "notes": chords})
print("  Chords -> Fm voicings")

# -- melody --
tcp("create_clip", {"track_index": track["Melody"], "clip_index": 0, "length": 8})
tcp("add_notes_to_clip", {"track_index": track["Melody"], "clip_index": 0, "notes": [
    {"pitch":60,"start_time":0,"duration":0.5,"velocity":85,"mute":False},
    {"pitch":63,"start_time":1,"duration":0.5,"velocity":80,"mute":False},
    {"pitch":65,"start_time":2,"duration":0.5,"velocity":85,"mute":False},
    {"pitch":67,"start_time":3,"duration":1,"velocity":90,"mute":False},
    {"pitch":65,"start_time":4,"duration":0.5,"velocity":80,"mute":False},
    {"pitch":63,"start_time":5,"duration":0.5,"velocity":80,"mute":False},
    {"pitch":60,"start_time":6,"duration":2,"velocity":75,"mute":False},
]})
print("  Melody -> Fm phrase")

# -- scenes --
for si in range(1, 6):
    tcp("create_scene", {"index": -1})
    tcp("set_scene_name", {"scene_index": si, "name": f"Part{si}"})
    for n in names:
        src = tcp("get_clip_notes", {"track_index": track[n], "clip_index": 0})
        if isinstance(src, dict) and src.get("notes"):
            tcp("create_clip", {"track_index": track[n], "clip_index": si, "length": 8})
            tcp("add_notes_to_clip", {"track_index": track[n], "clip_index": si, "notes": src["notes"]})
print("  Scenes 1-5 ready")

print("\nStarting playback…")
tcp("start_playback")
time.sleep(0.5)
for n in names:
    tcp("fire_clip", {"track_index": track[n], "clip_index": 0})
print("  All clips fired.\n")

bpm = get_tempo()


# -- step 2: metering -----------------------------------------------------

section(2, "Metering -- get_level_snapshot")
r = tcp("get_level_snapshot")
for td in r.get("tracks", [])[:6]:
    print(f"  {td.get('name','?'):8s}  L={td.get('output_meter_left',0):.3f}  "
          f"R={td.get('output_meter_right',0):.3f}  vol={td.get('volume',0):.2f}")
print("  ✓ Metering: all track levels read")


# -- step 3: bass-forward mix ---------------------------------------------

section(3, "Bass-Forward Mix -- apply_bass_forward_mix")
others = [track["Kick"], track["HiHat"], track["Chords"], track["Melody"]]
step_vol(track["Bass"], 0.88)
for o in others:
    step_vol(o, 0.50)
step_param(track["Bass"], 0, 2, 0.2)
print("  Bass->0.88  Others->0.50  Filter->0.2  ✓")
time.sleep(bs(4, bpm))


# -- step 4: dub drop -----------------------------------------------------

section(4, "Dub Drop -- apply_dub_drop")
drops = [track["Bass"], track["Chords"], track["Melody"]]
for t in drops:
    step_param(t, 0, 2, 0.15)
print("  Instant slam -> 0.15")
time.sleep(bs(1, bpm))
rsteps, rt_beats = 8, 10.0
for i in range(rsteps):
    t = i / (rsteps - 1) if rsteps > 1 else 1
    v = 0.15 + (0.75 - 0.15) * t
    for ti in drops:
        step_param(ti, 0, 2, v)
    time.sleep(bs(rt_beats / rsteps, bpm))
print(f"  Gradual return 0.15->0.75 over {rt_beats} beats  ✓")


# -- step 5: strip & build ------------------------------------------------

section(5, "Strip & Build -- apply_strip_and_build")
for i in range(6):
    step_vol(i, 0.25)
time.sleep(bs(4, bpm))
print("  Stripped: all vol->0.25")
for ti, vol in [(track["Kick"],0.80),(track["Snare"],0.70),(track["Bass"],0.85),
                (track["Chords"],0.70),(track["Melody"],0.65)]:
    step_vol(ti, vol)
    print(f"  Restored track {ti} -> vol {vol}")
    time.sleep(bs(4, bpm))
print("  ✓ Strip & build done")


# -- step 6: crossfader ---------------------------------------------------

section(6, "Crossfader -- assign tracks & sweep")
try:
    tcp("set_track_crossfade_assign", {"track_index": track["Kick"], "value": "A"})
    print("  Kick -> A")
    tcp("set_track_crossfade_assign", {"track_index": track["Bass"], "value": "B"})
    print("  Bass -> B")
    cf_steps = 16
    for i in range(cf_steps):
        tcp("set_crossfader", {"value": -1.0 + 2.0 * (i / (cf_steps - 1))})
        time.sleep(bs(1, bpm))
    print("  Swept -1.0 -> 1.0  ✓")
except Exception as e:
    print(f"  ⚠ Crossfader error: {e}")


# -- step 7: send sweep ---------------------------------------------------

section(7, "Send Sweep -- apply_send_sweep")
try:
    tcp("get_track_sends", {"track_index": track["Bass"]})
    s_steps = 8
    for i in range(s_steps):
        tcp("set_send_amount", {
            "track_index": track["Bass"], "send_index": 0,
            "amount": 0.8 * (i / (s_steps - 1)),
        })
        time.sleep(bs(1, bpm))
    print("  Bass send 0 -> 0.8  ✓")
except Exception as e:
    print(f"  ⚠ Send error: {e}")


# -- step 8: scene progression --------------------------------------------

section(8, "Scene Progression -- apply_scene_progression")
try:
    for si in range(5):
        tcp("fire_scene", {"scene_index": si})
        vol = 0.4 + si * 0.12
        step_param(track["Bass"], 0, 2, 0.25 + si * 0.12)
        print(f"  Scene {si}  bass filter->{0.25+si*0.12:.2f}  vol->{vol:.2f}")
        time.sleep(bs(4, bpm))
    print("  ✓ Scene progression done")
except Exception as e:
    print(f"  ⚠ Scene error: {e}")


# -- done -----------------------------------------------------------------

print(f"\n{'=' * 60}")
print("  ALL 8 DEMOS COMPLETE")
print(f"  Session: {track['_c']} tracks at {int(bpm)} BPM")
print("  Each mixing tool exercised via TCP/UDP primitives")
print(f"{'=' * 60}")

if _tcp:
    _tcp.close()
