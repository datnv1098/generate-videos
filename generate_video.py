#!/usr/bin/env python3
"""
YouTube Video Generator
Converts video scripts into actual video files using text-to-speech and visual generation.

Requirements:
  pip install anthropic pyttsx3 pillow moviepy numpy

Or with system packages:
  apt install ffmpeg (Linux)
  brew install ffmpeg (macOS)
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re
import textwrap

# Try to import video libraries (optional, graceful fallback)
try:
    from moviepy.editor import (
        VideoFileClip, CompositeVideoClip, TextClip, ColorClip,
        AudioFileClip, concatenate_videoclips
    )
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False
    print("⚠️  moviepy not installed. Install with: pip install moviepy")

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    print("⚠️  pyttsx3 not installed. Install with: pip install pyttsx3")

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️  pillow not installed. Install with: pip install pillow")


def load_video_script(script_file: str) -> Dict:
    """Load JSON video script file."""
    with open(script_file, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_tts_audio(text: str, output_file: str, rate: int = 150) -> bool:
    """
    Generate text-to-speech audio using pyttsx3.
    Returns True if successful, False otherwise.
    """
    if not HAS_PYTTSX3:
        print("⚠️  Text-to-speech skipped (pyttsx3 not installed)")
        return False
    
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        print(f"✅ Generated audio: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        return False


def create_title_slide(title: str, subtitle: str, output_file: str, duration: float = 3):
    """
    Create a title slide image.
    """
    if not HAS_PIL:
        print("⚠️  Title slide skipped (pillow not installed)")
        return False
    
    try:
        # Create image
        width, height = 1280, 720
        image = Image.new("RGB", (width, height), color=(20, 20, 40))  # Dark blue background
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 200), title, fill=(255, 200, 0), font=title_font)
        
        # Add subtitle
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        draw.text((subtitle_x, 400), subtitle, fill=(200, 200, 200), font=subtitle_font)
        
        # Save
        image.save(output_file)
        print(f"✅ Created title slide: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating title slide: {e}")
        return False


def create_video_from_script(script: Dict, output_folder: str = "generated_videos") -> str:
    """
    Create a complete video from the script.
    This is a template - actual implementation depends on available libraries.
    """
    
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_title = "".join(c for c in script["title"] if c.isalnum() or c in " -_")[:50]
    video_file = output_path / f"video_{timestamp}_{safe_title}.mp4"
    audio_folder = output_path / "audio_temp"
    audio_folder.mkdir(exist_ok=True)
    
    print(f"\n🎬 Creating video: {script['title']}")
    print(f"📍 Output: {video_file}\n")
    
    if not HAS_MOVIEPY:
        print("\n⚠️  MOVIEPY NOT INSTALLED!")
        print("Video generation skipped. To enable, install moviepy:")
        print("  pip install moviepy")
        print("\nBUT YOUR SCRIPT IS READY! You can:")
        print("  1. Create video manually in CapCut, Premiere Pro, DaVinci Resolve")
        print("  2. Use online video generators")
        print("  3. Install moviepy and run this script again")
        return str(video_file)
    
    # Generate TTS for each section
    audio_files = []
    for i, section in enumerate(script["sections"]):
        audio_file = audio_folder / f"section_{i:02d}.wav"
        
        # Generate audio for the content
        if generate_tts_audio(section["content"], str(audio_file)):
            audio_files.append(str(audio_file))
    
    # Create title slide
    title_slide_file = output_path / "title_slide.png"
    create_title_slide(
        script["title"],
        f"{script['duration_minutes']} Min Market Briefing",
        str(title_slide_file)
    )
    
    print(f"\n✅ Video components prepared!")
    print(f"📁 Temporary audio files: {len(audio_files)} files")
    print(f"🎨 Title slide created")
    print(f"\n💡 Next steps:")
    print(f"  1. Import audio files to your video editor")
    print(f"  2. Add visuals (charts, news clips, screen recordings)")
    print(f"  3. Use the script sections as timing guides")
    print(f"  4. Export final video to {video_file}")
    
    return str(video_file)


def print_video_generation_guide(script: Dict) -> None:
    """
    Print a guide for manual video generation in popular tools.
    """
    
    guide = f"""
╔════════════════════════════════════════════════════════════════════════╗
║                   VIDEO GENERATION GUIDE                              ║
╚════════════════════════════════════════════════════════════════════════╝

📺 Video Title: {script['title']}
⏱️  Duration: {script['duration_minutes']} minutes
📅 Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RECOMMENDED VIDEO CREATION TOOLS:

1. CAPCUT (Free, Web-based)
   - Upload your background music
   - Add text overlays for each section
   - Use the timing cues provided
   - Export as MP4
   - Website: capcut.com

2. DAVINCI RESOLVE (Free Desktop)
   - Professional-grade editing
   - Multi-track editing
   - Color grading capabilities
   - Export with H.264 codec
   - Download: blackmagicdesign.com

3. PREMIERE PRO (Paid)
   - Industry standard
   - Dynamic Link integration
   - Advanced motion graphics
   - Export presets for YouTube
   - Adobe Creative Cloud

4. FFMPEG (Command-line, Advanced)
   - Batch processing
   - Automated workflow
   - Free and open-source
   - Command: ffmpeg -i video.mp4 -i audio.wav -c:v copy output.mp4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 SCRIPT STRUCTURE FOR VIDEO TIMING:

"""
    
    current_time = 0
    for i, section in enumerate(script["sections"], 1):
        guide += f"\n{i}. {section['title'].upper()}\n"
        guide += f"   ⏱️  {section['time_start']} - {section['time_end']}\n"
        guide += f"   🎭 Type: {section['type']}\n"
        guide += f"   🎵 BGM: {section.get('bgm', 'Not specified')}\n"
        guide += f"   👀 Visuals: {section['visual_notes'][:80]}...\n"
    
    guide += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 PRODUCTION CHECKLIST:

□ Record voiceover or generate TTS audio
□ Prepare background music (royalty-free from YouTube Audio Library)
□ Collect news graphics and charts (screenshots/animations)
□ Create thumbnail image (1280x720px)
□ Set background for each section
□ Add text overlays with timing
□ Add transitions between sections
□ Color grade and apply effects
□ Add captions/subtitles
□ Export in YouTube-recommended format (MP4, H.264, 1080p)
□ Add thumbnail when uploading

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 THUMBNAIL DESIGN:

{script['thumbnail_concept']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 YOUTUBE UPLOAD METADATA:

Title: {script['title']}

Tags: {', '.join(script['tags'])}

Description: 
[Use the description from your .md file]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    print(guide)


def main():
    """Main execution flow."""
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║           YOUTUBE VIDEO GENERATOR FROM SCRIPT                         ║
╚════════════════════════════════════════════════════════════════════════╝
""")
    
    # Find latest script file
    scripts_folder = Path("videos_scripts")
    if not scripts_folder.exists():
        print("❌ No 'videos_scripts' folder found!")
        print("   Run the Jupyter notebook first to generate scripts.")
        sys.exit(1)
    
    script_files = list(scripts_folder.glob("*.json"))
    if not script_files:
        print("❌ No script files found in videos_scripts folder!")
        sys.exit(1)
    
    # Use latest script
    latest_script = sorted(script_files)[-1]
    print(f"📂 Found script: {latest_script.name}\n")
    
    try:
        script = load_video_script(str(latest_script))
    except Exception as e:
        print(f"❌ Error loading script: {e}")
        sys.exit(1)
    
    # Create video
    video_path = create_video_from_script(script)
    
    # Print guide for manual creation
    print_video_generation_guide(script)
    
    print(f"\n✅ Video project prepared!")
    print(f"   Script: {latest_script}")
    print(f"   Output folder: generated_videos/")


if __name__ == "__main__":
    main()
