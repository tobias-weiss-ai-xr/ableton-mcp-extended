#!/usr/bin/env python3
"""
Ableton Project Generator - Create .als files directly

Generates Ableton Live project files (.als) without needing Remote Script connection.
Based on Ableton's XML-based project format.
"""

import xml.etree.ElementTree as ET
import gzip
from datetime import datetime
from pathlib import Path


class AbletonProject:
    """Create Ableton Live project files directly."""
    
    # Ableton XML namespace
    NS = {'ableton': 'http://www.ableton.com/ableton-live-project/4.0/'}
    
    def __init__(self, title="Untitled", bpm=120, artist=""):
        self.title = title
        self.bpm = bpm
        self.artist = artist
        self.root = ET.Element("Ableton")
        self.root.set("MajorVersion", "4")
        self.root.set("MinorVersion", "2")
        
    def create_project(self):
        """Create the basic project structure."""
        # Create creator
        creator = ET.SubElement(self.root, "Creator")
        ET.SubElement(creator, "SoftwareIdentity")
        
        # Create meta data
        meta_data = ET.SubElement(self.root, "MetaDataSet")
        self._add_meta_data(meta_data)
        
        # Create arrangement
        arrangement = ET.SubElement(self.root, "Arrangement")
        self._create_arrangement(arrangement)
        
        # Create master track
        self._create_master_track()
        
        return self.root
    
    def _add_meta_data(self, meta_data):
        """Add project metadata."""
        project_data = ET.SubElement(meta_data, "ProjectData", {
            "Tempo": str(self.bpm),
            "TimeSignature": "4/4",
            "Artist": self.artist,
            "Created": datetime.now().isoformat()
        })
        
    def _create_arrangement(self, arrangement):
        """Create arrangement with locators."""
        # Set tempo
        arrangement.set("Tempo", str(self.bpm))
        arrangement.set("TimeSignature", "4/4")
        
        # Create tracks list
        tracks = ET.SubElement(arrangement, "Tracks")
        
        # Add tracks
        self._add_tracks(tracks)
        
        # Add locators
        self._add_locators(arrangement)
        
    def _create_master_track(self):
        """Create master track."""
        master = ET.SubElement(self.root, "MasterTrack")
        master.set("Name", "Master")
        
        # Volume
        volume = ET.SubElement(master, "Volume")
        volume.set("Value", "0.75")  # -6dB approximately
        
    def _add_tracks(self, tracks_element):
        """Add instrument tracks."""
        track_configs = [
            ("Reggae Kick (One Drop)", -6.0, 0.0, "midi"),
            ("Sub Bass (Roots)", -4.0, 0.0, "midi"),
            ("Snare (Backbeat)", -5.0, -0.15, "midi"),
            ("Hi-Hats (Upbeat)", -8.0, 0.2, "midi"),
            ("Guitar (Upstroke)", -9.0, -0.25, "midi"),
            ("Keyboards/Organ", -10.0, 0.3, "midi"),
            ("Dub Echo FX", -15.0, 0.4, "audio"),
            ("Reverb/Spring", -12.0, 0.0, "audio")
        ]
        
        for idx, config in enumerate(track_configs):
            name, vol_db, pan, track_type = config
            track = self._create_track(idx, name, vol_db, pan, track_type)
            tracks_element.append(track)
    
    def _create_track(self, index, name, volume_db, pan, track_type):
        """Create a single track."""
        track = ET.Element("Track")
        track.set("Id", str(index))
        track.set("Name", name)
        track.set("Type", track_type)
        
        # Volume
        volume = ET.SubElement(track, "Volume")
        vol_value = 10 ** (volume_db / 20)  # Convert dB to linear
        volume.set("Value", str(vol_value))
        
        # Pan
        pan_el = ET.SubElement(track, "Pan")
        pan_el.set("Value", str(pan))
        
        # Device chain
        _devices = ET.SubElement(track, "DeviceChain")
        
        if track_type == "midi":
            # Add MIDI device (simple)
            device = ET.SubElement(_devices, "Device")
            device.set("Type", "MidiInstrument")
            device.set("Name", name)
        
        # Add basic effects
        self._add_effects(_devices, name)
        
        return track
    
    def _add_effects(self, device_chain, track_name):
        """Add basic effects to track."""
        # Add EQ Eight (basic)
        eq = ET.SubElement(device_chain, "Device")
        eq.set("Type", "Eq8")
        eq.set("Name", "EQ Eight")
        
        # Add compression for bass/kicks
        if any(x in track_name for x in ["Kick", "Bass"]):
            comp = ET.SubElement(device_chain, "Device")
            comp.set("Type", "Compressor")
            comp.set("Name", "Compressor")
    
    def _add_locators(self, arrangement):
        """Add locators at section boundaries."""
        locators_element = ET.SubElement(arrangement, "Locators")
        
        # Reggae locators
        locator_data = [
            ("One Drop Intro", 0, 80),
            ("Rockers Groove", 32, 80),
            ("Vocal Chant", 64, 80),
            ("Dub Section Drop", 80, 80),
            ("Roots Rockers Verse", 112, 80),
            ("Dub Echo Breakdown", 144, 80),
            ("Lion of Judah", 176, 80),
            ("Babylon System Drop", 192, 80),
            ("Natural Mystic Outro", 240, 80),
            ("Reggae_KingOfDub_End", 272, 80)
        ]
        
        for idx, config in enumerate(locator_data):
            name, bar, tempo = config
            locator = self._create_locator(idx, name, bar, tempo)
            locators_element.append(locator)
    
    def _create_locator(self, index, name, bar, tempo):
        """Create a single locator."""
        locator = ET.Element("Locator")
        locator.set("Id", str(index))
        locator.set("Name", name)
        locator.set("Bar", str(bar))
        locator.set("Beats", "0")
        locator.set("Tempo", str(tempo))
        return locator
    
    def save(self, filename):
        """Save project to .als file."""
        # Create project structure
        self.create_project()
        
        # Generate XML string
        xml_string = ET.tostring(self.root, encoding="utf-8", xml_declaration=True)
        
        # Ableton .als files are GZIP-compressed
        with gzip.open(filename, "wb") as f:
            f.write(xml_string)
        
        print(f"[SUCCESS] Saved Ableton project to: {filename}")


def create_reggae_project(
    artist="KingOfDub",
    title="Roots Reggae Mix",
    filename="Reggae_KingOfDub.als"
):
    """Create a reggae project for Ableton Live."""
    
    print(f"[CREATING ABLETON PROJECT]")
    print(f"  Artist: {artist}")
    print(f"  Title: {title}")
    print(f"  Tempo: 80 BPM")
    print(f"  Location: {filename}")
    print()
    
    # Create project
    project = AbletonProject(title=title, bpm=80, artist=artist)
    project.create_project()
    
    # Save project
    project.save(filename)
    
    print()
    print(f"[PROJECT SUMMARY]")
    print(f"  BPM: 80")
    print(f"  Tracks: 8 (Reggae configured)")
    print(f"  Locators: 10")
    print(f"  Duration: ~3.4 minutes (272 bars)")
    print()
    print(f"[NEXT STEPS]")
    print(f"  1. Open {filename} in Ableton Live")
    print(f"  2. Add your MIDI/audio clips to each track")
    print(f"  3. Use the locators to navigate between sections")
    print(f"  4. Press play to hear your arrangement")
    print()
    print(f"[READY!] Your Reggae project is ready for production by {artist}!")
    
    return filename


if __name__ == "__main__":
    import sys
    
    # Check arguments
    artist = "KingOfDub"
    title = "Roots Reggae Mix"
    filename = "Reggae_KingOfDub.als"
    
    if len(sys.argv) > 1:
        artist = sys.argv[1]
    if len(sys.argv) > 2:
        title = sys.argv[2]
    if len(sys.argv) > 3:
        filename = sys.argv[3]
    
    # Create project
    create_reggae_project(artist, title, filename)
