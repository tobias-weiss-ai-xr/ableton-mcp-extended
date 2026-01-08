#!/usr/bin/env python3
"""
Audio Export Utilities for AbletonMCP

Converts WAV files to MP3 format for Ableton exports.
Requires: pydub, ffmpeg (or system ffmpeg)

Usage:
    python convert_to_mp3.py input.wav [output.mp3]
"""

import os
import sys
from pathlib import Path
import subprocess


def check_dependencies():
    """Check if required dependencies are available"""
    missing = []

    try:
        import pydub
        from pydub import AudioSegment

        print("v pydub available")
        print("v FFmpeg backend: pydub")
        return True
    except ImportError:
        missing.append("pydub")

    # Check for ffmpeg
    try:
        subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, check=True
        )
        print("v FFmpeg available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        if "ffmpeg" not in [dep.lower() for dep in missing]:
            missing.append("ffmpeg (system)")

    if missing:
        print("\nX Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with:")
        print("  pip install pydub")
        print("  # FFmpeg: Download from https://ffmpeg.org/download.html")
        return False

    return True


def convert_wav_to_mp3(input_file, output_file=None):
    """Convert WAV file to MP3 using pydub/ffmpeg"""

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"X Error: Input file not found: {input_file}")
        return False

    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix(".mp3")
    else:
        output_file = Path(output_file)

    print(f"\n[ Converting: {input_path.name}")
    print(f"[ Output: {output_file}")

    try:
        from pydub import AudioSegment

        # Load WAV file
        print("[ Loading WAV file...")
        audio = AudioSegment.from_wav(str(input_path))

        # Get file info
        duration = len(audio) / 1000  # seconds
        channels = audio.channels
        sample_rate = audio.frame_rate
        print(f"i Duration: {duration:.2f} seconds")
        print(f"i Channels: {channels}")
        print(f"i Sample rate: {sample_rate} Hz")

        # Export to MP3
        print("[ Converting to MP3...")
        audio.export(
            str(output_file),
            format="mp3",
            bitrate="320k",  # High quality
            parameters=["-q:a", "0"],  # Best quality
        )

        # Get file sizes
        input_size = input_path.stat().st_size / (1024 * 1024)
        output_size = output_file.stat().st_size / (1024 * 1024)

        print(f"\n[ Conversion complete!")
        print(f"[ Input:  {input_size:.2f} MB")
        print(f"[ Output: {output_size:.2f} MB")
        print(f"[ Compression: {(1 - output_size / input_size) * 100:.1f}% reduction")

        return str(output_file)

    except ImportError:
        print("\nX pydub not installed")
        print("Install: pip install pydub")
        return False
    except Exception as e:
        print(f"\nX Error during conversion: {str(e)}")
        return False


def convert_batch(directory=".", pattern="*.wav"):
    """Convert all WAV files in a directory to MP3"""

    dir_path = Path(directory)
    wav_files = list(dir_path.glob(pattern))

    if not wav_files:
        print(f"X No WAV files found in {directory}")
        return

    print(f"[ Found {len(wav_files)} WAV file(s) in {directory}")
    print()

    converted = []
    failed = []

    for wav_file in wav_files:
        print(f"\n{'=' * 60}")
        result = convert_wav_to_mp3(wav_file)
        if result:
            converted.append(wav_file)
        else:
            failed.append(wav_file)

    print(f"\n{'=' * 60}")
    print(f"[ Successfully converted: {len(converted)} file(s)")
    if failed:
        print(f"X Failed: {len(failed)} file(s)")


def main():
    """Main entry point"""

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Parse arguments
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n[ Examples:")
        print("  # Convert single file")
        print("  python convert_to_mp3.py recording.wav")
        print()
        print("  # Convert with custom output name")
        print("  python convert_to_mp3.py recording.wav mytrack.mp3")
        print()
        print("  # Batch convert all WAVs in directory")
        print("  python convert_to_mp3.py . *.wav")
        sys.exit(0)

    command = sys.argv[1]

    if command == "batch":
        # Batch conversion
        directory = sys.argv[2] if len(sys.argv) > 2 else "."
        pattern = sys.argv[3] if len(sys.argv) > 3 else "*.wav"
        convert_batch(directory, pattern)
    else:
        # Single file conversion
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_wav_to_mp3(input_file, output_file)


if __name__ == "__main__":
    main()
