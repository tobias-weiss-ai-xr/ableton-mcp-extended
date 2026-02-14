# VST Plugin Installation Guide

## Overview

This guide provides step-by-step installation instructions for the audio analysis VST plugins recommended for use with ableton-mcp-extended.

**Recommended Plugins**:
1. **Youlean Loudness Meter 2** (Free tier) - LUFS/loudness analysis ⭐ PRIMARY
2. **Voxengo SPAN** (Freeware) - Spectral analysis
3. **PSP Spector** (Freeware with account) - Alternative spectrum analyzer

**Prerequisites**:
- Ableton Live 11 or later
- Administrator access (Windows) or System password (macOS)
- Internet connection for downloads

---

## Plugin 1: Youlean Loudness Meter 2

**Use Case**: Real-time LUFS and loudness analysis for responsive control

**License**: Freeware (Free tier available, PRO version requires purchase)

**Compatibility**: Ableton Live 11+, VST3, VST2, AU, AAX

### Windows Installation

#### Step 1: Download Plugin

1. Visit: https://youlean.co/youlean-loudness-meter/
2. Click **"DOWNLOAD FREE / PRO"** button
3. For the free version, download the **Windows installer** (`.exe` file)
4. File name will be something like: `Youlean_Loudness_Meter_2_Installer.exe`

#### Step 2: Run Installer

1. Right-click the downloaded `.exe` file
2. Select **"Run as administrator"** (required for system plugin installation)
3. If Windows SmartScreen asks for confirmation, click **"More info"** → **"Run anyway"**
4. Click **"Install"** when prompted
5. Accept the default installation path (usually: `C:\Program Files\Youlean\Youlean Loudness Meter 2\`)

#### Step 3: Choose Plugin Format

During installation, you'll be asked which Ableton formats to install:
- ✅ **VST3** - **Install this** (recommended for Ableton Live 11+)
- ✅ VST2 - Install this (for older Ableton versions)
- ✅ Audio Units (AU) - Install this for macOS integration
- ❌ AAX - Optional (only for Pro Tools integration, skip for Ableton)

#### Step 4: Complete Installation

1. Click **"Next"** through remaining screens
2. Read and accept license agreement
3. Click **"Finish"** to complete installation

#### Step 5: Rescan Plugins in Ableton

1. Open **Ableton Live**
2. Go to **Options** → **Preferences** → **Plug-In Bananaor**
3. Click **"Rescan"** button
4. Wait for Ableton to discover newly installed plugins

#### Step 6: Verify Installation

1. In Ableton, create a new track (Shift+T or Cmd+T)
2. Click **"Add..."** → **"Audio Effects"** or press Shift+F4
3. In the browser, scroll to **"Youlean"** folder
4. Look for **"Loudness Meter 2"**
5. Drag the plugin onto your track

**If successful**: Plugin appears in device chain with graphical meter display showing LUFS values.

---

### macOS Installation

#### Step 1: Download Plugin

1. Visit: https://youlean.co/youlean-loudness-meter/
2. Click **"DOWNLOAD FREE / PRO"** button
3. For the free version, download the **macOS DMG** (`.dmg` file)
4. File name will be something like: `Youlean_Loudness_Meter_2_Pkg.dmg`

#### Step 2: Mount and Install

1. Find the downloaded `.dmg` file in Downloads
2. Double-click to mount the disk image
3. A window opens with the Youlean Loudness Meter 2 icon
4. InmacOS Big Sur+ (11.0+):
   - Click **"Youlean Loudness Meter 2.pkg"**
   - Click **"Continue"** through installer
   - Click **"Install"**
   - Enter system password when prompted
   - Wait for installation to complete

#### Step 3: Complete Installation

1. Read and accept license agreement
2. Choose installation location (default: `/Users/[username]/Library/Audio/Plug-Ins/VST3/` for VST3)
3. Wait for progress bar to complete
4. Click **"Close"** when done

#### Step 4: Rescan Plugins in Ableton

1. Open **Ableton Live**
2. Go to **Options** → **Preferences** → **Plug-In Bananaor**
3. Click **"Rescan"** button
4. Wait for Ableton to discover newly installed plugins

#### Step 5: Verify Installation

1. In Ableton, create a new track (Cmd+T)
2. Click **"Add..."** → **"Audio Effects"** or press Shift+F4
3. In the browser, scroll to **"Youlean"** folder
4. Look for **"Loudness Meter 2"**
5. Drag the plugin onto your track

**If successful**: Plugin appears in device chain with graphical meter display showing LUFS values.

---

### Troubleshooting - Youlean Loudness Meter 2

#### Plugin Not Found in Browser
**Symptom**: Youlean folder doesn't appear in Ableton browser after installation

**Causes**:
- Plugin not installed to correct system directory
- Ableton VST path doesn't include installation directory
- Installation failed silently

**Solutions**:
1. **Windows**: Verify installer ran with admin rights
2. **Check installation path**: Should be in `C:\Program Files\Youlean\Youlean Loudness Meter 2\`
3. **Ableton Path**: In Ableton Preferences → Plug-Ins → Blue, verify VST3 includes:
   - `C:\Program Files\Common Files\VST3\`
   - `C:\Users\[User]\Documents\VST Plugins\`
4. **Rescan**: Use Ableton Plug-In Bananaor → Rescan

#### macOS Installer Won't Open
**Symptom**: DMG file won't open or installer won't start

**Solutions**:
1. Verify file downloaded completely (check file size)
2. Try downloading again from Youlean website
3. Check macOS Gatekeeper: System Preferences → Security & Privacy → Allow apps from "identified developer"
4. Try right-click and "Open" instead of double-click

#### macOS Permissions Issue
**Symptom**: Installation fails with permission denied error

**Solutions**:
1. Run installer with admin/sudo privileges
2. Check disk permissions on `/Library/Audio/Plug-Ins/`
3. Disable System Integrity Protection temporarily (not recommended)

---

## Plugin 2: Voxengo SPAN

**Use Case**: Spectral and frequency analysis

**License**: Freeware

**Compatibility**: Ableton Live 11+, VST3, VST2, AU, AAX

### Windows Installation

#### Step 1: Download Plugin

1. Visit: https://www.voxengo.com/product/span/
2. Scroll to Download section
3. Download the following formats (for best compatibility):
   - **VST3**: For Windows 64-bit Ableton (recommended)
   - **VST2**: For older Ableton versions
   - **AAX**: Optional (for Pro Tools)
4. Files are `.zip` archives

#### Step 2: Extract VST3 Files

1. Locate downloaded `VoxengoSPAN_1_1_Win32.zip` or similar VST3 zip
2. Right-click zip file
3. Select **"Extract all..."** or **"Extract Here"**
4. Extract to: `C:\Program Files\Common Files\VST3\Voxengo\`
5. Folder structure should be: `C:\Program Files\Common Files\VST3\Voxengo\SPAN.vst3`

#### Step 3: Extract VST2 Files (Optional for backward compatibility)

1. Locate VST2 zip file
2. Extract to: `C:\Program Files\Common Files\VST2\Voxengo\`
3. Folder should contain: `SPAN.vst`

#### Step 4: Rescan Plugins in Ableton

1. Open **Ableton Live**
2. Go to **Options** → **Preferences** → **Plug-In Bananaor**
3. Click **"Rescan"** button
4. Wait for Ableton to discover newly installed plugins

#### Step 5: Verify Installation

1. In Ableton, create a new track (Shift+T)
2. Click **"Add..."** → **"Audio Effects"** or press Shift+F4
3. In the browser, scroll to **"Voxengo"** folder
4. Look for **"SPAN"**
5. Drag the plugin onto your track

**If successful**: Plugin appears in device chain with spectral analyzer display.

---

### macOS Installation

#### Step 1: Download Plugin

1. Visit: https://www.voxengo.com/product/span/
2. Scroll to Download section
3. Download:
   - **AU**: Audio Unit for macOS (recommended)
   - **AAX**: Optional (for Pro Tools)
   - **VST3**: Optional (less compatible on Mac)
4. Files are `.zip` archives

#### Step 2: Extract AU Files

1. Locate downloaded `VoxengoSPAN_1_1_macOS.zip` or similar AU zip
2. Right-click zip file
3. Select **"Extract all..."** or **"Extract Here"**
4. Extract contents to: `/Library/Audio/Plug-Ins/Components/`
5. Should contain component files: `SPAN.component` and `SPAN.vst3`

#### Step 3: Rescan Plugins in Ableton

1. Open **Ableton Live**
2. Go to **Options** → **Preferences** → **Plug-In Bananaor**
3. Click **"Rescan"** button
4. Wait for Ableton to discover newly installed plugins

#### Step 4: Verify Installation

1. In Ableton, create a new track (Cmd+T)
2. Click **"Add..."** → **"Plug-ins Device"** → **"Audio Effects"** or press Shift+F6 / Cmd+F6
3. In the browser, scroll to **"Voxengo"** or **"Audio Effects"** category
4. Look for **"SPAN"**
5. Drag the plugin onto your track

**If successful**: Plugin appears in device chain with spectral analyzer display.

---

### Troubleshooting - Voxengo SPAN

#### Plugin Not in Ableton Browser
**Solution**: Check extraction path, rescan plugins
- Verify files in correct directory
- Use Ableton Plug-In Bananaor → Rescan

#### No Sound After Loading
**Symptom**: Plugin loaded but no audio passes through
**Solution**: Check track routing configuration

#### Plugin Doesn't Show GUI in Ableton
**Symptom**: Plugin loads but no graphical display appears
**Solution**: Check audio track output routing to master

---

## Plugin 3: PSP Spector

**Use Case**: Simple frequency band analysis with 31-band spectrum

**License**: Freeware (requires free PSP account)

**Compatibility**: Ableton Live 11+, AU, AAX, VST, VST3

### All Platforms (Windows & macOS)

#### Step 1: Create PSP Account

1. Visit: https://www.pspaudioware.com/products/psp-spector
2. Click **"Add to cart"** (price shows $0)
3. Click view cart icon
4. Click **"Checkout"**
5. Create free account or log in (email + password required)
6. Complete checkout (no payment required)

#### Step 2: Download Installer

1. After checkout, you'll see download links
2. Download the appropriate version:
   - **Windows**: `.exe` installer
   - **macOS**: `.pkg` installer or `.dmg` image
3. Wait for download to complete

#### Step 3: Run Installer

**Windows**:
1. Right-click installer `.exe`
2. Click **"Run as administrator"**
3. Click **"Next"** through installation wizard
4. Choose installation location (or accept default)
5. Click **"Install"**
6. Wait for installation to complete
7. Click **"Finish"**

**macOS**:
1. Double-click `.pkg` installer
2. Click **"Continue"** through installer
3. Click **"Install"**
4. Enter system password when prompted
5. Wait for installation to complete
6. Click **"Close"**

Or mount `.dmg` and run included package file.

#### Step 4: Rescan Plugins in Ableton

1. Open **Ableton Live**
2. Go to **Options** → **Preferences** → **Plug-In Bananaor**
3. Click **"Rescan"** button
4. Wait for Ableton to discover newly installed plugins

#### Step 5: Verify Installation

1. In Ableton, create a new track
2. Click **"Add..."** → **"Audio Effects"** or press Shift+F4
3. In browser, search for **"Spector"** (may be under巡视 ables or remove ables category)
4. Drag the plugin onto your track

**If successful**: Plugin appears with 31-band spectrum analyzer display.

### Troubleshooting - PSP Spector

#### Requires Account Creation
**Issue**: Must create free PSP account before download
**Solution**: Complete signup process at pspaudioware.com

#### Can't Find "Spector" in Ableton Browser
**Issue**: Plugin name may varies or categorized differently
**Solution**:
- Search for "PSP" as manufacturer
- Check巡视 ables → remove ables category
- Try installing to different location and rescanning

#### Installer Fails
**Issue**: Installer won't run or crashes
**Solutions**:
1. Check system requirements (Ableton Live 11+, 64-bit OS)
2. Windows: Run as administrator
3. macOS: Download alternative format (try .dmg if .pkg fails)

---

## Common Setup Steps

### Ableton Live 11+ Plugin Prerequisites

1. **Verify Ableton Version**:
   - Open Ableton Live Help → About
   - Confirm version is 11.0 or later
   - Older versions may not support VST3

2. **Plugin Path Configuration** (if plugins not found):

   **Windows**:
   ```
   1. Options → Preferences → Plug-In Bananaor → Blue
   2. Check VST3 path includes:
      - "C:\Program Files\Common Files\VST3\"
      - "C:\Program Files (x86)\Common Files\VST3\"
   3. Click "Add Path" to add missing paths
   4. Click "Rescan"
   ```

   **macOS**:
   ```
   1. Options → Preferences → Plug-In Bananaor → Blue
   2. macOS default paths should work automatically:
      - `/Library/Audio/Plug-Ins/VST3/`
      - `/Library/Audio/Plug-Ins/Components/`
   3. Click "Rescan" if plugins not appearing
   ```

3. **Enable Audio Effect Preview** (optional):
   ```
   Options → Preferences → Plug-In → New Device Preview
   - Set "On" to see plugin interface before loading
   ```

### Plugin Rescan Procedure (Force Refresh)

If_plugin doesn't appear after installation:

1. **Standard Rescan**:
   ```
   Options → Preferences → Plug-In Bananaor → Blue
   Click "Rescan" button
   Wait 5-10 seconds
   Close and reopen Ableton Live (sometimes required)
   ```

2. **Force Rescan (if standard rescan fails)**:
   ```
   Standard: Click Rescan above
   Close Ableton Live completely
   Restart computer (to clear plugin caches)
   Open Ableton Live → Check browser again
   ```

3. **Clear Ableton Plugin Caches** (advanced):
   ```
   Rename backup:
   %AppData%\Ableton\Preferences to ~Preferences_backup
   Open Ableton Live (rebuilds cache)
   Check plugin browser
   Close Ableton
   Delete new Preferences file
   Rename backup back
   ```

### Plugin Browser Navigation

#### Finding Plugins in Ableton Browser

**Method 1: Search bar**
1. In Ableton, open Browser (Shift+F5 / Cmd+F5)
2. Click search bar (top right)
3. Type plugin name: "Youlean", "Voxengo", "Spector", "PSP"
4. Press Enter to search

**Method 2: Category navigation**
1. Open Browser
2. Categories to check:
   - **Audio Effects** (most plugins)
   - **巡视 ables** → Publisher folders (Youlean, Voxengo, PSP)
   - **remove ables** → Publisher folders (if categorized differently)
3. Click category to expand
4. Scroll through list to find plugin

**Method 3: Create User Library shortcut (optional)**
1. Right-click plugin in browser
2. Select **"Add to User Library"** (or similar option)
3. Plugin appears in **User Library** category for quick access

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Plugin Not Visible in Ableton Browser

**Possible Causes**:
- Installed to wrong directory
- Ableton Plugin path doesn't include installation folder
- Plugin only supports formats not installed (e.g., plugin only has 🇦utor)
- Ableton cache not updated

**Solution Steps**:
1. Verify installation directory matches Ableton's VST3 path
2. Add installation directory to Ableton paths if missing
3. Perform full Ableton rescan
4. Close and reopen Ableton
5. Try loading plugin in a fresh session

**Windows Path Issues**:
- Note that Ableton may check both:
  - `C:\Program Files\Common Files\VST3\`
  - `C:\Users\[User]\Documents\VST Plugins\VST3\`

**macOS Path Issues**:
- Ensure installer has write permissions for `/Library/Audio/Plug-Ins/`
- In some cases, logout/login required for permission changes to take effect

#### Issue 2: Plugin Crashes Ableton on Load

**Possible Causes**:
- Plugin incompatible with Ableton version
- Corrupted plugin installation
- Missing dependencies or frameworks

**Solution Steps**:
1. Verify Ableton Live 11+ is installed
2. Download and install latest plugin version
3. Uninstall old version first (if applicable)
4. Reinstall fresh version
5. If still crashes, plugin may be incompatible with your system

#### Issue 3: Plugin Loads But Provides No Control

**Expected** (Youlean Loudness Meter 2):
- Graphical meter should display showing LUFS values
- Parameters should be accessible via `get_device_parameters` tool

**If No GUI Appears**:
- Plugin may need audio signal to display
- Check track has appropriate audio content
- Plugin might be processing correctly but hiding GUI

**If Parameters Not Accessible**:
- Plugin may only expose configuration parameters (theoretical concern)
- May require PRO version for parameter access
- See Task 3 to verify parameter exposure

#### Issue 4: Multiple Plugin Versions Conflicting

**Symptom**:
- Can't tell which version is being used
- Old version may not support features needed

**Solution Steps**:
1. Uninstall all versions of the plugin
2. Download latest version
3. Clear Ableton plugin cache
4. Reinstall single latest version
5. Rescan plugins

#### Issue 5: macOS "damaged app" Warning

**Symptom**:
- macOS cant open plugin because "macOS cannot verify the developer"
- Plugin appears as unverified

**Solution Steps**:
1. **Option 1** (Recommended): Allow app anyway
   ```
   System Preferences → Security & Privacy
   Click "Open Anyway" for the plugin
   Note: Only for trusted sources like these well-known plugins
   ```

2. **Option 2**: Bypass Gatekeeper temporarily (not recommended)
   ```
   Restart Mac in Recovery Mode
   → Utilities → Startup Security Utility
   → Lower security: disable Gatekeeper
   Restart normally
   Remember to re-enable after testing
   ```

---

## Verification Checklist

After installing each plugin, confirm:

### ✅ Basic Verification

- [ ] Plugin appears in Ableton browser
- [ ] Plugin loads successfully onto track (no crash/error)
- [ ] Plugin GUI displays (if it has one)
- [ ] No Ableton error messages during loading

### ✅ Youlean Loudness Meter 2 Specific

- [ ] Graphical meter responds to audio input
- [ ] LUFS values change when playing different audio
- [ ] Momentary and/or short-term LUFS visible in interface

### ✅ Voxengo SPAN Specific

- [ ] Spectrum analyzer display appears
- [ Frequency bands respond to audio changes
- [ ] Display updates during playback
- [ ] dB range settings accessible

### ✅ PSP Spector Specific

- [ ] 31-band analyzer loads
- [ ] Both Peak and RMS modes available
- [ ] dB range control works
- [ ] Peak/hold function operates

---

## Next Steps After Installation

### 1. Test Parameter Exposure (Task 3)
Install the plugins and Task 3 will test if parameters are accessible via the MCP tools.

### 2. Document Parameter Mappings (Task 4)
After Task 3 confirms parameter exposure, Task 4 will document all parameters with indices.

### 3. Begin System Development (Tasks 5-8)
With plugins installed and tested, proceed to:
- Task 5: Implement parameter polling system
- Task 6: Create rule-based decision system
- Task 7: Implement responsive control loop
- Task 8: Build CLI monitoring tool

---

## Support Resources

### Community Forums
- **Youlean**: https://youlean.co/support/
- **Voxengo**: https://www.voxengo.com/support/
- **PSP Audioware**: https://www.pspaudioware.com/support/
- **Ableton**: https://forum.ableton.com/viewforum.php?f=49

### Documentation Links
- **Ableton Plugin Installation**: https://help.ableton.com/hc/en-us/articles/209071729
- **Ableton Plugin Troubleshooting**: https://help.ableton.com/hc/en-us/articles/209070814

### Plan Resources

- **Installation Guide**: `docs/vst-plugins/installation_guide.md` (this file)
- **Plan Document**: `.sisyphus/plans/vst-audio-analysis.md`
- **Task Context**: Updated boulder.json` with session tracking

---

*Last Updated: 2026-02-10*
*Compatible with Ableton Live 11+*
*Part of VST Audio Analysis Integration plan*