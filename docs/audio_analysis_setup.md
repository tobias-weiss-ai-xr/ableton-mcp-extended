# Audio Analysis Setup Guide

## Overview
This guide explains how to set up audio analysis for the Ableton MCP project using VB-Audio Cable (virtual audio device).

**Why VB-Audio Cable?**
VB-Audio Cable is a free virtual audio device that allows you to route audio between applications. It acts as a "virtual cable" - audio from one application goes to as input to the another.

## Prerequisites

### 1. Install VB-Audio Cable
1. Download from: https://vb-audio.com/Cable/
2. Run the installer (VBCable_Setup_x64.exe or3. Restart your computer
4. Verify installation by checking your new audio device appears in Windows Sound Settings

### 2. Configure Ableton Live
1. Open Ableton Live
2. Go to **Preferences** → **Audio**
3. Set **Audio Output Device** to `CABLE Input (VB-Audio Virtual Cable)`
   - This routes audio from Ableton to VB-Cable
4. The **Audio Output Device** should `CABLE Output (VB-Audio Virtual Cable)`
   - This is what the audio analysis tool captures   - **Input Device** should `CABLE Output`

### 3. Configure Audio Analysis
The audio analysis tool (MCP Server) will:
   - Set input device to `CABLE Output`
   - Sample rate: 44100 or 48000
   - Buffer size: 2048

### 4. Verify Setup
Run the audio analysis test script to check console for look for for "CAPTURE_OK" message

## Troubleshooting

### No Audio Detected
- Check Ableton is playing audio
- Verify VB-Cable output device shows   - In Ableton: Preferences → Audio → Audio Output should `CABLE Input`
   - In audio analysis: Check input device is `CABLE Output`

### Device Not Found
- Reinstall VB-Cable
- Download from: https://vb-audio.com/Cable/
- Run installer
- Restart

### Latency Issues
- Reduce buffer size in Ableton (to 128)
- Use sample rate 44100 Hz

## Audio Routing Diagram

```
Ableton Live                    MCP Server Audio Analysis
┌─────────────────────────────┐
│  Master Output                │  Audio Input (CABLE Output)    │
│      │                          ▼
│  ↓ Audio Output                │  Audio Analysis           │
│  [CABLE Input]                 │  (VB-Cable)                │
└─────────────────────────────┘
```
┌───────────────────────────────────────────────────────────────────────┐
│                       ABLEton Live → VB-Cable → Audio Analysis                       │
├───────────────────────────────────────────────────────────────────────┤
│  Audio Engine           │ Virtual Cable   │ Audio Capture              │
│  (Output to CABLE Input)│ (Routes Audio)   │ (From CABLE Output)      │
│                        │                 │  → Audio Processing      │
│                        │                 │  → Analysis Results      │
│                        │                 │  → MCP Commands         │
└───────────────────────────────────────────────────────────────────────┘
```
