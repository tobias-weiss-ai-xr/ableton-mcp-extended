#!/usr/bin/env python3
"""
Explore drum kits available in Ableton's browser.

This script queries the Ableton browser to find available drum kits
and their properties, to help with selecting appropriate kits for
different track types (dub hats, percs, etc.).
"""

import socket
import json
from typing import Dict, List, Any


def send_ableton_command(
    command_type: str, params: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Send a command to the Ableton Remote Script via TCP (port 9877).
    """
    if params is None:
        params = {}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9877))

    command = {"type": command_type, "params": params}

    sock.send(json.dumps(command).encode("utf-8"))
    response = sock.recv(8192).decode("utf-8")
    sock.close()

    return json.loads(response)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{title}")
    print("-" * len(title))


def loadable_kits_from_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter browser items to find loadable drum kits.

    Returns items that have is_loadable=True and proper naming.
    """
    loadable = []
    for item in items:
        if item.get("is_loadable", False):
            loadable.append(item)
    return loadable


def main():
    print_section("ABLETON BROWSER - DRUM KIT EXPLORER")

    # Step 1: Get browser categories
    print_subsection("Step 1: Available Browser Categories")
    try:
        result = send_ableton_command("get_browser_tree")
        if "items" in result:
            categories = result["items"]
            print(f"Found {len(categories)} top-level categories:")
            for cat in categories:
                name = cat.get("name", "Unknown")
                is_folder = cat.get("is_folder", False)
                has_children = cat.get("has_children", False)
                marker = (
                    "[Folder]"
                    if is_folder
                    else f"[{'✓' if has_children else '✗'} Children]"
                )
                print(f"  - {name} {marker}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to get browser tree: {e}")
        return

    # Step 2: Explore drums category - acoustic subfolder
    print_subsection("Step 2: Drums/Acoustic - Standard Drum Kits")
    try:
        result = send_ableton_command(
            "get_browser_items_at_path", {"path": "drums/acoustic"}
        )
        if "items" in result:
            items = result["items"]
            loadable = loadable_kits_from_items(items)

            print(f"Total items: {len(items)}")
            print(f"Loadable drum kits: {len(loadable)}")

            if loadable:
                print(f"\nTop {min(10, len(loadable))} acoustic drum kits:")
                for i, kit in enumerate(loadable[:10], 1):
                    name = kit.get("name", "Unknown")
                    uri = kit.get("uri", "No URI")
                    print(f"  {i}. {name}")
                    print(f"     URI: {uri}")
            else:
                print("No loadable kits found in drums/acoustic")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to get drums/acoustic kits: {e}")

    # Step 3: Explore drums category - electronic subfolder
    print_subsection("Step 3: Drums/Electronic - Electronic Drum Kits")
    try:
        result = send_ableton_command(
            "get_browser_items_at_path", {"path": "drums/electronic"}
        )
        if "items" in result:
            items = result["items"]
            loadable = loadable_kits_from_items(items)

            print(f"Total items: {len(items)}")
            print(f"Loadable drum kits: {len(loadable)}")

            if loadable:
                print(f"\nTop {min(10, len(loadable))} electronic drum kits:")
                for i, kit in enumerate(loadable[:10], 1):
                    name = kit.get("name", "Unknown")
                    uri = kit.get("uri", "No URI")
                    print(f"  {i}. {name}")
                    print(f"     URI: {uri}")
            else:
                print("No loadable kits found in drums/electronic")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to get drums/electronic kits: {e}")

    # Step 4: Explore drums category - drum kits subfolder
    print_subsection("Step 4: Drums/Drum Kits - Pre-built Drum Rack Kits")
    try:
        result = send_ableton_command(
            "get_browser_items_at_path", {"path": "drums/drum kits"}
        )
        if "items" in result:
            items = result["items"]
            loadable = loadable_kits_from_items(items)

            print(f"Total items: {len(items)}")
            print(f"Loadable drum kits: {len(loadable)}")

            if loadable:
                print(f"\nTop {min(10, len(loadable))} pre-built drum kits:")
                for i, kit in enumerate(loadable[:10], 1):
                    name = kit.get("name", "Unknown")
                    uri = kit.get("uri", "No URI")
                    print(f"  {i}. {name}")
                    print(f"     URI: {uri}")
            else:
                print("No loadable kits found in drums/drum kits")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to get drums/drum kits: {e}")

    # Step 5: Explore packs folder for drum racks
    print_subsection("Step 5: Packs - Factory Drum Racks")
    try:
        result = send_ableton_command(
            "get_browser_items_at_path", {"path": "Packs/Drums"}
        )
        if "items" in result:
            items = result["items"]
            loadable = loadable_kits_from_items(items)

            print(f"Total items: {len(items)}")
            print(f"Loadable items: {len(loadable)}")

            if loadable:
                print(f"\nTop {min(10, len(loadable))} Drum Packs:")
                for i, pack in enumerate(loadable[:10], 1):
                    name = pack.get("name", "Unknown")
                    uri = pack.get("uri", "No URI")
                    print(f"  {i}. {name}")
                    print(f"     URI: {uri}")
            else:
                print("No loadable items found in Packs/Drums")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to get Packs/Drums: {e}")

    # Step 6: Search for specific hi-hat or percussion kits
    print_subsection("Step 6: Search for Hi-Hat focused kits (Percussion folder)")
    try:
        result = send_ableton_command(
            "get_browser_items_at_path", {"path": "drums/percussion"}
        )
        if "items" in result:
            items = result["items"]
            loadable = loadable_kits_from_items(items)

            print(f"Total items: {len(items)}")
            print(f"Loadable kits: {len(loadable)}")

            if loadable:
                print(f"\nTop {min(10, len(loadable))} percussion kits:")
                for i, kit in enumerate(loadable[:10], 1):
                    name = kit.get("name", "Unknown")
                    uri = kit.get("uri", "No URI")
                    print(f"  {i}. {name}")
                    print(f"     URI: {uri}")
            else:
                print("No loadable kits found in drums/percussion")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Failed to get drums/percussion: {e}")

    # Step 7: Show specific recommendations for dub hats and percs
    print_section("RECOMMENDATIONS FOR DUB TECHNO TRACKS")

    print("""
Based on the available drum kits, here are recommendations:

For DUB HATS (Track 2):
- Use: drums/acoustic → Standard acoustic hi-hats
- MIDI Note 42 → Closed Hi-hat
- MIDI Note 46 → Open Hi-hat

For PERCS (Track 3):
- Use: drums/percussion → Tambourines, shakers, claps
- Options: drums/electronic → Electronic percussion

GENERAL DUB TECHNO DRUM RACKS:
- drums/acoustic → Classic dub/reggae feel
- drums/drum kits → Pre-configured Drum Racks
- Packs/Drums → Factory Drum Rack presets

To load a drum kit:
1. Load Drum Rack container: "Drums/Drum Rack"
2. Load drum kit into it: "drums/acoustic/[kit_name]" or specific URI
    """)

    print_section("EXPLORATION COMPLETE")
    print("\nNext steps:")
    print("1. Choose appropriate drum kit for Track 2 (Dub Hats)")
    print("2. Use a script to replace the empty Drum Rack with a populated one")
    print("3. Test that the hi-hat pattern plays with actual sounds")


if __name__ == "__main__":
    main()
