"""Image Generation Module - Generate images using OpenAI DALL-E."""

import logging
import requests
from pathlib import Path
from openai import OpenAI

from .config import Config

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generate images using OpenAI DALL-E API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def generate_slide_image(self, description: str, title: str, output_path: Path, max_retries: int = 2) -> Path:
        """Generate a slide background image using DALL-E based on description.
        
        Args:
            description: Text description of the image to generate
            title: Section title for context
            output_path: Path to save the generated image
            max_retries: Number of retry attempts on failure
        
        Returns:
            Path to the generated image, or None if generation fails
        """
        # Create a more detailed prompt for DALL-E
        prompt = f"""Create a professional, visually appealing background image for a video slide about: "{title}"
        
Details: {description}

Requirements:
- Modern, clean design
- High quality, 1920x1080 aspect ratio
- Professional color scheme
- Suitable for YouTube video backgrounds
- Include relevant visual elements that support the topic
- Avoid text overlays"""
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Generating DALL-E image for: {title} (attempt {attempt + 1}/{max_retries + 1})")
                
                response = self.client.images.generate(
                    model=self.config.openai_image_model,
                    prompt=prompt,
                    size="1792x1024",  # DALL-E 3 supported size (16:9 aspect ratio)
                    quality="standard",
                    n=1
                )
                
                # Download and save the image
                image_url = response.data[0].url
                logger.debug(f"Image URL received: {image_url[:50]}...")
                
                image_data = requests.get(image_url, timeout=10).content
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(image_data)
                
                logger.info(f"✓ Image saved successfully: {output_path}")
                return output_path
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                else:
                    logger.error(f"Failed to generate DALL-E image for '{title}' after {max_retries + 1} attempts: {e}")
        
        return None
    
    def generate_thumbnail_image(self, thumbnail_concept: str, title: str, tags: list, output_path: Path, max_retries: int = 2) -> Path:
        """Generate a professional YouTube thumbnail using DALL-E.
        
        Args:
            thumbnail_concept: Description of desired thumbnail
            title: Video title
            tags: Video tags for additional context
            output_path: Path to save the thumbnail
            max_retries: Number of retry attempts on failure
        
        Returns:
            Path to the generated thumbnail
        """
        # Create detailed thumbnail prompt
        tags_str = ", ".join(tags[:3]) if tags else ""
        prompt = f"""Create a professional, eye-catching YouTube thumbnail:

Title: {title}
Tags: {tags_str}

Concept: {thumbnail_concept}

Requirements:
- 1280x720 resolution (YouTube standard)
- High contrast, bold colors
- Clear, readable text areas (leave space for overlays)
- Professional, modern design
- Suitable for YouTube thumbnail
- Grab viewer attention instantly
- Avoid cluttered design"""
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Generating DALL-E thumbnail for: {title} (attempt {attempt + 1}/{max_retries + 1})")
                
                response = self.client.images.generate(
                    model=self.config.openai_image_model,
                    prompt=prompt,
                    size="1792x1024",  # Will be resized to 1280x720
                    quality="standard",
                    n=1
                )
                
                # Download and save the image
                image_url = response.data[0].url
                logger.debug(f"Thumbnail URL received: {image_url[:50]}...")
                
                image_data = requests.get(image_url, timeout=10).content
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(image_data)
                
                logger.info(f"✓ Thumbnail saved successfully: {output_path}")
                return output_path
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                else:
                    logger.error(f"Failed to generate DALL-E thumbnail for '{title}' after {max_retries + 1} attempts: {e}")
        
        return None
