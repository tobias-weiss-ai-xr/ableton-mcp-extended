# DUB TECHNO 2H KNOWLEDGE

**Parent:** ../AGENTS.md
**Purpose:** 2-hour automated dub techno track generation

## OVERVIEW
Complete automation system creating 12-track dub techno composition with 48 MIDI clips over 120 minutes.

## STRUCTURE
```
dub_techno_2h/
├── create_2h_dub_techno_fixed.py    # Track/clip creation (1,934 lines)
├── load_instruments_and_effects.py   # Instrument/effect configuration (1,484 lines)
├── auto_play_2h_dub_techno.py      # Full automation orchestrator (1,394 lines)
├── automate_all_setup.py            # All-in-one setup script
├── archive/                          # Legacy/deprecated versions
├── DUB_TECHNO_2H*.md             # Documentation files (5 files)
└── README.md                         # Quick start guide
```

## WHERE TO LOOK
| Task                    | Location                               |
|-------------------------|----------------------------------------|
| Track/clip creation  | create_2h_dub_techno_fixed.py       |
| Instrument setup     | load_instruments_and_effects.py        |
| Automation execution  | auto_play_2h_dub_techno.py         |
| Documentation        | DUB_TECHNO_2H_*.md               |

## TRACK STRUCTURE (12 tracks)
| Track | Type     | Role                           |
|-------|----------|--------------------------------|
| 4-11  | MIDI     | Kick, Sub-bass, Hi-hats, Synth Pads, FX |
| 12    | Audio    | Dub Delays (send returns)          |
| 13    | Audio    | Reverb Send (send returns)         |

## SECTION STRUCTURE (30 sections, 4 minutes each)
1-8:  Introduction, Hypnotic, First Build, Breakdown
9-16: Second Build, Journey, Final Push, Wind Down

## CONVENTIONS
- **Timer-based progression**: Scene triggers every 4 minutes (240 beats at 126 BPM)
- **dB input**: Track volumes specified in dB, auto-converted to normalized values
- **Filter automation**: 400-2000 Hz sweeps on synth pads (Track 7)
- **Error recovery**: Continues despite parameter set failures
- **Progress tracking**: Visual bar `[====----] XX%` and elapsed time

## AUTOMATION FEATURES
- ✅ Automatic scene progression
- ✅ Filter frequency sweeps
- ✅ Section-based volume changes
- ✅ Progress tracking with visual feedback
- ✅ Graceful stopping (Ctrl+C)

## MANUAL SETUP REQUIRED
- Instrument presets (choose sounds in Ableton UI)
- Send routing (configure in Ableton mixer)
- Effect parameters (reverb, delay - tune for best results)
- Initial mix levels

## ANTI-PATTERNS
- DO NOT assume instruments are loaded → scripts create tracks/clips only
- DO NOT skip manual setup → results will be poor without it
- DO NOT ignore error messages → they indicate configuration issues

## WORKFLOW
1. `python create_2h_dub_techno_fixed.py` - Create 48 clips across 12 tracks
2. Manual setup (30-40 min) - Load instruments, effects, configure sends, set levels
3. `python load_instruments_and_effects.py` - Apply instrument/effect configurations
4. `python auto_play_2h_dub_techno.py` - Run full 2-hour automation

## DOCUMENTATION FILES
- `DUB_TECHNO_2H_COMPLETE_GUIDE.md` - Configuration guide
- `DUB_TECHNO_2H_COMPLETE_SUMMARY.md` - Complete summary
- `DUB_TECHNO_2H_AUTOMATION_DOCS.md` - Automation features
