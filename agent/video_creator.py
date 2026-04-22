"""Video Creation Module - Generate voiceover, slides, and assemble video."""

import asyncio
import io
import logging
import textwrap
from pathlib import Path

import edge_tts
import requests
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

    def _fetch_theme_image(self, keywords: str) -> Image.Image | None:
        """Fetch a thematic background image from Unsplash API based on keywords.
        
        Returns:
            PIL Image or None if fetch fails
        """
        try:
            # Use Unsplash API (free, no key required for basic usage)
            # Limit size to reduce network overhead
            search_query = keywords.split()[0] if keywords else "abstract"
            url = f"https://source.unsplash.com/1920x1080/?{search_query}"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                return image.convert("RGB")
        except Exception as e:
            logger.debug(f"Failed to fetch theme image for '{keywords}': {e}")
        
        return None

    def _create_slide_with_background(
        self,
        filepath: Path,
        title: str,
        subtitle: str = "",
        bg_image: Image.Image = None,
        bg_color=(20, 20, 40),
        text_color=(255, 255, 255),
        accent_color=(0, 168, 255),
    ) -> Path:
        """Create a slide with optional background image and text overlay."""
        # Create base image
        if bg_image:
            img = bg_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        else:
            img = Image.new("RGB", (self.width, self.height), bg_color)
        
        draw = ImageDraw.Draw(img, "RGBA")

        # Add dark overlay for better text readability
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 100))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)

        # Draw accent bar at top
        draw.rectangle([0, 0, self.width, 8], fill=accent_color)

        # Add subtle gradient overlay for depth
        for y in range(self.height):
            alpha = int(50 * (y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(alpha, alpha, alpha + 10))

        # Load fonts
        try:
            title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 72)
            subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
        except OSError:
            try:
                title_font = ImageFont.truetype("arial.ttf", 72)
                subtitle_font = ImageFont.truetype("arial.ttf", 40)
            except OSError:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

        # Wrap and draw title with outline for better visibility
        wrapped_title = textwrap.fill(title, width=30)
        bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=title_font)
        text_height = bbox[3] - bbox[1]
        y_pos = (self.height - text_height) // 2 - 50

        # Draw title with outline
        for offset_x in [-2, -1, 0, 1, 2]:
            for offset_y in [-2, -1, 0, 1, 2]:
                draw.multiline_text(
                    (self.width // 2 + offset_x, y_pos + offset_y),
                    wrapped_title,
                    fill=(0, 0, 0, 180),
                    font=title_font,
                    anchor="ma",
                    align="center",
                )

        # Draw title text (bright)
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
            wrapped_sub = textwrap.fill(subtitle, width=50)
            # Subtitle outline
            for offset_x in [-1, 0, 1]:
                for offset_y in [-1, 0, 1]:
                    draw.multiline_text(
                        (self.width // 2 + offset_x, y_pos + text_height + 50 + offset_y),
                        wrapped_sub,
                        fill=(0, 0, 0, 160),
                        font=subtitle_font,
                        anchor="ma",
                        align="center",
                    )
            
            # Subtitle text
            draw.multiline_text(
                (self.width // 2, y_pos + text_height + 50),
                wrapped_sub,
                fill=accent_color,
                font=subtitle_font,
                anchor="ma",
                align="center",
            )

        img.save(filepath)
        return filepath

    def create_slides(self, script: VideoScript) -> list[Path]:
        """Create slide images for each section of the script with thematic background images."""
        slides_dir = self.config.today_dir("slides")
        slide_paths = []

        logger.info("Fetching thematic background images...")

        # Title slide - fetch image based on title keywords
        title_bg = self._fetch_theme_image(script.title)
        title_path = self._create_slide_with_background(
            slides_dir / "00_title.png",
            title=script.title,
            subtitle="",
            bg_image=title_bg,
            accent_color=(0, 168, 255),
        )
        slide_paths.append(title_path)

        # Hook slide
        hook_bg = self._fetch_theme_image(script.tags[0] if script.tags else "")
        hook_path = self._create_slide_with_background(
            slides_dir / "01_hook.png",
            title=script.hook[:80],
            subtitle=script.hook[80:160] if len(script.hook) > 80 else "",
            bg_image=hook_bg,
            accent_color=(255, 100, 50),
        )
        slide_paths.append(hook_path)

        # Section slides - each with thematic background
        for i, section in enumerate(script.sections, 2):
            # Fetch background based on section heading or visual notes
            section_keywords = section.get("visual_notes", section["heading"])
            section_bg = self._fetch_theme_image(section_keywords)
            
            slide_path = self._create_slide_with_background(
                slides_dir / f"{i:02d}_{section['heading'][:20].replace(' ', '_')}.png",
                title=section["heading"],
                subtitle=section.get("visual_notes", "")[:120],
                bg_image=section_bg,
                accent_color=(0, 168, 255),
            )
            slide_paths.append(slide_path)

        # Outro slide
        outro_bg = self._fetch_theme_image("success celebration")
        outro_path = self._create_slide_with_background(
            slides_dir / f"{len(script.sections) + 2:02d}_outro.png",
            title="Thanks for watching!",
            subtitle="Like, Subscribe & Comment",
            bg_image=outro_bg,
            accent_color=(255, 50, 50),
        )
        slide_paths.append(outro_path)

        logger.info(f"Created {len(slide_paths)} slides with thematic backgrounds")
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

    def create_thumbnail(self, script, topic_name: str = None) -> Path:
        """Create a professional video thumbnail based on thumbnail_concept.
        
        YouTube standard thumbnail size: 1280x720 pixels
        """
        if topic_name:
            safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' 
                                for c in topic_name).strip().replace(' ', '_')
            videos_dir = self.config.today_dir("videos") / safe_topic
        else:
            videos_dir = self.config.today_dir("videos")
        
        videos_dir.mkdir(parents=True, exist_ok=True)
        output_path = videos_dir / "thumbnail.png"

        logger.info(f"Creating thumbnail from concept: {script.thumbnail_concept}")

        # Fetch background image for thumbnail based on title
        bg_image = self._fetch_theme_image(script.title)

        # Create thumbnail with standard YouTube dimensions
        thumb_width, thumb_height = 1280, 720

        if bg_image:
            img = bg_image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        else:
            img = Image.new("RGB", (thumb_width, thumb_height), (20, 20, 40))

        draw = ImageDraw.Draw(img, "RGBA")

        # Add dark overlay for text readability
        overlay = Image.new("RGBA", (thumb_width, thumb_height), (0, 0, 0, 80))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)

        # Draw bright accent border
        accent_color = (255, 100, 50)
        border_width = 8
        draw.rectangle(
            [border_width, border_width, thumb_width - border_width, thumb_height - border_width],
            outline=accent_color,
            width=border_width
        )

        # Load font
        try:
            title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 56)
            subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
        except OSError:
            try:
                title_font = ImageFont.truetype("arial.ttf", 56)
                subtitle_font = ImageFont.truetype("arial.ttf", 32)
            except OSError:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

        # Draw main title/concept
        title = script.title[:40]  # Truncate for thumbnail
        wrapped_title = textwrap.fill(title, width=20)

        # Title with outline for visibility
        for offset_x in [-2, -1, 0, 1, 2]:
            for offset_y in [-2, -1, 0, 1, 2]:
                draw.multiline_text(
                    (thumb_width // 2 + offset_x, thumb_height // 3 + offset_y),
                    wrapped_title,
                    fill=(0, 0, 0, 200),
                    font=title_font,
                    anchor="ma",
                    align="center",
                )

        # Bright title text
        draw.multiline_text(
            (thumb_width // 2, thumb_height // 3),
            wrapped_title,
            fill=(255, 255, 255),
            font=title_font,
            anchor="ma",
            align="center",
        )

        # Add a key visual element or tag
        tags_text = " • ".join(script.tags[:2]) if script.tags else ""
        if tags_text:
            draw.text(
                (thumb_width // 2, thumb_height * 2 // 3),
                tags_text[:30],
                fill=accent_color,
                font=subtitle_font,
                anchor="mm",
            )

        img.save(output_path)
        logger.info(f"Thumbnail saved to {output_path}")
        return output_path

    def assemble_video(self, slide_paths: list[Path], audio_path: Path, topic_name: str = None) -> Path:
        """Assemble slides + audio into a final video.
        
        Args:
            slide_paths: List of slide image paths
            audio_path: Path to voiceover audio file
            topic_name: Topic name for organizing output. If provided, creates a topic subfolder.
                       If None, defaults to 'final_video.mp4'
        """
        # Create topic-specific folder if topic_name provided
        if topic_name:
            # Sanitize topic name for filesystem
            safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' 
                                for c in topic_name).strip().replace(' ', '_')
            videos_dir = self.config.today_dir("videos") / safe_topic
            video_filename = f"{safe_topic}.mp4"
        else:
            videos_dir = self.config.today_dir("videos")
            video_filename = "final_video.mp4"
        
        videos_dir.mkdir(parents=True, exist_ok=True)
        output_path = videos_dir / video_filename
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
        """Full video creation pipeline: TTS -> Slides -> Assemble -> Thumbnail."""
        logger.info("=== Starting video creation ===")

        # Step 1: Generate voiceover
        audio_path = await self.generate_voiceover(script)

        # Step 2: Create slides with thematic backgrounds
        slide_paths = self.create_slides(script)

        # Step 3: Create thumbnail
        self.create_thumbnail(script, topic_name=script.title)

        # Step 4: Assemble video (organize by topic)
        video_path = self.assemble_video(slide_paths, audio_path, topic_name=script.title)

        logger.info(f"=== Video creation complete: {video_path} ===")
        return video_path
