#!/usr/bin/env python3
"""
GOLDEN_RATIO STUDIO - XML GENERATOR FIXED
Proper Ableton Live 12.4.3 ALS file generation with:
- Correct zlib compression/decompression
- XML escaping for special characters
- Proper track and device structures
- Return tracks with effects
- Validation and error handling
"""

import zlib
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("GoldenRatioStudio.XMLGenerator")

@dataclass
class AbletonTrack:
    """Ableton track configuration."""
    id: int
    name: str
    notes: List[Dict]
    midi_channel: int = 0
    volume: float = 0.75
    pan: float = 0.0
    instrument_path: str = "Drums/Acoustic/Memphis Studio Kit"

@dataclass
class AbletonReturnTrack:
    """Ableton return track with effects."""
    id: int
    name: str
    effects: List[str]
    volume: float = 0.8
    pan: float = 0.0

class AlexLiveXMLGenerator:
    """Generate Ableton Live 12.4.3 XML structure."""
    
    MAJOR_VERSION = 5
    MINOR_VERSION = "12.0_12402"
    CREATOR = "Ableton Live 12.4.3"
    SCHEMA_CHANGE_COUNT = 5
    
    @staticmethod
    def escape_xml(text: str) -> str:
        """Escape special XML characters."""
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text
    
    @staticmethod
    def create_midi_note_xml(note: Dict, indent: str = "                  ") -> str:
        """Create XML for a single MIDI note with validation."""
        try:
            time = float(note.get('time', 0))
            pitch = int(note.get('pitch', 36))
            velocity = int(note.get('velocity', 100))
            duration = float(note.get('duration', 0.5))
            
            # Validate MIDI ranges
            if not (0 <= pitch <= 127):
                logger.warning(f"Invalid pitch {pitch}, clipping to valid range")
                pitch = max(0, min(127, pitch))
            
            if not (1 <= velocity <= 127):
                logger.warning(f"Invalid velocity {velocity}, clipping to valid range")
                velocity = max(1, min(127, velocity))
            
            if duration < 0:
                logger.warning(f"Invalid duration {duration}, using minimum")
                duration = 0.01
            
            return f'{indent}<Note Time="{time:.3f}" Pitch="{pitch}" Velocity="{velocity}" Duration="{duration:.3f}" />\n'
        except Exception as e:
            logger.error(f"Error creating note XML: {e}")
            return ""
    
    @staticmethod
    def create_midi_track_xml(track: AbletonTrack) -> str:
        """Create XML for a MIDI track."""
        escaped_name = AlexLiveXMLGenerator.escape_xml(track.name)
        
        xml = f'''      <MidiTrack Id="{track.id}">
        <Name><EffectiveName Value="{escaped_name}"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset>
                <PresetPath Value="{track.instrument_path}"/></PresetPath>
              </Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer>
            <Volume Value="{track.volume}"/>
            <Pan Value="{track.pan}"/>
          </Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="{track.id}_slot">
            <ClipSlot>
              <Clip Id="{track.id}_clip" Time="0">
                <Name><EffectiveName Value="{escaped_name}"/></Name>
                <Loop>
                  <LoopOn Value="true"/>
                  <LoopStart Value="0"/>
                  <LoopLength Value="{len(track.notes) * 4}"/>
                </Loop>
                <NoteList>'''
        
        # Add MIDI notes
        for note in track.notes[:500]:  # Limit to 500 for file size
            xml += AlexLiveXMLGenerator.create_midi_note_xml(note)
        
        if len(track.notes) > 500:
            xml += f'                  <!-- {len(track.notes) - 500} additional notes omitted -->\n'
        
        xml += '''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>'''
        
        return xml
    
    @staticmethod
    def create_return_track_xml(track: AbletonReturnTrack) -> str:
        """Create XML for a return track with effects."""
        escaped_name = AlexLiveXMLGenerator.escape_xml(track.name)
        
        xml = f'''      <AudioTrack Id="{track.id}">
        <Name><EffectiveName Value="{escaped_name}"/></Name>
        <DeviceChain>
          <MainMixer>
            <Volume Value="{track.volume}"/>
            <Pan Value="{track.pan}"/>
          </MainMixer>
          <DeviceChain>
'''
        
        # Add effects devices
        for effect in track.effects:
            xml += f'            <SimpleAudioEffect Id="{effect.lower()}">\n'
            xml += f'              <Name><EffectiveName Value="{effect}"/></Name>\n'
            xml += f'              <Automation>\n'
            xml += f'                <Envelope Value="0.5" Min="0.0" Max="1.0"/>\n'
            xml += f'              </Automation>\n'
            xml += f'            </SimpleAudioEffect>\n'
        
        xml += '''          </DeviceChain>
        </DeviceChain>
      </AudioTrack>'''
        
        return xml
    
    @staticmethod
    def create_master_track_xml(bpm: int) -> str:
        """Create XML for master track with tempo."""
        return f'''    <MasterTrack>
      <DeviceChain>
        <Mixer>
          <Tempo>
            <Manual><Value Value="{bpm}"/></Manual>
          </Tempo>
          <Volume Value="0.88"/>
        </Mixer>
      </DeviceChain>
    </MasterTrack>'''
    
    @staticmethod
    def create_scenes_xml(sections: List[str], bar_count: int) -> str:
        """Create XML for scene markers."""
        xml = '    <Scenes>\n'
        
        for i, section in enumerate(sections):
            escaped_section = AlexLiveXMLGenerator.escape_xml(section)
            bar_start = int((i / len(sections)) * bar_count)
            time_position = bar_start * 4  # Convert bars to beats
            xml += f'      <Scene Id="{i}"><Name><EffectiveName Value="{escaped_section}"/></Name><Time Value="{time_position}"/></Scene>\n'
        
        xml += '    </Scenes>\n'
        return xml
    
    @staticmethod
    def create_ableton_xml(midi_tracks: List[AbletonTrack],
                          return_tracks: List[AbletonReturnTrack],
                          bpm: int,
                          sections: List[str],
                          bar_count: int) -> str:
        """Create complete Ableton Live XML structure."""
        
        # Build header
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Ableton MajorVersion="{AlexLiveXMLGenerator.MAJOR_VERSION}" 
        MinorVersion="{AlexLiveXMLGenerator.MINOR_VERSION}" 
        Creator="{AlexLiveXMLGenerator.CREATOR}" 
        SchemaChangeCount="{AlexLiveXMLGenerator.SCHEMA_CHANGE_COUNT}">
  <LiveSet>
    <Tracks>'''
        
        # Add MIDI tracks
        for track in midi_tracks:
            xml += '\n' + AlexLiveXMLGenerator.create_midi_track_xml(track)
        
        # Add return tracks
        for track in return_tracks:
            xml += '\n' + AlexLiveXMLGenerator.create_return_track_xml(track)
        
        xml += '\n    </Tracks>\n'
        
        # Add master track
        xml += AlexLiveXMLGenerator.create_master_track_xml(bpm) + '\n'
        
        # Add scenes
        xml += AlexLiveXMLGenerator.create_scenes_xml(sections, bar_count)
        
        # Add transport
        xml += '''  </LiveSet>
  <Transport>
    <LoopOn Value="true"/>
    <LoopStartTime Value="0.0"/>
    <LoopLength Value="''' + str(bar_count * 4) + '''"/>
  </Transport>
</Ableton>'''
        
        return xml

class AbletonProjectSaver:
    """Save Ableton projects with correct compression."""
    
    # Header magic bytes for Ableton files (not actual compressed, just a marker)
    FILE_HEADER = b' Golden Ratio Studio '
    
    @staticmethod
    def save_ableton_file(xml_content: str, filename: str) -> int:
        """Save Ableton project with proper compression."""
        try:
            # Validate XML
            if not xml_content or len(xml_content) < 100:
                raise ValueError("XML content too short or empty")
            
            # Encode to UTF-8
            xml_bytes = xml_content.encode('utf-8')
            logger.info(f"XML size: {len(xml_bytes)} bytes")
            
            # Compress with zlib
            compressed = zlib.compress(xml_bytes, level=9)
            logger.info(f"Compressed size: {len(compressed)} bytes")
            logger.info(f"Compression ratio: {len(compressed) / len(xml_bytes):.2%}")
            
            # Write file with header
            with open(filename, 'wb') as f:
                f.write(AbletonProjectSaver.FILE_HEADER)
                f.write(compressed)
            
            logger.info(f"Saved project: {filename}")
            return len(compressed)
            
        except Exception as e:
            logger.error(f"Error saving Ableton file {filename}: {e}")
            raise
    
    @staticmethod
    def load_ableton_file(filename: str) -> Optional[str]:
        """Load and decompress Ableton project file."""
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            if len(data) < len(AbletonProjectSaver.FILE_HEADER):
                raise ValueError("File too short to be valid Ableton file")
            
            # Skip header and decompress
            compressed = data[len(AbletonProjectSaver.FILE_HEADER):]
            xml_bytes = zlib.decompress(compressed)
            xml_content = xml_bytes.decode('utf-8')
            
            logger.info(f"Loaded project: {filename}")
            logger.info(f"Decompressed size: {len(xml_bytes)} bytes")
            
            return xml_content
            
        except Exception as e:
            logger.error(f"Error loading Ableton file {filename}: {e}")
            return None

def generate_and_save_project(project_data: Dict, filename: str,
                              return_tracks: Optional[List[AbletonReturnTrack]] = None) -> int:
    """Generate and save a complete Ableton project."""
    
    config = project_data['config']
    patterns = project_data['patterns']
    
    # Create MIDI tracks
    midi_tracks = []
    track_id = 0
    
    for track_name, notes in patterns.items():
        # Convert note objects to dictionaries
        note_dicts = []
        for note in notes:
            if hasattr(note, 'to_dict'):
                note_dicts.append(note.to_dict())
            elif isinstance(note, dict):
                note_dicts.append(note)
        
        # Set instrument based on track name
        instrument_path = "Drums/Acoustic/Memphis Studio Kit"
        if "Bass" in track_name:
            instrument_path = "Instruments/Piano/Piano Melt"
        elif "Guitar" in track_name:
            instrument_path = "Instruments/Guitar/Guitar Tab"
        elif "Pad" in track_name or "Synth" in track_name:
            instrument_path = "Instruments/Synth/Analog"
        
        track = AbletonTrack(
            id=track_id,
            name=track_name,
            notes=note_dicts,
            instrument_path=instrument_path
        )
        midi_tracks.append(track)
        track_id += 1
    
    # Create default return tracks if not provided
    if return_tracks is None:
        return_tracks = [
            AbletonReturnTrack(
                id=0,
                name="Dub Echo",
                effects=["Tape Delay", "Reverb"]
            ),
            AbletonReturnTrack(
                id=1,
                name="Master Reverb",
                effects=["Reverb", "Compressor"]
            )
        ]
    
    # Generate XML
    xml = AlexLiveXMLGenerator.create_ableton_xml(
        midi_tracks=midi_tracks,
        return_tracks=return_tracks,
        bpm=project_data.get('bpm', 120),
        sections=config.sections,
        bar_count=project_data.get('bar_count', 128)
    )
    
    # Save file
    file_size = AbletonProjectSaver.save_ableton_file(xml, filename)
    
    return file_size

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 80)
    print("GOLDEN RATIO STUDIO - XML GENERATOR TEST")
    print("=" * 80)
    print()
    
    # Create test project data
    test_project = {
        'genre': 'test_dub',
        'bpm': 78,
        'config': type('obj', (object,), {
            'sections': ['INTRO', 'DROP', 'OUTRO']
        })(),
        'patterns': {
            'Kick': [
                {'time': 0.0, 'pitch': 36, 'velocity': 100, 'duration': 0.5},
                {'time': 4.0, 'pitch': 36, 'velocity': 95, 'duration': 0.5},
            ],
            'Bass': [
                {'time': 0.0, 'pitch': 36, 'velocity': 110, 'duration': 2.0},
                {'time': 2.0, 'pitch': 43, 'velocity': 105, 'duration': 1.5},
            ]
        },
        'bar_count': 64
    }
    
    # Test saving
    try:
        size = generate_and_save_project(test_project, 'test_golden_ratio.als')
        print(f"[OK] Test project saved: test_golden_ratio.als ({size} bytes)")
        
        # Test loading
        content = AbletonProjectSaver.load_ableton_file('test_golden_ratio.als')
        if content:
            print(f"[OK] Test project loaded successfully")
            print(f"  XML length: {len(content)} characters")
            print(f"  First 200 chars: {content[:200]}")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("XML generator test complete!")
