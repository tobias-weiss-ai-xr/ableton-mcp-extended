# Reggae Mix - Quick Start

> **Create Authentic Roots Reggae in Ableton with One Command**

---

## ⚡ **IN ONE COMMAND**

```bash
python scripts/production_pipeline.py reggae --mp3 --title "Roots Reggae Mix" --artist "Studio One Vibes"
```

---

## 📋 **MIX SPECS**

| Setting | Value |
|---------|-------|
| **Genre** | Reggae (Roots) |
| **BPM** | 80 |
| **Duration** | ~3.4 minutes (272 bars) |
| **Sections** | 9 |
| **Tracks** | 8 |
| **Style** | One Drop, Rockers, Dub |

---

## 🎯 **SECTIONS**

| Bars | Section | BPM | Energy | Style |
|------|---------|-----|---------|-------|
| 0-31 | One Drop Intro | 80 | 30% | Gentle intro |
| 32-63 | Rockers Groove | 80 | 50% | Main groove |
| 64-79 | Vocal Chant | 80 | 60% | Chorus |
| 80-111 | Dub Section Drop | 80 | 80% | Dub with echo |
| 112-143 | Roots Rockers Verse | 80 | 55% | Verse |
| 144-175 | Dub Echo Breakdown | 80 | 35% | Breakdown |
| 176-191 | Lion of Judah | 80 | 75% | Build |
| 192-239 | Babylon System Drop | 80 | 90% | Strong drop |
| 240-271 | Natural Mystic Outro | 80 | 20% | Fade out |

---

## 🎛️ **TRACKS**

| # | Name | Vol | Pan | Purpose |
|---|------|-----|-----|---------|
| 0 | Reggae Kick (One Drop) | -6dB | 0.0 | No kick on beat 1 |
| 1 | Sub Bass (Roots) | -4dB | 0.0 | Deep roots bass |
| 2 | Snare (Backbeat) | -5dB | -0.15 | Snare on 2 & 4 |
| 3 | Hi-Hats (Upbeat) | -8dB | +0.2 | Offbeat hi-hats |
| 4 | Guitar (Upstroke) | -9dB | -0.25 | Skank/chops |
| 5 | Keyboards/Organ | -10dB | +0.3 | Hammond chords |
| 6 | Dub Echo FX | -15dB | +0.4 | Echo sends |
| 7 | Reverb/Spring | -12dB | 0.0 | Spring reverb |

---

## 🎵 **ONE DROP RHYTHM**

```
Beat: 1     2     3     4
Kick: .     .     .     .
Snre:      X           X
Hats:   X     X     X
Guit: X     X     X     X (offbeats)
```
**Kick does NOT play on beat 1** (signature one drop)

---

## 🎶 **KEY REGGAE CHARACTERISTICS**

✅ **80 BPM** - Traditional reggae speed  
✅ **One Drop** - No kick on beat 1  
✅ **Skanking** - Guitar on offbeats  
✅ **Roots Bass** - Deep, syncopated bass  
✅ **Echo & Reverb** - Dub-style processing  
✅ **Cross-stick snares** - Backbeat emphasis  

---

## 🚀 **EXAMPLES**

### **Basic Setup**
```bash
python scripts/production_pipeline.py reggae
```

### **With MP3**
```bash
python scripts/production_pipeline.py reggae --mp3
```

### **With MP3 & Video**
```bash
python scripts/production_pipeline.py reggae --mp3 --video \
    --title "Roots Reggae Mix" --artist "Studio One Vibes"
```

### **Full Workflow**
```bash
python scripts/production_pipeline.py reggae --mp3 --video --youtube \
    --title "Roots Reggae Mix - July 2026" \
    --artist "Jah Love" \
    --description "Authentic roots reggae mix"
```

---

## 📂 **SCENE CONFIGURATION**

### **Scene 0: Intro/Outro**
- Sub Bass: Simple roots
- Guitar: Gentle upstrokes
- Reverb: Ambient

### **Scene 1: Verse (Main Groove)**
- Kick: No kick on 1
- Snare: Backbeats (2 & 4)
- Hi-Hats: Offbeats
- Guitar: Skank (offbeats)
- Organ: Chord stabs

### **Scene 2: Chorus**
- All from Scene 1 +
- More active organ fills
- Busier guitar
- Open hi-hats

### **Scene 3: Dub Drop**
- All from Scene 2 +
- Heavier bass
- Dub echo sends (60-80% feedback)
- Long reverb tails
- Dub filtered chords

### **Scene 4: Breakdown**
- Guitar: Minimal with heavy echo
- Reverb: Ambient wash
- Echo: Echo effects

---

## 🎚️ **PRODUCTION TIPS**

### **Bass**
- Keep it simple (roots + 5th)
- Mix sine wave below 50Hz with bass
- Sidechain to kick
- EQ: Boost 80-100Hz, cut 200-300Hz

### **Guitar**
- Play on offbeats (between beats)
- Use palm muting for bite
- Add chorus for motion
- Use triads (no thirds for roots feel)

### **Organ**
- Use Leslie rotary effect
- Play triads on offbeats
- Create fill patterns
- Warm analog sound

### **Drums**
- One Drop: No kick on beat 1
- Snare: Tight with room reverb
- Hi-Hats: Offbeats
- Add percussion (timbales, guiro)

### **Dub Effects**
- Echo: 1/4 or 1/8 note, 60-80% feedback
- Reverb: Spring on drums, room on others
- Use bus sends for dub processing

---

## ✅ **FINAL CHECKLIST**

- [ ] Tempo set to 80 BPM
- [ ] One Drop rhythm (no kick on 1)
- [ ] Sub bass in place
- [ ] Guitar skanking on offbeats
- [ ] Organ chord stabs
- [ ] Dub echo and reverb
- [ ] Tracks at appropriate volumes
- [ ] Master at -6dB or lower
- [ ] No clipping
- [ ] Export test mix

---

## 📚 **MORE INFO**

- **[REGGAE_MIX_GUIDE.md](REGGAE_MIX_GUIDE.md)** - Complete guide (10KB)
- **[PIPELINEREADME.md](PIPELINEREADME.md)** - Pipeline workflow
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command reference

---

## 🎯 **READY TO PRODUCE?**

```bash
python scripts/production_pipeline.py reggae --mp3 --title "Roots Reggae Mix" --artist "Studio One Vibes"
```

Ableton will be set up with:
- ✅ 8 reggae tracks with appropriate names
- ✅ 9 authentic sections
- ✅ 80 BPM tempo
- ✅ Volumes and panning configured
- ✅ Ready for your creative content!

---

## 🎉 **GO PRODUCE YOUR REGGAE MIX!** 🎵🇯🇲

---

**Version**: 1.0  
**Status**: PRODUCTION READY ✅  
**BPM**: 80  
**Duration**: ~3.4 minutes
