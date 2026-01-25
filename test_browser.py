import socket
import json

s = socket.socket()
s.connect(("127.0.0.1", 9877))
s.send(
    json.dumps(
        {"type": "get_browser_items_at_path", "params": {"path": "Drums"}}
    ).encode("utf-8")
)

data = b""
while True:
    chunk = s.recv(8192)
    if not chunk:
        break
    data += chunk
    try:
        obj = json.loads(data.decode("utf-8"))
        break
    except json.JSONDecodeError:
        continue

print(json.dumps(obj, indent=2))
s.close()
