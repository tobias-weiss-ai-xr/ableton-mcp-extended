"""Probe: does duplicate_clip_to_arrangement copy notes? + robust reader test."""
import json
import socket
import time


def tcp(cmd, params=None, timeout=60):
    s = socket.socket()
    s.settimeout(timeout)
    s.connect(("localhost", 9877))
    s.sendall((json.dumps({"type": cmd, "params": params or {}}) + "\n").encode())
    r = json.loads(s.recv(4194304).decode())
    s.close()
    return r


# wait for full document restore (49 session clips)
ok = False
for _ in range(75):
    try:
        r = tcp("get_all_clips_in_track", {"track_index": 0})
        n = len((r.get("result") or {}).get("clips") or [])
        if n >= 7:
            ok = True
            print(f"session restored: {n} clips on t0")
            break
    except Exception:
        pass
    time.sleep(4)
if not ok:
    raise SystemExit("document never restored")

# session source of truth: DROP drums
rs = tcp("get_clip_notes", {"track_index": 0, "clip_index": 3})
sess = (rs.get("result") or {}).get("notes") or []
print(f"session t0 s3 DROP: {len(sess)} notes")

# duplicate WITHOUT notes payload
r = tcp("build_arrangement", {"sections": [
    {"track_index": 0, "clip_index": 3, "position_bar": 200.0}]})
item = (r.get("result") or {}).get("items", [{}])[0]
print("duplicate probe:", json.dumps(item))

# find clip at 800 and read notes
r = tcp("get_arrangement_clips", {"track_index": 0})
idx = None
for c in (r.get("result") or {}).get("arrangement_clips") or []:
    if abs(c.get("start_time", 0) - 800.0) < 0.01:
        idx = c.get("clip_index")
print("arrangement index at bar 200:", idx)
if idx is not None:
    ra = tcp("get_arrangement_clip_notes", {"track_index": 0, "clip_index": idx})
    res = ra.get("result") or {}
    arr = res.get("notes") or []
    print(f"arrangement readback: {res.get('note_count')} notes")
    if sess and arr:
        ss = sorted((round(n["start_time"], 3), n["pitch"]) for n in sess)
        as_ = sorted((round(n["start_time"], 3), n["pitch"]) for n in arr)
        print("notes copied by duplicate:", ss == as_)
        print("first arr notes:", arr[:3])
