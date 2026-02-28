import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.sendto(b"/ping\0" * 12, ("127.0.0.1", 8000))
    print("OSC 8000: OK")
except Exception as e:
    print(f"OSC 8000: {e}")
try:
    sock.sendto(b"/ping\0" * 12, ("127.0.0.1", 9000))
    print("OSC 9000: OK")
except Exception as e:
    print(f"OSC 9000: {e}")
try:
    sock.sendto(b"/ping\0" * 12, ("127.0.0.1", 8553))
    print("OSC 8553: OK")
except Exception as e:
    print(f"OSC 8553: {e}")
sock.close()
