@echo off
REM YouTube Content Generator - Vietnamese
REM Auto generates YouTube content with titles, tags, description, thumbnail concept, and hook

cd /d "C:\Users\xdatg\Desktop\Claude Code Skill"

echo.
echo ====================================================================
echo    YouTube Content Generator - Tiếng Việt
echo ====================================================================
echo.
echo Đang tổng hợp tin tức từ Reuters, AP, CoinGecko, Yahoo Finance...
echo Vui lòng chờ (khoảng 10-15 giây)
echo.

node build/cli.js vi

echo.
echo ====================================================================
echo    ✅ Hoàn thành! Kiểm tra file youtube-content-*.md
echo ====================================================================
echo.
pause
