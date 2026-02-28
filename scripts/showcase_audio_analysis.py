#!/usr/bin/env python3
"""
Real-Time Audio Analysis Showcase for Ableton MCP Extended

This script demonstrates the real-time audio analysis capabilities:
- BPM detection via aubio
- Key detection via librosa
- Loudness measurement (LUFS) via pyloudnorm
- Spectral analysis (centroid, rolloff)
- WebSocket streaming for dashboards

SETUP REQUIREMENTS:
1. Route Ableton audio output to VB-Cable:
   - In Ableton: Preferences -> Audio -> Audio Output Device = "CABLE Input"
2. Run this script while Ableton is playing

USAGE:
    python showcase_audio_analysis.py
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from MCP_Server.audio_analysis import (
    AudioAnalyzer,
    AudioAnalyzerConfig,
    AudioAnalysisCondition,
    AudioConditionType,
)


def print_progress_bar(iteration, total, prefix="", suffix="", length=50, fill="█"):
    """Print a progress bar."""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="\r")
    if iteration == total:
        print()


def main():
    print("=" * 60)
    print("  REAL-TIME AUDIO ANALYSIS SHOWCASE")
    print("  Ableton MCP Extended")
    print("=" * 60)
    print()

    # Configuration
    config = AudioAnalyzerConfig(
        sample_rate=44100,
        buffer_size=2048,
        analysis_features={
            "bpm": True,
            "key": True,
            "spectral": True,
            "loudness": True,
        },
    )

    # Create analyzer
    analyzer = AudioAnalyzer(config)

    # Start analyzer
    print("Starting audio analyzer...")
    started = analyzer.start()

    if not started:
        print()
        print("ERROR: Could not start audio analyzer!")
        print()
        print("TROUBLESHOOTING:")
        print("1. Install VB-Audio Cable from: https://vb-audio.com/Cable/")
        print("2. In Ableton, go to: Preferences -> Audio")
        print("3. Set 'Audio Output Device' to 'CABLE Input (VB-Audio Virtual Cable)'")
        print("4. Make sure audio is playing in Ableton")
        print()
        return

    print("Audio analyzer started successfully!")
    print()
    print("Listening for audio from VB-Cable...")
    print("Press Ctrl+C to stop")
    print()
    print("-" * 60)

    # Analysis loop
    iteration = 0
    max_iterations = 60  # 60 seconds at 1 second intervals

    try:
        while iteration < max_iterations:
            # Get analysis
            analysis = analyzer.get_analysis()

            # Clear and display
            print(f"\033[H\033[J", end="")  # Clear screen
            print("=" * 60)
            print("  REAL-TIME AUDIO ANALYSIS")
            print("=" * 60)
            print()
            print(f"  BPM:              {analysis.get('bpm', 0):.1f}")
            print(
                f"  Key:              {analysis.get('key', 'unknown')} (confidence: {analysis.get('key_confidence', 0):.2%})"
            )
            print(f"  Loudness:         {analysis.get('loudness_lufs', -100):.1f} LUFS")
            print(f"  Spectral Centroid:{analysis.get('spectral_centroid', 0):.0f} Hz")
            print(f"  Spectral Rolloff: {analysis.get('spectral_rolloff', 0):.0f} Hz")
            print(f"  RMS Level:        {analysis.get('rms', 0):.4f}")
            print(
                f"  Beat Detected:    {'YES' if analysis.get('beat', False) else 'NO'}"
            )
            print()
            print("-" * 60)

            # Rule engine demo
            print("  AUTO-DJ RULES DEMO:")
            print()

            # BPM rule
            bpm_rule = AudioAnalysisCondition(condition_type="bpm_gt", threshold=120)
            if bpm_rule.evaluate(analysis):
                print("    [TRIGGERED] BPM > 120 - Tempo is high!")
            else:
                print(
                    f"    [MONITORING] BPM > 120 - Current: {analysis.get('bpm', 0):.1f}"
                )

            # Loudness rule
            loud_rule = AudioAnalysisCondition(
                condition_type="loudness_lt", threshold=-20
            )
            if loud_rule.evaluate(analysis):
                print("    [TRIGGERED] LUFS < -20 - Audio is quiet")
            else:
                print(
                    f"    [MONITORING] LUFS < -20 - Current: {analysis.get('loudness_lufs', -100):.1f}"
                )

            # Spectral rule
            bright_rule = AudioAnalysisCondition(
                condition_type="spectral_centroid_gt", threshold=3000
            )
            if bright_rule.evaluate(analysis):
                print("    [TRIGGERED] Spectral Centroid > 3000 Hz - Bright sound!")
            else:
                print(
                    f"    [MONITORING] Spectral > 3000 Hz - Current: {analysis.get('spectral_centroid', 0):.0f} Hz"
                )

            print()
            print("-" * 60)
            print(
                f"  Running: {iteration + 1}/{max_iterations}s | Press Ctrl+C to stop"
            )
            print()

            time.sleep(1)
            iteration += 1

    except KeyboardInterrupt:
        print()
        print("Stopping analyzer...")

    finally:
        analyzer.stop()
        print()
        print("=" * 60)
        print("  Audio analyzer stopped.")
        print("=" * 60)


if __name__ == "__main__":
    main()
