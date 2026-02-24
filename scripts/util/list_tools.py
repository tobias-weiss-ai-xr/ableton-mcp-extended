#!/usr/bin/env python3
import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 9877))
sock.send(json.dumps({"type": "list_tools", "params": {}}).encode("utf-8"))
response = json.loads(sock.recv(8192).decode("utf-8"))
sock.close()

print(json.dumps(response, indent=2)[:2000])
