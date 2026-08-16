#!/usr/bin/env python3
"""
FINE DUB REAGAE TRACK GENERATOR
Creates a complete dub reggae track using your Ableton instrument inventory.
"""

from pathlib import Path
import random
import math

def generate_dub_reggae_track():
    """Generate complete fine dub reggae track design."""
    
    print('FINE DUB REAGAE TRACK GENERATOR')
    print('=' * 80)
    print()
    
    # Your Ableton instrument inventory
    base_path = Path('C:/Users/Tobias/Documents/Ableton/Factory Packs')
    
    # Select perfect instruments for fine dub reggae
    dub_instruments = {
        'kick': {
            'pack': 'Drum Essentials', 
            'preset': 'Memphis Studio Kit',
            'notes': 'One-drop kick pattern, tight professional room sound'
        },
        'bass': {
            'pack': 'Guitar and Bass',
            'preset': 'Fretless Bass', 
            'notes': 'Smooth dub bass, essential for authentic dub weight'
        },
        'snare': {
            'pack': 'Drum Essentials',
            'preset': 'Arizona Kit',
            'notes': 'Tight backbeat snare, dry sound for dub echo'
        },
        'hihats': {
            'pack': 'Drum Essentials', 
            'preset': 'Memphis Studio Kit',
            'notes': 'Dark hi-hats, offbeat skanking rhythm'
        },
        'organ': {
            'pack': 'Electric Keyboards',
            'preset': 'Organ Joyous Tonewheels',
            'notes': 'Happy Hammond B3, essential for reggae'
        },
        'guitar': {
            'pack': 'Guitar and Bass',
            'preset': 'Guitar Mute',
            'notes': 'Palm-muted guitar for authentic skanking'
        },
        'electric_piano': {
            'pack': 'Electric Keyboards',
            'preset': 'Wurly Low & Durty', 
            'notes': 'Gritty low electric piano for dub character'
        },
        'percussion': {
            'pack': 'Latin Percussion',
            'preset': 'Bossa Nova',
            'notes': 'Congas and timbales for authentic reggae'
        }
    }
    
    print('SELECTED INSTRUMENTS FOR FINE DUB REAGAE:')
    print('-' * 80)
    for name, details in dub_instruments.items():
        print(f'{name.upper()}:')
        print(f'  Pack: {details["pack"]}')
        print(f'  Preset: {details["preset"]}')
        print(f'  Notes: {details["notes"]}')
        print()
    
    print('=' * 80)
    print('FINE DUB REAGAE TRACK STRUCTURE')
    print('=' * 80)
    
    # Define fine dub track structure
    track_structure = [
        {'section': 'INTRO', 'bars': (0, 15), 'elements': ['kick', 'bass', 'hihats', 'subtle wash'], 'dub_level': 'light'},
        {'section': 'ONE DROP', 'bars': (16, 31), 'elements': ['kick', 'bass', 'snare', 'hihats', 'guitar skank'], 'dub_level': 'light'},  
        {'section': 'DUB SECTION 1', 'bars': (32, 47), 'elements': ['kick syncopated', 'bass drops', 'echo effects', 'filter sweeps'], 'dub_level': 'medium'},
        {'section': 'ROCKERS', 'bars': (48, 63), 'elements': ['rockers kick', 'bassline', 'guitar skanks', 'organ stabs'], 'dub_level': 'low'},
        {'section': 'DUB DROP', 'bars': (64, 79), 'elements': ['heavy bass drops', 'punchy echoes', 'filter automation', 'space'], 'dub_level': 'heavy'},
        {'section': 'BUILD UP', 'bars': (80, 95), 'elements': ['kick pattern evolves', 'bass layers', 'guitar fills', 'organ intensity'], 'dub_level': 'medium'},
        {'section': 'BASS INVERSION', 'bars': (96, 111), 'elements': ['inverted bassline', 'dub echo intensifies', 'percussion enters', 'space'], 'dub_level': 'heavy'},
        {'section': 'FINAL DUB', 'bars': (112, 127), 'elements': ['echo melodies', 'bass drops', 'filter banks', 'tape echo'], 'dub_level': 'maximum'},
        {'section': 'RE-ENTRY', 'bars': (128, 143), 'elements': ['full rhythm returns', 'organ crescendo', 'guitar fills', 'percussion'], 'dub_level': 'medium'},
        {'section': 'OUTRO', 'bars': (144, 159), 'elements': ['elements strip away', 'echo dominates', 'final bass drop', 'fade'], 'dub_level': 'light to fade'}
    ]
    
    for section in track_structure:
        start, end = section['bars']
        duration = end - start + 1
        element_str = ', '.join(section['elements'])
        print(f'{section["section"]} (Bars {start}-{end}, {duration} bars):')
        print(f'  Dub Level: {section["dub_level"]}')
        print(f'  Elements: {element_str}')
        print()
    
    print('=' * 80)
    print('FINE DUB REAGAE MIXING PARAMETERS')
    print('=' * 80)
    
    mix_parameters = {
        'BPM': 78,
        'Key': 'C Minor',
        'Time Signature': '4/4',
        'Master Volume': -3.0,
        'Volumes': {
            'Kick': -7.0,
            'Bass': -5.0,
            'Snare': -9.0,
            'Hi-Hats': -15.0,
            'Guitar': -12.0,
            'Organ': -10.0,
            'Electric Piano': -14.0,
            'Percussion': -18.0,
            'Dub Echo Send': -4.0,
            'Spring Reverb Send': -6.0
        },
        'Panning': {
            'Kick': 0.0,
            'Bass': 0.0,
            'Snare': 0.0,
            'Hi-Hats': 0.15,
            'Guitar': -0.25,
            'Organ': 0.35,
            'Electric Piano': -0.15,
            'Percussion': 0.4,
            'Dub Echo': 0.5,
            'Spring Reverb': -0.75
        },
        'Echo Settings': {
            'Time': '1/4',
            'Feedback': '75%',
            'Mix': '40%',
            'Filter': 'Low-pass at 4kHz',
            'Saturation': 'Slight tape compression'
        },
        'Reverb Settings': {
            'Type': 'Spring',
            'Decay': '3.2s', 
            'Pre-delay': '15ms',
            'Mix': '25%',
            'Damping': 'High frequencies'
        }
    }
    
    print('TEMPO AND KEY:')
    print(f'  BPM: {mix_parameters["BPM"]} (Perfect dub tempo)')
    print(f'  Key: {mix_parameters["Key"]} (C Minor - classic dub)')
    print(f'  Time: {mix_parameters["Time Signature"]}')
    print()
    
    print('VOLUME LEVELS (dB):')
    for track, level in mix_parameters['Volumes'].items():
        print(f'  {track}: {level} dB')
    print()
    
    print('PANNING (L/R):')  
    for track, val in mix_parameters['Panning'].items():
        position = 'CENTER' if abs(val) < 0.05 else ('LEFT' if val < 0 else 'RIGHT')
        print(f'  {track}: {position} ({val})')
    print()
    
    print('ECHO SETTINGS (Essential for dub!):')
    for setting, value in mix_parameters['Echo Settings'].items():
        print(f'  {setting}: {value}')
    print()
    
    print('REVERB SETTINGS:')
    for setting, value in mix_parameters['Reverb Settings'].items():
        print(f'  {setting}: {value}')
    
    print()
    print('=' * 80)
    print('FINE DUB REAGAE TRACK READY TO PRODUCE!')
    print('=' * 80)
    print(f'Instruments selected: {len(dub_instruments)}')
    print(f'Track structure: {len(track_structure)} sections')
    print(f'Total duration: 160 bars @ 78 BPM = ~8 minutes')
    print(f'Mix parameters: Configured for authentic dub')
    print()
    print('[INSTRUCTIONS FOR PRODUCTION]')
    print('1. Open Ableton Live 12.4.3')
    print('2. Create 8 audio/MIDI tracks as specified')
    print('3. Load instruments as listed above')
    print('4. Apply mixing parameters')
    print('5. Create arrangement using track structure')
    print('6. Press PLAY for authentic fine dub reggae!')
    print()
    print('BLESS UP - Fine dub reggae track designed, mon!')
    
    return dub_instruments, mix_parameters, track_structure


if __name__ == "__main__":
    generate_dub_reggae_track()
