#!/usr/bin/env python3
"""Diagnose TCP transfer latency to the Ableton Remote Script (9877).

Measures per-command round-trip times for create_clip / add_notes_to_clip
at increasing payload sizes, checks session state left by earlier runs
(tempo, stray clips), and repairs obvious damage (tempo back to 75).
"""
import json
import socket
import sys
import time

HOST, PORT = "localhost", 9877


def tcp(cmd, params=None, timeout=20):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    msg = json.dumps({"type": cmd, "params": params or {}}).encode() + b"\n"
    t0 = time.time()
    s.sendall(msg)
    raw = s.recv(262144).decode()
    dt = time.time() - t0
    s.close()
    r = json.loads(raw) if raw else {}
    return r, dt


def main():
    # 1) session state
    r, dt = tcp("get_tempo")
    tempo = (r.get("result") or {}).get("tempo") if isinstance(r.get("result"), dict) else None
    if tempo is None:
        tempo = r.get("result")  # some handlers return raw value
    print(f"get_tempo: {dt:.3f}s -> {r.get('status')} tempo={tempo}")

    r, _ = tcp("get_all_tracks")
    tracks = (r.get("result") or {}).get("tracks") or []
    print(f"tracks: {len(tracks)}")

    # 2) repair tempo if a killed run left it at 600
    if isinstance(tempo, (int, float)) and abs(float(tempo) - 75.0) > 1.0:
        r, dt = tcp("set_tempo", {"tempo": 75.0})
        print(f"set_tempo 75: {dt:.3f}s -> {r.get('status')} (was {tempo})")

    # 3) clean the probe slot, then time create + notes at several sizes
    r, dt = tcp("delete_clip", {"track_index": 0, "clip_index": 0})
    print(f"delete_clip t0s0: {dt:.3f}s -> {r.get('status')}")

    r, dt = tcp("create_clip", {"track_index": 0, "clip_index": 0, "length": 48.0})
    print(f"create_clip(48 beats): {dt:.3f}s -> {r.get('status')}")

    for n in (53, 200, 500):
        notes = [{"pitch": 36 + (i % 12), "start": i * 0.25,
                  "duration": 0.2, "velocity": 100} for i in range(n)]
        payload_kb = len(json.dumps({"notes": notes})) // 1024
        r, dt = tcp("add_notes_to_clip",
                    {"track_index": 0, "clip_index": 0, "notes": notes},
                    timeout=60)
        print(f"add_notes({n:4d} notes, {payload_kb:3d}KB): {dt:.3f}s -> {r.get('status')}")

    # 4) real-world sample: DRUMS INTRO pattern from the dub script
    sys.path.insert(0, ".")
    from scripts.create_5min_dub import drums_for
    notes = drums_for("INTRO", 12)
    payload_kb = len(json.dumps({"notes": notes})) // 1024
    r, dt = tcp("add_notes_to_clip",
                {"track_index": 0, "clip_index": 0, "notes": notes}, timeout=60)
    print(f"add_notes(real DRUMS/INTRO, {len(notes)} notes, {payload_kb}KB): "
          f"{dt:.3f}s -> {r.get('status')}")

    # 5) cleanup probe clip
    r, dt = tcp("delete_clip", {"track_index": 0, "clip_index": 0})
    print(f"cleanup delete_clip t0s0: {dt:.3f}s -> {r.get('status')}")

    print("\nEstimated full build (49 clips):",
          f"~{49 * (dt + 0.1):.0f}s at the measured per-clip cost")


if __name__ == "__main__":
    main()
