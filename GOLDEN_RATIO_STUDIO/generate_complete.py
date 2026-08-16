#!/usr/bin/env python3
"""
GOLDEN RATIO STUDIO - COMPLETE PRODUCTION SYSTEM
Complete integration of pattern generation and XML saving.
"""

import logging
from generate_all_genres_refactored import (
    Genre,
    GenreProjectGenerator,
    MIDINote
)
from als_generator_fixed import (
    AbletonProjectSaver,
    AbletonReturnTrack,
    generate_and_save_project
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GoldenRatioStudio.CompleteGenerator")

def create_dub_return_tracks() -> list:
    """Create return tracks for dub reggae with authentic effects."""
    return [
        AbletonReturnTrack(
            id=0,
            name="Dub Echo",
            effects=["Tape Delay (1/4 @ 75%)", "Ping Pong Delay"],
            volume=0.85,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=1,   
            name="Spring Reverb",
            effects=["Spring Reverb (3.2s)", "EQ Eight"],
            volume=0.75,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=2,
            name="Dub Filter",
            effects=["Auto Filter", "Utility"],
            volume=0.70,
            pan=0.0
        )
    ]

def create_techno_return_tracks() -> list:
    """Create return tracks for techno with industrial effects."""
    return [
        AbletonReturnTrack(
            id=0,
            name="Techno Echo",
            effects=["Filter Delay", "Simple Delay"],
            volume=0.85,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=1,
            name="Reverb Space",
            effects=["Hybrid Reverb", "Saturator"],
            volume=0.70,
            pan=0.0
        )
    ]

def create_house_return_tracks() -> list:
    """Create return tracks for house with warm effects."""
    return [
        AbletonReturnTrack(
            id=0,
            name="House Delay",
            effects=["Tape Delay (1/8)", "Ping Pong Delay"],
            volume=0.80,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=1,
            name="Warm Reverb",
            effects=["Transient Master", "Reverb"],
            volume=0.75,
            pan=0.0
        )
    ]

def create_hiphop_return_tracks() -> list:
    """Create return tracks for hip-hop with lo-fi effects."""
    return [
        AbletonReturnTrack(
            id=0,
            name="Lo-Fi Tape",
            effects=["Vinyl Distortion", "Redux"],
            volume=0.85,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=1,
            name="Hip-Hop Verb",
            effects=["Convolution Reverb", "EQ Eight"],
            volume=0.70,
            pan=0.0
        )
    ]

def create_dnb_return_tracks() -> list:
    """Create return tracks for DnB with aggressive effects."""
    return [
        AbletonReturnTrack(
            id=0,
            name="DnB Reverb",
            effects=["Reverb", "Utility"],
            volume=0.80,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=1,
            name="Break FX",
            effects=["Saturator", "EQ Eight"],
            volume=0.75,
            pan=0.0
        )
    ]

def create_ambient_return_tracks() -> list:
    """Create return tracks for ambient with spacious effects."""
    return [
        AbletonReturnTrack(
            id=0,
            name="Space",
            effects=["Reverb (Long)", "Delay"],
            volume=0.90,
            pan=0.0
        ),
        AbletonReturnTrack(
            id=1,
            name="Texture",
            effects=["Granulator", "Corpus"],
            volume=0.70,
            pan=0.0
        )
    ]

# Genre to return track mapping
RETURN_TRACK_CONFIGS = {
    Genre.DUB_REGGAE: create_dub_return_tracks,
    Genre.DUB_TECHNO: create_techno_return_tracks,
    Genre.DEEP_HOUSE: create_house_return_tracks,
    Genre.TECH_HOUSE: create_house_return_tracks,
    Genre.HIP_HOP: create_hiphop_return_tracks,
    Genre.TRAP: create_hiphop_return_tracks,
    Genre.DNB: create_dnb_return_tracks,
    Genre.AMBIENT: create_ambient_return_tracks,
}

def generate_complete_project(genre: Genre, bar_count: int = 128, 
                             seed: int = None, 
                             output_file: str = None) -> dict:
    """Generate complete project with patterns and save to ALS file."""
    
    logger.info(f"Generating complete project for {genre.value}")
    
    # Generate patterns
    project_data = GenreProjectGenerator.generate_project(genre, bar_count, seed)
    if not project_data:
        logger.error(f"Failed to generate project for {genre.value}")
        return None
    
    # Get appropriate return tracks
    return_tracks_fn = RETURN_TRACK_CONFIGS.get(genre, lambda: [])
    return_tracks = return_tracks_fn()
    
    # Determine output filename
    if output_file is None:
        output_file = f"{genre.value}_enhanced.als"
    
    # Save project
    try:
        file_size = generate_and_save_project(project_data, output_file, return_tracks)
        logger.info(f"Project saved: {output_file} ({file_size} bytes)")
        
        # Add file info to project data
        project_data['filename'] = output_file
        project_data['file_size'] = file_size
        project_data['return_tracks'] = len(return_tracks)
        
        return project_data
        
    except Exception as e:
        logger.error(f"Failed to save project: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_all_genres(bar_count: int = 128, seed: int = None):
    """Generate complete projects for all genres."""
    
    print("=" * 80)
    print("GOLDEN RATIO STUDIO - COMPLETE GENERATION SYSTEM")
    print("Generating enhanced projects with proper XML & compression")
    print("=" * 80)
    print()
    
    genres = [
        Genre.DUB_REGGAE,
        Genre.DUB_TECHNO,
        Genre.DEEP_HOUSE,
        Genre.TECH_HOUSE,
        Genre.HIP_HOP,
        Genre.TRAP,
        Genre.DNB,
        Genre.AMBIENT
    ]
    
    results = []
    
    for i, genre in enumerate(genres, 1):
        print(f"[{i}/{len(genres)}] Generating {genre.value}...")
        
        # Use deterministic seed per genre
        genre_seed = seed or (42 + i)
        
        project = generate_complete_project(
            genre=genre,
            bar_count=bar_count,
            seed=genre_seed,
            output_file=f"{genre.value}_enhanced_v2.als"
        )
        
        if project:
            results.append(project)
            print(f"  - BPM: {project['bpm']}, Key: {project['key']}")
            print(f"  - Tracks: {len(project['patterns'])}, Return Tracks: {project.get('return_tracks', 0)}")
            print(f"  - File: {project['filename']} ({project['file_size']} bytes)")
            print()
        else:
            print(f"  [ERROR] Failed to generate {genre.value}")
            print()
    
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"Successful: {len(results)}/{len(genres)}")
    print()
    
    if results:
        print("PROJECTS GENERATED:")
        for result in results:
            genre = result['genre']
            print(f"  - {result['filename']} ({result['bpm']} BPM, {result['key']})")
        
        total_size = sum(r['file_size'] for r in results)
        total_notes = sum(len(r['patterns'].get(track_name, [])) 
                         for r in results 
                         for track_name in r['patterns'])
        
        print()
        print(f"Total file size: {total_size} bytes")
        print(f"Total MIDI notes: {total_notes}")
    
    print()
    print("BLESS UP - Golden Ratio Studio complete, mon!")
    
    return results

if __name__ == '__main__':
    import sys
    
    # Parse command line args
    bar_count = 128
    seed = None
    specific_genre = None
    
    if len(sys.argv) > 1:
        try:
            bar_count = int(sys.argv[1])
        except ValueError:
            pass
    
    if len(sys.argv) > 2:
        try:
            seed = int(sys.argv[2])
        except ValueError:
            pass
    
    if len(sys.argv) > 3:
        specific_genre = sys.argv[3]
    
    if specific_genre:
        # Generate single genre
        genre_map = {g.value: g for g in Genre}
        if specific_genre in genre_map:
            print(f"Generating single genre: {specific_genre}")
            project = generate_complete_project(
                genre=genre_map[specific_genre],
                bar_count=bar_count,
                seed=seed
            )
            if project:
                print(f"Done: {project['filename']}")
        else:
            print(f"Unknown genre: {specific_genre}")
            print(f"Available genres: {list(genre_map.keys())}")
    else:
        # Generate all genres
        generate_all_genres(bar_count=bar_count, seed=seed)
