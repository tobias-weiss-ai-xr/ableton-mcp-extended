import socket
import json
import sys

s = socket.socket()
s.connect(("localhost", 9877))


def fire_clip(track_index, clip_index, clip_name=""):
    """Fire a specific clip"""
    s.send(
        json.dumps(
            {
                "type": "fire_clip",
                "params": {"track_index": track_index, "clip_index": clip_index},
            }
        ).encode("utf-8")
    )
    response = json.loads(s.recv(4096).decode("utf-8"))
    if clip_name:
        print(f"[OK] Fired: {clip_name}")
    return response


# Section definitions
sections = {
    "intro": [
        (4, 2, "Dub Bass - Breakdown"),
        (5, 2, "Drums - Minimalist"),
        (6, 0, "Atmosphere - Basic"),
        (7, 0, "Dub Melody - Basic"),
        (10, 0, "Percussion - Basic"),
    ],
    "buildup": [
        (4, 1, "Dub Bass - Alternative"),
        (5, 3, "Drums - Buildup"),
        (6, 1, "Atmosphere - Complex"),
        (7, 1, "Dub Melody - Alternative"),
    ],
    "drop": [
        (4, 0, "Dub Bass - Main"),
        (5, 4, "Drums - Drop"),
        (6, 1, "Atmosphere - Complex"),
        (7, 0, "Dub Melody - Basic"),
        (8, 0, "FX - Active"),
    ],
    "breakdown": [
        (4, 2, "Dub Bass - Breakdown"),
        (5, 2, "Drums - Minimalist"),
        (6, 1, "Atmosphere - Complex"),
    ],
    "fulldrop": [
        (4, 0, "Dub Bass - Main"),
        (5, 4, "Drums - Drop"),
        (6, 1, "Atmosphere - Complex"),
        (7, 1, "Dub Melody - Alternative"),
        (8, 0, "FX - Active"),
        (10, 0, "Percussion - Basic"),
    ],
}

# Usage
if len(sys.argv) < 2:
    print("DUB SONG SECTION SWITCHER")
    print("=" * 50)
    print("\nUsage: python switch_section.py [section_name]")
    print("\nAvailable sections:")
    print("  intro     - Minimal, spacey dub")
    print("  buildup   - Adding energy")
    print("  drop      - Maximum energy")
    print("  breakdown - Space and atmosphere")
    print("  fulldrop  - All elements active")
    print("\nExample: python switch_section.py intro")
else:
    section_name = sys.argv[1].lower()

    if section_name in sections:
        print(f"\nSwitching to: {section_name.upper()}")
        print("-" * 50)

        for track_idx, clip_idx, clip_name in sections[section_name]:
            fire_clip(track_idx, clip_idx, clip_name)

        print("-" * 50)
        print(f"Section '{section_name}' is now playing!")
    else:
        print(f"\nError: Unknown section '{section_name}'")
        print("Available sections: intro, buildup, drop, breakdown, fulldrop")

s.close()
