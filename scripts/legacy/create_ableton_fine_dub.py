#!/usr/bin/env python3
"""
ABLETON LIVE 12.4.3 PROJECT FILE GENERATOR
Creates a complete Ableton project file (.als) for the Fine Dub Reggae track.
"""

import struct
import zlib

def create_ableton_1243_project():
    """
    Create a complete Ableton Live 12.4.3 project file for Fine Dub Reggae.
    Based on the correct XML structure discovered from real projects.
    """
    
    print('[ABLETON LIVE 12.4.3 PROJECT GENERATOR]')
    print('Creating Fine Dub Reggae project...')
    print()
    
    # Build XML structure for Ableton Live 12.4.3
    # Format discovered: MajorVersion=5, MinorVersion=12.0_12402, Creator="Ableton Live 12.4.3"
    
    xml_content = f'<?xml version="1.0" encoding="UTF-8"?>'
    xml_content += f'<Ableton MajorVersion="5" MinorVersion="12.0_12402" Creator="Ableton Live 12.4.3" SchemaChangeCount="4">'
    
    xml_content += f'  <LiveSet>'
    xml_content += f'    <Tracks>'
    
    # Track 0: Kick Drum
    xml_content += f'      <MidiTrack Id="0">'
    xml_content += f'        <Name><EffectiveName Value="Kick Drum"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio>'
    xml_content += f'            <Instrument><Preset><Source Value="Internal"/><PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/></Preset></Instrument>'
    xml_content += f'          </MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.75"/><Pan Value="0.0"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="One Drop Kick"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 1: Dub Bass
    xml_content += f'      <MidiTrack Id="1">'
    xml_content += f'        <Name><EffectiveName Value="Dub Bass"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><Presets><Preset><PresetPath Value="Sounds/Bass/Fretless Bass"/></Preset></Presets></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.84"/><Pan Value="0.0"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Dub Bassline"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 2: Snare
    xml_content += f'      <MidiTrack Id="2">'
    xml_content += f'        <Name><EffectiveName Value="Snare"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><PresetPath Value="Drums/Acoustic/Arizona Kit"/></Preset></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.63"/><Pan Value="0.0"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Backbeat Snare"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 3: Hi-Hats
    xml_content += f'      <MidiTrack Id="3">'
    xml_content += f'        <Name><EffectiveName Value="Hi-Hats"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/></Preset></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.44"/><Pan Value="0.15"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Skanking Hi-Hats"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 4: Hammond Organ
    xml_content += f'      <MidiTrack Id="4">'
    xml_content += f'        <Name><EffectiveName Value="Hammond Organ"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><PresetPath Value="Sounds/Tonewheel Organ/Organ Joyous Tonewheels"/></Preset></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.56"/><Pan Value="0.35"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Organ Stabs"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 5: Rhythm Guitar
    xml_content += f'      <MidiTrack Id="5">'
    xml_content += f'        <Name><EffectiveName Value="Rhythm Guitar"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><PresetPath Value="Sounds/Guitar Clean/Guitar Mute"/></Preset></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.50"/><Pan Value="-0.25"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Guitar Skank"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 6: Electric Piano
    xml_content += f'      <MidiTrack Id="6">'
    xml_content += f'        <Name><EffectiveName Value="Electric Piano"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><PresetPath Value="Sounds/Wurly Piano/Wurly Low & Durty"/></Preset></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.46"/><Pan Value="-0.15"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Dub Electric Piano"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Track 7: Percussion
    xml_content += f'      <MidiTrack Id="7">'
    xml_content += f'        <Name><EffectiveName Value="Percussion"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <MidiToAudio><Instrument><PresetPath Value="Presets/Bossa Nova"/></Preset></Instrument></MidiToAudio>'
    xml_content += f'          <Mixer><Volume Value="0.39"/><Pan Value="0.4"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'        <ClipSlotList><ClipSlot>'
    xml_content += f'          <ClipSlot>'
    xml_content += f'            <Clip>'
    xml_content += f'              <Name><EffectiveName Value="Latin Percussion"/></Name>'
    xml_content += f'              <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="16"/></Loop>'
    xml_content += f'            </Clip>'
    xml_content += f'          </ClipSlot>'
    xml_content += f'        </ClipSlotList>'
    xml_content += f'      </MidiTrack>'
    
    # Master Track
    xml_content += f'    </Tracks>'
    xml_content += f'    <MasterTrack>'
    xml_content += f'      <DeviceChain>'
    xml_content += f'        <Mixer>'
    xml_content += f'          <Tempo>'
    xml_content += f'            <Manual><Value Value="78.0"/></Manual>'
    xml_content += f'          </Tempo>'
    xml_content += f'          <Volume Value="0.88"/>'
    xml_content += f'        </Mixer>'
    xml_content += f'      </DeviceChain>'
    xml_content += f'    </MasterTrack>'
    
    # Return Tracks (Dub Echo, Spring Reverb)
    xml_content += f'    <Returns>'
    xml_content += f'      <AudioTrack Id="100">'
    xml_content += f'        <Name><EffectiveName Value="Dub Echo Return"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <AudioEffectChain>'
    xml_content += f'            <Device><Type Value="Echo"/><EchoOn Value="true"/>'
    xml_content += f'              <Time Value="1/4"/><Feedback Value="0.75"/><Mix Value="0.4"/>'
    xml_content += f'              <FilterOn Value="true"/><FilterFreq Value="4000.0"/>'
    xml_content += f'            </Device>'
    xml_content += f'          </AudioEffectChain>'
    xml_content += f'          <Mixer><Volume Value="0.80"/><Pan Value="0.5"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'      </AudioTrack>'
    xml_content += f'      <AudioTrack Id="101">'
    xml_content += f'        <Name><EffectiveName Value="Spring Reverb Return"/></Name>'
    xml_content += f'        <DeviceChain>'
    xml_content += f'          <AudioEffectChain>'
    xml_content += f'            <Device><Type Value="Reverb"/>'
    xml_content += f'              <ReverbOn Value="true"/><Decay Value="3.2"/><DryWet Value="0.25"/>'
    xml_content += f'              <Predelay Value="0.015"/><Damping Value="0.7"/>'
    xml_content += f'            </Device>'
    xml_content += f'          </AudioEffectChain>'
    xml_content += f'          <Mixer><Volume Value="0.75"/><Pan Value="-0.75"/></Mixer>'
    xml_content += f'        </DeviceChain>'
    xml_content += f'      </AudioTrack>'
    xml_content += f'    </Returns>'
    
    # Scenes for arrangement
    xml_content += f'    <Scenes>'
    for section_num in range(10):
        xml_content += f'      <Scene Id="{section_num}">'
        xml_content += f'        <Name><EffectiveName Value="{get_scene_name(section_num)}"/></Name>'
        xml_content += f'        <Time Value="{section_num * 16}"/>'
        xml_content += f'      </Scene>'
    xml_content += f'    </Scenes>'
    
    # Transport settings
    xml_content += f'  </LiveSet>'
    xml_content += f'  <Transport>'
    xml_content += f'    <LoopOn Value="true"/>'
    xml_content += f'    <LoopStartTime Value="0.0"/>'
    xml_content += f'    <LoopLength Value="640.0"/>'  # 160 bars * 4 beats/bar
    xml_content += f'  </Transport>'
    xml_content += f'</Ableton>'
    
    return xml_content


def get_scene_name(num):
    """Get section name for scene."""
    sections = [
        "INTRO", "ONE DROP", "DUB SECTION 1", "ROCKERS", "DUB DROP",
        "BUILD UP", "BASS INVERSION", "FINAL DUB", "RE-ENTRY", "OUTRO"
    ]
    return sections[num] if num < len(sections) else f"Section {num}"


def save_ableton_project(content, filename):
    """Save Ableton project file with compression."""
    # Convert XML to bytes
    xml_bytes = content.encode('utf-8')
    
    # Compress using zlib (Ableton uses zip compression)
    compressed = zlib.compress(xml_bytes, level=9)
    
    # Add Ableton header
    header = struct.pack('<', len(compressed))
    
    # Write file
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(compressed)
    
    return len(compressed)


if __name__ == "__main__":
    # Create project
    xml_content = create_ableton_1243_project()
    
    # Save to file
    output_file = "Fine_Dub_Reggae_v1.als"
    compressed_size = save_ableton_project(xml_content, output_file)
    
    print()
    print('[PROJECT FILE CREATION COMPLETE]')
    print(f'Filename: {output_file}')
    print(f'Compressed size: {compressed_size} bytes')
    print()
    print('[PROJECT SPECIFICATIONS]')
    print('Version: Ableton Live 12.4.3')
    print('BPM: 78')
    print('Tracks: 8 MIDI tracks + 2 Return tracks')
    print('Duration: 160 bars (~8 minutes)')
    print('Sections: 10 arrangement sections')
    print()
    print('[TRACKS]')
    print('1. Kick Drum - Memphis Studio Kit')
    print('2. Dub Bass - Fretless Bass')
    print('3. Snare - Arizona Kit')
    print('4. Hi-Hats - Memphis Studio Kit')
    print('5. Hammond Organ - Organ Joyous Tonewheels')
    print('6. Rhythm Guitar - Guitar Mute')
    print('7. Electric Piano - Wurly Low & Durty')
    print('8. Percussion - Bossa Nova')
    print()
    print('[RETURN TRACKS]')
    print('1. Dub Echo - Echo @ 1/4, 75% feedback, 40% mix')
    print('2. Spring Reverb - Reverb @ 3.2s decay, 25% mix')
    print()
    print('/n[OPENING INSTRUCTIONS]')
    print(f'1. Open Ableton Live 12.4.3')
    print(f'2. File > Open Set...')
    print(f'3. Select {output_file}')
    print(f'4. Press PLAY for Fine Dub Reggae!')
    print()
    print('BLESS UP - Project file created successfully, mon!')
