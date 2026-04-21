"""Main Agent Orchestrator - Coordinates the full pipeline."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import Config
from .researcher import YouTubeResearcher, ResearchResult
from .synthesizer import ContentSynthesizer, VideoScript
from .video_creator import VideoCreator
from .uploader import YouTubeUploader

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    topic: str
    research: ResearchResult | None = None
    script: VideoScript | None = None
    video_path: Path | None = None
    video_id: str | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and self.video_path is not None

    def summary(self) -> str:
        lines = [
            f"{'=' * 60}",
            f"  PIPELINE RESULT",
            f"{'=' * 60}",
            f"  Topic:    {self.topic}",
        ]
        if self.research:
            lines.append(f"  Videos:   {len(self.research.videos)} analyzed")
        if self.script:
            lines.append(f"  Title:    {self.script.title}")
            lines.append(f"  Sections: {len(self.script.sections)}")
        if self.video_path:
            lines.append(f"  Video:    {self.video_path}")
        if self.video_id:
            lines.append(f"  YouTube:  https://www.youtube.com/watch?v={self.video_id}")
        if self.error:
            lines.append(f"  ERROR:    {self.error}")
        lines.append(f"  Status:   {'SUCCESS' if self.success else 'FAILED'}")
        lines.append(f"{'=' * 60}")
        return "\n".join(lines)


class Agent:
    """YouTube Automation Agent - Full pipeline from research to upload."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.config.validate()

        self.researcher = YouTubeResearcher(self.config)
        self.synthesizer = ContentSynthesizer(self.config)
        self.video_creator = VideoCreator(self.config)
        self.uploader = YouTubeUploader(self.config)

    async def run(
        self,
        topic: str,
        upload: bool = True,
        privacy: str = "private",
    ) -> PipelineResult:
        """Run the full automation pipeline.

        Args:
            topic: The topic to research and create a video about
            upload: Whether to upload to YouTube
            privacy: YouTube privacy status ('private', 'unlisted', 'public')

        Returns:
            PipelineResult with all outputs
        """
        result = PipelineResult(topic=topic)
        start_time = datetime.now()

        try:
            # Phase 1: Research
            logger.info(f"\n[1/4] RESEARCHING: '{topic}'")
            result.research = self.researcher.research_topic(topic)

            if not result.research.videos:
                result.error = "No videos found for this topic"
                return result

            # Phase 2: Synthesize content
            logger.info(f"\n[2/4] SYNTHESIZING CONTENT")
            result.script = self.synthesizer.synthesize(result.research)

            # Phase 3: Create video
            logger.info(f"\n[3/4] CREATING VIDEO")
            result.video_path = await self.video_creator.create_video(result.script)

            # Phase 4: Upload (optional)
            if upload:
                logger.info(f"\n[4/4] UPLOADING TO YOUTUBE")
                result.video_id = self.uploader.upload(
                    result.video_path, result.script, privacy=privacy
                )
            else:
                logger.info(f"\n[4/4] UPLOAD SKIPPED (--no-upload flag)")

        except Exception as e:
            result.error = str(e)
            logger.error(f"Pipeline failed: {e}", exc_info=True)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"\nPipeline completed in {elapsed:.1f}s")
        logger.info(result.summary())

        return result

    async def research_only(self, topic: str) -> ResearchResult:
        """Run only the research phase."""
        return self.researcher.research_topic(topic)

    async def create_from_script(self, script: VideoScript, upload: bool = False) -> PipelineResult:
        """Create video from an existing script (skip research + synthesis)."""
        result = PipelineResult(topic="custom")
        result.script = script

        try:
            result.video_path = await self.video_creator.create_video(script)
            if upload:
                result.video_id = self.uploader.upload(result.video_path, script)
        except Exception as e:
            result.error = str(e)

        return result
