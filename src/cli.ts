#!/usr/bin/env node

/**
 * YouTube Content Generator CLI
 * Generates YouTube content with title, tags, description, thumbnail concept, and hook
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import * as dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import Parser from "rss-parser";
import axios from "axios";
import * as fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: resolve(__dirname, "../.env") });

const youtube = google.youtube({
  version: "v3",
  auth: process.env.YOUTUBE_API_KEY,
});

const rssParser = new Parser({
  timeout: 10000,
  headers: { "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)" },
});

async function fetchRSSItems(url: string, limit = 5): Promise<{ title: string; link: string; pubDate?: string; contentSnippet?: string }[]> {
  try {
    const feed = await rssParser.parseURL(url);
    return feed.items.slice(0, limit).map(item => ({
      title: item.title ?? "(no title)",
      link: item.link ?? "",
      pubDate: item.pubDate ?? item.isoDate ?? "",
      contentSnippet: item.contentSnippet?.slice(0, 200) ?? "",
    }));
  } catch {
    return [];
  }
}

async function searchTopicNews(topic: string, limit = 5): Promise<{ title: string; source: string }[]> {
  // Search for news related to a specific topic
  const items: { title: string; source: string }[] = [];
  const topicLower = topic.toLowerCase();
  
  try {
    // Search across multiple RSS feeds for matching content
    const feeds = [
      "https://feeds.reuters.com/Reuters/allNews",
      "https://feeds.apnews.com/rss/apf-news",
      "https://feeds.bloomberg.com/markets/news.rss",
    ];
    
    for (const feedUrl of feeds) {
      try {
        const r = await fetchRSSItems(feedUrl, 20);
        r.filter(i => i.title.toLowerCase().includes(topicLower))
          .forEach(i => items.push({ title: i.title, source: new URL(feedUrl).hostname || "News" }));
      } catch {
        // Continue to next feed
      }
    }
  } catch {
    // Fallback: return generic content
  }
  
  return items.slice(0, limit).length > 0 
    ? items.slice(0, limit) 
    : [{ title: `Latest news about ${topic}`, source: "News Feed" }];
}

async function generateYouTubeContent(language = "vi", topic = ""): Promise<string> {
  const isVi = language !== "en";

  // If topic is provided, search for topic news
  let topicItems: { title: string; source: string }[] = [];
  if (topic) {
    topicItems = await searchTopicNews(topic);
  }

  // Fetch all news in parallel
  const [politicsItems, cryptoRes, marketItems, empItems] = await Promise.all([
    (async () => {
      if (topic) return topicItems.slice(0, 5); // Use topic items if searching
      const items: { title: string; source: string }[] = [];
      for (const url of ["https://feeds.reuters.com/Reuters/PoliticsNews", "https://feeds.apnews.com/rss/apf-politics"]) {
        const r = await fetchRSSItems(url, 3);
        r.forEach(i => items.push({ title: i.title, source: url.includes("reuters") ? "Reuters" : "AP" }));
      }
      return items.slice(0, 5);
    })(),
    (async () => {
      try {
        const r = await axios.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true", { timeout: 8000 });
        return r.data;
      } catch { return {}; }
    })(),
    (async () => {
      const items: { title: string; source: string }[] = [];
      for (const url of ["https://finance.yahoo.com/rss/topstories", "https://feeds.reuters.com/reuters/businessNews"]) {
        const r = await fetchRSSItems(url, 3);
        r.forEach(i => items.push({ title: i.title, source: url.includes("yahoo") ? "Yahoo Finance" : "Reuters" }));
      }
      return items.slice(0, 5);
    })(),
    (async () => {
      const keywords = ["job", "employment", "unemployment", "payroll", "labor"];
      const items: { title: string; source: string }[] = [];
      const r = await fetchRSSItems("https://feeds.reuters.com/reuters/businessNews", 20);
      r.filter(i => keywords.some(k => i.title.toLowerCase().includes(k))).slice(0, 5)
        .forEach(i => items.push({ title: i.title, source: "Reuters" }));
      if (items.length === 0) r.slice(0, 3).forEach(i => items.push({ title: i.title, source: "Reuters" }));
      return items;
    })(),
  ]);

  const btcPrice = cryptoRes.bitcoin?.usd?.toLocaleString("en-US") ?? "N/A";
  const btcChange = (cryptoRes.bitcoin?.usd_24h_change ?? 0).toFixed(2);
  const ethPrice = cryptoRes.ethereum?.usd?.toLocaleString("en-US") ?? "N/A";
  const ethChange = (cryptoRes.ethereum?.usd_24h_change ?? 0).toFixed(2);

  const today = new Date().toLocaleDateString(isVi ? "vi-VN" : "en-US", { year: "numeric", month: "long", day: "numeric" });
  const btcDir = parseFloat(btcChange) >= 0 ? (isVi ? "tăng" : "rises") : (isVi ? "giảm" : "falls");
  const marketTone = parseFloat(btcChange) >= 2 ? (isVi ? "BỐC CHÁY" : "SURGING") : parseFloat(btcChange) <= -2 ? (isVi ? "LAOXA DỐC" : "CRASHING") : (isVi ? "BIẾN ĐỘNG" : "VOLATILE");

  const topicPrefix = topic ? `${topic} - ` : "";
  const politicsSummary = politicsItems.slice(0, 3).map(i => `- ${i.title}`).join("\n");
  const marketSummary = marketItems.slice(0, 3).map(i => `- ${i.title}`).join("\n");
  const empSummary = empItems.slice(0, 3).map(i => `- ${i.title}`).join("\n");

  const titleOptions = isVi ? [
    `🔥 ${topicPrefix}BTC ${btcDir} ${btcChange}% | Chính trị Mỹ rung chuyển | Vàng & Cổ phiếu hôm nay ${today}`,
    `⚡ Tin NÓNG ${today}: ${topicPrefix}Bitcoin $${btcPrice}, Bầu cử Mỹ căng thẳng, Thị trường ${marketTone}`,
    `🚨 ${topicPrefix}CẬP NHẬT ${today} | BTC $${btcPrice} | ETH $${ethPrice} | Chính Trị Mỹ Mới Nhất`,
  ] : [
    `🔥 ${topicPrefix}BTC ${btcDir} ${btcChange}% | US Politics SHAKEUP | Gold & Stocks Update ${today}`,
    `⚡ BREAKING ${today}: ${topicPrefix}Bitcoin $${btcPrice}, US Markets ${marketTone}, Jobs Report`,
    `🚨 ${topicPrefix}MARKET UPDATE ${today} | BTC $${btcPrice} | ETH $${ethPrice} | US Politics Latest`,
  ];

  const tags = isVi
    ? ["Bitcoin", "BTC", "Ethereum", "ETH", "Chính trị Mỹ", "Vàng hôm nay", "Cổ phiếu Mỹ", "Thị trường tài chính", "Tin tức hôm nay", "Crypto", "Tỷ giá", "Thất nghiệp Mỹ", "S&P500", "NASDAQ", "Dow Jones", "Kinh tế Mỹ", "Tài chính quốc tế", "Tin hot", "Breaking news", "Đầu tư"]
    : ["Bitcoin", "BTC price", "Ethereum", "ETH", "US Politics", "Gold price today", "US stocks", "Stock market", "Crypto news", "Financial markets", "Unemployment", "Jobs report", "S&P500", "NASDAQ", "Dow Jones", "US Economy", "Breaking news", "Investment", "Trading", "Market update"];

  const content = isVi ? `
## 📋 NỘI DUNG BÀI ĐĂNG YOUTUBE

---

### 🎯 TIÊU ĐỀ ĐỀ XUẤT (chọn 1):
${titleOptions.map((t, i) => `**Lựa chọn ${i + 1}:** ${t}`).join("\n")}

---

### 🏷️ TAGS (copy toàn bộ):
\`${tags.join(", ")}\`

---

### 📝 MÔ TẢ VIDEO (Description):
${today} - ${topicPrefix}Cập nhật toàn bộ tin tức quan trọng nhất trong ngày!

₿ **CRYPTO:**
• Bitcoin (BTC): $${btcPrice} (${btcChange}%)
• Ethereum (ETH): $${ethPrice} (${ethChange}%)

🇺🇸 **CHÍNH TRỊ MỸ:**
${politicsSummary}

📈 **THỊ TRƯỜNG:**
${marketSummary}

👷 **VIỆC LÀM / THẤT NGHIỆP:**
${empSummary}

---
⏰ Timestamps:
00:00 - Giới thiệu
01:00 - Chính trị Mỹ
05:00 - Bitcoin & Crypto
10:00 - Vàng & Cổ phiếu
15:00 - Thị trường việc làm
18:00 - Tổng kết & Nhận định

---
👉 Like, Subscribe và bật thông báo để không bỏ lỡ tin tức!
#Bitcoin #ChínhTrịMỹ #ThịTrường #TinTứcHômNay

---

### 💡 GỢI Ý NỘI DUNG THUMBNAIL:
- Nền đỏ/cam nóng với biểu tượng BTC và cờ Mỹ
- Text lớn: "BTC $${btcPrice}" + "BREAKING NEWS"
- Khuôn mặt người dẫn với biểu cảm ngạc nhiên/lo lắng

### 📊 HOOK MỞ ĐẦU (15 giây đầu):
"${topicPrefix}Thị trường hôm nay có những biến động CỰC LỚN mà bạn không thể bỏ lỡ - Bitcoin vừa ${btcDir} ${btcChange}%, chính trị Mỹ đang rung chuyển, và tôi sẽ cho bạn biết điều đó ảnh hưởng đến túi tiền của bạn như thế nào trong 20 phút tới!"
` : `
## 📋 YOUTUBE CONTENT PACKAGE

---

### 🎯 TITLE OPTIONS (pick 1):
${titleOptions.map((t, i) => `**Option ${i + 1}:** ${t}`).join("\n")}

---

### 🏷️ TAGS (copy all):
\`${tags.join(", ")}\`

---

### 📝 VIDEO DESCRIPTION:
${today} - ${topicPrefix}Complete daily market & news briefing!

₿ **CRYPTO:**
• Bitcoin (BTC): $${btcPrice} (${btcChange}%)
• Ethereum (ETH): $${ethPrice} (${ethChange}%)

🇺🇸 **US POLITICS:**
${politicsSummary}

📈 **MARKETS:**
${marketSummary}

👷 **EMPLOYMENT:**
${empSummary}

---
⏰ Timestamps:
00:00 - Intro
01:00 - US Politics
05:00 - Bitcoin & Crypto
10:00 - Gold & Stocks
15:00 - Jobs Market
18:00 - Summary & Outlook

---
👉 Like, Subscribe and hit the bell!
#Bitcoin #USPolitics #StockMarket #BreakingNews

---

### 💡 THUMBNAIL CONCEPT:
- Red/orange background with BTC symbol and US flag
- Bold text: "BTC $${btcPrice}" + "BREAKING"
- Presenter with shocked/concerned expression

### 📊 HOOK (first 15 seconds):
"${topicPrefix}Today's markets are moving in ways you CANNOT ignore - Bitcoin just ${btcDir} ${btcChange}%, US politics is shaking up Wall Street, and I'm going to show you exactly how this affects YOUR money in the next 20 minutes!"
`;

  return content.trim();
}

// Main CLI execution
async function main() {
  try {
    let language = "vi";
    let topic = "";

    // Parse command line arguments
    if (process.argv.length > 2) {
      // Check for --topic
      const topicIndex = process.argv.findIndex(arg => arg === "--topic");
      if (topicIndex !== -1 && process.argv[topicIndex + 1]) {
        topic = process.argv[topicIndex + 1];
      }
      
      // Check for --lang
      const langIndex = process.argv.findIndex(arg => arg === "--lang");
      if (langIndex !== -1 && process.argv[langIndex + 1]) {
        language = process.argv[langIndex + 1];
      }
      
      // If first positional arg is not an option, treat it as language
      const firstArg = process.argv[2];
      if (firstArg && !firstArg.startsWith("--") && firstArg !== "vi" && firstArg !== "en") {
        topic = firstArg;
      } else if (firstArg && (firstArg === "vi" || firstArg === "en")) {
        language = firstArg;
      }
    }

    const prefix = topic ? `Topic: "${topic}" | Language: ${language}` : `Language: ${language}`;
    console.log(`⏳ Generating YouTube content... (${prefix})\n`);
    
    const content = await generateYouTubeContent(language, topic);
    
    // Create videos folder structure
    const timestamp = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    const videoDir = `videos/${timestamp}`;
    
    // Create directory if not exists
    if (!fs.existsSync(videoDir)) {
      fs.mkdirSync(videoDir, { recursive: true });
    }
    
    // Save to file with full path
    const filename = `${videoDir}/youtube-content-${timestamp}-${language}.md`;
    fs.writeFileSync(filename, content, { encoding: "utf-8" });
    
    // Output to console
    console.log(content);
    console.log(`\n✅ Content saved to: ${filename}\n`);
  } catch (error) {
    console.error("❌ Error:", error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
