#!/usr/bin/env python3
"""
Continuous Dub Mix Orchestrator
Automatically creates and plays dub mixes continuously
"""
import time
import json
import urllib.request

SERVER_URL = "http://localhost:8080"

def send_command(cmd):
    """Send command to Ableton MCP server"""
    try:
        data = json.dumps(cmd).encode('utf-8')
        req = urllib.request.Request(
            SERVER_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Command failed: {e}")
        return None

def check_connection():
    """Verify Ableton connection"""
    result = send_command({"command": "get_session_overview"})
    if result and "tracks" in result:
        print("✓ Ableton connection established")
        return True
    return False

def build_dub_mix():
    """Initialize dub mix structure"""
    print("\n[1/6] Setting dub tempo")
    send_command({"command": "set_tempo", "args": [123.0]})
    
    print("[2/6] Creating dub tracks")
    send_command({"command": "create_audio_track", "args": [-1]})
    send_command({"command": "create_midi_track", "args": [-1]})
    send_command({"command": "create_midi_track", "args": [-1]})
    send_command({"command": "create_midi_track", "args": [-1]})
    
    print("[3/6] Configuring dub instruments")
    send_command({"command": "load_drum_kit", "args": [6, "Drums/Drum Rack", "drums/acoustic/kit1"]})
    
    print("[4/6] Creating dub drum pattern")
    send_command({"command": "create_drum_pattern", "args": [6, 0, "one_drop", 4.0]})
    send_command({"command": "create_drum_pattern", "args": [6, 1, "dub_techno", 8.0]})
    
    print("[5/6] Creating dub bassline")
    send_command({"command": "create_clip", "args": [5, 0, 4.0]})
    
    print("[6/6] Starting dub playback")
    send_command({"command": "start_playback"})
    send_command({"command": "fire_clip", "args": [6, 0]})
    
    print("\n✅ Dub mix infrastructure ready!")

def trigger_scene_sequence():
    """Trigger scenes in sequence for continuous dub flow"""
    scenes = [0, 1, 2, 3, 4, 5, 6, 7]
    for i, scene_idx in enumerate(scenes):
        try:
            print(f"  > Triggering Scene {scene_idx}")
            send_command({"command": "trigger_scene", "args": [scene_idx]})
        except Exception as e:
            print(f"  Scene {scene_idx} failed: {e}")
        time.sleep(4.0)  # Wait 4 beats between scenes

def create_infinite_filter_sweep():
    """Continuous filter sweep automation for dub atmosphere"""
    for cycle in range(10):
        print(f"[Sweep cycle {cycle}] Applying filter modulation")
        send_command({"command": "apply_filter_buildup", "args": [[0, 1, 9, 0, 0, 32, 16]})
        time.sleep(32.0)  # 8 bar sweep

def continuous_dub_mode():
    """Run infinite dub mixing loop"""
    print("\n🎛️ STARTING CONTINUOUS DUB MIX MODE 🎛️")
    print("=" * 60)
    
    iterations = 0
    while True:
        iterations += 1
        print(f"\n[🔄 Dub Loop {iterations} - {time.strftime('%H:%M:%S')}]")
        
        # Check connection
        if not check_connection():
            print("⚠ Re-establishing connection...")
            time.sleep(5)
            continue
        
        # Trigger scene transitions
        print("  → Triggering scene sequence...")
        trigger_scene_sequence()
        
        # Apply dub effects
        print("  → Applying filter sweeps...")
        create_infinite_filter_sweep()
        
        # Continue looping
        time.sleep(60)  # Wait 1 minute before next iteration

if __name__ == "__main__":
    # First, build the dub mix structure
    if not check_connection():
        print("Initializing dub mix infrastructure...")
        build_dub_mix()
    
    # Then go into continuous operation
    try:
        continuous_dub_mode()
    except KeyboardInterrupt:
        print("\n\n🛑 Dub mix stopped by user")
    except Exception as e:
        print(f"\n\n❌ Dub mix error: {e}")
