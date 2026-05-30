"""
CLI runner for the LangGraph agentic mix pipeline.

Usage:
    python -m agentic_mix.cli --genre dub_techno --tempo 126 --duration 120

Or programmatically:
    from agentic_mix.cli import main
    main()
"""
import argparse
import sys
from .graph import run_pipeline
from .state import Config


def parse_args() -> Config:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ableton Live agentic mix generator using LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
epilog="""
Examples:
  # Dub techno 2h mix
  python -m agentic_mix.cli --genre dub_techno --tempo 126 --duration 120

  # House 1h mix with high variation
  python -m agentic_mix.cli --genre house --tempo 124 --duration 60 --variation 0.8

  # Ambient 30m mix
  python -m agentic_mix.cli --genre ambient --tempo 90 --duration 30 --energy gentle
        """
    )

    parser.add_argument("--genre", choices=["dub_techno", "house", "techno", "ambient"],
                       default="dub_techno", help="Musical genre")
    parser.add_argument("--tempo", type=int, default=126,
                       help="Tempo in BPM (60-180)")
    parser.add_argument("--duration", type=int, default=120,
                       help="Mix duration in minutes (1-480)")
    parser.add_argument("--tracks", type=int, default=8,
                       help="Number of tracks (2-16)")
    parser.add_argument("--key", type=str, default="Fm",
                       help="Musical key (e.g., Fm, Cm, Am)")
    parser.add_argument("--energy", choices=["gradual", "aggressive", "gentle"],
                       default="gradual", help="Energy curve type")
    parser.add_argument("--variation", type=float, default=0.5,
                       help="Variation level (0.0-1.0)")

    args = parser.parse_args()

    # Create and validate Config
    config = Config(
        tempo=args.tempo,
        duration_minutes=args.duration,
        genre=args.genre,
        track_count=args.tracks,
        key=args.key,
        energy_curve=args.energy,
        variation_level=args.variation
    )

    return config


def print_feedback(feedback: list):
    """Print feedback messages."""
    for msg in feedback:
        print(f"[INFO] {msg}")


def print_metrics(metrics: dict):
    """Print mix metrics."""
    print("\n" + "=" * 60)
    print("MIX METRICS")
    print("=" * 60)

    transitions = metrics.get("section_transitions", [])
    if transitions:
        print(f"\nSections: {len(transitions)}")
        for t in transitions[:5]:  # Show first 5
            print(f"  - {t['name']}: energy={t['energy_level']:.2f}, technique={t['technique']}")
        if len(transitions) > 5:
            print(f"  ... and {len(transitions) - 5} more sections")

    errors = metrics.get("errors", [])
    if errors:
        print(f"\nErrors: {len(errors)}")
        for err in errors:
            print(f"  - {err}")

    if metrics.get("start_time") and metrics.get("current_time"):
        duration = metrics["current_time"] - metrics["start_time"]
        print(f"\nDuration: {duration:.1f} seconds ({duration/60:.1f} minutes)")

    print("=" * 60)


def main():
    """Main entry point."""
    try:
        # Parse configuration
        config = parse_args()

        print("=" * 60)
        print("AGENTIC ABLETON MIX GENERATOR")
        print("=" * 60)
        print(f"Genre:     {config.genre}")
        print(f"Tempo:     {config.tempo} BPM")
        print(f"Duration:  {config.duration_minutes} minutes")
        print(f"Tracks:    {config.track_count}")
        print(f"Key:       {config.key}")
        print(f"Energy:    {config.energy_curve}")
        print(f"Variation: {config.variation_level}")
        print("=" * 60)

        # Run the pipeline
        result = run_pipeline(config)

        # Print feedback
        print_feedback(result["feedback"])

        # Print metrics
        print_metrics(result["metrics"])

        # Check for errors
        if result["error"]:
            print(f"\n[ERROR] {result['error']}")
            sys.exit(1)

        # Check completion
        if result["complete"]:
            print("\n[SUCCESS] Mix generation complete!")
            sys.exit(0)
        else:
            print("\n[WARNING] Mix generation incomplete")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Mix generation stopped by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[FATAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
