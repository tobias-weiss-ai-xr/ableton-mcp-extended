#!/usr/bin/env python3
"""
Ableton Live 12 Project Generator - Create functional .als files

Creates working Ableton Live 12 project files using proper XML structure.
Ableton Live 12 uses MajorVersion="10" with appropriate MinorVersion.
"""

import xml.etree.ElementTree as ET
import gzip
import struct
from datetime import datetime
from pathlib import Path


def create_ableton_12_project(
    artist="KingOfDub",
    title="Roots Reggae Mix",
    filename="Reggae_KingOfDub.als",
    bpm=80
):
    """
    Create a working Ableton Live 12 .als project file.
    Uses proper Ableton 12 XML structure (MajorVersion="10").
    """
    
    print(f"[CREATING ABLETON LIVE 12 PROJECT]")
    print(f"  Artist: {artist}")
    print(f"  Title: {title}")
    print(f"  Tempo: {bpm} BPM")
    print(f"  Location: {filename}")
    print()
    
    # Create root element with Ableton 12 structure
    # Ableton Live 12 typically uses MajorVersion="10" with various MinorVersions
    root = ET.Element("Ableton")
    root.set("MajorVersion", "10")
    root.set("MinorVersion", "5")  # Common Ableton 12 version
    
    # Creator section
    creator = ET.SubElement(root, "Creator")
    creator_minor_version = ET.SubElement(creator, "CreatorMinorVersion")
    creator_minor_version.set("Value", "5")
    creator_major_version = ET.SubElement(creator, "CreatorMajorVersion")
    creator_major_version.set("Value", "10")
    
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
    
    # Track Management
    track_manager = ET.SubElement(arrangement, "TrackManager")
    
    # FlexMachineViewData (Ableton 12 feature)
    flex_machine = ET.SubElement(track_manager, "FlexMachineViewData")
    flex_machine.set("FilterFrequency", "3.0")
    flex_machine.set("FilterResonance", "0.0")
    
    # Arrangement Master (tempo, time signature)
    arrangement_master = ET.SubElement(arrangement, "ArrangementMaster")
    arrangement_master.set("LomId", "1")
    
    # Tempo
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
    
    # Tracks container
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
        track = create_ableton_12_track(idx, name, volume_db, pan, track_id, track_type)
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
        locator = create_ableton_12_locator(idx, name, bar)
        locators.append(locator)
    
    # Master track arrangement
    master_track_arr = ET.SubElement(arrangement, "MasterTrack")
    master_device_chain = ET.SubElement(master_track_arr, "DeviceChain")
    
    # Generate XML with proper encoding
    # Add XML declaration
    xml_string = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_string += ET.tostring(root, encoding="utf-8", xml_declaration=False)
    
    # Ableton .als files are GZIP-compressed with specific format
    with gzip.open(filename, "wb", compresslevel=6) as f:
        f.write(xml_string)
    
    file_size = Path(filename).stat().st_size
    print(f"[SUCCESS] Saved Ableton Live 12 project to: {filename}")
    print(f"[FILE SIZE] {file_size} bytes")
    print()
    print(f"[PROJECT SUMMARY]")
    print(f"  Version: Ableton Live 12 (MajorVersion=10)")
    print(f"  BPM: {bpm}")
    print(f"  Tracks: 8 (Reggae configured)")
    print(f"  Locators: 10")
    print(f"  Duration: ~{272 * 60 / bpm:.1f} minutes (272 bars)")
    print()
    print(f"[NEXT STEPS]")
    print(f"  1. Open {filename} in Ableton Live 12")
    print(f"  2. Add your MIDI/audio clips to each track")
    print(f"  3. Use the locators to navigate between sections")
    print(f"  4. Press play to hear your arrangement")
    print()
    print(f"[READY!] Your Reggae project is ready for production by {artist}!")
    
    return filename


def create_ableton_12_track(index, name, volume_db, pan, track_id, track_type):
    """Create an Ableton Live 12 track element with proper structure."""
    track = ET.Element("Track")
    track.set("Locked", "false")
    track.set("UserColor", "0")
    track.set("LomId", str(track_id + 10))
    
    # Basic track info
    name_element = ET.SubElement(track, "Name")
    name_element.set("Value", name)
    name_element.set("EffectiveName", name)
    
    # Device chain
    device_chain = ET.SubElement(track, "DeviceChain")
    
    # Main mixer volume
    main_mixer_volume = ET.SubElement(device_chain, "MainMixerVolume")
    volume_manual = ET.SubElement(main_mixer_volume, "Manual")
    
    # Convert dB to linear volume (Ableton uses linear scale)
    # 0dB = 1.0, -6dB ≈ 0.501
    if volume_db == 0:
        linear_vol = 1.0
    else:
        linear_vol = min(max(10 ** (volume_db / 20.0), 0.0), 1.0)
    
    # Volume value
    volume_time = ET.SubElement(volume_manual, "Time")
    volume_events = ET.SubElement(volume_time, "Events")
    volume_event = ET.SubElement(volume_events, "FloatEvent")
    volume_event.set("Id", "0")
    volume_event.set("Pos", "0")
    volume_event.set("Value", str(linear_vol))
    volume_event.set("Min", "0.0")
    volume_event.set("Max", "1.0")
    
    # Panning
    main_mixer_pan = ET.SubElement(device_chain, "MainMixerPan")
    pan_manual = ET.SubElement(main_mixer_pan, "Manual")
    pan_time = ET.SubElement(pan_manual, "Time")
    pan_events = ET.SubElement(pan_time, "Events")
    pan_event = ET.SubElement(pan_events, "FloatEvent")
    pan_event.set("Id", "0")
    pan_event.set("Pos", "0")
    pan_event.set("Value", str(pan))
    pan_event.set("Min", "-1.0")
    pan_event.set("Max", "1.0")
    
    # Track type specific setup
    if track_type == "midi":
        # MIDI track setup
        last_device_id = ET.SubElement(device_chain, "LastDeviceId")
        last_device_id.set("Value", "0")
        
        # Midi automation target
        midi_automation = ET.SubElement(device_chain, "AutomationTarget")
        midi_automation.set("Id", "0")
        midi_automation.set("EffectId", "0")
        midi_automation.set("Parameter" ,"0")
    else:
        # Audio track setup
        pass
    
    return track


def create_ableton_12_locator(index, name, bar):
    """Create an Ableton Live 12 locator element."""
    locator = ET.Element("Locator")
    locator.set("Id", str(index))
    
    # Position in beats (bar * 4)
    position = str(bar * 4)
    
    # Position element
    position_element = ET.SubElement(locator, "Position")
    position_element.set("Type", "TimePosition")
    
    # Time position with value
    time_value = ET.SubElement(position_element, "Value")
    time_value.set("Value", position)
    
    # Name
    time_name = ET.SubElement(locator, "TimeName")
    formatted_string = ET.SubElement(time_name, "FormattedString")
    formatted_string.set("Value", name)
    
    # Duration (1 bar = 4 beats)
    time_duration = ET.SubElement(locator, "TimeDuration")
    duration_value = ET.SubElement(time_duration, "Value")
    duration_value.set("Value", "4")
    
    return locator


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
    
    # Ensure projects directory exists
    Path("projects/ableton").mkdir(parents=True, exist_ok=True)
    
    # Create and save project
    full_filename = f"projects/ableton/{filename}"
    create_ableton_12_project(artist, title, full_filename, bpm)
