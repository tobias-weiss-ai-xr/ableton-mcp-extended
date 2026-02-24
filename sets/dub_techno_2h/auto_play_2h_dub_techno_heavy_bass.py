#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2-Hour Dub Techno Live Automation - Heavy Bass Edition
=======================================================

DJ-style live automation following the golden rule:
**ONE CLIP CHANGE AT A TIME**

Features:
- 8 sections over 120 minutes
- Gradual parameter sweeps
- Energy management (builds, drops, breakdowns)
- Heavy bass focus (Track 1)
- Real-time UDP parameter updates for smooth sweeps

Usage:
    python auto_play_2h_dub_techno_heavy_bass.py

Requires: Ableton Live with session loaded via create_2h_dub_techno_heavy_bass_fixed.py
"""

import socket
import json
import time
import sys
import signal
import random
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

# Timing (in seconds)
SECTION_DURATION = 15 * 60  # 15 minutes per section (8 sections = 2 hours)
BAR_DURATION = 60 / 114 * 4  # ~2.1 seconds per bar at 114 BPM
CHANGE_INTERVAL = 32 * BAR_DURATION  # ~67 seconds between clip changes (8 bars)

# Track indices
TRACKS = {
    "KICK": 0,
    "SUB_BASS": 1,
    "HATS": 2,
    "PERCS": 3,
    "ATMO_PAD": 4,
    "DUB_FX": 5,
    "LEAD_PAD": 6,
    "CHORD_STABS": 7,
}

# Parameter indices (typical for dub techno devices)
# These may need adjustment based on actual devices loaded
PARAMS = {
    "FILTER_CUTOFF": 2,  # LP Freq
    "REVERB": 8,  # Reverb amount
    "DELAY": 6,  # Delay amount
    "DRIVE": 3,  # Overdrive
}

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class Section:
    """Represents a performance section"""

    name: str
    energy: str  # minimal, building, peak, breakdown, fading
    description: str
    duration_minutes: float = 15.0


@dataclass
class ClipChange:
    """Represents a single clip change"""

    track: int
    clip: int
    track_name: str
    clip_name: str


# =============================================================================
# SECTION DEFINITIONS (8 sections, 15 min each = 2 hours)
# =============================================================================

SECTIONS = [
    Section("01_Intro", "minimal", "Establish groove, dark atmosphere"),
    Section("02_Hypnotic", "minimal", "Deep groove, subtle evolution"),
    Section("03_First_Build", "building", "Energy rises, layers added"),
    Section("04_Breakdown", "breakdown", "Space, atmosphere, remove elements"),
    Section("05_Second_Build", "building", "Energy returns, heavier bass"),
    Section("06_Journey", "peak", "Sustained groove, maximum depth"),
    Section("07_Final_Push", "peak", "Peak energy, complex layers"),
    Section("08_Wind_Down", "fading", "Strip back, fade to silence"),
]

# =============================================================================
# CLIPO CHANGES PER SECTION
# Following DJ rule: ONE CLIP CHANGE AT A TIME
# =============================================================================

CLIP_CHANGES = {
    "01_Intro": [
        ClipChange(0, 0, "KICK", "Kick_Fund"),
        # Wait 8 bars
        ClipChange(1, 0, "SUB_BASS", "Sub_F_Drone"),
        # Wait 8 bars
        ClipChange(4, 0, "ATMO_PAD", "Pad_Fm_Sustain"),
        # Wait 8 bars
        ClipChange(2, 0, "HATS", "Hats_Minimal"),
    ],
    "02_Hypnotic": [
        ClipChange(3, 0, "PERCS", "Percs_Rim"),
        ClipChange(0, 2, "KICK", "Kick_Deep"),
        ClipChange(1, 2, "SUB_BASS", "Sub_F_Pluck"),
        ClipChange(6, 0, "LEAD_PAD", "Lead_Melody_F"),
    ],
    "03_First_Build": [
        ClipChange(2, 2, "HATS", "Hats_Syncopated"),
        ClipChange(4, 3, "ATMO_PAD", "Pad_Fm_Movement"),
        ClipChange(1, 3, "SUB_BASS", "Sub_Chord_Stab"),
        ClipChange(7, 0, "CHORD_STABS", "Chord_Fm"),
    ],
    "04_Breakdown": [
        ClipChange(0, 3, "KICK", "Kick_Sparse"),
        ClipChange(2, 1, "HATS", "Hats_Sparse"),
        ClipChange(3, 4, "PERCS", "Percs_None"),
        ClipChange(4, 4, "ATMO_PAD", "Pad_Drones"),
    ],
    "05_Second_Build": [
        ClipChange(0, 4, "KICK", "Kick_Push"),
        ClipChange(1, 4, "SUB_BASS", "Sub_Octave_Bounce"),
        ClipChange(2, 4, "HATS", "Hats_Fast"),
        ClipChange(6, 4, "LEAD_PAD", "Lead_Arpeggio_F"),
    ],
    "06_Journey": [
        ClipChange(0, 5, "KICK", "Kick_Steady"),
        ClipChange(1, 5, "SUB_BASS", "Sub_Cinematic"),
        ClipChange(4, 6, "ATMO_PAD", "Pad_Dub_Wash"),
        ClipChange(3, 3, "PERCS", "Percs_Layered"),
    ],
    "07_Final_Push": [
        ClipChange(0, 1, "KICK", "Kick_Punchy"),
        ClipChange(1, 1, "SUB_BASS", "Sub_C_Drone"),
        ClipChange(2, 3, "HATS", "Hats_6_8"),
        ClipChange(4, 7, "ATMO_PAD", "Pad_Peak"),
        ClipChange(6, 3, "LEAD_PAD", "Lead_Melody_Improved"),
    ],
    "08_Wind_Down": [
        ClipChange(2, 5, "HATS", "Hats_Muted"),
        ClipChange(3, 4, "PERCS", "Percs_None"),
        ClipChange(0, 6, "KICK", "Kick_Swung"),
        ClipChange(1, 6, "SUB_BASS", "Sub_Tremolo"),
        ClipChange(4, 5, "ATMO_PAD", "Pad_None"),
    ],
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
) -> None:
    """
    Smoothly sweep a parameter from start to end value.
    Uses UDP for real-time updates.
    """
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


def apply_filter_buildup(
    tracks: List[int],
    device: int = 0,
    start: float = 0.3,
    end: float = 0.9,
    duration_beats: int = 16,
) -> None:
    """Apply filter sweep buildup on multiple tracks"""
    steps = 16
    delay = (duration_beats * BAR_DURATION) / steps

    print(f"  [FILTER BUILDUP] Tracks {tracks}: {start:.1f} -> {end:.1f}")
    sweep_parameter(
        tracks[0], device, PARAMS["FILTER_CUTOFF"], start, end, steps, int(delay * 1000)
    )


def apply_drop(
    tracks: List[int],
    device: int = 0,
    drop_value: float = 0.2,
    return_value: float = 0.8,
    drop_beats: int = 1,
    return_beats: int = 8,
) -> None:
    """Apply instant drop then gradual return (classic dub technique)"""
    # Instant drop on all tracks
    for track in tracks:
        send_udp(
            "set_device_parameter",
            {
                "track_index": track,
                "device_index": device,
                "parameter_index": PARAMS["FILTER_CUTOFF"],
                "value": drop_value,
            },
        )

    print(f"  [DROP] Filter dropped to {drop_value:.1f}")

    # Wait, then gradual return
    time.sleep(drop_beats * BAR_DURATION)

    # Return sweep
    for track in tracks:
        sweep_parameter(
            track,
            device,
            PARAMS["FILTER_CUTOFF"],
            drop_value,
            return_value,
            steps=8,
            delay_ms=100,
        )


def set_track_volume(track: int, volume: float) -> None:
    """Set track volume (normalized 0.0-1.0)"""
    send_udp("set_track_volume", {"track_index": track, "volume": volume})


# =============================================================================
# PERFORMANCE FUNCTIONS
# =============================================================================


def fire_clip(track: int, clip: int) -> bool:
    """Fire a single clip"""
    result = send_tcp("fire_clip", {"track_index": track, "clip_index": clip})
    return result.get("status") == "success"


def start_playback() -> bool:
    """Start session playback"""
    result = send_tcp("start_playback")
    return result.get("status") == "success"


def get_playhead() -> Dict:
    """Get current playhead position"""
    result = send_tcp("get_playhead_position")
    if result.get("status") == "success":
        return result.get("result", {})
    return {}


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


class DubTechnoAutomation:
    """Main automation controller"""

    def __init__(self):
        self.running = True
        self.start_time = 0
        self.current_section_idx = 0
        self.clip_change_idx = 0

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
        print("  2-HOUR DUB TECHNO LIVE AUTOMATION")
        print("  Heavy Bass Edition | DJ Style | One Change At A Time")
        print("=" * 70)
        print()
        print(f"  Total Duration: 120 minutes (8 sections x 15 min)")
        print(f"  Section Interval: {SECTION_DURATION / 60:.0f} minutes")
        print(f"  Clip Change Interval: ~{CHANGE_INTERVAL:.0f} seconds")
        print(f"  Tempo: 114 BPM")
        print()
        print("  DJ PERFORMANCE RULES:")
        print("  * ONE CLIP CHANGE AT A TIME")
        print("  * Wait 8 bars between changes")
        print("  * Gradual parameter sweeps")
        print("  * Heavy bass focus")
        print()
        print("=" * 70)
        print()

    def run_section(self, section: Section) -> None:
        """Run a single section with clip changes and automation"""
        section_start = time.time()
        changes = CLIP_CHANGES.get(section.name, [])

        print(f"\n{'=' * 70}")
        print(f"  SECTION: {section.name}")
        print(f"  Energy: {section.energy.upper()}")
        print(f"  Description: {section.description}")
        print(f"  Duration: {section.duration_minutes:.0f} minutes")
        print(f"  Clip Changes: {len(changes)}")
        print(f"{'=' * 70}\n")

        # Apply section-specific automation
        self._apply_section_automation(section)

        # Process clip changes with DJ timing
        for i, change in enumerate(changes):
            if not self.running:
                break

            # Calculate progress
            elapsed = time.time() - section_start
            remaining = section.duration_minutes * 60 - elapsed

            # Print status
            total_elapsed = time.time() - self.start_time
            total_progress = total_elapsed / (120 * 60)

            print(f"\n  {progress_bar(total_progress)}")
            print(f"  Time: {format_time(total_elapsed)} / 02:00:00")
            print(f"  Remaining: {format_time(remaining)}")
            print()

            # Fire the clip
            print(f"  [CLIP CHANGE {i + 1}/{len(changes)}]")
            print(f"    Track: {change.track_name} ({change.track})")
            print(f"    Clip: {change.clip_name} ({change.clip})")

            if fire_clip(change.track, change.clip):
                print(f"    Status: FIRED")
            else:
                print(f"    Status: ERROR")

            # Wait between changes (DJ rule: let it breathe)
            if i < len(changes) - 1:
                wait_time = CHANGE_INTERVAL
                print(
                    f"\n  Waiting {wait_time:.0f}s ({wait_time / BAR_DURATION:.0f} bars)..."
                )

                # Small parameter automation during wait
                self._ambient_automation(section.energy, wait_time)
            else:
                # Last change in section - wait for section end
                remaining_section = (section.duration_minutes * 60) - (
                    time.time() - section_start
                )
                if remaining_section > 0:
                    print(f"\n  Waiting {remaining_section:.0f}s until next section...")
                    self._ambient_automation(section.energy, remaining_section)

    def _apply_section_automation(self, section: Section) -> None:
        """Apply energy-specific automation at section start"""
        energy = section.energy

        if energy == "minimal":
            # Low energy: subtle reverb, low filter
            set_track_volume(TRACKS["SUB_BASS"], 0.75)
            set_track_volume(TRACKS["ATMO_PAD"], 0.50)
            print("  [AUTOMATION] Minimal energy: bass 0.75, pad 0.50")

        elif energy == "building":
            # Rising energy: gradual filter open
            set_track_volume(TRACKS["SUB_BASS"], 0.82)
            set_track_volume(TRACKS["LEAD_PAD"], 0.65)
            print("  [AUTOMATION] Building energy: bass 0.82, lead 0.65")

        elif energy == "peak":
            # Maximum energy: full levels
            set_track_volume(TRACKS["SUB_BASS"], 0.90)
            set_track_volume(TRACKS["LEAD_PAD"], 0.75)
            set_track_volume(TRACKS["ATMO_PAD"], 0.70)
            print("  [AUTOMATION] Peak energy: bass 0.90, lead 0.75, pad 0.70")

        elif energy == "breakdown":
            # Space: reduce elements
            set_track_volume(TRACKS["SUB_BASS"], 0.60)
            set_track_volume(TRACKS["LEAD_PAD"], 0.40)
            print("  [AUTOMATION] Breakdown: bass 0.60, lead 0.40")

        elif energy == "fading":
            # Fade out: reduce everything
            set_track_volume(TRACKS["SUB_BASS"], 0.65)
            set_track_volume(TRACKS["LEAD_PAD"], 0.45)
            set_track_volume(TRACKS["ATMO_PAD"], 0.40)
            print("  [AUTOMATION] Fading: bass 0.65, lead 0.45, pad 0.40")

    def _ambient_automation(self, energy: str, duration: float) -> None:
        """Perform subtle automation during wait periods"""
        # Break duration into segments
        segment_duration = min(30, duration)  # Max 30 seconds per segment
        segments = int(duration / segment_duration)

        for seg in range(segments):
            if not self.running:
                break

            # Subtle parameter tweaks
            if energy in ["peak", "building"]:
                # During high energy: occasional filter wobbles
                if random.random() > 0.7:
                    track = random.choice([TRACKS["ATMO_PAD"], TRACKS["LEAD_PAD"]])
                    current = random.uniform(0.5, 0.8)
                    target = current + random.uniform(-0.1, 0.1)
                    target = max(0.3, min(0.9, target))
                    print(f"  [AMBIENT] Filter wobble on track {track}")
                    sweep_parameter(
                        track,
                        0,
                        PARAMS["FILTER_CUTOFF"],
                        current,
                        target,
                        steps=4,
                        delay_ms=200,
                    )

            elif energy == "breakdown":
                # During breakdown: add space with reverb
                if random.random() > 0.8:
                    track = random.choice([TRACKS["ATMO_PAD"], TRACKS["LEAD_PAD"]])
                    print(f"  [AMBIENT] Reverb swell on track {track}")

            # Sleep for segment
            time.sleep(segment_duration)

    def run(self):
        """Main automation loop"""
        self.print_header()

        print("[1/2] Starting playback...")
        if not start_playback():
            print("[ERROR] Could not start playback")
            return
        print("[OK] Playback started\n")

        # Fire initial clips
        print("[2/2] Firing initial clips...")
        initial_clips = [
            (TRACKS["KICK"], 0, "Kick_Fund"),
            (TRACKS["SUB_BASS"], 0, "Sub_F_Drone"),
            (TRACKS["ATMO_PAD"], 0, "Pad_Fm_Sustain"),
        ]
        for track, clip, name in initial_clips:
            if fire_clip(track, clip):
                print(f"  [OK] {name}")
            time.sleep(0.3)
        print()

        self.start_time = time.time()

        # Run each section
        for section in SECTIONS:
            if not self.running:
                break
            self.run_section(section)

        # Final summary
        total_time = time.time() - self.start_time
        print("\n" + "=" * 70)
        print("  AUTOMATION COMPLETE")
        print("=" * 70)
        print(f"  Total Duration: {format_time(total_time)}")
        print(f"  Sections Completed: {self.current_section_idx}/8")
        print("=" * 70)


# =============================================================================
# ENTRY POINT
# =============================================================================


def main():
    """Main entry point"""
    automation = DubTechnoAutomation()
    automation.run()


if __name__ == "__main__":
    main()
