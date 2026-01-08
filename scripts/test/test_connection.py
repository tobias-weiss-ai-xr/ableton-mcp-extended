import socket
import json

print("=" * 80)
print("TESTING ABLETON MCP CONNECTION")
print("=" * 80)

try:
    s = socket.socket()
    s.connect(("localhost", 9877))
    print("[OK] Connected to Ableton MCP server on port 9877")

    # Test basic commands
    test_commands = [
        "get_session_info",
        "delete_all_tracks",
    ]

    for cmd in test_commands:
        print(f"\nTesting command: {cmd}")
        s.send(json.dumps({"type": cmd, "params": {}}).encode("utf-8"))
        response = json.loads(s.recv(8192).decode("utf-8"))
        if response.get("status") == "success":
            print(f"  [OK] {cmd} works")
        else:
            print(f"  [FAIL] {cmd} failed: {response}")

    s.close()
    print("\n" + "=" * 80)
    print("CONNECTION TEST COMPLETE")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] Could not connect to Ableton MCP server")
    print(f"Details: {str(e)}")
    print("\nTROUBLESHOOTING:")
    print("1. Ensure Ableton Live is running")
    print("2. Ensure AbletonMCP Remote Script is loaded")
    print("3. Check that MCP Server is running (python MCP_Server/server.py)")
    print("4. Verify Remote Script location in Ableton Preferences")
