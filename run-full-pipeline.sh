#!/bin/bash

# Full Pipeline: Generate News Content → Process with LLM → Create Video Scripts → Generate Videos
# Usage: ./run-full-pipeline.sh [language]
# Example: ./run-full-pipeline.sh vi

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  FULL PIPELINE: Content Generation to Video Creation          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Node.js
echo "🔍 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Install from https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check Python
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found! Install from https://www.python.org/"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Step 1: Generate Content
echo ""
echo "📝 STEP 1: Generating YouTube Content..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

npm run content-gen
if [ $? -ne 0 ]; then
    echo "❌ Content generation failed!"
    exit 1
fi
echo "✅ Content generated successfully!"
echo ""

# Step 2: Process with LLM (Jupyter)
echo "🤖 STEP 2: Processing Content with LLM in Jupyter..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Jupyter is available
if ! command -v jupyter &> /dev/null; then
    echo "⚠️  Jupyter not found. Installing..."
    pip3 install jupyter ipykernel
fi

echo "Executing notebook: content-processor.ipynb"
jupyter nbconvert --to notebook --execute content-processor.ipynb --output content-processor-executed.ipynb

if [ $? -ne 0 ]; then
    echo "❌ Notebook execution failed!"
    exit 1
fi
echo "✅ Notebook executed successfully!"
echo ""

# Step 3: Generate Videos
echo "🎬 STEP 3: Generating Video Scripts..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 generate_video.py
# Don't fail on this step as it might just be missing optional libraries

echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    PIPELINE COMPLETE!                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "📂 Generated Files:"
echo "  📄 Content Files: videos/YYYY-MM-DD/*.md"
echo "  📋 Script Files: videos_scripts/*.json + *.txt"
echo "  🎬 Video Guides: generated_videos/"
echo ""

echo "📋 Next Steps:"
echo "  1. Review the generated scripts in 'videos_scripts' folder"
echo "  2. Use the video generation guide to create your video"
echo "  3. Import scripts into your video editor (CapCut, Premiere Pro, etc.)"
echo "  4. Add visuals, music, and effects"
echo "  5. Export final video and upload to YouTube"
echo ""

echo "✨ Your content is ready for production!"
echo ""
