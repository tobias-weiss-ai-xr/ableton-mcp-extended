"""
Reggae Baseline - Short reggae template

Creates a foundational reggae track with:
- 2 sections (16 bars each, ~32 bars total)
- 70 BPM tempo
- Classic reggae instrumentation (bass, drums, keys)
- Offbeat skank patterns
- Dub effects setup

Usage:
    python reggae_baseline.py
"""

import socket
import json
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

REGGAE_TEMPO = 70.0
SECTIONS = [
    {"name": "Intro", "bars": 8, "bpm": REGGAE_TEMPO},
    {"name": "Drop", "bars": 8, "bpm": REGGAE_TEMPO},
]

TRACKS = {
    "Kick": {"index": 0, "name": "Reggae Kick"},
    "Bass": {"index": 1, "name": "Reggae Bass"},
    "Hi-Hats": {"index": 2, "name": "Reggae Hi-Hats"},
    "Clap": {"index": 3, "name": "Reggae Clap"},
    "Guitar": {"index": 4, "name": "Reggae Guitar"},
    "Keys": {"index": 5, "name": "Reggae Keys"},
    "FX": {"index": 6, "name": "Dub FX"},
}

# Note: MIDI pitch 36 = C2
# Note: MIDI velocity 100-110 for percussive, 80-90 for melodic
REGGAE_ROOT_NOTE = 36

# ============================================================================
# SOCKET COMMUNICATION
# ============================================================================

def send_command(cmd_type, params=None):
    """Send a command and return the response"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 9877))
    
    try:
        s.send(json.dumps({"type": cmd_type, "params": params or {}}).encode("utf-8"))
        response = json.loads(s.recv(8192).decode("utf-8"))
        return response
    finally:
        s.close()

def safe_send_command(cmd_type, params=None, max_retries=3):
    """Send command with retry logic"""
    for attempt in range(max_retries):
        try:
            result = send_command(cmd_type, params)
            if result.get("success", False):
                return result["result"]
            print(f"  [WARN] Command failed: {cmd_type}")
        except (ConnectionRefusedError, ConnectionResetError) as e:
            print(f" [ERROR] Connection error: {e}")
            time.sleep(0.5)
    return None

# ============================================================================
# PATTERN GENERATION
# ============================================================================

def get_kick_pattern(start_beat):
    """Generate 8-beat reggae kick pattern with variations"""
    # Reggae kick: 4-beat bar (on beats 1, 3, and offbeat accent)
    # Pattern: X . . . X . . . (bar 1), then variation
    
    kick_notes = []
    
    # Bar 1: Basic 4-beat with offbeat
    for bar in range(4):
        beat = start_beat + (bar * 4)
        kick_notes.extend([
            {"pitch": REGGAE_ROOT_NOTE, "start_time": beat, "duration": 0.25, "velocity": 120},
            {"pitch": REGGAE_ROOT_NOTE, "start_time": beat + 1.0, "duration": 0.125, "velocity": 110, "mute": True},  # Offbeat
            {"pitch": REGGAE_ROOT_NOTE, "start_time": beat + 2.0, "duration": 0.125, "velocity": 120},
            {"pitch": REGGAE_ROOT_NOTE, "start_time": beat + 3.0, "duration": 0.125, "velocity": 120},
        ])
    
    # Bar 2: Syncopated pattern (every bar)
    for bar in range(4, 8):
        beat = start_beat + (bar * 4)
        kick_notes.extend([
            {"pitch": REGGAE_ROOT_NOTE, "start_time": beat, "duration": 0.25, "velocity": 115},
            {"pitch": REGGAE_ROOT_NOTE, "start_time": beat + 1.0, "duration": 0.125, "velocity": 100},
            {"pitch": REGG_ROOT_NOTE, "start_time": beat + 2.0, "duration": 0.125, "velocity": 115},
            {"pitch": REGG_ROOT_NOTE, "start_time": beat + 3.0, "duration": 0.125, "velocity": 115},
        ])
    
    return kick_notes

def get_bass_pattern(start_beat):
    """Generate 8-beat reggae bass pattern"""
    # Root and fifth (octave down) emphasize low frequencies
    # Simple steady rhythm with occasional skips for reggae feel
    
    bass_notes = []
    
    for bar in range(8):
        beat = start_beat + (bar * 4)
        
        # Bar 1-2: Playing on beats 1 and 3
        if bar < 2:
            bass_notes.extend([
                {"pitch": REGGAE_ROOT_NOTE, "start_time": beat, "duration": 1.0, "velocity": 95},      # C2
                {"pitch": REGGAE_ROOT_NOTE + 12, "start_time": beat + 2.0, "duration": 0.5, "velocity": 90},  # G2
            ])
        # Bar 3+: On beat 1 only, with rest (skank feel)
        else:
            bass_notes.extend([
                {"pitch": REGGAE_ROOT_NOTE, "start_time": beat, "duration": 0.5, "velocity": 95},
                {"pitch": REGGAE_ROOT_NOTE + 12, "start_time": beat + 2.5, "duration": 1.0, "velocity": 85},
                {"pitch": REGGAE_ROOT_NOTE, "start_time": beat + 3.5, "duration": 0.5, "velocity": 85},
            ])
    
    return bass_notes

def get_hi_hat_pattern(start_beat):
    """Generate 8-beat hi-hat pattern (typical reggae: 2 and 4)"""
    # Reggae hi-hats: On beats 2 and 4 (2-4-2-4-2-4...)
    # Occasional triplet for variation
    
    hat_notes = []
    
    for bar in range(8):
        beat = start_beat + (bar * 4)
        
        if bar % 2 == 0:
            # Bar with triplets
            hat_notes.extend([
                {"pitch": REGGAE_ROOT_NOTE + 24, "start_time": beat, "duration": 0.125, "velocity": 70},  # D#4
                {"pitch": REGGAE_ROOT_NOTE + 24, "start_time": beat + 1.0, "duration": 0.0625, "velocity": 70},  # triplet first 16th
                {"pitch": REGAE_ROOT_NOTE + 24, "start_time": beat + 1.1875, "duration": 0.0625, "velocity": 70}, # triplet
                {"pitch": REGAE_ROOT_NOTE + 24, "start_time": beat + 2.0, "duration": 0.125, "velocity": 75},
                {"pitch": REGAE_ROOT_NOTE + 24, "start_time": beat + 3.0, "duration": 0.125, "velocity": 75},
            ])
        else:
            # Standard 2 and 4
            hat_notes.extend([
                {"pitch": REGAE_ROOT_NOTE + 24, "start_time": beat, "duration": 0.125, "velocity": 65},
                {"pitch": REGAE_ROOT_NOTE + 24, "start_time": beat + 2.0, "duration": 0.125, "velocity": 70},
                {"pitch": REGAE_ROOT_NOTE + 24, "start_time": beat + 3.0, "duration": 0.125, "velocity": 70},
            ])
    
    return hat_notes

def get_clap_pattern(start_beat):
    """Generate 8-beat reggae clap pattern (2 and 4 with skank)"""
    # Reggae clap: Emphasize beat 3 (offbeat after 2)
    # Occasional roll or ghost notes on beat 1
    
    clap_notes = []
    
    for bar in range(8):
        beat = start_beat + (bar * 4)
        
        if bar % 3 == 0:
            # Emphasize offbeat after 2
            clap_notes.extend([
                {"pitch": REGGAE_ROOT_NOTE + 12, "start_time": beat, "duration": 0.0625, "velocity": 80},
                {"pitch": REGGAE_ROOT_NOTE + 12, "start_time": beat + 0.125, "velocity": 90},   # Offbeat accent
                {"pitch": REGAE_ROOT_NOTE + 12, "start_time": beat + 1.0, "duration": 0.125, "velocity": 85},
                {"pitch": REGAE_ROOT_NOTE + 12, "start_time": beat + 2.0, "duration": 0.125, "velocity": 85},
            ])
        else:
            clap_notes.extend([
                {"pitch": REGGAE_ROOT_NOTE + 12, "start_time": beat, "duration": 0.125, "velocity": 75},
                {"pitch": REGAE_ROOT_NOTE + 12, "start_time": beat + 1.0, "duration": 0.125, "velocity": 90},
                {"pitch": REGAE_ROOT_NOTE + 12, "start_time": beat + 2.0, "duration": 0.125, "velocity": 75},
                {"pitch": REGAE_ROOT_NOTE + 12, "start_time": beat + 3.0, "duration": 0.125, "velocity": 90},  # Emphasize beat 3
            ])
    
    return clap_notes

def get_guitar_skank_pattern(start_beat):
    """Generate 8-beat guitar skank pattern"""
    # Skank guitar: Offbeat rhythms, typically on beats 2 and 4
    # Reggae: Occasional chromatic notes for color
    
    guitar_notes = []
    chord_root = REGGAE_ROOT_NOTE  # C2 base
    
    for bar in range(8):
        beat = start_beat + (bar * 4)
        
        # Every bar: simple offbeat pattern (2 and 4)
        guitar_notes.extend([
            {"pitch": chord_root, "start_time": beat + 0.25, "duration": 0.5, "velocity": 70},      # Root
            {"pitch": chord_root + 4, "start_time": beat + 2.25, "duration": 0.25, "velocity": 65},       # Third (E2)
            {"pitch": chord_root + 7, "start_time": beat + 3.25, "duration": 0.5, "velocity": 65},       # Fifth (G2)
        ])
    
    return guitar_notes

def get_keys_pattern(start_beat):
    """Generate 8-beat reggae keys pattern (chords)"""
    # Reggae keys: Simple triads on downbeats
    # Keys: Am, F, G, C (root of C2)
    
    keys_chord_roots = [
        REGGAE_ROOT_NOTE,      # C
        REGGAE_ROOT_NOTE + 3, # D
        REGGAE_ROOT_NOTE + 5,  # F
        REGGAE_ROOT_NOTE + 9,  # G
        REGGAE_ROOT_NOTE - 12,  # Ab (minor)
    ]
    
    keys_notes = []
    
    for bar in range(8):
        beat = start_beat + (bar * 4)
        chord_root = keys_chord_roots[bar % len(keys_chord_roots)]
        
        # Simple triad on downbeats: 1, 2, 3
        keys_notes.extend([
            {"pitch": chord_root, "start_time": beat + 0.25, "duration": 0.75, "velocity": 65},
            {"pitch": chord_root + 4, "start_time": beat + 1.25, "duration": 0.75, "velocity": 60},
            {"pitch": chord_root + 7, "start_time": beat + 2.25, "duration": 0.75, "velocity": 60},
        ])
    
    return keys_notes

# ============================================================================
# TRACK CREATION
# ============================================================================

def create_tracks():
    """Create all tracks for reggae baseline"""
    print("\n[1/7] Creating reggae tracks...")
    
    # Sort tracks by desired index
    sorted_tracks = sorted(TRACKS.items(), key=lambda x: x[1]["index"])
    
    for track_name, track_info in sorted_tracks:
        print(f"[2/7] Creating {track_name} track (index {track_info['index']})...")
        
        result = safe_send_command(
            "create_midi_track",
            {"index": track_info["index"]}
        )
        
        if result is None:
            print(f"   [ERROR] Failed to create {track_name}")
            return False
        
        result = safe_send_command(
            "set_track_name",
            {
                "track_index": track_info["index"],
                "name": track_info["name"]
            }
        )
        
        if result.get("success", False):
            print(f"   [OK] Named {track_info['name']}")
        else:
            print(f"   [WARN] Name might not have taken")
    
    time.sleep(0.2)
    return True

# ============================================================================
# CLIP CREATION
# ============================================================================

def create_clip(track_index, clip_index, notes, section_name, bars=8):
    """Create a MIDI clip with notes"""
    print(f"[3/7] Creating {section_name} clip for track {track_index}...")
    
    result = safe_send_command(
        "create_clip",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": bars
        }
    )
    
    if result is None:
        print(f"   [ERROR] Failed to create clip")
        return None
    
    # Add notes to clip
    result = safe_send_command(
        "add_notes_to_clip",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        }
    )
    
    if result is None:
        print(f"   [ERROR] Failed to add notes")
        return None
    
    # Name the clip
    result = safe_send_command(
        "set_clip_name",
        {
            "track_index": track_index,
            "clip_index": clip_index,
            "name": f"{section_name} ({bars} bars"
        }
    )
    
    print(f"   [OK] Created clip with {len(notes)} notes")
    return True

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Create short reggae baseline track"""
    print("\n" + "=" * 80)
    print("REGGAE BASELINE - SHORT TEMPLATE")
    print("=" * 80)
    print(f"Tempo: {REGGAE_TEMPO} BPM")
    print(f"Duration: {SECTIONS[0]['bars'] + SECTIONS[1]['bars']} bars")
    print(f"Sections: {[s['name'] for s in SECTIONS]}")
    print("=" * 80)
    
    # Check server connection
    print("\n[1/7] Checking Ableton connection...")
    session_info = send_command("get_session_info")
    
    if session_info is None or not session_info.get("success", False):
        print("   [ERROR] Cannot connect to Ableton")
        print("   [TIP] Make sure Ableton Live is open and Remote Script is loaded")
        print("   [TIP] Run 'python MCP_Server/server.py' first if server is not running")
        return False
    
    print(f"   [OK] Found {session_info['result']['track_count']} tracks in session")
    
    # Create tracks
    if not create_tracks():
        print("\n[ERROR] Track creation failed")
        return False
    
    time.sleep(0.5)
    
    # Set tempo
    print(f"\n[2/7] Setting tempo to {REGGAE_TEMPO} BPM...")
    result = safe_send_command("set_tempo", {"tempo": REGGAE_TEMPO})
    
    if result is None or not result.get("success", False):
        print("   [WARN] Tempo might not have been set")
    else:
        print(f"   [OK] Tempo set to {REGGAE_TEMPO} BPM")
    
    time.sleep(0.5)
    
    # Create clips for each section
    for section_idx, section in enumerate(SECTIONS):
        section_name = section["name"]
        section_bars = section["bars"]
        start_bar = section_idx * section_bars
        
        print(f"\n[3/7] Processing section: {section_name} (bars {start_bar}-{start_bar + section_bars - 1})...")
        
        # Track 0: Kick
        print(f"[4/7]   Kick pattern...")
        if not create_clip(0, section_idx * 2, get_kick_pattern(start_bar), section_name):
            print("      [ERROR] Failed to create kick clip")
        
        # Track 1: Bass
        print(f"[4/7]   Bass pattern...")
        if not create_clip(1, section_idx * 2, get_bass_pattern(start_bar), section_name):
            print("      [ERROR] Failed to create bass clip")
        
        # Track 2: Hi-Hats
        print(f"[4/7]   Hi-hats pattern...")
        if not create_clip(2, section_idx * 2, get_hi_hat_pattern(start_bar), section_name):
            print("      [ERROR] Failed to create hi-hats clip")
        
        # Track 3: Clap
        print(f"[4/7]   Clap pattern...")
        if not create_clip(3, section_idx * 2, get_clap_pattern(start_bar), section_name):
            print("      [ERROR] Failed to create clap clip")
        
        # Track 4: Guitar Skank
        print(f"[4/7]   Guitar skank pattern...")
        if not create_clip(4, section_idx * 2, get_guitar_skank_pattern(start_bar), section_name):
            print("      [ERROR] Failed to create guitar clip")
        
        # Track 5: Keys
        print(f"[4/7]   Keys pattern...")
        if not create_clip(5, section_idx * 2, get_keys_pattern(start_bar), section_name):
            print("      [ERROR] Failed to create keys clip")
        
        # Track 6: FX (keep empty for dub effects)
        print(f"[4/7]   FX track (empty for effects)...")
        if not create_clip(6, section_idx * 2, [], section_name):
            print("      [ERROR] Failed to create FX clip")
        
        print(f"\n   [OK] Section {section_name} complete")
        time.sleep(0.2)
    
    # Summary
    print("\n" + "=" * 80)
    print("REGGAE BASELINE CREATION COMPLETE")
    print("=" * 80)
    print("\nTrack Structure:")
    for track_name, track_info in TRACKS.items():
        print(f"  - {track_name} (Track {track_info['index']})")
    print(f"\nSections:")
    for section in SECTIONS:
        print(f"  - {section['name']: {section['bars']} bars")
    print("\nCharacteristics:")
    print("  - Tempo: 70 BPM (slower than dub techno)")
    print("  - Rhythm: 4/4 patterns with offbeat accents")
    print("  - Bass: Emphasizes C2 octave")
    print("  - Duration: ~32 bars (short baseline)")
    print("  \nUsage: Fire clips in Ableton to playback")
    print("  \nNOTE: This is a baseline - add dub effects manually for authentic reggae sound")
    print("=" * 80)

if __name__ == "__main__":
    main()
