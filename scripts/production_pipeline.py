#!/usr/bin/env python3
"""
PRODUCTION PIPELINE - Complete Mix Production & Distribution

A reusable pipeline for:
1. Creating mixes (any genre or custom)
2. Optional real-time capture to arrangement
3. Exporting to WAV/MP3
4. Optional video creation with waveform visualization
5. Optional YouTube upload (via OpenMusic-style integration)

Usage:
    # Basic: Create + Export to MP3
    python scripts/production_pipeline.py dub_techno --mp3
    
    # Full: Create + Capture + MP3 + Video + YouTube
    python scripts/production_pipeline.py dub_techno --capture --mp3 --video --youtube
    
    # Custom genre
    python scripts/production_pipeline.py custom --genre hiphop --bpm 90 --mp3
    
    # With title and artist
    python scripts/production_pipeline.py dub_techno --mp3 --title "My Dub Techno" --artist "DJ Name"
"""

import json
import socket
import os
import sys
import subprocess
import argparse
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

# YouTube API Configuration (optional)
YOUTUBE_API_CONFIG = {
    "enabled": False,
    "client_secrets_file": "youtube_client_secrets.json",
    "scope": ["https://www.googleapis.com/auth/youtube.upload"],
    "privacy_status": "public"  # or "private", "unlisted"
}

# Video settings
VIDEO_SETTINGS = {
    "resolution": "1280x720",
    "fps": 30,
    "duration": None,  # Auto from audio
    "waveform_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFBE0B"],
    "background_color": "#1a1a2e",
    "background_image": None,  # Optional path to image
    "title_font": "Arial Bold",
    "title_color": "#FFFFFF",
    "title_size": 48
}

# Audio settings
AUDIO_SETTINGS = {
    "format": "wav",
    "bit_depth": 24,
    "sample_rate": 44100,
    "normalize": False,
    "mp3_bitrate": "320k",
    "mp3_quality": 0  # LAME quality: 0=highest, 9=lowest
}

# File paths
BASE_DIR = Path(__file__).parent.parent
AUDIO_EXPORT_DIR = BASE_DIR / "exports" / "audio"
VIDEO_EXPORT_DIR = BASE_DIR / "exports" / "video"
UPLOADS_DIR = BASE_DIR / "exports" / "uploads"

# Create directories if they don't exist
for d in [AUDIO_EXPORT_DIR, VIDEO_EXPORT_DIR, UPLOADS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ============================================================================
# ENUMS & MODELS
# ============================================================================

class Genre(Enum):
    DUB = "dub"
    TECHNO = "techno"
    HIPHOP = "hiphop"
    HOUSE = "house"
    DNB = "dnb"
    AMBIENT = "ambient"
    DUB_TECHNO = "dub_techno"
    CUSTOM = "custom"


class Format(Enum):
    WAV = "wav"
    MP3 = "mp3"
    BOTH = "both"


@dataclass
class TrackConfig:
    index: int
    name: str
    type: str
    volume_db: float
    pan: float
    effects: List[str] = field(default_factory=list)


@dataclass
class Section:
    name: str
    type: str
    bars: int
    bpm: float
    energy: float
    scene_index: int
    start_bar: int = 0


@dataclass
class MixProject:
    name: str
    genre: str
    bpm: float
    sections: List[Section] = field(default_factory=list)
    tracks: List[TrackConfig] = field(default_factory=list)
    duration_seconds: float = 0.0
    duration_minutes: float = 0.0
    total_bars: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    output_dir: Path = AUDIO_EXPORT_DIR
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "genre": self.genre,
            "bpm": self.bpm,
            "sections": [s.__dict__ for s in self.sections],
            "tracks": [t.__dict__ for t in self.tracks],
            "duration_seconds": self.duration_seconds,
            "duration_minutes": self.duration_minutes,
            "total_bars": self.total_bars,
            "timestamp": self.timestamp
        }


@dataclass
class PipelineResult:
    success: bool
    project: Optional[MixProject] = None
    wav_file: Optional[Path] = None
    mp3_file: Optional[Path] = None
    video_file: Optional[Path] = None
    youtube_url: Optional[str] = None
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ============================================================================
# ABLETON CLIENT
# ============================================================================

class AbletonClient:
    """Enhanced client with retry logic."""
    
    def __init__(self, host: str = "localhost", port: int = 9877):
        self.host = host
        self.port = port
        self.socket = None
        self.last_command_time = 0
        self.command_count = 0
    
    def connect(self, max_retries: int = 3) -> bool:
        for i in range(max_retries):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(30)
                self.socket.connect((self.host, self.port))
                return True
            except Exception as e:
                print(f"[CONNECT] Attempt {i+1}/{max_retries}: {e}")
                if i < max_retries - 1:
                    time.sleep(2)
        return False
    
    def send(self, cmd_type: str, params: Optional[Dict] = None, retry: bool = True) -> Optional[Dict]:
        if not self.socket and not self.connect():
            return None
        
        message = {"type": cmd_type, "params": params or {}}
        
        try:
            self.socket.sendall(json.dumps(message).encode() + b"\n")
            response = self.socket.recv(4096).decode()
            self.command_count += 1
            self.last_command_time = time.time()
            return json.loads(response) if response else {"status": "ok"}
        except Exception as e:
            self.socket = None
            if retry:
                return self.send(cmd_type, params, retry=False)
            return {"status": "error", "message": str(e)}
    
    def close(self):
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
    
    def get_tracks(self) -> List[Dict]:
        result = self.send("get_all_tracks")
        return result.get("result", {}).get("tracks", []) if result else []
    
    def get_scenes(self) -> List[Dict]:
        result = self.send("get_all_scenes")
        return result.get("result", {}).get("scenes", []) if result else []


# ============================================================================
# MIX GENERATOR FACTORY
# ============================================================================

class MixGenerator:
    """Factory for generating different mix types."""
    
    GENRE_CONFIGS = {
        "dub_techno": {
            "name": "Dub Techno",
            "bpm": 125,
            "sections": [
                {"name": "Dub Space Intro", "type": "intro", "bars": 32, "energy": 0.2, "scene": 0},
                {"name": "Dub Steppers", "type": "groove", "bars": 32, "energy": 0.5, "scene": 1},
                {"name": "Echo Build", "type": "build", "bars": 16, "energy": 0.7, "scene": 2},
                {"name": "Dub Bomb", "type": "drop", "bars": 32, "energy": 0.9, "scene": 3},
                {"name": "Deep Dub Bass", "type": "groove", "bars": 32, "energy": 0.6, "scene": 1},
                {"name": "Atmospheric Break", "type": "breakdown", "bars": 32, "energy": 0.3, "scene": 4},
                {"name": "Reverb Rise", "type": "build", "bars": 16, "energy": 0.8, "scene": 2},
                {"name": "Filter Sweep Drop", "type": "drop", "bars": 48, "energy": 0.95, "scene": 3},
                {"name": "Dub Techno Outro", "type": "outro", "bars": 32, "energy": 0.2, "scene": 0},
            ],
            "tracks": [
                {"name": "Sub Bass (Dub)", "type": "bass", "volume": -4.0, "pan": 0.0},
                {"name": "Kick (Techno)", "type": "drum", "volume": -2.0, "pan": 0.0},
                {"name": "Snare/Clap", "type": "drum", "volume": -5.0, "pan": 0.15},
                {"name": "Hi-Hats", "type": "drum", "volume": -8.0, "pan": -0.15},
                {"name": "Atmospheric Pads", "type": "melody", "volume": -12.0, "pan": 0.3},
                {"name": "Dub Echo FX", "type": "fx", "volume": -15.0, "pan": 0.5},
                {"name": "Filter Sweep", "type": "fx", "volume": -12.0, "pan": 0.0},
                {"name": "White Noise", "type": "fx", "volume": -18.0, "pan": 0.0},
            ]
        },
        "dub": {
            "name": "Dub",
            "bpm": 75,
            "sections": [
                {"name": "Dub Space", "type": "intro", "bars": 32, "energy": 0.2, "scene": 0},
                {"name": "Steppers", "type": "verse", "bars": 32, "energy": 0.5, "scene": 1},
                {"name": "Filter Rise", "type": "build", "bars": 16, "energy": 0.7, "scene": 2},
                {"name": "Echo Explosion", "type": "drop", "bars": 32, "energy": 0.85, "scene": 3},
                {"name": "Root Movement", "type": "verse", "bars": 32, "energy": 0.5, "scene": 1},
                {"name": "Echo Chamber", "type": "breakdown", "bars": 32, "energy": 0.3, "scene": 4},
                {"name": "Feedback Ascent", "type": "build", "bars": 16, "energy": 0.75, "scene": 2},
                {"name": "Filter Sweep", "type": "drop", "bars": 48, "energy": 0.9, "scene": 3},
                {"name": "Echo Exit", "type": "outro", "bars": 32, "energy": 0.25, "scene": 0},
            ],
            "tracks": [
                {"name": "Sub Bass", "type": "bass", "volume": -6.0, "pan": 0.0},
                {"name": "Kick", "type": "drum", "volume": -3.0, "pan": 0.0},
                {"name": "Snare", "type": "drum", "volume": -4.0, "pan": -0.2},
                {"name": "Hi-Hats", "type": "drum", "volume": -8.0, "pan": 0.2},
                {"name": "Percussion", "type": "drum", "volume": -10.0, "pan": -0.3},
                {"name": "Echo FX", "type": "fx", "volume": -15.0, "pan": 0.4},
                {"name": "Filter Sweep", "type": "fx", "volume": -12.0, "pan": 0.0},
                {"name": "Reverb Pad", "type": "melody", "volume": -14.0, "pan": 0.25},
            ]
        },
        "techno": {
            "name": "Techno",
            "bpm": 128,
            "sections": [
                {"name": " Hourglass Start", "type": "intro", "bars": 32, "energy": 0.3, "scene": 0},
                {"name": "Four on Floor", "type": "groove", "bars": 32, "energy": 0.7, "scene": 1},
                {"name": "Riser", "type": "build", "bars": 16, "energy": 0.85, "scene": 2},
                {"name": "Kick Drop", "type": "drop", "bars": 32, "energy": 0.95, "scene": 3},
                {"name": "Rolling Bass", "type": "groove", "bars": 32, "energy": 0.75, "scene": 1},
                {"name": "Atmosphere", "type": "breakdown", "bars": 16, "energy": 0.2, "scene": 4},
                {"name": "Snare Rolls", "type": "build", "bars": 24, "energy": 0.9, "scene": 2},
                {"name": "Hydraulic Drop", "type": "drop", "bars": 48, "energy": 1.0, "scene": 3},
                {"name": "End Sweep", "type": "outro", "bars": 32, "energy": 0.4, "scene": 0},
            ],
            "tracks": [
                {"name": "Kick", "type": "drum", "volume": -3.0, "pan": 0.0},
                {"name": "Bass", "type": "bass", "volume": -5.0, "pan": 0.0},
                {"name": "Clap", "type": "drum", "volume": -4.0, "pan": -0.15},
                {"name": "Hi-Hats", "type": "drum", "volume": -6.0, "pan": 0.15},
                {"name": "Percussion", "type": "drum", "volume": -7.0, "pan": -0.2},
                {"name": "Synth", "type": "melody", "volume": -8.0, "pan": 0.25},
                {"name": "Atmo Pad", "type": "melody", "volume": -12.0, "pan": 0.0},
                {"name": "Noise FX", "type": "fx", "volume": -15.0, "pan": 0.0},
            ]
        },
        "reggae": {
            "name": "Reggae",
            "bpm": 80,
            "sections": [
                {"name": "One Drop Intro", "type": "intro", "bars": 32, "energy": 0.3, "scene": 0},
                {"name": "Rockers Groove", "type": "verse", "bars": 32, "energy": 0.5, "scene": 1},
                {"name": "Vocal Chant", "type": "chorus", "bars": 16, "energy": 0.6, "scene": 2},
                {"name": "Dub Section Drop", "type": "drop", "bars": 32, "energy": 0.8, "scene": 3},
                {"name": "Roots Rockers Verse", "type": "verse", "bars": 32, "energy": 0.55, "scene": 1},
                {"name": "Dub Echo Breakdown", "type": "breakdown", "bars": 32, "energy": 0.35, "scene": 4},
                {"name": "Lion of Judah", "type": "build", "bars": 16, "energy": 0.75, "scene": 2},
                {"name": "Babylon System Drop", "type": "drop", "bars": 48, "energy": 0.9, "scene": 3},
                {"name": "Natural Mystic Outro", "type": "outro", "bars": 32, "energy": 0.2, "scene": 0},
            ],
            "tracks": [
                {"name": "Reggae Kick (One Drop)", "type": "drum", "volume": -6.0, "pan": 0.0},
                {"name": "Sub Bass (Roots)", "type": "bass", "volume": -4.0, "pan": 0.0},
                {"name": "Snare (Backbeat)", "type": "drum", "volume": -5.0, "pan": -0.15},
                {"name": "Hi-Hats (Upbeat)", "type": "drum", "volume": -8.0, "pan": 0.2},
                {"name": "Guitar (Upstroke)", "type": "melody", "volume": -9.0, "pan": -0.25},
                {"name": "Keyboards/Organ", "type": "melody", "volume": -10.0, "pan": 0.3},
                {"name": "Dub Echo FX", "type": "fx", "volume": -15.0, "pan": 0.4},
                {"name": "Reverb/Spring", "type": "fx", "volume": -12.0, "pan": 0.0},
            ]
        }
    }
    
    def create_mix(self, genre: str, bpm: Optional[float] = None, name: Optional[str] = None) -> MixProject:
        """Create a mix project for the specified genre."""
        config = self.GENRE_CONFIGS.get(genre, self.GENRE_CONFIGS["dub_techno"])
        
        project_name = name or f"{config['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create sections with start bars
        sections = []
        start_bar = 0
        for i, section_data in enumerate(config["sections"]):
            section = Section(
                name=section_data["name"],
                type=section_data["type"],
                bars=section_data["bars"],
                bpm=bpm or config["bpm"],
                energy=section_data["energy"],
                scene_index=section_data["scene"],
                start_bar=start_bar
            )
            sections.append(section)
            start_bar += section_data["bars"]
        
        # Create tracks
        tracks = []
        for i, track_data in enumerate(config["tracks"]):
            track = TrackConfig(
                index=i,
                name=track_data["name"],
                type=track_data["type"],
                volume_db=track_data["volume"],
                pan=track_data["pan"]
            )
            tracks.append(track)
        
        # Calculate duration
        total_bars = sum(s.bars for s in sections)
        duration_seconds = (total_bars * 60) / (bpm or config["bpm"])
        duration_minutes = duration_seconds / 60
        
        return MixProject(
            name=project_name,
            genre=genre,
            bpm=bpm or config["bpm"],
            sections=sections,
            tracks=tracks,
            total_bars=total_bars,
            duration_seconds=duration_seconds,
            duration_minutes=duration_minutes
        )


# ============================================================================
# ABLETON INTEGRATION
# ============================================================================

class AbletonIntegration:
    """Handles Ableton configuration and capture."""
    
    def __init__(self, client: AbletonClient):
        self.client = client
    
    def setup_project(self, project: MixProject) -> bool:
        """Setup the mix structure in Ableton."""
        print("\n[ABLETON] Setting up project...")
        
        # Stop playback and recording
        self.client.send("stop_playback")
        self.client.send("stop_recording")
        
        # Set tempo
        self.client.send("set_tempo", {"bpm": project.bpm})
        self.client.send("set_playhead_position", {"bar": 0, "beat": 0})
        print(f"  [OK] Tempo: {project.bpm} BPM")
        
        # Create locators
        print("[ABLETON] Creating locators...")
        for section in project.sections:
            self.client.send("create_locator", {
                "name": section.name,
                "bar": section.start_bar
            })
            print(f"  [OK] {section.name} at bar {section.start_bar}")
        
        # End locator
        end_bar = project.sections[-1].start_bar + project.sections[-1].bars
        self.client.send("create_locator", {"name": f"{project.name}_End", "bar": end_bar})
        print(f"  [OK] End locator at bar {end_bar}")
        
        # Configure tracks
        print("[ABLETON] Configuring tracks...")
        for track in project.tracks:
            self.client.send("set_track_name", {"track_index": track.index, "name": track.name})
            self.client.send("set_track_volume", {"track_index": track.index, "volume_db": track.volume_db})
            self.client.send("set_track_pan", {"track_index": track.index, "pan": track.pan})
            print(f"  [OK] Track {track.index}: {track.name} at {track.volume_db}dB, pan {track.pan}")
        
        # Set master volume
        self.client.send("set_master_volume", {"volume_db": -6.0})
        print("  [OK] Master volume: -6.0dB")
        
        return True
    
    def apply_polish(self, project: MixProject) -> bool:
        """Apply polish suite to the project."""
        print("\n[ABLETON] Applying polish...")
        
        try:
            result = subprocess.run(
                ["python", "scripts/polish_suite.py", "full"],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(result.stdout)
            return result.returncode == 0
        except Exception as e:
            print(f"  [WARNING] Polish failed: {e}")
            return False


# ============================================================================
# AUDIO EXPORT
# ============================================================================

class AudioExporter:
    """Handles audio export and MP3 conversion."""
    
    @staticmethod
    def export_to_wav(project: MixProject, output_path: Optional[Path] = None) -> Path:
        """Export to WAV (manual - user must trigger in Ableton)."""
        wav_path = output_path or AUDIO_EXPORT_DIR / f"{project.name}.wav"
        
        print("\n[AUDIO] Export to WAV")
        print("  [!] Manual step required:")
        print("  1. In Ableton: File -> Export Audio/Video...")
        print("  2. Format: WAV")
        print(f"  3. Bit Depth: {AUDIO_SETTINGS['bit_depth']}")
        print(f"  4. Sample Rate: {AUDIO_SETTINGS['sample_rate']}")
        print("  5. Normalize: OFF")
        print(f"  6. Range: Use locators ({project.name} to {project.name}_End)")
        print(f"  7. Save as: {wav_path.name}")
        print("  8. Click Export")
        
        # Check if file exists (after user exports)
        if not wav_path.exists():
            print("\n  [WAITING] Please complete export in Ableton...")
            print("  Press Enter when done")
            input()
        
        if wav_path.exists():
            print(f"  [OK] WAV exported to: {wav_path}")
            return wav_path
        else:
            # Try default Ableton export location
            default_path = Path.home() / "Documents" / "Ableton" / "User Library" / "Exports" / f"{project.name}.wav"
            if default_path.exists():
                print(f"  [OK] Found WAV at: {default_path}")
                return default_path
            raise FileNotFoundError(f"WAV file not found at {wav_path} or default location")
    
    @staticmethod
    def convert_to_mp3(wav_path: Path, mp3_path: Optional[Path] = None, bitrate: str = "320k") -> Path:
        """Convert WAV to MP3 using FFmpeg."""
        mp3_path = mp3_path or wav_path.with_suffix(".mp3")
        
        print(f"\n[AUDIO] Converting to MP3...")
        print(f"  Input: {wav_path}")
        print(f"  Output: {mp3_path}")
        print(f"  Bitrate: {bitrate}")
        
        # Try FFmpeg first
        try:
            cmd = [
                "ffmpeg",
                "-i", str(wav_path),
                "-codec:a", "libmp3lame",
                "-qscale:a", str(AUDIO_SETTINGS["mp3_quality"]),
                "-b:a", bitrate,
                "-y",  # Overwrite without asking
                str(mp3_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and mp3_path.exists():
                size = mp3_path.stat().st_size
                print(f"  [OK] MP3 created: {mp3_path} ({size / 1024 / 1024:.1f} MB)")
                return mp3_path
        except Exception as e:
            print(f"  [WARNING] FFmpeg failed: {e}")
        
        # Try LAME
        try:
            cmd = [
                "lame",
                "-h",  # High quality
                "-b", bitrate,
                str(wav_path),
                str(mp3_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and mp3_path.exists():
                size = mp3_path.stat().st_size
                print(f"  [OK] MP3 created with LAME: {mp3_path} ({size / 1024 / 1024:.1f} MB)")
                return mp3_path
        except Exception as e:
            print(f"  [WARNING] LAME failed: {e}")
        
        # Try online conversion as last resort
        print("\n  [MANUAL] Please convert using online tool:")
        print(f"    1. Upload {wav_path.name} to online-audio-converter.com")
        print(f"    2. Select MP3, {bitrate}")
        print(f"    3. Download and save as {mp3_path.name}")
        print("    4. Press Enter when done")
        input()
        
        if mp3_path.exists():
            return mp3_path
        
        raise FileNotFoundError(f"MP3 conversion failed: {mp3_path}")


# ============================================================================
# VIDEO CREATION
# ============================================================================

class VideoCreator:
    """Creates video with waveform visualization."""
    
    @staticmethod
    def create_waveform_video(audio_path: Path, video_path: Optional[Path] = None, 
                              title: str = "", artist: str = "") -> Path:
        """Create a waveform video using FFmpeg."""
        video_path = video_path or VIDEO_EXPORT_DIR / f"{audio_path.stem}.mp4"
        
        print("\n[VIDEO] Creating waveform visualization...")
        print(f"  Audio: {audio_path}")
        print(f"  Output: {video_path}")
        
        # Generate waveform image
        waveform_png = video_path.with_suffix(".png")
        
        try:
            # Create waveform
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-filter_complex",
                "[0:a]showwavespic=s=1280x720:colors=#FF6B6B|#4ECDC4",
                "-frames:v", "1",
                "-y",
                str(waveform_png)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0 or not waveform_png.exists():
                raise Exception("Waveform generation failed")
        except Exception as e:
            print(f"  [WARNING] Waveform generation failed: {e}")
            # Use simpler waveform
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),
                "-filter_complex",
                f"[0:a]showwaves=s={VIDEO_SETTINGS['resolution']}:mode=cline",
                "-frames:v", "1",
                "-y",
                str(waveform_png)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise Exception("All waveform generation methods failed")
        
        # Create video from waveform
        try:
            # Get audio duration
            duration_cmd = [
                "ffprobe",
                "-i", str(audio_path),
                "-show_entries", "format=duration",
                "-v", "quiet",
                "-of", "csv=p=0"
            ]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, timeout=10)
            duration = float(duration_result.stdout.strip()) if duration_result.stdout.strip() else 600
            
            # Create video with zoom/pan effect on waveform
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", str(waveform_png),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "320k",
                "-filter_complex",
                f"[0:v]zoompan=z='min(zoom+0.0015,1.5)':d=1:i='if(eq(zoom,1.5),1,0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={VIDEO_SETTINGS['resolution']}:fps={VIDEO_SETTINGS['fps']},"
                f"drawtext=text='{title}':fontfile=/Windows/Fonts/arialbd.ttf:fontsize={VIDEO_SETTINGS['title_size']}:fontcolor={VIDEO_SETTINGS['title_color']}:x=(w-text_w)/2:y=h-(text_h*2),"
                f"drawtext=text='{artist}':fontfile=/Windows/Fonts/arial.ttf:fontsize=24:fontcolor={VIDEO_SETTINGS['title_color']}:x=(w-text_w)/2:y=h-text_h",
                "-t", str(duration),
                "-shortest",
                "-y",
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and video_path.exists():
                size = video_path.stat().st_size
                print(f"  [OK] Video created: {video_path} ({size / 1024 / 1024:.1f} MB)")
                
                # Cleanup
                waveform_png.unlink(missing_ok=True)
                
                return video_path
            else:
                raise Exception(f"Video creation failed: {result.stderr}")
                
        except Exception as e:
            print(f"  [WARNING] Video creation failed: {e}")
            print("  [FALLBACK] Creating static image video...")
            
            # Simple fallback: static waveform with audio
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", str(waveform_png),
                "-i", str(audio_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "320k",
                "-t", str(duration),
                "-shortest",
                "-y",
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and video_path.exists():
                print(f"  [OK] Fallback video created: {video_path}")
                return video_path
            
            raise Exception("All video creation methods failed")


# ============================================================================
# YOUTUBE UPLOADER (OpenMusic-inspired)
# ============================================================================

class YouTubeUploader:
    """Handles YouTube upload (OpenMusic-style)."""
    
    @staticmethod
    def upload(video_path: Path, title: str, description: str = "", 
               tags: List[str] = None, category_id: str = "10", 
               privacy: str = "public") -> Optional[str]:
        """
        Upload to YouTube.
        
        Requires:
        1. Google API credentials (client_secrets.json)
        2. OAuth consent screen configured
        3. YouTube Data API enabled
        
        Or use manual upload as fallback.
        """
        print("\n[YOUTUBE] Uploading video...")
        print(f"  Video: {video_path}")
        print(f"  Title: {title}")
        print(f"  Privacy: {privacy}")
        
        tags = tags or ["music", "dub", "techno", "mix", "ableton", "generated"]
        
        # Option 1: Try using youtube-upload (CLI tool)
        try:
            cmd = [
                "youtube-upload",
                "--title", title,
                "--description", description,
                "--tags", ",".join(tags),
                "--category", category_id,
                "--privacy", privacy,
                "--client-secrets", YOUTUBE_API_CONFIG["client_secrets_file"],
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Extract URL from output
                for line in result.stdout.split('\n'):
                    if "youtube.com/watch?v=" in line or "youtu.be/" in line:
                        url = line.strip()
                        print(f"  [OK] Uploaded: {url}")
                        return url
                print(f"  [OK] Uploaded (URL not found in output)")
                return None
        except Exception as e:
            print(f"  [WARNING] youtube-upload failed: {e}")
        
        # Option 2: Manual upload instructions
        print("\n  [MANUAL UPLOAD]")
        print(f"  1. Go to YouTube Studio (studio.youtube.com)")
        print(f"  2. Click CREATE -> Upload Video")
        print(f"  3. Select: {video_path}")
        print(f"  4. Title: {title}")
        print(f"  5. Description: {description or '(auto-generated mix)'}")
        print(f"  6. Tags: {', '.join(tags)}")
        print(f"  7. Visibility: {privacy.capitalize()}")
        print(f"  8. Category: Music")
        print(f"  9. Click Publish")
        print(f"  10. Copy video URL and paste below:")
        
        url = input("  URL: ").strip()
        if url:
            print(f"  [OK] Video URL: {url}")
            return url
        
        return None


# ============================================================================
# PIPELINE ORCHESTRATOR
# ============================================================================

class ProductionPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self):
        self.client = AbletonClient()
        self.mix_generator = MixGenerator()
        self.ableton_integration = None
        self.result = PipelineResult(success=False)
    
    def connect(self) -> bool:
        """Connect to Ableton."""
        if not self.client.connect():
            self.result.errors.append("Failed to connect to Ableton Remote Script")
            return False
        self.ableton_integration = AbletonIntegration(self.client)
        return True
    
    def run(self, genre: str, name: str = None, bpm: float = None,
            do_capture: bool = False, do_polish: bool = True,
            do_mp3: bool = True, do_video: bool = False,
            do_youtube: bool = False, title: str = None,
            artist: str = "Ableton MCP Extended", 
            description: str = None) -> PipelineResult:
        """Run the complete production pipeline."""
        
        start_time = time.time()
        
        # Initialize result
        self.result = PipelineResult(
            success=True,
            messages=[],
            errors=[]
        )
        
        try:
            # Step 1: Create mix project
            self.result.messages.append("[1/7] Creating mix project...")
            project = self.mix_generator.create_mix(genre, bpm, name)
            self.result.project = project
            self.result.messages.append(f"  Created {len(project.sections)} sections, {project.total_bars} bars, {project.duration_minutes:.1f} min")
            
            # Step 2: Setup Ableton
            self.result.messages.append("[2/7] Setting up Ableton...")
            if not self.connect():
                raise Exception("Connection failed")
            
            if not self.ableton_integration.setup_project(project):
                raise Exception("Ableton setup failed")
            
            # Step 3: Optional capture (user must manually trigger scenes)
            if do_capture:
                self.result.messages.append("[3/7] Capture mode...")
                print("\n  [!] CAPTURE MODE")
                print("  1. Arm all tracks in Ableton")
                print("  2. Start recording")
                print("  3. Follow the locators and trigger scenes in sequence")
                print(f"  4. Total duration: ~{project.duration_minutes:.1f} minutes")
                print("  5. Stop recording when done")
                print("  6. Press Enter when capture is complete")
                input()
                self.result.messages.append("  Capture complete")
            
            # Step 4: Optional polish
            if do_polish:
                self.result.messages.append("[4/7] Applying polish...")
                self.ableton_integration.apply_polish(project)
            
            # Step 5: Export to WAV (manual step)
            self.result.messages.append("[5/7] Exporting to WAV...")
            wav_path = AudioExporter.export_to_wav(project)
            self.result.wav_file = wav_path
            self.result.messages.append(f"  WAV: {wav_path}")
            
            # Step 6: Optional MP3 conversion
            if do_mp3:
                self.result.messages.append("[6/7] Converting to MP3...")
                mp3_path = AudioExporter.convert_to_mp3(wav_path)
                self.result.mp3_file = mp3_path
                self.result.messages.append(f"  MP3: {mp3_path}")
            
            # Step 7: Optional video creation
            if do_video:
                self.result.messages.append("[7/7] Creating video...")
                video_title = title or f"{project.genre.replace('_', ' ').title()} Mix"
                video_path = VideoCreator.create_waveform_video(
                    self.result.mp3_file or wav_path,
                    title=video_title,
                    artist=artist
                )
                self.result.video_file = video_path
                self.result.messages.append(f"  Video: {video_path}")
            
            # Optional YouTube upload
            if do_youtube and self.result.video_file:
                self.result.messages.append("[8/7] Uploading to YouTube...")
                yt_title = title or f"{project.genre.replace('_', ' ').title()} Mix - {artist}"
                yt_description = description or f"Auto-generated {yt_title} using Ableton MCP Extended"
                
                yt_url = YouTubeUploader.upload(
                    self.result.video_file,
                    title=yt_title,
                    description=yt_description,
                    tags=[genre, "music", "mix", "ableton", "generated"],
                    privacy=YOUTUBE_API_CONFIG["privacy_status"]
                )
                self.result.youtube_url = yt_url
                if yt_url:
                    self.result.messages.append(f"  YouTube: {yt_url}")
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            self.result.messages.append(f"\nPipeline completed in {elapsed:.1f} seconds")
            
        except Exception as e:
            self.result.success = False
            self.result.errors.append(str(e))
            self.result.messages.append(f"Pipeline failed: {e}")
        finally:
            if self.client:
                self.client.close()
        
        return self.result


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Production Pipeline - Complete mix production and distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python production_pipeline.py dub_techno --mp3
  python production_pipeline.py reggae --mp3
  python production_pipeline.py techno --mp3 --video
  python production_pipeline.py dub --capture --mp3 --title "My Dub Mix"
  python production_pipeline.py custom --genre house --bpm 120 --mp3 --youtube

Note: YouTube upload requires youtube-upload CLI tool or manual upload.
        """
    )
    
    # Mix type
    parser.add_argument("mix_type", type=str, default="dub_techno",
                       help="Mix type: dub_techno, dub, techno, hiphop, house, dnb, ambient, reggae, custom")
    
    # Customization
    parser.add_argument("--name", type=str, help="Project name (defaults to timestamp)")
    parser.add_argument("--genre", type=str, help="Genre for custom mixes")
    parser.add_argument("--bpm", type=float, help="BPM override")
    
    # Pipeline options
    parser.add_argument("--capture", action="store_true", 
                       help="Enable capture mode (requires manual scene triggering)")
    parser.add_argument("--no-polish", action="store_true", dest="no_polish",
                       help="Skip polish pass")
    parser.add_argument("--mp3", action="store_true", help="Convert to MP3")
    parser.add_argument("--video", action="store_true", help="Create waveform video")
    parser.add_argument("--youtube", action="store_true", help="Upload to YouTube")
    
    # Metadata
    parser.add_argument("--title", type=str, help="Mix title")
    parser.add_argument("--artist", type=str, default="Ableton MCP Extended",
                       help="Artist name")
    parser.add_argument("--description", type=str, 
                       help="Description for YouTube upload")
    
    # Debug
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would happen without executing")
    
    args = parser.parse_args()
    
    # Validate
    if args.mix_type == "custom" and not args.genre:
        print("[ERROR] --genre required for custom mixes")
        parser.print_help()
        return
    
    # Determine genre
    genre = args.genre or args.mix_type
    
    print("=" * 70)
    print("PRODUCTION PIPELINE")
    print("=" * 70)
    print(f"\n[CONFIGURATION]")
    print(f"  Mix Type: {args.mix_type}")
    print(f"  Genre: {genre}")
    print(f"  BPM: {args.bpm or 'default'}")
    print(f"  Name: {args.name or 'auto'}")
    print(f"  Title: {args.title or 'auto'}")
    print(f"  Artist: {args.artist}")
    print(f"\n[PIPELINE OPTIONS]")
    print(f"  Capture: {'Yes' if args.capture else 'No'}")
    print(f"  Polish: {'No' if args.no_polish else 'Yes'}")
    print(f"  MP3: {'Yes' if args.mp3 else 'No'}")
    print(f"  Video: {'Yes' if args.video else 'No'}")
    print(f"  YouTube: {'Yes' if args.youtube else 'No'}")
    if args.dry_run:
        print(f"\n[DRY RUN] Would execute the above pipeline")
        return
    
    print("\n" + "=" * 70)
    print("EXECUTING PIPELINE")
    print("=" * 70 + "\n")
    
    # Run pipeline
    pipeline = ProductionPipeline()
    result = pipeline.run(
        genre=genre,
        name=args.name,
        bpm=args.bpm,
        do_capture=args.capture,
        do_polish=not args.no_polish,
        do_mp3=args.mp3,
        do_video=args.video,
        do_youtube=args.youtube,
        title=args.title,
        artist=args.artist,
        description=args.description
    )
    
    # Print results
    print("\n" + "=" * 70)
    if result.success:
        print("PIPELINE COMPLETED SUCCESSFULLY")
    else:
        print("PIPELINE COMPLETED WITH ERRORS")
    print("=" * 70)
    
    print("\n[RESULTS]")
    if result.project:
        print(f"  Project: {result.project.name}")
        print(f"  Genre: {result.project.genre}")
        print(f"  BPM: {result.project.bpm}")
        print(f"  Duration: {result.project.duration_minutes:.1f} minutes")
        print(f"  Total Bars: {result.project.total_bars}")
    
    if result.wav_file:
        print(f"  WAV: {result.wav_file}")
    if result.mp3_file:
        print(f"  MP3: {result.mp3_file}")
    if result.video_file:
        print(f"  Video: {result.video_file}")
    if result.youtube_url:
        print(f"  YouTube: {result.youtube_url}")
    
    if result.messages:
        print("\n[LOG]")
        for msg in result.messages:
            print(f"  {msg}")
    
    if result.errors:
        print("\n[ERRORS]")
        for error in result.errors:
            print(f"  [ERROR] {error}")
    
    print("\n" + "=" * 70)
    
    return result


if __name__ == "__main__":
    result = main()
    
    # Exit code
    sys.exit(0 if result and result.success else 1)
