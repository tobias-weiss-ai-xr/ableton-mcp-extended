# Arrangement & Song Structure Theory

> Comprehensive guide to song structure, arrangement techniques, and form in electronic music production.

---

## Overview

Arrangement is the art of organizing musical elements over time. Good arrangement keeps listeners engaged, creates emotional journeys, and ensures your track works on the dancefloor, in headphones, or in film/TV.

---

## Classic Song Structures

### Pop Structure (AABA)

```
Intro | Verse | Chorus | Verse | Chorus | Bridge | Chorus | Outro
  8    |  16   |   16   |  16   |   16   |   8    |   16   |   8
```

**Characteristics:**
- Most common in pop, rock, and EDM
- Clear verse-chorus distinction
- Bridge provides contrast before final chorus

### Electronic/Dance Structure

```
Intro | Build | Drop | Break | Build | Drop | Outro
 16   |   8   |  16  |   8   |   8   |  16  |   8
```

**Characteristics:**
- Optimized for DJ mixing (8/16 bar phrases)
- Intro/outro for beatmatching
- Multiple drops for dancefloor impact

### Through-Composed (Continuous Development)

```
Section 1 → Section 2 → Section 3 → ... → End
   32         32          32
```

**Characteristics:**
- Common in ambient, dub techno, progressive
- Constant evolution, no repetition
- Hypnotic, trance-inducing effect

---

## Section Types & Functions

### Intro (8-32 bars)

**Purpose:**
- Establish mood and tempo
- Provide DJ mix-in point
- Build anticipation

**Techniques:**
- Filtered drums
- Atmospheric pads
- Rhythmic elements entering one by one
- Kick drum after 4-8 bars

**Example (16-bar intro):**
```
Bars 1-4:   Atmosphere only (pads, FX)
Bars 5-8:   Add hi-hats and percussion
Bars 9-12:  Add snare/clap pattern
Bars 13-16: Add kick drum, filter opening
```

### Verse (8-16 bars)

**Purpose:**
- Tell the story (lyrical content)
- Build toward chorus
- Lower energy than chorus

**Techniques:**
- Sparse arrangement
- Focus on vocals/instruments
- Subtle harmonic movement

### Chorus/Hook (8-16 bars)

**Purpose:**
- Main melodic idea
- Highest energy section
- Memorable and repeatable

**Techniques:**
- Full arrangement
- Strong melodic hook
- Maximum impact

### Build/Riser (4-16 bars)

**Purpose:**
- Create tension before drop
- Signal energy shift
- Psychological preparation

**Techniques:**
- Rising pitch (snare roll, synth rise)
- Increasing density
- Opening filters
- White noise sweep
- Removing elements (reverse psychology)

**Build Formula:**
```python
# 8-bar build
bars 1-2:  Add snare roll (every 1/4 note)
bars 3-4:  Snare every 1/8, add riser synth
bars 5-6:  Snare every 1/16, filter open
bars 7-8:  All elements, pitch rise, silence last 1/4
```

### Drop (8-32 bars)

**Purpose:**
- Release of tension
- Main groove/energy
- Dancefloor peak

**Techniques:**
- Full bass and drums
- Main hook/riff
- Maximum impact
- Often first drop is simpler, second drop adds elements

### Break/Breakdown (8-16 bars)

**Purpose:**
- Remove drums/bass
- Create contrast
- Build anticipation for next drop

**Techniques:**
- Drums drop out
- Bass drops out
- Focus on melody/atmosphere
- Often introduces new melodic element

### Bridge (8 bars)

**Purpose:**
- Contrast before final chorus
- New harmonic/melodic material
- Break from repetition

**Techniques:**
- Different chord progression
- New melody
- Different rhythm
- Key change possible

### Outro (8-32 bars)

**Purpose:**
- DJ mix-out point
- Gradual energy decrease
- Clean ending

**Techniques:**
- Mirror intro (reverse)
- Elements removed one by one
- Filter closing
- Fade out option

---

## Energy Curve Design

### The Energy Arc

```
Energy
  ^
  |           Drop 2
  |          /\
  |         /  \
  |    Drop 1   \
  |      /\      \
  |     /  \      \
  |    /    \      \
  |   /      \      \
  |  /        \      \
  | /          \      \
  |/            \      \
  +-----------------------------> Time
   Intro Build Drop Break Build Drop Outro
```

### Energy Levels (0-10)

| Section | Energy | Elements |
|---------|--------|----------|
| Intro | 2-4 | Sparse, building |
| Verse | 4-6 | Moderate, focused |
| Build | 6-9 | Rising, tense |
| Drop | 9-10 | Maximum, full |
| Break | 3-5 | Atmospheric, minimal |
| Outro | 2-3 | Decreasing |

### Energy Management Techniques

**Increasing Energy:**
- Add elements (instruments, layers)
- Increase density (more notes, faster rhythm)
- Open filters (low-pass → open)
- Raise pitch (risers, snare pitch)
- Increase volume/layers

**Decreasing Energy:**
- Remove elements
- Decrease density
- Close filters
- Lower pitch
- Reduce layers

---

## Phrase Lengths & DJ Compatibility

### Standard Phrase Lengths

| Genre | Typical Phrase | Intro | Outro |
|-------|---------------|-------|-------|
| House | 8-16 bars | 32 bars | 32 bars |
| Techno | 8-16 bars | 32-64 bars | 32-64 bars |
| Dub Techno | 16-32 bars | 64+ bars | 64+ bars |
| Trance | 16-32 bars | 32-64 bars | 32-64 bars |
| Drum & Bass | 8-16 bars | 32 bars | 32 bars |
| Dubstep | 8 bars | 16-32 bars | 16-32 bars |

### 8-Bar Phrasing Rule

Most electronic music uses 8-bar phrases:
- Elements change every 8 bars
- DJ can predict when to mix
- Creates predictable structure for dancers

```
| 1 2 3 4 5 6 7 8 | 1 2 3 4 5 6 7 8 |
|   New element   |   New element   |
```

### 16-Bar Phrases

Longer phrases for progressive styles:
```
| 1-8: Setup    | 9-16: Development |
| 17-24: Peak   | 25-32: Transition |
```

---

## Arrangement Templates

### House Music (128 BPM, ~6 min)

```
Section    | Bars | Time   | Energy
-----------|------|--------|-------
Intro      | 32   | 1:00   | 3
Build 1    | 8    | 0:15   | 6
Drop 1     | 16   | 0:30   | 8
Break      | 16   | 0:30   | 4
Build 2    | 8    | 0:15   | 7
Drop 2     | 32   | 1:00   | 10
Break 2    | 8    | 0:15   | 5
Build 3    | 8    | 0:15   | 8
Drop 3     | 32   | 1:00   | 10
Outro      | 32   | 1:00   | 2
-----------|------|--------|-------
Total      | 192  | ~6:00  |
```

### Techno (130 BPM, ~7 min)

```
Section    | Bars | Time   | Energy
-----------|------|--------|-------
Intro      | 64   | 2:00   | 2-4
Development| 32   | 1:00   | 5-6
Peak 1     | 32   | 1:00   | 8
Break      | 16   | 0:30   | 4
Peak 2     | 48   | 1:30   | 9
Break 2    | 8    | 0:15   | 5
Peak 3     | 32   | 1:00   | 10
Outro      | 32   | 1:00   | 2
-----------|------|--------|-------
Total      | 264  | ~7:00  |
```

### Dub Techno (120 BPM, ~8 min)

```
Section    | Bars | Time   | Energy
-----------|------|--------|-------
Intro      | 64   | 2:08   | 2
Groove 1   | 64   | 2:08   | 5
Evolution  | 64   | 2:08   | 6-7
Peak       | 64   | 2:08   | 8
Wind Down  | 64   | 2:08   | 4-2
-----------|------|--------|-------
Total      | 320  | ~8:00  |
```

---

## Transition Techniques

### Between Sections

**Hard Cut:**
- Immediate change
- High impact
- Good for drops

**Crossfade:**
- Gradual transition
- Smooth flow
- Good for ambient/progressive

**Fill-Based:**
- Drum fill or FX before change
- Signals upcoming change
- Most common in electronic music

### Transition Lengths

| Transition Type | Length | Use Case |
|----------------|--------|----------|
| Instant | 0 beats | Drop impact |
| Quick | 1-2 beats | Section change |
| Standard | 1 bar | Most transitions |
| Extended | 2-4 bars | Major section change |
| Gradual | 4-8 bars | Ambient/progressive |

---

## Automation & Movement

### Types of Automation

**Filter Sweeps:**
- Low-pass: close → open (build energy)
- High-pass: introduce element gently
- Band-pass: create movement

**Volume Automation:**
- Fade in new elements
- Duck for sidechain
- Gradual builds

**Pan Automation:**
- Create width
- Movement interest
- Hypnotic effects

**FX Automation:**
- Reverb: dry → wet (space)
- Delay: feedback increase
- Distortion: clean → dirty

### Automation Curves

```
Linear:      /_____
Exponential: /~~~~~
Logarithmic: _____/
S-Curve:     ___/~
```

---

## Common Arrangement Mistakes

### 1. Static Arrangement
**Problem:** No changes for too long
**Fix:** Add/remove elements every 8 bars

### 2. Too Many Elements
**Problem:** Cluttered, no space
**Fix:** Less is more - mute tracks

### 3. Predictable Structure
**Problem:** Boring, obvious
**Fix:** Add surprises, unexpected changes

### 4. No Contrast
**Problem:** Same energy throughout
**Fix:** Create high/low energy sections

### 5. Weak Transitions
**Problem:** Abrupt, jarring changes
**Fix:** Use fills, FX, or gradual changes

---

## Arrangement Workflow

### Step-by-Step Process

1. **Create 8-bar loop** with all core elements
2. **Duplicate to full length** (128-256 bars)
3. **Mark sections** with locators
4. **Remove elements** from intro/breaks
5. **Add transitions** (fills, FX, automation)
6. **Automate energy** throughout
7. **Fine-tune** timing and flow

### Checklist

- [ ] Intro has mix-in point (kick on 1)
- [ ] Outro has mix-out point
- [ ] Energy has peaks and valleys
- [ ] Transitions are smooth
- [ ] Something changes every 8 bars
- [ ] Drop has impact
- [ ] Breakdown creates contrast
- [ ] Total length appropriate for genre

---

## MCP Integration Examples

### Create Arrangement Markers

```python
# Set locators for arrangement
set_locators(start_bar=0, end_bar=192)

# Create cue points for sections
create_cue_point(0, "Intro")
create_cue_point(32, "Build 1")
create_cue_point(40, "Drop 1")
create_cue_point(56, "Break")
create_cue_point(64, "Build 2")
create_cue_point(72, "Drop 2")
```

### Automate Energy Curve

```python
# Apply energy curve over 192 bars
apply_energy_curve(
    track_volumes=[
        {"track": 0, "start": 0.5, "peak": 0.9, "end": 0.3},  # Drums
        {"track": 1, "start": 0.0, "peak": 0.8, "end": 0.0},  # Bass
        {"track": 2, "start": 0.7, "peak": 0.9, "end": 0.5},  # Pad
    ],
    duration_bars=192
)
```

### Filter Build Automation

```python
# 8-bar filter build
apply_filter_buildup(
    track_index=2,
    device_index=0,
    start_value=0.1,  # Closed
    end_value=0.9,    # Open
    duration_bars=8
)
```

---

## Quick Reference Card

### Section Energy Levels

```
Intro:    ████░░░░░░  40%
Build:    ████████░░  80%
Drop:     ██████████  100%
Break:    ██░░░░░░░░  20%
Outro:    ███░░░░░░░  30%
```

### Bar Counts by Genre

| Genre | Intro | Drop | Break | Outro | Total |
|-------|-------|------|-------|-------|-------|
| House | 32 | 32 | 16 | 32 | 192 |
| Techno | 64 | 48 | 16 | 32 | 264 |
| Dub | 64 | 64 | 32 | 64 | 320 |
| Trance | 32 | 64 | 32 | 32 | 256 |
| DnB | 32 | 32 | 16 | 32 | 192 |

---

## Further Reading

- "The Art of Mixing" by David Gibson
- "Dance Music Manual" by Rick Snoman
- "Making Music" by Dennis DeSantis
- Ableton Learning Synths (ableton.com)

---

*Last updated: 2026-03-04*
