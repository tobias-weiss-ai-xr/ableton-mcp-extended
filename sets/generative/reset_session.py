"""
Reset Ableton session to clean state.

Resets follow actions, track volumes, device parameters, stops all clips,
and resets playhead to bar 1.

Usage:
    python reset_session.py           # Apply reset
    python reset_session.py --dry-run # Preview changes without applying
    python reset_session.py --verbose # Verbose output
"""

import sys
import argparse
from typing import Optional

from config import TRACKS, BASELINE_VALUES, CLIPS_PER_TRACK
from mcp_client import MCPClient, MCPConnectionError


def reset_session(dry_run: bool = False, verbose: bool = False) -> int:
    """
    Reset Ableton session to clean state.

    Args:
        dry_run: If True, preview changes without applying
        verbose: If True, show detailed output

    Returns:
        0: Success
        1: Connection error
        2: Command error
    """
    log = lambda msg: print(f"[reset_session] {msg}")

    # Count for summary
    total_clips = len(TRACKS) * CLIPS_PER_TRACK
    total_tracks = len(TRACKS)

    if dry_run:
        log("DRY RUN - no changes will be made")
        log(f"Would clear {total_clips} follow actions")
        log(f"Would reset {total_tracks} track volumes to 0.75")
        log("Would reset device parameters")
        log("Would stop all clips")
        log("Would reset playhead to bar 1")
        log(f"DRY RUN complete: {total_clips} clips, {total_tracks} tracks")
        return 0

    # Connect to Ableton
    log("Connecting to Ableton...")
    try:
        with MCPClient() as client:
            client.verify_connection()
            log("Connected successfully")

            # 1. Clear all follow actions
            log(f"Clearing follow actions for {total_clips} clips...")
            follow_errors = 0
            for track_name, track_index in TRACKS.items():
                for clip_index in range(CLIPS_PER_TRACK):
                    try:
                        client.send(
                            "set_clip_follow_action",
                            {
                                "track_index": track_index,
                                "clip_index": clip_index,
                                "action_slot": 0,
                                "action_type": 0,  # None
                                "trigger_time": 0,
                                "clip_index_target": 0,
                            },
                        )
                        if verbose:
                            log(f"  Cleared follow action: {track_name}[{clip_index}]")
                    except Exception as e:
                        follow_errors += 1
                        if verbose:
                            log(
                                f"  Warning: Could not clear follow action for {track_name}[{clip_index}]: {e}"
                            )

            if follow_errors > 0 and not verbose:
                log(
                    f"  {follow_errors} follow action clear errors (use --verbose for details)"
                )

            # 2. Reset all track volumes to 0.75 (~0 dB)
            log(f"Resetting {total_tracks} track volumes to 0.75...")
            volume_errors = 0
            default_volume = 0.75
            for track_name, track_index in TRACKS.items():
                # Use track-specific baseline if available, otherwise 0.75
                target_volume = BASELINE_VALUES.get("volume", {}).get(
                    track_name, default_volume
                )
                try:
                    client.send(
                        "set_track_volume",
                        {"track_index": track_index, "volume": target_volume},
                    )
                    if verbose:
                        log(f"  Reset volume: {track_name} -> {target_volume}")
                except Exception as e:
                    volume_errors += 1
                    if verbose:
                        log(f"  Warning: Could not reset volume for {track_name}: {e}")

            if volume_errors > 0 and not verbose:
                log(
                    f"  {volume_errors} volume reset errors (use --verbose for details)"
                )

            # 3. Reset device parameters (informational - no specific device API)
            log("Resetting device parameters...")
            if verbose:
                log("  Note: Device parameter reset requires device-specific knowledge")
                log(
                    "  Use load_device_preset or set_device_parameter for specific devices"
                )

            # 4. Stop all playing clips
            log("Stopping all clips...")
            clip_errors = 0
            for track_name, track_index in TRACKS.items():
                for clip_index in range(CLIPS_PER_TRACK):
                    try:
                        client.send(
                            "stop_clip",
                            {"track_index": track_index, "clip_index": clip_index},
                        )
                        if verbose:
                            log(f"  Stopped clip: {track_name}[{clip_index}]")
                    except Exception as e:
                        clip_errors += 1
                        if verbose:
                            log(
                                f"  Warning: Could not stop clip {track_name}[{clip_index}]: {e}"
                            )

            if clip_errors > 0 and not verbose:
                log(f"  {clip_errors} clip stop errors (use --verbose for details)")

            # 5. Stop playback
            log("Stopping playback...")
            try:
                client.send("stop_playback", {})
            except Exception as e:
                if verbose:
                    log(f"  Warning: Could not stop playback: {e}")

            # 6. Reset playhead to bar 1
            log("Resetting playhead to bar 1...")
            try:
                client.send("set_playhead_position", {"bar": 1, "beat": 0})
            except Exception as e:
                if verbose:
                    log(f"  Warning: Could not reset playhead: {e}")

            # Summary
            log(f"Reset complete: {total_clips} clips, {total_tracks} tracks")
            return 0

    except MCPConnectionError as e:
        log(f"Connection error: {e}")
        return 1
    except Exception as e:
        log(f"Command error: {e}")
        return 2


def main() -> int:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Reset Ableton session to clean state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python reset_session.py           # Apply reset
    python reset_session.py --dry-run # Preview changes without applying
    python reset_session.py --verbose # Show detailed output

Exit codes:
    0: Success
    1: Connection error (Ableton not running or MCP not available)
    2: Command error (operation failed)
""",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    return reset_session(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
