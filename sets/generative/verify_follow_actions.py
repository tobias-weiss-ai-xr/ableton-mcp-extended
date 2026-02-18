"""
Verify follow action chain completeness.

Queries all clips, builds transition graph, detects dead ends and unreachable clips.
Read-only operation - does not modify any Ableton state.

Usage:
    python verify_follow_actions.py           # Normal output
    python verify_follow_actions.py --verbose # Detailed output

Exit codes:
    0: All chains valid
    1: Dead ends or unreachable clips found
"""

import argparse
import sys
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

from config import TRACKS, CLIPS_PER_TRACK
from mcp_client import MCPClient, MCPConnectionError


def get_all_clip_ids() -> List[Tuple[int, int]]:
    """Generate all (track_index, clip_index) pairs."""
    clip_ids = []
    track_count = len(TRACKS)
    for track_idx in range(track_count):
        for clip_idx in range(CLIPS_PER_TRACK):
            clip_ids.append((track_idx, clip_idx))
    return clip_ids


def query_follow_actions(
    client: MCPClient, verbose: bool = False
) -> Dict[Tuple[int, int], dict]:
    """
    Query follow actions for all clips.

    Returns:
        Dict mapping (track_idx, clip_idx) -> follow action dict
    """
    clip_ids = get_all_clip_ids()
    total_clips = len(clip_ids)

    print(f"[verify] Querying {total_clips} clips across {len(TRACKS)} tracks...")

    follow_actions = {}

    for track_idx, clip_idx in clip_ids:
        try:
            result = client.tcp_command(
                "get_clip_follow_actions",
                {"track_index": track_idx, "clip_index": clip_idx},
            )

            if result and "result" in result:
                follow_actions[(track_idx, clip_idx)] = result["result"]
            else:
                follow_actions[(track_idx, clip_idx)] = {"action_type": 0}

        except Exception as e:
            if verbose:
                print(
                    f"[verify] Warning: Could not query track {track_idx} clip {clip_idx}: {e}"
                )
            follow_actions[(track_idx, clip_idx)] = {"action_type": 0}

    return follow_actions


def build_transition_graph(
    follow_actions: Dict[Tuple[int, int], dict], verbose: bool = False
) -> Tuple[
    Dict[Tuple[int, int], Set[Tuple[int, int]]],
    Dict[Tuple[int, int], Set[Tuple[int, int]]],
]:
    """
    Build directed graph of clip transitions.

    Returns:
        Tuple of (outgoing_graph, incoming_graph)
        - outgoing_graph: from_clip -> set of to_clips
        - incoming_graph: to_clip -> set of from_clips
    """
    print("[verify] Building transition graph...")

    outgoing: Dict[Tuple[int, int], Set[Tuple[int, int]]] = defaultdict(set)
    incoming: Dict[Tuple[int, int], Set[Tuple[int, int]]] = defaultdict(set)

    for (track_idx, clip_idx), actions in follow_actions.items():
        from_clip = (track_idx, clip_idx)

        # action_type: 0=None, 1=Play Clip, 2=Stop Clip, 3=Play Other Clip
        action_type = actions.get("action_type", 0)

        if action_type == 3:  # Play Other Clip
            # Get target clip index
            target_clip_idx = actions.get("clip_index_target", -1)
            if target_clip_idx >= 0 and target_clip_idx < CLIPS_PER_TRACK:
                to_clip = (track_idx, target_clip_idx)
                outgoing[from_clip].add(to_clip)
                incoming[to_clip].add(from_clip)

                if verbose:
                    print(
                        f"  Clip {track_idx}:{clip_idx} -> Clip {track_idx}:{target_clip_idx} (action_type=3)"
                    )

    return outgoing, incoming


def find_dead_ends(
    outgoing: Dict[Tuple[int, int], Set[Tuple[int, int]]],
    all_clips: List[Tuple[int, int]],
    verbose: bool = False,
) -> List[Tuple[int, int]]:
    """
    Find clips with no outgoing transitions (action_type=0 or None).

    These are dead ends unless they're intentionally terminal clips.
    """
    print("[verify] Checking for dead ends...")

    dead_ends = []

    for clip_id in all_clips:
        if len(outgoing[clip_id]) == 0:
            dead_ends.append(clip_id)

    return dead_ends


def find_unreachable(
    incoming: Dict[Tuple[int, int], Set[Tuple[int, int]]],
    all_clips: List[Tuple[int, int]],
    entry_points: List[Tuple[int, int]],
    verbose: bool = False,
) -> List[Tuple[int, int]]:
    """
    Find clips that cannot be reached from any entry point.

    Uses BFS from entry points to find all reachable clips.
    """
    print("[verify] Checking for unreachable clips...")

    # BFS from entry points
    visited = set()
    queue = deque(entry_points)

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        # Add all clips that have incoming edges from current clip
        # (clips that can be reached from current)
        for clip_id in all_clips:
            if current in incoming.get(clip_id, set()) and clip_id not in visited:
                queue.append(clip_id)

    unreachable = [clip for clip in all_clips if clip not in visited]
    return unreachable


def get_track_name(track_idx: int) -> str:
    """Get track name by index."""
    for name, idx in TRACKS.items():
        if idx == track_idx:
            return name
    return f"track_{track_idx}"


def main():
    parser = argparse.ArgumentParser(description="Verify follow action chains")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    args = parser.parse_args()

    verbose = args.verbose

    try:
        with MCPClient() as client:
            client.verify_connection()

            # Query all follow actions
            follow_actions = query_follow_actions(client, verbose)

            # Build graph
            outgoing, incoming = build_transition_graph(follow_actions, verbose)

            all_clips = get_all_clip_ids()

            if verbose:
                print(
                    f"[verify] Graph has {len(all_clips)} nodes, {sum(len(v) for v in outgoing.values())} edges"
                )

            # Find entry points (first clip of each track)
            entry_points = [(track_idx, 0) for track_idx in range(len(TRACKS))]

            # Check for dead ends
            dead_ends = find_dead_ends(outgoing, all_clips, verbose)

            # Check for unreachable clips
            unreachable = find_unreachable(incoming, all_clips, entry_points, verbose)

            if verbose:
                print(f"[verify] Dead ends: {len(dead_ends)}")
                print(f"[verify] Unreachable: {len(unreachable)}")

                if dead_ends:
                    print("[verify] Dead end clips:")
                    for track_idx, clip_idx in dead_ends:
                        print(f"  {get_track_name(track_idx)} clip {clip_idx}")

                if unreachable:
                    print("[verify] Unreachable clips:")
                    for track_idx, clip_idx in unreachable:
                        print(f"  {get_track_name(track_idx)} clip {clip_idx}")

            # Report result
            if not dead_ends and not unreachable:
                print("PASS: All clips reachable, no dead ends")
                return 0
            else:
                reasons = []
                if dead_ends:
                    reasons.append(f"{len(dead_ends)} dead ends")
                if unreachable:
                    reasons.append(f"{len(unreachable)} unreachable")
                print(f"FAIL: {', '.join(reasons)}")
                return 1

    except MCPConnectionError as e:
        print(f"[verify] Error: Cannot connect to Ableton - {e}")
        return 1
    except Exception as e:
        print(f"[verify] Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
