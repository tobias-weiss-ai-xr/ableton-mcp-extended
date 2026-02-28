#!/usr/bin/env python3
import time, json, urllib.request, os

SERVER_URL = os.environ.get("ABLETON_MCP_URL", "http://localhost:8080")


def send_cmd(cmd, args=None):
    try:
        payload = json.dumps({"command": cmd, "args": args or []}).encode("utf-8")
        req = urllib.request.Request(
            SERVER_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode("utf-8"))
    except:
        return None


def main():
    global loop_count
    loop_count += 1
    print("\n" + "=" * 60)
    print("DUB MIX LOOP #%d" % loop_count)
    print("=" * 60)
    if not send_cmd("get_session_overview"):
        print("Ableton unavailable - retrying...")
        time.sleep(10)
        return
    print("Ableton OK")
    print("Triggering scenes...")
    for s in range(8):
        send_cmd("trigger_scene", s)
        time.sleep(4)
    print("Applying effects...")
    for i in range(4):
        send_cmd("apply_filter_buildup", [[0, 9, 0], 0.2, 0.8, 8, 8])
        time.sleep(8)
    print("Setting sends...")
    send_cmd("set_send_amount", [0, 0, 0.7])
    send_cmd("set_send_amount", [1, 0, 0.6])
    time.sleep(4)
    print("Firing drums...")
    for i in range(4):
        send_cmd("fire_clip", [6, 0])
        time.sleep(4)
    print("Loop #%d done" % loop_count)
    time.sleep(10)


print("=" * 60)
print("CONTINUOUS DUB MIX ORCHESTRATOR")
print("=" * 60)
print("Starting infinite loop... Ctrl+C to stop\n")
loop_count = 0
try:
    while True:
        main()
except KeyboardInterrupt:
    print("\nStopped")
except:
    time.sleep(5)
    main()
