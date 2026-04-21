@echo off
REM YouTube Content Generator - English
REM Auto generates YouTube content with titles, tags, description, thumbnail concept, and hook

cd /d "C:\Users\xdatg\Desktop\Claude Code Skill"

echo.
echo ====================================================================
echo    YouTube Content Generator - English
echo ====================================================================
echo.
echo Fetching news from Reuters, AP, CoinGecko, Yahoo Finance...
echo Please wait (approximately 10-15 seconds)
echo.

node build/cli.js en

echo.
echo ====================================================================
echo    ✅ Done! Check the generated youtube-content-*.md file
echo ====================================================================
echo.
pause
