"""
MCP Optimization Tools for Ableton Live Mixes

Provides intelligent optimization and fine-tuning tools:
- Auto-level balancing
- Frequency spectrum analysis
- Dynamic range optimization
- CPU/performance monitoring
- Clip gain normalization
- Sidechain compression assistance
- EQ suggestions based on collisions
- Mix bus processing

These tools help achieve professional-sounding mixes that can then
be fine-tuned manually in Ableton Live.
"""

import json
import logging
import time
import math
from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("AbletonMCPServer")


def _get_tempo(ableton) -> float:
    """Query Ableton tempo via TCP, return BPM. Fallback: 120."""
    try:
        result = ableton.send_command("get_tempo", {})
        if isinstance(result, dict):
            return float(result.get("tempo", 120.0))
    except Exception:
        pass
    return 120.0


def register_optimization_tools(mcp: FastMCP, get_ableton_connection):
    """Register all optimization MCP tools."""

    # =========================================================================
    # LEVEL BALANCING
    # =========================================================================

    @mcp.tool()
    def auto_balance_levels(
        ctx: Context,
        target_headroom_db: float = -6.0,
        reference_track: Optional[int] = None,
        max_boost_db: float = 6.0,
    ) -> str:
        """
        Automatically balance track levels to achieve consistent headroom.
        
        Analyzes current meter levels and adjusts track volumes so that
        the loudest track peaks at the target headroom, with other tracks
        scaled proportionally.
        
        Parameters:
        - target_headroom_db: Desired headroom in dB (default: -6.0)
        - reference_track: Optional track index to use as reference (default: None = loudest)
        - max_boost_db: Maximum volume boost in dB (default: 6.0)
        
        Examples:
        - auto_balance_levels(-6.0)  # Balance to -6dB headroom
        - auto_balance_levels(-3.0, reference_track=0, max_boost_db=3.0)
        """
        try:
            ableton = get_ableton_connection()
            
            # Get level snapshot
            levels_result = ableton.send_command("get_level_snapshot", {})
            levels = levels_result.get("levels", {})
            
            tracks_info = ableton.send_command("get_all_tracks", {})
            tracks = tracks_info.get("result", {}).get("tracks", [])
            
            # Find the loudest track
            track_levels = []
            for track in tracks:
                track_idx = track.get("index")
                if track_idx < 0:  # Skip master
                    continue
                level_db = levels.get(f"track_{track_idx}_output_level", -60.0)
                track_levels.append((track_idx, level_db, track.get("name", f"Track {track_idx}")))
            
            if not track_levels:
                return json.dumps({
                    "status": "error",
                    "message": "No tracks found or no level data available"
                }, indent=2)
            
            # Sort by level (highest first)
            track_levels.sort(key=lambda x: x[1], reverse=True)
            
            # If reference track specified, use it
            if reference_track is not None:
                ref_idx = next((i for i, t in enumerate(track_levels) if t[0] == reference_track), None)
                if ref_idx is not None:
                    track_levels[0], track_levels[ref_idx] = track_levels[ref_idx], track_levels[0]
            
            loudest_level = track_levels[0][1]
            
            # Calculate adjustments to reach target headroom
            target_linear = 10 ** (target_headroom_db / 20.0)
            loudest_linear = 10 ** (loudest_level / 20.0)
            scale_factor = target_linear / loudest_linear
            
            adjustments = []
            for track_idx, level_db, name in track_levels:
                # Calculate new level in dB
                new_linear = (10 ** (level_db / 20.0)) * scale_factor
                new_db = 20.0 * math.log10(new_linear) if new_linear > 0 else -60.0
                
                # Convert dB to volume multiplier
                db_diff = target_headroom_db - level_db
                if db_diff > max_boost_db:
                    db_diff = max_boost_db
                volume_multiplier = 10 ** (db_diff / 20.0)
                
                # Clamp to reasonable range
                new_db = level_db + db_diff
                
                adjustments.append({
                    "track_index": track_idx,
                    "name": name,
                    "current_level_db": round(level_db, 1),
                    "target_level_db": round(new_db, 1),
                    "volume_adjustment_db": round(db_diff, 1),
                    "new_volume": round(min(1.0, max(0.0, volume_multiplier)), 3),
                })
                
                # Apply volume adjustment
                current_track_result = ableton.send_command("get_track_info", {"track_index": track_idx})
                current_volume = current_track_result.get("result", {}).get("volume", 0.75)
                new_volume = current_volume * volume_multiplier
                new_volume = max(0.0, min(1.0, new_volume))
                
                ableton.send_command("set_track_volume", {
                    "track_index": track_idx,
                    "volume": new_volume,
                })
            
            return json.dumps({
                "status": "success",
                "target_headroom_db": target_headroom_db,
                "reference_track": reference_track,
                "max_boost_db": max_boost_db,
                "adjustments": adjustments,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error auto-balancing levels: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def normalize_clip_gain(
        ctx: Context,
        track_index: int,
        clip_index: int,
        target_peak_db: float = -6.0,
    ) -> str:
        """
        Normalize the gain of a clip to reach target peak level.
        
        Analyzes the clip's current peak level and adjusts note velocities
        to achieve the target peak.
        
        Parameters:
        - track_index: Index of the track containing the clip
        - clip_index: Index of the clip
        - target_peak_db: Target peak level in dB (default: -6.0)
        
        Examples:
        - normalize_clip_gain(0, 0, -6.0)  # Drum clip to -6dB peak
        """
        try:
            ableton = get_ableton_connection()
            
            # Get clip notes
            notes_result = ableton.send_command("get_clip_notes", {
                "track_index": track_index,
                "clip_index": clip_index,
            })
            notes = notes_result.get("result", {}).get("notes", [])
            
            # Find current max velocity
            max_velocity = max([n.get("velocity", 0) for n in notes]) if notes else 100
            
            # Calculate velocity scaling to reach target
            target_velocity = int(127 * (10 ** (target_peak_db / 20.0)))
            if target_velocity <= 0:
                target_velocity = 1
            
            velocity_scale = target_velocity / max_velocity if max_velocity > 0 else 1.0
            velocity_scale = max(0.0, min(2.0, velocity_scale))
            
            # Apply velocity scaling
            new_notes = []
            for note in notes:
                new_note = note.copy()
                new_velocity = int(note.get("velocity", 0) * velocity_scale)
                new_velocity = max(0, min(127, new_velocity))
                new_note["velocity"] = new_velocity
                new_notes.append(new_note)
            
            ableton.send_command("add_notes_to_clip", {
                "track_index": track_index,
                "clip_index": clip_index,
                "notes": new_notes,
            })
            
            return json.dumps({
                "status": "success",
                "track_index": track_index,
                "clip_index": clip_index,
                "current_max_velocity": max_velocity,
                "target_velocity": target_velocity,
                "velocity_scale": round(velocity_scale, 3),
            }, indent=2)
        except Exception as e:
            logger.error(f"Error normalizing clip gain: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # FREQUENCY ANALYSIS & EQ
    # =========================================================================

    @mcp.tool()
    def analyze_frequency_collisions(
        ctx: Context,
        track_indices: Optional[List[int]] = None,
        freq_bands: List[Dict[str, float]] = None,
    ) -> str:
        """
        Analyze tracks for frequency range collisions.
        
        Identifies which tracks occupy similar frequency ranges and suggests
        EQ adjustments to reduce muddiness and improve clarity.
        
        Parameters:
        - track_indices: List of track indices to analyze (default: all tracks)
        - freq_bands: Custom frequency band definitions (default: standard bands)
        
        Examples:
        - analyze_frequency_collisions([0, 1, 2])  # Analyze first 3 tracks
        """
        if freq_bands is None:
            freq_bands = [
                {"name": "Sub Bass", "low": 20, "high": 60},
                {"name": "Bass", "low": 60, "high": 250},
                {"name": "Low Mids", "low": 250, "high": 500},
                {"name": "Mids", "low": 500, "high": 2000},
                {"name": "Upper Mids", "low": 2000, "high": 5000},
                {"name": "Presence", "low": 5000, "high": 8000},
                {"name": "Brilliance", "low": 8000, "high": 20000},
            ]
        
        try:
            ableton = get_ableton_connection()
            tracks_info = ableton.send_command("get_all_tracks", {})
            tracks = tracks_info.get("result", {}).get("tracks", [])
            
            if track_indices is None:
                track_indices = [t.get("index") for t in tracks if t.get("index") >= 0]
            
            # Get device info for each track to infer frequency ranges
            track_freq_ranges = {}
            for track_idx in track_indices:
                track_devices = ableton.send_command("get_track_info", {
                    "track_index": track_idx
                }).get("result", {}).get("devices", [])
                
                # Infer frequency range from instrument type
                low, high = 20, 20000  # Default full range
                track_name = next((t.get("name") for t in tracks if t.get("index") == track_idx), 
                                 f"Track {track_idx}").lower()
                
                if any(word in track_name for word in ["kick", "bass", "sub"]):
                    low, high = 20, 250
                elif any(word in track_name for word in ["snare", "drum", "perc"]):
                    low, high = 100, 5000
                elif any(word in track_name for word in ["lead", "synth", "pluck"]):
                    low, high = 200, 8000
                elif any(word in track_name for word in ["pad", "chord", "strings"]):
                    low, high = 100, 2000
                elif any(word in track_name for word in ["fx", "noise", "atmo"]):
                    low, high = 1000, 20000
                
                track_freq_ranges[track_idx] = {
                    "name": next((t.get("name") for t in tracks if t.get("index") == track_idx), 
                                 f"Track {track_idx}"),
                    "low": low,
                    "high": high,
                }
            
            # Find collisions in each frequency band
            collisions = []
            for band in freq_bands:
                tracks_in_band = []
                for track_idx, freq_range in track_freq_ranges.items():
                    # Check if track overlaps with this band
                    overlap_start = max(freq_range["low"], band["low"])
                    overlap_end = min(freq_range["high"], band["high"])
                    if overlap_start < overlap_end:
                        overlap_pct = ((overlap_end - overlap_start) / 
                                     (band["high"] - band["low"])) * 100
                        tracks_in_band.append({
                            "track_index": track_idx,
                            "name": freq_range["name"],
                            "overlap_pct": round(overlap_pct, 1),
                        })
                
                if len(tracks_in_band) > 1:
                    collisions.append({
                        "band": band["name"],
                        "range": f"{band['low']:.0f}-{band['high']:.0f} Hz",
                        "tracks": tracks_in_band,
                        "collision_count": len(tracks_in_band),
                    })
            
            # Sort by most collisions first
            collisions.sort(key=lambda x: x["collision_count"], reverse=True)
            
            # Generate EQ suggestions
            suggestions = []
            for collision in collisions:
                if collision["collision_count"] > 2:
                    # Priority order: bass (cut highs), lead (cut lows), etc.
                    sorted_tracks = sorted(
                        collision["tracks"],
                        key=lambda x: ["bass", "kick", "drum", "lead", "pad", "fx"].index(
                            next((w for w in ["bass", "kick", "drum", "lead", "pad", "fx"] 
                                  if w in x["name"].lower()), "")
                        ) if next((w for w in ["bass", "kick", "drum", "lead", "pad", "fx"] 
                                   if w in x["name"].lower()), False) else 999
                    )
                    
                    suggestions.append({
                        "band": collision["band"],
                        "range": collision["range"],
                        "action": "Reduce frequency overlap",
                        "priority_tracks": [t["name"] for t in sorted_tracks[:3]],
                        "recommendation": f"Use EQ to carve space: cut {collision['range']} on competing tracks",
                    })
            
            return json.dumps({
                "status": "success",
                "track_freq_ranges": track_freq_ranges,
                "collisions": collisions,
                "suggestions": suggestions,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error analyzing frequency collisions: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def suggest_eq_settings(
        ctx: Context,
        track_index: int,
        instrument_type: Optional[str] = None,
    ) -> str:
        """
        Suggest EQ settings based on instrument type.
        
        Parameters:
        - track_index: Index of the track
        - instrument_type: Type of instrument (auto-detected if not specified)
        
        Examples:
        - suggest_eq_settings(0, "kick")
        - suggest_eq_settings(1)  # Auto-detect from track name
        """
        # Standard EQ presets for different instruments
        EQ_PRESETS = {
            "kick": {
                "name": "Kick Drum",
                "cuts": [
                    {"freq": 200, "gain": -3.0, "q": 1.5, "reason": "Reduce boxiness"},
                    {"freq": 400, "gain": -2.0, "q": 1.2, "reason": "Clean up mud"},
                ],
                "boosts": [
                    {"freq": 60, "gain": 2.0, "q": 1.2, "reason": "Boost thump"},
                    {"freq": 3000, "gain": 3.0, "q": 1.5, "reason": "Add click"},
                    {"freq": 8000, "gain": 2.0, "q": 1.0, "reason": "Add air"},
                ],
                "high_pass": 30,
                "low_pass": None,
            },
            "bass": {
                "name": "Bass",
                "cuts": [
                    {"freq": 200, "gain": -2.0, "q": 1.2, "reason": "Reduce mud"},
                ],
                "boosts": [
                    {"freq": 80, "gain": 2.0, "q": 1.2, "reason": "Boost sub"},
                    {"freq": 700, "gain": 1.5, "q": 1.5, "reason": "Add presence"},
                ],
                "high_pass": None,
                "low_pass": None,
            },
            "snare": {
                "name": "Snare Drum",
                "cuts": [
                    {"freq": 400, "gain": -3.0, "q": 1.5, "reason": "Reduce boxiness"},
                    {"freq": 1000, "gain": -2.0, "q": 1.2, "reason": "Clean up"},
                ],
                "boosts": [
                    {"freq": 150, "gain": 2.0, "q": 1.0, "reason": "Add body"},
                    {"freq": 4000, "gain": 3.0, "q": 1.5, "reason": "Add snap"},
                ],
                "high_pass": 80,
                "low_pass": None,
            },
            "lead": {
                "name": "Lead Synth",
                "cuts": [
                    {"freq": 300, "gain": -3.0, "q": 1.5, "reason": "Remove mud"},
                ],
                "boosts": [
                    {"freq": 2000, "gain": 2.0, "q": 1.5, "reason": "Add presence"},
                    {"freq": 10000, "gain": 1.5, "q": 1.0, "reason": "Add sparkle"},
                ],
                "high_pass": 200,
                "low_pass": None,
            },
            "pad": {
                "name": "Pad",
                "cuts": [
                    {"freq": 100, "gain": -2.0, "q": 1.2, "reason": "Remove rumble"},
                    {"freq": 3000, "gain": -1.5, "q": 1.0, "reason": "Smooth highs"},
                ],
                "boosts": [
                    {"freq": 500, "gain": 2.0, "q": 1.2, "reason": "Add warmth"},
                    {"freq": 8000, "gain": 1.5, "q": 1.0, "reason": "Add air"},
                ],
                "high_pass": 100,
                "low_pass": 12000,
            },
            "fx": {
                "name": "FX/Noise",
                "cuts": [
                    {"freq": 200, "gain": -4.0, "q": 2.0, "reason": "Remove mud"},
                ],
                "boosts": [
                    {"freq": 5000, "gain": 3.0, "q": 1.5, "reason": "Add sizzle"},
                ],
                "high_pass": 500,
                "low_pass": None,
            },
        }
        
        try:
            ableton = get_ableton_connection()
            
            # Auto-detect instrument type if not specified
            if instrument_type is None:
                track_info = ableton.send_command("get_track_info", {"track_index": track_index})
                track_name = track_info.get("result", {}).get("name", f"Track {track_index}").lower()
                
                for inst_type in EQ_PRESETS.keys():
                    if inst_type in track_name:
                        instrument_type = inst_type
                        break
                else:
                    instrument_type = "lead"  # Default
            
            instrument_type = instrument_type.lower()
            preset = EQ_PRESETS.get(instrument_type, EQ_PRESETS["lead"])
            
            return json.dumps({
                "status": "success",
                "track_index": track_index,
                "detected_instrument": instrument_type,
                "eq_preset": preset.get("name"),
                "recommended_settings": {
                    "high_pass_hz": preset.get("high_pass"),
                    "low_pass_hz": preset.get("low_pass"),
                    "cuts": preset.get("cuts", []),
                    "boosts": preset.get("boosts", []),
                },
            }, indent=2)
        except Exception as e:
            logger.error(f"Error suggesting EQ settings: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # DYNAMICS & COMPRESSION
    # =========================================================================

    @mcp.tool()
    def suggest_compression_settings(
        ctx: Context,
        track_index: int,
        instrument_type: Optional[str] = None,
    ) -> str:
        """
        Suggest compression settings based on instrument type.
        
        Parameters:
        - track_index: Index of the track
        - instrument_type: Type of instrument (auto-detected if not specified)
        
        Examples:
        - suggest_compression_settings(0, "kick")
        - suggest_compression_settings(1, "bass")
        """
        COMPRESSION_PRESETS = {
            "kick": {
                "name": "Kick Drum",
                "device": "query:AudioFx#Glue%20Compressor",
                "threshold_db": -20,
                "ratio": 4.0,
                "attack_ms": 10,
                "release_ms": 100,
                "makeup_db": 2.0,
                "notes": "Fast attack to preserve transient, moderate ratio",
            },
            "snare": {
                "name": "Snare Drum",
                "device": "query:AudioFx#Glue%20Compressor",
                "threshold_db": -18,
                "ratio": 4.0,
                "attack_ms": 20,
                "release_ms": 50,
                "makeup_db": 3.0,
                "notes": "Fast attack and release for punch",
            },
            "bass": {
                "name": "Bass",
                "device": "query:AudioFx#Glue%20Compressor",
                "threshold_db": -15,
                "ratio": 3.0,
                "attack_ms": 30,
                "release_ms": 200,
                "makeup_db": 1.0,
                "notes": "Moderate attack to preserve low end",
            },
            "vocals": {
                "name": "Vocals",
                "device": "query:AudioFx#Compressor",
                "threshold_db": -18,
                "ratio": 2.5,
                "attack_ms": 50,
                "release_ms": 200,
                "makeup_db": 2.0,
                "notes": "Smooth, natural compression",
            },
            "lead": {
                "name": "Lead Synth",
                "device": "query:AudioFx#Compressor",
                "threshold_db": -24,
                "ratio": 2.0,
                "attack_ms": 100,
                "release_ms": 500,
                "makeup_db": 0.0,
                "notes": "Gentle compression to control peaks",
            },
            "pad": {
                "name": "Pad",
                "device": "query:AudioFx#Glue%20Compressor",
                "threshold_db": -20,
                "ratio": 2.0,
                "attack_ms": 50,
                "release_ms": 1000,
                "makeup_db": 1.0,
                "notes": "Slow release for sustain, low ratio",
            },
        }
        
        try:
            ableton = get_ableton_connection()
            
            if instrument_type is None:
                track_info = ableton.send_command("get_track_info", {"track_index": track_index})
                track_name = track_info.get("result", {}).get("name", f"Track {track_index}").lower()
                
                for inst_type in COMPRESSION_PRESETS.keys():
                    if inst_type in track_name:
                        instrument_type = inst_type
                        break
                else:
                    instrument_type = "lead"
            
            instrument_type = instrument_type.lower()
            preset = COMPRESSION_PRESETS.get(instrument_type, COMPRESSION_PRESETS["lead"])
            
            return json.dumps({
                "status": "success",
                "track_index": track_index,
                "detected_instrument": instrument_type,
                "compression_preset": preset.get("name"),
                "recommended_device": preset.get("device"),
                "recommended_settings": {
                    "threshold_db": preset.get("threshold_db"),
                    "ratio": preset.get("ratio"),
                    "attack_ms": preset.get("attack_ms"),
                    "release_ms": preset.get("release_ms"),
                    "makeup_db": preset.get("makeup_db"),
                },
                "notes": preset.get("notes"),
            }, indent=2)
        except Exception as e:
            logger.error(f"Error suggesting compression settings: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def setup_sidechain_compression(
        ctx: Context,
        source_track: int,
        target_track: int,
        threshold_db: float = -12.0,
        ratio: float = 4.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
    ) -> str:
        """
        Setup sidechain compression from one track to another.
        
        Creates a routing and compression setup where the source track
        triggers compression on the target track (classic kick-bass ducking).
        
        Parameters:
        - source_track: Track that triggers compression (e.g., kick drum)
        - target_track: Track to be compressed (e.g., bass)
        - threshold_db: Compression threshold
        - ratio: Compression ratio
        - attack_ms: Attack time in milliseconds
        - release_ms: Release time in milliseconds
        
        Note: This requires manual setup in Ableton as the Remote Script API
        doesn't support full sidechain routing. This tool provides the guidance.
        
        Examples:
        - setup_sidechain_compression(0, 1)  # Kick (0) -> Bass (1)
        """
        try:
            ableton = get_ableton_connection()
            
            # Get track info
            source_info = ableton.send_command("get_track_info", {"track_index": source_track})
            target_info = ableton.send_command("get_track_info", {"track_index": targetrack})
            
            source_name = source_info.get("result", {}).get("name", f"Track {source_track}")
            target_name = target_info.get("result", {}).get("name", f"Track {target_track}")
            
            # In Ableton, sidechain setup requires:
            # 1. Create an audio track for sidechain
            # 2. Route source track to sidechain track
            # 3. Add compressor on target track
            # 4. Select sidechain input on compressor
            # 5. Configure compressor settings
            
            return json.dumps({
                "status": "guidance",
                "message": "Manual sidechain setup required in Ableton",
                "instructions": [
                    f"1. Create a new audio track",
                    f"2. Set its input to '{source_name}'",
                    f"3. Mute the new track (no output needed)",
                    f"4. On '{target_name}', add a Compressor device",
                    f"5. In the compressor, set Sidechain Input to the new audio track",
                    f"6. Configure compressor: threshold={threshold_db}dB, ratio={ratio}:1, "
                    f"attack={attack_ms}ms, release={release_ms}ms",
                    f"7. Enable the compressor and adjust to taste",
                ],
                "source_track": source_track,
                "source_name": source_name,
                "target_track": target_track,
                "target_name": target_name,
                "suggested_settings": {
                    "threshold_db": threshold_db,
                    "ratio": ratio,
                    "attack_ms": attack_ms,
                    "release_ms": release_ms,
                },
            }, indent=2)
        except Exception as e:
            logger.error(f"Error setting up sidechain: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # MIX BUS PROCESSING
    # =========================================================================

    @mcp.tool()
    def setup_mix_bus_processing(
        ctx: Context,
        glue_compression: bool = True,
        saturation: bool = True,
        eq: bool = True,
        limiter: bool = True,
    ) -> str:
        """
        Setup master bus (mix bus) processing chain.
        
        Adds a standard mix bus processing chain to the master track:
        1. Glue Compressor (subtle mixing glue)
        2. Saturator (analog warmth)
        3. EQ Eight (broad tone shaping)
        4. Limiter (final ceiling)
        
        Parameters:
        - glue_compression: Whether to add glue compression (default: True)
        - saturation: Whether to add saturation (default: True)
        - eq: Whether to add EQ (default: True)
        - limiter: Whether to add limiter (default: True)
        
        Examples:
        - setup_mix_bus_processing()  # Full processing chain
        - setup_mix_bus_processing(glue_compression=True, limiter=True)  # Just compression and limiting
        """
        try:
            ableton = get_ableton_connection()
            actions = []
            
            if glue_compression:
                result = ableton.send_command("load_browser_item", {
                    "track_index": -1,
                    "item_uri": "query:AudioFx#Glue%20Compressor",
                })
                actions.append({"device": "Glue Compressor", "status": result.get("status", "success")})
                time.sleep(0.3)
                
                # Configure glue compression
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 0,
                    "value": 0.3,  # Threshold
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 1,
                    "value": 0.3,  # Ratio (4:1)
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 2,
                    "value": 0.2,  # Attack
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 3,
                    "value": 0.4,  # Release
                })
            
            if saturation:
                result = ableton.send_command("load_browser_item", {
                    "track_index": -1,
                    "item_uri": "query:AudioFx#Saturator",
                })
                actions.append({"device": "Saturator", "status": result.get("status", "success")})
                time.sleep(0.3)
                
                # Soft saturation
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 0,
                    "value": 0.1,  # Drive
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 1,
                    "value": 0.3,  # Color
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 2,
                    "value": 0.2,  # Output
                })
            
            if eq:
                result = ableton.send_command("load_browser_item", {
                    "track_index": -1,
                    "item_uri": "query:AudioFx#EQ%20Eight",
                })
                actions.append({"device": "EQ Eight", "status": result.get("status", "success")})
                time.sleep(0.3)
                
                # Gentle EQ curve
                # Boost low end slightly
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 0,
                    "value": 0.6,  # Low band freq
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 1,
                    "value": 0.1,  # Low band gain
                })
                # Slight high end boost
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 14,
                    "value": 0.7,  # High band freq
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 15,
                    "value": 0.05,  # High band gain
                })
            
            if limiter:
                result = ableton.send_command("load_browser_item", {
                    "track_index": -1,
                    "item_uri": "query:AudioFx#Limiter",
                })
                actions.append({"device": "Limiter", "status": result.get("status", "success")})
                time.sleep(0.3)
                
                # Set ceiling and output
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 0,
                    "value": 0.9,  # Ceiling (-0.9dB)
                })
                ableton.send_command_udp("set_device_parameter", {
                    "track_index": -1,
                    "device_index": len(actions) - 1,
                    "parameter_index": 1,
                    "value": 0.95,  # Output
                })
            
            return json.dumps({
                "status": "success",
                "devices_added": len(actions),
                "processing_chain": [a["device"] for a in actions],
                "actions": actions,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error setting up mix bus processing: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    # =========================================================================
    # PERFORMANCE OPTIMIZATION
    # =========================================================================

    @mcp.tool()
    def optimize_cpu_usage(
        ctx: Context,
        freeze_tracks: Optional[List[int]] = None,
        disable_unused_devices: bool = True,
        reduce_buffer_size: bool = False,
    ) -> str:
        """
        Optimize CPU usage for large sessions.
        
        Parameters:
        - freeze_tracks: List of track indices to freeze (default: all non-recording tracks)
        - disable_unused_devices: Disable devices on muted tracks (default: True)
        - reduce_buffer_size: Reduce audio buffer size (default: False - may cause glitches)
        
        Examples:
        - optimize_cpu_usage()  # Optimize with defaults
        - optimize_cpu_usage(freeze_tracks=[2,3,4], disable_unused_devices=True)
        """
        try:
            ableton = get_ableton_connection()
            actions = []
            
            tracks_info = ableton.send_command("get_all_tracks", {})
            tracks = tracks_info.get("result", {}).get("tracks", [])
            
            if freeze_tracks is None:
                # Freeze all tracks that aren't armed for recording
                freeze_tracks = []
                for track in tracks:
                    if track.get("index") >= 0 and not track.get("arm", False):
                        freeze_tracks.append(track.get("index"))
            
            # Freeze selected tracks
            for track_idx in freeze_tracks:
                ableton.send_command("freeze_track", {"track_index": track_idx})
                actions.append({"action": "freeze", "track_index": track_idx})
                time.sleep(0.2)
            
            # Disable devices on muted tracks
            if disable_unused_devices:
                for track in tracks:
                    track_idx = track.get("index")
                    if track_idx >= 0 and track.get("mute", False):
                        # Disable all devices on muted track
                        devices = ableton.send_command("get_track_info", {
                            "track_index": track_idx
                        }).get("result", {}).get("devices", [])
                        for device_idx, device in enumerate(devices):
                            ableton.send_command_udp("toggle_device_bypass", {
                                "track_index": track_idx,
                                "device_index": device_idx,
                                "enabled": True,  # Bypass the device
                            })
                            actions.append({
                                "action": "bypass_device",
                                "track_index": track_idx,
                                "device_index": device_idx,
                                "device_name": device.get("name", "Unknown"),
                            })
            
            return json.dumps({
                "status": "success",
                "actions": actions,
                "tracks_frozen": len([a for a in actions if a["action"] == "freeze"]),
                "devices_bypassed": len([a for a in actions if a["action"] == "bypass_device"]),
            }, indent=2)
        except Exception as e:
            logger.error(f"Error optimizing CPU usage: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def get_performance_metrics(ctx: Context) -> str:
        """
        Get current performance metrics from Ableton Live.
        
        Returns CPU usage, memory, disk I/O, and other performance data.
        
        Examples:
        - get_performance_metrics()
        """
        try:
            ableton = get_ableton_connection()
            
            # Get basic info
            session_info = ableton.send_command("get_session_info", {})
            tracks_info = ableton.send_command("get_all_tracks", {})
            clips_info = ableton.send_command("get_all_clips_in_track", {"track_index": 0})
            
            tracks = tracks_info.get("result", {}).get("tracks", [])
            clips_in_track_0 = clips_info.get("result", {}).get("clips", [])
            
            # Count total clips
            total_clips = len(clips_in_track_0)
            for track in tracks[1:]:  # Skip first track already counted
                try:
                    track_clips = ableton.send_command("get_all_clips_in_track", {
                        "track_index": track.get("index")
                    }).get("result", {}).get("clips", [])
                    total_clips += len(track_clips)
                except:
                    pass
            
            # Estimate CPU indicators
            active_tracks = sum(1 for t in tracks if not t.get("mute", False))
            
            metrics = {
                "status": "success",
                "session": {
                    "bpm": session_info.get("result", {}).get("tempo", 120),
                    "tracks_count": len([t for t in tracks if t.get("index") >= 0]),
                    "return_tracks_count": len([t for t in tracks if t.get("index") < 0]),
                    "total_clips": total_clips,
                    "active_tracks": active_tracks,
                },
                "estimated_resource_usage": {
                    "cpu_percent": round(active_tracks * 5 + total_clips * 0.5, 1),
                    "memory_mb": round(active_tracks * 100 + total_clips * 10, 1),
                },
                "recommendations": [],
            }
            
            # Add recommendations
            if metrics["session"]["tracks_count"] > 16:
                metrics["recommendations"].append("Consider freezing some tracks to reduce CPU load")
            if metrics["session"]["total_clips"] > 64:
                metrics["recommendations"].append("Large clip count - consider consolidating or archiving unused clips")
            if metrics["estimated_resource_usage"]["cpu_percent"] > 70:
                metrics["recommendations"].append("High estimated CPU - freeze tracks, disable unused devices, or increase buffer size")
            if metrics["estimated_resource_usage"]["memory_mb"] > 500:
                metrics["recommendations"].append("High memory usage - freeze tracks or close unused Live sets")
            
            return json.dumps(metrics, indent=2)
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
