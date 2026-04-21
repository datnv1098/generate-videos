#!/usr/bin/env powershell
<#
.SYNOPSIS
    One Command Video Creator - Create YouTube videos with a single command!
    
.DESCRIPTION
    Automated YouTube content creation: News → Content → LLM Processing → Video Script
    
.PARAMETER Language
    Language for content generation: "vi" (Vietnamese, default) or "en" (English)
    
.PARAMETER Quick
    Enable quick mode - skip some validations
    
.EXAMPLE
    .\create-video.ps1                    # Default (Vietnamese)
    .\create-video.ps1 -Language "en"     # English
    .\create-video.ps1 -Quick             # Quick mode
    .\create-video.ps1 -Language "en" -Quick
#>

param(
    [string]$Language = "vi",
    [switch]$Quick
)

$ErrorActionPreference = "Continue"

# Color output
function Write-Header {
    param([string]$Text)
    Write-Host "`n" -ForegroundColor White
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Text.PadRight(60)║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "`n"
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Main
Write-Header "🎬 ULTIMATE YOUTUBE VIDEO CREATOR"

Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Check Python
Write-Info "Checking Python installation..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error-Custom "Python not found!"
    Write-Info "Install from: https://www.python.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Success "Python found: $(python --version)"

# Build arguments
$arguments = @()
if ($Language -and $Language -ne "vi") {
    $arguments += @("--lang", $Language)
}
if ($Quick) {
    $arguments += "--quick"
}

# Show configuration
Write-Host "`n📋 Configuration:" -ForegroundColor White
Write-Host "  Language: $Language" -ForegroundColor Gray
if ($Quick) {
    Write-Host "  Mode: Quick (fast mode enabled)" -ForegroundColor Yellow
}

# Run Python script
Write-Host "`n" -ForegroundColor White
Write-Info "Running pipeline..."

python create_video.py $arguments
$exitCode = $LASTEXITCODE

# Summary
if ($exitCode -eq 0) {
    Write-Host "`n" -ForegroundColor White
    Write-Header "✨ PIPELINE COMPLETE! ✨"
    
    Write-Host "📂 Files generated in:" -ForegroundColor White
    Write-Host "  • videos/YYYY-MM-DD/       (Markdown content)" -ForegroundColor Gray
    Write-Host "  • videos_scripts/          (JSON scripts + text guides)" -ForegroundColor Gray
    Write-Host "  • generated_videos/        (Video resources)" -ForegroundColor Gray
    
    Write-Host "`n📋 Next Steps:" -ForegroundColor White
    Write-Host "  1. Review scripts in videos_scripts/ folder" -ForegroundColor Gray
    Write-Host "  2. Open script_*.txt in any text editor" -ForegroundColor Gray
    Write-Host "  3. Use in video editor (CapCut, DaVinci, Premiere)" -ForegroundColor Gray
    Write-Host "  4. Add visuals, music, effects" -ForegroundColor Gray
    Write-Host "  5. Export and upload to YouTube!" -ForegroundColor Gray
    
    Write-Host "`n✨ Your content is ready for video production!" -ForegroundColor Green
} else {
    Write-Error-Custom "Pipeline failed with exit code: $exitCode"
    Write-Info "Check logs above for details"
}

Write-Host "`n"
Read-Host "Press Enter to close"
exit $exitCode
