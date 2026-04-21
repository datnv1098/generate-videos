# YouTube Automation Agent

Automated pipeline: **Research → Synthesize → Create Video → Upload to YouTube**

## Architecture

```
┌──────────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────┐
│  1. RESEARCH │───▶│ 2. SYNTHESIZE │───▶│ 3. CREATE    │───▶│ 4.UPLOAD │
│  (YouTube    │    │ (OpenAI       │    │    VIDEO     │    │(YouTube  │
│   Data API)  │    │  GPT-4o)      │    │ (TTS+Slides) │    │  OAuth2) │
└──────────────┘    └───────────────┘    └──────────────┘    └──────────┘
  Search topic       Analyze data        Edge-TTS audio      Auto-upload
  Get transcripts    Write script        PIL slide images    Set metadata
  Get comments       SEO optimize        MoviePy assembly    Tags/desc
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API keys in .env
#    - YOUTUBE_API_KEY (from Google Cloud Console)
#    - OPENAI_API_KEY (from OpenAI)
#    - client_secrets.json (for YouTube upload - OAuth2)

# 3. Run the agent
python main.py "your topic here"
```

## Usage

```bash
# Full pipeline (research + create + upload as private)
python main.py "artificial intelligence trends 2026"

# Create video without uploading
python main.py "python programming tips" --no-upload

# Upload as unlisted
python main.py "crypto market analysis" --privacy unlisted

# Research only (no video creation)
python main.py "machine learning" --research-only

# Custom voice and max results
python main.py "tech news" --voice en-US-GuyNeural --max-results 15

# Verbose logging
python main.py "AI" -v
```

## Setup Guide

### 1. YouTube Data API Key (for search/research)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **YouTube Data API v3**
3. Create API Key → Copy to `.env` as `YOUTUBE_API_KEY`

### 2. OpenAI API Key (for content synthesis)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create API Key → Copy to `.env` as `OPENAI_API_KEY`

### 3. YouTube OAuth2 (for uploading)
1. In Google Cloud Console → **APIs & Services** → **Credentials**
2. Create **OAuth 2.0 Client ID** (Application type: Desktop App)
3. Download JSON → Save as `client_secrets.json` in project root
4. First run will open browser for authorization

## Project Structure

```
main.py                  # CLI entry point
agent/
  config.py              # Configuration & environment
  researcher.py          # YouTube search & data collection
  synthesizer.py         # GPT-4o content generation
  video_creator.py       # TTS + slides + video assembly
  uploader.py            # YouTube OAuth2 upload
  orchestrator.py        # Pipeline coordinator
output/                  # Generated files (auto-created)
  research/              # Research data (JSON)
  scripts/               # Video scripts (JSON)
  audio/                 # TTS voiceover files
  slides/                # Generated slide images
  videos/                # Final rendered videos
```

## Output

Each run produces:
- `output/research/` - Raw research data from YouTube
- `output/scripts/` - Generated video script with metadata
- `output/audio/` - TTS voiceover MP3
- `output/slides/` - Slide images (1920x1080)
- `output/videos/` - Final rendered MP4 video
