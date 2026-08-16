#!/usr/bin/env python3
"""
Genre-Specific Mix Generator

Creates mixes tailored to specific genres:
- Dub
- Hip-Hop
- Techno
- House
- Drum & Bass
- Ambient

Usage:
    python scripts/genre_mix_generator.py dub
    python scripts/genre_mix_generator.py hiphop
    python scripts/genre_mix_generator.py techno
"""

class AbletonClient:
    """Enhanced client with tracking capabilities."""
    
    def __init__(self, host="localhost", port=9877):
        self.host = host
        self.port = port
        self.socket = None
        self.scenes_cache = None
        self.tracks_cache = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def send(self, cmd_type, params=None):
        if not self.socket:
            if not self.connect():
                return None
        
        if params is None:
            params = {}
        
        message = {"type": cmd_type, "params": params}
        
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
            response = self.socket.recv(4096).decode()
            if response:
                return json.loads(response)
            return {"status": "ok"}
        except Exception as e:
            print(f"[ERROR] Command {cmd_type} failed: {e}")
            self.socket = None
            return {"status": "error", "message": str(e)}
    
    def get_scenes(self):
        """Get and cache scenes."""
        if self.scenes_cache is None:
            result = self.send("get_all_scenes")
            if result and "result" in result and "scenes" in result["result"]:
                self.scenes_cache = result["result"]["scenes"]
        return self.scenes_cache or []
    
    def get_tracks(self):
        """Get and cache tracks."""
        if self.tracks_cache is None:
            result = self.send("get_all_tracks")
            if result and "result" in result and "tracks" in result["result"]:
                self.tracks_cache = result["result"]["tracks"]
        return self.tracks_cache or []
    
    def close(self):
        try:
            if self.socket:
                self.socket.close()
        except:
            pass



GENRE_CONFIGS = {
    "dub": {
        "name": "Dub",
        "bpm_range": (60, 95),
        "base_bpm": 75,
        "structure": [
            {"type": "intro", "bars": 32, "energy": 0.2, "dub_pointers": True, "effects": "heavy"},
            {"type": "verse", "bars": 32, "energy": 0.5, "bassline": "steppers", "dub_pointers": True},
            {"type": "build", "bars": 16, "energy": 0.7, "filter_sweep": True},
            {"type": "drop", "bars": 32, "energy": 0.85, "echo": "maximum", "reverb": "hall"},
            {"type": "verse", "bars": 32, "energy": 0.5, "bassline": "oneshot", "dub_pointers": True},
            {"type": "breakdown", "bars": 32, "energy": 0.3, "effects": "space"},
            {"type": "build", "bars": 16, "energy": 0.75, "filter_sweep": True},
            {"type": "drop", "bars": 48, "energy": 0.9, "echo": "maximum", "filter": "resonant"},
            {"type": "outro", "bars": 32, "energy": 0.25, "filter_sweep": "down"},
        ],
        "processing": {
            "sub_bass_boost": 12,
            "echo_feedback": 0.9,
            "reverb_decay": 4.0,
            "filter_resonance": 0.8,
            "stereo_width": 0.7
        },
        "description": "Classic dub with heavy echo, reverb, and filter sweeps"
    },
    
    "hiphop": {
        "name": "Hip-Hop",
        "bpm_range": (70, 100),
        "base_bpm": 85,
        "structure": [
            {"type": "intro", "bars": 16, "energy": 0.3, "drums": False},
            {"type": "verse", "bars": 16, "energy": 0.6, "drums": True, "kick_pattern": "loose"},
            {"type": "hook", "bars": 8, "energy": 0.75, "vocals": True, "snare_roll": True},
            {"type": "verse", "bars": 16, "energy": 0.65, "kick_pattern": "loose"},
            {"type": "hook", "bars": 8, "energy": 0.8, "vocals": True, "doubled": True},
            {"type": "bridge", "bars": 8, "energy": 0.4, "halftime": True},
            {"type": "hook", "bars": 16, "energy": 0.85, "vocals": True, "adlibs": True},
            {"type": "outro", "bars": 16, "energy": 0.35, "fade": True},
        ],
        "processing": {
            "sub_bass_boost": 8,
            "compression": 0.8,
            "saturation": 0.6,
            "stereo_width": 0.6,
            "sidechain": 0.3
        },
        "description": "Old school hip-hop with punchy drums and bass"
    },
    
    "techno": {
        "name": "Techno",
        "bpm_range": (120, 135),
        "base_bpm": 128,
        "structure": [
            {"type": "intro", "bars": 32, "energy": 0.3, "hourglass": True, "filter": "closed"},
            {"type": "groove", "bars": 32, "energy": 0.7, "kick": "four_on_floor", "bass": "rolling"},
            {"type": "build", "bars": 16, "energy": 0.85, "risers": True, "white_noise": True},
            {"type": "drop", "bars": 32, "energy": 0.95, "kick": "pounding", "hi_hat": "fast"},
            {"type": "groove", "bars": 32, "energy": 0.75, "kick": "four_on_floor", "variation": True},
            {"type": "breakdown", "bars": 16, "energy": 0.2, "atmospheric": True},
            {"type": "build", "bars": 24, "energy": 0.9, "risers": True, "snare_rolls": True},
            {"type": "drop", "bars": 48, "energy": 1.0, "kick": "pounding", "hydraulic": True},
            {"type": "outro", "bars": 32, "energy": 0.4, "filter": "sweep_down"},
        ],
        "processing": {
            "sub_bass_boost": 6,
            "compression": 0.7,
            "saturation": 0.7,
            "stereo_width": 0.8,
            "sidechain": 0.0
        },
        "description": "Hard-hitting techno with pounding kicks and atmospheric breaks"
    },
    
    "house": {
        "name": "House",
        "bpm_range": (115, 130),
        "base_bpm": 120,
        "structure": [
            {"type": "intro", "bars": 16, "energy": 0.3, "four_on_floor": False},
            {"type": "groove", "bars": 16, "energy": 0.7, "four_on_floor": True, "bass": "bouncy"},
            {"type": "build", "bars": 8, "energy": 0.8, "risers": True, "clap_filters": True},
            {"type": "drop", "bars": 16, "energy": 0.9, "four_on_floor": True, "organ": True},
            {"type": "groove", "bars": 16, "energy": 0.75, "variation": True},
            {"type": "break", "bars": 8, "energy": 0.3, "reprise": True},
            {"type": "build", "bars": 8, "energy": 0.85, "risers": True},
            {"type": "drop", "bars": 32, "energy": 0.95, "piano": True, " vocals": False},
            {"type": "groove", "bars": 16, "energy": 0.8, "four_on_floor": True, "disco": True},
            {"type": "outro", "bars": 16, "energy": 0.35, "filter_sweep": True},
        ],
        "processing": {
            "sub_bass_boost": 5,
            "compression": 0.6,
            "saturation": 0.5,
            "stereo_width": 0.7,
            "sidechain": 0.4
        },
        "description": "Groovy house music with four-on-the-floor kicks and soulful elements"
    },
    
    "dnb": {
        "name": "Drum & Bass",
        "bpm_range": (160, 180),
        "base_bpm": 174,
        "structure": [
            {"type": "intro", "bars": 16, "energy": 0.3, "amen": False, "sub_bass": True},
            {"type": "verse", "bars": 16, "energy": 0.7, "amen": True, "breakbeat": "original"},
            {"type": "build", "bars": 8, "energy": 0.8, "amen": True, "breakbeat": "half_time"},
            {"type": "drop", "bars": 32, "energy": 0.95, "amen": True, "breakbeat": "full", "bass": "wobble"},
            {"type": "verse", "bars": 16, "energy": 0.75, "amen": True, "breakbeat": "variation"},
            {"type": "breakdown", "bars": 16, "energy": 0.4, "amen": False, "atmospheric": True},
            {"type": "build", "bars": 8, "energy": 0.85, "amen": True, "breakbeat": "build_up"},
            {"type": "drop", "bars": 48, "energy": 1.0, "amen": True, "breakbeat": "full", "rollers": True},
            {"type": "outro", "bars": 16, "energy": 0.4, "amen": True, "breakbeat": "exit"},
        ],
        "processing": {
            "sub_bass_boost": 4,
            "compression": 0.9,
            "saturation": 0.8,
            "stereo_width": 0.5,
            "sidechain": 0.0
        },
        "description": "High-energy drum & bass with breakbeats and wobble bass"
    },
    
    "ambient": {
        "name": "Ambient",
        "bpm_range": (50, 80),
        "base_bpm": 60,
        "structure": [
            {"type": "intro", "bars": 64, "energy": 0.1, "texture": "pad", "reverb": "infinite"},
            {"type": "evolve", "bars": 64, "energy": 0.2, "texture": "pad", "movement": "slow"},
            {"type": "build", "bars": 32, "energy": 0.35, "texture": "synth", "automation": "filter"},
            {"type": "peak", "bars": 32, "energy": 0.5, "texture": "full", "reverb": "cathedral"},
            {"type": "evolve", "bars": 64, "energy": 0.25, "texture": "pad", "movement": "subtle"},
            {"type": "texture", "bars": 48, "energy": 0.3, "texture": "granular", "space": True},
            {"type": "build", "bars": 32, "energy": 0.4, "texture": "synth", "automation": "volume"},
            {"type": "peak", "bars": 64, "energy": 0.6, "texture": "lush", "reverb": "eternal"},
            {"type": "outro", "bars": 64, "energy": 0.15, "texture": "fading", "reverb": "eternal"},
        ],
        "processing": {
            "sub_bass_boost": 2,
            "compression": 0.1,
            "saturation": 0.1,
            "stereo_width": 1.0,
            "sidechain": 0.0
        },
        "description": "Ethereal ambient with infinite reverb and slow evolution"
    }
}


class GenreMixGenerator:
    """Generates genre-specific mixes."""
    
    SCENE_APPROXIMATION = {
        "dub": [0, 1, 2, 3, 4],       # 5 scenes: intro, verse, build, drop, breakdown
        "hiphop": [0, 1, 2, 3, 4, 5],  # 6 scenes: intro, verse, hook, bridge, outro
        "techno": [0, 1, 2, 3, 4],     # 5 scenes: intro, groove, build, drop, breakdown
        "house": [0, 1, 2, 3, 4, 5],   # 6 scenes: intro, groove, build, drop, break, outro
        "dnb": [0, 1, 2, 3, 4, 5],     # 6 scenes: intro, verse, build, drop, breakdown, outro
        "ambient": [0, 1, 2, 3, 4],    # 5 scenes: various textures
    }
    
    def __init__(self, client, genre: str):
        self.client = client
        self.genre = genre.lower()
        self.config = GENRE_CONFIGS.get(self.genre, GENRE_CONFIGS["dub"])
        self.base_bpm = self.config["base_bpm"]
    
    def convert_to_structure(self) -> List[Dict[str, Any]]:
        """Convert genre config to executable structure."""
        structure = []
        start_bar = 0
        current_scene = 0
        
        for section in self.config["structure"]:
            # Map section type to scene
            if self.genre == "dub":
                type_map = {"intro": 0, "verse": 1, "build": 2, "drop": 3, "breakdown": 4, "outro": 0}
            elif self.genre == "hiphop":
                type_map = {"intro": 0, "verse": 1, "hook": 2, "bridge": 3, "outro": 0}
            elif self.genre == "techno":
                type_map = {"intro": 0, "groove": 1, "build": 2, "drop": 3, "breakdown": 4, "outro": 0}
            elif self.genre == "house":
                type_map = {"intro": 0, "groove": 1, "build": 2, "drop": 3, "break": 4, "outro": 0}
            elif self.genre == "dnb":
                type_map = {"intro": 0, "verse": 1, "build": 2, "drop": 3, "breakdown": 4, "outro": 0}
            elif self.genre == "ambient":
                type_map = {"intro": 0, "evolve": 1, "build": 2, "peak": 3, "texture": 4, "outro": 0}
            else:
                type_map = {}
            
            scene_idx = type_map.get(section["type"], current_scene)
            current_scene = scene_idx
            
            # Calculate BPM
            bpm = self.base_bpm
            if "bpm" in section:
                bpm = section["bpm"]
            
            section_data = {
                "name": self.generate_name(section["type"]),
                "section_type": section["type"],
                "scene_index": scene_idx,
                "bars": section["bars"],
                "bpm": bpm,
                "energy": section.get("energy", 0.5),
                "start_bar": start_bar
            }
            
            structure.append(section_data)
            start_bar += section["bars"]
        
        return structure
    
    def generate_name(self, section_type: str) -> str:
        """Generate a name for the section based on genre."""
        names = {
            "dub": {
                "intro": ["Dub Space", "Echo Void", "Filter Dawn", "Reverb Beginnings"],
                "verse": ["Bassline Flow", "Dub Steppers", "Groove Foundation", "Root Movement"],
                "build": ["Filter Rise", "Echo Tension", "Resonance Build", "Feedback Ascent"],
                "drop": ["Dub Bomb", "Filter Sweep", "Echo Explosion", "Reverb Apocalypse"],
                "breakdown": ["Echo Chamber", "Space Out", "Dub Hole", "Silence"],
                "outro": ["Dub Fade", "Echo Exit", "Filter Down", "Closing Void"]
            },
            "hiphop": {
                "intro": ["Beat Intro", "Sample Start", "Vinyl Crackle", "Scratch In"],
                "verse": ["Flow Verse", "Rhyme Time", "Bars", "Story"],
                "hook": ["Chorus", "Refrain", "Sing Along", "Catchy"],
                "bridge": ["Break", "Interlude", "Change Up", "Middle 8"],
                "outro": ["Fade Out", "Scratch Out", "Record Spin", "End"]
            },
            "techno": {
                "intro": ["Hourglass Start", "Synth Rise", "Kick Introduce", "Bass Entry"],
                "groove": ["Four on Floor", "Kick Pattern", "Bassline", "Rhythm"],
                "build": ["Riser", "White Noise", "Filter Sweep", "Tension"],
                "drop": ["Kick Drop", "Bass Explosion", "Synth Rush", "Energy Peak"],
                "breakdown": ["Atmosphere", "Pad Section", "Breathing Space", "Pause"],
                "outro": ["Filter Fade", "Kick Exit", "Synth Outro", "End Sweep"]
            },
            "house": {
                "intro": ["Groove Start", "Piano Intro", "Disco Begin", "Four Start"],
                "groove": ["Disco Groove", "House Beat", "Four on Floor", "Bouncy Bass"],
                "build": ["Clap Build", "Riser", "Filter Up", "Tension"],
                "drop": ["Piano Drop", "Organ Rush", "Synth Hit", "Energy"] ,
                "break": ["Reprise", "Quiet Section", "Minimal", "Space"],
                "outro": ["Filter Out", "Fade", "Disco Exit", "End Groove"]
            },
            "dnb": {
                "intro": ["Amen Start", "Sub Intro", "Break Begin", "DnB Entry"],
                "verse": ["Breakbeat", "Amen Flow", "Jungle Verse", "Roller"],
                "build": ["Half-Time Build", "Amen Tension", "Fill Rolls", "Riser"],
                "drop": ["Amen Smash", "Wobble Bass", "Full Break", "Jungle Drop"],
                "breakdown": ["Atmosphere", "Pad Section", "Space", "Gap"],
                "outro": ["Amen Out", "Break Exit", "Fade", "End"]
            },
            "ambient": {
                "intro": ["Eternal Start", "Pad Dawn", "Texture Rise", "Space Opening"],
                "evolve": ["Slow Evolution", "Texture Change", "Subtle Movement", "Drone Shift"],
                "build": ["Filter Automation", "Volume Swell", "Texture Build", "Rise"],
                "peak": ["Lush Peak", "Full Texture", "Pad Climax", "Energy Maximum"],
                "texture": ["Granular Section", "Glitch Texture", "Noise Pad", "Sound Design"],
                "outro": ["Eternal Fade", "Infinite Reverb", "Space Exit", "Endless"]
            }
        }
        
        import random
        genre_names = names.get(self.genre, names["dub"])
        return random.choice(genre_names.get(section_type, [f"{section_type.capitalize()}"]))
    
    def create_genre_mix(self):
        """Create a genre-specific mix."""
        print("\n" + "=" * 70)
        print(f"{self.config['name'].upper()} MIX GENERATOR")
        print("=" * 70)
        print(f"\n[GENRE] {self.config['name']}")
        print(f"[DESCRIPTION] {self.config['description']}")
        print(f"[BPM] {self.config['bpm_range'][0]}-{self.config['bpm_range'][1]}")
        
        # Convert config to structure
        print("\n[STEP 1] Converting configuration...")
        structure = self.convert_to_structure()
        
        total_bars = sum(s["bars"] for s in structure)
        duration = total_bars * 60 / self.base_bpm
        
        print(f"[STRUCTURE] {len(structure)} sections, {total_bars} bars")
        print(f"[DURATION] {duration:.1f} minutes")
        
        # Display structure
        print("\n[BLUEPRINT]")
        print("-" * 70)
        print(f"{'#':<3} {'Bars':<8} {'Type':<12} {'Scene':<7} {'Name':<25} {'BPM':<6} {'Energy'}")
        print("-" * 70)
        
        for i, s in enumerate(structure):
            print(f"{i+1:<3} {s['start_bar']:<3}-{s['start_bar']+s['bars']-1:<3} {s['section_type']:<12} {s['scene_index']:<7} {s['name']:<25} {s['bpm']:<6.0f} {s['energy']*10:.1f}/10")
        
        print("-" * 70)
        
        # Setup Ableton
        print("\n[STEP 2] Setting up Ableton...")
        self.client.send("stop_playback")
        self.client.send("stop_recording")
        self.client.send("set_tempo", {"bpm": self.base_bpm})
        self.client.send("set_playhead_position", {"bar": 0, "beat": 0})
        print("[OK]")
        
        # Create locators
        print("\n[STEP 3] Creating locators...")
        for section in structure:
            self.client.send("create_locator", {
                "name": f"{section['name']}",
                "bar": section["start_bar"]
            })
        
        # End locator
        end_bar = structure[-1]["start_bar"] + structure[-1]["bars"]
        self.client.send("create_locator", {"name": "Mix_End", "bar": end_bar})
        print(f"[OK] Created {len(structure) + 1} locators")
        
        # Apply genre-specific processing
        print("\n[STEP 4] Applying genre-specific processing...")
        self.apply_genre_processing()
        
        # Summary
        print("\n" + "=" * 70)
        print("{GENRE} MIX COMPLETE!".format(GENRE=self.config['name'].upper()))
        print("=" * 70)
        
        # Genre-specific tips
        print(f"\n[GENRE TIPS]")
        tips = {
            "dub": [
                "Use heavy delay and reverb on sends",
                "Automate filter cutoff for dub siren effect",
                "Keep basslines simple but deep",
                "Use spring reverb for authentic dub sound"
            ],
            "hiphop": [
                "Layer kick drums for punch",
                "Add vinyl crackle and samples",
                "Use sidechain compression for that pumping effect",
                "Keep hi-hats swingy and loose"
            ],
            "techno": [
                "Use 4/4 kick pattern consistently",
                "Layer percussion for complexity",
                "Automate filter cutoff during builds",
                "Keep bassline simple but powerful"
            ],
            "house": [
                "Use disco-style basslines",
                "Add piano chords for groove",
                "Use clap on 2nd and 4th beat",
                "Keep hi-hats shuffle-style"
            ],
            "dnb": [
                "Use Amen break or variations",
                "Keep bassline wobbly or reese",
                "Use fast hi-hat rolls",
                "Automate filter during drops"
            ],
            "ambient": [
                "Use long reverb tails (4+ seconds)",
                "Automate filter very slowly",
                "Keep sounds evolving over time",
                "Use minimal rhythmic elements"
            ]
        }
        
        for tip in tips.get(self.genre, []):
            print(f"  * {tip}")
        
        print(f"\n[NEXT STEPS]")
        print(f"  1. Open Ableton and review the locators")
        print(f"  2. Arm all tracks")
        print(f"  3. Start recording and trigger scenes following the blueprint")
        print(f"  4. Add effects specific to {self.config['name'].lower()} genre")
        print(f"  5. Export and enjoy!")
        
        print("\n" + "=" * 70)
        
        return {
            "status": "success",
            "genre": self.config["name"],
            "structure": structure,
            "base_bpm": self.base_bpm,
            "total_bars": total_bars,
            "duration_minutes": duration,
            "processing": self.config["processing"]
        }
    
    def apply_genre_processing(self):
        """Apply genre-specific processing to tracks."""
        processing = self.config["processing"]
        
        print(f"[INFO] Applying {self.config['name']} processing...")
        
        # Apply volume and pan based on genre
        track_configs = {
            "dub": [
                {"track": 0, "volume": -6.0, "pan": 0.0, "name": " Bass Sub"},
                {"track": 1, "volume": -3.0, "pan": 0.0, "name": "Kick"},
                {"track": 2, "volume": -4.0, "pan": -0.2, "name": "Snare"},
                {"track": 3, "volume": -8.0, "pan": 0.2, "name": "Hi-Hats"},
            ],
            "hiphop": [
                {"track": 0, "volume": -5.0, "pan": 0.0, "name": "Kick"},
                {"track": 1, "volume": -6.0, "pan": 0.0, "name": "Bass"},
                {"track": 2, "volume": -4.0, "pan": -0.2, "name": "Snare"},
                {"track": 3, "volume": -7.0, "pan": 0.2, "name": "Hi-Hats"},
            ],
            "techno": [
                {"track": 0, "volume": -3.0, "pan": 0.0, "name": "Kick"},
                {"track": 1, "volume": -5.0, "pan": 0.0, "name": "Bass"},
                {"track": 2, "volume": -4.0, "pan": -0.15, "name": "Clap"},
                {"track": 3, "volume": -6.0, "pan": 0.15, "name": "Hi-Hats"},
            ],
            "house": [
                {"track": 0, "volume": -4.0, "pan": 0.0, "name": "Kick"},
                {"track": 1, "volume": -5.0, "pan": 0.0, "name": "Bass"},
                {"track": 2, "volume": -3.0, "pan": -0.2, "name": "Clap/Snare"},
                {"track": 3, "volume": -6.0, "pan": 0.2, "name": "Hi-Hats"},
            ],
            "dnb": [
                {"track": 0, "volume": -4.0, "pan": 0.0, "name": "Kick"},
                {"track": 1, "volume": -3.0, "pan": 0.0, "name": "Amen/Loop"},
                {"track": 2, "volume": -5.0, "pan": 0.0, "name": "Bass"},
                {"track": 3, "volume": -6.0, "pan": 0.0, "name": "Percussion"},
            ],
            "ambient": [
                {"track": 0, "volume": -12.0, "pan": -0.3, "name": "Pad Left"},
                {"track": 1, "volume": -12.0, "pan": 0.3, "name": "Pad Right"},
                {"track": 2, "volume": -9.0, "pan": 0.0, "name": "Texture"},
                {"track": 3, "volume": -15.0, "pan": 0.0, "name": "Ambient FX"},
            ]
        }
        
        # Get appropriate track config
        genre_tracks = track_configs.get(self.genre, track_configs["dub"])
        
        for config in genre_tracks[:4]:  # First 4 tracks
            self.client.send("set_track_volume", {
                "track_index": config["track"],
                "volume_db": config["volume"] + processing.get("sub_bass_boost", 0) * -0.5
            })
            self.client.send("set_track_pan", {
                "track_index": config["track"],
                "pan": config["pan"]
            })
            print(f"[OK] Track {config['track']} ({config['name']}): {config['volume']}dB, pan {config['pan']}")
        
        print(f"[OK] Genre processing applied")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/genre_mix_generator.py <genre>")
        print("\nAvailable genres:")
        for genre_id in GENRE_CONFIGS:
            config = GENRE_CONFIGS[genre_id]
            print(f"  {genre_id:10s} - {config['description']}")
        return None
    
    genre = sys.argv[1].lower()
    
    if genre not in GENRE_CONFIGS:
        print(f"Unknown genre: {genre}")
        print(f"Available: {', '.join(GENRE_CONFIGS.keys())}")
        return None
    
    print(f"\nCreating {GENRE_CONFIGS[genre]['name']} mix...")
    
    # Create client
    client = AbletonClient()
    
    if not client.connect():
        print("\n[ERROR] Could not connect to Remote Script")
        return None
    
    print("[OK] Connected to Remote Script")
    
    # Create generator
    generator = GenreMixGenerator(client, genre)
    
    try:
        result = generator.create_genre_mix()
        return result
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        client.close()


if __name__ == "__main__":
    result = main()
    
    if result and result.get("status") == "success":
        import time as t
        timestamp = t.strftime("%Y%m%d_%H%M%S")
        filename = f"genre_mix_{result['genre'].lower()}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n[INFO] Mix saved to: {filename}")
