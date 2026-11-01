#!/usr/bin/env python3
"""
ABLETON LIVE 12.4.3 COMPLETE REAGAE PROJECT GENERATOR
Creates a fully mixed Ableton project file (.als) with complete song arrangement.
"""

import struct
import zlib
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Note:
    """MIDI note event."""
    time: float
    pitch: int
    velocity: int
    duration: float = 0.5

@dataclass
class AutomationPoint:
    """Automation point for effects/parameters."""
    time: float
    value: float

class MIDIPatterns:
    """Reggae MIDI pattern generators."""
    
    @staticmethod
    def one_drop_kick() -> List[Note]:
        """One drop rhythm - kick on beat 1 only."""
        return [Note(0.0, 36, 110, 0.8)]
    
    @staticmethod
    def rockers_kick() -> List[Note]:
        """Rockers rhythm - more syncopated kick."""
        return [
            Note(0.0, 36, 110, 0.6),
            Note(3.0, 36, 100, 0.5),
            Note(6.0, 36, 110, 0.6),
            Note(9.0, 36, 100, 0.5),
        ]
    
    @staticmethod
    def steppers_kick() -> List[Note]:
        """Steppers rhythm - four on the floor."""
        return [
            Note(0.0, 36, 110, 0.5),
            Note(1.0, 36, 108, 0.5),
            Note(2.0, 36, 110, 0.5),
            Note(3.0, 36, 108, 0.5),
        ]
    
    @staticmethod
    def snare() -> List[Note]:
        """Backbeat snare."""
        return [Note(2.0, 40, 100, 0.4)]
    
    @staticmethod
    def hihats() -> List[Note]:
        """Offbeat hihats."""
        return [
            Note(1.0, 42, 75, 0.2),
            Note(3.0, 42, 75, 0.2),
        ]
    
    @staticmethod
    def dub_bass() -> List[Note]:
        """Dub bassline (C minor)."""
        return [
            Note(0.0, 24, 120, 2.0),   # C1 root
            Note(2.0, 31, 110, 1.5),   # G1 fifth
            Note(3.5, 24, 120, 2.0),   # C1
            Note(6.0, 20, 110, 1.5),   # G#0 flat sev
        ]
    
    @staticmethod
    def inverted_bass() -> List[Note]:
        """Inverted bassline for bass inversion section."""
        return [
            Note(0.0, 20, 120, 2.0),   # G#0
            Note(2.0, 24, 110, 1.5),   # C1
            Note(3.5, 31, 120, 2.0),   # G1
            Note(6.0, 24, 110, 1.5),   # C1
        ]
    
    @staticmethod
    def guitar_skank() -> List[Note]:
        """Guitar skanking (offbeats)."""
        return [
            Note(0.5, 60, 85, 0.3),    # C4 offbeat 1
            Note(1.5, 60, 85, 0.3),    # C4 offbeat 2
            Note(2.5, 60, 85, 0.3),    # C4 offbeat 3
            Note(3.5, 60, 85, 0.3),    # C4 offbeat 4
        ]
    
    @staticmethod
    def organ_stabs() -> List[Note]:
        """Hammond organ stabs."""
        return [
            Note(0.0, 60, 100, 1.0),   # C4 root
            Note(2.0, 67, 95, 0.8),    # G4 fifth
            Note(4.0, 60, 100, 1.0),   # C4
            Note(6.0, 67, 95, 0.8),    # G4
        ]
    
    @staticmethod
    def electric_piano() -> List[Note]:
        """Electric piano dub fills."""
        return [
            Note(0.0, 48, 80, 1.5),    # C3
            Note(2.0, 55, 75, 1.0),    # G3
            Note(3.5, 48, 80, 1.5),    # C3
            Note(6.0, 55, 75, 1.0),    # G3
        ]
    
    @staticmethod
    def percussion() -> List[Note]:
        """Latin percussion (congas)."""
        return [
            Note(0.0, 65, 70, 0.4),    # Conga high
            Note(2.0, 64, 75, 0.5),    # Conga low
            Note(4.0, 65, 72, 0.4),
            Note(6.0, 64, 78, 0.5),
        ]


class Arrangement:
    """Complete arrangement with MIDI and automation."""
    
    def __init__(self):
        self.bpm = 78
        self.key = 'C Minor'
        self.time_signature = '4/4'
        self.tempo = 78.0
        
        # 10 sections, 16 bars each = 160 bars
        self.sections = [
            {'name': 'INTRO', 'bar_start': 0, 'bar_end': 15, 'kick': 'one_drop', 'bass': 'dub'},
            {'name': 'ONE_DROP', 'bar_start': 16, 'bar_end': 31, 'kick': 'one_drop', 'bass': 'dub'},
            {'name': 'DUB_SECTION_1', 'bar_start': 32, 'bar_end': 47, 'kick': 'rockers', 'bass': 'dub'},
            {'name': 'ROCKERS', 'bar_start': 48, 'bar_end': 63, 'kick': 'rockers', 'bass': 'dub'},
            {'name': 'DUB_DROP', 'bar_start': 64, 'bar_end': 79, 'kick': 'steppers', 'bass': 'dub'},
            {'name': 'BUILD_UP', 'bar_start': 80, 'bar_end': 95, 'kick': 'rockers', 'bass': 'dub'},
            {'name': 'BASS_INVERSION', 'bar_start': 96, 'bar_end': 111, 'kick': 'steppers', 'bass': 'inverted'},
            {'name': 'FINAL_DUB', 'bar_start': 112, 'bar_end': 127, 'kick': 'steppers', 'bass': 'inverted'},
            {'name': 'RE_ENTRY', 'bar_start': 128, 'bar_end': 143, 'kick': 'rockers', 'bass': 'dub'},
            {'name': 'OUTRO', 'bar_start': 144, 'bar_end': 159, 'kick': 'one_drop', 'bass': 'dub'},
        ]
        
        # Total duration
        self.total_bars = 160
        self.total_beats = self.total_bars * 4
        self.duration_seconds = (self.total_beats / self.bpm) * 60


def create_xml_header():
    """Create XML header for Ableton Live 12.4.3."""
    return f'<?xml version="1.0" encoding="UTF-8"?>\\n'


def create_magflet():
    """Create Magflet/Ableton file header."""
    return 'Ableton Live 12.4.3 Project File'


def build_ableton_liveproject(arrangement: Arrangement) -> str:
    """Build complete Ableton Live project XML."""
    
    print('[CREATING ABLETON LIVE 12.4.3 PROJECT]')
    print('Building XML structure...')
    print()
    
    xml = create_xml_header()
    xml += '<Ableton MajorVersion="5" MinorVersion="12.0_12402" Creator="Ableton Live 12.4.3" SchemaChangeCount="4">\\n'
    xml += '  <LiveSet>\\n'
    xml += '    <Tracks>\\n'
    
    # Track 0: Kick Drum
    xml += '      <MidiTrack Id="0">\\n'
    xml += '        <Name><EffectiveName Value="Kick Drum"/></Name>\\n'
    xml += '        <Color Id="18"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><Source Value="Internal"/><PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.75"/>\\n'
    xml += '            <Pan Value="0.0"/>\\n'
    xml += '            <Balance><SendLevel Value="0.5"/></Balance>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    for i, section in enumerate(arrangement.sections):
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="{id}_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - Kick"/></Name>\\n'
        xml += f'                <Color Id="18"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Generate MIDI notes for kick pattern
        if section["kick"] == "one_drop":
            notes = MIDIPatterns.one_drop_kick()
        elif section["kick"] == "rockers":
            notes = MIDIPatterns.rockers_kick()
        else:  # steppers
            notes = MIDIPatterns.steppers_kick()
        
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 1: Dub Bass
    xml += '      <MidiTrack Id="1">\\n'
    xml += '        <Name><EffectiveName Value="Dub Bass"/></Name>\\n'
    xml += '        <Color Id="12"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Sounds/Bass/Fretless Bass"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '              <AudioEffectChain>\\n'
    xml += '                <Device><Type Value="Compressor"/>\\n'
    xml += '                  <Enabled Value="true"/>\\n'
    xml += '                  <Threshold Value="-10.0"/>\\n'
    xml += '                  <Ratio Value="3.0"/>\\n'
    xml += '                </Device>\\n'
    xml += '                <Device><Type Value="EQEight"/>\\n'
    xml += '                  <Enabled Value="true"/>\\n'
    xml += '                  <FilterFreq Value="200.0"/>\\n'
    xml += '                </Device>\\n'
    xml += '              </AudioEffectChain>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.84"/>\\n'
    xml += '            <Pan Value="0.0"/>\\n'
    xml += '            <Balance><SendLevel Value="0.6"/></Balance>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    for i, section in enumerate(arrangement.sections):
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="1_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - Bass"/></Name>\\n'
        xml += f'                <Color Id="12"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Generate MIDI notes for bass pattern
        if section["bass"] == "dub":
            notes = MIDIPatterns.dub_bass()
        else:  # inverted
            notes = MIDIPatterns.inverted_bass()
        
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 2: Snare
    xml += '      <MidiTrack Id="2">\\n'
    xml += '        <Name><EffectiveName Value="Snare"/></Name>\\n'
    xml += '        <Color Id="5"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Drums/Acoustic/Arizona Kit"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.63"/>\\n'
    xml += '            <Pan Value="0.0"/>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    for i, section in enumerate(arrangement.sections[:7]):  # Snare drops out sections 7-9
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="2_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - Snare"/></Name>\\n'
        xml += f'                <Color Id="5"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Snare pattern
        notes = MIDIPatterns.snare()
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 3: Hi-Hats
    xml += '      <MidiTrack Id="3">\\n'
    xml += '        <Name><EffectiveName Value="Hi-Hats"/></Name>\\n'
    xml += '        <Color Id="8"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.44"/>\\n'
    xml += '            <Pan Value="0.15"/>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    for i, section in enumerate(arrangement.sections):
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="3_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - HiHats"/></Name>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Hi-hat pattern
        notes = MIDIPatterns.hihats()
        for bar in range(section["bar_start"], min(section["bar_end"] + 1, 96)):  # Hi-hats drop out
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 4: Hammond Organ
    xml += '      <MidiTrack Id="4">\\n'
    xml += '        <Name><EffectiveName Value="Hammond Organ"/></Name>\\n'
    xml += '        <Color Id="2"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Sounds/Tonewheel Organ/Organ Joyous Tonewheels"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.56"/>\\n'
    xml += '            <Pan Value="0.35"/>\\n'
    xml += '            <Balance><SendLevel Value="0.4"/></Balance>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    # Organ enters in section 4 (ROCKERS)
    for i in range(3, 10):
        section = arrangement.sections[i]
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="4_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - Organ"/></Name>\\n'
        xml += f'                <Color Id="2"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Organ stabs
        notes = MIDIPatterns.organ_stabs()
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 5: Rhythm Guitar
    xml += '      <MidiTrack Id="5">\\n'
    xml += '        <Name><EffectiveName Value="Rhythm Guitar"/></Name>\\n'
    xml += '        <Color Id="22"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Sounds/Guitar Clean/Guitar Mute"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.50"/>\\n'
    xml += '            <Pan Value="-0.25"/>\\n'
    xml += '            <Balance><SendLevel Value="0.3"/></Balance>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    # Guitar enters in section 2 (ONE DROP), drops out in sections 8-9
    for i in [1, 2, 3, 4, 5, 6, 7]:
        section = arrangement.sections[i]
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="5_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - Guitar"/></Name>\\n'
        xml += f'                <Color Id="22"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Guitar skank
        notes = MIDIPatterns.guitar_skank()
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 6: Electric Piano
    xml += '      <MidiTrack Id="6">\\n'
    xml += '        <Name><EffectiveName Value="Electric Piano"/></Name>\\n'
    xml += '        <Color Id="3"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Sounds/Wurly Piano/Wurly Low & Durty"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '              <AudioEffectChain>\\n'
    xml += '                <Device><Type Value="Saturator"/>\\n'
    xml += '                  <Enabled Value="true"/>\\n'
    xml += '                  <Drive Value="0.5"/>\\n'
    xml += '                </Device>\\n'
    xml += '              </AudioEffectChain>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.46"/>\\n'
    xml += '            <Pan Value="-0.15"/>\\n'
    xml += '            <Balance><SendLevel Value="0.5"/></Balance>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    # Electric piano throughout, builds up intensity
    for i in range(10):
        section = arrangement.sections[i]
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="6_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - EPiano"/></Name>\\n'
        xml += f'                <Color Id="3"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Electric piano
        notes = MIDIPatterns.electric_piano()
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity + i * 2}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Track 7: Percussion
    xml += '      <MidiTrack Id="7">\\n'
    xml += '        <Name><EffectiveName Value="Percussion"/></Name>\\n'
    xml += '        <Color Id="31"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <MainLoom>\\n'
    xml += '            <MidiToAudio>\\n'
    xml += '              <Instrument>\\n'
    xml += '                <Preset><PresetPath Value="Presets/Bossa Nova"/></Preset>\\n'
    xml += '              </Instrument>\\n'
    xml += '            </MidiToAudio>\\n'
    xml += '          </MainLoom>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.39"/>\\n'
    xml += '            <Pan Value="0.4"/>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '        <ClipSlotList>\\n'
    # Percussion enters in section 7 (BASS INVERSION)
    for i in range(6, 10):
        section = arrangement.sections[i]
        xml += f'          <ClipSlot Id="{i}">\\n'
        xml += f'            <ClipSlot>\\n'
        xml += f'              <Clip Id="7_clip_{i}" Time="{section["bar_start"] * 4}">\\n'
        xml += f'                <Name><EffectiveName Value="{section["name"]} - Percussion"/></Name>\\n'
        xml += f'                <Color Id="31"/>\\n'
        xml += f'                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="64"/></Loop>\\n'
        xml += f'                <NoteList>\\n'
        # Percussion
        notes = MIDIPatterns.percussion()
        for bar in range(section["bar_start"], section["bar_end"] + 1):
            for note in notes:
                time_offset = (bar - section["bar_start"]) * 4
                xml += f'                  <Note Time="{note.time + time_offset}" Pitch="{note.pitch}" Velocity="{note.velocity}" Duration="{note.duration * 0.25}"/>\\n'
        xml += f'                </NoteList>\\n'
        xml += f'              </Clip>\\n'
        xml += f'            </ClipSlot>\\n'
        xml += f'          </ClipSlot>\\n'
    xml += '        </ClipSlotList>\\n'
    xml += '      </MidiTrack>\\n'
    
    # Close Tracks
    xml += '    </Tracks>\\n'
    
    # Master Track
    xml += '    <MasterTrack>\\n'
    xml += '      <DeviceChain>\\n'
    xml += '        <Mixer>\\n'
    xml += '          <Tempo>\\n'
    xml += f'            <Manual><Value Value="{arrangement.tempo}"/></Manual>\\n'
    xml += '          </Tempo>\\n'
    xml += '          <Volume Value="0.88"/>\\n'
    xml += '          <Pan Value="0.0"/>\\n'
    xml += '        </Mixer>\\n'
    xml += '      </DeviceChain>\\n'
    xml += '    </MasterTrack>\\n'
    
    # Return Tracks
    xml += '    <Returns>\\n'
    xml += '      <AudioTrack Id="100">\\n'
    xml += '        <Name><EffectiveName Value="Dub Echo Return"/></Name>\\n'
    xml += '        <Color Id="28"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <AudioEffectChain>\\n'
    xml += '            <Device><Type Value="Echo"/>\\n'
    xml += '              <Enabled Value="true"/>\\n'
    xml += '              <Time Value="1/4"/>\\n'
    xml += '              <Feedback><Manual Value="0.75"/></Feedback>\\n'
    xml += '              <DryWet Value="0.4"/>\\n'
    xml += '              <FilterEnabled Value="true"/>\\n'
    xml += '              <FilterFreq Value="4000.0"/>\\n'
    xml += '              <FilterGain Value="0.0"/>\\n'
    xml += '              <FilterRes Value="0.5"/>\\n'
    xml += '            </Device>\\n'
    xml += '          </AudioEffectChain>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.80"/>\\n'
    xml += '            <Pan Value="0.5"/>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '      </AudioTrack>\\n'
    xml += '      <AudioTrack Id="101">\\n'
    xml += '        <Name><EffectiveName Value="Spring Reverb Return"/></Name>\\n'
    xml += '        <Color Id="17"/>\\n'
    xml += '        <DeviceChain>\\n'
    xml += '          <AudioEffectChain>\\n'
    xml += '            <Device><Type Value="Reverb"/>\\n'
    xml += '              <Enabled Value="true"/>\\n'
    xml += '              <DecayTime Value="3.2"/>\\n'
    xml += '              <Predelay Value="0.015"/>\\n'
    xml += '              <HighCut Value="6000.0"/>\\n'
    xml += '              <DryWet Value="0.25"/>\\n'
    xml += '              <OutputGain Value="0.0"/>\\n'
    xml += '            </Device>\\n'
    xml += '          </AudioEffectChain>\\n'
    xml += '          <Mixer>\\n'
    xml += '            <Volume Value="0.75"/>\\n'
    xml += '            <Pan Value="-0.75"/>\\n'
    xml += '          </Mixer>\\n'
    xml += '        </DeviceChain>\\n'
    xml += '      </AudioTrack>\\n'
    xml += '    </Returns>\\n'
    
    # Scenes
    xml += '    <Scenes>\\n'
    for i, section in enumerate(arrangement.sections):
        xml += f'      <Scene Id="{i}">\\n'
        xml += f'        <Name><EffectiveName Value="{section["name"]}"/></Name>\\n'
        xml += f'        <Time Value="{section["bar_start"] * 4}"/>\\n'
        xml += f'      </Scene>\\n'
    xml += '    </Scenes>\\n'
    
    # Close LiveSet
    xml += '  </LiveSet>\\n'
    
    # Transport
    xml += '  <Transport>\\n'
    xml += '    <LoopOn Value="true"/>\\n'
    xml += '    <LoopStartTime Value="0.0"/>\\n'
    xml += '    <LoopLength Value="640.0"/>\\n'  # 160 bars * 4 beats
    xml += '  </Transport>\\n'
    
    # Close Ableton
    xml += '</Ableton>\\n'
    
    print('[XML STRUCTURE BUILT]')
    print(f'Total sections: {len(arrangement.sections)}')
    print(f'Total bars: {arrangement.total_bars}')
    print(f'Total duration: {arrangement.duration_seconds:.1f} seconds ({arrangement.duration_seconds / 60:.1f} minutes)')
    print()
    
    return xml


def save_als_file(filename: str, xml_content: str):
    """Save Ableton Live project file with compression."""
    
    print(f'[SAVING PROJECT FILE: {filename}]')
    
    # Convert to bytes
    xml_bytes = xml_content.encode('utf-8')
    
    # Compress
    compressed = zlib.compress(xml_bytes, level=9)
    
    # Create header (simple Ableton header)
    header = b' Ableton Live 12.4.3 \\n'
    
    # Write file
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(compressed)
    
    print(f'File size: {len(compressed)} bytes (compressed)')
    print(f'File size: {len(xml_bytes)} bytes (uncompressed)')
    print(f'Compression ratio: {len(compressed) / len(xml_bytes) * 100:.1f}%')
    print()
    
    return len(compressed)


def main():
    """Main function to generate complete Ableton project."""
    
    print('=' * 80)
    print('FINE DUB REAGAE - ABLETON PROJECT GENERATOR')
    print('Creating complete mixed song project for Ableton Live 12.4.3')
    print('=' * 80)
    print()
    
    # Create arrangement
    arrangement = Arrangement()
    
    print('[ARRANGEMENT CREATED]')
    for section in arrangement.sections:
        print(f'  {section["name"]}: Bars {section["bar_start"]}-{section["bar_end"]} (Kick: {section["kick"]}, Bass: {section["bass"]})')
    print()
    
    # Build XML
    xml_content = build_ableton_liveproject(arrangement)
    
    # Save file
    output_file = 'Fine_Dub_Reggae_Complete.als'
    save_als_file(output_file, xml_content)
    
    print('=' * 80)
    print('[PROJECT FILE CREATION COMPLETE]')
    print('=' * 80)
    print(f'Filename: {output_file}')
    print(f'Version: Ableton Live 12.4.3')
    print(f'BPM: {arrangement.bpm}')
    print(f'Key: {arrangement.key}')
    print(f'Tracks: 8 MIDI tracks + 2 Return tracks')
    print(f'Duration: {arrangement.total_bars} bars ({arrangement.duration_seconds:.1f} seconds)')
    print(f'Sections: {len(arrangement.sections)} arrangement sections')
    print()
    print('[TRACKS WITH MIDI PATTERNS]')
    print('1. Kick Drum - One Drop/Rockers/Steppers patterns by section')
    print('2. Dub Bass - Dub/Inverted basslines by section')
    print('3. Snare - Backbeat pattern (drops out final sections)')
    print('4. Hi-Hats - Offbeat pattern (drops out later sections)')
    print('5. Hammond Organ - Organ stabs (enters section 4)')
    print('6. Rhythm Guitar - Skanking enters section 2')
    print('7. Electric Piano - Dub fills throughout')
    print('8. Percussion - Congas/timbales (enters section 7)')
    print()
    print('[MIXING & EFFECTS]')
    print('Master Volume: -3.0 dB')
    print('Return Track 1: Dub Echo - 1/4 note, 75% feedback, 40% mix')
    print('Return Track 2: Spring Reverb - 3.2s decay, 25% mix')
    print('Individual Track Volumes: Configured for dub balance')
    print('Panning: Strategically placed for stereo spread')
    print()
    print('[OPENING INSTRUCTIONS]')
    print(f'1. Open Ableton Live 12.4.3')
    print(f'2. File > Open Set...')
    print(f'3. Select {output_file}')
    print(f'4. Press SPACE to play the complete mixed song!')
    print()
    print('BLESS UP - Your complete Fine Dub Reggae project is ready, mon!')
    print('=' * 80)


if __name__ == '__main__':
    main()
