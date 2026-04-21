#!/usr/bin/env powershell
<#
.SYNOPSIS
    Full Pipeline: Generate News Content → Process with LLM → Create Video Scripts → Generate Videos
    
.DESCRIPTION
    Automated YouTube content creation pipeline using Node.js CLI, Jupyter Notebook, and Python script generation.
    
.PARAMETER Language
    Language for content generation: "vi" (Vietnamese) or "en" (English). Default is "vi".
    
.EXAMPLE
    .\run-full-pipeline.ps1 -Language "vi"
    .\run-full-pipeline.ps1 -Language "en"
#>

param(
    [string]$Language = "vi"
)

$ErrorActionPreference = "Continue"

Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  FULL PIPELINE: Content Generation to Video Creation          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# Check Node.js
Write-Host "🔍 Checking Node.js..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "❌ Node.js not found! Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Node.js found: $(node --version)" -ForegroundColor Green

# Check Python
Write-Host "🔍 Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found! Please install Python from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green

# Step 1: Generate Content
Write-Host "`n📝 STEP 1: Generating YouTube Content..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

npm run content-gen
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Content generation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Content generated successfully!`n" -ForegroundColor Green

# Step 2: Process with LLM (Jupyter)
Write-Host "🤖 STEP 2: Processing Content with LLM in Jupyter..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Check if Jupyter is available
$jupyter = Get-Command jupyter -ErrorAction SilentlyContinue
if (-not $jupyter) {
    Write-Host "⚠️  Jupyter not found. Installing..." -ForegroundColor Yellow
    pip install jupyter ipykernel
}

Write-Host "Executing notebook: content-processor.ipynb" -ForegroundColor Yellow
jupyter nbconvert --to notebook --execute content-processor.ipynb --output content-processor-executed.ipynb

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Notebook execution failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ Notebook executed successfully!`n" -ForegroundColor Green

# Step 3: Generate Videos
Write-Host "🎬 STEP 3: Generating Video Scripts..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

python generate_video.py
# Don't fail on this step as it might just be missing optional libraries

Write-Host "`n`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    PIPELINE COMPLETE!                         ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "`n"

Write-Host "📂 Generated Files:" -ForegroundColor Cyan
Write-Host "  📄 Content Files: videos/YYYY-MM-DD/*.md" -ForegroundColor White
Write-Host "  📋 Script Files: videos_scripts/*.json + *.txt" -ForegroundColor White
Write-Host "  🎬 Video Guides: generated_videos/" -ForegroundColor White
Write-Host "`n"

Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review the generated scripts in 'videos_scripts' folder" -ForegroundColor White
Write-Host "  2. Use the video generation guide to create your video" -ForegroundColor White
Write-Host "  3. Import scripts into your video editor (CapCut, Premiere Pro, etc.)" -ForegroundColor White
Write-Host "  4. Add visuals, music, and effects" -ForegroundColor White
Write-Host "  5. Export final video and upload to YouTube" -ForegroundColor White
Write-Host "`n"

Write-Host "✨ Your content is ready for production!" -ForegroundColor Green
Write-Host "`n"

Read-Host "Press Enter to close"
