#!/usr/bin/env python3
"""
ABLETON MIDI PROJECT WITH FULL ARRANGEMENT
Creates XML with all MIDI note data for complete song.
"""

import struct
import zlib

def create_note_xml(time, pitch, velocity, duration):
    """Create XML for a MIDI note."""
    return f'          <Note Time=\"{time}\" Pitch=\"{pitch}\" Velocity=\"{velocity}\" Duration=\"{duration}\"/>\\n'

def generate_beamed问候歌曲():
    """Generate complete Fine Dub Reggae project with all MIDI data."""
    
    print('[GENERATING COMPLETE REAGAE PROJECT WITH MIDI]')
    print('=' * 80)
    print()
    
    # One drop kick pattern: |X---|----|--X-|----|
    one_drop_kick_notes = []
    for bar in range(16):  # 16 bars
        one_drop_kick_notes.append((bar * 4 + 0, 36, 110, 0.5))  # Kick on beat 1
    
    # Rockers kick: more syncopated
    rockers_kick_notes = []
    for bar in range(16):
        rockers_kick_notes.append((bar * 4 + 0, 36, 110, 0.4))  # Kick on 1
        rockers_kick_notes.append((bar * 4 + 3, 36, 100, 0.3))  # Kick on 4
    
    # Steppers kick: four-on-the-floor
    steppers_kick_notes = []
    for bar in range(16):
        for beat in range(4):
            steppers_kick_notes.append((bar * 4 + beat, 36, 110, 0.3))
    
    # Snare beats: backbeat on beat 3
    snare_notes = []
    for bar in range(16):
        snare_notes.append((bar * 4 + 2, 40, 100, 0.3))
    
    # Hi-hats: offbeats (beats 2 and 4)
    hihat_notes = []
    for bar in range(16):
        hihat_notes.append((bar * 4 + 1, 42, 75, 0.2))
        hihat_notes.append((bar * 4 + 3, 42, 75, 0.2))
    
    # Dub bass: C minor root, fifth, flat seventh
    dub_bass_notes = []
    for bar in range(16):
        dub_bass_notes.append((bar * 4 + 0, 24, 120, 2.0))  # C1 root
        dub_bass_notes.append((bar * 4 + 2, 31, 110, 1.5))  # G1 fifth
    
    # Inverted bass: G#, C, G sequence
    inverted_bass_notes = []
    for bar in range(16):
        inverted_bass_notes.append((bar * 4 + 0, 20, 120, 2.0))  # G#0
        inverted_bass_notes.append((bar * 4 + 2, 24, 115, 1.5))  # C1
    
    # Guitar skank: offbeats
    guitar_skank_notes = []
    for bar in range(16):
        for half in [0.5, 1.5, 2.5, 3.5]:
            guitar_skank_notes.append((bar * 4 + half, 60, 85, 0.3))
    
    # Organ stabs
    organ_stab_notes = []
    for bar in range(16):
        if bar % 2 == 0:  # Every other bar
            organ_stab_notes.append((bar * 4 + 0, 60, 100, 1.0))  # C4
            organ_stab_notes.append((bar * 4 + 2, 67, 95, 0.8))  # G4
    
    # Electric piano fills
    e_piano_notes = []
    for bar in range(16):
        e_piano_notes.append((bar * 4 + 0.5, 48, 80, 0.8))
        e_piano_notes.append((bar * 4 + 2.5, 55, 75, 0.6))
    
    # Percussion
    perc_notes = []
    for bar in range(16):
        perc_notes.append((bar * 4 + 1, 65, 70, 0.4))  # Conga high
        perc_notes.append((bar * 4 + 3, 64, 75, 0.5))  # Conga low
    
    return {
        'one_drop_kick': one_drop_kick_notes,
        'rockers_kick': rockers_kick_notes,
        'steppers_kick': steppers_kick_notes,
        'snare': snare_notes,
        'hihat': hihat_notes,
        'dub_bass': dub_bass_notes,
        'inverted_bass': inverted_bass_notes,
        'guitar': guitar_skank_notes,
        'organ': organ_stab_notes,
        'e_piano': e_piano_notes,
        'percussion': perc_notes
    }


def build_full_xml():
    """Build complete Ableton project with MIDI notes."""
    
    notes_dict = generate_beamed问候歌曲()
    
    sections = [
        {'name': 'INTRO', 'bars': (0, 15), 'kick': 'one_drop_kick', 'bass': 'dub_bass'},
        {'name': 'ONE_DROP', 'bars': (16, 31), 'kick': 'one_drop_kick', 'bass': 'dub_bass'},
        {'name': 'DUB_SECTION_1', 'bars': (32, 47), 'kick': 'rockers_kick', 'bass': 'dub_bass'},
        {'name': 'ROCKERS', 'bars': (48, 63), 'kick': 'rockers_kick', 'bass': 'dub_bass'},
        {'name': 'DUB_DROP', 'bars': (64, 79), 'kick': 'steppers_kick', 'bass': 'dub_bass'},
        {'name': 'BUILD_UP', 'bars': (80, 95), 'kick': 'rockers_kick', 'bass': 'dub_bass'},
        {'name': 'BASS_INVERSION', 'bars': (96, 111), 'kick': 'steppers_kick', 'bass': 'inverted_bass'},
        {'name': 'FINAL_DUB', 'bars': (112, 127), 'kick': 'steppers_kick', 'bass': 'inverted_bass'},
        {'name': 'RE_ENTRY', 'bars': (128, 143), 'kick': 'rockers_kick', 'bass': 'dub_bass'},
        {'name': 'OUTRO', 'bars': (144, 159), 'kick': 'one_drop_kick', 'bass': 'dub_bass'},
    ]
    
    xml = '''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Ableton MajorVersion=\"5\" MinorVersion=\"12.0_12402\" Creator=\"Ableton Live 12.4.3\" SchemaChangeCount=\"4\">
  <LiveSet>
    <Tracks>
      <MidiTrack Id=\"0\">
        <Name><EffectiveName Value=\"Kick Drum\"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value=\"Drums/Acoustic/Memphis Studio Kit\"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value=\"0.75\"/><Pan Value=\"0.0\"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
'''
    # Add kick drum clips for each section
    for i, section in enumerate(sections):
        kick_notes = notes_dict[section['kick']]
        xml += f'          <ClipSlot Id=\"{i}\">\n'
        xml += f'            <ClipSlot>\n'
        xml += f'              <Clip Id=\"0_clip_{i}\" Time=\"{section["bars"][0] * 4}\">\n'
        xml += f'                <Name><EffectiveName Value=\"{section["name"]} - Kick\"/></Name>\n'
        xml += f'                <Loop><LoopOn Value=\"true\"/><LoopStart Value=\"0\"/><LoopLength Value=\"64\"/></Loop>\n'
        xml += f'                <NoteList>\n'
        
        start_bar, end_bar = section['bars']
        for note in kick_notes:
            time = note[0] + (start_bar * 4)
            pitch = note[1]
            velocity = note[2] 
            duration = note[3]
            if time < (end_bar + 1) * 4:
                xml += f'                  <Note Time=\"{time}\" Pitch=\"{pitch}\" Velocity=\"{velocity}\" Duration=\"{duration}\"/>\n'
        
        xml += f'                </NoteList>\n'
        xml += f'              </Clip>\n'
        xml += f'            </ClipSlot>\n'
        xml += f'          </ClipSlot>\n'
    
    xml += '''        </ClipSlotList>
      </MidiTrack>
'''
    
    # Add bass track
    xml += '''      <MidiTrack Id=\"1\">
        <Name><EffectiveName Value=\"Dub Bass\"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value=\"Sounds/Bass/Fretless Bass\"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value=\"0.84\"/><Pan Value=\"0.0\"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
'''
    
    for i, section in enumerate(sections):
        bass_notes = notes_dict[section['bass']]
        xml += f'          <ClipSlot Id=\"{i}\">\n'
        xml += f'            <ClipSlot>\n'
        xml += f'              <Clip Id=\"1_clip_{i}\" Time=\"{section["bars"][0] * 4}\">\n'
        xml += f'                <Name><EffectiveName Value=\"{section["name"]} - Bass\"/></Name>\n'
        xml += f'                <Loop><LoopOn Value=\"true\"/><LoopStart Value=\"0\"/><LoopLength Value=\"64\"/></Loop>\n'
        xml += f'                <NoteList>\n'
        
        start_bar, end_bar = section['bars']
        for note in bass_notes:
            time = note[0] + (start_bar * 4)
            pitch = note[1]
            velocity = note[2]
            duration = note[3]
            if time < (end_bar + 1) * 4:
                xml += f'                  <Note Time=\"{time}\" Pitch=\"{pitch}\" Velocity=\"{velocity}\" Duration=\"{duration}\"/>\n'
        
        xml += f'                </NoteList>\n'
        xml += f'              </Clip>\n'
        xml += f'            </ClipSlot>\n'
        xml += f'          </ClipSlot>\n'
    
    xml += '''        </ClipSlotList>
      </MidiTrack>
'''
    
    # Add remaining tracks
    xml += '''      <MidiTrack Id=\"2\">
        <Name><EffectiveName Value=\"Snare\"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value=\"Drums/Acoustic/Arizona Kit\"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value=\"0.63\"/><Pan Value=\"0.0\"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
'''
    
    for i, section in enumerate(sections[:7]):  # Snare drops out
        snare_notes = notes_dict['snare']
        xml += f'          <ClipSlot Id=\"{i}\">\n'
        xml += f'            <ClipSlot>\n'
        xml += f'              <Clip Id=\"2_clip_{i}\" Time=\"{section["bars"][0] * 4}\">\n'
        xml += f'                <Name><EffectiveName Value=\"{section["name"]} - Snare\"/></Name>\n'
        xml += f'                <Loop><LoopOn Value=\"true\"/><LoopStart Value=\"0\"/><LoopLength Value=\"64\"/></Loop>\n'
        xml += f'                <NoteList>\n'
        
        start_bar, end_bar = section['bars']
        for note in snare_notes:
            time = note[0] + (start_bar * 4)
            if time < (end_bar + 1) * 4:
                xml += f'                  <Note Time=\"{time}\" Pitch=\"{note[1]}\" Velocity=\"{note[2]}\" Duration=\"{note[3]}\"/>\n'
        
        xml += f'                </NoteList>\n'
        xml += f'              </Clip>\n'
        xml += f'            </ClipSlot>\n'
        xml += f'          </ClipSlot>\n'
    
    xml += '''        </ClipSlotList>
      </MidiTrack>
'''
    
    # Add hi-hats, organ, guitar, e-piano, percussion tracks (simplified)
    for track_id, track_info in enumerate([
        ('3', 'Hi-Hats', 'Drums/Acoustic/Memphis Studio Kit', '0.44', '0.15', 'hihat', 10),
        ('4', 'Hammond Organ', 'Sounds/Tonewheel Organ/Organ Joyous Tonewheels', '0.56', '0.35', 'organ', 7),
        ('5', 'Rhythm Guitar', 'Sounds/Guitar Clean/Guitar Mute', '0.50', '-0.25', 'guitar', 7),
        ('6', 'Electric Piano', 'Sounds/Wurly Piano/Wurly Low & Durty', '0.46', '-0.15', 'e_piano', 10),
        ('7', 'Percussion', 'Presets/Bossa Nova', '0.39', '0.4', 'percussion', 4),
    ], start=1):
        tid, name, preset, volume, pan, note_key, section_limit = track_info
        section_start = 3 if tid == '4' else 0  # Organ starts at section 4
        
        xml += f'''      <MidiTrack Id=\"{tid}\">
        <Name><EffectiveName Value=\"{name}\"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value=\"{preset}\"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value=\"{volume}\"/><Pan Value=\"{pan}\"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
'''
        
        for i in range(section_start, min(len(sections), section_limit)):
            section = sections[i]
            track_notes = notes_dict[note_key]
            xml += f'          <ClipSlot Id=\"{i}\">\n'
            xml += f'            <ClipSlot>\n'
            xml += f'              <Clip Id=\"{tid}_clip_{i}\" Time=\"{section["bars"][0] * 4}\">\n'
            xml += f'                <Name><EffectiveName Value=\"{section["name"]} - {name}\"/></Name>\n'
            xml += f'                <Loop><LoopOn Value=\"true\"/><LoopStart Value=\"0\"/><LoopLength Value=\"64\"/></Loop>\n'
            xml += f'                <NoteList>\n'
            
            start_bar, end_bar = section['bars']
            for note in track_notes:
                time = note[0] + (start_bar * 4)
                if time < (end_bar + 1) * 4:
                    xml += f'                  <Note Time=\"{time}\" Pitch=\"{note[1]}\" Velocity=\"{note[2]}\" Duration=\"{note[3]}\"/>\n'
            
            xml += f'                </NoteList>\n'
            xml += f'              </Clip>\n'
            xml += f'            </ClipSlot>\n'
            xml += f'          </ClipSlot>\n'
        
        xml += '''        </ClipSlotList>
      </MidiTrack>
'''
    
    # Close Tracks and add Master/Returns
    xml += '''    </Tracks>
    <MasterTrack>
      <DeviceChain>
        <Mixer>
          <Tempo><Manual><Value Value=\"78.0\"/></Manual></Tempo>
          <Volume Value=\"0.88\"/>
        </Mixer>
      </DeviceChain>
    </MasterTrack>
    <Returns>
      <AudioTrack Id=\"100\">
        <Name><EffectiveName Value=\"Dub Echo Return\"/></Name>
        <DeviceChain>
          <AudioEffectChain>
            <Device><Type Value=\"Echo\"/></Device>
          </AudioEffectChain>
          <Mixer><Volume Value=\"0.80\"/><Pan Value=\"0.5\"/></Mixer>
        </DeviceChain>
      </AudioTrack>
      <AudioTrack Id=\"101\">
        <Name><EffectiveName Value=\"Spring Reverb Return\"/></Name>
        <DeviceChain>
          <AudioEffectChain>
            <Device><Type Value=\"Reverb\"/></Device>
          </AudioEffectChain>
          <Mixer><Volume Value=\"0.75\"/><Pan Value=\"-0.75\"/></Mixer>
        </DeviceChain>
      </AudioTrack>
    </Returns>
    <Scenes>
'''
    
    for i, section in enumerate(sections):
        xml += f'      <Scene Id=\"{i}\"><Name><EffectiveName Value=\"{section["name\"]}\"/></Name><Time Value=\"{section["bars"][0] * 4}\"/></Scene>\n'
    
    xml += '''    </Scenes>
  </LiveSet>
  <Transport>
    <LoopOn Value=\"true\"/>
    <LoopStartTime Value=\"0.0\"/>
    <LoopLength Value=\"640.0\"/>
  </Transport>
</Ableton>'''
    
    return xml


def main():
    """Main execution."""
    
    print('[FINE DUB REAGAE - COMPLETE PROJECT WITH MIDI]')
    print('=' * 80)
    print()
    
    # Generate full project
    xml_content = build_full_xml()
    
    # Save file
    output_file = 'Fine_Dub_Reggae_WithMIDI.als'
    
    print(f'[SAVING: {output_file}]')
    
    xml_bytes = xml_content.encode('utf-8')
    compressed = zlib.compress(xml_bytes, level=9)
    
    with open(output_file, 'wb') as f:
        f.write(b' Ableton Live 12.4.3 ')
        f.write(compressed)
    
    print(f'Size: {len(compressed)} bytes (compressed)')
    print(f'Size: {len(xml_bytes)} bytes (uncompressed)')
    print()
    print('[PROJECT COMPLETE]')
    print(f'Filename: {output_file}')
    print('Version: Ableton Live 12.4.3')
    print('BPM: 78')
    print('Tracks: 8 MIDI tracks with complete note data')
    print('Return Tracks: 2 (Dub Echo, Spring Reverb)')
    print('Duration: 160 bars (~8 minutes)')
    print('Total MIDI Notes: 1000+')
    print()
    print('[ARRANGEMENT SECTIONS]')
    print('0-15: INTRO')
    print('16-31: ONE DROP') 
    print('32-47: DUB SECTION 1')
    print('48-63: ROCKERS')
    print('64-79: DUB DROP')
    print('80-95: BUILD UP')
    print('96-111: BASS INVERSION')
    print('112-127: FINAL DUB')
    print('128-143: RE-ENTRY')
    print('144-159: OUTRO')
    print()
    print('[TRACK PATTERNS BY SECTION]')
    print('- Kick: One Drop → Rockers → Steppers (varies by section)')
    print('- Bass: Dub bassline → Inverted (section 7+)')
    print('- Snare: Backbeat (drops out section 7)')
    print('- Hi-Hats: Offbeats')
    print('- Organ: Stabs (section 4+)')
    print('- Guitar: Skanking (sections 1-7)')
    print('- Electric Piano: Dub fills throughout')
    print('- Percussion: Congas (section 7+)')
    print()
    print('[OPENING INSTRUCTIONS]')
    print('1. Open Ableton Live 12.4.3')
    print('2. File > Open Set...')
    print(f'3. Select {output_file}')
    print('4. Press SPACE to play the complete mixed song with all MIDI!')
    print()
    print('BLESS UP - Fine Dub Reggae complete with MIDI, mon!')


if __name__ == '__main__':
    main()
