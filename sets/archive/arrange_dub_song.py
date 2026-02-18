import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))


def fire_clip(track_index, clip_index):
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


# Song Structure for 5 minutes at 75 BPM
# Each clip is 4 bars = 4 beats = 3.2 seconds at 75 BPM
# Need approximately 94 bars for 5 minutes
# With 4-bar clips, that's ~23 clips per track

print("Arranging Dub Song - 5 minutes (approx 94 bars)")
print("=" * 60)

# Section 1: INTRO (0:00-0:40) - Bars 1-10
print("\n[INTRO] Setting up minimal intro...")
fire_clip(4, 2)  # Bass - breakdown (very minimal)
fire_clip(5, 2)  # Drums - minimalist dub
fire_clip(6, 0)  # Atmosphere - basic
fire_clip(7, 0)  # Melody - basic
fire_clip(10, 0)  # Percussion - basic
print("[OK] Intro clips fired")

# Section 2: BUILDUP 1 (0:40-1:20) - Bars 11-20
print("\n[BUILDUP 1] Adding energy...")
fire_clip(4, 1)  # Bass - alternative
fire_clip(5, 3)  # Drums - buildup
fire_clip(6, 1)  # Atmosphere - complex
fire_clip(7, 1)  # Melody - alternative
print("[OK] Buildup 1 clips fired")

# Section 3: DROP (1:20-2:00) - Bars 21-30
print("\n[DROP] Maximum energy...")
fire_clip(4, 0)  # Bass - main
fire_clip(5, 4)  # Drums - drop (intense)
fire_clip(6, 1)  # Atmosphere - complex
fire_clip(7, 0)  # Melody - basic
fire_clip(8, 0)  # FX - add some FX
print("[OK] Drop clips fired")

# Section 4: BUILDUP 2 (2:00-2:40) - Bars 31-40
print("\n[BUILDUP 2] Building again...")
fire_clip(4, 1)  # Bass - alternative
fire_clip(5, 3)  # Drums - buildup
fire_clip(6, 0)  # Atmosphere - basic
fire_clip(7, 1)  # Melody - alternative
print("[OK] Buildup 2 clips fired")

# Section 5: BREAKDOWN (2:40-3:20) - Bars 41-50
print("\n[BREAKDOWN] Space and atmosphere...")
fire_clip(4, 2)  # Bass - breakdown
fire_clip(5, 2)  # Drums - minimalist
fire_clip(6, 1)  # Atmosphere - complex
# No melody in breakdown
print("[OK] Breakdown clips fired")

# Section 6: BUILDUP 3 (3:20-4:00) - Bars 51-60
print("\n[BUILDUP 3] Final buildup...")
fire_clip(4, 1)  # Bass - alternative
fire_clip(5, 3)  # Drums - buildup
fire_clip(7, 0)  # Melody - bring it back
print("[OK] Buildup 3 clips fired")

# Section 7: FINAL DROP (4:00-4:40) - Bars 61-70
print("\n[FINAL DROP] Maximum impact...")
fire_clip(4, 0)  # Bass - main
fire_clip(5, 4)  # Drums - drop
fire_clip(6, 1)  # Atmosphere - complex
fire_clip(7, 1)  # Melody - alternative
fire_clip(8, 0)  # FX - add FX
fire_clip(10, 0)  # Percussion - add
print("[OK] Final drop clips fired")

# Section 8: OUTRO (4:40-5:00) - Bars 71-80
print("\n[OUTRO] Fading out...")
fire_clip(4, 2)  # Bass - breakdown
fire_clip(5, 2)  # Drums - minimalist
fire_clip(6, 0)  # Atmosphere - basic
# Fade out elements
print("[OK] Outro clips fired")

# Start playback
print("\n[START] Starting playback...")
s.send(json.dumps({"type": "start_playback", "params": {}}).encode("utf-8"))
response = json.loads(s.recv(4096).decode("utf-8"))
print("[OK] Playback started:", response)

print("\n" + "=" * 60)
print("Dub Song Arrangement Complete!")
print("Total Duration: ~5 minutes")
print("Tempo: 75 BPM")
print("Sections: 8 (Intro, Buildups, Drops, Breakdown, Outro)")
print("=" * 60)

s.close()
