"""Content Synthesis Module - Use OpenAI GPT-4o to generate video content."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from .config import Config
from .researcher import ResearchResult

logger = logging.getLogger(__name__)


@dataclass
class VideoScript:
    title: str
    description: str
    tags: list[str]
    hook: str  # Opening 15-second hook
    sections: list[dict]  # [{heading, narration, visual_notes}]
    outro: str
    thumbnail_concept: str

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "hook": self.hook,
            "sections": self.sections,
            "outro": self.outro,
            "thumbnail_concept": self.thumbnail_concept,
        }

    def get_full_narration(self) -> str:
        """Get the complete narration text for TTS."""
        parts = [self.hook]
        for section in self.sections:
            parts.append(section.get("narration", ""))
        parts.append(self.outro)
        return "\n\n".join(parts)

    def save(self, date_dir: Path, topic: str, timestamp: str) -> Path:
        filepath = date_dir / f"script_{topic.replace(' ', '_')}_{timestamp}.json"
        filepath.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Script saved to {filepath}")
        return filepath


SYSTEM_PROMPT = """You are an expert YouTube content creator and scriptwriter. 
Your job is to analyze research data from multiple YouTube videos on a topic and create 
an original, engaging video script that synthesizes the best information.

Rules:
- Create ORIGINAL content, do not copy from source videos
- Make it engaging and conversational for YouTube audience
- Include data, statistics, and specific examples
- Optimize for YouTube SEO
- Structure with clear sections for a 8-12 minute video
- Write in English only
- All fields in the JSON response must be in English
- If source comments or transcript fragments are not in English, ignore them unless their meaning is clear and can be restated in English"""

SCRIPT_PROMPT = """Based on the following research data from YouTube videos about "{topic}", 
create a complete video script.

RESEARCH DATA:
{research_data}

Create a JSON response with this exact structure:
{{
    "title": "Catchy, SEO-optimized title (max 100 chars)",
    "description": "YouTube description with timestamps and links (500+ chars)",
    "tags": ["tag1", "tag2", ...],  // 15-20 relevant tags
    "hook": "Compelling opening hook (first 15 seconds narration)",
    "sections": [
        {{
            "heading": "Section Title",
            "narration": "Full narration text for this section (2-3 paragraphs)",
            "visual_notes": "Description of what should appear on screen"
        }}
    ],
    "outro": "Closing narration with CTA (subscribe, like, comment)",
    "thumbnail_concept": "Description of ideal thumbnail design"
}}

Create 5-7 sections. Each section narration should be 100-200 words.
Write every title, description, tag, heading, narration, visual note, and outro in English only.
Respond with ONLY the JSON, no markdown formatting."""


class ContentSynthesizer:
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)

    def synthesize(self, research: ResearchResult) -> VideoScript:
        """Generate a video script from research data using GPT-4o."""
        logger.info(f"Synthesizing content for topic: '{research.topic}'")

        # Prepare research summary for the prompt
        research_summary = self._format_research(research)

        prompt = SCRIPT_PROMPT.format(
            topic=research.topic,
            research_data=research_summary,
        )

        logger.info("Calling OpenAI GPT-4o...")
        response = self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.config.max_tokens,
            temperature=0.7,
        )

        raw_content = response.choices[0].message.content.strip()

        # Parse JSON response
        # Handle cases where LLM wraps in ```json blocks
        if raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1]
            if raw_content.startswith("json"):
                raw_content = raw_content[4:]

        script_data = json.loads(raw_content)

        script = VideoScript(
            title=script_data["title"],
            description=script_data["description"],
            tags=script_data["tags"],
            hook=script_data["hook"],
            sections=script_data["sections"],
            outro=script_data["outro"],
            thumbnail_concept=script_data.get("thumbnail_concept", ""),
        )

        # Save script
        script.save(self.config.today_dir("scripts"), research.topic, research.timestamp)

        logger.info(f"Script generated: '{script.title}' ({len(script.sections)} sections)")
        return script

    def _format_research(self, research: ResearchResult) -> str:
        """Format research data into a concise prompt-friendly string."""
        parts = [f"Topic: {research.topic}\n"]

        for i, video in enumerate(research.videos[:7], 1):  # Top 7 videos
            parts.append(f"--- Video {i} ---")
            parts.append(f"Title: {video.title}")
            parts.append(f"Channel: {video.channel}")
            parts.append(f"Views: {video.view_count:,} | Likes: {video.like_count:,}")

            if video.transcript:
                # Send first ~1500 chars of transcript
                parts.append(f"Transcript excerpt: {video.transcript[:1500]}")

            if video.top_comments:
                parts.append(f"Top comments: {' | '.join(video.top_comments[:5])}")

            parts.append("")

        return "\n".join(parts)
