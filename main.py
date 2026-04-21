"""YouTube Automation Agent - CLI Entry Point."""

import argparse
import asyncio
import logging
import sys

from agent.config import Config
from agent.orchestrator import Agent


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Automation Agent - Research, create, and upload videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "artificial intelligence trends 2026"
  python main.py "python programming tips" --no-upload
  python main.py "crypto market analysis" --privacy unlisted
  python main.py "machine learning" --research-only
        """,
    )

    parser.add_argument("topic", help="Topic to research and create a video about")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private",
                        help="YouTube privacy status (default: private)")
    parser.add_argument("--research-only", action="store_true", help="Only do research, skip video creation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--max-results", type=int, default=None, help="Max YouTube search results")
    parser.add_argument("--voice", type=str, default=None, help="TTS voice (e.g., en-US-GuyNeural)")

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Build config
    config = Config()
    if args.max_results:
        config.max_search_results = args.max_results
    if args.voice:
        config.tts_voice = args.voice

    # Run agent
    agent = Agent(config)

    if args.research_only:
        research = asyncio.run(agent.research_only(args.topic))
        print(f"\nResearch complete: {len(research.videos)} videos analyzed")
        print(f"Saved to: output/research/")
    else:
        result = asyncio.run(agent.run(
            topic=args.topic,
            upload=not args.no_upload,
            privacy=args.privacy,
        ))
        print(result.summary())
        sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
