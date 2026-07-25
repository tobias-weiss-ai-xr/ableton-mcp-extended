"""
8-track live set with 16-bar clips, per-track effects chains, return tracks, and master FX.

Usage:
    python scripts/build_live_set.py
"""
import sys, time, random, math
sys.path.insert(0, r'C:\Users\Tobias\git\ableton-mcp-extended')
from MCP_Server.server import create_drum_pattern, create_chord_notes
from agentic_mix.tools import _client
random.seed(42)

def tcp(cmd, params=None):
    return _client.tcp_command(cmd, params or {})

def load(track, uri):
    tcp("load_browser_item", {"track_index": track, "item_uri": uri})

def log(msg): print("[BUILD] {}".format(msg))

def clean_extra(max_idx=8):
    tracks = tcp("get_all_tracks").get('result', {}).get('tracks', [])
    for t in sorted(tracks, key=lambda x: x.get('index'), reverse=True):
        if t.get('index', 0) >= max_idx:
            tcp("delete_track", {"track_index": t.get('index')})
            time.sleep(0.15)

# ---- Reset ----
tcp("delete_all_tracks")
time.sleep(1)

# ---- Return tracks ----
for r in range(2):
    tcp("create_return_track", {"index": r}); time.sleep(0.2)
load(0, "query:AudioFx#Hybrid%20Reverb"); time.sleep(0.3)
tcp("set_track_name", {"track_index": -1, "name": "Reverb"}); time.sleep(0.1)
tcp("create_return_track", {"index": 0}); time.sleep(0.2)
load(0, "query:AudioFx#Delay"); time.sleep(0.3)
tcp("set_track_name", {"track_index": -1, "name": "Delay"}); time.sleep(0.1)

rt = tcp("get_return_tracks").get('result', {}).get('return_tracks', [])
reverb_idx = None; delay_idx = None
for r in rt:
    if 'Reverb' in r.get('name',''): reverb_idx = r.get('index')
    if 'Delay' in r.get('name',''): delay_idx = r.get('index')

# ---- 8 MIDI tracks ----
names = ["Drums", "Bass", "Chords", "Lead", "FX", "Percussion", "Strings", "Arp"]
for i in range(8):
    tcp("create_midi_track", {"index": i}); time.sleep(0.3)
for i, n in enumerate(names):
    tcp("set_track_name", {"track_index": i, "name": n}); time.sleep(0.05)

tcp("set_tempo", {"tempo": 128})
tcp("set_master_volume", {"volume": 0.82})
time.sleep(0.2)

# ---- Instruments ----
log("Loading instruments...")
instr = [
    (0, "query:Drums#FileId_58622"),
    (1, "query:Sounds#Bass:FileId_49654"),
    (2, "query:Sounds#Pad:FileId_45564"),
    (3, "query:Sounds#Synth%20Lead:FileId_50175"),
    (5, "query:Drums#FileId_58623"),
    (6, "query:Sounds#Pad:FileId_45564"),
    (7, "query:Sounds#Synth%20Lead:FileId_50175"),
]
for idx, uri in instr:
    load(idx, uri); time.sleep(0.5); clean_extra(8)
for fx_uri in ["query:AudioFx#Hybrid%20Reverb", "query:AudioFx#Delay", "query:AudioFx#Auto%20Filter"]:
    load(4, fx_uri); time.sleep(0.3)
clean_extra(8)

# ---- Per-track effects ----
log("Loading effects...")
effects_chain = {
    0: ["query:AudioFx#Drum%20Buss", "query:AudioFx#Glue%20Compressor", "query:AudioFx#EQ%20Eight"],
    1: ["query:AudioFx#Glue%20Compressor", "query:AudioFx#Saturator", "query:AudioFx#EQ%20Three"],
    2: ["query:AudioFx#Chorus-Ensemble", "query:AudioFx#Convolution%20Reverb%20Pro"],
    3: ["query:AudioFx#Echo", "query:AudioFx#Auto%20Filter", "query:AudioFx#Reverb"],
    4: ["query:AudioFx#Spectral%20Resonator"],
    5: ["query:AudioFx#Compressor", "query:AudioFx#EQ%20Eight", "query:AudioFx#Gate"],
    6: ["query:AudioFx#Chorus-Ensemble", "query:AudioFx#Convolution%20Reverb%20Pro", "query:AudioFx#Auto%20Filter"],
    7: ["query:AudioFx#Delay", "query:AudioFx#Reverb", "query:AudioFx#Beat%20Repeat"],
}
for track_idx, uris in effects_chain.items():
    for uri in uris:
        load(track_idx, uri); time.sleep(0.3); clean_extra(8)
for i, n in enumerate(names):
    tcp("set_track_name", {"track_index": i, "name": n}); time.sleep(0.05)

# ---- Sends ----
if reverb_idx is not None:
    for t in [0,5]: _client.udp_command("set_send_amount", {"track_index":t,"send_index":reverb_idx,"amount":0.15})
    for t in [2,6]: _client.udp_command("set_send_amount", {"track_index":t,"send_index":reverb_idx,"amount":0.28})
    for t in [3,7]: _client.udp_command("set_send_amount", {"track_index":t,"send_index":reverb_idx,"amount":0.22})
if delay_idx is not None:
    _client.udp_command("set_send_amount", {"track_index":3,"send_index":delay_idx,"amount":0.30})
    _client.udp_command("set_send_amount", {"track_index":7,"send_index":delay_idx,"amount":0.20})

# ---- Master FX ----
log("Master FX...")
load(-1, "query:AudioFx#Glue%20Compressor"); time.sleep(0.3); clean_extra(8)
load(-1, "query:AudioFx#Limiter"); time.sleep(0.3); clean_extra(8)

# ---- Scenes ----
scene_names = ["Intro", "Groove", "Build", "Drop", "Breakdown", "Bridge"]
for i, name in enumerate(scene_names):
    tcp("create_scene", {"index": i})
    tcp("set_scene_name", {"scene_index": i, "name": name}); time.sleep(0.1)
for s in range(37, 6, -1):
    tcp("delete_scene", {"scene_index": s}); time.sleep(0.02)

BARS = 16; BEATS = BARS * 4

# ---- Track 0: Drums ----
log("Track 0: Drums...")
for si, pat in enumerate(["house_basic","techno_4x4","techno_4x4","house_basic","dub_techno","rockers"]):
    create_drum_pattern(ctx=None, track_index=0, clip_index=si,
                         pattern_name=pat, length=BARS,
                         kick_note=36, snare_note=38, hat_note=42, clap_note=39)
    time.sleep(0.2)

# ---- Track 1: Bass ----
log("Track 1: Bass...")
bass_roots = {0:36,1:36,2:36,3:41,4:34,5:36}
for si in range(6):
    tcp("create_clip", {"track_index":1,"clip_index":si,"length":BARS}); time.sleep(0.05)
    root = bass_roots[si]; notes = []
    if si in [0,4,5]:
        for b in range(BEATS//8):
            o=b*8
            notes+=[{"pitch":root,"start_time":o,"duration":4.0,"velocity":90,"mute":False},
                    {"pitch":root-2,"start_time":o+4,"duration":2.0,"velocity":80,"mute":False},
                    {"pitch":root,"start_time":o+6,"duration":1.5,"velocity":85,"mute":False}]
    elif si==3:
        for b in range(BEATS//4):
            o=b*4
            notes+=[{"pitch":root,"start_time":o,"duration":0.5,"velocity":100,"mute":False},
                    {"pitch":root+5,"start_time":o+0.75,"duration":0.25,"velocity":85,"mute":False},
                    {"pitch":root,"start_time":o+1.5,"duration":0.5,"velocity":92,"mute":False},
                    {"pitch":root+7,"start_time":o+2.25,"duration":0.25,"velocity":85,"mute":False},
                    {"pitch":root+5,"start_time":o+3,"duration":0.5,"velocity":88,"mute":False}]
    elif si==2:
        for b in range(BEATS//2):
            o=b*2; p=root+[0,5,3,7][b%4]
            notes+=[{"pitch":p,"start_time":o,"duration":0.75,"velocity":90,"mute":False},
                    {"pitch":p+2,"start_time":o+1,"duration":0.5,"velocity":80,"mute":False}]
    else:
        for b in range(BEATS//4):
            o=b*4
            notes+=[{"pitch":root,"start_time":o,"duration":1.5,"velocity":95,"mute":False},
                    {"pitch":root+7,"start_time":o+2,"duration":0.5,"velocity":85,"mute":False},
                    {"pitch":root,"start_time":o+3,"duration":0.5,"velocity":80,"mute":False},
                    {"pitch":root+3,"start_time":o+4,"duration":1.0,"velocity":90,"mute":False},
                    {"pitch":root+5,"start_time":o+5.5,"duration":0.25,"velocity":80,"mute":False},
                    {"pitch":root-2,"start_time":o+6,"duration":1.5,"velocity":90,"mute":False}]
    tcp("add_notes_to_clip",{"track_index":1,"clip_index":si,"notes":notes}); time.sleep(0.1)

# ---- Track 2: Chords ----
log("Track 2: Chords...")
chord_presets = [
    {"root":45,"type":"min7","vel":65,"prog":[(0,0),(4,4)]},
    {"root":48,"type":"min7","vel":75,"prog":[(0,0),(4,4),(8,0),(12,4)]},
    {"root":48,"type":"min7","vel":80,"prog":[(0,0),(4,4),(8,0),(12,4)]},
    {"root":48,"type":"maj7","vel":85,"prog":[(0,0),(4,4),(8,7),(12,0)]},
    {"root":45,"type":"min7","vel":65,"prog":[(0,0)]},
    {"root":50,"type":"min7","vel":72,"prog":[(0,0),(8,0),(12,5)]},
]
for si, cp in enumerate(chord_presets):
    tcp("create_clip",{"track_index":2,"clip_index":si,"length":BARS}); time.sleep(0.05)
    for start_beat, root_offset in cp["prog"]:
        create_chord_notes(ctx=None, track_index=2, clip_index=si,
                            root=cp["root"]+root_offset, chord_type=cp["type"],
                            start_time=start_beat, duration=6.0, velocity=cp["vel"])
        time.sleep(0.05)

# ---- Track 3: Lead ----
log("Track 3: Lead...")
leads=[[67,64,69,67,62,64,69,67,67,69,71,72,71,69,67,64],
       [67,69,71,72,74,72,71,69,67,64,67,69,71,72,71,69],
       [64,65,67,69,71,72,71,69,67,69,71,72,74,72,71,69],
       [72,74,76,77,79,77,76,74,72,71,72,74,76,74,72,71],
       [60,64,67,64,60,64,67,64,60,62,65,62,60,62,65,62],
       [71,72,74,72,71,69,67,69,71,72,74,76,77,76,74,72]]
for si in range(6):
    tcp("create_clip",{"track_index":3,"clip_index":si,"length":BARS}); time.sleep(0.05)
    phrase=leads[si]; notes=[]
    for i in range(BEATS):
        p=phrase[i%len(phrase)]; vel=80+random.randint(-8,12)
        if i%2==0:
            notes.append({"pitch":p,"start_time":i*0.5,"duration":0.4,"velocity":vel,"mute":False})
    if si==3:
        notes+=[{"pitch":84,"start_time":b,"duration":0.15,"velocity":50,"mute":False} for b in range(0,BEATS,8)]
    tcp("add_notes_to_clip",{"track_index":3,"clip_index":si,"notes":notes}); time.sleep(0.1)

# ---- Track 4: FX ----
log("Track 4: FX...")
for si in range(6):
    tcp("create_clip",{"track_index":4,"clip_index":si,"length":BARS}); time.sleep(0.05)
    if si in [0,4]:
        notes=[{"pitch":60,"start_time":b*4,"duration":0.5,"velocity":40,"mute":False} for b in range(BARS//4)]
    elif si==2:
        notes=[{"pitch":36+(i%12),"start_time":i*0.25,"duration":0.12,"velocity":min(35+i,75),"mute":False} for i in range(64)]
    elif si==3:
        notes=[]
        for b in range(BEATS):
            if b%4==0:
                notes.append({"pitch":72,"start_time":b,"duration":0.08,"velocity":75,"mute":False})
                notes.append({"pitch":84,"start_time":b,"duration":0.08,"velocity":65,"mute":False})
    elif si==5:
        notes=[{"pitch":60+(i%24),"start_time":i*0.5,"duration":0.15,"velocity":50+random.randint(-10,15),"mute":False} for i in range(32)]
    else:
        notes=[{"pitch":60,"start_time":b*8,"duration":1.0,"velocity":55,"mute":False} for b in range(BARS//8)]
    tcp("add_notes_to_clip",{"track_index":4,"clip_index":si,"notes":notes}); time.sleep(0.05)

# ---- Track 5: Percussion ----
log("Track 5: Percussion...")
for si, pat in enumerate(["steppers","rockers","house_basic","techno_4x4","dub_techno","rockers"]):
    create_drum_pattern(ctx=None, track_index=5, clip_index=si,
                         pattern_name=pat, length=BARS,
                         kick_note=47, snare_note=45, hat_note=42, clap_note=39)
    time.sleep(0.2)

# ---- Track 6: Strings ----
log("Track 6: Strings...")
string_chords=[
    [(45,48,52,57),(48,52,55,60),(43,47,50,55),(45,49,52,57)],
    [(48,52,55,60),(50,54,57,62),(48,52,55,60),(45,49,52,57)],
    [(48,52,55,60),(50,54,57,62),(48,52,55,60),(43,47,50,56)],
    [(48,52,55,60),(53,57,60,64),(50,54,57,62),(45,49,52,57)],
    [(45,49,52,57),(43,47,50,55),(45,49,52,57),(48,52,55,60)],
    [(50,54,57,62),(48,52,55,60),(52,56,59,64),(48,52,55,60)],
]
for si in range(6):
    tcp("create_clip",{"track_index":6,"clip_index":si,"length":BARS}); time.sleep(0.05)
    voicings=string_chords[si]; section_len=BEATS//len(voicings); notes=[]
    for vi,(n1,n2,n3,n4) in enumerate(voicings):
        beat=vi*section_len
        notes+=[{"pitch":n1,"start_time":beat,"duration":float(section_len),"velocity":70,"mute":False},
                {"pitch":n2,"start_time":beat,"duration":float(section_len),"velocity":68,"mute":False},
                {"pitch":n3,"start_time":beat,"duration":float(section_len),"velocity":66,"mute":False},
                {"pitch":n4,"start_time":beat,"duration":float(section_len),"velocity":64,"mute":False}]
    tcp("add_notes_to_clip",{"track_index":6,"clip_index":si,"notes":notes}); time.sleep(0.05)

# ---- Track 7: Arp ----
log("Track 7: Arp...")
arp_presets=[
    {"root":48,"base":[0,4,7,12],"vel":60,"pat":"up"},
    {"root":48,"base":[0,3,7,10],"vel":70,"pat":"updown"},
    {"root":48,"base":[0,3,7,10],"vel":75,"pat":"updown"},
    {"root":48,"base":[0,4,7,11],"vel":80,"pat":"random"},
    {"root":45,"base":[0,3,7,10],"vel":60,"pat":"up"},
    {"root":50,"base":[0,4,7,10],"vel":72,"pat":"updown"},
]
for si, ap in enumerate(arp_presets):
    tcp("create_clip",{"track_index":7,"clip_index":si,"length":BARS}); time.sleep(0.05)
    base=ap["base"]; root=ap["root"]; vel=ap["vel"]; pat=ap["pat"]; notes=[]
    for b in range(BEATS*2):
        if pat=="up": ni=b%len(base)
        elif pat=="updown":
            n=b%(len(base)*2-2)
            if n>=len(base): n=len(base)*2-2-n
            ni=n
        else: ni=b%len(base) if b%3 else random.randint(0,len(base)-1)
        pitch=root+base[ni]
        notes.append({"pitch":pitch,"start_time":b*0.25,"duration":0.2,"velocity":vel+random.randint(-5,10),"mute":False})
    tcp("add_notes_to_clip",{"track_index":7,"clip_index":si,"notes":notes}); time.sleep(0.1)

# ---- Polish ----
log("Polishing...")
colors = {0:10,1:20,2:60,3:40,4:80,5:15,6:70,7:50}
volumes = {0:0.82,1:0.88,2:0.60,3:0.68,4:0.45,5:0.70,6:0.50,7:0.52}
panning = {0:0.0,1:0.0,2:-0.18,3:0.15,4:0.0,5:0.0,6:0.22,7:-0.12}
for i in range(8):
    tcp("set_track_color", {"track_index": i, "color_index": colors[i]}); time.sleep(0.05)
    _client.udp_command("set_track_volume", {"track_index": i, "volume": volumes[i]})
    _client.udp_command("set_track_pan", {"track_index": i, "pan": panning[i]})
    time.sleep(0.05)

# Group tracks
tcp("group_tracks", {"track_indices": [0, 5]}); time.sleep(0.5)
tcp("set_track_name", {"track_index": 8, "name": "Rhythm"}); time.sleep(0.05)
tcp("group_tracks", {"track_indices": [1, 2, 3, 6, 7]}); time.sleep(0.5)
tcp("set_track_name", {"track_index": 9, "name": "Melodic"}); time.sleep(0.05)

# ---- Verification ----
log("\n=== VERIFICATION ===")
tracks = tcp("get_all_tracks").get('result',{}).get('tracks',[])
for t in tracks:
    ti=tcp("get_track_info",{"track_index":t.get('index')})
    devs=ti.get('result',{}).get('devices',ti.get('devices',[]))
    dn=[d.get('name','?') for d in (devs if isinstance(devs,list) else [])]
    log("  [{}] {} -> {}".format(t.get('index'),t.get('name'),dn))

rt = tcp("get_return_tracks").get('result',{}).get('return_tracks',[])
for r in rt:
    log("  Return [{}] {}".format(r.get('index'),r.get('name')))

log("\nDone! 8 tracks + 2 returns with full effects chains.")
