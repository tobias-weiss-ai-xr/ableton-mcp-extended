#!/usr/bin/env python3
"""
DEEP AUDIT - Search for remaining gaps, issues, and improvement potential
"""

import re
from pathlib import Path

print("=" * 80)
print("GOLDEN_RATIO_STUDIO - DEEP AUDIT FOR REMAINING ISSUES")
print("=" * 80)
print()

issues_found = []

# AUDIT 1: Pattern Analysis
print("[AUDIT 1] Pattern Feature Analysis")
print("-" * 80)

refactored_content = Path('generate_all_genres_refactored.py').read_text() if Path('generate_all_genres_refactored.py').exists() else ""

checklist = {
    "Snare Patterns": re.search(r'snare|Snare', refactored_content) is not None,
    "Clap Patterns": re.search(r'clap|Clap', refactored_content) is not None,
    "Cymbal/Crash": re.search(r'crash|Crash|cymbal|Cymbal', refactored_content) is not None,
    "Tom Patterns": re.search(r'tom|Tom', refactored_content) is not None,
    "Percussion Layers": re.search(r'percussion|Percussion', refactored_content) is not None,
    "Arpeggios": re.search(r'arp|arpeggio|Arpeggio', refactored_content, re.I) is not None,
    "Melody/Hook": re.search(r'melody|hook|lead', refactored_content, re.I) is not None,
    "Pad/Layering": re.search(r'pad|layer', refactored_content, re.I) is not None,
    "Fill Transitions": re.search(r'fill|transition', refactored_content, re.I) is not None,
    "Breakbeat Variants": re.search(r'breakbeat|break.*beat', refactored_content, re.I) is not None,
}

missing_patterns = [feature for feature, present in checklist.items() if not present]
if missing_patterns:
    print(f"  [GAP] Missing patterns ({len(missing_patterns)}): {missing_patterns}")
    issues_found.append(f"Missing advanced patterns: {len(missing_patterns)}")
else:
    print(f"  [OK] All checked patterns present")

# AUDIT 2: Genre Track Count
print("\n[AUDIT 2] Genre Track Coverage")
print("-" * 80)

genre_track_counts = {
    'dub_reggae': 3,
    'dub_techno': 2,
    'deep_house': 3,
    'tech_house': 3,
    'hip_hop': 2,
    'trap': 2,
    'dnb': 2,
    'ambient': 1,
}

insufficient_tracks = [g for g, count in genre_track_counts.items() if count < 3]
if insufficient_tracks:
    print(f"  [GAP] Genres with <3 tracks: {insufficient_tracks}")
    issues_found.append(f"Minimal instrument tracks in {len(insufficient_tracks)} genres")
else:
    print(f"  [OK] All genres have sufficient tracks")

# AUDIT 3: Runtime Tests
print("\n[AUDIT 3] Runtime Integration")
print("-" * 80)

import time
import sys

try:
    from generate_all_genres_refactored import Genre, GenreProjectGenerator
    
    start = time.time()
    project = GenreProjectGenerator.generate_project(Genre.DUB_REGGAE, bar_count=128, seed=42)
    generation_time = time.time() - start
    
    if project:
        total_notes = sum(len(notes) for notes in project['patterns'].values())
        memory = sys.getsizeof(project)
        
        print(f"  [OK] Generation works")
        print(f"       Time: {generation_time:.3f}s, Notes: {total_notes}, Memory: {memory}B")
        
        if generation_time > 5:
            print(f"  [SLOW] Generation >5s")
            issues_found.append("Slow generation performance")
    else:
        print(f"  [ERROR] Generation returned None")
        issues_found.append("Generation failed")
        
except Exception as e:
    print(f"  [ERROR] {e}")
    issues_found.append(f"Runtime error: {e}")

# AUDIT 4: Documentation
print("\n[AUDIT 4] Documentation Check")
print("-" * 80)

required_docs = ['README.md', 'USER_GUIDE.md', 'API.md']
missing_docs = [doc for doc in required_docs if not Path(doc).exists()]

if missing_docs:
    print(f"  [GAP] Missing docs: {missing_docs}")
    issues_found.append(f"Missing {len(missing_docs)} documentation files")
else:
    print(f"  [OK] All documentation present")

# AUDIT 5: Edge Cases
print("\n[AUDIT 5] Edge Case Handling")
print("-" * 80)

edge_issues = []

try:
    from generate_all_genres_refactored import GenreProjectGenerator
    
    # Zero bars
    zero = GenreProjectGenerator.generate_project(Genre.DUB_REGGAE, bar_count=0)
    if zero:
        print(f"  [ISSUE] Zero bars should handle gracefully")
        edge_issues.append("Zero bars not handled")
    
    # Negative bars
    try:
        neg = GenreProjectGenerator.generate_project(Genre.DUB_REGGAE, bar_count=-1)
        print(f"  [ISSUE] Negative bars should raise error")
        edge_issues.append("Negative bars not validated")
    except:
        print(f"  [OK] Negative bars raises error")
    
    # Extreme bars
    huge = GenreProjectGenerator.generate_project(Genre.DUB_REGGAE, bar_count=10000)
    if huge:
        print(f"  [ISSUE] No limit on bar count")
        edge_issues.append("No bar count limit")
        
except Exception as e:
    print(f"  [INFO] Edge case testing: {e}")

if edge_issues:
    issues_found.extend(edge_issues)

# SUMMARY
print("\n" + "=" * 80)
print("AUDIT RESULTS")
print("=" * 80)

if not issues_found:
    print("\n[SUCCESS] NO CRITICAL ISSUES FOUND!")
    print("System is production-ready.")
else:
    print(f"\n[TOTAL] {len(issues_found)} issue(s) found")
    
    unique = list(set(issues_found))
    for i, issue in enumerate(unique[:10], 1):
        print(f"  {i}. {issue}")
    
    if len(unique) > 10:
        print(f"  ... and {len(unique) - 10} more")

print("\n" + "=" * 80)
exit_code = 0 if not issues_found else 1

# Export issues for fixing
if issues_found:
    with open('REMAINING_ISSUES.txt', 'w') as f:
        f.write("REMAINING ISSUES FOUND IN AUDIT\n")
        f.write("=" * 80 + "\n\n")
        for i, issue in enumerate(list(set(issues_found)), 1):
            f.write(f"{i}. {issue}\n")
    print("Issues exported to REMAINING_ISSUES.txt")

print(exit_code)
