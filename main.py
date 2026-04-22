"""YouTube Automation Agent - CLI Entry Point."""

import argparse
import asyncio
import logging
import sys

from agent.config import Config
from agent.orchestrator import Agent
from agent.uploader import YouTubeUploader


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
  python main.py --list-channels
        """,
    )

    parser.add_argument("topic", nargs="?", help="Topic to research and create a video about")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private",
                        help="YouTube privacy status (default: private)")
    parser.add_argument("--research-only", action="store_true", help="Only do research, skip video creation")
    parser.add_argument("--list-channels", action="store_true",
                        help="List all YouTube channels on this account and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--max-results", type=int, default=None, help="Max YouTube search results")
    parser.add_argument("--voice", type=str, default=None, help="TTS voice (e.g., en-US-GuyNeural)")
    parser.add_argument("--channel-id", type=str, default=None,
                        help="Target YouTube channel ID (overrides YOUTUBE_CHANNEL_ID in .env)")

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Build config
    config = Config()
    if args.max_results:
        config.max_search_results = args.max_results
    if args.voice:
        config.tts_voice = args.voice
    if args.channel_id:
        config.youtube_channel_id = args.channel_id

    # --list-channels: show all channels and exit
    if args.list_channels:
        uploader = YouTubeUploader(config)
        uploader.print_channels()
        sys.exit(0)

    if not args.topic:
        parser.error("topic is required unless using --list-channels")

    should_upload = not args.no_upload and not args.research_only

    # Require --channel-id only when upload is enabled
    if should_upload and not config.youtube_channel_id:
        print(f"\nERROR: --channel-id is required when uploading (--privacy '{args.privacy}')")
        print("  Run: python main.py --list-channels")
        print("  Then: python main.py \"<topic>\" --privacy private --channel-id UCxxxxxxxxxxxxxxxxxx\n")
        sys.exit(1)

    if config.youtube_channel_id and config.youtube_channel_id.startswith("UCxxx"):
        print(f"\nERROR: --channel-id is still set to the placeholder value '{config.youtube_channel_id}'")
        print("  Run: python main.py --list-channels  to get your real channel ID\n")
        sys.exit(1)

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
