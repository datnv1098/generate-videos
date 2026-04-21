#!/bin/bash

# 🎬 One Command Video Creator
# Tạo YouTube video chỉ với 1 lệnh duy nhất!
#
# Usage:
#   ./create-video.sh              (Default - Vietnamese)
#   ./create-video.sh en           (English)
#   ./create-video.sh quick        (Quick mode)
#

set -e

# Colors
HEADER='\033[95m'
OKBLUE='\033[94m'
OKCYAN='\033[96m'
OKGREEN='\033[92m'
WARNING='\033[93m'
FAIL='\033[91m'
ENDC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${HEADER}${BOLD}╔════════════════════════════════════════════════════════════════╗${ENDC}"
echo -e "${HEADER}${BOLD}║  ✨ ULTIMATE YOUTUBE VIDEO CREATOR ✨                         ║${ENDC}"
echo -e "${HEADER}${BOLD}╚════════════════════════════════════════════════════════════════╝${ENDC}"
echo ""

# Check Python
echo -e "${OKCYAN}Checking Python installation...${ENDC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${FAIL}❌ Python3 not found!${ENDC}"
    echo -e "${OKBLUE}ℹ️  Install from: https://www.python.org/${ENDC}"
    exit 1
fi
echo -e "${OKGREEN}✅ Python found: $(python3 --version)${ENDC}"

# Run Python script
echo ""
echo -e "${OKBLUE}ℹ️  Running pipeline...${ENDC}"
echo ""

python3 create_video.py "$@"
exit_code=$?

# Summary
if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${OKGREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${ENDC}"
    echo -e "${OKGREEN}${BOLD}✨ PIPELINE COMPLETE! ✨${ENDC}"
    echo -e "${OKGREEN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${ENDC}"
    echo ""
    
    echo -e "${BOLD}📂 Files generated in:${ENDC}"
    echo "  • videos/YYYY-MM-DD/       (Markdown content)"
    echo "  • videos_scripts/          (JSON scripts + text guides)"
    echo "  • generated_videos/        (Video resources)"
    
    echo ""
    echo -e "${BOLD}📋 Next Steps:${ENDC}"
    echo "  1. Review scripts in videos_scripts/ folder"
    echo "  2. Open script_*.txt in any text editor"
    echo "  3. Use in video editor (CapCut, DaVinci, Premiere)"
    echo "  4. Add visuals, music, effects"
    echo "  5. Export and upload to YouTube!"
    
    echo ""
    echo -e "${OKGREEN}✨ Your content is ready for video production!${ENDC}"
    echo ""
else
    echo -e "${FAIL}❌ Pipeline failed with exit code: $exit_code${ENDC}"
    echo -e "${OKBLUE}ℹ️  Check logs above for details${ENDC}"
    echo ""
fi

exit $exit_code
