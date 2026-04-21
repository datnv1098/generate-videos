# 🎬 ONE COMMAND VIDEO CREATOR - CHEAT SHEET

**Chỉ cần 1 lệnh để tạo YouTube video từ tin tức đến video script!**

---

## ⚡ FASTEST WAY (Recommended)

### **Windows (CMD)**
```bash
create-video.bat
```

### **Windows (PowerShell)**
```powershell
.\create-video.ps1
```

### **macOS / Linux**
```bash
./create-video.sh
```

### **Anywhere (npm)**
```bash
npm run create
```

---

## 🎯 ALL COMMANDS

### **Basic (Default = Vietnamese)**

| OS | Command | Method |
|----|---------| -------|
| Windows (CMD) | `create-video.bat` | Batch file |
| Windows (PowerShell) | `.\create-video.ps1` | PowerShell script |
| macOS/Linux | `./create-video.sh` | Bash script |
| Any | `npm run create` | Node.js script |
| Any | `python create_video.py` | Python direct |

### **With Languages**

```bash
# Vietnamese (default)
npm run create:vi
npm run create           # Same as above
create-video.bat

# English
npm run create:en
create-video.bat en
python create_video.py --lang en

# Using npm
npm run create:vi        # Vietnamese
npm run create:en        # English
```

### **Quick Mode (Faster, skip validations)**

```bash
# npm
npm run create:quick

# Batch
create-video.bat quick

# PowerShell
.\create-video.ps1 -Quick

# Bash
./create-video.sh quick

# Python
python create_video.py --quick
```

### **Combined Options**

```bash
# English + Quick
create-video.bat en quick
python create_video.py --lang en --quick

# Or with PowerShell
.\create-video.ps1 -Language "en" -Quick
```

---

## 📊 WHAT HAPPENS

When you run **1 command**, it automatically:

### **Step 1: Content Generation (1 min)**
- 📡 Fetch latest news from 10+ sources
- 📰 Support: US politics, crypto, markets, employment
- 📝 Generate markdown with hooks & thumbnails
- 💾 Save to: `videos/YYYY-MM-DD/`

### **Step 2: LLM Processing (1-2 min)**
- 🤖 Send to Claude API for enhancement
- ✍️ Generate professional video script
- 🎬 Add timing cues (00:00, 01:00, etc.)
- 📋 Export JSON + text formats

### **Step 3: Video Guide (30 sec)**
- 🎞️ Create production guide
- 🛠️ Recommend tools (CapCut, DaVinci, Premiere)
- 📸 Generate title slides
- 📊 YouTube metadata

**Total: ~2-3 minutes** ⚡

---

## ✅ OUTPUT

After running 1 command, you get:

```
📂 videos/2026-04-21/
   └── youtube-content-2026-04-21-vi.md      (Markdown)

📂 videos_scripts/
   ├── script_2026-04-21_Title.json          (Machine-readable)
   └── script_2026-04-21_Title.txt           (Human-readable)

📂 generated_videos/
   ├── title_slide.png                       (Visual)
   ├── production_guide.txt
   └── (Video resources)
```

---

## 🚀 QUICK START (5 STEPS)

### **1. Setup (first time only)**
```bash
cd "Claude Code Skill"
npm install
```

### **2. Add API Keys**
Create `.env` file:
```
YOUTUBE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### **3. Run (One Command!)**
```bash
npm run create        # or any command above
```

### **4. Wait (2-3 minutes)**
Script runs automatically, showing progress

### **5. Create Video**
- Open `videos_scripts/script_*.txt`
- Copy to CapCut / DaVinci / Premiere
- Add visuals & music
- Export & upload YouTube!

---

## 💡 EXAMPLES

### Example 1: Create English Video
```bash
npm run create:en
```

### Example 2: Quick Vietnamese Video
```bash
create-video.bat quick
```

### Example 3: Daily Automation
```bash
# Windows Task Scheduler
# Run daily at 6:00 AM
create-video.bat

# macOS/Linux cron
0 6 * * * /path/to/create-video.sh
```

### Example 4: Create Multiple Videos
```bash
npm run create        # Day 1
npm run create:en     # Day 2 (English)
npm run create:vi     # Day 3 (Vietnamese)
# Each creates new video from latest news
```

---

## 🎯 YOUR TYPICAL WORKFLOW

### **Daily Content Creator**
```bash
# Every morning
npm run create

# News → Script → Done in 3 minutes!
# Then spend 30 mins making video
# Upload to YouTube
```

### **Content Producer**
```bash
# Multiple languages
npm run create:vi     # Vietnamese version
npm run create:en     # English version
# Both scripts ready in 3 mins
```

### **Bulk Creation**
```bash
# Create 5 videos at once
for i in {1..5}; do npm run create; done
# All ready, edit them throughout the week
```

---

## ⚙️ TROUBLESHOOTING

| Error | Solution |
|-------|----------|
| `npm: command not found` | Install Node.js: https://nodejs.org/ |
| `Python not found` | Install Python: https://www.python.org/ |
| `Permission denied` | Make script executable: `chmod +x create-video.sh` |
| `.env not found` | Create `.env` with API keys |
| API errors | Check ANTHROPIC_API_KEY in .env |

---

## 📊 PERFORMANCE

| Step | Time | Notes |
|------|------|-------|
| Content Gen | ~60s | Parallel API calls |
| LLM Process | ~60-120s | Claude API call |
| Video Guide | ~10-30s | Local processing |
| **Total** | **~2-3 min** | Very fast! |

Actual time depends on:
- Internet speed
- API response time
- Your computer power

---

## 🎬 VIDEO CREATION (After Pipeline)

Once pipeline creates script, use any:

### **Free Tools**
- **CapCut**: https://capcut.com (Web, easiest)
- **DaVinci Resolve**: https://blackmagicdesign.com (Pro, free version)
- **Shotcut**: https://shotcut.org (Open source)

### **Paid Tools**
- **Premiere Pro**: Adobe Creative Cloud
- **Final Cut Pro**: macOS
- **Vegas Pro**: Windows

### **Typical Steps**
1. 📥 Import script from pipeline
2. 🎨 Add visuals (news screenshots, charts)
3. 🎵 Add background music
4. 📝 Add text overlays with timing
5. 🎬 Color grade & effects
6. 📤 Export MP4 (H.264, 1080p)
7. 📱 Upload YouTube

---

## 📚 DOCUMENTATION

| File | Purpose |
|------|---------|
| `ONE_COMMAND.md` | This file |
| `QUICKSTART.md` | 5-minute setup |
| `README.md` | Complete guide |
| `PIPELINE_STATUS.md` | Detailed status |

---

## 🔥 POWER USER TIPS

### **Pro Tip 1: Daily Automation**
```bash
# Windows: Use Task Scheduler
# macOS/Linux: Use cron
# Cloud: Use GitHub Actions
```

### **Pro Tip 2: Batch Processing**
```bash
# Create 10 videos at once
npm run create && npm run create && npm run create...
```

### **Pro Tip 3: Monitor Output**
```bash
# Save output to file
npm run create 2>&1 | tee video-$(date +%Y%m%d).log
```

### **Pro Tip 4: Custom Prompts**
Edit `content-processor.ipynb` to customize Claude prompts

---

## ✨ START NOW!

Pick your OS and run:

### **Windows (Easiest)**
```bash
create-video.bat
```

### **macOS/Linux**
```bash
./create-video.sh
```

### **Any OS**
```bash
npm run create
```

---

## 🎉 THAT'S IT!

**1 command = Professional YouTube video script in 2-3 minutes**

No more:
- ❌ Manual news gathering
- ❌ Manual script writing
- ❌ Manual formatting
- ❌ Manual timing

Just:
- ✅ Run command
- ✅ Wait 3 minutes
- ✅ Edit in video software
- ✅ Upload YouTube

---

**Happy Creating! 🚀**

Questions? Check detailed docs:
- `README.md` - Complete guide
- `QUICKSTART.md` - Setup help
- `PIPELINE_STATUS.md` - Technical details

---

*Last Updated: April 21, 2026*
*Status: Production Ready ✅*
