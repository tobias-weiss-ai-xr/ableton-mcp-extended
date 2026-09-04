#!/usr/bin/env python3
"""Empirically probe capture_and_insert_arrangement behavior.

Times the call (instant => direct LOM capture, ~10s => recording fallback),
then delete-probes the arrangement to see whether clips actually appeared.
Variants: (tempo 75, bar 0), (tempo 75, bar 12), (tempo 600, bar 0).
"""
import json
import socket
import time

HOST, PORT = "localhost", 9877


def tcp(cmd, params=None, timeout=30):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    msg = json.dumps({"type": cmd, "params": params or {}}).encode() + b"\n"
    t0 = time.time()
    s.sendall(msg)
    raw = s.recv(262144).decode()
    dt = time.time() - t0
    s.close()
    return (json.loads(raw) if raw else {}), dt


def probe_empty():
    """True if track 0 arrangement has 0 clips (probe idx 0..15)."""
    for idx in range(16):
        r, _ = tcp("delete_arrangement_clip", {"track_index": 0, "clip_index": idx})
        if r.get("status") == "success":
            return False, idx
    return True, None


def variant(label, tempo, start_bar, length_bars):
    print(f"--- variant: {label}")
    tcp("stop_playback")
    tcp("set_tempo", {"tempo": tempo})
    tcp("set_track_arm", {"track_index": 0, "arm": True})
    r, dt = tcp("capture_and_insert_arrangement",
                {"start_bar": start_bar, "length_bars": length_bars,
                 "quantize": False}, timeout=40)
    print(f"  capture call: {dt:.2f}s status={r.get('status')} "
          f"result={json.dumps(r.get('result'))[:140]}")
    tcp("stop_playback")
    tcp("set_track_arm", {"track_index": 0, "arm": False})
    empty, at = probe_empty()
    print(f"  arrangement clips on track 0 after: "
          f"{'NONE' if empty else f'EXISTS (first found at idx {at}, now deleted)'}")
    return not empty


def main():
    variant("tempo 75, start_bar 0, len 2", 75.0, 0.0, 2)
    variant("tempo 75, start_bar 12, len 2", 75.0, 12.0, 2)
    variant("tempo 600, start_bar 0, len 2", 600.0, 0.0, 2)
    tcp("set_tempo", {"tempo": 75.0})
    tcp("stop_playback")
    print("done (tempo restored to 75)")


if __name__ == "__main__":
    main()
