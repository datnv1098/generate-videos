# ⚡ ONE COMMAND TO CREATE VIDEO

Chỉ cần 1 lệnh duy nhất để tạo video từ tin tức đến video script!

## 🚀 TÓM TẮT LỆNH

### **Lệnh Chính (Tất cả công việc)**
```bash
npm run create
```

### **Lệnh Phụ (Tùy chọn)**
```bash
npm run create:quick      # Bỏ qua một số bước (nhanh hơn)
npm run create:vi         # Content tiếng Việt
npm run create:en         # Content tiếng Anh
npm run create:en --quick # Tiếng Anh, mode nhanh
```

### **Hoặc dùng Python trực tiếp**
```bash
python create_video.py
python create_video.py --quick
python create_video.py --lang en
```

---

## 📊 QUY TRÌNH TỰ ĐỘNG

**1 lệnh sẽ tự động chạy:**

```
📝 Step 1: Content Generation (1 min)
   ↓ Fetch tin tức từ 10+ nguồn
   ↓ Tạo markdown content
   ↓ Thêm hooks & thumbnail concepts

🤖 Step 2: LLM Processing (1-2 min)
   ↓ Parse markdown content
   ↓ Gửi đến Claude API
   ↓ Tạo professional video script
   ↓ Export JSON + text guides

🎬 Step 3: Video Guide (30 sec)
   ↓ Tạo production guide
   ↓ Gợi ý video tools
   ↓ Tạo title slides
   ↓ Summary metadata
```

**Total Time: ~2-3 phút** ⚡

---

## ✅ KỲ VỌNG KẾT QUẢ

Sau khi chạy `npm run create`, bạn sẽ có:

```
✅ videos/2026-04-21/
   └── youtube-content-2026-04-21-vi.md        (Markdown content)

✅ videos_scripts/
   ├── script_2026-04-21_Title.json            (JSON script)
   └── script_2026-04-21_Title.txt             (Text guide)

✅ generated_videos/
   ├── title_slide.png                         (Nếu có PIL)
   └── (Video resources & guides)
```

---

## 🎯 QUICK START

### **Cách 1: Đơn giản nhất (Recommended)**
```bash
npm run create
```
✅ Tất cả tự động, hiển thị progress colorful!

### **Cách 2: Tuỳ chỉnh**
```bash
npm run create:en          # English content
npm run create:vi --quick  # Vietnamese, skip some steps
```

### **Cách 3: Direct Python**
```bash
python create_video.py
```

---

## 📋 SAU KHI SCRIPT CHẠY XONG

### **Bạn sẽ nhận được:**

1. **Video Script (JSON)**
   - Dùng cho video editors
   - Title, duration, sections
   - Timing cues, visual notes
   - Background music suggestions

2. **Video Guide (Text)**
   - Dễ đọc trong text editor
   - Narration scripts
   - Section timing
   - Visual directions

3. **Markdown Content**
   - Tất cả tin tức
   - Hooks & descriptions
   - Tags & metadata
   - Thumbnail concepts

### **Tiếp theo - Tạo Video**

```
1. Mở script trong: videos_scripts/script_*.txt
2. Copy nội dung vào video editor:
   • CapCut (Web): https://capcut.com
   • DaVinci Resolve: https://blackmagicdesign.com
   • Premiere Pro: Adobe Creative Cloud

3. Thêm:
   • Visuals (news clips, screenshots)
   • Music (YouTube Audio Library)
   • Transitions & effects
   • Text overlays với timing

4. Export & Upload YouTube!
```

---

## 🔄 CHẠY HÀ NGÀY

Vì script tự động fetch tin tức mới, bạn có thể:

```bash
# Hàng ngày tạo nội dung mới
npm run create

# Hoặc tạo schedule (Windows Task Scheduler / cron)
# Chạy mỗi sáng 6:00 AM để có content sẵn
```

---

## ⚙️ CẤU HÌNH

### **Lần đầu (setup)**
```bash
# 1. Cài dependencies
npm install

# 2. Tạo .env file với API keys
YOUTUBE_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 3. Chạy!
npm run create
```

### **Lần sau (dễ hơn)**
```bash
npm run create
```

---

## 🐛 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| `npm: command not found` | Cài Node.js: https://nodejs.org/ |
| `Python not found` | Cài Python: https://www.python.org/ |
| `API key not found` | Kiểm tra .env file |
| `Jupyter not found` | Script tự động install |
| Step 2 failed (LLM) | Check ANTHROPIC_API_KEY trong .env |

---

## 💡 TIPS

### **Optimization**
- `npm run create:quick` - Nhanh hơn, bỏ qua validations
- Chạy đêm để không ảnh hưởng máy
- Có thể chạy nhiều lần (không xóa files cũ)

### **Customization**
- Edit `content-processor.ipynb` để custom prompt
- Thay đổi news sources trong `src/cli.ts`
- Tuỳ chỉnh video sections trong `generate_video.py`

### **Advanced**
```bash
# Chỉ step 1 (content gen)
npm run content-gen

# Chỉ step 2 (LLM)
npm run notebook-exec

# Chỉ step 3 (video guide)
npm run generate-video

# Tất cả
npm run create
```

---

## 📊 PERFORMANCE

| Operation | Time | Hardware |
|-----------|------|----------|
| Content Gen | ~60s | 100 MB RAM |
| LLM Process | ~60-120s | 100-200 MB RAM |
| Video Guide | ~10-30s | 50 MB RAM |
| **Total** | **~2-3 min** | **Typical PC** |

---

## 🎬 EXAMPLES

### Example 1: Daily Automation
```bash
# Windows Task Scheduler
run-full-pipeline.bat  (hoặc npm run create)

# Linux/macOS cron
0 6 * * * cd /path && npm run create
```

### Example 2: Custom Language
```bash
npm run create:en    # English
npm run create:vi    # Vietnamese
```

### Example 3: Multiple Videos
```bash
npm run create
npm run create  # Run again tomorrow
# Mỗi lần chạy tạo video mới từ tin tức mới nhất
```

---

## 📞 HELP

```bash
# Xem tất cả commands
npm run

# Xem help
python create_video.py --help  (khi implemented)

# Xem logs
npm run create 2>&1 | tee create-video.log
```

---

**🎉 That's it! Chỉ cần 1 lệnh để bắt đầu tạo video!**

```bash
npm run create
```

**Enjoy! 🚀**
