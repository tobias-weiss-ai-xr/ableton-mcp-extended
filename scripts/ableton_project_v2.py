#!/usr/bin/env python3
"""
Ableton Live Project Generator - Create functional .als files

Creates working Ableton Live project files using proper XML structure.
Based on Ableton Live's actual .als file format (GZIP-compressed XML).
"""

import xml.etree.ElementTree as ET
import gzip
import struct
from datetime import datetime
from pathlib import Path


def create_ableton_project(
    artist="KingOfDub",
    title="Roots Reggae Mix",
    filename="Reggae_KingOfDub.als",
    bpm=80
):
    """
    Create a working Ableton Live .als project file.
    Uses proper Ableton XML structure including major/minor version attributes.
    """
    
    print(f"[CREATING ABLETON PROJECT]")
    print(f"  Artist: {artist}")
    print(f"  Title: {title}")
    print(f"  Tempo: {bpm} BPM")
    print(f"  Location: {filename}")
    print()
    
    # Create root element with proper Ableton structure
    # Ableton uses MajorVersion="4" MinorVersion="2" for Live 4/5+
    root = ET.Element("Ableton")
    root.set("MajorVersion", "4")
    root.set("MinorVersion", "2")
    
    # Creator section
    creator = ET.SubElement(root, "Creator")
    creator_minor_version = ET.SubElement(creator, "CreatorMinorVersion")
    creator_minor_version.set("Value", "2")
    creator_major_version = ET.SubElement(creator, "CreatorMajorVersion")
    creator_major_version.set("Value", "4")
    
    # Meta section
    meta = ET.SubElement(root, "Meta")
    
    # Project MetaData
    meta_data = ET.SubElement(meta, "MetaDataSet")
    meta_data.set("Id", "LiveData.Meta")
    meta_data.set("ListName", "MetaInfo Entries")
    
    # Add project info
    entries = ET.SubElement(meta_data, "Entries")
    
    # Title
    meta_entry = ET.SubElement(entries, "Entry")
    meta_entry.set("Name", "Title")
    meta_entry.set("XValue", title)
    
    # Artist
    meta_entry2 = ET.SubElement(entries, "Entry")
    meta_entry2.set("Name", "Author")
    meta_entry2.set("XValue", artist)
    
    # Tempo
    meta_entry3 = ET.SubElement(entries, "Entry")
    meta_entry3.set("Name", "Tempo")
    meta_entry3.set("Value", f"{bpm}.0")
    
    # Arrangement section
    arrangement = ET.SubElement(root, "Arrangement")
    arrangement.set("AutoSmoothTransitions", "true")
    arrangement.set("AutoSmoothLaunchParam", "true")
    arrangement.set("IsSessionArrangement", "false")
    arrangement.set("Layout", "0")
    arrangement.set("LogicalTimestamper", "0")
    arrangement.set("LomId", "0")
    arrangement.set("Style", "0")
    
    # Tempo
    arrangement_master = ET.SubElement(arrangement, "ArrangementMaster")
    arrangement_master.set("LomId", "1")
    
    # Automation tempo
    auto_tempo = ET.SubElement(arrangement_master, "AutomationTarget")
    
    # Tempo value
    tempo = ET.SubElement(arrangement_master, "Tempo")
    tempo_envelope = ET.SubElement(tempo, "Manual")
    tempo_value = ET.SubElement(tempo_envelope, "Time")
    tempo_point_list = ET.SubElement(tempo_value, "Events")
    tempo_event = ET.SubElement(tempo_point_list, "FloatEvent")
    tempo_event.set("Id", "1")
    tempo_event.set("Pos", "0")
    tempo_event.set("Value", str(bpm))
    
    # Time signature
    time_signature = ET.SubElement(arrangement_master, "TimeSignature")
    time_signature.set("Denominator", "4")
    time_signature.set("Numerator", "4")
    
    # Tracks
    tracks = ET.SubElement(arrangement, "Tracks")
    
    # Create 8 reggae tracks
    track_configs = [
        ("Reggae Kick (One Drop)", -6.0, 0.0, 0, "midi"),
        ("Sub Bass (Roots)", -4.0, 0.0, 1, "midi"),
        ("Snare (Backbeat)", -5.0, -0.15, 2, "midi"),
        ("Hi-Hats (Upbeat)", -8.0, 0.2, 3, "midi"),
        ("Guitar (Upstroke)", -9.0, -0.25, 4, "midi"),
        ("Keyboards/Organ", -10.0, 0.3, 5, "midi"),
        ("Dub Echo FX", -15.0, 0.4, 6, "audio"),
        ("Reverb/Spring", -12.0, 0.0, 7, "audio")
    ]
    
    for idx, config in enumerate(track_configs):
        name, volume_db, pan, track_id, track_type = config
        track = create_track(idx, name, volume_db, pan, track_id, track_type)
        tracks.append(track)
    
    # Locators
    locators = ET.SubElement(arrangement, "Locators")
    
    # Create locators at reggae section boundaries
    locator_data = [
        ("One Drop Intro", 0, bpm),
        ("Rockers Groove", 32, bpm),
        ("Vocal Chant", 64, bpm),
        ("Dub Section Drop", 80, bpm),
        ("Roots Rockers Verse", 112, bpm),
        ("Dub Echo Breakdown", 144, bpm),
        ("Lion of Judah", 176, bpm),
        ("Babylon System Drop", 192, bpm),
        ("Natural Mystic Outro", 240, bpm),
        ("Reggae_KingOfDub_End", 272, bpm)
    ]
    
    for idx, config in enumerate(locator_data):
        name, bar, tempo = config
        locator = create_locator(idx, name, bar)
        locators.append(locator)
    
    # Master track arrangement
    master_track_arr = ET.SubElement(arrangement, "MasterTrack")
    master_device_chain = ET.SubElement(master_track_arr, "DeviceChain")
    
    # Generate XML and save
    xml_string = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    
    # Ableton .als files are GZIP-compressed
    with gzip.open(filename, "wb") as f:
        f.write(xml_string)
    
    print(f"[SUCCESS] Saved Ableton project to: {filename}")
    print(f"[FILE SIZE] {Path(filename).stat().st_size} bytes")
    print()
    print(f"[PROJECT SUMMARY]")
    print(f"  BPM: {bpm}")
    print(f"  Tracks: 8 (Reggae configured)")
    print(f"  Locators: 10")
    print(f"  Duration: ~{272 * 60 / bpm:.1f} minutes (272 bars)")
    print()
    print(f"[NEXT STEPS]")
    print(f"  1. Open {filename} in Ableton Live")
    print(f"  2. Add your MIDI/audio clips to each track")
    print(f"  3. Use the locators to navigate between sections")
    print(f"  4. Press play to hear your arrangement")
    print()
    print(f"[READY!] Your Reggae project is ready for production by {artist}!")
    
    return filename


def create_track(index, name, volume_db, pan, track_id, track_type):
    """Create a track element with proper Ableton structure."""
    track = ET.Element("Track")
    track.set("Locked", "false")
    track.set("UserColor", "0")
    track.set("LomId", str(track_id + 10))  # Unique ID
    
    # Basic track info
    name_element = ET.SubElement(track, "Name")
    name_element.set("Value", name)
    name_element.set("EffectiveName", name)
    
    # Device chain
    device_chain = ET.SubElement(track, "DeviceChain")
    
    # Main mixer strip
    main_mixer = ET.SubElement(device_chain, "MainMixerVolume")
    volume_value = ET.SubElement(main_mixer, "Manual")
    
    # Convert dB to linear volume (Ableton uses linear scale)
    # 0dB = 1.0, -6dB ≈ 0.501
    if volume_db == 0:
        linear_vol = 1.0
    else:
        linear_vol = 10 ** (volume_db / 20.0)
    
    volume_element = ET.SubElement(volume_value, "Value")
    volume_element.set("Value", str(linear_vol))
    
    # Panning
    pan_mixer = ET.SubElement(device_chain, "MainMixerPan")
    pan_value = ET.SubElement(pan_mixer, "Value")
    pan_value.set("Value", str(pan))
    
    # Depending on track type, add appropriate devices
    if track_type == "midi":
        # Add a simple MIDI instrument placeholder
        last_device_id = ET.SubElement(device_chain, "LastDeviceId")
        last_device_id.set("Value", "0")
    else:
        # For audio tracks
        pass
    
    return track


def create_locator(index, name, bar):
    """Create a locator element."""
    locator = ET.Element("Locator")
    locator.set("Id", str(index))
    
    # Position in beats (bar * 4)
    position = str(bar * 4)
    
    # Position element
    position_element = ET.SubElement(locator, "Position")
    position_element.set("Type", "TimePosition")
    position_value = ET.SubElement(position_element, "Value")
    position_value.set("Value", position)
    
    # Name
    time_name = ET.SubElement(locator, "TimeName")
    time_name_element = ET.SubElement(time_name, "FormattedString")
    time_name_element.set("Value", name)
    
    # Duration
    time_duration = ET.SubElement(locator, "TimeDuration")
    timeval = ET.SubElement(time_duration, "Value")
    timeval.set("Value", "4")  # One bar = 4 beats
    
    return locator


def save_project_to_file(root, filename):
    """Save project to GZIP file."""
    # Generate XML string
    xml_string = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    
    # GZIP compress
    with gzip.open(filename, "wb") as f:
        f.write(xml_string)


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    artist = "KingOfDub"
    title = "Roots Reggae Mix"
    filename = "Reggae_KingOfDub.als"
    bpm = 80
    
    if len(sys.argv) > 1:
        artist = sys.argv[1]
    if len(sys.argv) > 2:
        title = sys.argv[2]
    if len(sys.argv) > 3:
        filename = sys.argv[3]
    if len(sys.argv) > 4:
        bpm = float(sys.argv[4])
    
    # Create and save project
    create_ableton_project(artist, title, filename, bpm)
