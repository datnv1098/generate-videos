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
an original, engaging video script that synthesizes the best information with INSPIRING and EMOTIONAL tone.

Rules:
- Create ORIGINAL content, do not copy from source videos
- Make it ENGAGING, INSPIRATIONAL, and CONVERSATIONAL for YouTube audience
- Write narration that moves and inspires viewers emotionally
- Include data, statistics, and specific examples that support your emotional message
- Optimize for YouTube SEO
- Structure with clear sections for a 12-15 minute video
- Write in English only for main content
- All fields in the JSON response must be in English (EXCEPT visual_notes_vi which must be in Vietnamese)
- If source comments or transcript fragments are not in English, ignore them unless their meaning is clear and can be restated in English
- MINIMUM 10 SECTIONS REQUIRED - each section must cover a distinct aspect of the topic
- Use inspiring language that connects emotionally with the audience
- Each section should build on previous insights and drive viewers toward action"""

SCRIPT_PROMPT = """Based on the following research data from YouTube videos about "{topic}", 
create a comprehensive video script with AT LEAST 10 DETAILED SECTIONS using INSPIRING and EMOTIONAL tone.

RESEARCH DATA:
{research_data}

Create a JSON response with this exact structure:
{{
    "title": "Catchy, SEO-optimized title (max 100 chars)",
    "description": "YouTube description with timestamps and links (500+ chars)",
    "tags": ["tag1", "tag2", ...],  // 15-20 relevant tags
    "hook": "Compelling opening hook (first 15 seconds narration) - MUST BE INSPIRING",
    "sections": [
        {{
            "heading": "Section Title",
            "narration": "Full narration text for this section (150-250 words) - WRITE WITH INSPIRATION AND EMOTION",
            "visual_notes": "Description of what should appear on screen in English",
            "visual_notes_vi": "Mô tả nội dung video này nói về cái gì? (Vietnamese description of what this section covers)"
        }}
    ],
    "outro": "Closing narration with CTA (subscribe, like, comment) - INSPIRING CALL TO ACTION",
    "thumbnail_concept": "Description of ideal thumbnail design"
}}

CRITICAL REQUIREMENTS:
- Create EXACTLY 10-15 sections (no fewer than 10, no more than 15)
- Each section heading must be unique and cover a distinct topic/aspect
- Each section narration must be 150-250 words, written with INSPIRING and EMOTIONAL tone
- Sections should cover: introduction, key concepts, analysis, examples, implications, and conclusions
- Vary the section types: explanatory, analytical, practical, visionary, inspirational
- Use inspiring language like "imagine", "discover", "transform", "empower", "breakthrough", "unlock", "journey"
- Include emotional hooks that connect with viewers
- Connect data and facts to human stories and impact
- For "visual_notes_vi": Write ONLY in Vietnamese (tiếng Việt), describe what content/topic this section is about (e.g. "Phân tích về tác động của lãi suất", "Dự báo thị trường năm 2026")
- Write every title, description, tag, heading, narration, visual note, and outro in English only (EXCEPT visual_notes_vi which is VIETNAMESE ONLY)
- Respond with ONLY the JSON, no markdown formatting or explanation."""


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

        # Validate minimum sections requirement
        num_sections = len(script_data.get("sections", []))
        if num_sections < 10:
            logger.warning(
                f"Script has only {num_sections} sections, but minimum 10 required. "
                f"Regenerating with emphasis on comprehensive coverage..."
            )
            # Regenerate with explicit instruction
            enhanced_prompt = SCRIPT_PROMPT.format(
                topic=research.topic,
                research_data=research_summary,
            ) + "\n\nIMPORTANT: The previous attempt had fewer than 10 sections. " \
                "You MUST create exactly 10-15 sections. Each section must be substantial and distinct."
            
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": enhanced_prompt},
                ],
                max_tokens=self.config.max_tokens,
                temperature=0.7,
            )
            
            raw_content = response.choices[0].message.content.strip()
            if raw_content.startswith("```"):
                raw_content = raw_content.split("```")[1]
                if raw_content.startswith("json"):
                    raw_content = raw_content[4:]
            
            script_data = json.loads(raw_content)
            num_sections = len(script_data.get("sections", []))
            
            if num_sections < 10:
                logger.error(
                    f"Failed to generate minimum 10 sections after retry. "
                    f"Got {num_sections} sections. This video may be too short."
                )

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
        
        # Display Vietnamese content summary for user reference
        self._display_vietnamese_summary(script)
        
        return script

    def _display_vietnamese_summary(self, script: VideoScript) -> None:
        """Display Vietnamese visual notes summary for user reference."""
        summary_lines = [
            "\n" + "=" * 70,
            "  NỘI DUNG VIDEO - TIẾNG VIỆT (Video Content Summary in Vietnamese)",
            "=" * 70,
            f"  Chủ đề: {script.title}",
            "",
            "  Các phần nội dung được đăng (Video Sections):",
            "",
        ]
        
        for i, section in enumerate(script.sections, 1):
            heading = section.get("heading", "")
            visual_notes_vi = section.get("visual_notes_vi", "")
            summary_lines.append(f"  {i}. {heading}")
            if visual_notes_vi:
                summary_lines.append(f"     → {visual_notes_vi}")
            summary_lines.append("")
        
        summary_lines.extend([
            "=" * 70,
            "",
        ])
        
        summary_text = "\n".join(summary_lines)
        logger.info(summary_text)
        print(summary_text)

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
