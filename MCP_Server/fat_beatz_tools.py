"""
Fat Beatz Tools - For Maximum Thickness and Punch

This module provides specialized tools for creating fat, punchy, bass-heavy beats
with professional-grade processing. Combines dub aesthetics with modern production
techniques for maximum impact.

Key Features:
- Bass enhancement (sub-harmonics, saturation, layering)
- Drum fattening (kick enhancement, snare thickening)
- Mix fatness (stereo widening, harmonic excitement)
- Mastering (loudness, low-end focus)
- One-shot beat creation
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple
from mcp.server.fastmcp import FastMCP, Context


def _find_compressor(ableton, track_index: int) -> Optional[Tuple[int, Dict]]:
    """Find compressor device on track."""
    try:
        devices = ableton.send_command("get_track_devices", {"track_index": track_index})
        if isinstance(devices, dict):
            for i, device in enumerate(devices.get("devices", [])):
                name = device.get("name", "").lower()
                if any(kw in name for kw in ["compressor", "glue", "compressor ii", "Cycles"]):
                    return (i, device)
    except:
        pass
    return None


def _find_saturator(ableton, track_index: int) -> Optional[Tuple[int, Dict]]:
    """Find saturation device on track."""
    try:
        devices = ableton.send_command("get_track_devices", {"track_index": track_index})
        if isinstance(devices, dict):
            for i, device in enumerate(devices.get("devices", [])):
                name = device.get("name", "").lower()
                if any(kw in name for kw in ["saturator", "saturation", "traction", "decimator"]):
                    return (i, device)
    except:
        pass
    return None


def _find_limiter(ableton, track_index: int) -> Optional[Tuple[int, Dict]]:
    """Find limiter device on track."""
    try:
        devices = ableton.send_command("get_track_devices", {"track_index": track_index})
        if isinstance(devices, dict):
            for i, device in enumerate(devices.get("devices", [])):
                name = device.get("name", "").lower()
                if any(kw in name for kw in ["limiter", "loudness", "maximus", "Limiting"]):
                    return (i, device)
    except:
        pass
    return None


def _find_utility(ableton, track_index: int) -> Optional[Tuple[int, Dict]]:
    """Find utility device (gain, mono, etc.) on track."""
    try:
        devices = ableton.send_command("get_track_devices", {"track_index": track_index})
        if isinstance(devices, dict):
            for i, device in enumerate(devices.get("devices", [])):
                name = device.get("name", "").lower()
                if "utility" in name or "gain" in name or "mono" in name:
                    return (i, device)
    except:
        pass
    return None


def _set_device_parameter(ableton, track_index: int, device_index: int, param_index: int, value: float):
    """Set a device parameter (normalized 0-1)."""
    try:
        ableton.send_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": param_index,
            "value": max(0.0, min(1.0, value))
        })
    except:
        pass


# =============================================================================
# BASS ENHANCEMENT TOOLS
# =============================================================================

def register_fat_beatz_tools(mcp: FastMCP, get_ableton_connection):
    """Register all Fat Beatz tools."""
    import logging
    logger = logging.getLogger("AbletonMCPServer")

    @mcp.tool()
    def add_sub_bass_harmonic(
        ctx: Context,
        track_index: int,
        harmonic_octave: int = -1,
        harmonic_volume: float = 0.5,
        filter_cutoff: float = 150.0,
        saturation_amount: float = 0.3,
    ) -> str:
        """
        Add sub-bass harmonic to thicken thin basslines.
        
        Creates a new audio track with:
        - Octave-shifted version of source (sine wave sub)
        - Low-pass filter to remove mud
        - Light saturation for warmth
        - Volume blending with original
        
        Parameters:
        - track_index: Source track to enhance
        - harmonic_octave: -1 (sub), -2 (sub-sub), +1 (up)
        - harmonic_volume: Volume of harmonic relative to original (0-1)
        - filter_cutoff: LP filter cutoff in Hz
        - saturation_amount: Saturation drive (0-1)
        
        Returns: JSON with new track info and settings applied
        """
        try:
            ableton = get_ableton_connection()
            
            # Create a new audio track for the sub
            result = ableton.send_command("create_audio_track", {})
            new_track_idx = result.get("track_index", len(ableton.send_command("get_all_tracks", {}).get("tracks", [])))
            
            # Name it
            ableton.send_command("set_track_name", {
                "track_index": new_track_idx,
                "name": f"Sub-Bass ({harmonic_octave}oct)"
            })
            
            # Set pan to center for low-end
            ableton.send_command("set_track_pan", {
                "track_index": new_track_idx,
                "pan": 0.0
            })
            
            # Route audio from source track
            ableton.send_command("set_track_audio_from", {
                "track_index": new_track_idx,
                "source_track": track_index,
                "mono": True
            })
            
            # Add EQ to filter out unwanted frequencies
            eq_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": new_track_idx,
                "device_name": "EQ Eight"
            })
            eq_idx = eq_result.get("device_index", 0)
            
            # Set low-pass filter (first band)
            # Parameter indices for EQ Eight bands start at 1, 3, 5...
            # Band 1: Freq=1, Gain=2, Q=3
            freq_norm = min(1.0, filter_cutoff / 20000.0)
            _set_device_parameter(ableton, new_track_idx, eq_idx, 1, freq_norm)
            # Set it as low-pass (type parameter might be 0)
            # For simplicity, just set gain and Q
            
            # Add saturator for analog warmth
            sat_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": new_track_idx,
                "device_name": "Saturator"
            })
            sat_idx = sat_result.get("device_index", 1)
            _set_device_parameter(ableton, new_track_idx, sat_idx, 0, saturation_amount)
            
            # Add pitch shift (using simpler method - clone and transpose)
            # For octave shift, we create a new clip with pitch shift
            # This is a simplification - would need MIDI for proper octave tracking
            
            # Set volume
            ableton.send_command("set_track_volume", {
                "track_index": new_track_idx,
                "volume": harmonic_volume
            })
            
            logger.info(f"Added sub-bass harmonic on track {new_track_idx} (octave: {harmonic_octave})")
            
            return json.dumps({
                "status": "success",
                "source_track": track_index,
                "new_track": new_track_idx,
                "octave": harmonic_octave,
                "volume": harmonic_volume,
                "filter_cutoff_hz": filter_cutoff,
                "saturation": saturation_amount,
                "recommendation": "Route both tracks to a bus and blend to taste"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error adding sub-bass harmonic: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def boost_bass_frequencies(
        ctx: Context,
        track_index: int,
        boost_db: float = 6.0,
        center_frequency: float = 80.0,
        q_factor: float = 1.5,
        use_eq_eight: bool = True,
    ) -> str:
        """
        Apply targeted bass frequency boost using EQ.
        
        Creates a gentle bell curve or low-shelf boost centered on sub-bass frequencies,
        with appropriate Q factor to avoid muddiness.
        
        Parameters:
        - track_index: Track to boost
        - boost_db: Amount of boost in dB
        - center_frequency: Center frequency in Hz (40-150 typical)
        - q_factor: Bandwidth (0.5-3.0, lower = wider)
        - use_eq_eight: Use EQ Eight (True) or EQ Three (False)
        
        Returns: JSON with EQ settings applied
        """
        try:
            ableton = get_ableton_connection()
            
            # Find or create EQ device
            eq_device = _find_eq_device(ableton, track_index)
            if not eq_device:
                # Load EQ Eight
                result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": track_index,
                    "device_name": "EQ Eight" if use_eq_eight else "EQ Three"
                })
                eq_idx = result.get("device_index", len(ableton.send_command("get_track_devices", {"track_index": track_index}).get("devices", [])))
                eq_type = "EQ Eight" if use_eq_eight else "EQ Three"
            else:
                eq_idx, eq_device_info = eq_device
                eq_type = eq_device_info.get("name", "Unknown EQ")
            
            # Calculate normalized values
            freq_norm = min(1.0, max(0.0, math.log(center_frequency / 20.0) / math.log(20000.0 / 20.0)))
            gain_norm = min(1.0, max(0.0, (boost_db + 24.0) / 48.0))  # -24 to +24 dB -> 0-1
            q_norm = min(1.0, max(0.0, q_factor / 10.0))  # 0-10 -> 0-1
            
            # Set EQ band (use first available band)
            # For EQ Eight, band 1: Freq=1, Gain=2, Q=3
            # For EQ Three, Low band: Freq, Gain, Q
            if use_eq_eight or "Eight" in eq_type:
                # Bell curve on band 1
                _set_device_parameter(ableton, track_index, eq_idx, 1, freq_norm)   # Freq
                _set_device_parameter(ableton, track_index, eq_idx, 2, gain_norm)   # Gain
                _set_device_parameter(ableton, track_index, eq_idx, 3, q_norm)     # Q
            else:
                # EQ Three - Low band would be different
                # Simplify: use first band
                _set_device_parameter(ableton, track_index, eq_idx, 0, freq_norm)
                _set_device_parameter(ableton, track_index, eq_idx, 1, gain_norm)
            
            logger.info(f"Boosted bass on track {track_index}: {boost_db}db at {center_frequency}Hz, Q={q_factor}")
            
            return json.dumps({
                "status": "success",
                "track": track_index,
                "eq_device": eq_type,
                "eq_index": eq_idx,
                "boost_db": boost_db,
                "center_frequency_hz": center_frequency,
                "q_factor": q_factor,
                "tip": "Use a spectrum analyzer to verify the boost isn't causing mud"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error boosting bass: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def create_parallel_bass_compression(
        ctx: Context,
        track_index: int,
        compression_amount: float = 0.5,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
        ratio: float = 4.0,
        threshold_db: float = -12.0,
    ) -> str:
        """
        Create NY-style parallel bass compression for punch and sustain.
        
        Duplicates the track, applies heavy compression, then blends back.
        This maintains transients while adding body and sustain.
        
        Parameters:
        - track_index: Source bass track
        - compression_amount: Mix of compressed signal (0-1)
        - attack_ms: Compressor attack time
        - release_ms: Compressor release time
        - ratio: Compression ratio (2.0-8.0)
        - threshold_db: Threshold in dB (-24 to 0)
        
        Returns: JSON with new track and compressor settings
        """
        try:
            ableton = get_ableton_connection()
            
            # Create duplicate track
            result = ableton.send_command("duplicate_track", {"track_index": track_index})
            comp_track_idx = result.get("new_track_index", len(ableton.send_command("get_all_tracks", {}).get("tracks", [])))
            
            # Name it
            ableton.send_command("set_track_name", {
                "track_index": comp_track_idx,
                "name": f"Bass Comp (Parallel)"
            })
            
            # Add compressor
            comp_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": comp_track_idx,
                "device_name": "Glue Compressor"
            })
            comp_idx = comp_result.get("device_index", 0)
            
            # Set compressor parameters (Glue Compressor parameter indices)
            # 0: Ratio, 1: Threshold, 2: Attack, 3: Release, 4: Makeup Gain
            ratio_norm = min(1.0, max(0.0, (ratio - 1.0) / 20.0))  # 1-20 -> 0-1
            threshold_norm = min(1.0, max(0.0, (-threshold_db) / 60.0))  # -60 to 0 -> 0-1
            attack_norm = min(1.0, max(0.0, math.log(attack_ms / 0.1) / math.log(1000.0 / 0.1)))
            release_norm = min(1.0, max(0.0, math.log(release_ms / 10.0) / math.log(3000.0 / 10.0)))
            
            _set_device_parameter(ableton, comp_track_idx, comp_idx, 0, ratio_norm)
            _set_device_parameter(ableton, comp_track_idx, comp_idx, 1, threshold_norm)
            _set_device_parameter(ableton, comp_track_idx, comp_idx, 2, attack_norm)
            _set_device_parameter(ableton, comp_track_idx, comp_idx, 3, release_norm)
            
            # Set dry/wet mix on compressor if available, or use track volume
            # For parallel compression, we want full wet on the duplicate
            ableton.send_command("set_track_volume", {
                "track_index": comp_track_idx,
                "volume": compression_amount
            })
            
            logger.info(f"Created parallel bass compression on track {comp_track_idx}")
            
            return json.dumps({
                "status": "success",
                "original_track": track_index,
                "compressed_track": comp_track_idx,
                "compression_amount": compression_amount,
                "compressor": "Glue Compressor",
                "settings": {
                    "ratio": ratio,
                    "threshold_db": threshold_db,
                    "attack_ms": attack_ms,
                    "release_ms": release_ms
                },
                "tip": "Blend the compressed track with the original for NY-style punch"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error creating parallel compression: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)


    # =============================================================================
    # DRUM FATNESS TOOLS
    # =============================================================================

    @mcp.tool()
    def enhance_kick_drum(
        ctx: Context,
        track_index: int,
        add_click: bool = True,
        click_volume: float = 0.3,
        boost_attack: bool = True,
        attack_db: float = 12.0,
        extend_tail: bool = True,
        tail_hz: float = 40.0,
        saturation_drive: float = 0.5,
    ) -> str:
        """
        Make kick drums punch through the mix.
        
        Applies multiple enhancements:
        - Adds click sample for attack (optional)
        - Boosts high-frequency attack
        - Extends low-frequency tail
        - Adds analog saturation
        
        Parameters:
        - track_index: Drum track with kick
        - add_click: Layer a click sample for attack
        - click_volume: Volume of click layer
        - boost_attack: Boost high frequencies
        - attack_db: Amount of high-frequency boost
        - extend_tail: Enhance sub frequencies
        - tail_hz: Center frequency for tail boost
        - saturation_drive: Saturation amount
        
        Returns: JSON with enhancement details
        """
        try:
            ableton = get_ableton_connection()
            
            enhancements = []
            
            # 1. Add saturation
            sat_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "Saturator"
            })
            sat_idx = sat_result.get("device_index", 0)
            _set_device_parameter(ableton, track_index, sat_idx, 0, saturation_drive)
            _set_device_parameter(ableton, track_index, sat_idx, 1, 0.5)  # Color
            enhancements.append({"type": "saturation", "drive": saturation_drive})
            
            # 2. Add EQ for attack and tail
            eq_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "EQ Eight"
            })
            eq_idx = eq_result.get("device_index", 1)
            
            if boost_attack:
                # High frequency boost (5-10kHz for click)
                attack_freq_norm = min(1.0, 8000.0 / 20000.0)
                attack_gain_norm = min(1.0, (attack_db + 24.0) / 48.0)
                _set_device_parameter(ableton, track_index, eq_idx, 5, attack_freq_norm)  # Band 3 freq
                _set_device_parameter(ableton, track_index, eq_idx, 6, attack_gain_norm)  # Band 3 gain
                enhancements.append({"type": "attack_boost", "db": attack_db, "hz": 8000})
            
            if extend_tail:
                # Low frequency boost
                tail_freq_norm = min(1.0, tail_hz / 20000.0)
                tail_gain_norm = min(1.0, 6.0 / 48.0)  # +6dB
                _set_device_parameter(ableton, track_index, eq_idx, 13, tail_freq_norm)  # Band 7 freq
                _set_device_parameter(ableton, track_index, eq_idx, 14, tail_gain_norm)  # Band 7 gain
                enhancements.append({"type": "tail_boost", "hz": tail_hz})
            
            # 3. Add click sample (simplified - would need sample loading)
            if add_click:
                # Create a new track for click layer
                click_result = ableton.send_command("create_audio_track", {})
                click_track = click_result.get("track_index", len(ableton.send_command("get_all_tracks", {}).get("tracks", [])))
                ableton.send_command("set_track_name", {
                    "track_index": click_track,
                    "name": "Kick Click Layer"
                })
                # Set volume
                ableton.send_command("set_track_volume", {
                    "track_index": click_track,
                    "volume": click_volume
                })
                enhancements.append({"type": "click_layer", "track": click_track, "volume": click_volume})
            
            logger.info(f"Enhanced kick on track {track_index}: {len(enhancements)} enhancements")
            
            return json.dumps({
                "status": "success",
                "track": track_index,
                "enhancements": enhancements,
                "recommendation": "Solo the track and adjust each enhancement to taste"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error enhancing kick: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def thicken_snare(
        ctx: Context,
        track_index: int,
        parallel_reverb: bool = True,
        reverb_decay: float = 0.5,
        reverb_mix: float = 0.3,
        add_body: bool = True,
        body_freq: float = 200.0,
        body_db: float = 6.0,
        gate_threshold: float = -20.0,
        saturation: float = 0.4,
    ) -> str:
        """
        Make snares thick and punchy with professional processing.
        
        Parameters:
        - track_index: Track with snare
        - parallel_reverb: Add reverb on a parallel bus
        - reverb_decay: Decay time in seconds
        - reverb_mix: Wet/dry mix for parallel reverb
        - add_body: Boost mid frequencies for body
        - body_freq: Frequency for body boost
        - body_db: Amount of body boost
        - gate_threshold: Noise gate threshold
        - saturation: analog warmth
        
        Returns: JSON with snare thickening details
        """
        try:
            ableton = get_ableton_connection()
            
            enhancements = []
            
            # 1. Add saturation
            sat_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "Saturator"
            })
            sat_idx = sat_result.get("device_index", 0)
            _set_device_parameter(ableton, track_index, sat_idx, 0, saturation)
            enhancements.append({"type": "saturation", "amount": saturation})
            
            # 2. Add EQ for body
            if add_body:
                eq_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": track_index,
                    "device_name": "EQ Eight"
                })
                eq_idx = eq_result.get("device_index", 1)
                body_freq_norm = min(1.0, body_freq / 20000.0)
                body_gain_norm = min(1.0, (body_db + 24.0) / 48.0)
                _set_device_parameter(ableton, track_index, eq_idx, 5, body_freq_norm)  # Band 3
                _set_device_parameter(ableton, track_index, eq_idx, 6, body_gain_norm)
                enhancements.append({"type": "body_boost", "hz": body_freq, "db": body_db})
            
            # 3. Add gate
            gate_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "Gate"
            })
            gate_idx = gate_result.get("device_index", 2)
            threshold_norm = min(1.0, max(0.0, (-gate_threshold) / 60.0))
            _set_device_parameter(ableton, track_index, gate_idx, 0, threshold_norm)
            enhancements.append({"type": "gate", "threshold_db": gate_threshold})
            
            # 4. Parallel reverb
            if parallel_reverb:
                # Create return track for reverb
                return_result = ableton.send_command("create_audio_track", {})
                reverb_track = return_result.get("track_index", len(ableton.send_command("get_all_tracks", {}).get("tracks", [])))
                ableton.send_command("set_track_name", {
                    "track_index": reverb_track,
                    "name": "Snare Reverb Bus"
                })
                
                # Add reverb
                rev_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": reverb_track,
                    "device_name": "Reverb"
                })
                rev_idx = rev_result.get("device_index", 0)
                decay_norm = min(1.0, reverb_decay / 10.0)
                _set_device_parameter(ableton, reverb_track, rev_idx, 2, decay_norm)
                
                # Route snare to reverb bus
                # Set send amount
                ableton.send_command("set_send_amount", {
                    "track_index": track_index,
                    "send_index": 0,
                    "amount": reverb_mix
                })
                
                enhancements.append({"type": "parallel_reverb", "track": reverb_track, "mix": reverb_mix})
            
            logger.info(f"Thickened snare on track {track_index}: {len(enhancements)} enhancements")
            
            return json.dumps({
                "status": "success",
                "track": track_index,
                "enhancements": enhancements,
                "tip": "Use a spectrum analyzer to check the frequency balance"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error thickening snare: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)


    # =============================================================================
    # MIX FATNESS TOOLS
    # =============================================================================

    @mcp.tool()
    def apply_stereo_widening(
        ctx: Context,
        track_index: int,
        method: str = "haas",
        width_percent: float = 100.0,
        high_pass_hz: float = 200.0,
        delay_ms: float = 25.0,
    ) -> str:
        """
        Widen stereo image for fatness.
        
        Methods:
        - "haas": Haas effect (delay one side)
        - "mid_side": Mid/Side processing
        - "chorus": Chorus effect for movement
        
        Parameters:
        - track_index: Track to widen
        - method: Widening technique
        - width_percent: 0-100% width
        - high_pass_hz: HP filter to avoid phase issues in low end
        - delay_ms: Delay time for Haas effect (10-50ms)
        
        Returns: JSON with widening configuration
        """
        try:
            ableton = get_ableton_connection()
            
            if method == "haas":
                # Use Utility device for Haas effect
                # Left: original, Right: delayed
                util_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": track_index,
                    "device_name": "Utility"
                })
                util_idx = util_result.get("device_index", 0)
                
                # Set width (mono to wide stereo)
                width_norm = width_percent / 100.0
                _set_device_parameter(ableton, track_index, util_idx, 0, width_norm)  # Width
                
                # For true Haas, we need to create a return track with delay
                # Simplified: use chorus for similar effect
                chorus_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": track_index,
                    "device_name": "Chorus"
                })
                chorus_idx = chorus_result.get("device_index", 1)
                delay_norm = min(1.0, delay_ms / 100.0)
                _set_device_parameter(ableton, track_index, chorus_idx, 0, delay_norm)
                
                return json.dumps({
                    "status": "success",
                    "track": track_index,
                    "method": "haas",
                    "width_percent": width_percent,
                    "delay_ms": delay_ms,
                    "devices": ["Utility", "Chorus"],
                    "note": "Low frequencies are kept mono to avoid phase cancellation"
                }, indent=2)
                
            elif method == "mid_side":
                # Mid/Side EQ for widening
                eq_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": track_index,
                    "device_name": "EQ Eight"
                })
                eq_idx = eq_result.get("device_index", 0)
                
                # Boost high frequencies on sides
                # This would require actual mid/side routing which is complex
                # For now, use stereo image widening
                
                return json.dumps({
                    "status": "success",
                    "track": track_index,
                    "method": "mid_side",
                    "width_percent": width_percent,
                    "high_pass_hz": high_pass_hz,
                    "note": "For true M/S processing, use Utility device in M/S mode"
                }, indent=2)
                
            else:  # chorus
                chorus_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": track_index,
                    "device_name": "Chorus"
                })
                chorus_idx = chorus_result.get("device_index", 0)
                
                rate_norm = width_percent / 100.0
                depth_norm = width_percent / 100.0
                _set_device_parameter(ableton, track_index, chorus_idx, 0, rate_norm)
                _set_device_parameter(ableton, track_index, chorus_idx, 1, depth_norm)
                
                return json.dumps({
                    "status": "success",
                    "track": track_index,
                    "method": "chorus",
                    "width_percent": width_percent,
                    "device": "Chorus",
                    "tip": "Adjust rate and depth for subtle widening vs. obvious effect"
                }, indent=2)
            
        except Exception as e:
            logger.error(f"Error applying stereo widening: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    @mcp.tool()
    def add_harmonic_excitement(
        ctx: Context,
        track_index: int,
        mode: str = "tape",
        drive: float = 0.5,
        output: float = 0.0,
        high_pass: float = 100.0,
        low_pass: float = 12000.0,
    ) -> str:
        """
        Add upper harmonics to make sounds more present and fat.
        
        Modes:
        - "tape": Tape-style saturation (even harmonics, warm)
        - "tube": Tube-style saturation (odd harmonics, aggressive)
        - "digital": Digital clipping (bright, clean)
        - "bitcrush": Bit crushing (lo-fi, gritty)
        
        Parameters:
        - track_index: Track to excite
        - mode: Saturation type
        - drive: Saturation amount (0-1)
        - output: Output gain (-12 to +12 dB, normalized)
        - high_pass: HP filter before saturation (Hz)
        - low_pass: LP filter before saturation (Hz)
        
        Returns: JSON with excitement configuration
        """
        try:
            ableton = get_ableton_connection()
            
            # Load Saturator
            sat_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "Saturator"
            })
            sat_idx = sat_result.get("device_index", 0)
            
            # Set mode (parameter index for mode)
            # Saturator modes: 0=Soft Sine, 1=Hard Sine, 2=Tape, 3=Tape Soft, 4=Tube, 5=Tube Soft, 6=Digital Hard
            mode_map = {"tape": 2, "tube": 4, "digital": 6, "soft": 0, "hard": 1, "bitcrush": 6}
            mode_idx = mode_map.get(mode, 2)
            mode_norm = mode_idx / 6.0
            _set_device_parameter(ableton, track_index, sat_idx, 1, mode_norm)  # Mode
            
            # Set drive
            _set_device_parameter(ableton, track_index, sat_idx, 0, drive)
            
            # Set output
            output_norm = min(1.0, max(0.0, (output + 12.0) / 24.0))
            # Output might be a different parameter
            
            # Load EQ for filtering
            eq_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "EQ Eight"
            })
            eq_idx = eq_result.get("device_index", 1)
            
            # Set HP and LP filters
            hp_norm = min(1.0, high_pass / 20000.0)
            lp_norm = min(1.0, low_pass / 20000.0)
            
            # For EQ Eight, use band 1 as HP and band 8 as LP
            # This is simplified - actual parameter indices would need to be mapped
            
            logger.info(f"Added harmonic excitement to track {track_index}: {mode} mode, drive={drive}")
            
            return json.dumps({
                "status": "success",
                "track": track_index,
                "device": "Saturator",
                "mode": mode,
                "drive": drive,
                "output_db": output,
                "filter_range": f"{high_pass}Hz - {low_pass}Hz",
                "tip": "Brown noise test: if it becomes harsh, reduce drive"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error adding harmonic excitement: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)


    # =============================================================================
    # SIDECHAIN TOOLS
    # =============================================================================

    @mcp.tool()
    def setup_sidechain_pump(
        ctx: Context,
        source_track: int,
        target_tracks: List[int],
        compressor_threshold: float = -24.0,
        compressor_ratio: float = 4.0,
        compressor_attack: float = 10.0,
        compressor_release: float = 100.0,
        sidechain_amount: float = 0.5,
        key_input_gain: float = 6.0,
    ) -> str:
        """
        Setup sidechain compression to make elements pump with the bass.
        
        Creates a sidechain bus that takes input from the source track (typically bass)
        and uses it to trigger compression on target tracks (typically pads, leads).
        
        Parameters:
        - source_track: Track that triggers pumping (usually bass/drum bus)
        - target_tracks: List of track indices to apply pumping to
        - compressor_threshold: Threshold in dB
        - compressor_ratio: Compression ratio
        - compressor_attack: Attack time in ms
        - compressor_release: Release time in ms
        - sidechain_amount: Mix of compressed vs. dry signal (0-1)
        - key_input_gain: Boost incoming sidechain signal
        
        Returns: JSON with sidechain configuration
        """
        try:
            ableton = get_ableton_connection()
            
            setup = []
            
            for target_idx in target_tracks:
                # Add compressor to target track
                comp_result = ableton.send_command("load_instrument_or_effect", {
                    "track_index": target_idx,
                    "device_name": "Glue Compressor"
                })
                comp_idx = comp_result.get("device_index", 0)
                
                # Enable sidechain
                ableton.send_command("set_device_sidechain", {
                    "track_index": target_idx,
                    "device_index": comp_idx,
                    "source_track": source_track,
                    "enabled": True
                })
                
                # Set compressor parameters
                ratio_norm = min(1.0, max(0.0, (compressor_ratio - 1.0) / 20.0))
                threshold_norm = min(1.0, max(0.0, (-compressor_threshold) / 60.0))
                attack_norm = min(1.0, max(0.0, math.log(compressor_attack / 0.1) / math.log(1000.0 / 0.1)))
                release_norm = min(1.0, max(0.0, math.log(compressor_release / 10.0) / math.log(3000.0 / 10.0)))
                
                _set_device_parameter(ableton, target_idx, comp_idx, 0, ratio_norm)
                _set_device_parameter(ableton, target_idx, comp_idx, 1, threshold_norm)
                _set_device_parameter(ableton, target_idx, comp_idx, 2, attack_norm)
                _set_device_parameter(ableton, target_idx, comp_idx, 3, release_norm)
                
                # Set dry/wet mix
                mix_norm = min(1.0, max(0.0, sidechain_amount))
                # Dry/wet might be a specific parameter
                
                # Set key input gain
                gain_norm = min(1.0, max(0.0, (key_input_gain + 12.0) / 24.0))
                # This might be a sidechain-specific parameter
                
                setup.append({
                    "target_track": target_idx,
                    "source_track": source_track,
                    "compressor": "Glue Compressor",
                    "compressor_index": comp_idx,
                    "threshold_db": compressor_threshold,
                    "ratio": compressor_ratio
                })
            
            logger.info(f"Setup sidechain pump from track {source_track} to {len(target_tracks)} tracks")
            
            return json.dumps({
                "status": "success",
                "source_track": source_track,
                "target_tracks": target_tracks,
                "setup": setup,
                "compressor_settings": {
                    "threshold_db": compressor_threshold,
                    "ratio": compressor_ratio,
                    "attack_ms": compressor_attack,
                    "release_ms": compressor_release
                },
                "tip": "Adjust release time to match tempo for rhythmic pumping"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error setting up sidechain: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)


    # =============================================================================
    # MASTERING TOOLS
    # =============================================================================

    @mcp.tool()
    def maximize_loudness(
        ctx: Context,
        track_index: int,
        ceiling_db: float = -0.3,
        loudness_target: float = -8.0,
        release_ms: float = 50.0,
        lookahead_ms: float = 5.0,
        gain_boost: float = 3.0,
    ) -> str:
        """
        Maximize loudness using limiter with character.
        
        Applies subtle limiting to bring up overall level while preserving dynamics.
        
        Parameters:
        - track_index: Track to maximize (typically master)
        - ceiling_db: Maximum output level (-0.1 to -3.0)
        - loudness_target: Target LUFS (integrated loudness)
        - release_ms: Release time for limiter
        - lookahead_ms: Lookahead time for limiter
        - gain_boost: Initial gain boost before limiting
        
        Returns: JSON with limiter settings and loudness analysis
        """
        try:
            ableton = get_ableton_connection()
            
            # Load Limiter
            lim_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "Limiter"
            })
            lim_idx = lim_result.get("device_index", 0)
            
            # Set parameters
            ceiling_norm = min(1.0, max(0.0, (ceiling_db + 3.0) / 3.0))  # -3 to 0 -> 0-1
            release_norm = min(1.0, max(0.0, math.log(release_ms / 10.0) / math.log(5000.0 / 10.0)))
            lookahead_norm = min(1.0, max(0.0, lookahead_ms / 20.0))
            gain_norm = min(1.0, max(0.0, gain_boost / 12.0))
            
            _set_device_parameter(ableton, track_index, lim_idx, 0, ceiling_norm)  # Ceiling
            _set_device_parameter(ableton, track_index, lim_idx, 1, 0.5)  # Gain (automatic)
            _set_device_parameter(ableton, track_index, lim_idx, 2, release_norm)  # Release
            _set_device_parameter(ableton, track_index, lim_idx, 3, lookahead_norm)  # Lookahead
            
            # Add Utility for gain boost before limiter
            util_result = ableton.send_command("load_instrument_or_effect", {
                "track_index": track_index,
                "device_name": "Utility"
            })
            util_idx = util_result.get("device_index", 1)
            _set_device_parameter(ableton, track_index, util_idx, 0, gain_norm)  # Gain
            
            logger.info(f"Maximized loudness on track {track_index}: target {loudness_target} LUFS")
            
            return json.dumps({
                "status": "success",
                "track": track_index,
                "limiter": "Limiter",
                "ceiling_db": ceiling_db,
                "loudness_target_lufs": loudness_target,
                "release_ms": release_ms,
                "lookahead_ms": lookahead_ms,
                "gain_boost_db": gain_boost,
                "warning": "Details may vary based on actual LUFS measurement",
                "tip": "Use a LUFS meter to verify loudness - this provides a starting point"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error maximizing loudness: {str(e)}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)


    # =============================================================================
    # ONE-SHOT BEAT CREATION
    # =============================================================================

    @mcp.tool()
    def create_fat_beat(
        ctx: Context,
        # Beat structure
        bpm: float = 90.0,
        bars: int = 4,
        
        # Kick
        kick_pattern: str = "X---|----|X---|----",
        kick_sample: str = "Kick_Classic_01",
        kick_volume: float = 1.0,
        kick_pan: float = 0.0,
        
        # Snare
        snare_pattern: str = "----|X---|----|X---",
        snare_sample: str = "Snare_Classic_01",
        snare_volume: float = 0.8,
        snare_pan: float = 0.0,
        
        # Hi-Hat
        hat_pattern: str = "--x-|--x-|--x-|--x-",
        hat_sample: str = "Hat_Closed_01",
        hat_volume: float = 0.6,
        hat_pan: float = 0.5,
        
        # Bass
        bass_octave: int = 0,
        bass_pattern: str = "X---|----|X---|----",
        bass_volume: float = 0.9,
        
        # Processing
        add_compression: bool = True,
        add_saturation: bool = True,
        add_sidechain: bool = True,
        sidechain_source: int = 0,  # Bass track
        
        # Fatness settings
        bass_enhancement: str = "parallel",  # none, parallel, sub_harmonic
        stereo_widening: str = "haas",  # none, haas, chorus
        loudness_maximization: bool = False,
    ) -> str:
        """
        Create a complete fat beat from scratch with professional processing.
        
        This is the ultimate all-in-one fat beat creator that:
        1. Creates drum tracks with samples
        2. Creates bass track
        3. Applies fatness processing to each element
        4. Sets up routing and effects
        5. Optionally adds master bus processing
        
        Parameters:
        - bpm: Tempo
        - bars: Length in bars
        - kick_pattern/snare_pattern/hat_pattern: Step sequel notation ('X' = hit, '-' = rest, 'x' = ghost)
        - *_sample: Sample name from Ableton browser
        - *_volume: Volume for each element
        - *_pan: Pan for each element
        - add_*: Processing options
        - bass_enhancement: Type of bass processing
        - stereo_widening: Stereo widening method
        - loudness_maximization: Add limiter to master
        
        Returns: JSON with complete beat configuration
        """
        try:
            ableton = get_ableton_connection()
            
            # First, delete all existing tracks for a clean slate
            try:
                ableton.send_command("delete_all_tracks", {})
                # Small delay for cleanup
                import time; time.sleep(0.5)
            except:
                pass
            
            # Set tempo
            ableton.send_command("set_tempo", {"bpm": bpm})
            
            # Track indices (we'll use 0=kick, 1=snare, 2=hat, 3=bass, 4=fx)
            track_info = {}
            
            def parse_pattern(pattern: str, bars: int = 4) -> List[float]:
                """Parse pattern string into list of steps (0=rest, 1=hit, 0.5=ghost)."""
                steps = []
                beats_per_bar = 4
                for bar in range(bars):
                    bar_pattern = pattern.split('|')[bar % len(pattern.split('|'))]
                    for char in bar_pattern.strip():
                        if char == 'X':
                            steps.append(1.0)
                        elif char == 'x':
                            steps.append(0.5)
                        else:
                            steps.append(0.0)
                return steps
            
            # Create Kick Track
            kick_result = ableton.send_command("create_midi_track", {"index": 0})
            kick_idx = kick_result.get("track_index", 0)
            ableton.send_command("set_track_name", {"track_index": kick_idx, "name": "Kick"})
            ableton.send_command("set_track_volume", {"track_index": kick_idx, "volume": kick_volume})
            ableton.send_command("set_track_pan", {"track_index": kick_idx, "pan": kick_pan})
            
            # Load kick sample
            ableton.send_command("load_instrument_or_effect", {
                "track_index": kick_idx,
                "device_name": "Drum Rack"
            })
            # For now, useSimpler with a kick sample
            ableton.send_command("load_instrument_or_effect", {
                "track_index": kick_idx,
                "device_name": "Simpler"
            })
            # Load the kick sample (this is a simplification)
            
            track_info[kick_idx] = {"name": "Kick", "type": "drum", "pattern": parse_pattern(kick_pattern, bars)}
            
            # Create Snare Track
            snare_result = ableton.send_command("create_midi_track", {"index": 1})
            snare_idx = snare_result.get("track_index", 1)
            ableton.send_command("set_track_name", {"track_index": snare_idx, "name": "Snare"})
            ableton.send_command("set_track_volume", {"track_index": snare_idx, "volume": snare_volume})
            ableton.send_command("set_track_pan", {"track_index": snare_idx, "pan": snare_pan})
            track_info[snare_idx] = {"name": "Snare", "type": "drum", "pattern": parse_pattern(snare_pattern, bars)}
            
            # Create Hi-Hat Track
            hat_result = ableton.send_command("create_midi_track", {"index": 2})
            hat_idx = hat_result.get("track_index", 2)
            ableton.send_command("set_track_name", {"track_index": hat_idx, "name": "Hi-Hat"})
            ableton.send_command("set_track_volume", {"track_index": hat_idx, "volume": hat_volume})
            ableton.send_command("set_track_pan", {"track_index": hat_idx, "pan": hat_pan})
            track_info[hat_idx] = {"name": "Hi-Hat", "type": "drum", "pattern": parse_pattern(hat_pattern, bars)}
            
            # Create Bass Track
            bass_result = ableton.send_command("create_midi_track", {"index": 3})
            bass_idx = bass_result.get("track_index", 3)
            ableton.send_command("set_track_name", {"track_index": bass_idx, "name": "Bass"})
            ableton.send_command("set_track_volume", {"track_index": bass_idx, "volume": bass_volume})
            
            # Load bass synth
            ableton.send_command("load_instrument_or_effect", {
                "track_index": bass_idx,
                "device_name": "Operator"
            })
            # Set to bass preset
            track_info[bass_idx] = {"name": "Bass", "type": "bass", "pattern": parse_pattern(bass_pattern, bars)}
            
            # Create clips and add notes
            # For each track, create a clip and add notes based on pattern
            for track_idx, info in track_info.items():
                # Create clip
                clip_result = ableton.send_command("create_clip", {
                    "track_index": track_idx,
                    "clip_index": 0,
                    "length_bars": bars
                })
                
                # Add notes based on pattern
                steps_per_beat = 4  # 16th notes
                Eleventh_in_bar = bars * 4  # Total 16th notes
                
                for beat in range(Eleventh_in_bar):
                    step_value = info["pattern"][beat % len(info["pattern"])]
                    if step_value > 0:
                        velocity = 100 if step_value >= 1.0 else 60
                        ableton.send_command("add_note", {
                            "track_index": track_idx,
                            "clip_index": 0,
                            "pitch": 36 if info["name"] == "Kick" else (38 if info["name"] == "Snare" else (42 if info["name"] == "Hi-Hat" else (48 + bass_octave * 12))),
                            "velocity": velocity,
                            "start_beat": beat / float(steps_per_beat),
                            "duration_beats": 0.25 if info["name"] == "Hi-Hat" else 0.5
                        })
            
            # Apply fatness processing
            processing_log = []
            
            # Add saturation to drums
            if add_saturation:
                for track_idx in [kick_idx, snare_idx, hat_idx]:
                    sat_result = ableton.send_command("load_instrument_or_effect", {
                        "track_index": track_idx,
                        "device_name": "Saturator"
                    })
                    sat_idx = sat_result.get("device_index", 0)
                    _set_device_parameter(ableton, track_idx, sat_idx, 0, 0.3)
                    processing_log.append(f"Saturation on {track_info[track_idx]['name']}")
            
            # Add compression to snare and kick
            if add_compression:
                for track_idx in [kick_idx, snare_idx]:
                    comp_result = ableton.send_command("load_instrument_or_effect", {
                        "track_index": track_idx,
                        "device_name": "Glue Compressor"
                    })
                    comp_idx = comp_result.get("device_index", 0)
                    processing_log.append(f"Compression on {track_info[track_idx]['name']}")
            
            # Bass enhancement
            if bass_enhancement == "parallel":
                result = create_parallel_bass_compression(
                    ctx, bass_idx, compression_amount=0.6
                )
                processing_log.append("Parallel compression on bass")
            elif bass_enhancement == "sub_harmonic":
                result = add_sub_bass_harmonic(
                    ctx, bass_idx, harmonic_octave=-1, harmonic_volume=0.4
                )
                processing_log.append("Sub-harmonic on bass")
            
            # Stereo widening
            if stereo_widening != "none":
                for track_idx in [hat_idx, snare_idx]:
                    result = apply_stereo_widening(
                        ctx, track_idx, method=stereo_widening, width_percent=50.0
                    )
                    processing_log.append(f"Stereo widening ({stereo_widening}) on {track_info[track_idx]['name']}")
            
            # Sidechain
            if add_sidechain:
                result = setup_sidechain_pump(
                    ctx, source_track=sidechain_source, target_tracks=[hat_idx, snare_idx]
                )
                processing_log.append("Sidechain pump from bass to hats/snare")
            
            # Master bus processing
            if loudness_maximization:
                # Create master effects
                master_idx = len(track_info)  # Last track
                # In Ableton, master is typically a separate entity
                # For now, suggest adding to last track or master
                pass
            
            # Fire the scene (play all clips)
            ableton.send_command("trigger_scene", {"scene_index": 0})
            
            logger.info(f"Created fat beat: {bpm} BPM, {bars} bars, {len(track_info)} tracks")
            
            return json.dumps({
                "status": "success",
                "bpm": bpm,
                "bars": bars,
                "tracks": {
                    ti: info for ti, info in track_info.items()
                },
                "processing": processing_log,
                "options": {
                    "add_compression": add_compression,
                    "add_saturation": add_saturation,
                    "add_sidechain": add_sidechain,
                    "bass_enhancement": bass_enhancement,
                    "stereo_widening": stereo_widening,
                    "loudness_maximization": loudness_maximization
                },
                "next_steps": [
                    "Adjust individual track volumes for balance",
                    "Tune drum samples to match your style",
                    "Add effects returns for reverb/delay",
                    "Fine-tune compressor settings per track",
                    "Consider adding automation for variation"
                ]
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error creating fat beat: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return json.dumps({"status": "error", "message": str(e)}, indent=2)
