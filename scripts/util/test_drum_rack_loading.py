#!/usr/bin/env python3
"""
Test Drum Rack Loading
======================
Tests the improved drum rack loading functionality with fuzzy URI matching.

This script tests different URI formats:
- Simple path: "Drums/Drum Rack"
- Query format: "query:Drums#Drum Rack"
- URL encoded: "query:Drums#Drum%20Rack"
"""

import socket
import json
import time


def send_command(command_type, params=None):
    """Send command to Ableton MCP server"""
    if params is None:
        params = {}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9877))
        sock.settimeout(10.0)

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))

        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()

        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}


def test_drum_rack_uris():
    """Test various drum rack URI formats"""
    print("=" * 60)
    print("Testing Drum Rack Loading with Different URI Formats")
    print("=" * 60)
    print()

    # Test different URI formats for drum racks
    test_cases = [
        {
            "name": "Simple path format",
            "rack_uri": "Drums/Drum Rack",
            "description": "Tests simple path like 'Drums/Drum Rack'",
        },
        {
            "name": "Query format with hash",
            "rack_uri": "query:Drums#Drum Rack",
            "description": "Tests query format like 'query:Drums#Drum Rack'",
        },
        {
            "name": "Query format with URL encoding",
            "rack_uri": "query:Drums#Drum%20Rack",
            "description": "Tests URL-encoded format like 'query:Drums#Drum%20Rack'",
        },
    ]

    results = []

    for test in test_cases:
        print(f"Test: {test['name']}")
        print(f"  URI: {test['rack_uri']}")
        print(f"  {test['description']}")

        # Try to load drum rack on track 0
        result = send_command(
            "load_browser_item", {"track_index": 0, "item_uri": test["rack_uri"]}
        )

        if result.get("status") == "success":
            res = result.get("result", {})
            print(f"  [OK] SUCCESS")
            print(f"    Item: {res.get('item_name')}")
            print(f"    Track: {res.get('track_name')}")
            results.append({"name": test["name"], "success": True})
        else:
            error = result.get("message", "Unknown error")
            print(f"  [FAIL] FAILED: {error}")
            results.append({"name": test["name"], "success": False, "error": error})

        print()
        time.sleep(0.5)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"Passed: {len(successful)}/{len(results)}")
    print()

    if successful:
        print("Working formats:")
        for r in successful:
            print(f"  [OK] {r['name']}")
        print()

    if failed:
        print("Failed formats:")
        for r in failed:
            print(f"  [FAIL] {r['name']}: {r.get('error', 'Unknown')}")
        print()

    return len(successful) > 0


def test_get_browser_tree():
    """Get browser tree to see available drums"""
    print("=" * 60)
    print("Getting Browser Tree for Drums")
    print("=" * 60)
    print()

    result = send_command("get_browser_tree", {"category_type": "drums"})

    if result.get("status") == "success":
        tree = result.get("result", {})
        print(f"Category: {tree.get('type')}")
        print(f"Items: {len(tree.get('items', []))} top-level items")
        print()
        print("Available drum items:")
        for item in tree.get("items", [])[:10]:  # Show first 10
            name = item.get("name", "Unknown")
            is_folder = "[FOLDER]" if item.get("is_folder") else ""
            uri = item.get("uri", "")
            print(f"  - {name} {is_folder}")
            if uri:
                print(f"    URI: {uri}")
    else:
        print(f"Error: {result.get('message')}")


def main():
    print()
    print("=" * 60)
    print("  Drum Rack Loading Test - Fuzzy URI Matching")
    print("=" * 60)
    print()

    # First, get the browser tree to see what's available
    test_get_browser_tree()
    print()
    print()

    # Then test loading with different URI formats
    success = test_drum_rack_uris()

    if success:
        print("SUCCESS: At least one URI format works!")
        print("The fuzzy matching is successfully finding drum racks.")
    else:
        print("WARNING: All URI formats failed.")
        print("Check that:")
        print("  1. Ableton Live is running")
        print("  2. MCP server is connected")
        print("  3. Track 0 exists and is a MIDI track")
        print("  4. Drum Rack is available in the browser")


if __name__ == "__main__":
    main()
