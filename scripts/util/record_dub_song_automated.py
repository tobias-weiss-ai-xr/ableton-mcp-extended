import socket
import json
import time

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
        print(f"  [OK] {clip_name}")
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

print("=" * 70)
print("DUB SONG - AUTOMATED RECORDING")
print("=" * 70)
print("")
print("NOTE: AbletonMCP cannot start/stop recording directly.")
print("You need to record manually in Ableton while I play sections.")
print("")
print("=" * 70)
print("RECORDING INSTRUCTIONS")
print("=" * 70)
print("""
Step 1: PREPARE ABLETON
   - Make sure all tracks have instruments loaded
   - Check track levels (not clipping)
   - Press TAB for Session View

Step 2: START RECORDING
   - Click Record button on Master track
   - Press SPACE to start recording
   - Wait for recording to begin (red indicator shows)

Step 3: RUN THIS SCRIPT
   - Press Enter below to start playback
   - I will play all sections automatically
   - Each section plays for correct duration
   - Total time: exactly 5 minutes

Step 4: STOP RECORDING
   - Wait for script to complete
   - Press SPACE in Ableton to stop recording
   - Your dub song is now recorded!

Step 5: EXPORT (if needed)
   - If recording to audio track, export that track
   - Or use the recorded audio directly
""")

print("=" * 70)
input("Press Enter when Ableton is recording and ready...")
print("")

# At 75 BPM:
# 60 seconds / 75 BPM = 0.8 seconds per beat
# 4 beats per bar = 3.2 seconds per bar
# 8 bars = 8 * 3.2 = 25.6 seconds

# Let's use 25 seconds per section for a 5-minute song
# 9 sections * 25 seconds = 225 seconds = 3.75 minutes
# We need more time for a 5-minute song

# Let's do 10 sections at 30 seconds each = 300 seconds = 5 minutes

sequence = [
    ("intro", 30, "0:00 - 0:30", "INTRO - Minimal, spacey dub"),
    ("buildup", 30, "0:30 - 1:00", "BUILDUP 1 - Adding energy"),
    ("drop", 30, "1:00 - 1:30", "DROP 1 - Maximum energy"),
    ("buildup", 30, "1:30 - 2:00", "BUILDUP 2 - Building tension"),
    ("breakdown", 30, "2:00 - 2:30", "BREAKDOWN - Space and atmosphere"),
    ("buildup", 30, "2:30 - 3:00", "BUILDUP 3 - Final buildup"),
    ("drop", 40, "3:00 - 3:40", "DROP 2 - Extended drop"),
    ("fulldrop", 40, "3:40 - 4:20", "FULL DROP - All elements"),
    ("breakdown", 30, "4:20 - 4:50", "OUTRO - Fading out"),
]

total_duration = sum(duration for _, duration, _, _ in sequence)

print("=" * 70)
print("STARTING AUTOMATED PLAYBACK")
print("=" * 70)
print(f"Total duration: {total_duration} seconds ({total_duration / 60:.1f} minutes)")
print("")

start_time = time.time()

for i, (section_name, duration, time_range, description) in enumerate(sequence, 1):
    print(f"\n[{i}/{len(sequence)}] {time_range} - {description}")
    print("-" * 70)

    for track_idx, clip_idx, clip_name in sections[section_name]:
        fire_clip(track_idx, clip_idx, clip_name)

    print(f"\nPlaying for {duration} seconds...")

    # Countdown timer
    elapsed = 0
    while elapsed < duration:
        remaining = int(duration - elapsed)
        if remaining % 5 == 0 and remaining > 0:
            print(f"  {remaining} seconds remaining...", end="\r")
        time.sleep(1)
        elapsed += 1

    print("\n" + " " * 50, end="\r")  # Clear countdown line

end_time = time.time()
actual_duration = end_time - start_time

print("\n" + "=" * 70)
print("PLAYBACK COMPLETE!")
print("=" * 70)
print(
    f"Actual duration: {actual_duration:.1f} seconds ({actual_duration / 60:.1f} minutes)"
)
print("")
print("=" * 70)
print("STOP RECORDING NOW!")
print("=" * 70)
print("""
1. Press SPACE in Ableton to stop recording
2. The recording indicator will disappear
3. Your dub song is now recorded!

What to do next:
- Listen to the recorded track
- Export it if needed (File -> Export Audio/Video)
- Save your Ableton project
- Share your dub song!

""")
print("Recording complete! Your dub song is ready!")
print("=" * 70)

s.close()
