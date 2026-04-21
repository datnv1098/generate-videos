# 🚀 YouTube Content Generator - Hướng Dẫn Sử Dụng

## Cách chạy tự động (Không cần Claude Desktop)

### Bước 1: Double-click file .bat

Bạn có 2 file sẵn trong thư mục project:

- **`generate-content-vi.bat`** → Tạo nội dung **Tiếng Việt** 🇻🇳
- **`generate-content-en.bat`** → Tạo nội dung **Tiếng Anh** 🇬🇧

### Bước 2: Chạy

1. Mở Windows Explorer
2. Điều hướng tới: `C:\Users\xdatg\Desktop\Claude Code Skill`
3. Double-click `generate-content-vi.bat` (hoặc `generate-content-en.bat`)
4. **Chờ 10-15 giây** để fetch tin tức

### Bước 3: Kiểm tra kết quả

File kết quả sẽ được lưu ở cùng thư mục với tên như:
```
youtube-content-2026-04-21-vi.md
youtube-content-2026-04-21-en.md
```

---

## Nội dung tự động sinh ra

### ✅ Tiêu đề (Titles)
3 tiêu đề viral được gợi ý:
- Ví dụ: `🔥 BTC tăng 2.5% | Chính trị Mỹ rung chuyển | Vàng & Cổ phiếu hôm nay`

### ✅ Tags (Thẻ)
20 tags tối ưu SEO:
- Bitcoin, BTC, Ethereum, Chính trị Mỹ, Vàng, Cổ phiếu, v.v.

### ✅ Mô tả Video (Description)
- Giá BTC/ETH realtime
- Top 3 tin chính trị Mỹ
- Top 3 tin vàng & cổ phiếu
- Top 3 tin thất nghiệp Mỹ
- Timestamps chi tiết
- Hashtags viral

### ✅ Gợi ý Thumbnail
- Mô tả thiết kế nền, text, khuôn mặt

### ✅ Hook Script (15 giây đầu)
- Hook hấp dẫn để bắt sự chú ý người xem

---

## Cách sử dụng từ dòng lệnh (Command Line)

### Option 1: Tiếng Việt
```bash
npm run content-gen -- vi
```

### Option 2: Tiếng Anh
```bash
npm run content-gen -- en
```

### Option 3: Chạy trực tiếp
```bash
cd "C:\Users\xdatg\Desktop\Claude Code Skill"
node build/cli.js vi
# hoặc
node build/cli.js en
```

---

## Nguồn dữ liệu

Dữ liệu được fetch từ:
- 📰 **Reuters Politics** - Tin chính trị Mỹ
- 📰 **AP News** - Tin Mỹ
- 📰 **NPR** - Tin tức quốc tế
- 💹 **CoinGecko** - Giá BTC/ETH realtime
- 💹 **CoinTelegraph** - Tin crypto
- 💹 **CoinDesk** - Tin crypto
- 📊 **Yahoo Finance** - Tin cổ phiếu
- 📊 **MarketWatch** - Tin thị trường
- 📊 **Reuters Business** - Tin kinh tế
- 👷 **BLS / Reuters** - Tin việc làm

---

## Lưu ý quan trọng

1. **Cần Internet** - Script cần kết nối mạng để fetch dữ liệu từ RSS feeds
2. **Cần YouTube API Key** - Phải có `.env` file với `YOUTUBE_API_KEY` (đã cài ở bước setup)
3. **Thời gian chờ** - Lần đầu có thể chậm hơn (15-20 giây), lần sau nhanh hơn
4. **Định dạng output** - File kết quả là Markdown (.md), có thể copy-paste trực tiếp vào YouTube Description

---

## Ví dụ Output

```markdown
## 📋 NỘI DUNG BÀI ĐĂNG YOUTUBE

### 🎯 TIÊU ĐỀ ĐỀ XUẤT:
**Lựa chọn 1:** 🔥 BTC tăng 2.5% | Chính trị Mỹ rung chuyển | Vàng & Cổ phiếu 21-04-2026

### 🏷️ TAGS:
`Bitcoin, BTC, Ethereum, Chính trị Mỹ, ...`

### 📝 MÔ TẢ VIDEO:
₿ **CRYPTO:**
• Bitcoin (BTC): $42,500 (+2.5%)
• Ethereum (ETH): $2,350 (+1.8%)

... (đầy đủ nội dung) ...
```

---

## Troubleshooting

### ❌ "command not found: node"
→ Node.js chưa cài hoặc không trong PATH
→ Dùng full path: `C:\nvm4w\nodejs\node.exe build/cli.js vi`

### ❌ "Cannot find module..."
→ Chạy: `npm install` lại

### ❌ "Timeout fetching RSS"
→ Mạng chậm, chờ vài phút rồi thử lại

---

## Support

Nếu có lỗi, chạy từ PowerShell để xem chi tiết:
```powershell
cd "C:\Users\xdatg\Desktop\Claude Code Skill"
node build/cli.js vi 2>&1
```

Enjoy! 🎉
