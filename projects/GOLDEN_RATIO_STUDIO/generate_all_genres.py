#!/usr/bin/env python3
"""
GOLDEN RATIO STUDIO - MULTI-GENRE MUSIC PRODUCTION SYSTEM
Generates complete productions for Dub Reggae, Dub Techno, House, Hip-Hop, and more.
"""

import random
import math
import zlib
import os

class GoldenRatioGenerator:
    """Generate music using golden ratio (phi = 1.61803398875) principles."""
    
    PHI = 1.61803398875
    
    @staticmethod
    def golden_bpm(base_bpm):
        """Calculate perfect BPM using golden ratio relationships."""
        return round(base_bpm * (GoldenRatioGenerator.PHI ** random.randint(-1, 1)))
    
    @staticmethod
    def golden_section(total_length, section_ratio=PHI):
        """Divide music sections using golden ratio."""
        major_length = total_length / section_ratio
        minor_length = total_length - major_length
        return major_length, minor_length

class GenreMIDIGenerator:
    """Generate MIDI patterns for multiple electronic music genres."""
    
    @staticmethod
    def humanize(time, velocity, duration, variation=0.12):
        """Humanize MIDI with natural variation."""
        return {
            'time': max(0, time + random.uniform(-variation, variation)),
            'velocity': max(1, min(127, int(velocity * random.uniform(0.85, 1.15)))),
            'pitch': None,
            'duration': max(0.01, duration * random.uniform(0.8, 1.2))
        }

class DubReggaePatterns:
    """Authentic dub reggae MIDI patterns."""
    
    @staticmethod
    def one_drop_kick(bar_count, bpm=78):
        notes = []
        for bar in range(bar_count):
            time = bar * 4 + 0
            note = GenreMIDIGenerator.humanize(time, 110, 0.5, 0.12)
            note['pitch'] = 36
            notes.append(note)
            if bar % 4 == 2:
                ghost_time = bar * 4 + 2.8
                ghost = GenreMIDIGenerator.humanize(ghost_time, 55, 0.08, 0.15)
                ghost['pitch'] = 36
                notes.append(ghost)
        return notes
    
    @staticmethod
    def dub_bass(bar_count, key=None):
        notes = []
        patterns = [
            [(24, 120, 2.0), (31, 115, 1.5)],
            [(20, 120, 2.0), (24, 115, 1.5)],
            [(24, 118, 2.0), (28, 112, 1.5)],
            [(19, 120, 2.0), (24, 115, 1.5)],
        ]
        for bar in range(bar_count):
            pattern = patterns[bar % len(patterns)]
            for i, (pitch, velocity, duration) in enumerate(pattern):
                time = bar * 4 + (i * 2)
                note = GenreMIDIGenerator.humanize(time, velocity, duration, 0.15)
                note['pitch'] = pitch
                notes.append(note)
        return notes

class DubTechnoPatterns:
    """Dub techno patterns with hypnotic repetition and dub effects."""
    
    @staticmethod
    def four_on_floor_kick(bar_count, bpm=135):
        notes = []
        for bar in range(bar_count):
            for beat in range(4):
                time = bar * 4 + beat
                velocity = 115 if beat == 0 else (108 if beat == 2 else 105)
                note = GenreMIDIGenerator.humanize(time, velocity, 0.35, 0.08)
                note['pitch'] = 36
                notes.append(note)
        return notes
    
    @staticmethod
    def dub_techno_bass(bar_count):
        notes = []
        pattern = [(16, 115, 4.0), (16, 110, 4.0), (23, 118, 4.0), (15, 110, 4.0)]
        for bar in range(bar_count):
            note_data = pattern[bar % len(pattern)]
            time = bar * 4
            note = GenreMIDIGenerator.humanize(time, note_data[1], note_data[2], 0.1)
            note['pitch'] = note_data[0]
            notes.append(note)
        return notes

class HousePatterns:
    """House music patterns (deep house, tech house, progressive)."""
    
    @staticmethod
    def house_kick(bar_count, bpm=126):
        notes = []
        for bar in range(bar_count):
            for beat in range(4):
                time = bar * 4 + beat
                if beat in [1, 3]:
                    time += 0.02
                velocity = 118 if beat == 0 else 108
                note = GenreMIDIGenerator.humanize(time, velocity, 0.4, 0.1)
                note['pitch'] = 36
                notes.append(note)
        return notes
    
    @staticmethod
    def house_bass(bar_count, key="G# minor"):
        basslines = {
            "G# minor": [(20, 115, 2.0), (23, 112, 2.0), (27, 110, 1.5), (23, 115, 1.5)],
            "A minor": [(21, 115, 2.0), (24, 112, 2.0), (28, 110, 1.5), (24, 115, 1.5)],
            "E minor": [(16, 115, 2.0), (19, 114, 2.0), (23, 112, 1.5), (22, 115, 1.5)],
        }
        pattern = basslines.get(key, basslines["G# minor"])
        notes = []
        for bar in range(bar_count):
            for i, (pitch, velocity, duration) in enumerate(pattern):
                time = bar * 4 + (i * 2)
                note = GenreMIDIGenerator.humanize(time, velocity, duration, 0.12)
                note['pitch'] = pitch
                notes.append(note)
        return notes

class HipHopPatterns:
    """Hip-hop and trap MIDI patterns."""
    
    @staticmethod
    def hip_hop_kick(bar_count, bpm=95):
        notes = []
        patterns = [
            [0, 0, 2, 1.5, 2],
            [0, 1, 2, 1.5, 2.5],
            [0, 0.5, 2, 2.5, 3],
            [0, 0.5, 2, 2.5, 3.5],
        ]
        for bar in range(bar_count):
            pattern = patterns[bar % len(patterns)]
            for time_offset in pattern:
                time = bar * 4 + time_offset
                note = GenreMIDIGenerator.humanize(time, 110, 0.4, 0.15)
                note['pitch'] = 36
                notes.append(note)
        return notes
    
    @staticmethod
    def hip_hop_bass(bar_count, key="C minor"):
        basslines = {
            "C minor": [(36, 85, 0.2), (43, 90, 0.25), (36, 88, 0.2), (46, 85, 0.25)],
            "G minor": [(31, 85, 0.2), (38, 90, 0.25), (31, 88, 0.2), (41, 85, 0.25)],
            "D minor": [(26, 85, 0.2), (33, 90, 0.25), (26, 88, 0.2), (36, 85, 0.25)],
        }
        pattern = basslines.get(key, basslines["C minor"])
        notes = []
        for bar in range(bar_count):
            for i, (pitch, velocity, duration) in enumerate(pattern):
                time = bar * 4 + (i * 1)
                note = GenreMIDIGenerator.humanize(time, velocity, duration, 0.18)
                note['pitch'] = pitch
                notes.append(note)
        return notes

class DrumAndBassPatterns:
    """DnB and breakbeat patterns."""
    
    @staticmethod
    def dnb_amens_break(bar_count, bpm=174):
        notes = []
        for bar in range(bar_count):
            kicks = [0, 1.5, 2, 3]
            for time_offset in kicks:
                time = bar * 4 + time_offset
                note = GenreMIDIGenerator.humanize(time, 120, 0.15, 0.06)
                note['pitch'] = 36
                notes.append(note)
            for sixteen in [2, 2.25, 2.5, 2.75]:
                time = bar * 4 + sixteen
                velocity = 100 if sixteen == 2 else (85 if sixteen in [2.5, 2.75] else 95)
                note = GenreMIDIGenerator.humanize(time, velocity, 0.1, 0.08)
                note['pitch'] = 40
                notes.append(note)
        return notes

class AmbientPatterns:
    """Ambient and cinematic patterns."""
    
    @staticmethod
    def ambient_pad(bar_count, key="C minor", bpm=72):
        notes = []
        chords = {
            "C minor": [36, 43, 48, 51, 55, 59, 63],
            "E minor": [28, 35, 40, 43, 47, 51, 55],
            "F minor": [29, 36, 41, 44, 48, 52, 56],
        }
        chord = chords.get(key, chords["C minor"])
        for bar in range(bar_count * 2):
            time = bar * 8
            for pitch in chord:
                velocity = 40 + random.randint(-5, 10)
                note = GenreMIDIGenerator.humanize(time, velocity, 8.0, 0.2)
                note['pitch'] = pitch
                notes.append(note)
        return notes

def generate_genre_project(genre, bar_count=128):
    """Generate complete project for specified genre."""
    
    genres = {
        'dub_reggae': {
            'bpm': 78,
            'key': 'C Minor',
            'kick': DubReggaePatterns.one_drop_kick,
            'bass': DubReggaePatterns.dub_bass,
            'sections': ['INTRO', 'ONE_DROP', 'DUB_SECTION_1', 'ROCKERS', 'DUB_DROP', 'BUILD_UP', 'BASS_INVERSION', 'FINAL_DUB', 'RE_ENTRY', 'OUTRO']
        },
        'dub_techno': {
            'bpm': 135,
            'key': 'E Minor',
            'kick': DubTechnoPatterns.four_on_floor_kick,
            'bass': DubTechnoPatterns.dub_techno_bass,
            'sections': ['BUILD', 'DROP', 'PERC_LEDS', 'FILTER_SWEEP', 'BASS_CHANGE', 'PEAK', 'DECAY', 'BREAKDOWN']
        },
        'deep_house': {
            'bpm': 124,
            'key': 'G# Minor',
            'kick': HousePatterns.house_kick,
            'bass': HousePatterns.house_bass,
            'sections': ['BUILD', 'DROP', 'PERC_LEDS', 'MOTIF', 'BASIS', 'BUILD_UP', 'PEAK', 'DECAY', 'COMPRESS']
        },
        'tech_house': {
            'bpm': 128,
            'key': 'A Minor',
            'kick': HousePatterns.house_kick,
            'bass': HousePatterns.house_bass,
            'sections': ['LOOP', 'FILTER', 'DROP', 'PERC', 'BUILD', 'PEAK', 'DECAY']
        },
        'hip_hop': {
            'bpm': 92,
            'key': 'C Minor',
            'kick': HipHopPatterns.hip_hop_kick,
            'bass': HipHopPatterns.hip_hop_bass,
            'sections': ['INTRO', 'VERSE', 'CHORUS', 'BREAK', 'VERSE2', 'CHORUS', 'BRIDGE', 'OUTRO']
        },
        'trap': {
            'bpm': 140,
            'key': 'C Minor',
            'kick': HipHopPatterns.hip_hop_kick,
            'bass': HipHopPatterns.hip_hop_bass,
            'sections': ['INTRO', 'DROP', 'ROLLER', 'BUILD', 'DROP2', 'HOOK', 'OUTRO']
        },
        'dnb': {
            'bpm': 174,
            'key': 'G Minor',
            'kick': DrumAndBassPatterns.dnb_amens_break,
            'bass': DrumAndBassPatterns.dnb_amens_break,
            'sections': ['INTRO', 'BREAK', 'DROP', 'BUILD', 'BREAK2', 'DROP2', 'BUILD2', 'PEAK', 'DECAY']
        },
        'ambient': {
            'bpm': 70,
            'key': 'C Minor',
            'kick': lambda x, y: [],
            'bass': AmbientPatterns.ambient_pad,
            'sections': ['EMERGE', 'DEVELOP', 'PEAK', 'DECAY', 'TRANSFORM', 'RESOLVE']
        }
    }
    
    config = genres.get(genre)
    if not config:
        return None
    
    patterns = {
        'kick': config['kick'](bar_count, config['bpm']),
        'bass': config['bass'](bar_count),
    }
    
    return {
        'genre': genre,
        'config': config,
        'patterns': patterns,
        'bar_count': bar_count
    }

def save_genre_project(project_data, filename):
    """Save genre project as Ableton file."""
    
    config = project_data['config']
    patterns = project_data['patterns']
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Ableton MajorVersion="5" MinorVersion="12.0_12402" Creator="Ableton Live 12.4.3" SchemaChangeCount="5">
  <LiveSet>
    <Tracks>'''
    
    for track_id, (name, notes) in enumerate([('Kick Bass', patterns['kick']), ('Bass', patterns['bass'])]):
        xml += f'''
      <MidiTrack Id="{track_id}">
        <Name><EffectiveName Value="{name}"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset>
                <PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/>
              </Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer>
            <Volume Value="0.75"/>
            <Pan Value="0.0"/>
          </Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="{track_id}_clip_0" Time="0">
                <Name><EffectiveName Value="{config["key"]} - {name}"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="{project_data["bar_count"] * 4}"/></Loop>
                <NoteList>'''
        
        for note in notes[:500]:
            xml += f'                  <Note Time="{note["time"]:.3f}" Pitch="{note["pitch"]}" Velocity="{int(note["velocity"])}" Duration="{note["duration"]:.3f}"/>\\n'
        
        if len(notes) > 500:
            xml += f'                  <!-- {len(notes) - 500} additional notes omitted -->\\n'
        
        xml += '''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>'''
    
    xml += f'''
    </Tracks>
    <MasterTrack>
      <DeviceChain>
        <Mixer>
          <Tempo>
            <Manual><Value Value="{config["bpm"]}"/></Manual>
          </Tempo>
          <Volume Value="0.88"/>
        </Mixer>
      </DeviceChain>
    </MasterTrack>
    <Scenes>
'''
    
    for i, section in enumerate(config['sections']):
        bar_start = int((i / len(config['sections'])) * project_data['bar_count'])
        xml += f'      <Scene Id="{i}"><Name><EffectiveName Value="{section}"/></Name><Time Value="{bar_start * 4}"/></Scene>\\n'
    
    xml += '''    </Scenes>
  </LiveSet>
  <Transport>
    <LoopOn Value="true"/>
    <LoopStartTime Value="0.0"/>
    <LoopLength Value="''' + str(project_data['bar_count'] * 4) + '''"/></LoopLength>
  </Transport>
</Ableton>'''
    
    xml_bytes = xml.encode('utf-8')
    compressed = zlib.compress(xml_bytes, level=9)
    
    with open(filename, 'wb') as f:
        f.write(b' Golden Ratio Studio ')
        f.write(compressed)
    
    return len(compressed)

if __name__ == '__main__':
    print('=' * 80)
    print('GOLDEN RATIO STUDIO - MULTI-GENRE PRODUCTION')
    print('Generating music for 8 genres')
    print('=' * 80)
    print()
    
    genres = ['dub_reggae', 'dub_techno', 'deep_house', 'tech_house', 'hip_hop', 'trap', 'dnb', 'ambient']
    
    for genre in genres:
        project = generate_genre_project(genre, bar_count=128)
        if project:
            filename = f'{genre}_golden_ratio.als'
            size = save_genre_project(project, filename)
            print(f'Generated: {filename} ({size} bytes)')
    
    print()
    print('=' * 80)
    print('[GOLDEN RATIO STUDIO - ALL GENRES GENERATED]')
    print('=' * 80)
    print(f'Projects created: {len(genres)}')
    print('All projects saved to current directory')
    print()
    print('FILES GENERATED:')
    for genre in genres:
        print(f'  {genre}_golden_ratio.als')
    print()
    print('BLESS UP - Golden Ratio Studio complete, mon!')
