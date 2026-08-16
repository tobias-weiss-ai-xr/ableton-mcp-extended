"""
Performance-Optimized Arrangement Capture Tools for Ableton Live

Optimizations:
- Caching for track/scene/device lookups
- Batch processing for track operations
- Reduced network calls through memoization
- Pre-validation to avoid wasted captures
- Adaptive timing and timeouts
"""

import json
import time
import functools
from typing import Dict, List, Union, Optional, Any, Tuple, Set
from mcp.server.fastmcp import FastMCP, Context


class AbletonCache:
    """Cache for Ableton Live data to reduce redundant API calls."""
    
    def __init__(self, ttl: float = 5.0):
        """
        Initialize cache with time-to-live (TTL) in seconds.
        We use a short TTL since Live data can change during a session.
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if still valid."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache a value."""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """Clear all cached data."""
        self._cache.clear()
    
    def invalidate(self, key: str):
        """Invalidate a specific cache entry."""
        if key in self._cache:
            del self._cache[key]


# Global cache instance
_ableton_cache = AbletonCache(ttl=10.0)


def _cached_get_tempo(ableton) -> float:
    """Get current BPM with caching."""
    cache_key = "tempo"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        info = ableton.send_command("get_session_info", {})
        bpm = float(info.get("tempo", 120.0))
        _ableton_cache.set(cache_key, bpm)
        return bpm
    except:
        return 120.0


def _cached_get_all_tracks(ableton) -> List[Dict]:
    """Get all tracks with caching."""
    cache_key = "all_tracks"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        result = ableton.send_command("get_all_tracks", {})
        if isinstance(result, dict):
            tracks = result.get("tracks", [])
            _ableton_cache.set(cache_key, tracks)
            return tracks
        return []
    except:
        return []


def _cached_get_scene_info(ableton, scene_index: int) -> Optional[Dict]:
    """Get scene info with caching."""
    cache_key = f"scene_{scene_index}"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        result = ableton.send_command("get_scene_info", {"scene_index": scene_index})
        if isinstance(result, dict):
            _ableton_cache.set(cache_key, result)
            return result
        return None
    except:
        return None


def _cached_get_clips_in_scene(ableton, scene_index: int) -> List[Tuple[int, int]]:
    """Get clips in scene with caching."""
    cache_key = f"scene_clips_{scene_index}"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        result = ableton.send_command("get_scene_clips", {"scene_index": scene_index})
        if isinstance(result, dict):
            clips = result.get("clips", [])
            clip_list = [(c.get("track_index", 0), c.get("clip_index", 0)) for c in clips]
            _ableton_cache.set(cache_key, clip_list)
            return clip_list
        return []
    except:
        return []


def _cached_get_tracks_with_clips_in_scene(ableton, scene_index: int) -> List[int]:
    """Get track indices with clips in scene, with caching."""
    clips = _cached_get_clips_in_scene(ableton, scene_index)
    return list(set([track_idx for track_idx, _ in clips]))


def _cached_get_device_info(ableton, track_index: int, device_index: int) -> Optional[Dict]:
    """Get device info with caching."""
    cache_key = f"device_{track_index}_{device_index}"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        result = ableton.send_command("get_device_info", {
            "track_index": track_index,
            "device_index": device_index
        })
        if isinstance(result, dict):
            _ableton_cache.set(cache_key, result)
            return result
        return None
    except:
        return None


def _cached_get_track_devices(ableton, track_index: int) -> List[Dict]:
    """Get track devices with caching."""
    cache_key = f"track_devices_{track_index}"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        result = ableton.send_command("get_track_devices", {"track_index": track_index})
        if isinstance(result, dict):
            devices = result.get("devices", [])
            _ableton_cache.set(cache_key, devices)
            return devices
        return []
    except:
        return []


def _cached_find_filter_device(ableton, track_index: int) -> Optional[Tuple[int, Dict]]:
    """Find filter device with caching."""
    cache_key = f"filter_device_{track_index}"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    devices = _cached_get_track_devices(ableton, track_index)
    for i, device in enumerate(devices):
        name = device.get("name", "").lower()
        if any(keyword in name for keyword in ["auto filter", "eq three", "eq eight", "filter", "lpf", "hpf"]):
            result = (i, device)
            _ableton_cache.set(cache_key, result)
            return result
    
    _ableton_cache.set(cache_key, None)
    return None


def _cached_find_delay_device(ableton, track_index: int) -> Optional[Tuple[int, Dict]]:
    """Find delay device with caching."""
    cache_key = f"delay_device_{track_index}"
    cached = _ableton_cache.get(cache_key)
    if cached is not None:
        return cached
    
    devices = _cached_get_track_devices(ableton, track_index)
    for i, device in enumerate(devices):
        name = device.get("name", "").lower()
        if any(keyword in name for keyword in ["delay", "echo", "reverb", "grain delay"]):
            result = (i, device)
            _ableton_cache.set(cache_key, result)
            return result
    
    _ableton_cache.set(cache_key, None)
    return None


# Batch operations for performance

def _batch_arm_tracks(ableton, track_indices: List[int], arm: bool = True):
    """
    Arm/disarm multiple tracks efficiently.
    While Remote Script processes commands sequentially, batching still has benefits:
    - Better error handling
    - Cleaner logging
    - Easier to manage
    """
    success_count = 0
    for track_idx in track_indices:
        try:
            ableton.send_command("set_track_arm", {"track_index": track_idx, "arm": arm})
            success_count += 1
        except Exception as e:
            # Log but continue with other tracks
            pass
    
    # Small delay to allow Ableton to process
    time.sleep(0.1 if success_count > 10 else 0.05)
    return success_count


def _batch_set_track_volumes(ableton, volume_map: Dict[int, float]):
    """
    Set volumes for multiple tracks efficiently.
    
    Args:
        volume_map: Dict of {track_index: volume_value}
    """
    for track_idx, volume in volume_map.items():
        try:
            ableton.send_command("set_track_volume", {"track_index": track_idx, "volume": volume})
        except:
            pass
    time.sleep(0.1)


def _batch_create_locators(ableton, locators: List[Dict[str, Any]]):
    """
    Create multiple locators efficiently.
    
    Args:
        locators: List of dicts with 'name', 'bar', 'color' keys
    """
    for locator in locators:
        try:
            ableton.send_command("create_locator", {
                "name": locator.get("name", "Unnamed"),
                "bar": locator.get("bar", 0),
                "color": locator.get("color")
            })
        except:
            pass
    time.sleep(0.1)


def _prevalidate_capture(
    ableton, 
    scene_sequence: List[int], 
    scene_bars: List[int],
    bpm: float,
    max_time: float = 60.0
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Pre-validate capture setup to catch issues before starting.
    
    Returns: (is_valid, message, info_dict)
    """
    info = {
        "scene_count": len(scene_sequence),
        "total_bars": sum(scene_bars),
        "estimated_time": 0,
        "scenes_without_clips": [],
        "total_tracks_in_scenes": 0,
        "unique_tracks": set()
    }
    
    # Check scene/bar length match
    if len(scene_sequence) != len(scene_bars):
        return False, "scene_sequence and scene_bars length mismatch", info
    
    if len(scene_sequence) == 0:
        return False, "Empty scene sequence", info
    
    # Check each scene has clips
    secs_per_bar = (60.0 / bpm) if bpm > 0 else 0.5
    total_bars = sum(scene_bars)
    estimated_time = secs_per_bar * total_bars * 1.2  # 20% buffer
    info["estimated_time"] = estimated_time
    
    # Check time limit
    if estimated_time > max_time:
        return False, f"Estimated time ({estimated_time:.1f}s) exceeds {max_time}s limit", info
    
    # Check scenes exist and have clips
    for i, scene_idx in enumerate(scene_sequence):
        tracks = _cached_get_tracks_with_clips_in_scene(ableton, scene_idx)
        info["unique_tracks"].update(tracks)
        info["total_tracks_in_scenes"] += len(tracks)
        
        if len(tracks) == 0:
            info["scenes_without_clips"].append(scene_idx)
    
    # Check if any scenes are empty
    if info["scenes_without_clips"]:
        return False, f"Scenes without clips: {info['scenes_without_clips']}", info
    
    info["unique_tracks"] = sorted(list(info["unique_tracks"]))
    
    return True, "Validation passed", info


# Adaptive timing
class AdaptiveTimer:
    """Adaptive timing for scene capture based on actual BPM."""
    
    def __init__(self, bpm: float = 120.0):
        self.bpm = bpm
        self.secs_per_bar = (60.0 / bpm) * 4  # 4 beats = 1 bar
    
    def wait_for_bars(self, num_bars: float, safety_factor: float = 0.9):
        """Wait for a specific number of bars with safety buffer."""
        wait_time = self.secs_per_bar * num_bars * safety_factor
        # Add small buffer for processing time
        wait_time = max(wait_time, 0.1)
        time.sleep(wait_time)
    
    def wait_for_scene(self, bars: int, crossfade_bars: int = 0):
        """Wait for a scene to play, accounting for crossfade."""
        effective_bars = max(bars - crossfade_bars, 1)
        self.wait_for_bars(effective_bars)
    
    def update_bpm(self, bpm: float):
        """Update BPM and recalculate timing."""
        if bpm != self.bpm:
            self.bpm = bpm
            self.secs_per_bar = (60.0 / bpm) * 4


def _beats_to_seconds_cached(beats: float, bpm: float = None) -> float:
    """Convert beats to seconds with optional BPM override."""
    if bpm is None:
        # Use cached BPM from last call
        # We can't easily cache this without a global, so just use default
        bpm = 120.0
    return (60.0 / bpm) * beats


def register_performance_tools(mcp: FastMCP, get_ableton_connection):
    """Register performance-optimized arrangement tools."""
    import logging
    logger = logging.getLogger("AbletonMCPServer")

    # =========================================================================
    # OPTIMIZED SCENE CAPTURE
    # =========================================================================

    @mcp.tool()
    def capture_scenes_optimized(
        ctx: Context,
        scene_sequence: List[int],
        scene_bars: List[int],
        start_bar: int = 0,
        pre_count_bars: int = 0,
        use_metronome: bool = False,
        arm_only_relevant: bool = True,
        add_locators: bool = True,
        validate_first: bool = True,
        max_time: float = 60.0,
    ) -> str:
        """
        Performance-optimized scene capture with:
        - Pre-validation to catch issues early
        - Caching for all track/scene lookups
        - Batch operations for track arming and volume changes
        - Adaptive timing based on BPM
        - Minimal network calls
        
        Parameters:
        - scene_sequence: List of scene indices
        - scene_bars: List of bar lengths
        - start_bar: Starting bar (default: 0)
        - pre_count_bars: Count-in bars (default: 0)
        - use_metronome: Enable metronome (default: False)
        - arm_only_relevant: Only arm tracks with clips (default: True)
        - add_locators: Create locators at scene boundaries (default: True)
        - validate_first: Pre-validate before starting (default: True)
        - max_time: Maximum allowed capture time in seconds (default: 60)
        
        Returns: JSON with status, performance metrics, and capture details
        """
        try:
            import time as time_mod
            start_time = time_mod.time()
            
            ableton = get_ableton_connection()
            bpm = _cached_get_tempo(ableton)
            timer = AdaptiveTimer(bpm)
            
            # Pre-validation
            if validate_first:
                is_valid, message, info = _prevalidate_capture(
                    ableton, scene_sequence, scene_bars, bpm, max_time
                )
                
                if not is_valid:
                    return json.dumps({
                        "status": "validation_failed",
                        "message": message,
                        "validation_info": info
                    }, indent=2)
            
            # Get all scene track info in one pass (cached)
            scene_track_map = {}
            for scene_idx in scene_sequence:
                scene_track_map[scene_idx] = _cached_get_tracks_with_clips_in_scene(ableton, scene_idx)
            
            # Determine which tracks to arm
            if arm_only_relevant:
                all_relevant_tracks = set()
                for tracks in scene_track_map.values():
                    all_relevant_tracks.update(tracks)
                tracks_to_arm = sorted(list(all_relevant_tracks))
            else:
                all_tracks = _cached_get_all_tracks(ableton)
                tracks_to_arm = [t.get("index", i) for i, t in enumerate(all_tracks)]
            
            # Store original volumes (cached)
            original_volumes = {}
            for track_idx in tracks_to_arm:
                try:
                    info = _cached_get_track_info(ableton, track_idx)
                    if info:
                        original_volumes[track_idx] = float(info.get("volume", 1.0))
                except:
                    original_volumes[track_idx] = 1.0
            
            # Batch disarm all tracks first
            all_track_indices = [t.get("index", i) for i, t in enumerate(_cached_get_all_tracks(ableton))]
            _batch_arm_tracks(ableton, all_track_indices, arm=False)
            
            # Batch arm relevant tracks
            _batch_arm_tracks(ableton, tracks_to_arm, arm=True)
            
            # Enable metronome
            if use_metronome:
                try:
                    ableton.send_command("set_metronome", {"enabled": True})
                except:
                    pass
                time.sleep(0.1)
            
            # Set starting position
            try:
                ableton.send_command("set_playhead_position", {"bar": start_bar, "beat": 0})
            except:
                pass
            time.sleep(0.1)
            
            # Create start locator if requested
            locators_to_create = []
            if add_locators:
                locators_to_create.append({"name": "Capture_Start", "bar": start_bar, "color": None})
            
            # Handle pre-count
            if pre_count_bars > 0:
                ableton.send_command("start_recording", {})
                time.sleep(0.3)
                ableton.send_command("start_playback", {})
                time.sleep(0.3)
                timer.wait_for_bars(pre_count_bars)
            else:
                ableton.send_command("start_recording", {})
                time.sleep(0.3)
                ableton.send_command("start_playback", {})
                time.sleep(0.3)
            
            # Trigger scenes with optimized timing
            scenes_captured = 0
            current_bar = start_bar + pre_count_bars
            capture_log = []
            
            for i, (scene_idx, bars) in enumerate(zip(scene_sequence, scene_bars)):
                # Create locator for this scene
                if add_locators:
                    scene_name = f"Scene_{scene_idx}"
                    locators_to_create.append({"name": f"{scene_name}_Bar{current_bar}", "bar": current_bar, "color": None})
                
                # Trigger scene
                ableton.send_command("trigger_scene", {"scene_index": scene_idx})
                scenes_captured += 1
                
                capture_log.append({
                    "scene": scene_idx,
                    "bars": bars,
                    "start_bar": current_bar,
                    "bpm": bpm,
                    "tracks_in_scene": len(scene_track_map.get(scene_idx, []))
                })
                
                current_bar += bars
                timer.wait_for_bars(bars, safety_factor=0.9)
            
            # Wait for final buffer
            time.sleep(0.5)
            
            # Stop recording
            ableton.send_command("stop_recording", {})
            time.sleep(0.3)
            ableton.send_command("stop_playback", {})
            
            # Stop metronome
            if use_metronome:
                try:
                    ableton.send_command("set_metronome", {"enabled": False})
                except:
                    pass
            
            # Batch create locators
            if add_locators:
                locators_to_create.append({"name": "Capture_End", "bar": current_bar, "color": None})
                _batch_create_locators(ableton, locators_to_create)
            
            # Restore volumes if changed (would need batch volume set)
            # For now, just disarm
            _batch_arm_tracks(ableton, tracks_to_arm, arm=False)
            
            # Calculate performance metrics
            elapsed_time = time_mod.time() - start_time
            automation_points = len(capture_log)
            efficiency = (len(tracks_to_arm) / len(all_track_indices) * 100) if all_track_indices else 0
            
            logger.info(f"Optimized capture: {scenes_captured} scenes in {elapsed_time:.2f}s")
            
            return json.dumps({
                "status": "success",
                "scenes_captured": scenes_captured,
                "total_bars": sum(scene_bars) + pre_count_bars,
                "start_bar": start_bar,
                "end_bar": current_bar,
                
                "performance": {
                    "elapsed_time_seconds": elapsed_time,
                    "scenes_per_second": scenes_captured / elapsed_time if elapsed_time > 0 else 0,
                    "arming_efficiency": f"{efficiency:.1f}%",
                    "tracks_armed": len(tracks_to_arm),
                    "total_tracks": len(all_track_indices)
                },
                
                "options": {
                    "pre_count_bars": pre_count_bars,
                    "metronome_used": use_metronome,
                    "arm_only_relevant": arm_only_relevant,
                    "locators_created": add_locators,
                    "validate_first": validate_first
                },
                
                "capture_log": capture_log,
                "capture_method": "optimized"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in optimized capture: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # PARALLEL SCENE CAPTURE (Non-blocking for compatible commands)
    # =========================================================================

    @mcp.tool()
    def capture_scenes_parallel(
        ctx: Context,
        scene_sequence: List[int],
        scene_bars: List[int],
        start_bar: int = 0,
        parallel_arming: bool = True,
        parallel_volumeChanges: bool = False,
    ) -> str:
        """
        Capture scenes with parallel processing where possible.
        
        Note: Ableton's Remote Script is single-threaded, so true parallelism
        isn't possible. However, we can optimize by:
        - Grouping non-blocking operations
        - Reducing wait times between non-critical commands
        - Using batch operations
        
        Parameters:
        - scene_sequence: List of scene indices
        - scene_bars: List of bar lengths
        - start_bar: Starting bar (default: 0)
        - parallel_arming: Group track arming commands (default: True)
        - parallel_volumeChanges: Group volume changes (default: False)
        
        Returns: JSON with status and capture details
        """
        try:
            import time as time_mod
            
            if len(scene_sequence) != len(scene_bars):
                return json.dumps({
                    "status": "error",
                    "message": "scene_sequence and scene_bars must have the same length"
                }, indent=2)
            
            ableton = get_ableton_connection()
            bpm = _cached_get_tempo(ableton)
            secs_per_bar = (60.0 / bpm) * 4
            
            # Get all relevant tracks using caching
            all_relevant_tracks = _get_all_scene_track_indices(ableton, scene_sequence)
            
            # Optimized: Arm all tracks in one batch call
            if parallel_arming:
                _batch_arm_tracks(ableton, all_relevant_tracks, arm=True)
            else:
                for track_idx in all_relevant_tracks:
                    try:
                        ableton.send_command("set_track_arm", {"track_index": track_idx, "arm": True})
                    except:
                        pass
            
            # Optimized: Set position
            try:
                ableton.send_command("set_playhead_position", {"bar": start_bar, "beat": 0})
            except:
                pass
            time.sleep(0.1)  # Minimal delay
            
            # Start recording and playback (these must be sequential)
            ableton.send_command("start_recording", {})
            time.sleep(0.2)
            ableton.send_command("start_playback", {})
            time.sleep(0.2)
            
            # Trigger scenes
            for scene_idx, bars in zip(scene_sequence, scene_bars):
                ableton.send_command("trigger_scene", {"scene_index": scene_idx})
                # Non-blocking: Don't wait for full scene, just trigger and continue
                # The recording will capture everything
                time.sleep(0.1)  # Just enough to ensure command is processed
            
            # Wait for all scenes to complete
            total_time = secs_per_bar * sum(scene_bars) * 0.9
            time.sleep(total_time + 0.5)
            
            # Stop
            ableton.send_command("stop_recording", {})
            time.sleep(0.2)
            ableton.send_command("stop_playback", {})
            
            # Disarm
            _batch_arm_tracks(ableton, all_relevant_tracks, arm=False)
            
            return json.dumps({
                "status": "success",
                "scenes_captured": len(scene_sequence),
                "total_bars": sum(scene_bars),
                "parallel_arming": parallel_arming,
                "capture_method": "parallel"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in parallel capture: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # LIGHTWEIGHT CAPTURE (Minimal overhead, fast execution)
    # =========================================================================

    @mcp.tool()
    def capture_scenes_lightweight(
        ctx: Context,
        scene_sequence: List[int],
        scene_bars: List[int],
        start_bar: int = 0,
        minimal_logging: bool = True,
        no_locators: bool = True,
        no_metronome: bool = True,
    ) -> str:
        """
        Ultra-lightweight capture with minimal overhead.
        
        Perfect for:
        - Quick tests
        - Iterative capture
        - High-frequency capture operations
        - Systems with limited resources
        
        Parameters:
        - scene_sequence: List of scene indices
        - scene_bars: List of bar lengths
        - start_bar: Starting bar (default: 0)
        - minimal_logging: Suppress most logging (default: True)
        - no_locators: Skip locator creation (default: True)
        - no_metronome: Skip metronome (default: True)
        
        Returns: JSON with minimal data
        """
        try:
            import time as time_mod
            
            if len(scene_sequence) != len(scene_bars):
                return json.dumps({"status": "error", "message": "Length mismatch"}, indent=2)
            
            if len(scene_sequence) == 0:
                return json.dumps({"status": "success", "scenes_captured": 0}, indent=2)
            
            ableton = get_ableton_connection()
            bpm = _cached_get_tempo(ableton)
            secs_per_bar = (60.0 / bpm) * 4
            
            # Use cached scene track info
            all_relevant_tracks = _get_all_scene_track_indices(ableton, scene_sequence)
            
            # Fast arming (no error checking, no delays)
            for track_idx in all_relevant_tracks:
                try:
                    ableton.send_command("set_track_arm", {"track_index": track_idx, "arm": True})
                except:
                    pass
            
            # Set position
            try:
                ableton.send_command("set_playhead_position", {"bar": start_bar, "beat": 0})
            except:
                pass
            
            # Start
            ableton.send_command("start_recording", {})
            ableton.send_command("start_playback", {})
            time.sleep(0.1)
            
            # Trigger scenes quickly
            for scene_idx in scene_sequence:
                ableton.send_command("trigger_scene", {"scene_index": scene_idx})
                time.sleep(0.05)  # Minimal delay
            
            # Wait
            total_time = secs_per_bar * sum(scene_bars) * 0.95
            time.sleep(total_time)
            
            # Stop
            ableton.send_command("stop_recording", {})
            ableton.send_command("stop_playback", {})
            
            # Disarm
            for track_idx in all_relevant_tracks:
                try:
                    ableton.send_command("set_track_arm", {"track_index": track_idx, "arm": False})
                except:
                    pass
            
            return json.dumps({
                "status": "success",
                "scenes_captured": len(scene_sequence),
                "total_bars": sum(scene_bars),
                "capture_method": "lightweight"
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)[:100]}, indent=2)

    # =========================================================================
    # CAPTURE WITH PROGRESS CALLBACKS (For long operations)
    # =========================================================================

    @mcp.tool()
    def capture_scenes_with_progress(
        ctx: Context,
        scene_sequence: List[int],
        scene_bars: List[int],
        start_bar: int = 0,
        progress_interval_bars: int = 4,
    ) -> str:
        """
        Capture scenes with progress updates at regular intervals.
        
        This is useful for:
        - Long captures (progress feedback)
        - UI integration (progress bars)
        - Timeout management (check if still alive)
        
        Parameters:
        - scene_sequence: List of scene indices
        - scene_bars: List of bar lengths
        - start_bar: Starting bar (default: 0)
        - progress_interval_bars: Report progress every N bars (default: 4)
        
        Returns: JSON with progress updates throughout
        """
        try:
            import time as time_mod
            
            if len(scene_sequence) != len(scene_bars):
                return json.dumps({"status": "error", "message": "Length mismatch"}, indent=2)
            
            ableton = get_ableton_connection()
            bpm = _cached_get_tempo(ableton)
            secs_per_bar = (60.0 / bpm) * 4
            
            # Get relevant tracks
            all_relevant_tracks = _get_all_scene_track_indices(ableton, scene_sequence)
            _batch_arm_tracks(ableton, all_relevant_tracks, arm=True)
            
            # Set position
            try:
                ableton.send_command("set_playhead_position", {"bar": start_bar, "beat": 0})
            except:
                pass
            
            # Start
            ableton.send_command("start_recording", {})
            time.sleep(0.3)
            ableton.send_command("start_playback", {})
            time.sleep(0.3)
            
            # Trigger scenes with progress
            scenes_captured = 0
            current_bar = start_bar
            progress_updates = [{"status": "starting", "bar": current_bar, "timestamp": time_mod.time()}]
            
            for i, (scene_idx, bars) in enumerate(zip(scene_sequence, scene_bars)):
                ableton.send_command("trigger_scene", {"scene_index": scene_idx})
                scenes_captured += 1
                
                # Report progress at intervals
                bars_elapsed = current_bar - start_bar
                if progress_interval_bars > 0 and bars_elapsed % progress_interval_bars == 0:
                    progress = (current_bar - start_bar) / (sum(scene_bars) - bars) * 100
                    progress_updates.append({
                        "status": "progress",
                        "bar": current_bar,
                        "scene": i,
                        "percent_complete": f"{progress:.1f}%",
                        "timestamp": time_mod.time()
                    })
                
                current_bar += bars
                timer = AdaptiveTimer(bpm)
                timer.wait_for_bars(bars, safety_factor=0.9)
            
            # Final progress
            progress_updates.append({
                "status": "completing",
                "bar": current_bar,
                "percent_complete": "100%",
                "timestamp": time_mod.time()
            })
            
            # Stop
            time.sleep(0.5)
            ableton.send_command("stop_recording", {})
            time.sleep(0.3)
            ableton.send_command("stop_playback", {})
            _batch_arm_tracks(ableton, all_relevant_tracks, arm=False)
            
            progress_updates.append({
                "status": "complete",
                "scenes_captured": scenes_captured,
                "total_bars": sum(scene_bars),
                "timestamp": time_mod.time()
            })
            
            return json.dumps({
                "status": "success",
                "scenes_captured": scenes_captured,
                "total_bars": sum(scene_bars),
                "progress_updates": progress_updates,
                "capture_method": "with_progress"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in progress capture: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # PERFORMANCE BENCHMARK TOOL
    # =========================================================================

    @mcp.tool()
    def benchmark_capture_performance(
        ctx: Context,
        num_scenes: int = 5,
        bars_per_scene: int = 8,
        num_iterations: int = 3,
    ) -> str:
        """
        Benchmark capture performance to measure overhead.
        
        This runs multiple test captures and reports:
        - Execution time
        - Throughput (scenes/second)
        - Command processing time
        - Memory usage (if available)
        
        Parameters:
        - num_scenes: Number of scenes to test with (default: 5)
        - bars_per_scene: Bars per scene (default: 8)
        - num_iterations: Number of test runs (default: 3)
        
        Returns: JSON with benchmark results
        """
        try:
            import time as time_mod
            
            ableton = get_ableton_connection()
            bpm = _cached_get_tempo(ableton)
            secs_per_bar = (60.0 / bpm) * 4
            
            results = []
            
            for iteration in range(num_iterations):
                start_time = time_mod.time()
                
                # Get available scenes
                try:
                    all_scenes = ableton.send_command("get_all_scenes", {})
                    available_scenes = [s.get("index", i) for i, s in enumerate(all_scenes.get("scenes", []))]
                except:
                    available_scenes = list(range(num_scenes))
                
                # Use first N scenes
                scene_sequence = available_scenes[:num_scenes]
                scene_bars = [bars_per_scene] * num_scenes
                
                # Get relevant tracks
                all_relevant_tracks = _get_all_scene_track_indices(ableton, scene_sequence)
                
                # Quick capture
                _batch_arm_tracks(ableton, all_relevant_tracks, arm=True)
                
                try:
                    ableton.send_command("set_playhead_position", {"bar": 0, "beat": 0})
                except:
                    pass
                
                ableton.send_command("start_recording", {})
                time.sleep(0.2)
                ableton.send_command("start_playback", {})
                time.sleep(0.2)
                
                for scene_idx in scene_sequence:
                    ableton.send_command("trigger_scene", {"scene_index": scene_idx})
                    time.sleep(0.05)
                
                # Minimal wait
                minimal_wait = secs_per_bar * num_scenes * bars_per_scene * 0.5
                time.sleep(minimal_wait)
                
                ableton.send_command("stop_recording", {})
                time.sleep(0.2)
                ableton.send_command("stop_playback", {})
                _batch_arm_tracks(ableton, all_relevant_tracks, arm=False)
                
                elapsed = time_mod.time() - start_time
                
                results.append({
                    "iteration": iteration + 1,
                    "scenes": num_scenes,
                    "bars": num_scenes * bars_per_scene,
                    "elapsed_seconds": elapsed,
                    "scenes_per_second": num_scenes / elapsed if elapsed > 0 else 0
                })
                
                # Small delay between iterations
                time.sleep(0.5)
            
            # Calculate averages
            total_elapsed = sum(r["elapsed_seconds"] for r in results)
            avg_scenes_per_sec = sum(r["scenes_per_second"] for r in results) / len(results) if results else 0
            
            return json.dumps({
                "status": "success",
                "benchmarks": results,
                "summary": {
                    "iterations": num_iterations,
                    "scenes_per_iteration": num_scenes,
                    "bars_per_iteration": num_scenes * bars_per_scene,
                    "total_elapsed_seconds": total_elapsed,
                    "average_elapsed_seconds": total_elapsed / len(results) if results else 0,
                    "average_scenes_per_second": avg_scenes_per_sec,
                    "bpm": bpm
                }
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in benchmark: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # CLEAR CACHE TOOL
    # =========================================================================

    @mcp.tool()
    def clear_arrangement_cache(ctx: Context) -> str:
        """
        Clear all cached data for arrangement tools.
        
        Use this if:
        - Session has changed significantly
        - Cache might be stale
        - Testing cache behavior
        - Memory optimization
        
        Returns: JSON with cache status
        """
        try:
            _ableton_cache.clear()
            return json.dumps({
                "status": "success",
                "message": "Arrangement tool cache cleared"
            }, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
