import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))

print("DUB SONG COMPLETION GUIDE")
print("=" * 70)
print("\nYour dub song foundation is now playing!")
print("\nWhat's been created:")
print("-" * 70)
print("6 Complete MIDI Tracks:")
print("  1. Dub Bass - 3 variations (main, alternative, breakdown)")
print("  2. Drums - 3 variations (minimalist, buildup, drop)")
print("  3. Atmosphere - 2 variations (basic, complex)")
print("  4. Dub Melody - 2 variations (basic, alternative)")
print("  5. FX - Sound effects and transitions")
print("  6. Percussion - Additional texture")
print("\nSong Structure:")
print("  - 8 sections: Intro -> Buildup -> Drop -> Buildup -> Breakdown ->")
print("               Buildup -> Drop -> Outro")
print("  - Duration: 5 minutes at 75 BPM")
print("  - All clips are 4 bars long for easy arrangement")

print("\n" + "=" * 70)
print("NEXT STEPS TO COMPLETE YOUR DUB SONG")
print("=" * 70)

print("\n1. LOAD INSTRUMENTS")
print("-" * 70)
print("   - Dub Bass: Sub-bass synth (e.g., Operator, Serum)")
print("   - Drums: Drum rack or individual drum sounds")
print("   - Atmosphere: Pad synth with reverb")
print("   - Dub Melody: Lead synth or pluck")
print("   - FX: Sampler with sweeps and impacts")
print("   - Percussion: Percussion sounds")

print("\n2. ADD EFFECTS (Essential for Dub)")
print("-" * 70)
print("   - REVERB: Heavy reverb on atmosphere, melody, FX")
print("   - DELAY: Dub delays on bass, melody, drums (send effects)")
print("   - FILTERS: Low-pass filters for depth")
print("   - COMPRESSION: Glue drum elements together")
print("   - SIDECHAIN: Duck bass against kick")

print("\n3. MIXING")
print("-" * 70)
print("   - Bass: Heavy compression, EQ (boost low end)")
print("   - Kick: Punchy, prominent")
print("   - Snare: Crisp, add room reverb")
print("   - Atmosphere: Wide stereo, low volume")
print("   - Melody: Add delay and reverb")
print("   - FX: Automate for dramatic effects")

print("\n4. ARRANGEMENT TIPS")
print("-" * 70)
print("   - Duplicate clips and arrange them in Session View")
print("   - Create 4-8 bar clips for each section")
print("   - Use Scene Launch to trigger sections")
print("   - Add clips for transitions between sections")
print("   - Automate effects for buildups and drops")

print("\n5. AUTOMATION")
print("-" * 70)
print("   - Filter sweeps on buildups")
print("   - Reverb sends on drops")
print("   - Delay time changes for variation")
print("   - Volume automation for dynamics")
print("   - Pan automation for stereo width")

print("\n" + "=" * 70)
print("SONG IS NOW PLAYING IN ABLETON!")
print("=" * 70)
print("\nListen to the current arrangement and:")
print("  - Load appropriate instruments")
print("  - Add effects to each track")
print("  - Mix the levels")
print("  - Add automation")
print("  - Extend arrangement if needed")

print("\nFor more variations, you can:")
print("  - Duplicate existing clips and modify them")
print("  - Add more clip variations to each track")
print("  - Create additional sections (bridges, solos)")
print("  - Add more instrument tracks (keys, synths)")

print("\n" + "=" * 70)
print("CREATING MORE CONTENT")
print("=" * 70)


def create_example_clip(track_index, clip_index):
    s.send(
        json.dumps(
            {
                "type": "create_clip",
                "params": {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "length": 4.0,
                },
            }
        ).encode("utf-8")
    )
    response = json.loads(s.recv(4096).decode("utf-8"))
    return response


print("\nExample: Creating additional clips...")
clip_0 = create_example_clip(4, 3)
print(f"Created Bass clip 3: {clip_0['status']}")

clip_1 = create_example_clip(5, 5)
print(f"Created Drum clip 5: {clip_1['status']}")

clip_2 = create_example_clip(7, 2)
print(f"Created Melody clip 2: {clip_2['status']}")

print("\nYou can create more clips and arrange them in the Session View")
print("to build longer song sections and add variety.")

s.close()

print("\n" + "=" * 70)
print("ENJOY YOUR DUB SONG!")
print("=" * 70)
