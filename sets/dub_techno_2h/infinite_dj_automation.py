#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infinite Dub Techno DJ Automation Script
Keeps the mix running by repeatedly calling opencode with DJ commands
"""

import subprocess
import time
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dj_automation.log"), logging.StreamHandler()],
)
logger = logging.getLogger("DubTechnoDJ")

# Configuration
INTERVAL_SECONDS = 30  # Time between commands
MAX_VARIATIONS = 1000  # Maximum variations before restart
TRACK_INDEXES = {
    "kick": 0,
    "bass": 1,
    "hats": 2,
    "percs": 3,
    "pad": 4,
    "fx": 5,
    "lead": 6,
    "stabs": 7,
}

# Variation counter
variation_count = 0

# Command templates for DJ automation
DJ_COMMANDS = [
    # Bass variations (main focus)
    "fire_clip track_index=1 clip_index={bass_clip}",
    "set_track_volume track_index=1 volume={bass_vol}",
    # Hats variations
    "fire_clip track_index=2 clip_index={hats_clip}",
    "set_track_volume track_index=2 volume={hats_vol}",
    # Lead variations (max 0.5)
    "fire_clip track_index=6 clip_index={lead_clip}",
    "set_track_volume track_index=6 volume={lead_vol}",
    # Pad variations
    "fire_clip track_index=4 clip_index={pad_clip}",
    "set_track_volume track_index=4 volume={pad_vol}",
    # Percs variations
    "fire_clip track_index=3 clip_index={percs_clip}",
    "set_track_volume track_index=3 volume={percs_vol}",
    # FX variations
    "set_track_volume track_index=5 volume={fx_vol}",
    "set_send_amount track_index={send_track} send_index=0 amount={send_amt}",
    # Kick variations
    "fire_clip track_index=0 clip_index={kick_clip}",
    "set_master_volume volume={master_vol}",
]

# Clip indexes for each track
CLIP_OPTIONS = {
    "kick": [0, 1, 2, 3, 4, 5, 6],
    "bass": [0, 1, 2, 3, 4, 5, 6],
    "hats": [0, 1, 2, 3, 4, 5, 6],
    "percs": [0, 1, 2, 3, 4, 5, 6, 7],
    "pad": [0, 1, 2, 3, 4, 6],
    "lead": [0, 1, 2, 3, 4, 5, 6, 7],
    "fx": [0, 1, 2, 3, 4, 5, 6],
}

# Volume ranges
VOLUME_RANGES = {
    "bass": (0.85, 0.95),
    "hats": (0.45, 0.65),
    "lead": (0.35, 0.50),  # MAX 0.5 as requested
    "pad": (0.40, 0.65),
    "percs": (0.45, 0.72),
    "fx": (0.30, 0.55),
    "master": (0.75, 0.88),
}


def get_random_value(range_tuple):
    """Get a random value from a range"""
    return round(random.uniform(range_tuple[0], range_tuple[1]), 2)


def generate_dj_command():
    """Generate a random DJ command"""
    global variation_count

    # Select a random command template
    template = random.choice(DJ_COMMANDS)

    # Fill in the placeholders
    command = template.format(
        bass_clip=random.choice(CLIP_OPTIONS["bass"]),
        bass_vol=get_random_value(VOLUME_RANGES["bass"]),
        hats_clip=random.choice(CLIP_OPTIONS["hats"]),
        hats_vol=get_random_value(VOLUME_RANGES["hats"]),
        lead_clip=random.choice(CLIP_OPTIONS["lead"]),
        lead_vol=get_random_value(VOLUME_RANGES["lead"]),
        pad_clip=random.choice(CLIP_OPTIONS["pad"]),
        pad_vol=get_random_value(VOLUME_RANGES["pad"]),
        percs_clip=random.choice(CLIP_OPTIONS["percs"]),
        percs_vol=get_random_value(VOLUME_RANGES["percs"]),
        fx_vol=get_random_value(VOLUME_RANGES["fx"]),
        send_track=random.randint(0, 7),
        send_amt=round(random.uniform(0.3, 0.8), 2),
        kick_clip=random.choice(CLIP_OPTIONS["kick"]),
        master_vol=get_random_value(VOLUME_RANGES["master"]),
    )

    variation_count += 1
    return command


def run_opencode_command(prompt):
    """Run an opencode command"""
    try:
        cmd = ["opencode", "run", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        logger.warning("Command timed out")
        return None, -1
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return None, -1


def main_loop():
    """Main automation loop"""
    global variation_count

    logger.info("=" * 60)
    logger.info("  DUB TECHNO INFINITE DJ AUTOMATION")
    logger.info("  Press Ctrl+C to stop")
    logger.info("=" * 60)

    try:
        while variation_count < MAX_VARIATIONS:
            # Generate a DJ command
            dj_command = generate_dj_command()

            # Create the full prompt
            prompt = f"""
You are the DJ. Execute this command and continue the mix:
{dj_command}

Keep the mix evolving with more variations. Focus on:
- Bass: Volume 0.85-0.95 (main focus)
- Lead: Max volume 0.5
- Stabs: Volume 0.45, change rarely
- Evolve all patterns over time

Current variation: {variation_count}
"""

            logger.info(f"\n[VARIATION {variation_count}] Executing: {dj_command}")

            # Run the command
            output, returncode = run_opencode_command(prompt)

            if output:
                logger.info(f"Command executed successfully")
                logger.debug(f"Output: {output[:200]}...")
            else:
                logger.warning("Command failed, continuing...")

            # Wait before next command
            wait_time = random.randint(INTERVAL_SECONDS - 10, INTERVAL_SECONDS + 10)
            logger.info(f"Waiting {wait_time} seconds before next variation...")
            time.sleep(wait_time)

        logger.info(f"\nReached {MAX_VARIATIONS} variations. Restarting...")
        variation_count = 0

    except KeyboardInterrupt:
        logger.info(f"\n\nAutomation stopped by user at variation {variation_count}")
        return


def continuous_loop():
    """Run the main loop continuously, restarting if it stops"""
    logger.info("Starting continuous DJ automation loop...")

    while True:
        try:
            main_loop()
        except Exception as e:
            logger.error(f"Main loop crashed: {e}")
            logger.info("Restarting in 10 seconds...")
            time.sleep(10)


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  DUB TECHNO INFINITE DJ AUTOMATION                            ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  This script will keep the mix running indefinitely.           ║
    ║  Press Ctrl+C to stop.                                        ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    try:
        continuous_loop()
    except KeyboardInterrupt:
        print("\n\nAutomation stopped by user.")
