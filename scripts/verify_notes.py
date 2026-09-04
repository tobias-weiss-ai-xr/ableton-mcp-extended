"""Verify notes landed correctly in session AND arrangement clips.

Compares builder output vs get_clip_notes vs get_arrangement_clip_notes:
note count, first/last note start_time, and a checksum of (pitch, start).
"""
import json
import socket
import sys

sys.path.insert(0, "scripts")
from create_5min_dub import BUILDERS, SCENES, TRACKS  # noqa: E402


def tcp(cmd, params=None, timeout=30):
    s = socket.socket()
    s.settimeout(timeout)
    s.connect(("localhost", 9877))
    s.sendall((json.dumps({"type": cmd, "params": params or {}}) + "\n").encode())
    r = json.loads(s.recv(4194304).decode())
    s.close()
    return r


def sig(notes):
    """Sort note signature: list of (start_time, pitch) rounded."""
    return sorted((round(n["start_time"], 3), int(n["pitch"])) for n in notes)


def main():
    names = [t[0] for t in TRACKS]
    all_ok = True
    for si, (sname, sbars) in enumerate(SCENES):
        for ti, builder in enumerate(BUILDERS):
            expected = sig(builder(sname, sbars))
            if not expected:
                continue
            rs = tcp("get_clip_notes", {"track_index": ti, "clip_index": si})
            sess = ((rs.get("result") or {}).get("notes")
                    or (rs.get("result") or {}).get("note_list") or [])
            if not sess and isinstance(rs.get("result"), dict):
                for key in ("notes", "note_list", "data"):
                    if rs["result"].get(key):
                        sess = rs["result"][key]
                        break
            ra = tcp("get_arrangement_clip_notes",
                     {"track_index": ti, "clip_index": si})
            arr = (ra.get("result") or {}).get("notes") or []
            se, ae = sig(sess), sig(arr)
            # Live merges notes with identical (pitch, start, duration);
            # compare distinct (start, pitch) sets and report raw counts.
            exp_set, s_set, a_set = set(expected), set(se), set(ae)
            ok_s, ok_a = s_set == exp_set, a_set == exp_set
            all_ok &= ok_s and ok_a
            flag = "OK " if (ok_s and ok_a) else "BAD"
            print(f"{flag} t{ti} {names[ti]:8s} s{si} {sname:9s} "
                  f"exp={len(expected):4d} sess={len(se):4d} arr={len(ae):4d} "
                  f"| first exp={expected[0][0]:6.2f} sess={se[0][0] if se else -1:6.2f} "
                  f"arr={ae[0][0] if ae else -1:6.2f}"
                  f"| last exp={expected[-1][0]:7.2f} sess={se[-1][0] if se else -1:7.2f} "
                  f"arr={ae[-1][0] if ae else -1:7.2f}")
    print()
    print("NOTE VERIFICATION:",
          "ALL session + arrangement notes match builders exactly"
          if all_ok else "MISMATCH FOUND")


if __name__ == "__main__":
    main()
