"""
Verify that clips exist across all 8 scenes with appropriate melody lengths.
Checks: 8 tracks x 8 scenes = 64 clips expected
"""
import socket
import json

s = socket.socket()
s.connect(("localhost", 9877))

def send_command(cmd_type, params=None):
    s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
    return json.loads(s.recv(8192).decode("utf-8"))

TRACK_NAMES = [
    "Drums",  # 0
    "Bass",  # 1
    "FX_Risers",  # 2
    "Pad_Atmos",  # 3
    "Rhythm_Skank",  # 4
    "Horns_Melody",  # 5 - THIS IS THE MELODY TRACK!
    "Percussion",  # 6
    "Vocal_Chops",  # 7
]

SCENE_NAMES = [
    "Basic_4bar",
    "Extended_8bar",
    "Harmonic_Shift",
    "Syncopated",
    "Sparse_Breakdown",
    "Dense_Buildup",
    "Full_Arrangement",
    "Climax_16bar",
]

# Calculate expected length based on note durations and start times
def estimate_clip_length_from_notes(notes):
    """Estimate clip length from note data"""
    if not notes:
        return 0.0
    
    max_end_time = max(note.get("start_time", 0) + note.get("duration", 0) for note in notes)
    return max_end_time

print("=" * 80)
print("VERIFYING CLIPS ACROSS ALL 8 SCENES")
print("=" * 80)

# Track results
track_results = []
melody_results = []  # Track 5 (Horns_Melody)

for track_idx in range(8):
    track_name = TRACK_NAMES[track_idx]
    print(f"\nTrack {track_idx}: {track_name}")
    print("-" * 80)
    
    track_clips = []
    
    for scene_idx in range(8):
        scene_name = SCENE_NAMES[scene_idx]
        
        # Check if clip exists
        result = send_command("get_clip_notes", {
            "track_index": track_idx,
            "clip_index": scene_idx
        })
        
        if result.get("status") == "success":
            notes = result.get("result", {}).get("notes", [])
            note_count = len(notes)
            
            # Estimate clip length from notes
            estimated_length = estimate_clip_length_from_notes(notes)
            
            has_clip = True
        else:
            note_count = 0
            estimated_length = 0.0
            has_clip = False
        
        track_clips.append({
            "scene": scene_idx,
            "scene_name": scene_name,
            "has_clip": has_clip,
            "note_count": note_count,
            "length": estimated_length
        })
        
        # Special focus on melody track (track 5)
        if track_idx == 5:
            melody_results.append({
                "scene": scene_idx,
                "scene_name": scene_name,
                "has_clip": has_clip,
                "note_count": note_count,
                "length": estimated_length
            })
        
        # Print status
        status = "[OK]" if has_clip else "[MISSING]"
        length_str = f"{estimated_length:.1f} bars" if estimated_length > 0 else "N/A"
        note_str = f"{note_count} notes" if note_count > 0 else "empty"
        print(f"  Scene {scene_idx} ({scene_name:15s}) {status:10s} {length_str:10s} {note_str}")
    
    track_results.append({
        "track_idx": track_idx,
        "track_name": track_name,
        "clips": track_clips
    })

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_expected = 64
total_with_clips = 0
total_with_notes = 0

for track in track_results:
    clips_with_content = sum(1 for c in track["clips"] if c["has_clip"])
    clips_with_notes = sum(1 for c in track["clips"] if c["note_count"] > 0)
    
    print(f"\nTrack {track['track_idx']} ({track['track_name']}): {clips_with_content}/8 clips have content, {clips_with_notes}/8 have notes")
    
    total_with_clips += clips_with_content
    total_with_notes += clips_with_notes

print(f"\nTotal: {total_with_clips}/{total_expected} clips with content, {total_with_notes}/{total_expected} clips with notes")

# MELODY VERIFICATION (Track 5: Horns_Melody)
print("\n" + "=" * 80)
print("MELODY VERIFICATION (Track 5: Horns_Melody)")
print("=" * 80)
print("\nOriginal task: 'make sure melodies are longer than just a few bars'")
print("Checking Track 5 (Horns_Melody) across all 8 scenes:\n")

melody_long_count = 0
melody_short_count = 0
melody_missing_count = 0

for melody in melody_results:
    scene = melody["scene"]
    scene_name = melody["scene_name"]
    has_clip = melody["has_clip"]
    note_count = melody["note_count"]
    length = melody["length"]
    
    # Check if melody is "longer than just a few bars"
    # We'll consider < 4 bars as "a few bars"
    is_long_enough = length >= 4.0
    
    if not has_clip:
        status = "[MISSING]"
        melody_missing_count += 1
    elif is_long_enough:
        status = "[LONG]"
        melody_long_count += 1
    else:
        status = "[SHORT]"
        melody_short_count += 1
    
    actual_str = f"{length:.1f} bars" if length > 0 else "0.0 bars"
    print(f"  Scene {scene} ({scene_name:15s}) {status:10s} Actual: {actual_str:8s} Notes: {note_count}")

print("\n" + "-" * 80)
print(f"Melody clips summary:")
print(f"  Long enough (>=4 bars): {melody_long_count}/8")
print(f"  Too short (<4 bars):   {melody_short_count}/8")
print(f"  Missing clips:         {melody_missing_count}/8")

# Overall verdict
print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if total_with_notes == 64:
    print("[SUCCESS] All 64 clips created with MIDI content!")
elif total_with_clips == 64:
    print("[WARNING] All 64 clips exist, but some may be empty")
else:
    print(f"[FAIL] Only {total_with_clips}/64 clips exist")

print("\nMelody verification:")
if melody_long_count == 8:
    print("[PASS] All melody clips are longer than 'a few bars' (>=4 bars)")
elif melody_long_count >= 6:
    print(f"[PARTIAL] {melody_long_count}/8 melody clips are long enough")
else:
    print(f"[FAIL] Only {melody_long_count}/8 melody clips are long enough")
    print("       Original requirement: 'make sure melodies are longer than just a few bars'")

s.close()
