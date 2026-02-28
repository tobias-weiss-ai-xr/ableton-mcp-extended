#!/usr/bin/env python3
import json, urllib.request


def send(cmd):
    try:
        data = json.dumps(cmd).encode()
        req = urllib.request.Request(
            "http://localhost:8080",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode())
    except Exception as e:
        print(f"Error: {e}")
        return None


print("Testing Ableton MCP connection...")
result = send({"command": "get_session_overview"})
if result:
    print("Connected!")
    print("Tracks:", [t["name"] for t in result.get("tracks", [])])
else:
    print("Connection failed")
