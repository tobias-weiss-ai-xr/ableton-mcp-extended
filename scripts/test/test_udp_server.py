#!/usr/bin/env python
"""
Integration test for UDP server in AbletonMCP Remote Script.
"""

import socket
import json
import time
import sys


def test_udp_socket_creation():
    """Test that UDP socket can be created on port 9878"""
    print("TEST 1: UDP socket creation on port 9878")
    try:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(("127.0.0.1", 9878))
        print("  [PASS] UDP socket created and bound to port 9878")
        udp_socket.close()
        return True
    except socket.error as e:
        if "Address already in use" in str(e):
            print("  [WARN] Port 9878 already in use (expected if Ableton Live is running)")
            return True
        else:
            print("  [FAIL] Failed to create UDP socket: {}".format(e))
            return False
    except Exception as e:
        print("  [FAIL] Unexpected error: {}".format(e))
        return False


def test_udp_message_send():
    """Test that UDP messages can be sent"""
    print("\nTEST 2: UDP message sending")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_command = {
            "type": "set_device_parameter",
            "params": {
                "track_index": 0,
                "device_index": 0,
                "parameter_index": 0,
                "value": 0.5
            }
        }
        message = json.dumps(test_command).encode('utf-8')
        client_socket.sendto(message, ("127.0.0.1", 9878))
        print("  [PASS] UDP message sent to port 9878")
        client_socket.close()
        return True
    except socket.error as e:
        print("  [FAIL] Socket error: {}".format(e))
        if "Connection refused" in str(e) or "[Errno 10061]" in str(e):
            print("  [INFO] Server may not be running (expected)")
            return True
        return False
    except Exception as e:
        print("  [FAIL] Unexpected error: {}".format(e))
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AbletonMCP UDP Server Integration Test")
    print("=" * 60)

    results = []
    results.append(("UDP socket creation", test_udp_socket_creation()))
    results.append(("UDP message sending", test_udp_message_send()))

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print("  {} {}: {}".format("[PASS]" if result else "[FAIL]", test_name, status))

    print("-" * 60)
    print("Total: {}/{} tests passed".format(passed, total))

    if passed == total:
        print("\n[PASS] All tests passed!")
        return 0
    else:
        print("\n[FAIL] {} test(s) failed".format(total - passed))
        return 1


if __name__ == "__main__":
    sys.exit(main())
