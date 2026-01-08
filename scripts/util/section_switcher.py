import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def fire_clip(track_index, clip_index):
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
    return response


def stop_clip(track_index, clip_index):
    """Stop a specific clip"""
    s.send(
        json.dumps(
            {
                "type": "stop_clip",
                "params": {"track_index": track_index, "clip_index": clip_index},
            }
        ).encode("utf-8")
    )
    response = json.loads(s.recv(4096).decode("utf-8"))
    return response


print("DUB SONG - SECTION SWITCHER")
print("=" * 70)
print("""
This script helps you switch between different sections of your dub song.

Each section fires specific clips to create that section's sound.
You can play sections in any order to build your arrangement.
""")

print("AVAILABLE SECTIONS:")
print("-" * 70)

sections = {
    "1": {
        "name": "INTRO (Minimal, spacey)",
        "clips": [
            (4, 2, "Dub Bass - Breakdown"),
            (5, 2, "Drums - Minimalist"),
            (6, 0, "Atmosphere - Basic"),
            (7, 0, "Dub Melody - Basic"),
            (10, 0, "Percussion - Basic"),
        ],
    },
    "2": {
        "name": "BUILDUP (Adding energy)",
        "clips": [
            (4, 1, "Dub Bass - Alternative"),
            (5, 3, "Drums - Buildup"),
            (6, 1, "Atmosphere - Complex"),
            (7, 1, "Dub Melody - Alternative"),
        ],
    },
    "3": {
        "name": "DROP (Maximum energy)",
        "clips": [
            (4, 0, "Dub Bass - Main"),
            (5, 4, "Drums - Drop"),
            (6, 1, "Atmosphere - Complex"),
            (7, 0, "Dub Melody - Basic"),
            (8, 0, "FX - Active"),
        ],
    },
    "4": {
        "name": "BREAKDOWN (Space and atmosphere)",
        "clips": [
            (4, 2, "Dub Bass - Breakdown"),
            (5, 2, "Drums - Minimalist"),
            (6, 1, "Atmosphere - Complex"),
        ],
    },
    "5": {
        "name": "FULL DROP (All elements)",
        "clips": [
            (4, 0, "Dub Bass - Main"),
            (5, 4, "Drums - Drop"),
            (6, 1, "Atmosphere - Complex"),
            (7, 1, "Dub Melody - Alternative"),
            (8, 0, "FX - Active"),
            (10, 0, "Percussion - Basic"),
        ],
    },
}

for key, section in sections.items():
    print(f"{key}. {section['name']}")
    for track_idx, clip_idx, clip_name in section["clips"]:
        print(f"   - {clip_name}")

print("\n" + "=" * 70)
print("CONTROLS:")
print("-" * 70)
print("Enter section number (1-5) to switch to that section")
print("Enter 'q' to quit")
print("Enter 'h' to see this help again")
print("=" * 70)

while True:
    print("\nCurrent section: ", end="")
    choice = input("Switch to section (1-5, h=help, q=quit): ").strip()

    if choice.lower() == "q":
        print("\nExiting section switcher...")
        break

    elif choice.lower() == "h":
        print("\n" + "=" * 70)
        print("AVAILABLE SECTIONS:")
        print("-" * 70)
        for key, section in sections.items():
            print(f"{key}. {section['name']}")
        print("=" * 70)
        continue

    elif choice in sections:
        section = sections[choice]
        print(f"\nSwitching to: {section['name']}")
        print("-" * 70)

        for track_idx, clip_idx, clip_name in section["clips"]:
            result = fire_clip(track_idx, clip_idx)
            print(f"[OK] Fired: {clip_name}")

        print("=" * 70)
        print(f"Section '{section['name']}' is now playing!")
        print(f"Listen for about 8-16 bars (32-64 seconds)")
        print("Then switch to another section or press 'q' to quit")

    else:
        print("\nInvalid choice! Please enter 1-5, h, or q")

s.close()
print("\nSection switcher closed. Song continues playing in Ableton.")
