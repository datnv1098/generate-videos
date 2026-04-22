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
from .image_generator import ImageGenerator
from .synthesizer import VideoScript

logger = logging.getLogger(__name__)


class VideoCreator:
    def __init__(self, config: Config):
        self.config = config
        self.width = config.video_width
        self.height = config.video_height
        self.image_generator = ImageGenerator(config)

    async def generate_voiceover(self, script: VideoScript) -> Path:
        """Generate TTS audio from the video script using edge-tts."""
        narration = script.get_full_narration()
        output_path = self.config.today_dir("audio") / "voiceover.mp3"

        logger.info(f"Generating voiceover ({len(narration)} chars) with voice: {self.config.tts_voice}")

        communicate = edge_tts.Communicate(narration, self.config.tts_voice)
        await communicate.save(str(output_path))

        logger.info(f"Voiceover saved to {output_path}")
        return output_path

    def _generate_slide_background(self, title: str, description: str, slides_dir: Path) -> Image.Image | None:
        """Generate slide background image using DALL-E.
        
        Args:
            title: Slide title
            description: Visual notes/description for image generation
            slides_dir: Directory to save generated image
        
        Returns:
            PIL Image or None if generation fails
        """
        try:
            # Create a sanitized filename
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' 
                                for c in title).strip().replace(' ', '_')[:30]
            image_path = slides_dir / f"{safe_title}_bg.png"
            
            logger.debug(f"Generating slide background for '{title}' -> {image_path}")
            
            # Generate image using DALL-E
            result_path = self.image_generator.generate_slide_image(description, title, image_path)
            
            # Verify image was saved successfully
            if result_path is None:
                logger.warning(f"DALL-E image generation returned None for '{title}'")
                return None
            
            if not result_path.exists():
                logger.error(f"Generated image path does not exist: {result_path}")
                return None
            
            # Load and return the image
            try:
                img = Image.open(result_path)
                img_rgb = img.convert("RGB")
                logger.debug(f"✓ Successfully loaded background image: {result_path}")
                return img_rgb
            except Exception as load_err:
                logger.error(f"Failed to load generated image: {load_err}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating background for '{title}': {e}")
        
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
            # Use DALL-E generated image as background
            img = bg_image.resize((self.width, self.height), Image.Resampling.LANCZOS).convert("RGBA")
            # Semi-transparent dark overlay for text readability
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 120))
            img = Image.alpha_composite(img, overlay).convert("RGB")
        else:
            # Text-only: plain solid color background
            img = Image.new("RGB", (self.width, self.height), bg_color)
        
        draw = ImageDraw.Draw(img)

        # Draw accent bar at top
        draw.rectangle([0, 0, self.width, 8], fill=accent_color)

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
        """Create slide images for each section of the script with AI-generated background images."""
        slides_dir = self.config.today_dir("slides")
        slide_paths = []

        logger.info("Generating DALL-E background images for slides...")

        # Title slide - generate image based on title
        title_bg = self._generate_slide_background(script.title, script.title, slides_dir)
        title_path = self._create_slide_with_background(
            slides_dir / "00_title.png",
            title=script.title,
            subtitle="",
            bg_image=title_bg,
            accent_color=(0, 168, 255),
        )
        slide_paths.append(title_path)

        # Hook slide
        hook_description = script.tags[0] if script.tags else "engaging content"
        hook_bg = self._generate_slide_background("Hook", f"Opening hook about {script.title}", slides_dir)
        hook_path = self._create_slide_with_background(
            slides_dir / "01_hook.png",
            title=script.hook[:80],
            subtitle=script.hook[80:160] if len(script.hook) > 80 else "",
            bg_image=hook_bg,
            accent_color=(255, 100, 50),
        )
        slide_paths.append(hook_path)

        # Section slides - each with AI-generated background
        for i, section in enumerate(script.sections, 2):
            # Generate background based on section heading and visual notes
            section_description = section.get("visual_notes", section["heading"])
            section_bg = self._generate_slide_background(
                section["heading"], 
                section_description,
                slides_dir
            )
            
            slide_path = self._create_slide_with_background(
                slides_dir / f"{i:02d}_{section['heading'][:20].replace(' ', '_')}.png",
                title=section["heading"],
                subtitle=section.get("visual_notes", "")[:120],
                bg_image=section_bg,
                accent_color=(0, 168, 255),
            )
            slide_paths.append(slide_path)

        # Outro slide
        outro_bg = self._generate_slide_background("Outro", "Celebratory outro slide with call to action", slides_dir)
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
        """Create a professional video thumbnail using DALL-E.
        
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

        logger.info(f"Generating DALL-E thumbnail for: {script.title}")

        try:
            # Generate thumbnail using DALL-E
            result_path = self.image_generator.generate_thumbnail_image(
                script.thumbnail_concept,
                script.title,
                script.tags,
                output_path
            )

            if result_path and result_path.exists():
                logger.info(f"✓ Thumbnail created successfully: {result_path}")
                return result_path
            else:
                logger.warning("DALL-E thumbnail generation failed, using fallback")
                return self._create_fallback_thumbnail(script, output_path)
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return self._create_fallback_thumbnail(script, output_path)

    def _create_fallback_thumbnail(self, script, output_path: Path) -> Path:
        """Create a fallback thumbnail with text overlay when DALL-E generation fails."""
        thumb_width, thumb_height = 1280, 720
        img = Image.new("RGB", (thumb_width, thumb_height), (20, 20, 40))
        draw = ImageDraw.Draw(img)

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

        # Draw bright accent border
        accent_color = (255, 100, 50)
        border_width = 8
        draw.rectangle(
            [border_width, border_width, thumb_width - border_width, thumb_height - border_width],
            outline=accent_color,
            width=border_width
        )

        # Draw title
        title = script.title[:40]
        wrapped_title = textwrap.fill(title, width=20)

        # Title with outline
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

        # Add tags
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
        logger.info(f"Fallback thumbnail saved to {output_path}")
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
