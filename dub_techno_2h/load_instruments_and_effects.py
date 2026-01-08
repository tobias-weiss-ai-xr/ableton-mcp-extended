import socket
import json
import time

s = socket.socket()
s.connect(("localhost", 9877))


def send_command(cmd_type, params=None):
    """Send a command and return full response"""
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    data = b""
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            continue
    return json.loads(data.decode("utf-8"))


# ============================================================================
# LOAD INSTRUMENTS AND SOUNDS
# ============================================================================

print("=" * 80)
print("LOADING INSTRUMENTS AND SOUNDS FOR 2-HOUR DUB TECHNOPO")
print("=" * 80)

# Load Operator (synth) on Kick track
print("\n[1/6] Loading instrument on Kick track (Track 4)...")
result = send_command(
    "load_browser_item", {"track_index": 0, "uri": "query:Synths#Operator"}
)
print(f"   Result: {result.get('result', result)}")

# Load Tension (sub-bass synth) on Sub-bass track
print("\n[2/6] Loading instrument on Sub-bass track (Track 5)...")
result = send_command(
    "load_browser_item", {"track_index": 1, "uri": "query:Synths#Tension"}
)
print(f"   Result: {result.get('result', result)}")

# Load Drum Rack on Hi-hats track
print("\n[3/6] Loading instrument on Hi-hats track (Track 6)...")
result = send_command(
    "load_browser_item", {"track_index": 2, "uri": "query:Synths#Drum%20Rack"}
)
print(f"   Result: {result.get('result', result)}")

# Load Wavetable on Synth Pads track
print("\n[4/6] Loading instrument on Synth Pads track (Track 7)...")
result = send_command(
    "load_browser_item", {"track_index": 3, "uri": "query:Synths#Wavetable"}
)
print(f"   Result: {result.get('result', result)}")

# Load Simpler (sampler) on FX track
print("\n[5/6] Loading instrument on FX track (Track 8)...")
result = send_command(
    "load_browser_item", {"track_index": 4, "uri": "query:Synths#Simpler"}
)
print(f"   Result: {result.get('result', result)}")

# Dub Delays track is for send routing - no instrument needed
print("\n[6/6] Dub Delays track (Track 9) - Send track, no instrument needed")
print("   [OK] Ready for delay send routing")

print("\n" + "=" * 80)
print("ALL INSTRUMENTS LOADED")
print("=" * 80)

# ============================================================================
# ADD AUDIO EFFECTS
# ============================================================================

print("\n" + "=" * 80)
print("ADDING AUDIO EFFECTS")
print("=" * 80)

# Add EQ Eight to each main track
print("\nAdding EQ Eight to tracks for tonal control...")

for track_idx in [4, 5, 6, 7, 8]:
    result = send_command(
        "load_browser_item",
        {"track_index": track_idx, "uri": "query:AudioFx#EQ%20Eight"},
    )
    print(f"   Track {track_idx}: {result.get('result', result)}")

# Add Compressor to Kick and Sub-bass
print("\nAdding Compressor to Kick and Sub-bass tracks...")

for track_idx in [4, 5]:
    result = send_command(
        "load_browser_item",
        {"track_index": track_idx, "uri": "query:AudioFx#Compressor"},
    )
    print(f"   Track {track_idx}: {result.get('result', result)}")

# ============================================================================
# CREATE SEND TRACKS FOR REVERB AND DELAY
# ============================================================================

print("\n" + "=" * 80)
print("CREATING SEND TRACKS")
print("=" * 80)

# Create Reverb Send track
print("\nCreating Reverb Send track...")
send_command("create_midi_track", {"index": 6})
send_command("set_track_name", {"track_index": 6, "name": "Reverb Send"})
result = send_command(
    "load_browser_item",
    {"track_index": 6, "uri": "query:AudioFx#Hybrid%20Reverb"},
)
print(f"   Loaded Hybrid Reverb: {result.get('result', result)}")

# Create Delay Send track
print("\nCreating Delay Send track...")
send_command("create_midi_track", {"index": 7})
send_command("set_track_name", {"track_index": 7, "name": "Delay Send"})
result = send_command(
    "load_browser_item",
    {"track_index": 7, "uri": "query:AudioFx#Simple%20Delay"},
)
print(f"   Loaded Simple Delay: {result.get('result', result)}")

print("\n" + "=" * 80)
print("SEND TRACKS CREATED")
print("=" * 80)

# ============================================================================
# ADDITIONAL EFFECTS FOR DUB TECHNOPO SOUND
# ============================================================================

print("\n" + "=" * 80)
print("ADDING DUB-SPECIFIC EFFECTS")
print("=" * 80)

# Add Auto Filter to Synth Pads for evolution
print("\nAdding Auto Filter to Synth Pads (Track 7) for filter automation...")
result = send_command(
    "load_browser_item",
    {"track_index": 3, "uri": "query:AudioFx#Auto%20Filter"},
)
print(f"   Result: {result.get('result', result)}")

# Add Glue Compressor to master for cohesion
print("\nAdding Utility to Dub Delays track (Track 9)...")
result = send_command(
    "load_browser_item", {"track_index": 5, "uri": "query:AudioFx#Utility"}
)
print(f"   Result: {result.get('result', result)}")

# ============================================================================
# CONFIGURATION COMPLETE
# ============================================================================

print("\n" + "=" * 80)
print("INSTRUMENT AND EFFECTS SETUP COMPLETE!")
print("=" * 80)

print("\nInstrument Summary:")
print("  Track 4 (Kick):        Operator")
print("  Track 5 (Sub-bass):    Tension")
print("  Track 6 (Hi-hats):     Drum Rack")
print("  Track 7 (Synth Pads):  Wavetable + Auto Filter")
print("  Track 8 (FX):          Simpler")
print("  Track 9 (Dub Delays):  Utility (send track)")

print("\nEffects Summary:")
print("  Track 10 (Reverb Send):  Hybrid Reverb")
print("  Track 11 (Delay Send):   Simple Delay")
print("  All main tracks:          EQ Eight")
print("  Tracks 4-5 (Kick/Bass): Compressor")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
1. Configure instrument presets:
   - Kick: Create a punchy kick sound in Operator
   - Sub-bass: Design deep sub sound in Tension
   - Hi-hats: Load hi-hat samples in Drum Rack
   - Synth Pads: Choose atmospheric pad preset in Wavetable
   - FX: Load FX samples (sweeps, impacts) in Simpler

2. Configure effects:
   - EQ Eight: Shape the tone of each track
   - Compressor: Add punch to kick and glue to bass
   - Auto Filter: Automate filter on Synth Pads for evolution
   - Reverb Send: Set to Large Hall, add reverb tails
   - Delay Send: Set to dub delay (1/4 or 1/8 notes)

3. Set up send routing (in Ableton):
   - For each track (4-9), create sends to Track 10 (Reverb) and Track 11 (Delay)
   - Send levels:
     * Kick: 0%
     * Sub-bass: 5-10%
     * Hi-hats: 20-30%
     * Synth Pads: 40-50%
     * FX: 60-70%
     * Dub Delays: 80-100%

4. Mix track levels:
   - Kick: Reference level (-6 to -8 dB)
   - Sub-bass: -3 to -6 dB relative to kick
   - Hi-hats: -12 to -15 dB
   - Synth Pads: -18 to -24 dB
   - FX: -15 to -20 dB
   - Reverb Send: -15 dB
   - Delay Send: -12 dB

5. Add automation:
   - Filter sweeps on Synth Pads during buildups
   - Reverb sends during breakdowns
   - Delay sends during hypnotic sections
   - Volume automation for dynamic movement

6. Save the project and enjoy your 2-hour dub techno journey!
""")

print("=" * 80)
print("SETUP COMPLETE - READY FOR CONFIGURATION")
print("=" * 80)

s.close()
