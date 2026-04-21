#!/usr/bin/env python3
"""
Direct Python execution of notebook logic for video script generation
Avoids nbconvert/Jupyter execution issues on Windows
"""

import anthropic
import markdown
import json
import re
import textwrap
import os
import dotenv
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

def read_latest_content_file(folder_path: str = "videos") -> Tuple[str, Dict]:
    """Read the latest generated content markdown file"""
    videos_dir = Path(folder_path)
    if not videos_dir.exists():
        raise FileNotFoundError(f"Videos folder not found: {folder_path}")
    
    date_folders = sorted([d for d in videos_dir.iterdir() if d.is_dir()])
    if not date_folders:
        raise FileNotFoundError("No date folders found in videos folder")
    
    latest_folder = date_folders[-1]
    md_files = list(latest_folder.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No markdown files found in {latest_folder}")
    
    vi_file = [f for f in md_files if "-vi.md" in f.name]
    md_file = vi_file[0] if vi_file else md_files[0]
    
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    return str(md_file), content

def parse_markdown_content(content: str) -> Dict:
    """Parse the markdown content and extract key sections"""
    parsed = {
        "titles": [],
        "tags": [],
        "description": "",
        "thumbnail_concept": "",
        "hook": "",
        "raw_content": content
    }
    
    try:
        # Extract titles
        title_section = re.search(r"### 🎯 TIÊU ĐỀ|### 🎯 TITLE", content, re.IGNORECASE)
        if title_section:
            title_area = content[title_section.start():]
            lines = title_area.split('\n')
            for line in lines[1:6]:
                if '**' in line and line.strip():
                    match = re.search(r"\*\*.*?:\*\*\s*(.*)", line)
                    if match and match.group(1):
                        title = match.group(1).strip()
                        if title:
                            parsed["titles"].append(title)
        
        # Extract tags
        tags_section = re.search(r"###\s*🏷️.*?TAGS.*?`([^`]+)`", content, re.IGNORECASE | re.DOTALL)
        if tags_section and tags_section.group(1):
            tags_text = tags_section.group(1)
            if tags_text:
                parsed["tags"] = [t.strip() for t in tags_text.split(",") if t.strip()]
        
        # Extract description
        desc_section = re.search(r"###\s*📝.*?(?:MÔ TẢ|DESCRIPTION).*?\n+(.*?)(?=\n---|\n###|$)", content, re.IGNORECASE | re.DOTALL)
        if desc_section and desc_section.group(1):
            desc = desc_section.group(1).strip()
            if desc:
                parsed["description"] = desc[:500]
        
        # Extract thumbnail concept
        thumb_section = re.search(r"###\s*💡.*?(?:THUMBNAIL|CONCEPT).*?\n+(.*?)(?=\n###|$)", content, re.IGNORECASE | re.DOTALL)
        if thumb_section and thumb_section.group(1):
            thumb = thumb_section.group(1).strip()
            if thumb:
                parsed["thumbnail_concept"] = thumb
        
        # Extract hook
        hook_section = re.search(r"###\s*📊.*?HOOK.*?\n+\"?(.*?)\"?(?=\n|$)", content, re.IGNORECASE | re.DOTALL)
        if hook_section and hook_section.group(1):
            hook = hook_section.group(1).strip()
            if hook:
                parsed["hook"] = hook
    except Exception as e:
        print(f"Warning during parsing: {str(e)}")
    
    # Add defaults for missing fields
    if not parsed["titles"]:
        parsed["titles"] = ["Cryptocurrency News"]
    if not parsed["tags"]:
        parsed["tags"] = ["Cryptocurrency", "Regulations", "Finance", "News"]
    if not parsed["description"]:
        parsed["description"] = f"Latest news and analysis on cryptocurrency regulations. Generated: {datetime.now().strftime('%Y-%m-%d')}"
    if not parsed["thumbnail_concept"]:
        parsed["thumbnail_concept"] = "Bold text with red/orange background, BTC symbol, and breaking news badge"
    if not parsed["hook"]:
        parsed["hook"] = "Stay informed about the latest in cryptocurrency regulations!"
    
    return parsed

def generate_video_script(parsed_content: Dict) -> Dict:
    """Use Claude API to enhance and structure the video script"""
    client = anthropic.Anthropic()
    
    prompt = f"""Based on the following YouTube video content information, create a detailed video script.

Content Details:
- Titles: {', '.join(parsed_content['titles'][:3])}
- Tags: {', '.join(parsed_content['tags'][:10])}
- Description: {parsed_content['description']}
- Thumbnail Concept: {parsed_content['thumbnail_concept']}
- Opening Hook: {parsed_content['hook']}

Please provide:
1. A structured video outline (intro, sections, conclusion)
2. Detailed script for each section (500-1000 words per section)
3. Call-to-action suggestions
4. Suggested video length and pacing

Format the response as JSON with keys: outline, detailed_script, cta, video_info"""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    try:
        # Try to parse as JSON
        script_data = json.loads(response_text)
    except json.JSONDecodeError:
        # If not valid JSON, wrap it
        script_data = {
            "outline": "See detailed_script",
            "detailed_script": response_text,
            "cta": "Subscribe and like for more content",
            "video_info": {"estimated_length": "15-20 minutes"}
        }
    
    return script_data

def save_video_script(script_data: Dict, content_file: str):
    """Save the generated script to files"""
    scripts_dir = Path("videos_scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    # Save as JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = scripts_dir / f"video_script_{timestamp}.json"
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    
    # Save as text file
    text_file = scripts_dir / f"video_guide_{timestamp}.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("VIDEO SCRIPT GUIDE\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Source: {content_file}\n\n")
        
        if isinstance(script_data.get("outline"), str):
            f.write("OUTLINE:\n")
            f.write(script_data["outline"] + "\n\n")
        
        if isinstance(script_data.get("detailed_script"), str):
            f.write("DETAILED SCRIPT:\n")
            f.write(script_data["detailed_script"] + "\n\n")
        
        if isinstance(script_data.get("cta"), str):
            f.write("CALL TO ACTION:\n")
            f.write(script_data["cta"] + "\n\n")

def main():
    """Main execution"""
    print("\n🎬 Processing content and generating video script...\n")
    
    try:
        # Read latest content
        content_file, content = read_latest_content_file()
        print(f"✓ Loaded content from: {content_file}")
        
        # Parse content
        parsed = parse_markdown_content(content)
        print(f"✓ Extracted {len(parsed['titles'])} titles and {len(parsed['tags'])} tags")
        
        # Generate script using Claude
        print("✓ Generating video script with Claude API...")
        script_data = generate_video_script(parsed)
        
        # Save scripts
        save_video_script(script_data, content_file)
        print("✓ Video scripts saved to videos_scripts/")
        
        print("\n✅ Video script generation completed!\n")
        return True
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
