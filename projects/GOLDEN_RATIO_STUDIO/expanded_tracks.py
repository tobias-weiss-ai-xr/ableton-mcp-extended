#!/usr/bin/env python3
"""
Expanded tracks for genres with minimal instrumentation.
Adds snare, percussion, and additional elements to hip-hop, trap, dnb, etc.
"""

from generate_all_genres_refactored import (
    PatternGenerator, MIDINote, Genre, TrackType, MIDIConstants
)
import random
from typing import List

class HipHopSnarePattern(PatternGenerator):
    """Hip-hop snare pattern (boom-bap style)."""
    
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        notes = []
        for bar in range(bar_count):
            for beat in range(4):
                if beat in [1, 3]:  # Snares on 2 and 4
                    time = bar * 4 + beat
                    velocity = 110 if beat == 1 else 102
                    snare = MIDINote(time, MIDIConstants.SNARE, velocity, 0.2)
                    notes.append(self._humanize(snare, 
                                              velocity_var=0.15,
                                              timing_var=0.12))
        return notes

class HipHopHiHatPattern(PatternGenerator):
    """Hip-hop hi-hat pattern with variations."""
    
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        notes = []
        patterns = [
            [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],  # 8th notes
            [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],  # 8th notes
            [0, 0.5, 1.5, 2, 2.5, 3.5],      # Skip some
            [0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75],  # 16th notes (roll)
        ]
        
        for bar in range(bar_count):
            pattern = patterns[bar % len(patterns)]
            for time_offset in pattern:
                time = bar * 4 + time_offset
                velocity = 80 if time_offset % 1 == 0 else 70
                hihat = MIDINote(time, MIDIConstants.HI_HAT_CLOSED, velocity, 0.05)
                notes.append(self._humanize(hihat,
                                            velocity_var=0.10,
                                            timing_var=0.08))
        return notes

class TrapHiHatPattern(PatternGenerator):
    """Trap hi-hat pattern with rapid 16th notes."""
    
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        notes = []
        for bar in range(bar_count):
            for beat in range(4):
                for subdivision in [0, 0.25, 0.5, 0.75]:  # 16th notes
                    time = bar * 4 + beat + subdivision
                    velocity = 85 if subdivision in [0, 0.5] else 75
                    hihat = MIDINote(time, MIDIConstants.HI_HAT_CLOSED, velocity, 0.04)
                    notes.append(self._humanize(hihat,
                                                velocity_var=0.12,
                                                timing_var=0.06))
        return notes

class DnBPercussionPattern(PatternGenerator):
    """DnB percussion with cymbals and additional elements."""
    
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        notes = []
        for bar in range(bar_count):
            # Crash cymbal on bar 0 and 4
            if bar % 4 == 0:
                time = bar * 4 + 0
                crash = MIDINote(time, MIDIConstants.CRASH, 90, 2.0)
                notes.append(self._humanize(crash,
                                            velocity_var=0.08,
                                            timing_var=0.06))
            
            # Ride cymbal pattern
            for beat in [0, 2]:
                time = bar * 4 + beat
                ride = MIDINote(time, MIDIConstants.RIDE, 70, 3.5)
                notes.append(self._humanize(ride,
                                            velocity_var=0.10,
                                            timing_var=0.08))
            
            # Tom fills on bar 3
            if bar % 4 == 3:
                for i, tom_time in enumerate([0.5, 0.75, 1.0]):
                    time = bar * 4 + tom_time
                    tom_pitch = MIDIConstants.HIGH_TOM - (i * 3)
                    tom = MIDINote(time, tom_pitch, 95 - (i * 5), 0.1)
                    notes.append(self._humanize(tom,
                                                velocity_var=0.12,
                                                timing_var=0.10))
        return notes

class DubTechnoPercussionPattern(PatternGenerator):
    """Dub techno percussion with industrial elements."""
    
    def generate(self, bar_count: int, **kwargs) -> List[MIDINote]:
        notes = []
        for bar in range(bar_count):
            # Clap on offbeats
            for beat in [1, 3]:
                time = bar * 4 + beat
                clap = MIDINote(time, MIDIConstants.CLAP, 90, 0.15)
                notes.append(self._humanize(clap,
                                            velocity_var=0.12,
                                            timing_var=0.08))
            
            # Occasional crash (every 8 bars)
            if bar % 8 == 7:
                crash = MIDINote(bar * 4 + 3.75, MIDIConstants.CRASH, 80, 1.5)
                notes.append(self._humanize(crash,
                                            velocity_var=0.10,
                                            timing_var=0.08))
        return notes

class AmbientPadLayers(PatternGenerator):
    """Additional ambient pad layers for texture."""
    
    def generate(self, bar_count: int, key: str = "C minor", **kwargs) -> List[MIDINote]:
        notes = []
        
        # High drone layer
        drone_pitches = [60, 64, 67] if key == "C minor" else [59, 62, 65]
        
        for bar in range(bar_count):
            for pitch in drone_pitches:
                time = bar * 8
                duration = 4.0
                velocity = 25  # Very quiet background drone
                
                drone = MIDINote(time, pitch, velocity, duration)
                notes.append(self._humanize(drone,
                                            velocity_var=0.08,
                                            timing_var=0.15,
                                            duration_var=0.25))
        return notes

if __name__ == '__main__':
    print("Testing expanded track patterns...")
    
    # Test hip-hop snare
    snare = HipHopSnarePattern(Genre.HIP_HOP)
    snare_notes = snare.generate(8)
    print(f"Hip-Hop Snare: {len(snare_notes)} notes")
    
    # Test hihat
    hihat = HipHopHiHatPattern(Genre.HIP_HOP)
    hihat_notes = hihat.generate(8)
    print(f"Hip-Hop HiHat: {len(hihat_notes)} notes")
    
    # Test trap hihat
    trap_hihat = TrapHiHatPattern(Genre.TRAP)
    trap_notes = trap_hihat.generate(8)
    print(f"Trap HiHat: {len(trap_notes)} notes")
    
    # Test DnB percussion
    dnb_perc = DnBPercussionPattern(Genre.DNB)
    dnb_notes = dnb_perc.generate(16)
    print(f"DnB Percussion: {len(dnb_notes)} notes")
    
    # Test techno percussion
    techno = DubTechnoPercussionPattern(Genre.DUB_TECHNO)
    techno_notes = techno.generate(16)
    print(f"Techno Percussion: {len(techno_notes)} notes")
    
    # Test ambient pads
    ambient = AmbientPadLayers(Genre.AMBIENT)
    ambient_notes = ambient.generate(16)
    print(f"Ambient Pad Layers: {len(ambient_notes)} notes")
    
    print("\nExpanded patterns test complete!")
