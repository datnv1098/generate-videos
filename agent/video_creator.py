"""Video Creation Module - Generate voiceover, slides, and assemble video."""

import asyncio
import logging
import textwrap
from pathlib import Path

import edge_tts
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFont

from .config import Config
from .synthesizer import VideoScript

logger = logging.getLogger(__name__)


class VideoCreator:
    def __init__(self, config: Config):
        self.config = config
        self.width = config.video_width
        self.height = config.video_height

    async def generate_voiceover(self, script: VideoScript) -> Path:
        """Generate TTS audio from the video script using edge-tts."""
        narration = script.get_full_narration()
        output_path = self.config.today_dir("audio") / "voiceover.mp3"

        logger.info(f"Generating voiceover ({len(narration)} chars) with voice: {self.config.tts_voice}")

        communicate = edge_tts.Communicate(narration, self.config.tts_voice)
        await communicate.save(str(output_path))

        logger.info(f"Voiceover saved to {output_path}")
        return output_path

    def create_slides(self, script: VideoScript) -> list[Path]:
        """Create slide images for each section of the script."""
        slides_dir = self.config.today_dir("slides")
        slide_paths = []

        # Title slide
        title_path = self._create_slide(
            slides_dir / "00_title.png",
            title=script.title,
            subtitle="",
            bg_color=(20, 20, 40),
            text_color=(255, 255, 255),
            accent_color=(0, 168, 255),
        )
        slide_paths.append(title_path)

        # Hook slide
        hook_path = self._create_slide(
            slides_dir / "01_hook.png",
            title=script.hook[:80],
            subtitle=script.hook[80:160] if len(script.hook) > 80 else "",
            bg_color=(25, 25, 50),
            text_color=(255, 255, 255),
            accent_color=(255, 100, 50),
        )
        slide_paths.append(hook_path)

        # Section slides
        for i, section in enumerate(script.sections, 2):
            slide_path = self._create_slide(
                slides_dir / f"{i:02d}_{section['heading'][:20].replace(' ', '_')}.png",
                title=section["heading"],
                subtitle=section.get("visual_notes", "")[:120],
                bg_color=(20 + i * 5, 20, 40 + i * 3),
                text_color=(255, 255, 255),
                accent_color=(0, 168, 255),
            )
            slide_paths.append(slide_path)

        # Outro slide
        outro_path = self._create_slide(
            slides_dir / f"{len(script.sections) + 2:02d}_outro.png",
            title="Thanks for watching!",
            subtitle="Like, Subscribe & Comment",
            bg_color=(20, 20, 40),
            text_color=(255, 255, 255),
            accent_color=(255, 50, 50),
        )
        slide_paths.append(outro_path)

        logger.info(f"Created {len(slide_paths)} slides")
        return slide_paths

    def _create_slide(
        self,
        filepath: Path,
        title: str,
        subtitle: str = "",
        bg_color=(20, 20, 40),
        text_color=(255, 255, 255),
        accent_color=(0, 168, 255),
    ) -> Path:
        """Create a single slide image."""
        img = Image.new("RGB", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw accent bar at top
        draw.rectangle([0, 0, self.width, 8], fill=accent_color)

        # Draw gradient overlay
        for y in range(self.height):
            alpha = int(30 * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(alpha, alpha, alpha + 10))

        # Try to use a nice font, fall back to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 64)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
        except OSError:
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 64)
                subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 36)
            except OSError:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

        # Wrap and draw title
        wrapped_title = textwrap.fill(title, width=35)
        bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=title_font)
        text_height = bbox[3] - bbox[1]
        y_pos = (self.height - text_height) // 2 - 40

        draw.multiline_text(
            (self.width // 2, y_pos),
            wrapped_title,
            fill=text_color,
            font=title_font,
            anchor="ma",
            align="center",
        )

        # Draw subtitle
        if subtitle:
            wrapped_sub = textwrap.fill(subtitle, width=55)
            draw.multiline_text(
                (self.width // 2, y_pos + text_height + 40),
                wrapped_sub,
                fill=(*accent_color, 200),
                font=subtitle_font,
                anchor="ma",
                align="center",
            )

        img.save(filepath)
        return filepath

    def assemble_video(self, slide_paths: list[Path], audio_path: Path) -> Path:
        """Assemble slides + audio into a final video."""
        output_path = self.config.today_dir("videos") / "final_video.mp4"
        logger.info("Assembling video...")

        # Load audio to get total duration
        audio = AudioFileClip(str(audio_path))
        total_duration = audio.duration

        # Calculate duration per slide
        num_slides = len(slide_paths)
        duration_per_slide = total_duration / num_slides

        # Create video clips from slides
        clips = []
        for slide_path in slide_paths:
            clip = ImageClip(str(slide_path)).with_duration(duration_per_slide)
            clips.append(clip)

        # Concatenate all slides
        video = concatenate_videoclips(clips, method="compose")

        # Add audio
        video = video.with_audio(audio)

        # Render (using lower quality for faster encoding)
        logger.info(f"Rendering video ({total_duration:.1f}s) to {output_path}...")
        logger.info("This may take 2-5 minutes depending on system...")
        video.write_videofile(
            str(output_path),
            fps=12,  # Lower FPS for faster encoding
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None,
        )

        # Cleanup
        audio.close()
        video.close()

        logger.info(f"Video saved to {output_path}")
        return output_path

    async def create_video(self, script: VideoScript) -> Path:
        """Full video creation pipeline: TTS -> Slides -> Assemble."""
        logger.info("=== Starting video creation ===")

        # Step 1: Generate voiceover
        audio_path = await self.generate_voiceover(script)

        # Step 2: Create slides
        slide_paths = self.create_slides(script)

        # Step 3: Assemble video
        video_path = self.assemble_video(slide_paths, audio_path)

        logger.info(f"=== Video creation complete: {video_path} ===")
        return video_path
