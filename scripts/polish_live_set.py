"""
Polish an existing session: track colors, mix levels, panning,
master bus FX, send routing, and group tracks.

Usage:
    python scripts/polish_live_set.py
"""
import sys, time
sys.path.insert(0, r'C:\Users\Tobias\git\ableton-mcp-extended')
from agentic_mix.tools import _client

def tcp(cmd, params=None):
    return _client.tcp_command(cmd, params or {})

def load(track, uri):
    tcp("load_browser_item", {"track_index": track, "item_uri": uri})

def log(msg): print("[POLISH] {}".format(msg))

# Master bus
log("Master FX...")
load(-1, "query:AudioFx#Glue%20Compressor"); time.sleep(0.3)
load(-1, "query:AudioFx#Limiter"); time.sleep(0.3)

# Colors
colors = {0:10,1:20,2:60,3:40,4:80,5:15,6:70,7:50}

# Mix
volumes = {0:0.82,1:0.88,2:0.60,3:0.68,4:0.45,5:0.70,6:0.50,7:0.52}
panning = {0:0.0,1:0.0,2:-0.18,3:0.15,4:0.0,5:0.0,6:0.22,7:-0.12}

log("Mix...")
for i in range(8):
    tcp("set_track_color", {"track_index": i, "color_index": colors[i]}); time.sleep(0.05)
    _client.udp_command("set_track_volume", {"track_index": i, "volume": volumes[i]})
    _client.udp_command("set_track_pan", {"track_index": i, "pan": panning[i]})
    time.sleep(0.05)

# Sends
log("Sends...")
rt = tcp("get_return_tracks").get('result',{}).get('return_tracks',[])
reverb_idx = next((r.get('index') for r in rt if 'Reverb' in r.get('name','')), None)
delay_idx = next((r.get('index') for r in rt if 'Delay' in r.get('name','')), None)
if reverb_idx is not None:
    for t in [0,5]: _client.udp_command("set_send_amount", {"track_index":t,"send_index":reverb_idx,"amount":0.15})
    for t in [2,6]: _client.udp_command("set_send_amount", {"track_index":t,"send_index":reverb_idx,"amount":0.28})
    for t in [3,7]: _client.udp_command("set_send_amount", {"track_index":t,"send_index":reverb_idx,"amount":0.22})
if delay_idx is not None:
    _client.udp_command("set_send_amount", {"track_index":3,"send_index":delay_idx,"amount":0.30})
    _client.udp_command("set_send_amount", {"track_index":7,"send_index":delay_idx,"amount":0.20})

# Group
log("Grouping...")
tcp("group_tracks", {"track_indices": [0, 5]}); time.sleep(0.5)
tcp("set_track_name", {"track_index": 8, "name": "Rhythm"})
tcp("group_tracks", {"track_indices": [1, 2, 3, 6, 7]}); time.sleep(0.5)
tcp("set_track_name", {"track_index": 9, "name": "Melodic"})

log("\nPolish complete.")
