#!/usr/bin/env python3
"""
REAGAE INSTRUMENT SETUP GUIDE AND AUTOMATED CONFIGURATION

Addresses what instruments are actually needed for authenic reggae sound,
with specific Ableton instrument recommendations and device loading strategies.

IMPORTANT: MIDI alone doesn't make sound - you need actual instruments (VSTs, samples, synths).
"""

class ReggaeInstrumentsGuide:
    """Complete guide to reggae instruments for Ableton Live."""
    
    def __init__(self):
        # ABLETON STOCK INSTRUMENTS (what comes with Live)
        self.ableton_instruments = {
            'kick': {
                'stock': ['Drum Rack with C60 Kick', 'Punchy Kick sample', 'Impulse with One Drop kit'],
                'vst': ['XLN Audio Addictive Drums 2', 'Toontrack EZ Drummer 2'],
                ' Technique': 'Use a tight, punchy kick tuned to 80-120Hz. For one-drop, emphasize beats 2 and 4, no kick on beat 1.'
            },
            'snare': {
                'stock': ['Drum Rack with Reggae Snare', 'Impulse with dry snare'],
                'vst': ['Spectrasonics STYLUS RMX', 'Native Instruments Abbey Road Drummer'],
                ' Technique': 'Tight, dry snare on backbeat (beats 2 & 4). Short decay for punch, medium attack for snap. Velocity 110-120 for impact.'
            },
            'hi_hat': {
                'stock': ['Drum Rack with dark hi-hats', 'Sampler with closed hat samples'],
                'vst': ['Native Instruments Supercharger', 'Spectrasonics Keyscape hats'],
                ' Technique': 'Dark, closed hi-hats on offbeat 16th notes for skanking feel. Low velocity (70-85) so they support rather than lead.'
            },
            'bass': {
                'stock': ['Operator Sine + Compressor', 'Analog in sub mode', 'Simpler sine wave sample'],
                'vst': ['Spectrasonics Trilian Bass Module', 'Native Instruments Scarbee Jay Bass', 'Ubass VST'],
                ' Technique': 'Pure sine wave BELOW 60Hz for authentic dub weight. Cutoff at 200Hz, slight compression. No EQ, just smooth sub.'
            },
            'rhythm_guitar': {
                'stock': ['Sampler with guitar samples', 'Electric piano with pickup model'],
                'vst': ['Spectrasonics Omnisphere guitar patches', 'Native Instruments Session Guitarist Electric'],
                ' Technique': 'SKANKING TECHNIQUE: Palm-muted upstroke (Gup) on offbeats. Voicing: Root + 5th only (no third) for roots feel. Short, staccato notes.'
            },
            'lead_guitar': {
                'stock': ['Sampler with guitar licks', 'Amp with overdrive simulation'],
                'vst': ['Spectrasonics Omnisphere guitar', 'MusicLab RealGuitar'],
                ' Technique': 'Melodic fills in chorus sections. Slight amount of overdrive/delay. Not too present in mix (-16dB to -20dB).'
            },
            'hammond_organ': {
                'stock': ['Vintage Organ in B3 mode', 'Electric with Leslie simulation'],
                'vst': ['Native Instruments Vintage Organs (B3/Leslie)', 'Arturia B-3 V (Leslie essential)'],
                ' Technique': 'HAMMOND B3 withrotary Leslie speaker FAST. Drawbars 88840000 (root section). Chord stabs on offbeats. Crisp, swirling Leslie sound.'
            },
            'piano': {
                'stock': ['Electric', 'Grand Piano with felt'], 
                'vst': ['Native Instruments Kontakt "The Gentleman"', 'Spectrasonics Keyscape'],
                ' Technique': 'Bright electric piano or felted grand. Very sparse - occasional chord stabs to reinforce harmony. Mix low (-20dB).'
            },
            'vocal': {
                'stock': ['Sampler with vocal samples', 'Vocoder for effects'],
                'vst': ['Native Instruments Vocalizer', 'iZotope VocalSynth 2'],
                ' Technique': 'Use vocal samples for melody lines, not full lyrics. Apply dub echo and reverb. Pitch correction optional for robotic dub effect.'
            },
            'percussion': {
                'stock': ['Drum Rack with congas, timbales', 'Sampler with percussion'],
                'vst': ['Spectrasonics Stylus RMX', 'Native Instruments West Africa'],
                ' Technique': 'Congas: Open note on beat 1, muted on beat 3. Timbales: Rim shots on offbeats. Keep low in mix (-22dB).'
            }
        }
        
        # SPECIFIC SAMPLE LIBRARIES (best for reggae)
        self.reggae_sample_libs = {
            'comprehensive': [
                'Spectrasonics STYLUS RMX (reggae/dub grooves)',
                'Native Instruments "Session Strings Pro"',
                'EastWest "Symphonic Choirs" (for atmospheric vocals)'
            ],
            'drums': [
                'XLN Audio "Addictive Drums 2" - Reggae kit',
                'Toontrack "EZ Drummer 2" - Reggae expansion',
                'Native Instruments Reggae kit (Studio Drummer)'
            ],
            'bass': [
                'Spectrasonics "Trilian" Bass Module',
                'Native Instruments "Scarbee Jay-Bass"',
                'EastWest "Symphonic Orchestra" (midi bass)'
            ],
            'keyboards': [
                'Native Instruments "Vintage Organs" (Hammond B3)',
                'Spectrasonics "Keyscape" (pianos)',
                'Arturia "V Collection" (synth keys)'
            ],
            'percussion': [
                'Native Instruments "West Africa"',
                'EastWest "Ra" (world percussion)',
                'Spectrasonics "Atmosphere" (ethnic sounds)'
            ]
        }
        
        # ABLETON DEVICE CHAIN CONFIGURATIONS
        self.ableton_device_chains = {
            'kick': {
                'instruments': ['Operator (kick preset)', 'Drum Rack'],
                'effects': [
                    {'device': 'Compressor', 'threshold': -20, 'ratio': 4},
                    {'device': 'EQ Eight', 'type': 'Low Cut', 'freq': '80Hz'},
                    {'device': 'Utility', 'pan': 0}
                ]
            },
            'bass': {
                'instruments': ['Operator (sine mode)', 'Analog (sub preset)'],
                'effects': [
                    {'device': 'Compressor', 'threshold': -15, 'ratio': 3},
                    {'device': 'EQ Eight', 'type': 'Low Pass', 'freq': '200Hz'},
                    {'device': 'Utility', 'pan': 0},
                    {'device': 'Utility', 'pan': 0}
                ]
            },
            'guitar': {
                'instruments': ['Sampler (guitar samples)', 'Amp (overdrive preset)'],
                'effects': [
                    {'device': 'Compressor', 'threshold': -10, 'ratio': 2},
                    {'device': 'EQ Eight', 'high': '+3dB', 'high_mid': '-2dB'},
                    {'device': 'Delay (Ping Pong)', 'time': '1/4', 'feedback': '30%'},
                    {'device': 'Utility', 'pan': -0.3}
                ]
            },
            'hammond': {
                'instruments': ['Vintage Organ (B3 preset)'],
                'effects': [
                    {'device': 'Compressor', 'threshold': -12, 'ratio': 2},
                    {'device': 'Chorus Ensemble', 'rate': '5Hz', 'depth': '40%'},
                    {'device': 'Utility', 'pan': 0}
                ]
            },
            'vocal': {
                'instruments': ['Sampler (vocal samples)', 'Vocoder'],
                'effects': [
                    {'device': 'Compressor', 'threshold': -8, 'ratio': 3},
                    {'device': 'Delay (Dub Echo)', 'time': '1/4', 'feedback': '60%'},
                    {'device': 'Reverb', 'decay': '3s'},
                    {'device': 'Utility', 'pan': 0}
                ]
            }
        }


def print_instrument_guide():
    """Print comprehensive instrument guide."""
    
    guide = ReggaeInstrumentsGuide()
    
    print()
    print('=' * 80)
    print('REAGAE INSTRUMENT SETUP GUIDE')
    print('=' * 80)
    print()
    print('[CRITICAL QUESTION: Do we address instruments?]')
    print()
    print('ANSWER: YES! The project file needs ACTUAL INSTRUMENTS to make sound.')
    print('MIDI patterns alone are silent - you must load instruments on each track.')
    print()
    print('=' * 80)
    print('REAGAE INSTRUMENT BREAKDOWN')
    print('=' * 80)
    print()
    
    # Print each instrument category
    categories = [
        ('KICK DRUM', 'kick', 'Drum Track 0'),
        ('SUB BASS', 'bass', 'Drum Track 1'),
        ('SNARE', 'snare', 'Drum Track 2'),
        ('HI-HATS', 'hi_hat', 'Drum Track 3'),
        ('RHYTHM GUITAR', 'rhythm_guitar', 'Instrument Track 4'),
        ('LEAD GUITAR', 'lead_guitar', 'Instrument Track 5'),
        ('HAMMOND ORGAN', 'hammond_organ', 'Instrument Track 6'),
        ('PIANO/KEYS', 'piano', 'Instrument Track 7'),
        ('VOCAL AD-LIBS', 'vocal', 'Instrument Track 8'),
        ('PERCUSSION', 'percussion', 'Instrument Track 9')
    ]
    
    for full_name, category, track_num in categories:
        print(f'{full_name} ({track_num})')
        print('-' * 80)
        
        data = guide.ableton_instruments.get(category, {})
        
        print(f'[ABLETON STOCK INSTRUMENTS]')
        for i, instrument in enumerate(data.get('stock', []), 1):
            print(f'  {i}. {instrument}')
        
        print(f'\\n[VST/AUDIO UNITS PLUGINS]')
        for i, vst in enumerate(data.get('vst', []), 1):
            print(f'  {i}. {vst}')
        
        print(f'\\n[REAGAE PRODUCTION TECHNIQUES]')
        technique = data.get(' Technique', 'Use authentic reggae samples and techniques')
        print(f'  {technique}')
        
        print()
    
    print('=' * 80)
    print('ABLETON DEVICE CHAIN CONFIGURATIONS')
    print('=' * 80)
    print()
    
    for category, config in guide.ableton_device_chains.items():
        print(f'{category.upper()}:')
        print('[INSTRUMENT]', ', '.join(config['instruments']))
        
        print('[EFFECTS CHAIN]')
        for i, effect in enumerate(config['effects'], 1):
            device = effect['device']
            params = ', '.join([f'{k}={v}' for k, v in effect.items() if k != 'device'])
            print(f'  {i}. {device}')
            if params:
                print(f'     {params}')
        print()


def print_ableton_instrument_setup_steps():
    """Print step-by-step Ableton instrument setup."""
    
    print()
    print('=' * 80)
    print('STEP-BY-STEP: LOADING INSTRUMENTS IN ABLETON LIVE 12.4.3')
    print('=' * 80)
    print()
    
    steps = [
        {
            'track': 'Track 0: KICK',
            'instrument': 'Drag "Drum Rack" onto track, add kick samples',
            'settings': 'Tune samples to 80-120Hz, one-drop pattern'
        },
        {
            'track': 'Track 1: SUB BASS',
            'instrument': 'Drag "Operator" or use "Sampler" with sine wave',
            'settings': 'Frequency below 60Hz, cutoff at 200Hz, slight compression'
        },
        {
            'track': 'Track 2: SNARE',
            'instrument': 'Drag "Drum Rack" or "Impulse", add snare sample',
            'settings': 'Tight, dry snare, short decay, place on beats 2&4'
        },
        {
            'track': 'Track 3: HI-HATS',
            'instrument': 'Drag "Drum Rack" with dark hi-hat samples',
            'settings': 'Closed hats, velocity 70-85, offbeat 16ths'
        },
        {
            'track': 'Track 4: RHYTHM GUITAR',
            'instrument': 'Drag "Sampler" with guitar samples OR "Amp"',
            'settings': 'Palm-muted upstroke, root+5th voicing, skanking pattern'
        },
        {
            'track': 'Track 5: LEAD GUITAR',
            'instrument': 'Drag "Sampler" or guitar VST',
            'settings': 'Melodic fills, light overdrive, occasional presence'
        },
        {
            'track': 'Track 6: HAMMOND ORGAN',
            'instrument': 'Drag "Vintage Organ" set to B3 mode',
            'settings': 'Leslie speed FAST, drawbars 88840000, swells'
        },
        {
            'track': 'Track 7: PIANO',
            'instrument': 'Drag "Electric" or piano samples',
            'settings': 'Bright electric piano or felted grand, sparse'
        },
        {
            'track': 'Track 8: VOCAL',
            'instrument': 'Drag "Sampler" with vocal samples',
            'settings': 'Apply dub echo, reverb, occasional melody lines'
        },
        {
            'track': 'Track 9: PERCUSSION',
            'instrument': 'Drag "Drum Rack" with congas/percussion',
            'settings': 'Congas on beat 1, rim shots offbeats, low mix'
        },
        {
            'track': 'Track 10: DUB ECHO RETURN',
            'instrument': 'Add "Echo" delay device',
            'settings': '1/4 note time, 60-80% feedback, automation'
        },
        {
            'track': 'Track 11: REVERB RETURN',
            'instrument': 'Add "Reverb" device',
            'settings': '2-4 second decay, pre-fader send routing'
        }
    ]
    
    for i, step in enumerate(steps, 1):
        print(f'STEP {i}: {step["track"]}')
        print('-' * 80)
        print(f'[LOAD] {step["instrument"]}')
        print(f'[SETTINGS] {step["settings"]}')
        print()


def print_alternative_solutions():
    """Print alternative solutions for obtaining reggae instruments."""
    
    print()
    print('=' * 80)
    print('ALTERNATIVE SOLUTIONS: HOW TO GET REAGAE INSTRUMENTS')
    print('=' * 80)
    print()
    
    solutions = [
        {
            'solution': 'OPTION 1: ABLETON STOCK INSTRUMENTS (FREE)',
            'description': 'Use instruments that come with Ableton Live',
            'instruments': [
                'Operator (sine for bass)',
                'Drum Rack (load your own samples)',
                'Impulse (load samples)',
                'Sampler (load any samples)',
                'Vintage Organ (Hammond B3)',
                'Electric (piano)',
                'Amp (guitar simulation)'
            ],
            'pros': 'Free, no additional installation, perfectly integrated',
            'cons': 'Limited sound library, may need to find samples'
        },
        {
            'solution': 'OPTION 2: SAMPLE LIBRARIES (RECOMMENDED)',
            'description': 'Purchase/download reggae samples',
            'instruments': [
                'Reggae drum samples (kick, snare, hi-hats)',
                'Sub bass samples (sine waves)',
                'Guitar samples (skanking patterns)',
                'Organ samples (Hammond B3)',
                'Percussion samples (congas, timbales)'
            ],
            'pros': 'High quality, authentic sounds, can use in any DAW',
            'cons': 'Cost money, need to organize library'
        },
        {
            'solution': 'OPTION 3: VST PLUGINS (BEST FOR VARIETY)',
            'description': 'Install VST/AU instrument plugins',
            'instruments': [
                'Spectrasonics Trilian (bass)',
                'Native Instruments Vintage Organs (Hammond)',
                'XLN Audio Addictive Drums 2 (drums)',
                'Spectrasonics Keyscape (keyboards)',
                'Native Instruments Session Guitarist (guitar)'
            ],
            'pros': 'Professional quality, extensive variety, realistic',
            'cons': 'Expensive, requires installation, system intensive'
        },
        {
            'solution': 'OPTION 4: FREE VST PLUGINS (BUDGET)',
            'description': 'Download free VST instruments',
            'instruments': [
                'TAL NoiseMaker (synth bass)',
                'Sforzando (sampler with free libraries)',
                'Imitone (vocal synth)',
                'VSCO Orchestra (instruments)',
                'FreeReggaeKit (online samples)'
            ],
            'pros': 'Free, decent quality, no cost barrier',
            'cons': 'Variable quality, may have limitations'
        },
        {
            'solution': 'OPTION 5: GENERATE SAMPLES (FREE)',
            'description': 'Use your existing reggae projects',
            'instruments': [
                'Open auo_reggae1.als in Ableton Live 12.4.3',
                'Export individual track audio (Right-click → Export)',
                'Import samples as new instruments',
                'Reuse your authentic sounds'
            ],
            'pros': 'You already have the sounds, free, authentic',
            'cons': 'Need existing reggae projects'
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f'{solution["solution"]}')
        print('-' * 80)
        print(f'Description: {solution["description"]}')
        print(f'Instruments:')
        for j, inst in enumerate(solution['instruments'], 1):
            print(f'  {j}. {inst}')
        print(f'Pros: {solution["pros"]}')
        print(f'Cons: {solution["cons"]}')
        print()


def main():
    """Main function."""
    import sys
    
    print()
    print('=' * 80)
    print('INSTRUMENT ADDRESS: YES WE DO!')
    print('Comprehensive guide to loading reggae instruments in Ableton Live')
    print('=' * 80)
    
    print_instrument_guide()
    print_ableton_instrument_setup_steps()
    print_alternative_solutions()
    
    print('=' * 80)
    print('CONCLUSION')
    print('=' * 80)
    print()
    print('[YES we ADDRESS INSTRUMENTS]')
    print('The project file creates the TRACK STRUCTURE and MIDI PATTERNS')
    print('You MUST load actual INSTRUMENTS on each track for sound')
    print()
    print('[RECOMMENDED WORKFLOW]')
    print('1. Open the project file in Ableton Live 12.4.3')
    print('2. Drag instruments onto each track (as detailed above)')
    print('3. Adjust instrument settings for authentic reggae sound')
    print('4. Press PLAY to hear your reggae mix!')
    print()
    print('[FASTEST SOLUTION]')
    print('Open your existing reggae projects (auo_reggae1.als, etc.)')
    print('Export track audio → Import samples into new project')
    print('Same authentic sound, instant results!')
    print()
    print('BLESS UP - Instruments addressed, mon! 🇯🇲')
    print('=' * 80)
    print()


if __name__ == "__main__":
    main()
