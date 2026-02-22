#!/usr/bin/env python3
"""Try different URI formats for Drum Rack"""

import socket
import json


def send_command(cmd_type, params=None):
    if params is None:
        params = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9877))
    command = {"type": cmd_type, "params": params}
    sock.send(json.dumps(command).encode("utf-8"))
    response = sock.recv(8192).decode("utf-8")
    sock.close()
    return json.loads(response)


print("=" * 70)
print("TRYING DIFFERENT DRUM RACK URIs")
print("=" * 70)

# Different URI formats to try
uris = [
    "Drums/Drum Rack",
    "query:Drums#Drum%20Rack",
    "drums/drum rack",
    "Drum Rack",
]

for uri in uris:
    print(f'\nTrying URI: "{uri}"')
    result = send_command("load_browser_item", {"track_index": 2, "item_uri": uri})
    if result.get("status") == "success":
        print(f"  SUCCESS: {result.get('result', {})}")
    else:
        print(f"  FAILED: {result.get('message', 'Unknown error')}")

# Try getting browser tree to see what's available
print("\n" + "=" * 70)
print("CHECKING BROWSER TREE")
print("=" * 70)

tree_result = send_command("get_browser_tree", {})
print(f"\nResult: {json.dumps(tree_result, indent=2)}")
