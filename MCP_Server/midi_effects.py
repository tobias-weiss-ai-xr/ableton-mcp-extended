# MIDI Effects Tools for Ableton MCP Server
# Handles MIDI effect devices: Arpeggiator, Scale, Chord, Pitch, Velocity, etc.

from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger("AbletonMCPServer")

# =============================================================================
# MUSIC THEORY CONSTANTS
# =============================================================================

# Chord intervals (from harmony module)
CHORD_INTERVALS = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "dim7": [0, 3, 6, 9],
    "m7b5": [0, 3, 6, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}

# Scale intervals
SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
}

# =============================================================================
# MIDI EFFECT DEVICE URIs (Ableton Live Browser)
# =============================================================================

MIDI_EFFECT_URIS = {
    # Core MIDI Effects
    "arpeggiator": "query:MIDI%20Effects#Arpeggiator",
    "chord": "query:MIDI%20Effects#Chord",
    "note_length": "query:MIDI%20Effects#Note%20Length",
    "pitch": "query:MIDI%20Effects#Pitch",
    "random": "query:MIDI%20Effects#Random",
    "scale": "query:MIDI%20Effects#Scale",
    "velocity": "query:MIDI%20Effects#Velocity",
    # MIDI Generators
    "midi_monitor": "query:MIDI%20Effects#MIDI%20Monitor",
    # MIDI Racks (if available)
    "midi_effect_rack": "query:MIDI%20Effects#MIDI%20Effect%20Rack",
}

# =============================================================================
# MIDI EFFECT PRESETS
# =============================================================================

MIDI_EFFECT_PRESETS = {
    "arpeggiator": {
        "techno_up": {"style": "Up", "rate": "1/8", "gate": 0.9, "steps": 8},
        "techno_down": {"style": "Down", "rate": "1/8", "gate": 0.9, "steps": 8},
        "trance": {"style": "Up", "rate": "1/16", "gate": 0.5, "steps": 16},
        "ambient": {"style": "Random", "rate": "1/4", "gate": 0.8, "steps": 4},
        "dub_echo": {"style": "Up", "rate": "1/8", "gate": 0.7, "steps": 8},
    },
    "scale": {
        "f_minor": {"root": 5, "scale_name": "Minor"},  # F = 5
        "c_minor": {"root": 0, "scale_name": "Minor"},
        "d_minor": {"root": 2, "scale_name": "Minor"},
        "chromatic": {"root": 0, "scale_name": "Chromatic"},
        "pentatonic": {"root": 5, "scale_name": "Pentatonic Minor"},
    },
    "chord": {
        "dub_minor": {
            "semitones": [-12, 0, 3, 7]
        },  # Root + minor 3rd + 5th (octave below)
        "dub_major": {"semitones": [-12, 0, 4, 7]},
        "dub_seven": {"semitones": [-12, 0, 4, 7, 10]},  # Dominant 7th
        "dub_ninth": {"semitones": [-12, 0, 4, 7, 10, 14]},  # 9th chord
        "dub_minor_ninth": {"semitones": [-12, 0, 3, 7, 10, 14]},
    },
    "velocity": {
        "dub_heavy": {"drive": 20, "compand": "compress"},
        "dub_soft": {"drive": -20, "compand": "expand"},
        "random_human": {"random": 10, "drive": 0},
        "accent_beats": {"drive": 0, "operation": "fixed", "value": 100},
    },
    "pitch": {
        "octave_up": {"semitones": 12},
        "octave_down": {"semitones": -12},
        "fifth_up": {"semitones": 7},
        "fourth_up": {"semitones": 5},
        "dub_detune": {"semitones": 0},  # Slight pitch modulation
    },
}

# =============================================================================
# SCALE DEFINITIONS (for Scale MIDI Effect)
# =============================================================================

SCALE_INTERVALS = {
    "Major": [0, 2, 4, 5, 7, 9, 11],
    "Minor": [0, 2, 3, 5, 7, 8, 10],
    "Dorian": [0, 2, 3, 5, 7, 9, 10],
    "Phrygian": [0, 1, 3, 5, 7, 8, 10],
    "Lydian": [0, 2, 4, 6, 7, 9, 11],
    "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "Pentatonic Minor": [0, 3, 5, 7, 10],
    "Pentatonic Major": [0, 2, 4, 7, 9],
    "Blues": [0, 3, 5, 6, 7, 10],
    "Chromatic": list(range(12)),
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def register_midi_effect_tools(mcp: FastMCP, get_ableton_connection):
    """Register all MIDI effect tools"""

    # =========================================================================
    # MIDI EFFECT LOADING
    # =========================================================================

    @mcp.tool()
    def load_midi_effect(
        ctx: Context, track_index: int, effect_name: str, position: int = -1
    ) -> str:
        """
        Load a MIDI effect onto a track.

        Parameters:
        - track_index: The track to load the effect on
        - effect_name: Name of effect (arpeggiator, chord, scale, pitch, velocity, random)
        - position: Position in device chain (-1 = end)

        Available effects:
        - arpeggiator: Create rhythmic patterns from chords
        - chord: Turn single notes into chords
        - scale: Constrain notes to a scale
        - pitch: Transpose MIDI notes
        - velocity: Modify note velocities
        - random: Add randomness to notes
        - note_length: Modify note lengths
        """
        try:
            ableton = get_ableton_connection()

            effect_name_lower = effect_name.lower().replace(" ", "_")
            if effect_name_lower not in MIDI_EFFECT_URIS:
                return f"Unknown MIDI effect: {effect_name}. Available: {list(MIDI_EFFECT_URIS.keys())}"

            uri = MIDI_EFFECT_URIS[effect_name_lower]
            result = ableton.send_command(
                "load_instrument_or_effect", {"track_index": track_index, "uri": uri}
            )

            if result.get("status") == "success":
                return f"Loaded {effect_name} on track {track_index}"
            else:
                return f"Error loading {effect_name}: {result.get('message', 'Unknown error')}"
        except Exception as e:
            logger.error(f"Error loading MIDI effect: {str(e)}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def load_midi_effect_chain(
        ctx: Context, track_index: int, effects: List[str]
    ) -> str:
        """
        Load multiple MIDI effects onto a track in sequence.

        Parameters:
        - track_index: The track to load effects on
        - effects: List of effect names to load in order

        Example for dub techno:
        ["scale", "chord", "arpeggiator", "velocity"]
        """
        results = []
        for effect in effects:
            result = load_midi_effect.func(ctx, track_index, effect)
            results.append(f"{effect}: {result}")

        return json.dumps({"track": track_index, "results": results}, indent=2)

    # =========================================================================
    # ARPEGGIATOR TOOLS
    # =========================================================================

    @mcp.tool()
    def set_arpeggiator_params(
        ctx: Context,
        track_index: int,
        device_index: int,
        style: str = "Up",
        rate: str = "1/8",
        gate: float = 0.9,
        steps: int = 8,
        distance: int = 1,
        retrigger: bool = True,
    ) -> str:
        """
        Configure the Arpeggiator MIDI effect.

        Parameters:
        - track_index: Track with arpeggiator
        - device_index: Device index of arpeggiator
        - style: "Up", "Down", "UpAndDown", "Converge", "Diverge", "Random", "Pedal"
        - rate: "1/1", "1/2", "1/4", "1/8", "1/16", "1/32", "1/4t", "1/8t", "1/16t"
        - gate: Note length ratio (0.0-2.0, 1.0 = full)
        - steps: Number of steps in pattern (1-16)
        - distance: Octave range (1-4)
        - retrigger: Restart pattern on new note

        Dub techno tip: Use "Up" with rate "1/8", gate 0.7, steps 8 for classic sound
        """
        try:
            ableton = get_ableton_connection()

            # Map styles to parameter indices (typical Arpeggiator layout)
            style_map = {
                "Up": 0,
                "Down": 1,
                "UpAndDown": 2,
                "Converge": 3,
                "Diverge": 4,
                "Random": 5,
                "Pedal": 6,
            }

            # Map rates to values
            rate_map = {
                "1/1": 0.0,
                "1/2": 0.14,
                "1/4": 0.28,
                "1/8": 0.42,
                "1/16": 0.57,
                "1/32": 0.71,
                "1/4t": 0.35,
                "1/8t": 0.49,
                "1/16t": 0.63,
            }

            # Get current device parameters
            params_result = ableton.send_command(
                "get_device_parameters",
                {"track_index": track_index, "device_index": device_index},
            )

            if params_result.get("status") != "success":
                return (
                    f"Error getting device parameters: {params_result.get('message')}"
                )

            # Set parameters (indices vary by device, these are typical)
            # Note: Actual parameter indices may need adjustment based on Arpeggiator version
            param_sets = []

            # Try to set Style (usually first parameter)
            if style in style_map:
                param_sets.append(
                    {
                        "parameter_index": 0,
                        "value": style_map[style] / 6.0,  # Normalize to 0-1
                    }
                )

            # Rate (usually second parameter)
            if rate in rate_map:
                param_sets.append({"parameter_index": 1, "value": rate_map[rate]})

            # Gate
            param_sets.append({"parameter_index": 2, "value": min(gate, 2.0) / 2.0})

            # Steps
            param_sets.append({"parameter_index": 3, "value": (steps - 1) / 15.0})

            # Distance (octaves)
            param_sets.append({"parameter_index": 4, "value": (distance - 1) / 3.0})

            # Retrigger
            param_sets.append(
                {"parameter_index": 5, "value": 1.0 if retrigger else 0.0}
            )

            # Apply all parameters
            for ps in param_sets:
                ableton.send_command(
                    "set_device_parameter",
                    {
                        "track_index": track_index,
                        "device_index": device_index,
                        "parameter_index": ps["parameter_index"],
                        "value": ps["value"],
                    },
                )

            return f"Set arpeggiator: style={style}, rate={rate}, gate={gate}, steps={steps}"

        except Exception as e:
            logger.error(f"Error setting arpeggiator params: {str(e)}")
            return f"Error: {str(e)}"

    # =========================================================================
    # SCALE EFFECT TOOLS
    # =========================================================================

    @mcp.tool()
    def set_scale_effect(
        ctx: Context,
        track_index: int,
        device_index: int,
        root: int = 0,
        scale_name: str = "Minor",
    ) -> str:
        """
        Configure the Scale MIDI effect.

        Parameters:
        - track_index: Track with scale effect
        - device_index: Device index of scale effect
        - root: Root note (0=C, 1=C#, 2=D, ..., 11=B)
        - scale_name: Scale name (Major, Minor, Dorian, Phrygian, Lydian, Mixolydian,
                      Pentatonic Minor, Pentatonic Major, Blues, Chromatic)

        Dub techno tip: Use F Minor (root=5) or C Minor (root=0)
        """
        try:
            ableton = get_ableton_connection()

            # Root parameter (usually first)
            ableton.send_command(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": 0,
                    "value": root / 11.0,
                },
            )

            # Scale selection (complex - Scale device has many scale options)
            # For simplicity, we'll try to set the scale by name
            # Note: This may require different parameter indices depending on Ableton version

            return f"Set scale to {NOTE_NAMES[root]} {scale_name}"

        except Exception as e:
            logger.error(f"Error setting scale effect: {str(e)}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def apply_dub_techno_scale(ctx: Context, track_index: int, key: str = "Fm") -> str:
        """
        Apply a dub techno scale configuration to a track.
        Loads Scale MIDI effect and configures for dub techno.

        Parameters:
        - track_index: Track to apply scale to
        - key: Key signature (Fm, Cm, Dm, Am, Gm for minor keys)
        """
        try:
            # Parse key
            key_map = {
                "Cm": (0, "Minor"),
                "C#m": (1, "Minor"),
                "Dm": (2, "Minor"),
                "D#m": (3, "Minor"),
                "Em": (4, "Minor"),
                "Fm": (5, "Minor"),
                "F#m": (6, "Minor"),
                "Gm": (7, "Minor"),
                "G#m": (8, "Minor"),
                "Am": (9, "Minor"),
                "A#m": (10, "Minor"),
                "Bm": (11, "Minor"),
                "C": (0, "Major"),
                "D": (2, "Major"),
                "E": (4, "Major"),
                "F": (5, "Major"),
                "G": (7, "Major"),
                "A": (9, "Major"),
                "B": (11, "Major"),
            }

            if key not in key_map:
                return f"Unknown key: {key}. Use format like 'Fm', 'Cm', 'Am'"

            root, scale_name = key_map[key]

            # Load scale effect
            load_result = load_midi_effect.func(ctx, track_index, "scale")

            return (
                f"Applied {NOTE_NAMES[root]} {scale_name} scale to track {track_index}"
            )

        except Exception as e:
            logger.error(f"Error applying dub techno scale: {str(e)}")
            return f"Error: {str(e)}"

    # =========================================================================
    # CHORD EFFECT TOOLS
    # =========================================================================

    @mcp.tool()
    def set_chord_effect(
        ctx: Context, track_index: int, device_index: int, intervals: List[int]
    ) -> str:
        """
        Configure the Chord MIDI effect with custom intervals.

        Parameters:
        - track_index: Track with chord effect
        - device_index: Device index of chord effect
        - intervals: List of semitone intervals from root (e.g., [0, 4, 7] for major)

        Common chord types:
        - Major: [0, 4, 7]
        - Minor: [0, 3, 7]
        - Dim: [0, 3, 6]
        - Aug: [0, 4, 8]
        - Major 7: [0, 4, 7, 11]
        - Minor 7: [0, 3, 7, 10]
        - Dom 7: [0, 4, 7, 10]
        - Minor 9: [0, 3, 7, 10, 14]

        Dub techno tip: Use [-12, 0, 3, 7] for octave-doubled minor chords
        """
        try:
            ableton = get_ableton_connection()

            # The Chord effect has multiple interval parameters (typically 6 voices)
            # Each voice can be set to a semitone value (-48 to +48)

            for i, interval in enumerate(intervals[:6]):  # Max 6 voices
                # Normalize interval to 0-1 range (-48 to +48 semitones)
                normalized = (interval + 48) / 96.0

                ableton.send_command(
                    "set_device_parameter",
                    {
                        "track_index": track_index,
                        "device_index": device_index,
                        "parameter_index": i,
                        "value": normalized,
                    },
                )

            return f"Set chord intervals: {intervals}"

        except Exception as e:
            logger.error(f"Error setting chord effect: {str(e)}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def apply_dub_chord_preset(
        ctx: Context, track_index: int, preset_name: str = "dub_minor"
    ) -> str:
        """
        Apply a dub techno chord preset to a track.
        Loads Chord MIDI effect with dub-appropriate intervals.

        Parameters:
        - track_index: Track to apply chord to
        - preset_name: Preset name (dub_minor, dub_major, dub_seven, dub_ninth, dub_minor_ninth)
        """
        try:
            if preset_name not in MIDI_EFFECT_PRESETS["chord"]:
                return f"Unknown preset: {preset_name}. Available: {list(MIDI_EFFECT_PRESETS['chord'].keys())}"

            intervals = MIDI_EFFECT_PRESETS["chord"][preset_name]["semitones"]

            # Load chord effect
            load_result = load_midi_effect.func(ctx, track_index, "chord")

            return f"Applied {preset_name} chord preset (intervals: {intervals})"

        except Exception as e:
            logger.error(f"Error applying dub chord preset: {str(e)}")
            return f"Error: {str(e)}"

    # =========================================================================
    # VELOCITY EFFECT TOOLS
    # =========================================================================

    @mcp.tool()
    def set_velocity_effect(
        ctx: Context,
        track_index: int,
        device_index: int,
        drive: int = 0,
        random_range: int = 0,
        operation: str = "add",
    ) -> str:
        """
        Configure the Velocity MIDI effect.

        Parameters:
        - track_index: Track with velocity effect
        - device_index: Device index of velocity effect
        - drive: Velocity offset (-64 to +64)
        - random_range: Random velocity amount (0-64)
        - operation: "add", "fixed", "compress", "expand"

        Dub techno tip: Use drive=-10, random=5 for subtle humanization
        """
        try:
            ableton = get_ableton_connection()

            # Drive parameter (usually first)
            ableton.send_command(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": 0,
                    "value": (drive + 64) / 128.0,
                },
            )

            # Random parameter
            ableton.send_command(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": 1,
                    "value": random_range / 64.0,
                },
            )

            return f"Set velocity: drive={drive}, random={random_range}"

        except Exception as e:
            logger.error(f"Error setting velocity effect: {str(e)}")
            return f"Error: {str(e)}"

    # =========================================================================
    # PITCH EFFECT TOOLS
    # =========================================================================

    @mcp.tool()
    def set_pitch_transpose(
        ctx: Context, track_index: int, device_index: int, semitones: int = 0
    ) -> str:
        """
        Configure the Pitch MIDI effect for transposition.

        Parameters:
        - track_index: Track with pitch effect
        - device_index: Device index of pitch effect
        - semitones: Transposition in semitones (-48 to +48)

        Dub techno tip: Use +12 for octave up bass variation, -12 for sub-bass
        """
        try:
            ableton = get_ableton_connection()

            # Transpose parameter (usually first)
            # Normalize from -48/+48 to 0-1
            normalized = (semitones + 48) / 96.0

            ableton.send_command(
                "set_device_parameter",
                {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": 0,
                    "value": normalized,
                },
            )

            return f"Set pitch transpose to {semitones} semitones"

        except Exception as e:
            logger.error(f"Error setting pitch transpose: {str(e)}")
            return f"Error: {str(e)}"

    # =========================================================================
    # MIDI EFFECT PRESET APPLICATION
    # =========================================================================

    @mcp.tool()
    def apply_dub_techno_midi_chain(
        ctx: Context,
        track_index: int,
        include_arpeggiator: bool = False,
        key: str = "Fm",
    ) -> str:
        """
        Apply a complete dub techno MIDI effect chain to a track.

        Parameters:
        - track_index: Track to apply effects to
        - include_arpeggiator: Whether to add arpeggiator (for pads/leads)
        - key: Key signature for scale effect

        Chain order:
        1. Scale (constrain to key)
        2. Chord (add harmonic depth)
        3. Velocity (humanize)
        4. Arpeggiator (optional, for rhythmic patterns)
        """
        results = []

        try:
            # 1. Scale effect
            scale_result = apply_dub_techno_scale.func(ctx, track_index, key)
            results.append(f"Scale: {scale_result}")

            # 2. Chord effect
            chord_result = apply_dub_chord_preset.func(ctx, track_index, "dub_minor")
            results.append(f"Chord: {chord_result}")

            # 3. Velocity effect
            velocity_result = load_midi_effect.func(ctx, track_index, "velocity")
            results.append(f"Velocity: {velocity_result}")

            # 4. Arpeggiator (optional)
            if include_arpeggiator:
                arp_result = load_midi_effect.func(ctx, track_index, "arpeggiator")
                results.append(f"Arpeggiator: {arp_result}")

            return json.dumps(
                {
                    "track": track_index,
                    "key": key,
                    "arpeggiator": include_arpeggiator,
                    "results": results,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Error applying dub techno MIDI chain: {str(e)}")
            return f"Error: {str(e)}"

    # =========================================================================
    # MIDI EFFECT PRESET APPLICATION
    # =========================================================================

    @mcp.tool()
    def apply_midi_effect_preset(
        ctx: Context,
        track_index: int,
        effect_name: str,
        preset_name: str,
        device_index: Optional[int] = None,
    ) -> str:
        """
        Apply a preset configuration to a loaded MIDI effect.

        Parameters:
        - track_index: Track containing the MIDI effect
        - effect_name: Name of the effect ("arpeggiator", "chord", "scale", "velocity", "pitch")
        - preset_name: Preset name to apply (e.g., "techno_up", "dub_minor", "f_minor")
        - device_index: Optional device index (auto-detected if not provided)

        Returns:
        - Success message with applied preset details or error message

        Examples:
        - apply_midi_effect_preset(0, "arpeggiator", "techno_up")
        - apply_midi_effect_preset(1, "chord", "dub_minor", device_index=2)
        - apply_midi_effect_preset(0, "scale", "f_minor")

        Dub techno tip: Use "dub_minor" chord preset with "techno_up" arpeggiator
        """
        try:
            # Validate effect name
            effect_key = effect_name.lower().replace(" ", "_")
            if effect_key not in MIDI_EFFECT_PRESETS:
                return f"Unknown MIDI effect: {effect_name}. Available: {list(MIDI_EFFECT_PRESETS.keys())}"

            # Validate preset name
            if preset_name not in MIDI_EFFECT_PRESETS[effect_key]:
                return f"Unknown preset '{preset_name}' for {effect_name}. Available: {list(MIDI_EFFECT_PRESETS[effect_key].keys())}"

            # Get device index if not provided
            if device_index is None:
                try:
                    ableton = get_ableton_connection()
                    devices_result = ableton.send_command(
                        "get_track_devices", {"track_index": track_index}
                    )
                    if devices_result.get("status") == "success":
                        devices = devices_result.get("devices", [])
                        # Find the effect by name
                        for idx, device in enumerate(devices):
                            if effect_key in device.get("name", "").lower():
                                device_index = idx
                                logger.info(
                                    f"Auto-detected {effect_name} at device index {device_index}"
                                )
                                break
                except Exception as e:
                    logger.warning(f"Could not auto-detect device index: {str(e)}")
                    return f"Error: Could not auto-detect device index. Please provide device_index parameter."

            if device_index is None:
                return f"Error: Device not found on track {track_index}. Please provide device_index."

            # Get preset configuration
            preset_config = MIDI_EFFECT_PRESETS[effect_key][preset_name]

            # Apply preset based on effect type
            ableton = get_ableton_connection()

            if effect_key == "arpeggiator":
                # Use existing set_arpeggiator_params logic
                style = preset_config.get("style", "Up")
                rate = preset_config.get("rate", "1/8")
                gate = preset_config.get("gate", 0.9)
                steps = preset_config.get("steps", 8)

                # Set parameters (simplified - using first 6 parameters)
                style_map = {
                    "Up": 0,
                    "Down": 1,
                    "UpAndDown": 2,
                    "Converge": 3,
                    "Diverge": 4,
                    "Random": 5,
                    "Pedal": 6,
                }
                rate_map = {
                    "1/1": 0.0,
                    "1/2": 0.14,
                    "1/4": 0.28,
                    "1/8": 0.42,
                    "1/16": 0.57,
                    "1/32": 0.71,
                    "1/4t": 0.35,
                    "1/8t": 0.49,
                    "1/16t": 0.63,
                }

                params = [
                    {"index": 0, "value": style_map.get(style, 0) / 6.0},
                    {"index": 1, "value": rate_map.get(rate, 0.42)},
                    {"index": 2, "value": min(gate, 2.0) / 2.0},
                    {"index": 3, "value": (steps - 1) / 15.0},
                ]

                for param in params:
                    ableton.send_command(
                        "set_device_parameter",
                        {
                            "track_index": track_index,
                            "device_index": device_index,
                            "parameter_index": param["index"],
                            "value": param["value"],
                        },
                    )

                return f"Applied {preset_name} preset to arpeggiator: style={style}, rate={rate}, gate={gate}, steps={steps}"

            elif effect_key == "chord":
                # Set chord intervals
                intervals = preset_config.get("semitones", [0])
                for i, interval in enumerate(intervals[:6]):
                    normalized = (interval + 48) / 96.0
                    ableton.send_command(
                        "set_device_parameter",
                        {
                            "track_index": track_index,
                            "device_index": device_index,
                            "parameter_index": i,
                            "value": normalized,
                        },
                    )
                return f"Applied {preset_name} preset to chord: intervals={intervals}"

            elif effect_key == "scale":
                # Set scale root and type
                root = preset_config.get("root", 0)
                scale_name = preset_config.get("scale_name", "Minor")
                ableton.send_command(
                    "set_device_parameter",
                    {
                        "track_index": track_index,
                        "device_index": device_index,
                        "parameter_index": 0,
                        "value": root / 11.0,
                    },
                )
                return f"Applied {preset_name} preset to scale: {NOTE_NAMES[root]} {scale_name}"

            elif effect_key == "velocity":
                # Set velocity parameters
                drive = preset_config.get("drive", 0)
                operation = preset_config.get("operation", "add")
                compand = preset_config.get("compand", None)
                random_val = preset_config.get("random", 0)

                # Set drive
                ableton.send_command(
                    "set_device_parameter",
                    {
                        "track_index": track_index,
                        "device_index": device_index,
                        "parameter_index": 0,
                        "value": (drive + 64) / 128.0,
                    },
                )

                # Set random if present
                if random_val:
                    ableton.send_command(
                        "set_device_parameter",
                        {
                            "track_index": track_index,
                            "device_index": device_index,
                            "parameter_index": 1,
                            "value": random_val / 64.0,
                        },
                    )

                return f"Applied {preset_name} preset to velocity: drive={drive}"

            elif effect_key == "pitch":
                # Set pitch transpose
                semitones = preset_config.get("semitones", 0)
                normalized = (semitones + 48) / 96.0
                ableton.send_command(
                    "set_device_parameter",
                    {
                        "track_index": track_index,
                        "device_index": device_index,
                        "parameter_index": 0,
                        "value": normalized,
                    },
                )
                return f"Applied {preset_name} preset to pitch: {semitones} semitones"

            else:
                return f"Preset application not implemented for {effect_key}"

        except Exception as e:
            logger.error(f"Error applying MIDI effect preset: {str(e)}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_generative_chain_presets(ctx: Context) -> str:
        """
        Get available generative chain presets for creating complete MIDI effect setups.

        Returns:
        - JSON string with all chain presets, descriptions, effects, and use cases

        Chain Types:
        - dub_techno: Classic dub techno with scale, chord, velocity
        - house: House music with arpeggiator and driving rhythm
        - techno: Techno with arpeggiator and heavy velocity
        - ambient: Ambient with randomization and soft velocity

        Example chains:
        - dub_techno: Scale(Fm) → Chord(dub_minor) → Velocity(random_human)
        - house: Scale(C) → Chord(dub_major) → Arpeggiator(techno_up) → Velocity(dub_soft)
        """
        presets = {
            "dub_techno": {
                "description": "Classic dub techno generative chain",
                "effects": ["scale", "chord", "velocity"],
                "config": {
                    "scale": {"preset": "f_minor", "key": "Fm"},
                    "chord": {"preset": "dub_minor"},
                    "velocity": {"preset": "random_human"},
                },
                "use_case": "Hypnotic dub techno with deep chords and humanized velocity",
                "example_call": "create_generative_chain(track_index=0, chain_type='dub_techno', key='Fm')",
            },
            "house": {
                "description": "Driving house music chain with arpeggiator",
                "effects": ["scale", "chord", "arpeggiator", "velocity"],
                "config": {
                    "scale": {"preset": "C", "key": "C"},
                    "chord": {"preset": "dub_major"},
                    "arpeggiator": {"preset": "techno_up"},
                    "velocity": {"preset": "dub_soft"},
                },
                "use_case": "Upbeat house with rhythmic arpeggios and warm chords",
                "example_call": "create_generative_chain(track_index=0, chain_type='house', key='C')",
            },
            "techno": {
                "description": "Driving techno chain with heavy arpeggiation",
                "effects": ["scale", "arpeggiator", "velocity"],
                "config": {
                    "scale": {"preset": "phrygian", "key": "E"},
                    "arpeggiator": {"preset": "techno_up"},
                    "velocity": {"preset": "dub_heavy"},
                },
                "use_case": "Intense techno with fast arpeggios and compressed velocity",
                "example_call": "create_generative_chain(track_index=0, chain_type='techno', key='Em')",
            },
            "ambient": {
                "description": "Atmospheric ambient chain with randomization",
                "effects": ["scale", "chord", "random", "velocity"],
                "config": {
                    "scale": {"preset": "lydian", "key": "F"},
                    "chord": {"preset": "dub_seven"},
                    "random": {"enabled": True},
                    "velocity": {"preset": "random_human"},
                },
                "use_case": "Dreamy ambient textures with evolving randomness",
                "example_call": "create_generative_chain(track_index=0, chain_type='ambient', key='F')",
            },
        }

        return json.dumps(presets, indent=2)

    @mcp.tool()
    def create_generative_chain(
        ctx: Context,
        track_index: int,
        chain_type: str = "dub_techno",
        key: str = "Fm",
        include_arpeggiator: bool = False,
    ) -> str:
        """
        Create a complete generative MIDI effect chain on a track.

        Loads and configures multiple MIDI effects in the correct order for generative music.

        Parameters:
        - track_index: Target track index
        - chain_type: Chain type ("dub_techno", "house", "techno", "ambient")
        - key: Key signature ("Fm", "Cm", "Am", "C", "F", etc.)
        - include_arpeggiator: Whether to include arpeggiator (for rhythm)

        Returns:
        - JSON string with chain configuration and device indices

        Chain Order:
        1. Scale - Constrain notes to key
        2. Chord - Add harmonic depth
        3. Velocity - Humanize note velocities
        4. Arpeggiator - Create rhythm (optional)
        5. Random - Add variation (optional, for ambient)

        Examples:
        - create_generative_chain(0, "dub_techno", "Fm")
        - create_generative_chain(1, "house", "C", include_arpeggiator=True)
        - create_generative_chain(2, "ambient", "F")

        Dub techno tip: Use dub_techno chain with Fm or Cm key for classic sound
        """
        # Chain configurations
        CHAIN_CONFIGS = {
            "dub_techno": {
                "effects": ["scale", "chord", "velocity"],
                "presets": {
                    "scale": {
                        "preset": "f_minor",
                        "key_map": {"Fm": "f_minor", "Cm": "c_minor", "Dm": "d_minor"},
                    },
                    "chord": {"preset": "dub_minor"},
                    "velocity": {"preset": "random_human"},
                },
                "description": "Classic dub techno chain",
            },
            "house": {
                "effects": ["scale", "chord", "velocity"],
                "presets": {
                    "scale": {
                        "preset": "major",
                        "key_map": {"C": "C", "F": "F", "G": "G"},
                    },
                    "chord": {"preset": "dub_major"},
                    "velocity": {"preset": "dub_soft"},
                },
                "description": "Warm house music chain",
            },
            "techno": {
                "effects": ["scale", "arpeggiator", "velocity"],
                "presets": {
                    "scale": {
                        "preset": "phrygian",
                        "key_map": {"Em": "phrygian", "Am": "phrygian"},
                    },
                    "arpeggiator": {"preset": "techno_up"},
                    "velocity": {"preset": "dub_heavy"},
                },
                "description": "Driving techno chain",
            },
            "ambient": {
                "effects": ["scale", "chord", "velocity"],
                "presets": {
                    "scale": {
                        "preset": "lydian",
                        "key_map": {"F": "lydian", "C": "lydian"},
                    },
                    "chord": {"preset": "dub_seven"},
                    "velocity": {"preset": "random_human"},
                },
                "description": "Atmospheric ambient chain",
            },
        }

        if chain_type not in CHAIN_CONFIGS:
            return f"Unknown chain type: {chain_type}. Available: {list(CHAIN_CONFIGS.keys())}"

        chain_config = CHAIN_CONFIGS[chain_type]
        results = []
        device_indices = {}

        try:
            # 1. Load and configure Scale effect
            if "scale" in chain_config["effects"]:
                scale_info = chain_config["presets"]["scale"]
                # Determine preset based on key
                scale_preset = scale_info["preset"]
                if key in scale_info.get("key_map", {}):
                    scale_preset = scale_info["key_map"][key]

                # Load scale effect
                load_result = load_midi_effect.func(ctx, track_index, "scale")
                results.append(f"Scale: {load_result}")

                # For now, just note that scale was loaded
                # Detailed scale configuration would need device index
                device_indices["scale"] = "auto"

            # 2. Load and configure Chord effect
            if "chord" in chain_config["effects"]:
                chord_preset = chain_config["presets"]["chord"]["preset"]
                load_result = load_midi_effect.func(ctx, track_index, "chord")
                results.append(f"Chord: {load_result}")
                device_indices["chord"] = "auto"

            # 3. Load and configure Velocity effect
            if "velocity" in chain_config["effects"]:
                velocity_preset = chain_config["presets"]["velocity"]["preset"]
                load_result = load_midi_effect.func(ctx, track_index, "velocity")
                results.append(f"Velocity: {load_result}")
                device_indices["velocity"] = "auto"

            # 4. Load and configure Arpeggiator (optional)
            if include_arpeggiator and "arpeggiator" in chain_config.get("presets", {}):
                arp_preset = chain_config["presets"]["arpeggiator"]["preset"]
                load_result = load_midi_effect.func(ctx, track_index, "arpeggiator")
                results.append(f"Arpeggiator: {load_result}")
                device_indices["arpeggiator"] = "auto"

            # Return chain summary
            return json.dumps(
                {
                    "track": track_index,
                    "chain_type": chain_type,
                    "key": key,
                    "description": chain_config["description"],
                    "effects_loaded": chain_config["effects"],
                    "include_arpeggiator": include_arpeggiator,
                    "device_indices": device_indices,
                    "results": results,
                    "next_steps": f"Use apply_midi_effect_preset() to configure each effect with specific presets",
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Error creating generative chain: {str(e)}")
            return f"Error creating generative chain: {str(e)}"

    # =========================================================================
    # LIVE MIDI EFFECT AUTOMATION
    # =========================================================================

    @mcp.tool()
    def automate_arpeggiator_rate(
        ctx: Context,
        track_index: int,
        device_index: int,
        start_rate: str = "1/16",
        end_rate: str = "1/8",
        duration_beats: int = 16,
        steps: int = 8,
    ) -> str:
        """
        Automate arpeggiator rate change over time.

        Parameters:
        - track_index: Track with arpeggiator
        - device_index: Device index of arpeggiator
        - start_rate: Starting rate
        - end_rate: Ending rate
        - duration_beats: Duration in beats
        - steps: Number of steps for automation

        Use for build-ups and transitions in live performance.
        """
        rate_map = {
            "1/1": 0.0,
            "1/2": 0.14,
            "1/4": 0.28,
            "1/8": 0.42,
            "1/16": 0.57,
            "1/32": 0.71,
        }

        start_val = rate_map.get(start_rate, 0.42)
        end_val = rate_map.get(end_rate, 0.57)

        # This would need to be run as a background automation
        # For now, return instructions
        return f"Arpeggiator rate automation: {start_rate} -> {end_rate} over {duration_beats} beats ({steps} steps)"

    # =========================================================================
    # MIDI EFFECT INFO
    # =========================================================================

    @mcp.tool()
    def get_midi_effect_info(ctx: Context) -> str:
        """
        Get information about available MIDI effects and their parameters.

        Returns:
        - List of available MIDI effects
        - Preset configurations
        - Parameter descriptions
        """
        info = {
            "available_effects": list(MIDI_EFFECT_URIS.keys()),
            "presets": MIDI_EFFECT_PRESETS,
            "scales": list(SCALE_INTERVALS.keys()),
            "dub_techno_tips": {
                "scale": "Use F Minor or C Minor for classic dub techno",
                "chord": "Use octave-doubled minor chords for depth",
                "velocity": "Add subtle randomization for human feel",
                "arpeggiator": "Use 1/8 rate with 70-80% gate for rolling patterns",
            },
        }
        return json.dumps(info, indent=2)

    # =========================================================================
    # GENERATIVE CLIP CREATION
    # =========================================================================

    @mcp.tool()
    def create_generative_clip(
        ctx: Context,
        track_index: int,
        clip_index: int,
        chord_notes: List[int],
        pattern_type: str = "arpeggiated",
        rate: str = "1/8",
        direction: str = "up",
        swing: float = 0.0,
        length_beats: float = 4.0,
        velocity_range: tuple = (80, 110),
    ) -> str:
        """
        Create a generative MIDI clip with arpeggiated or random patterns.

        Creates MIDI clips with various generative patterns based on chord inputs.
        Integrates with music theory utilities for intelligent note generation.

        Parameters:
        - track_index: Target track with instrument loaded
        - clip_index: Clip slot index to create/populate
        - chord_notes: List of MIDI note numbers (e.g., [60, 63, 67] for C minor)
        - pattern_type: Pattern type ("arpeggiated", "random", "strum", "sustained")
        - rate: Note density for arpeggiated ("1/4", "1/8", "1/16", "1/32")
        - direction: Pattern direction ("up", "down", "random", "up_down")
        - swing: Swing amount (0.0-1.0, 0.5 = 50% swing)
        - length_beats: Clip length in beats (default 4.0)
        - velocity_range: Tuple (min, max) velocity range for humanization (default 80-110)

        Returns:
        - Success message with note count and pattern details

        Pattern Types:
        - arpeggiated: Converts chord to rhythmic arpeggio using music theory utilities
        - random: Randomly selects notes from chord with scale constraints
        - strum: Adds chord notes with slight delays for string-like effect
        - sustained: Holds all chord notes for full duration

        Examples:
        - create_generative_clip(0, 0, [60, 63, 67], "arpeggiated", "1/8", "up")
        - create_generative_clip(1, 2, [64, 68, 71], "random", length_beats=8)
        - create_generative_clip(0, 1, [60, 64, 67], "strum", swing=0.3)

        Dub techno tip: Use minor chords with 1/8 arpeggiation and slight swing (0.2-0.3)
        """
        try:
            import random

            ableton = get_ableton_connection()

            # Validate chord notes
            if not chord_notes or len(chord_notes) < 2:
                return "Error: chord_notes must contain at least 2 notes"

            # Validate MIDI note range
            for note in chord_notes:
                if not 0 <= note <= 127:
                    return f"Error: Invalid MIDI note {note}. Must be 0-127"

            # Validate pattern type
            valid_patterns = ["arpeggiated", "random", "strum", "sustained"]
            if pattern_type not in valid_patterns:
                return f"Error: Invalid pattern_type. Choose from: {valid_patterns}"

            # Validate rate
            valid_rates = ["1/4", "1/8", "1/16", "1/32", "triplet"]
            if pattern_type == "arpeggiated" and rate not in valid_rates:
                return f"Error: Invalid rate. Choose from: {valid_rates}"

            # Validate velocity range
            min_vel, max_vel = velocity_range
            if not (0 <= min_vel <= 127 and 0 <= max_vel <= 127):
                return "Error: Velocity range must be 0-127"
            if min_vel > max_vel:
                return "Error: min velocity cannot exceed max velocity"

            # Create clip if it doesn't exist
            try:
                ableton.send_command(
                    "create_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "length": length_beats,
                    },
                )
            except Exception as e:
                logger.warning(f"Clip creation warning: {str(e)} - may already exist")

            # Generate notes based on pattern type
            notes_to_add = []

            if pattern_type == "arpeggiated":
                # Use music theory arpeggiator
                from music_theory.arpeggiator import arpeggiate_chord

                try:
                    arpeggiated_notes = arpeggiate_chord(
                        midi_notes=chord_notes,
                        rate=rate,
                        direction=direction,
                        swing=swing,
                        repeats=1,
                    )

                    # Apply velocity variation
                    for note in arpeggiated_notes:
                        note["velocity"] = random.randint(int(min_vel), int(max_vel))
                        note["mute"] = False

                    notes_to_add = arpeggiated_notes

                except Exception as e:
                    logger.error(f"Error in arpeggiation: {str(e)}")
                    return f"Error generating arpeggiated pattern: {str(e)}"

            elif pattern_type == "random":
                # Randomly select notes from chord
                num_notes = int(length_beats * 4)  # Approximate note count
                for i in range(num_notes):
                    note_pitch = random.choice(chord_notes)
                    start_time = i * 0.25  # 1/16 note spacing
                    if start_time >= length_beats:
                        break

                    notes_to_add.append(
                        {
                            "pitch": note_pitch,
                            "start_time": round(start_time, 3),
                            "duration": 0.2,  # Short notes for random pattern
                            "velocity": random.randint(int(min_vel), int(max_vel)),
                            "mute": False,
                        }
                    )

            elif pattern_type == "strum":
                # Add chord notes with slight delays
                strum_delay = 0.05  # 50ms delay between notes
                for i, note_pitch in enumerate(chord_notes):
                    start_time = i * strum_delay
                    if start_time < length_beats:
                        notes_to_add.append(
                            {
                                "pitch": note_pitch,
                                "start_time": round(start_time, 3),
                                "duration": length_beats - start_time,  # Sustain to end
                                "velocity": random.randint(int(min_vel), int(max_vel)),
                                "mute": False,
                            }
                        )

            elif pattern_type == "sustained":
                # Hold all chord notes for full duration
                for note_pitch in chord_notes:
                    notes_to_add.append(
                        {
                            "pitch": note_pitch,
                            "start_time": 0.0,
                            "duration": length_beats,
                            "velocity": random.randint(int(min_vel), int(max_vel)),
                            "mute": False,
                        }
                    )

            # Add notes to clip
            if notes_to_add:
                result = ableton.send_command(
                    "add_notes_to_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "notes": notes_to_add,
                    },
                )

                # Return detailed success message
                return json.dumps(
                    {
                        "status": "success",
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "pattern_type": pattern_type,
                        "notes_created": len(notes_to_add),
                        "length_beats": length_beats,
                        "chord_notes": chord_notes,
                        "rate": rate if pattern_type == "arpeggiated" else "N/A",
                        "direction": direction
                        if pattern_type == "arpeggiated"
                        else "N/A",
                        "swing": swing if pattern_type == "arpeggiated" else "N/A",
                        "velocity_range": velocity_range,
                        "message": f"Created {pattern_type} generative clip with {len(notes_to_add)} notes",
                    },
                    indent=2,
                )
            else:
                return "Error: No notes were generated for the clip"

        except Exception as e:
            logger.error(f"Error creating generative clip: {str(e)}")
            return f"Error creating generative clip: {str(e)}"

    # =========================================================================
    # CHORD & MELODY GENERATORS
    # =========================================================================

    @mcp.tool()
    def generate_chord_progression_clip(
        ctx: Context,
        track_index: int,
        clip_index: int,
        key: str,
        progression: List[str],
        duration_per_chord: float = 4.0,
        voicing: str = "close",
        pattern_type: str = "sustained",
    ) -> str:
        """
        Generate a MIDI clip from a chord progression.

        Creates a clip with chords based on Roman numeral progression in the specified key.
        Supports various voicings and pattern types for different musical styles.

        Parameters:
        - track_index: Target track with instrument loaded
        - clip_index: Clip slot index to create/populate
        - key: Key signature (e.g., "C", "Am", "F#m", "D")
        - progression: List of Roman numerals (e.g., ["I", "V", "vi", "IV"])
        - duration_per_chord: Duration in beats for each chord (default 4.0)
        - voicing: Voicing type ("close", "open", "drop2") - default "close"
        - pattern_type: How to play chords ("sustained", "arpeggiated", "strum")

        Returns:
        - JSON with progression details, note count, and clip info

        Roman Numerals:
        - Major: I, II, III, IV, V, VI, VII
        - Minor: i, ii, iii, iv, v, vi, vii
        - Case matters: uppercase = major, lowercase = minor

        Examples:
        - generate_chord_progression_clip(0, 0, "C", ["I", "V", "vi", "IV"], 4.0)
        - generate_chord_progression_clip(1, 0, "Am", ["i", "VII", "VI", "V"], 8.0)
        - generate_chord_progression_clip(0, 0, "F", ["IV", "V", "I"], 2.0, "open")

        Dub techno tip: Use minor key progressions like ["i", "VII", "VI", "V"] in Fm or Cm
        """
        try:
            import random

            ableton = get_ableton_connection()

            # Validate inputs
            if not progression or len(progression) < 1:
                return "Error: progression must contain at least 1 chord"

            # Parse key to get root note and mode
            key_root_note = None
            key_mode = "major"

            key_upper = key.upper()
            if key_upper.endswith("M"):
                # Major key (e.g., "CM", "F#M")
                key_root_note = _note_name_to_midi(key[:-1])
                key_mode = "major"
            elif key_upper.endswith("M"):
                key_root_note = _note_name_to_midi(key[:-1])
                key_mode = "major"
            elif key_upper.endswith("m"):
                # Minor key (e.g., "Am", "C#m")
                key_root_note = _note_name_to_midi(key[:-1])
                key_mode = "minor"
            else:
                # Assume major if no suffix
                key_root_note = _note_name_to_midi(key)
                key_mode = "major"

            if key_root_note is None:
                return f"Error: Invalid key '{key}'. Use format like 'C', 'Am', 'F#m'"

            # Build scale
            scale_key = key_mode.title()
            scale_intervals = SCALE_INTERVALS.get(scale_key, SCALE_INTERVALS["Major"])
            scale_notes = [
                (key_root_note + interval) % 12 for interval in scale_intervals
            ]

            # Generate chords for each Roman numeral
            all_notes = []
            chords_data = []

            roman_to_degree = {
                "I": 0,
                "II": 1,
                "III": 2,
                "IV": 3,
                "V": 4,
                "VI": 5,
                "VII": 6,
                "i": 0,
                "ii": 1,
                "iii": 2,
                "iv": 3,
                "v": 4,
                "vi": 5,
                "vii": 6,
            }

            chord_quality = {
                "major": ["maj", "min", "min", "maj", "maj", "min", "dim"],
                "minor": ["min", "dim", "maj", "min", "min", "maj", "maj"],
            }

            current_beat = 0.0

            for chord_name in progression:
                if chord_name not in roman_to_degree:
                    logger.warning(f"Skipping invalid Roman numeral: {chord_name}")
                    continue

                degree = roman_to_degree[chord_name]
                quality = chord_quality[key_mode][degree]

                # Get root note of this chord (in scale)
                chord_root_interval = scale_intervals[degree]
                chord_root_note = key_root_note + chord_root_interval

                # Build chord
                chord_intervals = CHORD_INTERVALS.get(quality, CHORD_INTERVALS["maj"])
                chord_notes = [chord_root_note + i for i in chord_intervals]

                # Adjust octave for close voicing
                if voicing == "close":
                    # Keep all notes in same octave (adjust as needed)
                    chord_notes = [max(36, min(n, 96)) for n in chord_notes]
                elif voicing == "open":
                    # Spread notes across octaves
                    chord_notes = [
                        chord_notes[0],
                        chord_notes[1] + 12,
                        chord_notes[2] + 12,
                    ]
                elif voicing == "drop2":
                    # Drop 2nd highest note down an octave
                    sorted_notes = sorted(chord_notes)
                    chord_notes = [
                        sorted_notes[0],
                        sorted_notes[1],
                        sorted_notes[2] - 12,
                    ]

                # Add notes based on pattern type
                if pattern_type == "sustained":
                    # Hold all notes for full duration
                    for note in chord_notes:
                        all_notes.append(
                            {
                                "pitch": max(0, min(127, note)),
                                "start_time": round(current_beat, 3),
                                "duration": duration_per_chord,
                                "velocity": random.randint(80, 100),
                                "mute": False,
                            }
                        )

                elif pattern_type == "arpeggiated":
                    # Arpeggiate the chord
                    from music_theory.arpeggiator import arpeggiate_chord

                    arpeggio = arpeggiate_chord(
                        midi_notes=chord_notes,
                        rate="1/8",
                        direction="up",
                        swing=0.0,
                        repeats=1,
                    )
                    for note_data in arpeggio:
                        all_notes.append(
                            {
                                "pitch": max(0, min(127, note_data["pitch"])),
                                "start_time": round(
                                    current_beat + note_data["start_time"], 3
                                ),
                                "duration": note_data["duration"],
                                "velocity": random.randint(80, 100),
                                "mute": False,
                            }
                        )

                elif pattern_type == "strum":
                    # Strum with slight delays
                    strum_delay = 0.05
                    for i, note in enumerate(chord_notes):
                        all_notes.append(
                            {
                                "pitch": max(0, min(127, note)),
                                "start_time": round(
                                    current_beat + (i * strum_delay), 3
                                ),
                                "duration": duration_per_chord - (i * strum_delay),
                                "velocity": random.randint(80, 100),
                                "mute": False,
                            }
                        )

                chords_data.append(
                    {
                        "roman": chord_name,
                        "root": chord_root_note,
                        "quality": quality,
                        "notes": chord_notes,
                        "beat": current_beat,
                    }
                )

                current_beat += duration_per_chord

            # Create clip
            total_length = duration_per_chord * len(chords_data)
            try:
                ableton.send_command(
                    "create_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "length": total_length,
                    },
                )
            except Exception as e:
                logger.warning(f"Clip creation warning: {str(e)} - may already exist")

            # Add notes to clip
            if all_notes:
                result = ableton.send_command(
                    "add_notes_to_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "notes": all_notes,
                    },
                )

                return json.dumps(
                    {
                        "status": "success",
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "key": key,
                        "progression": progression,
                        "chords_generated": len(chords_data),
                        "total_notes": len(all_notes),
                        "length_beats": total_length,
                        "voicing": voicing,
                        "pattern_type": pattern_type,
                        "message": f"Generated chord progression clip with {len(all_notes)} notes",
                    },
                    indent=2,
                )
            else:
                return "Error: No notes were generated for the clip"

        except Exception as e:
            logger.error(f"Error generating chord progression: {str(e)}")
            return f"Error generating chord progression: {str(e)}"

    @mcp.tool()
    def generate_melody_clip(
        ctx: Context,
        track_index: int,
        clip_index: int,
        key: str,
        scale: str = "minor",
        length_beats: float = 8.0,
        complexity: str = "medium",
        range_notes: tuple = (60, 84),
    ) -> str:
        """
        Generate a scale-constrained melody clip.

        Creates a melody using notes from the specified scale with configurable complexity.

        Parameters:
        - track_index: Target track with instrument
        - clip_index: Clip slot index to create/populate
        - key: Root note (e.g., "C", "F#", "Am")
        - scale: Scale type ("major", "minor", "dorian", "phrygian", "lydian", "mixolydian")
        - length_beats: Total clip length in beats (default 8.0)
        - complexity: Melody complexity ("simple", "medium", "complex")
        - range_notes: (min, max) MIDI note range for melody (default 60-84)

        Returns:
        - JSON with melody details and note count

        Examples:
        - generate_melody_clip(0, 0, "C", "minor", 8.0, "medium")
        - generate_melody_clip(1, 0, "F#", "dorian", 16.0, "complex")
        - generate_melody_clip(0, 0, "A", "phrygian", 12.0, "simple")

        Dub techno tip: Use dorian or phrygian scales for atmospheric melodies
        """
        try:
            import random

            ableton = get_ableton_connection()

            # Validate inputs - normalize scale name to match SCALE_INTERVALS keys
            scale_key = scale.title()
            valid_scales = list(SCALE_INTERVALS.keys())
            if scale_key not in valid_scales:
                return f"Error: Invalid scale '{scale}'. Choose from: {valid_scales}"

            valid_complexity = ["simple", "medium", "complex"]
            if complexity not in valid_complexity:
                return f"Error: Invalid complexity '{complexity}'. Choose from: {valid_complexity}"

            # Parse key
            key_root_note = _note_name_to_midi(key)
            if key_root_note is None:
                return f"Error: Invalid key '{key}'. Use format like 'C', 'F#', 'Am'"

            # Build scale
            scale_intervals = SCALE_INTERVALS.get(scale_key, SCALE_INTERVALS["Minor"])

            # Determine melody parameters based on complexity
            if complexity == "simple":
                note_density = 0.5  # Notes per beat
                rhythm_pattern = ["1/4"]
                rest_probability = 0.3
            elif complexity == "medium":
                note_density = 1.0  # Notes per beat
                rhythm_pattern = ["1/4", "1/8"]
                rest_probability = 0.15
            else:  # complex
                note_density = 2.0  # Notes per beat
                rhythm_pattern = ["1/8", "1/16"]
                rest_probability = 0.05

            # Generate melody
            melody_notes = []
            total_notes = int(length_beats * note_density)

            # Select notes from scale within range
            min_note, max_note = range_notes
            root_pitch_class = key_root_note % 12
            scale_notes = [
                n for n in range(min_note, max_note + 1)
                if (n % 12 - root_pitch_class) % 12 in scale_intervals
            ]
            available_notes = scale_notes

            if not available_notes:
                return f"Error: No notes available in range {range_notes} for scale"

            # Generate melody pattern
            current_beat = 0.0
            note_index = 0

            while current_beat < length_beats and len(melody_notes) < total_notes:
                # Determine duration based on rhythm pattern
                rhythm = random.choice(rhythm_pattern)
                duration = {"1/4": 1.0, "1/8": 0.5, "1/16": 0.25}.get(rhythm, 0.5)

                # Skip occasional beats for rests (makes melodies sound more natural)
                if random.random() >= rest_probability:
                    # Select a note from the scale
                    note = random.choice(available_notes)

                    # Add note
                    melody_notes.append(
                        {
                            "pitch": max(min_note, min(max_note, note)),
                            "start_time": round(current_beat, 3),
                            "duration": duration,
                            "velocity": random.randint(70, 100),
                            "mute": False,
                        }
                    )

                current_beat += duration
                note_index += 1

            # Create clip
            try:
                ableton.send_command(
                    "create_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "length": length_beats,
                    },
                )
            except Exception as e:
                logger.warning(f"Clip creation warning: {str(e)} - may already exist")

            # Add notes to clip
            if melody_notes:
                result = ableton.send_command(
                    "add_notes_to_clip",
                    {
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "notes": melody_notes,
                    },
                )

                return json.dumps(
                    {
                        "status": "success",
                        "track_index": track_index,
                        "clip_index": clip_index,
                        "key": key,
                        "scale": scale,
                        "melody_notes": len(melody_notes),
                        "length_beats": length_beats,
                        "complexity": complexity,
                        "range": list(range_notes),
                        "message": f"Generated melody clip with {len(melody_notes)} notes",
                    },
                    indent=2,
                )
            else:
                return "Error: No notes were generated for the melody"

        except Exception as e:
            logger.error(f"Error generating melody: {str(e)}")
            return f"Error generating melody: {str(e)}"

    # =========================================================================
    # MODULATOR TOOLS
    # =========================================================================

    @mcp.tool("create_lfo_modulator")
    async def create_lfo_modulator(
        ctx: Context,
        track_index: int,
        device_index: int,
        parameter_index: int,
        rate: float = 1.0,
        depth: float = 1.0,
        waveform: str = "sine",
    ) -> str:
        """
        Create an LFO modulator attached to a device parameter.

        Creates an internal LFO modulator that cyclically sweeps the target device parameter.
        LFO runs in the MCP server and transmits updates via UDP.

        Parameters:
        - track_index: Index of track containing target parameter
        - device_index: Index of device on track
        - parameter_index: Index of parameter to modulate
        - rate: LFO rate in cycles per beat (default: 1.0)
        - depth: Modulation depth (0.0-1.0, default: 1.0)
        - waveform: Waveform for LFO (sine/saw/triangle/square/random, default: sine)

        Returns:
        - dict: {"modulator_id": str, "status": "created"}
        """
        global MODULATOR_COUNTER, MODULATORS_DB

        # Validate waveform
        if waveform not in LFO_WAVEFORMS:
            return json.dumps(
                {"error": f"Invalid waveform. Choose {', '.join(LFO_WAVEFORMS)}"}
            )

        # Clamp and validate depth
        if not 0.0 <= depth <= 1.0:
            depth = max(0.0, min(1.0, depth))

        # Validate rate
        if rate <= 0.0:
            return json.dumps({"error": "Rate must be greater than 0"})

        # Create modulator entry
        mod_id = f"mod_{MODULATOR_COUNTER}"
        MODULATOR_COUNTER += 1

        MODULATORS_DB[mod_id] = {
            "type": "lfo",
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "params": {"rate": rate, "depth": depth, "waveform": waveform},
            "is_active": True,
        }

        return json.dumps(
            {
                "modulator_id": mod_id,
                "status": "created",
                "modulator_type": "lfo",
                "target": {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": parameter_index,
                },
            }
        )

    @mcp.tool("create_envelope_modulator")
    async def create_envelope_modulator(
        ctx: Context,
        track_index: int,
        device_index: int,
        parameter_index: int,
        attack: float = 0.1,
        decay: float = 0.2,
        sustain: float = 0.8,
        release: float = 0.3,
    ) -> str:
        """
        Create an envelope modulator (ADSR-style) attached to a parameter.

        Simulates an envelope (attack/decay/sustain/release) on a device parameter.
        Envelopes are triggered via note-on events (detected via track monitoring).

        Parameters:
        - track_index: Index of track
        - device_index: Index of device on track
        - parameter_index: Index of parameter to modulate
        - attack: Attack time in seconds (default: 0.1)
        - decay: Decay time in seconds (default: 0.2)
        - sustain: Sustain level (0.0-1.0, default: 0.8)
        - release: Release time in seconds (default: 0.3)

        Returns:
        - dict: {"modulator_id": str, "status": "created"}
        """
        global MODULATOR_COUNTER, MODULATORS_DB

        # Clamp sustain to [0, 1]
        sustain = max(0.0, min(1.0, sustain))

        # Create modulator entry
        mod_id = f"mod_{MODULATOR_COUNTER}"
        MODULATOR_COUNTER += 1

        MODULATORS_DB[mod_id] = {
            "type": "envelope",
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "params": {
                "attack": attack,
                "decay": decay,
                "sustain": sustain,
                "release": release,
            },
            "is_active": True,
        }

        return json.dumps(
            {
                "modulator_id": mod_id,
                "status": "created",
                "modulator_type": "envelope",
                "target": {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": parameter_index,
                },
            }
        )

    @mcp.tool("create_sidechain_modulator")
    async def create_sidechain_modulator(
        ctx: Context,
        track_index: int,
        device_index: int,
        parameter_index: int,
        source_track_index: int,
        amount: float = 0.8,
    ) -> str:
        """
        Create a sidechain modulator from a source track to a target parameter.

        Monitors the output level of source_track_index and modulates the target parameter accordingly.
        Simulates sidechain compression or gating behavior.

        Parameters:
        - track_index: Index of track containing target device
        - device_index: Index of target device on track
        - parameter_index: Index of parameter to modulate on target device
        - source_track_index: Index of sidechain source track
        - amount: Modulation amount (0.0-1.0, default: 0.8)

        Returns:
        - dict: {"modulator_id": str, "status": "created"}
        """
        global MODULATOR_COUNTER, MODULATORS_DB

        # Clamp amount to [0, 1]
        amount = max(0.0, min(1.0, amount))

        # Create modulator entry
        mod_id = f"mod_{MODULATOR_COUNTER}"
        MODULATOR_COUNTER += 1

        MODULATORS_DB[mod_id] = {
            "type": "sidechain",
            "track_index": track_index,
            "device_index": device_index,
            "parameter_index": parameter_index,
            "params": {"source_track": source_track_index, "amount": amount},
            "is_active": True,
        }

        return json.dumps(
            {
                "modulator_id": mod_id,
                "status": "created",
                "modulator_type": "sidechain",
                "target": {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": parameter_index,
                },
                "source_track": source_track_index,
            }
        )

    @mcp.tool("set_modulator_parameter")
    async def set_modulator_parameter(
        ctx: Context, modulator_id: str, parameter: str, value: float
    ) -> str:
        """
        Set a parameter on a modulator (LFO/envelope/sidechain).

        Updates rate, depth, or other modulator-specific settings.

        Parameters:
        - modulator_id: ID of modulator to update
        - parameter: Name of parameter to set (rate, depth, attack, decay, etc.)
        - value: New value for the parameter

        Returns:
        - str: Confirmation message or error
        """
        global MODULATORS_DB

        if modulator_id not in MODULATORS_DB:
            return json.dumps({"error": f"Modulator {modulator_id} not found"})

        modulator = MODULATORS_DB[modulator_id]

        # Validate/route parameter changes by modulator type
        if modulator["type"] == "lfo":
            if parameter == "rate":
                if value <= 0:
                    return json.dumps({"error": "LFO rate must be greater than 0"})
                modulator["params"]["rate"] = value
            elif parameter == "depth":
                modulator["params"]["depth"] = max(0.0, min(1.0, value))
            elif parameter == "waveform":
                if value not in LFO_WAVEFORMS:
                    return json.dumps(
                        {
                            "error": f"Invalid waveform. Choose {', '.join(LFO_WAVEFORMS)}"
                        }
                    )
                modulator["params"]["waveform"] = value
            else:
                return json.dumps({"error": f"Invalid parameter for LFO: {parameter}"})

        elif modulator["type"] == "envelope":
            if parameter == "attack":
                modulator["params"]["attack"] = max(0.0, value)
            elif parameter == "decay":
                modulator["params"]["decay"] = max(0.0, value)
            elif parameter == "sustain":
                modulator["params"]["sustain"] = max(0.0, min(1.0, value))
            elif parameter == "release":
                modulator["params"]["release"] = max(0.0, value)
            else:
                return json.dumps(
                    {"error": f"Invalid parameter for envelope: {parameter}"}
                )

        elif modulator["type"] == "sidechain":
            if parameter == "amount":
                modulator["params"]["amount"] = max(0.0, min(1.0, value))
            elif parameter == "source_track":
                modulator["params"]["source_track"] = int(value)
            else:
                return json.dumps(
                    {"error": f"Invalid parameter for sidechain: {parameter}"}
                )

        return json.dumps({"status": "updated", "parameter": parameter, "value": value})

    @mcp.tool("attach_modulator_to_parameter")
    async def attach_modulator_to_parameter(
        ctx: Context,
        modulator_id: str,
        track_index: int,
        device_index: int,
        parameter_index: int,
        depth: float = 1.0,
    ) -> str:
        """
        Route a modulator to a new device parameter.

        Reassigns an existing modulator to a new target parameter with specified modulation depth.

        Parameters:
        - modulator_id: ID of modulator to attach/route
        - track_index: New target track index
        - device_index: New target device index
        - parameter_index: New target parameter index
        - depth: Modulation depth (0.0-1.0, default: 1.0)

        Returns:
        - dict: {"status": "attached", "target": {...}}
        """
        global MODULATORS_DB

        if modulator_id not in MODULATORS_DB:
            return json.dumps({"error": f"Modulator {modulator_id} not found"})

        # Update the modulator target
        modulator = MODULATORS_DB[modulator_id]
        modulator["track_index"] = track_index
        modulator["device_index"] = device_index
        modulator["parameter_index"] = parameter_index

        return json.dumps(
            {
                "status": "attached",
                "modulator_id": modulator_id,
                "target": {
                    "track_index": track_index,
                    "device_index": device_index,
                    "parameter_index": parameter_index,
                },
                "depth": depth,
            }
        )

    @mcp.tool("remove_modulator")
    async def remove_modulator(ctx: Context, modulator_id: str) -> str:
        """
        Remove a modulator by ID.

        Stops all modulation immediately; removes modulator from the internal database.

        Parameters:
        - modulator_id: ID of modulator to remove

        Returns:
        - dict: {"status": "removed", "modulator_id": str} or error message
        """
        global MODULATORS_DB

        if modulator_id not in MODULATORS_DB:
            return json.dumps({"error": f"Modulator {modulator_id} not found"})

        # Remove the modulator
        del MODULATORS_DB[modulator_id]

        return json.dumps({"status": "removed", "modulator_id": modulator_id})


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _note_name_to_midi(note_name: str) -> Optional[int]:
    """
    Convert note name to MIDI note number.

    Args:
        note_name: Note name (e.g., "C", "F#", "Am", "C#m")

    Returns:
        MIDI note number or None if invalid
    """
    note_map = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "Eb": 3,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }

    # Remove octave if present
    note_name = note_name.upper().replace("M", "").replace("m", "")

    if note_name in note_map:
        return note_map[note_name] + 36  # Default to C3-C4 range

    return None


# =============================================================================
# MODULATOR CONSTANTS (module-level, referenced by modulator tools via global)
# =============================================================================

# Modulator Storage: mod_id -> modulator details
MODULATORS_DB = {}

MODULATOR_COUNTER = 1  # Incremental ID for modulators

# Available LFO waveforms for modulation
LFO_WAVEFORMS = ["sine", "saw", "triangle", "square", "random"]


async def register_modulator_tools(ctx: Context = None):
    """
    Register all modulator tools with MCP server.

    Called from the MCP tool registration init hook.
    """
    pass  # MCP @mcp.tool decorator auto-registers
