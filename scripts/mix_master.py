#!/usr/bin/env python3
"""
MIX MASTER - The Ultimate Mix Creation Controller

This is the central command center for all mix generation tools.
It provides a unified interface to:
- Create 10-minute mixes
- Create smart adaptive mixes
- Create genre-specific mixes
- Quick setup and capture
- Batch operations

Usage:
    python scripts/mix_master.py 10min           # Basic 10-minute mix
    python scripts/mix_master.py smart          # Smart adaptive mix
    python scripts/mix_master.py dub            # Dub genre mix
    python scripts/mix_master.py hiphop         # Hip-Hop genre mix
    python scripts/mix_master.py techno         # Techno genre mix
    python scripts/mix_master.py house          # House genre mix
    python scripts/mix_master.py dnb            # Drum & Bass genre mix
    python scripts/mix_master.py ambient        # Ambient genre mix
    python scripts/mix_master.py setup          # Quick setup only (no capture)
    python scripts/mix_master.py list           # List all options
    python scripts/mix_master.py help           # Show help
"""

import subprocess
import sys
import os


# Available mix types
MIX_TYPES = {
    "10min": {
        "script": "scripts/create_10min_mix_windows.py",
        "name": "10-Minute Mix",
        "description": "Basic 10-minute dub x fat beatz mix",
        "time": "~10 minutes"
    },
    "simple": {
        "script": "scripts/create_10min_mix_simple.py",
        "name": "Simple 10-Minute Mix",
        "description": "Simple version with direct commands",
        "time": "~10 minutes"
    },
    "smart": {
        "script": "scripts/create_smart_mix.py",
        "name": "Smart Adaptive Mix",
        "description": "Intelligently adapts to your Ableton setup",
        "time": "~2 seconds (setup only)"
    },
    "setup": {
        "script": "scripts/test_10min_setup.py",
        "name": "Quick Setup",
        "description": "Configures Ableton with locators (no capture)",
        "time": "~2 seconds"
    },
    "dub": {
        "script": "scripts/genre_mix_generator_fixed.py dub",
        "name": "Dub Mix",
        "description": "Classic dub with heavy echo and reverb",
        "time": "~2 seconds (setup only)"
    },
    "hiphop": {
        "script": "scripts/genre_mix_generator_fixed.py hiphop",
        "name": "Hip-Hop Mix",
        "description": "Old school hip-hop with punchy drums",
        "time": "~2 seconds (setup only)"
    },
    "techno": {
        "script": "scripts/genre_mix_generator_fixed.py techno",
        "name": "Techno Mix",
        "description": "Hard-hitting techno with pounding kicks",
        "time": "~2 seconds (setup only)"
    },
    "house": {
        "script": "scripts/genre_mix_generator_fixed.py house",
        "name": "House Mix",
        "description": "Groovy house with four-on-the-floor",
        "time": "~2 seconds (setup only)"
    },
    "dnb": {
        "script": "scripts/genre_mix_generator_fixed.py dnb",
        "name": "Drum & Bass Mix",
        "description": "High-energy DnB with breakbeats",
        "time": "~2 seconds (setup only)"
    },
    "ambient": {
        "script": "scripts/genre_mix_generator_fixed.py ambient",
        "name": "Ambient Mix",
        "description": "Ethereal ambient with slow evolution",
        "time": "~2 seconds (setup only)"
    }
}


GENRES = ["dub", "hiphop", "techno", "house", "dnb", "ambient"]


def print_header():
    """Print the header."""
    print("\n" + "=" * 70)
    print("                    MIX MASTER CONTROL")
    print("=" * 70)


def print_help():
    """Print help text."""
    print_header()
    print("\n[USAGE]")
    print("  python scripts/mix_master.py <mix_type>")
    print("\n[MIX TYPES]")
    
    # Group by category
    print("\n  --- Standard Mixes ---")
    for key in ["10min", "simple", "smart", "setup"]:
        info = MIX_TYPES[key]
        print(f"    {key:10s} - {info['name']:20s} ({info['time']})")
        print(f"                 {info['description']}")
    
    print("\n  --- Genre-Specific Mixes ---")
    for genre in GENRES:
        info = MIX_TYPES[genre]
        print(f"    {genre:10s} - {info['name']:20s} ({info['time']})")
        print(f"                 {info['description']}")
    
    print("\n  --- Commands ---")
    print("    list          - List all available mix types")
    print("    help          - Show this help text")
    print("\n" + "=" * 70)


def list_mix_types():
    """List all available mix types."""
    print_header()
    print("\n<AVAILABLE MIX TYPES>\n")
    
    for key, info in sorted(MIX_TYPES.items()):
        print(f"  {key:12s} | {info['name']:20s} | {info['time']}")
        print(f"                | {info['description']}")
        print()
    
    print("=" * 70)


def run_script(script_path: str):
    """Run a script and capture its output."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, script_path)
    
    print(f"\n[RUNNING] {script_path}")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, full_path],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute max timeout
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("\n[STDERR]", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Script timed out (max 5 minutes)")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to run script: {e}")
        return False


def main():
    """Main entry point."""
    # No arguments - show help
    if len(sys.argv) < 2:
        print_help()
        return None
    
    mix_type = sys.argv[1].lower()
    
    # Special commands
    if mix_type == "help":
        print_help()
        return None
    
    if mix_type == "list":
        list_mix_types()
        return None
    
    # Check if valid mix type
    if mix_type not in MIX_TYPES:
        print(f"\n[ERROR] Unknown mix type: {mix_type}")
        print(f"\n[HINT] Type 'list' to see all available mix types")
        print(f"       Type 'help' for more information")
        return None
    
    # Run the script
    print_header()
    info = MIX_TYPES[mix_type]
    print(f"\n[SELECTED] {info['name']}")
    print(f"[DESCRIPTION] {info['description']}")
    print(f"[ESTIMATED TIME] {info['time']}")
    
    # For capture scripts, show warning
    if mix_type in ["10min", "simple"]:
        print("\n[WARNING] This will capture for the full mix duration!")
        print("          Make sure Ableton is ready to record.")
        print("          Press Ctrl+C to abort if needed.")
        
        import time
        print("\nStarting in 3 seconds... (press Ctrl+C to abort)")
        time.sleep(3)
    
    success = run_script(info["script"])
    
    if success:
        print("\n" + "=" * 70)
        print("SUCCESS! Your mix has been created.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("ERROR: Mix creation failed or was interrupted.")
        print("=" * 70)
    
    return success


if __name__ == "__main__":
    main()
