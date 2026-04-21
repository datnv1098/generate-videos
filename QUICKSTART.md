# 🚀 Quick Start Guide

Hướng dẫn nhanh để bắt đầu tạo nội dung YouTube tự động!

## 1️⃣ Chuẩn Bị (5 phút)

### Cài đặt phần mềm cần thiết
```bash
# Node.js: https://nodejs.org/
# Python: https://www.python.org/
# Git (tùy chọn): https://git-scm.com/
```

### Clone project
```bash
cd Desktop
git clone <repo-url>
cd "Claude Code Skill"
```

### Cài dependencies
```bash
npm install
```

## 2️⃣ Lấy API Keys (5 phút)

### YouTube API Key
1. Truy cập: https://console.cloud.google.com/
2. Tạo project mới
3. Bật **YouTube Data API v3**
4. Tạo **API Key**
5. Copy key vào `.env`

### Anthropic API Key
1. Truy cập: https://console.anthropic.com/
2. Đăng nhập với tài khoản Claude
3. Copy **API Key**
4. Thêm vào `.env`

### Tạo `.env` file
```bash
# .env
YOUTUBE_API_KEY=sk-...your-key-here...
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

## 3️⃣ Chạy Pipeline (3 phút)

### Option A: Tự động (Recommended) ⭐

**Windows CMD:**
```bash
run-full-pipeline.bat
```

**Windows PowerShell:**
```powershell
.\run-full-pipeline.ps1
```

**macOS/Linux:**
```bash
bash run-full-pipeline.sh  # (if available)
```

### Option B: Từng bước

**Bước 1: Tạo nội dung**
```bash
npm run content-gen
```
✅ Tạo: `videos/2026-04-20/youtube-content-2026-04-20-vi.md`

**Bước 2: Xử lý với LLM**
```bash
npm run notebook-exec
```
✅ Tạo: `videos_scripts/script_2026-04-20_*.json`

**Bước 3: Tạo hướng dẫn video**
```bash
npm run generate-video
```
✅ Tạo: `generated_videos/` với guides

## 4️⃣ Xem Kết Quả

### Nơi tìm files
```
📂 Claude Code Skill/
├── 📁 videos/               (Markdown content)
├── 📁 videos_scripts/       (JSON scripts + text guides)
└── 📁 generated_videos/     (Video resources)
```

### Files được tạo
- `youtube-content-YYYY-MM-DD-vi.md` - Nội dung tin tức (Markdown)
- `script_YYYY-MM-DD_Title.json` - Script video (JSON, dùng cho tools)
- `script_YYYY-MM-DD_Title.txt` - Script video (Text, dễ đọc)

## 5️⃣ Tạo Video Cuối Cùng

### Công cụ khuyến nghị
1. **CapCut** (Web, Free) - https://capcut.com ⭐
2. **DaVinci Resolve** (Desktop, Free) - https://blackmagicdesign.com
3. **Premiere Pro** (Professional) - Adobe Creative Cloud

### Workflow
1. ✅ Copy script từ `videos_scripts/`
2. 🎥 Mở CapCut/DaVinci/Premiere
3. 📝 Thêm text overlays với timing từ script
4. 🎨 Add visuals (charts, news screenshots, B-roll)
5. 🎵 Add background music (YouTube Audio Library)
6. 🔄 Add transitions & effects
7. 📤 Export MP4
8. 📱 Upload YouTube

## 🎓 Ví Dụ

### Chỉ tạo markdown content
```bash
npm run content-gen
```

### Chỉ chạy Jupyter notebook
```bash
npm run notebook-exec
```

### Chạy tất cả
```bash
npm run pipeline
```

## 🔧 Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"
- ✅ Kiểm tra `.env` file tồn tại
- ✅ Verify API key không có khoảng trắng
- ✅ Restart terminal sau khi thêm `.env`

### Error: "YouTube API quota exceeded"
- ✅ Check quota tại: https://console.cloud.google.com/
- ✅ Đợi 24h để reset
- ✅ Hoặc upgrade to paid plan

### Jupyter not found
```bash
pip install jupyter ipykernel
```

### Missing Python packages
```bash
pip install anthropic
```

## 📞 Cần Giúp?

### Resources
- MCP Docs: https://modelcontextprotocol.io/
- YouTube API: https://developers.google.com/youtube/v3
- Anthropic: https://docs.anthropic.com/

### Check Status
```bash
npm list                    # Check dependencies
node --version             # Check Node version
python --version           # Check Python version
```

## 🎬 Kết Quả

Sau 3-5 phút, bạn sẽ có:

✅ Markdown content từ top 20 tin tức mới nhất
✅ Professional video script với:
   - Hook engaging (15 giây)
   - Main content (17.5 phút) 
   - Call to action (30 giây)
✅ Timing cues cho từng section
✅ Visual notes cho video editor
✅ YouTube metadata (title, tags, description)

## 🚀 Next Steps

1. Review scripts trong `videos_scripts/`
2. Tạo video dùng CapCut / DaVinci
3. Upload YouTube
4. Monitor analytics
5. Iterate & improve

---

**Congratulations! 🎉 You're all set to create amazing YouTube content!**

Chi tiết hơn: Xem `README.md`
