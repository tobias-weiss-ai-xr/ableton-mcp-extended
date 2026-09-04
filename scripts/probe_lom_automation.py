"""Probe which automation-related attributes exist on live LOM objects."""
import json
import socket
import time


def tcp(cmd, params=None, timeout=30):
    s = socket.socket()
    s.settimeout(timeout)
    s.connect(("localhost", 9877))
    s.sendall((json.dumps({"type": cmd, "params": params or {}}) + "\n").encode())
    r = json.loads(s.recv(4194304).decode())
    s.close()
    return r


# wait for restore
for _ in range(75):
    try:
        r = tcp("get_all_clips_in_track", {"track_index": 0})
        if len((r.get("result") or {}).get("clips") or []) >= 7:
            print("session restored")
            break
    except Exception:
        pass
    time.sleep(4)
else:
    raise SystemExit("never restored")

CLIP_NAMES = [
    "create_automation_event", "add_automation_event",
    "create_automation_envelope", "automation_envelope",
    "get_automation_events", "clear_automation_envelope",
    "automation", "can_automation", "remove_automation_event",
    "get_automation_value", "automation_layers", "get_notes_extended",
    "is_automation_visible", "show_envelope",
]
OTHER = {
    "song": ["create_automation", "automation", "get_automation",
             "tempo_automation", "delete_arrangement_clip"],
    "song_view": ["highlighted_parameter", "highlighted_clip_slot",
                  "highlighted_track", "detail_clip"],
    "track": ["automation_lane", "create_automation", "arrangement_clips",
              "automation", "can_automation"],
    "param": ["automation_enabled", "is_automated", "is_quantized",
              "original_value", "value"],
}
for target, names in [("clip", CLIP_NAMES)] + list(OTHER.items()):
    r = tcp("lom_probe", {"target": target, "names": names})
    res = r.get("result") or {}
    if res.get("attrs") is None:
        print(f"{target}: {json.dumps(res)[:120]}")
        continue
    hits = [n for n, v in res["attrs"].items() if v]
    print(f"{target}: EXISTS -> {hits}")
    missing = [n for n, v in res["attrs"].items() if not v]
    print(f"    missing -> {missing}")
