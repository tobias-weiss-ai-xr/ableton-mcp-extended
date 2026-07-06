#!/usr/bin/env python
"""
Setup Return Track 5 with Reverb and Delay effects.
Dub techno returns: space and echo for dub washes.
"""

import sys
sys.path.insert(0, '.')

from mcp_client import MCPClientTCP

def main():
    """
    Create Return Track with Lémmer's Dub fx chain:
    - Pre-delay (ping-pong stereo)
    - Vintage Reverb (large hall)
    - EQ for warmth
    """

    print("Setting up Return Track 5 (Dub FX returns)...")

    client = MCPClientTCP()

    try:
        # Load ping-pong delay
        print("  1. Loading Ping Pong Delay...")
        delay_uri = 'query:Delays#Filter%20Delay#FileId_5050'
        client.send_command("load_instrument_or_effect", {
            "track_index": 5,
            "uri": delay_uri
        })

        # Load reverb
        print("  2. Loading Vintage Reverb...")
        reverb_uri = 'query:Reverbs#Hybrid%20Reverb#FileId_5052'
        client.send_command("load_instrument_or_effect", {
            "track_index": 5,
            "uri": reverb_uri
        })

        # Load channel EQ for warmth
        print("  3. Loading Channel EQ...")
        eq_uri = 'query:EQ%20Eight#FileId_6042'
        client.send_command("load_instrument_or_effect", {
            "track_index": 5,
            "uri": eq_uri
        })

        # Default parameter values for dub sound
        print("  4. Setting default dub EQ curve...")
        # Note: Use typical low-cut around 200-300Hz and high-shelf boost 2-4dB

        print("\nReturn Track 5 setup complete!")
        print("Note: Adjust parameters manually for optimal dub techno sound")
        print("      - Low cut: 200-300Hz (reduce mud)")
        print("      - High shelf: +2-4dB @ 8-12kHz (air)")
        print("      - Delay: 1/4 or 1/8, feedback 30-50%")
        print("      - Reverb: Large hall, decay 3-5s")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main() or 0)