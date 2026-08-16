#!/usr/bin/env python3
"""
ABLETON INSTRUMENTS INVENTORY SCRIPT
Systematically inventories all your Ableton instruments, effects, and samples.
"""

import os
from pathlib import Path
import json

class AbletonInventory:
    """Complete inventory of Ableton content."""
    
    def __init__(self, base_path="/c/Users/Tobias/Documents/Ableton"):
        self.base_path = Path(base_path)
        self.inventory = {
            'factory_packs': {},
            'user_presets': {},
            'samples': {},
            'effects': {},
            'instruments': {},
            'total_count': 0
        }
    
    def inventory_factory_packs(self):
        """Inventory all factory packs."""
        factory_packs_path = self.base_path / "Factory Packs"
        if not factory_packs_path.exists():
            return
        
        print("=" * 80)
        print("INVENTORYING FACTORY PACKS")
        print("=" * 80)
        
        for pack_dir in sorted(factory_packs_path.iterdir()):
            if pack_dir.is_dir():
                pack_name = pack_dir.name
                self.inventory['factory_packs'][pack_name] = {
                    'path': str(pack_dir),
                    'presets': [],
                    'samples': [],
                    'total_presets': 0
                }
                
                # Find all .adg files (presets)
                for adg_file in pack_dir.rglob("*.adg"):
                    relative_path = adg_file.relative_to(pack_dir)
                    preset_info = {
                        'name': adg_file.stem,
                        'path': str(adg_file),
                        'relative_path': str(relative_path),
                        'category': str(relative_path.parts[-2]) if len(relative_path.parts) > 1 else 'Root'
                    }
                    self.inventory['factory_packs'][pack_name]['presets'].append(preset_info)
                
                # Count total
                self.inventory['factory_packs'][pack_name]['total_presets'] = len(
                    self.inventory['factory_packs'][pack_name]['presets']
                )
                
                # Print summary
                total = self.inventory['factory_packs'][pack_name]['total_presets']
                print(f"\n📦 {pack_name}: {total} presets")
                
                # Show top 5 presets
                if total > 0:
                    print("   Top presets:")
                    for i, preset in enumerate(self.inventory['factory_packs'][pack_name]['presets'][:5], 1):
                        print(f"     {i}. {preset['name']} ({preset['category']})")
                    if total > 5:
                        print(f"     ... and {total - 5} more")
    
    def inventory_user_presets(self):
        """Inventory user-created presets."""
        user_presets_path = self.base_path / "User Library" / "Presets"
        if not user_presets_path.exists():
            return
        
        print("\n" + "=" * 80)
        print("INVENTORYING USER PRESETS")
        print("=" * 80)
        
        for category_dir in sorted(user_presets_path.iterdir()):
            if category_dir.is_dir():
                category = category_dir.name
                self.inventory['user_presets'][category] = []
                
                for preset_file in category_dir.rglob("*.adg"):
                    self.inventory['user_presets'][category].append({
                        'name': preset_file.stem,
                        'path': str(preset_file)
                    })
                
                count = len(self.inventory['user_presets'][category])
                if count > 0:
                    print(f"\n🎛️ {category}: {count} presets")
                    for preset in self.inventory['user_presets'][category]][:3]:
                        print(f"   - {preset['name']}")
    
    def inventory_samples(self):
        """Inventory available samples."""
        samples_paths = [
            self.base_path / "User Library" / "Samples",
            self.base_path / "User Library" / "Clips"
        ]
        
        print("\n" + "=" * 80)
        print("INVENTORYING SAMPLES")
        print("=" * 80)
        
        total_samples = 0
        for samples_path in samples_paths:
            if samples_path.exists():
                for sample_dir in samples_path.rglob(".*"):
                    pass  # Skip hidden files
                
                # Count audio files
                audio_extensions = ['.wav', '.aif', '.aiff', '.mp3', '.flac']
                for ext in audio_extensions:
                    audio_files = list(samples_path.rglob(f"*{ext}"))
                    total_samples += len(audio_files)
                
                if total_samples > 0:
                    print(f"\n🎵 {samples_path.name}: {total_samples} audio samples")
        
        self.inventory['samples']['total'] = total_samples
    
    def inventory_effects(self):
        """Inventory available effects."""
        effects_path = self.base_path / "User Library" / "Presets" / "Audio Effects"
        if not effects_path.exists():
            return
        
        print("\n" + "=" * 80)
        print("INVENTORYING EFFECT PRESETS")
        print("=" * 80)
        
        total_effects = 0
        for effect_type in sorted(effects_path.iterdir()):
            if effect_type.is_dir():
                effect_count = len(list(effect_type.rglob("*.adg")))
                total_effects += effect_count
                if effect_count > 0:
                    print(f"🔊 {effect_type.name}: {effect_count} presets")
        
        self.inventory['effects']['total'] = total_effects
    
    def categorize_for_reggae(self):
        """Categorize inventory for reggae production."""
        print("\n" + "=" * 80)
        print("REAGAE-READY INSTRUMENTS")
        print("=" * 80)
        
        reggae_ready = {
            'drums': [],
            'bass': [],
            'organ': [],
            'guitar': [],
            'piano': [],
            'percussion': [],
            'effects': []
        }
        
        # Drums for reggae
        drum_packs = ['Drum Essentials', 'Session Drums Club', 'Session Drums Studio', 'Latin Percussion']
        for pack_name in drum_packs:
            if pack_name in self.inventory['factory_packs']:
                presets = [p['name'] for p in self.inventory['factory_packs'][pack_name]['presets']]
                reggae_ready['drums'].extend([(p, pack_name) for p in presets])
        
        # Organ for reggae  
        if 'Electric Keyboards' in self.inventory['factory_packs']:
            presets = [p['name'] for p in self.inventory['factory_packs']['Electric Keyboards']['presets'])
            organ_presets = [p for p in presets if 'Organ' in p or 'Tonewheel' in p]
            reggae_ready['organ'] = organ_presets
        
        # Guitar for reggae
        if 'Guitar and Bass' in self.inventory['factory_packs']:
            presets = [p for p in self.inventory['factory_packs']['Guitar and Bass']['presets']]
            guitar_presets = [p['name'] for p in presets if 'Guitar' in p['name']]
            reggae_ready['guitar'] = guitar_presets
        
        # Piano for reggae
        if 'Electric Keyboards' in self.inventory['factory_packs']:
            presets = [p['name'] for p in self.inventory['factory_packs']['Electric Keyboards']['presets']]
            piano_presets = [p for p in presets if 'Piano' in p or 'Wurly' in p or 'Suitcase' in p]
            reggae_ready['piano'] = piano_presets
        
        # Print results
        print(f"\n🥁 DRUMS: {len(reggae_ready['drums'])} presets")
        if reggae_ready['drums']:
            print("   Highlights:", ', '.join([p[0] for p in reggae_ready['drums'][:5]]))
        
        print(f"\n🎹 ORGAN: {len(reggae_ready['organ'])} presets")
        if reggae_ready['organ']:
            print("   Highlights:", ', '.join(reggae_ready['organ'][:5]))
        
        print(f"\n🎸 GUITAR: {len(reggae_ready['guitar'])} presets")
        if reggae_ready['guitar']:
            print("   Highlights:", ', '.join(reggae
