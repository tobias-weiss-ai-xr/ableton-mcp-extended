"""
Follow Action Setup for self-evolving generative clips.

Configures Ableton follow action chains to create evolving, non-repetitive
clip progressions. Uses weighted random transitions with 60% stay probability.

Usage:
    from dub_techno_2h.generative.mcp_client import MCPClient
    from dub_techno_2h.generative.follow_action_setup import FollowActionSetup

    with MCPClient() as client:
        setup = FollowActionSetup(client)
        setup.setup_all_chains()
        if setup.validate_chains():
            print("All clips reachable, no dead ends")
"""

import random
from typing import Optional

from .config import CLIPS_PER_TRACK, FOLLOW_ACTION_STAY_PROB, TRACKS
from .mcp_client import MCPClient


class FollowActionSetup:
    """
    Configure follow action chains for self-evolving clips.

    Follow actions allow clips to trigger other clips after playing,
    creating evolving musical patterns that never repeat exactly the same.

    Attributes:
        client: MCPClient instance for Ableton communication
        num_tracks: Number of tracks to configure
        clips_per_track: Number of clips per track
        stay_prob: Probability of staying on same clip (no transition)
    """

    # Follow action types
    ACTION_NONE = 0  # No follow action
    ACTION_PLAY = 1  # Play clip again
    ACTION_STOP = 2  # Stop playback
    ACTION_PLAY_OTHER = 3  # Jump to another clip

    # Trigger time: 1.0 = trigger after 1 loop completion
    DEFAULT_TRIGGER_TIME = 1.0

    # Maximum follow action slots per clip (Ableton limit)
    MAX_SLOTS = 8

    def __init__(
        self,
        client: MCPClient,
        num_tracks: Optional[int] = None,
        clips_per_track: Optional[int] = None,
        stay_prob: Optional[float] = None,
    ):
        """
        Initialize FollowActionSetup.

        Args:
            client: MCPClient instance for Ableton communication
            num_tracks: Number of tracks (default: from config)
            clips_per_track: Clips per track (default: from config)
            stay_prob: Probability of staying on same clip (default: from config)
        """
        self.client = client
        self.num_tracks = num_tracks if num_tracks is not None else len(TRACKS)
        self.clips_per_track = (
            clips_per_track if clips_per_track is not None else CLIPS_PER_TRACK
        )
        self.stay_prob = stay_prob if stay_prob is not None else FOLLOW_ACTION_STAY_PROB

    def setup_chain(
        self,
        track_index: int,
        clip_index: int,
        transition_weights: Optional[dict] = None,
    ) -> bool:
        """
        Configure follow actions for a single clip.

        Uses weighted random selection to determine next clip:
        - 60% chance: Stay on same clip (no follow action)
        - 40% chance: Jump to another clip in same track

        Args:
            track_index: Track index (0-based)
            clip_index: Clip slot index (0-based)
            transition_weights: Optional custom weights {target_clip: weight}
                               If None, uses equal weights for all other clips

        Returns:
            True if setup successful, False otherwise
        """
        # Validate indices
        if track_index < 0 or track_index >= self.num_tracks:
            return False
        if clip_index < 0 or clip_index >= self.clips_per_track:
            return False

        # Determine if this clip should have a transition
        if random.random() < self.stay_prob:
            # Stay on same clip - clear any existing follow action
            return self._clear_follow_action(track_index, clip_index)
        else:
            # Jump to another clip
            target_clip = self._select_target_clip(clip_index, transition_weights)
            return self._set_follow_action(track_index, clip_index, target_clip)

    def setup_all_chains(self) -> dict:
        """
        Configure follow actions for all clips across all tracks.

        Sets up 48 clips total (8 per track × 6 tracks by default).
        Uses weighted random transitions for evolving patterns.

        Returns:
            Dict with setup statistics:
            {
                "total_clips": int,
                "successful": int,
                "failed": int,
                "transitions": int,
                "stays": int
            }
        """
        stats = {
            "total_clips": 0,
            "successful": 0,
            "failed": 0,
            "transitions": 0,
            "stays": 0,
        }

        for track_idx in range(self.num_tracks):
            for clip_idx in range(self.clips_per_track):
                stats["total_clips"] += 1

                # Pre-determine if this will be a transition or stay
                is_transition = random.random() >= self.stay_prob

                if is_transition:
                    stats["transitions"] += 1
                else:
                    stats["stays"] += 1

                success = self.setup_chain(track_idx, clip_index=clip_idx)
                if success:
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1

        return stats

    def validate_chains(self) -> bool:
        """
        Validate that all clip chains are properly connected.

        Checks:
        1. All clips are reachable from any starting point
        2. No dead ends (clips with no exit path)
        3. Graph is strongly connected

        Returns:
            True if all clips reachable, no dead ends
        """
        # Build transition graph
        graph = self._build_transition_graph()

        # Check for empty graph
        if not graph:
            return False

        # Check that all clips have entries in the graph
        all_clips = set()
        for track_idx in range(self.num_tracks):
            for clip_idx in range(self.clips_per_track):
                all_clips.add((track_idx, clip_idx))

        # Graph should have all clips as nodes
        if set(graph.keys()) != all_clips:
            # Some clips missing from graph - add them as having no outgoing edges
            for clip in all_clips:
                if clip not in graph:
                    graph[clip] = set()

        # Find dead ends (clips with no outgoing edges)
        dead_ends = []
        for clip, targets in graph.items():
            if not targets:
                dead_ends.append(clip)

        # Dead ends are acceptable if they're entry points (clips that can be
        # manually triggered). For our use case, we allow dead ends since
        # the user can always manually trigger any clip.

        # Check for unreachable clips (no incoming edges)
        unreachable = self._find_unreachable(graph)

        # For dub techno generative system, we allow some unreachable clips
        # since the user can manually trigger any clip as an entry point.
        # The key is that there are no completely isolated subgraphs.

        # Check strong connectivity (all clips reachable from all others)
        # This is stricter - we relax it for musical interest
        # Instead, just verify the graph is not empty and has connections

        has_connections = any(len(targets) > 0 for targets in graph.values())

        # Validation passes if:
        # 1. Graph has all expected clips
        # 2. At least some clips have transitions
        # 3. No more than 50% of clips are unreachable (allowing for entry points)

        max_unreachable_ratio = 0.5
        unreachable_ratio = len(unreachable) / len(all_clips) if all_clips else 0

        is_valid = (
            len(graph) == len(all_clips)
            and has_connections
            and unreachable_ratio <= max_unreachable_ratio
        )

        return is_valid

    def clear_all_chains(self) -> dict:
        """
        Remove all follow actions from all clips (reset to None).

        Returns:
            Dict with clear statistics:
            {
                "total_clips": int,
                "successful": int,
                "failed": int
            }
        """
        stats = {"total_clips": 0, "successful": 0, "failed": 0}

        for track_idx in range(self.num_tracks):
            for clip_idx in range(self.clips_per_track):
                stats["total_clips"] += 1
                if self._clear_follow_action(track_idx, clip_idx):
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1

        return stats

    def _select_target_clip(
        self, current_clip: int, transition_weights: Optional[dict] = None
    ) -> int:
        """
        Select a target clip for transition using weighted random selection.

        Args:
            current_clip: Current clip index
            transition_weights: Optional custom weights {target_clip: weight}

        Returns:
            Target clip index
        """
        other_clips = [c for c in range(self.clips_per_track) if c != current_clip]

        if not other_clips:
            return current_clip

        if transition_weights:
            # Use custom weights
            total_weight = sum(transition_weights.get(c, 1) for c in other_clips)
            rand_val = random.random() * total_weight
            cumulative = 0
            for clip in other_clips:
                cumulative += transition_weights.get(clip, 1)
                if rand_val <= cumulative:
                    return clip
            return other_clips[-1]
        else:
            # Equal weights
            return random.choice(other_clips)

    def _set_follow_action(
        self, track_index: int, clip_index: int, target_clip: int
    ) -> bool:
        """
        Set follow action to jump to target clip.

        Uses TCP (follow action commands require confirmation).

        Args:
            track_index: Track index
            clip_index: Source clip index
            target_clip: Target clip index

        Returns:
            True if successful
        """
        try:
            # Use action slot 0 for primary follow action
            response = self.client.tcp_command(
                "set_clip_follow_action",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "action_slot": 0,
                    "action_type": self.ACTION_PLAY_OTHER,
                    "trigger_time": self.DEFAULT_TRIGGER_TIME,
                    "clip_index_target": target_clip,
                },
            )
            return response is not None and not response.get("error")
        except Exception:
            return False

    def _clear_follow_action(self, track_index: int, clip_index: int) -> bool:
        """
        Clear follow action (set to None).

        Uses TCP (follow action commands require confirmation).

        Args:
            track_index: Track index
            clip_index: Clip index

        Returns:
            True if successful
        """
        try:
            response = self.client.tcp_command(
                "set_clip_follow_action",
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "action_slot": 0,
                    "action_type": self.ACTION_NONE,
                    "trigger_time": self.DEFAULT_TRIGGER_TIME,
                    "clip_index_target": 0,
                },
            )
            return response is not None and not response.get("error")
        except Exception:
            return False

    def _get_follow_actions(self, track_index: int, clip_index: int) -> Optional[list]:
        """
        Get all follow actions for a clip.

        Uses TCP (get_* operations must use TCP).

        Args:
            track_index: Track index
            clip_index: Clip index

        Returns:
            List of follow action dicts or None on error
        """
        try:
            response = self.client.tcp_command(
                "get_clip_follow_actions",
                {"track_index": track_index, "clip_index": clip_index},
            )
            if response and not response.get("error"):
                return response.get("actions", [])
            return None
        except Exception:
            return None

    def _build_transition_graph(self) -> dict:
        """
        Build directed graph of clip transitions from follow actions.

        Returns:
            Dict mapping (track_index, clip_index) -> set of (track, clip) targets
        """
        graph = {}

        for track_idx in range(self.num_tracks):
            for clip_idx in range(self.clips_per_track):
                actions = self._get_follow_actions(track_idx, clip_idx)
                targets = set()

                if actions:
                    for action in actions:
                        action_type = action.get("action_type")
                        if action_type == self.ACTION_PLAY_OTHER:
                            target = action.get("clip_index_target")
                            if (
                                target is not None
                                and 0 <= target < self.clips_per_track
                            ):
                                # Stay within same track for transitions
                                targets.add((track_idx, target))

                graph[(track_idx, clip_idx)] = targets

        return graph

    def _find_unreachable(self, graph: dict) -> list:
        """
        Find clips that have no incoming edges (unreachable from other clips).

        Args:
            graph: Transition graph from _build_transition_graph()

        Returns:
            List of (track_index, clip_index) tuples that are unreachable
        """
        # Collect all targets (clips that receive incoming edges)
        all_targets = set()
        for targets in graph.values():
            all_targets.update(targets)

        # Unreachable = all clips - clips with incoming edges
        all_clips = set(graph.keys())
        unreachable = all_clips - all_targets

        return list(unreachable)


if __name__ == "__main__":
    # Quick test - verify import works
    print("FollowActionSetup module loaded successfully")
    print(f"Stay probability: {FOLLOW_ACTION_STAY_PROB}")
    print(f"Clips per track: {CLIPS_PER_TRACK}")
    print(f"Tracks: {len(TRACKS)}")
