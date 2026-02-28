#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-Hour Reggae Dub Live Automation
==================================

DJ-style live automation with timer-based section progression.

Features:
- 30 sections over 120 minutes (4 minutes per section)
- Progressive drum patterns: One Drop -> Rockers -> Steppers
- Filter automation on synth tracks
- Volume changes per section
- Progress tracking with visual bar
- Graceful Ctrl+C stopping
- --test-mode for accelerated QA

Usage:
    python automate_2h_dub_reggae.py              # Full 2-hour run
    python automate_2h_dub_reggae.py --test-mode  # 30-second test
    python automate_2h_dub_reggae.py --dry-run    # Print only, no commands

Requires: Ableton Live with session loaded via create_2h_dub_reggae.py
"""

import socket
import json
import time
import sys
import signal
import argparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# =============================================================================
# CONFIGURATION
# =============================================================================

TCP_HOST = "localhost"
TCP_PORT = 9877
UDP_HOST = "localhost"
UDP_PORT = 9878

# Tempo
TEMPO = 72  # BPM

# Timing (in seconds)
SECTION_DURATION_FULL = 4 * 60  # 4 minutes per section
SECTION_DURATION_TEST = 1  # 1 second per section in test mode
BAR_DURATION = 60 / TEMPO * 4  # ~3.33 seconds per bar at 72 BPM

# Track indices
TRACKS = {
    "DRUMS": 0,
    "DUB_BASS": 1,
    "GUITAR_CHOP": 2,
    "ORGAN_BUBBLE": 3,
    "SYNTH_PAD": 4,
    "FX": 5,
    "REVERB_SEND": 6,
    "DELAY_SEND": 7,
}

# Parameter indices (typical for dub devices - adjust as needed)
PARAMS = {
    "FILTER_CUTOFF": 2,  # LP Freq
    "REVERB": 8,
    "DELAY": 6,
}

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class Section:
    """Represents a performance section"""

    name: str
    index: int
    drum_pattern: str  # one_drop, rockers, steppers
    energy: str  # minimal, building, peak, breakdown
    description: str
    duration_minutes: float = 4.0


@dataclass
class ClipChange:
    """Represents a single clip change"""

    track: int
    clip: int
    track_name: str
    clip_name: str


# =============================================================================
# SECTION DEFINITIONS (30 sections, 4 min each = 2 hours)
# =============================================================================

# Drum pattern distribution:
# - Sections 0-9: One Drop (minimal, space)
# - Sections 10-19: Rockers (building energy)
# - Sections 20-29: Steppers/Mix (peak energy, variation)

SECTIONS = [
    # Phase 1: One Drop (0-9) - Introduction, minimal drums
    Section(
        "01_Roots_Intro", 0, "one_drop", "minimal", "Establish groove, deep roots feel"
    ),
    Section("02_Deep_Groove", 1, "one_drop", "minimal", "Settle into the pocket"),
    Section("03_Bass_Foundation", 2, "one_drop", "minimal", "Bass comes forward"),
    Section("04_Space_Dub", 3, "one_drop", "minimal", "Wide space, sparse elements"),
    Section("05_Slow_Build", 4, "one_drop", "building", "Energy begins to rise"),
    Section("06_Meditation", 5, "one_drop", "minimal", "Hypnotic repetition"),
    Section("07_First_Layer", 6, "one_drop", "building", "Add texture layers"),
    Section("08_Echo_Chamber", 7, "one_drop", "minimal", "Heavy delay exploration"),
    Section("09_Pre_Transition", 8, "one_drop", "building", "Prepare for change"),
    Section("10_Crossroads", 9, "one_drop", "building", "Bridge to rockers feel"),
    # Phase 2: Rockers (10-19) - Building energy
    Section("11_Rockers_Entry", 10, "rockers", "building", "Rockers pattern enters"),
    Section("12_Steady_Pulse", 11, "rockers", "building", "Consistent driving pulse"),
    Section("13_Bass_Walks", 12, "rockers", "building", "Walking bass lines"),
    Section("14_Organ_Shuffle", 13, "rockers", "building", "Organ bubble prominent"),
    Section("15_First_Peak", 14, "rockers", "peak", "First energy peak"),
    Section("16_Guitar_Melody", 15, "rockers", "building", "Guitar chop melody"),
    Section("17_Full_Band", 16, "rockers", "peak", "All elements active"),
    Section("18_Breakdown_One", 17, "rockers", "breakdown", "Strip back, create space"),
    Section("19_Return", 18, "rockers", "building", "Energy returns"),
    Section("20_Pre_Steppers", 19, "rockers", "building", "Build toward steppers"),
    # Phase 3: Steppers/Mix (20-29) - Peak energy
    Section("21_Steppers_Entry", 20, "steppers", "peak", "Steppers pattern kicks in"),
    Section("22_Four_On_Floor", 21, "steppers", "peak", "Driving four-on-floor"),
    Section("23_Dance_Floor", 22, "steppers", "peak", "Maximum dance energy"),
    Section("24_Synth_Rise", 23, "steppers", "peak", "Synth pad swells"),
    Section("25_Climax", 24, "steppers", "peak", "Emotional peak moment"),
    Section("26_Breakdown_Two", 25, "steppers", "breakdown", "Second breakdown"),
    Section("27_Final_Rise", 26, "steppers", "peak", "Final energy push"),
    Section("28_CELEBRATION", 27, "steppers", "peak", "Joyful climax"),
    Section("29_Wind_Down", 28, "steppers", "fading", "Begin fade out"),
    Section("30_Outro", 29, "one_drop", "fading", "Return to roots, fade to silence"),
]

# =============================================================================
# CLIP CHANGES PER SECTION
# Following DJ rule: ONE CLIP CHANGE AT A TIME
# =============================================================================

CLIP_CHANGES = {
    "01_Roots_Intro": [
        ClipChange(0, 0, "DRUMS", "One_Drop_Basic"),
        ClipChange(1, 0, "DUB_BASS", "Bass_Drone_C"),
    ],
    "02_Deep_Groove": [
        ClipChange(2, 0, "GUITAR_CHOP", "Chop_Offbeat_Cm"),
    ],
    "03_Bass_Foundation": [
        ClipChange(1, 1, "DUB_BASS", "Bass_Walking_Cm"),
    ],
    "04_Space_Dub": [
        ClipChange(3, 0, "ORGAN_BUBBLE", "Organ_Shuffle"),
    ],
    "05_Slow_Build": [
        ClipChange(4, 0, "SYNTH_PAD", "Pad_Warm_Cm"),
    ],
    "06_Meditation": [
        ClipChange(0, 1, "DRUMS", "One_Drop_Heavy"),
    ],
    "07_First_Layer": [
        ClipChange(5, 0, "FX", "FX_Sub_Hit"),
    ],
    "08_Echo_Chamber": [
        ClipChange(2, 1, "GUITAR_CHOP", "Chop_Muted"),
    ],
    "09_Pre_Transition": [
        ClipChange(1, 2, "DUB_BASS", "Bass_Syncopated"),
    ],
    "10_Crossroads": [
        ClipChange(0, 2, "DRUMS", "One_Drop_Light"),
        ClipChange(3, 1, "ORGAN_BUBBLE", "Organ_Stab"),
    ],
    "11_Rockers_Entry": [
        ClipChange(0, 3, "DRUMS", "Rockers_Basic"),
    ],
    "12_Steady_Pulse": [
        ClipChange(1, 3, "DUB_BASS", "Bass_Pulse_Cm"),
    ],
    "13_Bass_Walks": [
        ClipChange(2, 2, "GUITAR_CHOP", "Chop_Melody"),
    ],
    "14_Organ_Shuffle": [
        ClipChange(3, 2, "ORGAN_BUBBLE", "Organ_Bubble"),
    ],
    "15_First_Peak": [
        ClipChange(4, 1, "SYNTH_PAD", "Pad_Swell_Cm"),
        ClipChange(0, 4, "DRUMS", "Rockers_Full"),
    ],
    "16_Guitar_Melody": [
        ClipChange(2, 3, "GUITAR_CHOP", "Chop_Rhythm"),
    ],
    "17_Full_Band": [
        ClipChange(1, 4, "DUB_BASS", "Bass_Full_Gm"),
    ],
    "18_Breakdown_One": [
        ClipChange(0, 5, "DRUMS", "Rockers_Light"),
        ClipChange(4, 2, "SYNTH_PAD", "Pad_Drone"),
    ],
    "19_Return": [
        ClipChange(0, 4, "DRUMS", "Rockers_Full"),
    ],
    "20_Pre_Steppers": [
        ClipChange(1, 5, "DUB_BASS", "Bass_Building"),
        ClipChange(5, 1, "FX", "FX_Rise"),
    ],
    "21_Steppers_Entry": [
        ClipChange(0, 6, "DRUMS", "Steppers_Basic"),
    ],
    "22_Four_On_Floor": [
        ClipChange(1, 6, "DUB_BASS", "Bass_Driving_Gm"),
    ],
    "23_Dance_Floor": [
        ClipChange(2, 4, "GUITAR_CHOP", "Chop_Energy"),
        ClipChange(3, 3, "ORGAN_BUBBLE", "Organ_Pad"),
    ],
    "24_Synth_Rise": [
        ClipChange(4, 3, "SYNTH_PAD", "Pad_Rise_Gm"),
    ],
    "25_Climax": [
        ClipChange(0, 7, "DRUMS", "Steppers_Full"),
        ClipChange(5, 2, "FX", "FX_Crash"),
    ],
    "26_Breakdown_Two": [
        ClipChange(0, 8, "DRUMS", "Steppers_Light"),
        ClipChange(1, 7, "DUB_BASS", "Bass_Minimal"),
    ],
    "27_Final_Rise": [
        ClipChange(0, 7, "DRUMS", "Steppers_Full"),
        ClipChange(4, 4, "SYNTH_PAD", "Pad_Peak_Gm"),
    ],
    "28_CELEBRATION": [
        ClipChange(1, 8, "DUB_BASS", "Bass_Joy_C"),
        ClipChange(2, 5, "GUITAR_CHOP", "Chop_Celebration"),
    ],
    "29_Wind_Down": [
        ClipChange(0, 6, "DRUMS", "Steppers_Basic"),
        ClipChange(3, 4, "ORGAN_BUBBLE", "Organ_Fade"),
    ],
    "30_Outro": [
        ClipChange(0, 0, "DRUMS", "One_Drop_Basic"),
        ClipChange(1, 0, "DUB_BASS", "Bass_Drone_C"),
        ClipChange(4, 5, "SYNTH_PAD", "Pad_Fade"),
    ],
}

# =============================================================================
# VOLUME TARGETS PER ENERGY LEVEL
# =============================================================================

VOLUME_TARGETS = {
    "minimal": {
        "DRUMS": 0.60,
        "DUB_BASS": 0.70,
        "GUITAR_CHOP": 0.50,
        "ORGAN_BUBBLE": 0.45,
        "SYNTH_PAD": 0.40,
        "FX": 0.35,
    },
    "building": {
        "DRUMS": 0.70,
        "DUB_BASS": 0.78,
        "GUITAR_CHOP": 0.60,
        "ORGAN_BUBBLE": 0.55,
        "SYNTH_PAD": 0.50,
        "FX": 0.45,
    },
    "peak": {
        "DRUMS": 0.80,
        "DUB_BASS": 0.88,
        "GUITAR_CHOP": 0.70,
        "ORGAN_BUBBLE": 0.65,
        "SYNTH_PAD": 0.60,
        "FX": 0.55,
    },
    "breakdown": {
        "DRUMS": 0.50,
        "DUB_BASS": 0.60,
        "GUITAR_CHOP": 0.40,
        "ORGAN_BUBBLE": 0.35,
        "SYNTH_PAD": 0.45,
        "FX": 0.30,
    },
    "fading": {
        "DRUMS": 0.55,
        "DUB_BASS": 0.65,
        "GUITAR_CHOP": 0.45,
        "ORGAN_BUBBLE": 0.40,
        "SYNTH_PAD": 0.35,
        "FX": 0.30,
    },
}

# =============================================================================
# NETWORK COMMUNICATION
# =============================================================================


def send_tcp(command_type: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Send command via TCP and wait for response"""
    if params is None:
        params = {}

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((TCP_HOST, TCP_PORT))

        command = {"type": command_type, "params": params}
        sock.send(json.dumps(command).encode("utf-8"))

        response = json.loads(sock.recv(8192).decode("utf-8"))
        sock.close()
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}


def send_udp(command_type: str, params: Dict) -> bool:
    """Send command via UDP (fire-and-forget for real-time control)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        command = {"type": command_type, "params": params}
        sock.sendto(json.dumps(command).encode("utf-8"), (UDP_HOST, UDP_PORT))
        sock.close()
        return True
    except Exception as e:
        print(f"  [UDP ERROR] {e}")
        return False


# =============================================================================
# PARAMETER AUTOMATION
# =============================================================================


def sweep_parameter(
    track: int,
    device: int,
    param: int,
    start: float,
    end: float,
    steps: int = 16,
    delay_ms: int = 100,
    dry_run: bool = False,
) -> None:
    """Smoothly sweep a parameter from start to end value."""
    if dry_run:
        print(
            f"    [DRY RUN] Sweep track {track} param {param}: {start:.2f} -> {end:.2f}"
        )
        return

    step_size = (end - start) / steps
    for i in range(steps + 1):
        value = start + (step_size * i)
        send_udp(
            "set_device_parameter",
            {
                "track_index": track,
                "device_index": device,
                "parameter_index": param,
                "value": value,
            },
        )
        time.sleep(delay_ms / 1000)


def set_track_volume(track: int, volume: float, dry_run: bool = False) -> None:
    """Set track volume (normalized 0.0-1.0)"""
    if dry_run:
        print(f"    [DRY RUN] Set track {track} volume: {volume:.2f}")
        return
    send_udp("set_track_volume", {"track_index": track, "volume": volume})


# =============================================================================
# PERFORMANCE FUNCTIONS
# =============================================================================


def fire_clip(track: int, clip: int, dry_run: bool = False) -> bool:
    """Fire a single clip"""
    if dry_run:
        print(f"    [DRY RUN] Fire clip: track {track}, clip {clip}")
        return True

    result = send_tcp("fire_clip", {"track_index": track, "clip_index": clip})
    return result.get("status") == "success"


def start_playback(dry_run: bool = False) -> bool:
    """Start session playback"""
    if dry_run:
        print("  [DRY RUN] Start playback")
        return True

    result = send_tcp("start_playback")
    return result.get("status") == "success"


def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def progress_bar(percent: float, width: int = 40) -> str:
    """Generate progress bar"""
    filled = int(width * percent)
    empty = width - filled
    return f"[{'=' * filled}{'-' * empty}] {percent * 100:.1f}%"


# =============================================================================
# MAIN AUTOMATION
# =============================================================================


class ReggaeDubAutomation:
    """Main automation controller"""

    def __init__(self, test_mode: bool = False, dry_run: bool = False):
        self.running = True
        self.start_time = 0
        self.current_section_idx = 0
        self.test_mode = test_mode
        self.dry_run = dry_run
        self.section_duration = (
            SECTION_DURATION_TEST if test_mode else SECTION_DURATION_FULL
        )

        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n[STOP] Gracefully stopping automation...")
        self.running = False

    def print_header(self):
        """Print automation header"""
        print("=" * 70)
        print("  2-HOUR REGGAE DUB LIVE AUTOMATION")
        print("  72 BPM | C Minor | 30 Sections | DJ Style")
        print("=" * 70)
        print()

        if self.test_mode:
            print("  [TEST MODE] Accelerated timing (1 second per section)")
        if self.dry_run:
            print("  [DRY RUN] No commands sent to Ableton")

        print()
        print(f"  Total Duration: {'~30 seconds' if self.test_mode else '120 minutes'}")
        print(
            f"  Section Interval: {self.section_duration} {'second' if self.test_mode else 'seconds'}"
        )
        print(f"  Tempo: {TEMPO} BPM")
        print()
        print("  DRUM PATTERN DISTRIBUTION:")
        print("  * Sections 0-9:   One Drop (minimal, space)")
        print("  * Sections 10-19: Rockers (building energy)")
        print("  * Sections 20-29: Steppers (peak energy)")
        print()
        print("  DJ PERFORMANCE RULES:")
        print("  * ONE CLIP CHANGE AT A TIME")
        print("  * Let the groove breathe")
        print("  * Bass is the foundation")
        print()
        print("=" * 70)
        print()

    def apply_section_volumes(self, section: Section) -> None:
        """Apply energy-specific volumes at section start"""
        targets = VOLUME_TARGETS.get(section.energy, VOLUME_TARGETS["minimal"])

        print(f"\n  [VOLUMES] Energy: {section.energy.upper()}")
        for track_name, volume in targets.items():
            track_idx = TRACKS[track_name]
            set_track_volume(track_idx, volume, self.dry_run)
            print(f"    {track_name}: {volume:.2f}")

    def run_section(self, section: Section) -> None:
        """Run a single section with clip changes and automation"""
        section_start = time.time()
        changes = CLIP_CHANGES.get(section.name, [])

        print(f"\n{'=' * 70}")
        print(f"  SECTION {section.index + 1}/30: {section.name}")
        print(f"  Drum Pattern: {section.drum_pattern.upper()}")
        print(f"  Energy: {section.energy.upper()}")
        print(f"  Description: {section.description}")
        print(f"  Duration: {self.section_duration}s")
        print(f"  Clip Changes: {len(changes)}")
        print(f"{'=' * 70}\n")

        # Apply section-specific volumes
        self.apply_section_volumes(section)

        # Process clip changes
        for i, change in enumerate(changes):
            if not self.running:
                break

            # Calculate progress
            elapsed = time.time() - self.start_time
            total_duration = len(SECTIONS) * self.section_duration
            total_progress = elapsed / total_duration if total_duration > 0 else 0

            print(f"\n  {progress_bar(min(1.0, total_progress))}")
            print(f"  Time: {format_time(elapsed)} / {format_time(total_duration)}")
            print()

            # Fire the clip
            print(f"  [CLIP CHANGE {i + 1}/{len(changes)}]")
            print(f"    Track: {change.track_name} ({change.track})")
            print(f"    Clip: {change.clip_name} ({change.clip})")

            if fire_clip(change.track, change.clip, self.dry_run):
                print(f"    Status: FIRED")
            else:
                print(f"    Status: ERROR")

            # Wait between changes (proportional to section duration)
            if i < len(changes) - 1:
                wait_time = self.section_duration / (len(changes) + 1)
                print(f"\n  Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)

        # Wait for section end
        section_elapsed = time.time() - section_start
        remaining = self.section_duration - section_elapsed
        if remaining > 0:
            print(f"\n  Waiting {remaining:.1f}s until next section...")
            time.sleep(remaining)

    def run(self):
        """Main automation loop"""
        self.print_header()

        print("[1/2] Starting playback...")
        if not start_playback(self.dry_run):
            print("[ERROR] Could not start playback")
            return
        print("[OK] Playback started\n")

        # Fire initial clips
        print("[2/2] Firing initial clips...")
        initial_clips = [
            (TRACKS["DRUMS"], 0, "One_Drop_Basic"),
            (TRACKS["DUB_BASS"], 0, "Bass_Drone_C"),
        ]
        for track, clip, name in initial_clips:
            if fire_clip(track, clip, self.dry_run):
                print(f"  [OK] {name}")
            time.sleep(0.3)
        print()

        self.start_time = time.time()

        # Run each section
        for section in SECTIONS:
            if not self.running:
                break
            self.run_section(section)
            self.current_section_idx += 1

        # Final summary
        total_time = time.time() - self.start_time
        print("\n" + "=" * 70)
        print("  AUTOMATION COMPLETE")
        print("=" * 70)
        print(f"  Total Duration: {format_time(total_time)}")
        print(f"  Sections Completed: {self.current_section_idx}/30")
        print("=" * 70)


# =============================================================================
# ENTRY POINT
# =============================================================================


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="2-hour reggae dub automation")
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run accelerated test (1 second per section)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without sending commands"
    )
    args = parser.parse_args()

    automation = ReggaeDubAutomation(test_mode=args.test_mode, dry_run=args.dry_run)
    automation.run()


if __name__ == "__main__":
    main()
