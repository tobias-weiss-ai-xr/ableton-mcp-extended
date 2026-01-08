import socket
import json

# Test MCP server connection
try:
    s = socket.socket()
    s.connect(("localhost", 9877))
    print("Connected to Ableton MCP server")

    # Test session info
    s.send(json.dumps({"type": "get_session_info", "params": {}}).encode("utf-8"))
    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue

    response = json.loads(data.decode("utf-8"))
    if response.get("status") == "success":
        print(
            f"Ableton responding - {response['result']['track_count']} tracks in session"
        )
        s.close()
    else:
        print("Ableton error:", response.get("message"))
        s.close()
except Exception as e:
    print(f"Cannot connect to Ableton: {e}")
    print("\nTo use this automation, you need:")
    print("1. Ableton Live running with Remote Script loaded")
    print("2. MCP Server running on port 9877")
