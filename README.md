# 🎬 YouTube Content Creation Pipeline

Một hệ thống tự động hoàn chỉnh để tạo nội dung YouTube từ tin tức → xử lý LLM → tạo video script.

## 🎯 Tổng Quan

Pipeline này gồm 3 bước chính:

1. **📝 Content Generation** - Fetch tin tức từ nhiều nguồn (chính trị, crypto, thị trường)
2. **🤖 LLM Processing** - Xử lý nội dung qua Claude API để tạo script video chuyên nghiệp
3. **🎬 Video Script Creation** - Tạo video scripts với timing, visual guides, và metadata

## 📋 Yêu Cầu

- **Node.js 18+** (với npm)
- **Python 3.8+**
- **YouTube API Key** (từ Google Cloud Console)
- **Anthropic API Key** (từ Claude.ai)

## ⚙️ Cài Đặt

### 1. Clone hoặc setup project

```bash
cd "Claude Code Skill"
```

### 2. Cài đặt Node dependencies

```bash
npm install
```

### 3. Cài đặt Python dependencies (tùy chọn, cho Jupyter)

```bash
pip install jupyter ipykernel anthropic
```

### 4. Cấu hình API Keys

Tạo file `.env` trong thư mục project:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Lấy API keys:
- **YouTube API**: https://console.cloud.google.com/
- **Anthropic API**: https://console.anthropic.com/

## 🚀 Chạy Pipeline

### Cách 1: Batch Script (Windows) - Tự động toàn bộ

```bash
run-full-pipeline.bat
```

### Cách 2: Từng bước

#### Bước 1: Tạo nội dung (CLI)

```bash
npm run content-gen
```

Điều này sẽ:
- Fetch top 5 tin tức chính trị Mỹ
- Fetch top 5 tin tức crypto (BTC/ETH)
- Fetch top 5 tin tức thị trường (vàng, cổ phiếu)
- Fetch tin tức việc làm
- Tạo file markdown: `videos/YYYY-MM-DD/youtube-content-YYYY-MM-DD-{vi|en}.md`

#### Bước 2: Xử lý với LLM (Jupyter Notebook)

```bash
jupyter notebook content-processor.ipynb
```

Hoặc tự động:

```bash
jupyter nbconvert --to notebook --execute content-processor.ipynb
```

Notebook sẽ:
1. Đọc file markdown mới nhất
2. Parse nội dung (titles, tags, description, hook)
3. Gửi đến Claude API để enhance
4. Tạo video script với timing và visual notes
5. Export thành JSON và text formats

#### Bước 3: Tạo video scripts

```bash
python generate_video.py
```

Tạo:
- Hướng dẫn tạo video
- Danh sách công cụ khuyến nghị (CapCut, Premiere Pro, DaVinci Resolve)
- Thumbnail design notes
- YouTube upload metadata

## 📁 Cấu Trúc Thư Mục

```
Claude Code Skill/
├── src/
│   ├── index.ts              # MCP Server (11 tools)
│   └── cli.ts                # CLI Content Generator
├── build/                    # Compiled JavaScript
├── content-processor.ipynb   # Jupyter notebook (LLM processing)
├── generate_video.py         # Video script generator
├── run-full-pipeline.bat     # Automated pipeline
├── package.json
├── tsconfig.json
├── .env                      # API keys
│
├── videos/                   # Generated content
│   └── 2026-04-20/
│       ├── youtube-content-2026-04-20-vi.md
│       └── youtube-content-2026-04-20-en.md
│
├── videos_scripts/           # Processed scripts
│   ├── script_2026-04-20_Title.json
│   └── script_2026-04-20_Title.txt
│
└── generated_videos/         # Video resources
    ├── audio_temp/
    ├── title_slide.png
    └── (video generation outputs)
```

## 🛠️ Công Cụ Có Sẵn (MCP Server)

Khi đã setup Claude Desktop, có thể sử dụng các tool:

### YouTube Research
- `search_videos` - Tìm video YouTube
- `get_video_info` - Lấy thông tin video
- `get_video_comments` - Lấy comments từ video
- `get_video_transcript` - Lấy transcript
- `get_channel_info` - Thông tin channel
- `analyze_video_sentiment` - Phân tích sentiment

### News Aggregation
- `get_us_politics_news` - Tin chính trị Mỹ
- `get_crypto_news` - Tin crypto
- `get_market_news` - Tin thị trường
- `get_employment_news` - Tin việc làm
- `generate_youtube_content` - Tạo nội dung (built-in)

## 📊 Dữ Liệu Nguồn

- **US Politics**: Reuters, AP News
- **Crypto**: CoinTelegraph, CoinDesk, CoinGecko
- **Markets**: Yahoo Finance, MarketWatch, Bloomberg
- **Employment**: Bureau of Labor Statistics, LinkedIn
- **Prices**: CoinGecko API (free, no auth)

## 📝 Output Format

### Markdown Content (Step 1)

```markdown
# [NEWS DATE]

## CHÍNH TRỊ MỸ (US POLITICS)

### Tin 1: [Title]
- **Tags:** tag1, tag2
- **Description:** [Content]
- **Hook:** [Engaging opening]
- **Thumbnail Concept:** [Design idea]

## CRYPTO

### Tin 1: ...
```

### Video Script (Step 3)

```json
{
  "title": "Market Update - April 20, 2026",
  "duration_minutes": 18,
  "tags": ["finance", "crypto", "markets"],
  "sections": [
    {
      "time_start": "00:00",
      "time_end": "00:15",
      "title": "Opening Hook",
      "content": "...",
      "visual_notes": "..."
    }
  ]
}
```

## 🎬 Tạo Video Cuối Cùng

Sau khi có video script, có thể dùng:

### Free Tools
- **CapCut** (Web): capcut.com - Dễ sử dụng, free
- **DaVinci Resolve** (Desktop): blackmagicdesign.com - Professional, free
- **Shotcut** (Desktop): shotcut.org - Open source
- **OpenShot** (Desktop): openshot.org - Simple

### Paid Tools
- **Adobe Premiere Pro** - Industry standard
- **Final Cut Pro** - macOS
- **Vegas Pro** - Windows

### Workflow

1. ✅ Tạo content với pipeline (bạn đã làm)
2. 📥 Import script vào video editor
3. 🎨 Add visuals (B-roll, charts, news footage)
4. 🎵 Add background music (YouTube Audio Library)
5. 📝 Add text overlays với timing
6. 🔄 Add transitions và effects
7. 🎬 Color grade
8. 📤 Export (MP4, H.264, 1080p)
9. 📱 Upload YouTube + Metadata

## 🔧 Troubleshooting

### "Module not found" errors
```bash
npm install
```

### YouTube API errors
- Kiểm tra API key trong `.env`
- Verify YouTube Data API v3 enabled
- Check API quotas

### Anthropic API errors
- Verify API key trong `.env`
- Check account credits
- Rate limiting

### Jupyter not found
```bash
pip install jupyter ipykernel
```

### FFmpeg not found (for video generation)
```bash
# Windows (choco)
choco install ffmpeg

# macOS (brew)
brew install ffmpeg

# Linux (apt)
sudo apt install ffmpeg
```

## 📚 API Documentation

- [YouTube API v3](https://developers.google.com/youtube/v3)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🎓 Ví Dụ Sử Dụng

### Chỉ tạo nội dung (không cần video)
```bash
npm run content-gen
```

### Chỉ process Jupyter
```bash
jupyter notebook content-processor.ipynb
```

### Full pipeline (recommended)
```bash
run-full-pipeline.bat
```

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra API keys trong `.env`
2. Chạy `npm run build` để compile TypeScript
3. Kiểm tra các dependencies: `npm list`
4. Xem logs từ MCP server

## 🚀 Next Steps

Sau khi tạo video:

1. **Optimize cho YouTube**
   - Title: < 60 characters
   - Description: Include links, timestamps
   - Tags: 5-10 relevant tags
   - Thumbnail: 1280x720px

2. **Promote**
   - Add to playlist
   - Create shorts từ best parts
   - Share on social media

3. **Monitor**
   - Track analytics
   - Respond to comments
   - Iterate based on performance

## 📜 License

MIT - Free to use and modify

---

**Created with ❤️ for content creators**

Chi tiết thêm về cách sử dụng các tool từ Claude Desktop, xem `.github/copilot-instructions.md`
