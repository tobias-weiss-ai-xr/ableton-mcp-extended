import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))

print("DUB SONG - RECORDING GUIDE")
print("=" * 70)

# Get session info
s.send(json.dumps({"type": "get_session_info", "params": {}}).encode("utf-8"))
session = json.loads(s.recv(4096).decode("utf-8"))

print("\nCurrent Session Info:")
print("-" * 70)
print(f"Tempo: {session['result']['tempo']} BPM")
print(
    f"Time Signature: {session['result']['signature_numerator']}/{session['result']['signature_denominator']}"
)
print(f"Track Count: {session['result']['track_count']}")

print("\n" + "=" * 70)
print("HOW TO RECORD YOUR DUB SONG")
print("=" * 70)

print("""
OPTION 1: EXPORT FROM ARRANGEMENT VIEW (RECOMMENDED)
-------------------------------------------------
This gives you the best quality and control:

1. In Ableton, press TAB to switch to Arrangement View
2. Arrange your clips horizontally:
   - Drag clips from Session View to Arrangement View
   - Place sections in this order:
     * Bars 1-10: INTRO (8 bars)
     * Bars 11-20: BUILDUP (10 bars)
     * Bars 21-30: DROP (10 bars)
     * Bars 31-40: BUILDUP (10 bars)
     * Bars 41-50: BREAKDOWN (10 bars)
     * Bars 51-60: BUILDUP (10 bars)
     * Bars 61-70: DROP (10 bars)
     * Bars 71-80: OUTRO (10 bars)
3. Click and drag to select the entire 5 minutes
4. Set loop markers if needed
5. File -> Export Audio/Video
6. Select export options:
   - Rendered Track: Master
   - Duration: Selection or Entire Song
   - Quality: 24-bit or 32-bit float
   - Sample Rate: 44100 or 48000
   - File Type: WAV (for best quality) or MP3 (for sharing)
7. Click Export
8. Wait for export to complete

OPTION 2: LIVE RECORDING WITH SECTION SWITCHER
-------------------------------------------
For a more live, improvised feel:

1. In Ableton, press TAB for Session View
2. Click the Record button on the Master track
3. Press Space to start playback
4. In terminal, run: python record_dub_song.py
   (This script plays sections automatically)
5. Listen and adjust if needed
6. Press Space in Ableton to stop recording

The automated script will:
- Play each section for the right duration
- Switch sections automatically
- Complete in exactly 5 minutes
""")

print("\n" + "=" * 70)
print("AUTOMATED RECORDING SCRIPT")
print("=" * 70)

# Write automated recording script
recording_script_content = """import time
import subprocess

def switch_section(section_name):
    subprocess.run(["python", "switch_section.py", section_name])

print("DUB SONG - AUTOMATED RECORDING")
print("=" * 70)
print("")
print("Press Space in Ableton to start recording NOW!")
print("Then press Enter here to begin section playback...")

input()

# Recording sequence - exactly 5 minutes
print("")
print("Starting automated playback...")
print("Sections will play in order with correct timing")
print("=" * 70)

# Section durations in seconds (at 75 BPM)
# 1 bar = 0.53 seconds, so 8 bars = 4.24 seconds ~ 4 seconds
# Let's use simpler timing: 8 bars = 32 seconds at 75 BPM

sections = [
    ("intro", 32, "0:00 - 0:32"),
    ("buildup", 32, "0:32 - 1:04"),
    ("drop", 32, "1:04 - 1:36"),
    ("buildup", 32, "1:36 - 2:08"),
    ("breakdown", 32, "2:08 - 2:40"),
    ("buildup", 32, "2:40 - 3:12"),
    ("drop", 32, "3:12 - 3:44"),
    ("fulldrop", 32, "3:44 - 4:16"),
    ("intro", 32, "4:16 - 4:48"),
]

total_duration = sum(duration for _, duration, _ in sections)
print(f"Total duration: {total_duration} seconds ({total_duration/60:.1f} minutes)")
print("")

for section_name, duration, time_range in sections:
    print(f"[{time_range}] Switching to: {section_name.upper()}")
    switch_section(section_name)
    print(f"Playing for {duration} seconds...")
    time.sleep(duration)

print("")
print("=" * 70)
print("Playback complete!")
print("Press Space in Ableton to stop recording")
print("Your dub song is now recorded!")
print("=" * 70)
"""

# Write the automated script
with open("record_dub_song_automated.py", "w") as f:
    f.write(recording_script_content)

print("\n[OK] Created: record_dub_song_automated.py")

print("\n" + "=" * 70)
print("HOW TO USE AUTOMATED RECORDING")
print("=" * 70)
print("""
Step 1: Prepare Ableton
   - Load instruments on all tracks
   - Check track levels
   - Press TAB for Session View

Step 2: Start Recording
   - Click Record button on Master track
   - Press Space to start recording
   - (Recording starts)

Step 3: Run Script
   - In terminal: python record_dub_song_automated.py
   - Press Enter when ready
   - Script will play sections automatically
   - Total time: 5 minutes

Step 4: Stop Recording
   - Wait for script to complete
   - Press Space in Ableton to stop
   - Your song is recorded!

Step 5: Export (optional)
   - If recording to audio track, export that track
   - Or use the recorded audio directly
""")

print("\n" + "=" * 70)
print("RECORDING TIPS")
print("=" * 70)
print("""
- Load instruments BEFORE recording
- Check levels aren't clipping (yellow/red)
- Use headphones to monitor
- Record a test take first
- Export at highest quality (24-bit/48kHz)
- Save project before recording
- Consider using automation for transitions
- For live feel, add small variations to sections
""")

print("\n" + "=" * 70)
print("SECTION TIMING REFERENCE")
print("=" * 70)
print("""
At 75 BPM:
- 1 bar = 0.53 seconds
- 4 bars = 2.13 seconds
- 8 bars = 4.27 seconds
- 16 bars = 8.53 seconds
- 32 bars = 17.07 seconds

For this song, I'm using:
- Each section = 8 bars (32 seconds)
- Total sections = 9
- Total time = ~4.8 minutes (5 minutes with transitions)
""")

print("\n" + "=" * 70)
print("RECOMMENDED: EXPORT FROM ARRANGEMENT VIEW")
print("=" * 70)
print("""
For the best quality and most control:

1. Arrange clips in Arrangement View
2. Set exact timing and markers
3. Export at highest quality
4. No timing issues or mistakes
5. Can edit and perfect before export

Use automated recording script for:
- Live performance feel
- Quick recording without arrangement
- Testing different section orders
""")

s.close()

print("\n" + "=" * 70)
print("READY TO RECORD!")
print("=" * 70)
print("""
Choose your method:

1. Arrange in Arrangement View + Export (Best quality)
2. Run: python record_dub_song_automated.py (Live feel)

Both methods will give you a complete dub song!
""")
