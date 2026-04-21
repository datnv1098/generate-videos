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

// Initialize the server
const server = new Server(
  {
    name: "youtube-research-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define YouTube Research Tools
const tools: Tool[] = [
  {
    name: "search_videos",
    description: "Search for YouTube videos by keyword or topic",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "The search query for YouTube videos",
        },
        maxResults: {
          type: "number",
          description: "Maximum number of results to return (default: 10)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "get_video_info",
    description: "Get detailed information about a specific YouTube video",
    inputSchema: {
      type: "object",
      properties: {
        videoId: {
          type: "string",
          description: "The YouTube video ID",
        },
      },
      required: ["videoId"],
    },
  },
  {
    name: "get_video_comments",
    description: "Retrieve comments from a YouTube video",
    inputSchema: {
      type: "object",
      properties: {
        videoId: {
          type: "string",
          description: "The YouTube video ID",
        },
        maxResults: {
          type: "number",
          description: "Maximum number of comments to return (default: 20)",
        },
      },
      required: ["videoId"],
    },
  },
  {
    name: "get_video_transcript",
    description:
      "Get the transcript or captions of a YouTube video if available",
    inputSchema: {
      type: "object",
      properties: {
        videoId: {
          type: "string",
          description: "The YouTube video ID",
        },
      },
      required: ["videoId"],
    },
  },
  {
    name: "get_channel_info",
    description:
      "Get information about a YouTube channel (subscribers, videos count, etc.)",
    inputSchema: {
      type: "object",
      properties: {
        channelId: {
          type: "string",
          description: "The YouTube channel ID",
        },
      },
      required: ["channelId"],
    },
  },
  {
    name: "analyze_video_sentiment",
    description: "Analyze the sentiment of comments on a video",
    inputSchema: {
      type: "object",
      properties: {
        videoId: {
          type: "string",
          description: "The YouTube video ID",
        },
      },
      required: ["videoId"],
    },
  },
  {
    name: "get_us_politics_news",
    description: "Lấy top 5 tin tức chính trị Mỹ mới nhất từ Reuters, AP News",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_crypto_news",
    description: "Lấy top 5 tin tức BTC/ETH và giá crypto thời gian thực từ CoinGecko",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_market_news",
    description: "Lấy giá vàng hiện tại và top tin tức cổ phiếu Mỹ (S&P500, NASDAQ, Dow Jones)",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_employment_news",
    description: "Lấy tin tức về tỷ lệ việc làm/thất nghiệp Mỹ mới nhất",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "generate_youtube_content",
    description: "Tổng hợp tất cả tin tức và tự động tạo bài viết YouTube với title viral và tags tối ưu SEO",
    inputSchema: {
      type: "object",
      properties: {
        language: {
          type: "string",
          description: "Ngôn ngữ bài viết: 'vi' (tiếng Việt) hoặc 'en' (tiếng Anh). Mặc định: 'vi'",
        },
      },
    },
  },
];

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

function formatDuration(iso: string): string {
  const match = iso.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return iso;
  const h = match[1] ? `${match[1]}h ` : "";
  const m = match[2] ? `${match[2]}m ` : "";
  const s = match[3] ? `${match[3]}s` : "";
  return `${h}${m}${s}`.trim();
}

function formatNumber(n: string | undefined | null): string {
  if (!n) return "N/A";
  const num = parseInt(n);
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toString();
}

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "search_videos": {
        const query = (args as Record<string, unknown>).query as string;
        const maxResults =
          ((args as Record<string, unknown>).maxResults as number) || 10;

        const res = await youtube.search.list({
          part: ["snippet"],
          q: query,
          maxResults,
          type: ["video"],
        });

        const items = res.data.items ?? [];
        if (items.length === 0) {
          return { content: [{ type: "text", text: `Không tìm thấy video nào cho: "${query}"` }] };
        }

        const lines = items.map((item, i) => {
          const s = item.snippet!;
          return `${i + 1}. **${s.title}**\n   Channel: ${s.channelTitle}\n   Video ID: ${item.id?.videoId}\n   Published: ${s.publishedAt?.slice(0, 10)}\n   URL: https://youtube.com/watch?v=${item.id?.videoId}`;
        });

        return {
          content: [{ type: "text", text: `Kết quả tìm kiếm "${query}" (${items.length} video):\n\n${lines.join("\n\n")}` }],
        };
      }

      case "get_video_info": {
        const videoId = (args as Record<string, unknown>).videoId as string;

        const res = await youtube.videos.list({
          part: ["snippet", "statistics", "contentDetails"],
          id: [videoId],
        });

        const video = res.data.items?.[0];
        if (!video) {
          return { content: [{ type: "text", text: `Không tìm thấy video ID: ${videoId}` }] };
        }

        const s = video.snippet!;
        const st = video.statistics!;
        const cd = video.contentDetails!;

        const text = [
          `**${s.title}**`,
          ``,
          `Channel: ${s.channelTitle}`,
          `Published: ${s.publishedAt?.slice(0, 10)}`,
          `Duration: ${formatDuration(cd.duration ?? "")}`,
          `Views: ${formatNumber(st.viewCount)}`,
          `Likes: ${formatNumber(st.likeCount)}`,
          `Comments: ${formatNumber(st.commentCount)}`,
          `URL: https://youtube.com/watch?v=${videoId}`,
          ``,
          `**Description:**`,
          s.description?.slice(0, 500) + (s.description && s.description.length > 500 ? "..." : ""),
          ``,
          `Tags: ${s.tags?.slice(0, 10).join(", ") ?? "None"}`,
        ].join("\n");

        return { content: [{ type: "text", text }] };
      }

      case "get_video_comments": {
        const videoId = (args as Record<string, unknown>).videoId as string;
        const maxResults =
          ((args as Record<string, unknown>).maxResults as number) || 20;

        const res = await youtube.commentThreads.list({
          part: ["snippet"],
          videoId,
          maxResults,
          order: "relevance",
        });

        const items = res.data.items ?? [];
        if (items.length === 0) {
          return { content: [{ type: "text", text: `Video ${videoId} không có comments hoặc comments bị tắt.` }] };
        }

        const lines = items.map((item, i) => {
          const c = item.snippet!.topLevelComment!.snippet!;
          return `${i + 1}. **${c.authorDisplayName}** (👍 ${formatNumber(String(c.likeCount ?? 0))})\n   ${c.textDisplay?.replace(/<[^>]+>/g, "")}`;
        });

        return {
          content: [{ type: "text", text: `Top ${items.length} comments của video ${videoId}:\n\n${lines.join("\n\n")}` }],
        };
      }

      case "get_video_transcript": {
        const videoId = (args as Record<string, unknown>).videoId as string;

        const res = await youtube.captions.list({
          part: ["snippet"],
          videoId,
        });

        const captions = res.data.items ?? [];
        if (captions.length === 0) {
          return { content: [{ type: "text", text: `Video ${videoId} không có transcript/captions khả dụng qua API.\n\nBạn có thể xem transcript thủ công tại: https://youtube.com/watch?v=${videoId} → "..." → "Open transcript"` }] };
        }

        const captionList = captions.map(c =>
          `- ${c.snippet?.name || "(auto)"} [${c.snippet?.language}] - ${c.snippet?.trackKind}`
        ).join("\n");

        return {
          content: [{ type: "text", text: `Captions có sẵn cho video ${videoId}:\n${captionList}\n\nNote: Tải nội dung transcript đầy đủ yêu cầu OAuth. Dùng https://downsub.com/ để tải transcript miễn phí.` }],
        };
      }

      case "get_channel_info": {
        const channelId = (args as Record<string, unknown>).channelId as string;

        const res = await youtube.channels.list({
          part: ["snippet", "statistics", "brandingSettings"],
          id: [channelId],
        });

        const channel = res.data.items?.[0];
        if (!channel) {
          return { content: [{ type: "text", text: `Không tìm thấy channel ID: ${channelId}` }] };
        }

        const s = channel.snippet!;
        const st = channel.statistics!;

        const text = [
          `**${s.title}**`,
          ``,
          `Subscribers: ${formatNumber(st.subscriberCount)}`,
          `Total Videos: ${formatNumber(st.videoCount)}`,
          `Total Views: ${formatNumber(st.viewCount)}`,
          `Created: ${s.publishedAt?.slice(0, 10)}`,
          `Country: ${s.country ?? "N/A"}`,
          `URL: https://youtube.com/channel/${channelId}`,
          ``,
          `**Description:**`,
          s.description?.slice(0, 500) + (s.description && s.description.length > 500 ? "..." : ""),
        ].join("\n");

        return { content: [{ type: "text", text }] };
      }

      case "analyze_video_sentiment": {
        const videoId = (args as Record<string, unknown>).videoId as string;

        const res = await youtube.commentThreads.list({
          part: ["snippet"],
          videoId,
          maxResults: 100,
          order: "relevance",
        });

        const items = res.data.items ?? [];
        if (items.length === 0) {
          return { content: [{ type: "text", text: `Video ${videoId} không có comments để phân tích.` }] };
        }

        const positiveWords = ["good", "great", "love", "amazing", "excellent", "best", "awesome", "fantastic", "wonderful", "perfect", "tuyệt", "hay", "thích", "xuất sắc", "tốt"];
        const negativeWords = ["bad", "worst", "hate", "terrible", "awful", "boring", "disappointed", "waste", "trash", "poor", "tệ", "dở", "chán", "thất vọng", "kém"];

        let positive = 0, negative = 0, neutral = 0;
        const samplePositive: string[] = [];
        const sampleNegative: string[] = [];

        for (const item of items) {
          const text = (item.snippet!.topLevelComment!.snippet!.textDisplay ?? "").toLowerCase();
          const isPos = positiveWords.some(w => text.includes(w));
          const isNeg = negativeWords.some(w => text.includes(w));

          if (isPos && !isNeg) {
            positive++;
            if (samplePositive.length < 3) samplePositive.push(text.slice(0, 100));
          } else if (isNeg && !isPos) {
            negative++;
            if (sampleNegative.length < 3) sampleNegative.push(text.slice(0, 100));
          } else {
            neutral++;
          }
        }

        const total = items.length;
        const pct = (n: number) => `${Math.round((n / total) * 100)}%`;

        const text = [
          `**Phân tích Sentiment - Video ${videoId}**`,
          `Dựa trên ${total} comments`,
          ``,
          `✅ Tích cực: ${positive} (${pct(positive)})`,
          `😐 Trung lập: ${neutral} (${pct(neutral)})`,
          `❌ Tiêu cực: ${negative} (${pct(negative)})`,
          ``,
          `**Mẫu comment tích cực:**`,
          samplePositive.length > 0 ? samplePositive.map(c => `- "${c}"`).join("\n") : "- Không có",
          ``,
          `**Mẫu comment tiêu cực:**`,
          sampleNegative.length > 0 ? sampleNegative.map(c => `- "${c}"`).join("\n") : "- Không có",
        ].join("\n");

        return { content: [{ type: "text", text }] };
      }

      case "get_us_politics_news": {
        const sources = [
          { name: "Reuters Politics", url: "https://feeds.reuters.com/Reuters/PoliticsNews" },
          { name: "AP Politics", url: "https://feeds.apnews.com/rss/apf-politics" },
          { name: "NPR Politics", url: "https://feeds.npr.org/1014/rss.xml" },
        ];

        const allItems: { title: string; link: string; pubDate?: string; source: string }[] = [];
        for (const src of sources) {
          const items = await fetchRSSItems(src.url, 5);
          items.forEach(item => allItems.push({ ...item, source: src.name }));
        }

        // Sort by date and take top 5
        const top5 = allItems
          .sort((a, b) => new Date(b.pubDate ?? 0).getTime() - new Date(a.pubDate ?? 0).getTime())
          .slice(0, 5);

        if (top5.length === 0) {
          return { content: [{ type: "text", text: "Không lấy được tin tức chính trị Mỹ." }] };
        }

        const lines = top5.map((item, i) =>
          `${i + 1}. **${item.title}**\n   Nguồn: ${item.source} | ${item.pubDate?.slice(0, 16) ?? ""}\n   🔗 ${item.link}`
        );

        return {
          content: [{ type: "text", text: `🇺🇸 **TOP 5 TIN TỨC CHÍNH TRỊ MỸ**\n\n${lines.join("\n\n")}` }],
        };
      }

      case "get_crypto_news": {
        // Fetch BTC & ETH prices from CoinGecko (free, no key)
        const priceRes = await axios.get(
          "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true&include_market_cap=true",
          { timeout: 8000 }
        );
        const prices = priceRes.data;
        const btcPrice = prices.bitcoin?.usd?.toLocaleString("en-US") ?? "N/A";
        const btcChange = prices.bitcoin?.usd_24h_change?.toFixed(2) ?? "0";
        const ethPrice = prices.ethereum?.usd?.toLocaleString("en-US") ?? "N/A";
        const ethChange = prices.ethereum?.usd_24h_change?.toFixed(2) ?? "0";

        // Fetch crypto news RSS
        const cryptoSources = [
          { name: "CoinTelegraph", url: "https://cointelegraph.com/rss" },
          { name: "CoinDesk", url: "https://www.coindesk.com/arc/outboundfeeds/rss/" },
        ];

        const allItems: { title: string; link: string; pubDate?: string; source: string }[] = [];
        for (const src of cryptoSources) {
          const items = await fetchRSSItems(src.url, 6);
          items.forEach(item => allItems.push({ ...item, source: src.name }));
        }

        const top5 = allItems
          .sort((a, b) => new Date(b.pubDate ?? 0).getTime() - new Date(a.pubDate ?? 0).getTime())
          .slice(0, 5);

        const btcSign = parseFloat(btcChange) >= 0 ? "🟢" : "🔴";
        const ethSign = parseFloat(ethChange) >= 0 ? "🟢" : "🔴";

        const newsLines = top5.map((item, i) =>
          `${i + 1}. **${item.title}**\n   Nguồn: ${item.source} | ${item.pubDate?.slice(0, 16) ?? ""}\n   🔗 ${item.link}`
        );

        const text = [
          `₿ **GIÁ CRYPTO THỜI GIAN THỰC**`,
          ``,
          `${btcSign} Bitcoin (BTC): $${btcPrice} | 24h: ${btcChange}%`,
          `${ethSign} Ethereum (ETH): $${ethPrice} | 24h: ${ethChange}%`,
          ``,
          `📰 **TOP 5 TIN TỨC BTC/ETH**`,
          ``,
          newsLines.join("\n\n"),
        ].join("\n");

        return { content: [{ type: "text", text }] };
      }

      case "get_market_news": {
        // Gold price from metals API (free endpoint)
        let goldText = "";
        try {
          const goldRes = await axios.get(
            "https://api.coinbase.com/v2/exchange-rates?currency=XAU",
            { timeout: 8000 }
          );
          const usdRate = goldRes.data?.data?.rates?.USD;
          if (usdRate) {
            const goldUSD = (1 / parseFloat(usdRate)).toFixed(2);
            goldText = `🥇 Vàng (XAU/USD): $${parseFloat(goldUSD).toLocaleString("en-US")} /oz`;
          }
        } catch {
          goldText = "🥇 Vàng: Không lấy được giá";
        }

        // US Market news RSS
        const marketSources = [
          { name: "Yahoo Finance", url: "https://finance.yahoo.com/rss/topstories" },
          { name: "MarketWatch", url: "https://feeds.content.dowjones.io/public/rss/mw_topstories" },
          { name: "Reuters Business", url: "https://feeds.reuters.com/reuters/businessNews" },
        ];

        const allItems: { title: string; link: string; pubDate?: string; source: string }[] = [];
        for (const src of marketSources) {
          const items = await fetchRSSItems(src.url, 4);
          items.forEach(item => allItems.push({ ...item, source: src.name }));
        }

        const top5 = allItems
          .sort((a, b) => new Date(b.pubDate ?? 0).getTime() - new Date(a.pubDate ?? 0).getTime())
          .slice(0, 5);

        const newsLines = top5.map((item, i) =>
          `${i + 1}. **${item.title}**\n   Nguồn: ${item.source} | ${item.pubDate?.slice(0, 16) ?? ""}\n   🔗 ${item.link}`
        );

        const text = [
          `📈 **THỊ TRƯỜNG TÀI CHÍNH MỸ**`,
          ``,
          goldText,
          ``,
          `📰 **TOP 5 TIN TỨC CỔ PHIẾU MỸ**`,
          ``,
          newsLines.join("\n\n"),
        ].join("\n");

        return { content: [{ type: "text", text }] };
      }

      case "get_employment_news": {
        const empSources = [
          { name: "Reuters Economy", url: "https://feeds.reuters.com/reuters/businessNews" },
          { name: "BLS News", url: "https://www.bls.gov/feed/bls_latest.rss" },
          { name: "CNBC Economy", url: "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258" },
        ];

        const keywords = ["job", "employment", "unemployment", "payroll", "labor", "workforce", "hiring", "layoff", "nonfarm"];
        const allItems: { title: string; link: string; pubDate?: string; source: string }[] = [];

        for (const src of empSources) {
          const items = await fetchRSSItems(src.url, 20);
          const filtered = items.filter(item =>
            keywords.some(kw => item.title.toLowerCase().includes(kw) || item.contentSnippet?.toLowerCase().includes(kw))
          );
          filtered.forEach(item => allItems.push({ ...item, source: src.name }));
        }

        const top5 = allItems
          .sort((a, b) => new Date(b.pubDate ?? 0).getTime() - new Date(a.pubDate ?? 0).getTime())
          .slice(0, 5);

        if (top5.length === 0) {
          // Fallback: any recent econ news
          const fallback = await fetchRSSItems("https://feeds.reuters.com/reuters/businessNews", 5);
          fallback.forEach(item => allItems.push({ ...item, source: "Reuters" }));
          top5.push(...allItems.slice(0, 5));
        }

        const lines = top5.map((item, i) =>
          `${i + 1}. **${item.title}**\n   Nguồn: ${item.source} | ${item.pubDate?.slice(0, 16) ?? ""}\n   🔗 ${item.link}`
        );

        return {
          content: [{ type: "text", text: `👷 **TIN TỨC VIỆC LÀM / THẤT NGHIỆP MỸ**\n\n${lines.join("\n\n")}` }],
        };
      }

      case "generate_youtube_content": {
        const language = ((args as Record<string, unknown>)?.language as string) ?? "vi";
        const isVi = language !== "en";

        // Fetch all news in parallel
        const [politicsItems, cryptoRes, marketItems, empItems] = await Promise.all([
          (async () => {
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

        // Build content
        const politicsSummary = politicsItems.slice(0, 3).map(i => `- ${i.title}`).join("\n");
        const marketSummary = marketItems.slice(0, 3).map(i => `- ${i.title}`).join("\n");
        const empSummary = empItems.slice(0, 3).map(i => `- ${i.title}`).join("\n");

        const titleOptions = isVi ? [
          `🔥 BTC ${btcDir} ${btcChange}% | Chính trị Mỹ rung chuyển | Vàng & Cổ phiếu hôm nay ${today}`,
          `⚡ Tin NÓNG ${today}: Bitcoin $${btcPrice}, Bầu cử Mỹ căng thẳng, Thị trường ${marketTone}`,
          `🚨 CẬP NHẬT THỊ TRƯỜNG ${today} | BTC $${btcPrice} | ETH $${ethPrice} | Chính Trị Mỹ Mới Nhất`,
        ] : [
          `🔥 BTC ${btcDir} ${btcChange}% | US Politics SHAKEUP | Gold & Stocks Update ${today}`,
          `⚡ BREAKING ${today}: Bitcoin $${btcPrice}, US Markets ${marketTone}, Jobs Report`,
          `🚨 MARKET UPDATE ${today} | BTC $${btcPrice} | ETH $${ethPrice} | US Politics Latest`,
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
${today} - Cập nhật toàn bộ tin tức quan trọng nhất trong ngày!

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
"Thị trường hôm nay có những biến động CỰC LỚN mà bạn không thể bỏ lỡ - Bitcoin vừa ${btcDir} ${btcChange}%, chính trị Mỹ đang rung chuyển, và tôi sẽ cho bạn biết điều đó ảnh hưởng đến túi tiền của bạn như thế nào trong 20 phút tới!"
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
${today} - Complete daily market & news briefing!

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
"Today's markets are moving in ways you CANNOT ignore - Bitcoin just ${btcDir} ${btcChange}%, US politics is shaking up Wall Street, and I'm going to show you exactly how this affects YOUR money in the next 20 minutes!"
`;

        return { content: [{ type: "text", text: content.trim() }] };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
        };
    }
  } catch (error) {
    const msg = error instanceof Error ? error.message : "Unknown error";
    return {
      content: [{ type: "text", text: `Lỗi khi gọi tool "${name}": ${msg}` }],
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("YouTube Research MCP Server started");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
