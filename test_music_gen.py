from MCP_Server.music_generation import PMarkov, PatternEvolution, ClipGenerator, GenerationPipeline, Scale, ScaleType

print("All imports OK")

# Test PMarkov
p = PMarkov(PMarkov.create_diatonic_transitions(ScaleType.MINOR), Scale(60, ScaleType.MINOR))
notes = p.generate(8)
print(f"PMarkov: {len(notes)} notes generated, pitches {notes[:4]}...")

# Test ClipGenerator Markov
gen = ClipGenerator(126, 64)
gen.add_markov_melody(16, 85, 1, 0, ScaleType.DORIAN)
print(f"add_markov_melody: {len(gen.notes)} notes")

# Test evolving pattern
gen2 = ClipGenerator(126, 64)
gen2.add_evolving_pattern("euclidean", 2, 8, 36, 110, "exponential")
print(f"add_evolving_pattern: {len(gen2.notes)} notes")

# Test dub_techno_session with build scene (uses new features)
result = GenerationPipeline.dub_techno_session(scene="build", length_bars=4)
print(f"dub_techno_session(build): {len(result['melody'])} melody notes, {len(result['kick'])} kick notes")

print("\nAll tests passed!")