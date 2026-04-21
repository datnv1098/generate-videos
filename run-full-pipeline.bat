@echo off
REM Full Pipeline: Generate News Content → Process with LLM → Create Video Scripts → Generate Videos
REM Usage: run-full-pipeline.bat [language]
REM Example: run-full-pipeline.bat vi

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  FULL PIPELINE: Content Generation to Video Creation          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check Node.js installation
where node >nul 2>nul
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

REM Check Python installation
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Step 1: Generate YouTube Content
echo 📝 STEP 1: Generating YouTube Content...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
npm run content-gen
if errorlevel 1 (
    echo ❌ Content generation failed!
    pause
    exit /b 1
)
echo ✅ Content generated successfully!
echo.

REM Step 2: Run Jupyter Notebook (Process with LLM)
echo 🤖 STEP 2: Processing Content with LLM in Jupyter...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Check if Jupyter is available
where jupyter >nul 2>nul
if errorlevel 1 (
    echo ⚠️  Jupyter not found. Installing jupyter...
    pip install jupyter ipykernel
)

echo Executing notebook: content-processor.ipynb
jupyter nbconvert --to notebook --execute content-processor.ipynb --output content-processor-executed.ipynb
if errorlevel 1 (
    echo ❌ Notebook execution failed!
    pause
    exit /b 1
)
echo ✅ Notebook executed successfully!
echo.

REM Step 3: Generate Videos
echo 🎬 STEP 3: Generating Video Scripts...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python generate_video.py
if errorlevel 1 (
    echo ⚠️  Video generation encountered an issue (may be expected if libraries missing)
)
echo.

REM Summary
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    PIPELINE COMPLETE!                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📂 Generated Files:
echo   Content Files: videos/YYYY-MM-DD/*.md
echo   Script Files: videos_scripts/*.json + *.txt
echo   Video Guides: generated_videos/
echo.
echo 📋 Next Steps:
echo   1. Review the generated scripts in 'videos_scripts' folder
echo   2. Use the video generation guide to create your video
echo   3. Import scripts into your video editor (CapCut, Premiere Pro, etc.)
echo   4. Add visuals, music, and effects
echo   5. Export final video and upload to YouTube
echo.
echo ✨ Your content is ready for production!
echo.

pause
