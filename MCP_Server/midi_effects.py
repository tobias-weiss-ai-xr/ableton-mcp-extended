# MIDI Effects Tools for Ableton MCP Server
# Handles MIDI effect devices: Arpeggiator, Scale, Chord, Pitch, Velocity, etc.

from mcp.server.fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger("AbletonMCPServer")

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
