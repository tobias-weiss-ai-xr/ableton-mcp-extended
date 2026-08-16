#!/usr/bin/env python3
"""Create complete Fine Dub Reggae project file."""

import zlib

print('[FINE DUB REAGAE - COMPLETE MIXED SONG PROJECT]')
print('=' * 80)
print()

# Build complete XML
xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Ableton MajorVersion="5" MinorVersion="12.0_12402" Creator="Ableton Live 12.4.3" SchemaChangeCount="4">
  <LiveSet>
    <Tracks>
      <MidiTrack Id="0">
        <Name><EffectiveName Value="Kick Drum"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.75"/><Pan Value="0.0"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="0_clip_0" Time="0">
                <Name><EffectiveName Value="Full Arrangement - Kick"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="640"/></Loop>
                <NoteList>'''

# Add kick notes (160 bars)
for bar in range(160):
    time = bar * 4 + 0
    xml += f'                  <Note Time="{time}" Pitch="36" Velocity="110" Duration="0.5"/>\n'
    if 32 <= bar < 64:  # Rockers
        xml += f'                  <Note Time="{bar * 4 + 3}" Pitch="36" Velocity="105" Duration="0.4"/>\n'
    elif 64 <= bar < 96:  # Steppers
        xml += f'                  <Note Time="{bar * 4 + 1}" Pitch="36" Velocity="108" Duration="0.3"/>\n'
        xml += f'                  <Note Time="{bar * 4 + 2}" Pitch="36" Velocity="108" Duration="0.3"/>\n'
        xml += f'                  <Note Time="{bar * 4 + 3}" Pitch="36" Velocity="108" Duration="0.3"/>\n'

xml += f'''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>
      <MidiTrack Id="1">
        <Name><EffectiveName Value="Dub Bass"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Sounds/Bass/Fretless Bass"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.84"/><Pan Value="0.0"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="1_clip_0" Time="0">
                <Name><EffectiveName Value="Full Arrangement - Bass"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="640"/></Loop>
                <NoteList>'''

# Add bass notes
for bar in range(160):
    if bar < 96:
        xml += f'                  <Note Time="{bar * 4 + 0}" Pitch="24" Velocity="120" Duration="2.0"/>\n'
        xml += f'                  <Note Time="{bar * 4 + 2}" Pitch="31" Velocity="110" Duration="1.5"/>\n'
    else:
        xml += f'                  <Note Time="{bar * 4 + 0}" Pitch="20" Velocity="120" Duration="2.0"/>\n'
        xml += f'                  <Note Time="{bar * 4 + 2}" Pitch="24" Velocity="115" Duration="1.5"/>\n'

xml += f'''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>
      <MidiTrack Id="2">
        <Name><EffectiveName Value="Snare"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Drums/Acoustic/Arizona Kit"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.63"/><Pan Value="0.0"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="2_clip_0" Time="0">
                <Name><EffectiveName Value="Full Arrangement - Snare"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="640"/></Loop>
                <NoteList>'''

# Add snare (drops out)
for bar in range(112):
    xml += f'                  <Note Time="{bar * 4 + 2}" Pitch="40" Velocity="100" Duration="0.3"/>\n'

xml += f'''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>
      <MidiTrack Id="3">
        <Name><EffectiveName Value="Hi-Hats"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Drums/Acoustic/Memphis Studio Kit"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.44"/><Pan Value="0.15"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="3_clip_0" Time="0">
                <Name><EffectiveName Value="Full Arrangement - HiHats"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="640"/></Loop>
                <NoteList>'''

# Hi-hats
for bar in range(160):
    xml += f'                  <Note Time="{bar * 4 + 1}" Pitch="42" Velocity="75" Duration="0.2"/>\n'
    xml += f'                  <Note Time="{bar * 4 + 3}" Pitch="42" Velocity="75" Duration="0.2"/>\n'

xml += f'''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>
      <MidiTrack Id="4">
        <Name><EffectiveName Value="Hammond Organ"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Sounds/Tonewheel Organ/Organ Joyous Tonewheels"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.56"/><Pan Value="0.35"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="4_clip_0" Time="0">
                <Name><EffectiveName Value="Full Arrangement - Organ"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="640"/></Loop>
                <NoteList>'''

# Organ (starts bar 48)
for bar in range(48, 160):
    if bar % 2 == 0:
        xml += f'                  <Note Time="{bar * 4 + 0}" Pitch="60" Velocity="100" Duration="1.0"/>\n'
        xml += f'                  <Note Time="{bar * 4 + 2}" Pitch="67" Velocity="95" Duration="0.8"/>\n'

xml += f'''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>
      <MidiTrack Id="5">
        <Name><EffectiveName Value="Rhythm Guitar"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Sounds/Guitar Clean/Guitar Mute"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.50"/><Pan Value="-0.25"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="5_clip_0" Time="0">
                <Name><EffectiveName Value="Full Arrangement - Guitar"/></Name>
                <Loop><LoopOn Value="true"/><LoopStart Value="0"/><LoopLength Value="640"/></Loop>
                <NoteList>'''

# Guitar (bars 16-112)
for bar in range(16, 112):
    for half in [0.5, 1.5, 2.5, 3.5]:
        xml += f'                  <Note Time="{bar * 4 + half}" Pitch="60" Velocity="85" Duration="0.3"/>\n'

xml += f'''                </NoteList>
              </Clip>
            </ClipSlot>
          </ClipSlot>
        </ClipSlotList>
      </MidiTrack>
      <MidiTrack Id="6">
        <Name><EffectiveName Value="Electric Piano"/></Name>
        <DeviceChain>
          <MidiToAudio>
            <Instrument>
              <Preset><PresetPath Value="Sounds/Wurly Piano/Wurly Low & Durty"/></Preset>
            </Instrument>
          </MidiToAudio>
          <Mixer><Volume Value="0.46"/><Pan Value="-0.15"/></Mixer>
        </DeviceChain>
        <ClipSlotList>
          <ClipSlot Id="0">
            <ClipSlot>
              <Clip Id="6_clip_0" Time="0">
                <Name><Effec
