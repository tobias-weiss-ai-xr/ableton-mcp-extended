import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    return json.loads(s.recv(8192).decode("utf-8"))


print("=" * 80)
print("CHECKING ABLETON SESSION STATE")
print("=" * 80)

# Get session info
result = send_command("get_session_info")
print("\nFull session info response:")
print(json.dumps(result, indent=2))

s.close()
