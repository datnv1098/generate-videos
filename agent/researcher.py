"""YouTube Research Module - Search and collect data from YouTube."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class VideoData:
    video_id: str
    title: str
    channel: str
    channel_id: str
    description: str
    published_at: str
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    subscriber_count: int = 0
    transcript: str = ""
    top_comments: list = None

    def __post_init__(self):
        if self.top_comments is None:
            self.top_comments = []


@dataclass
class ResearchResult:
    topic: str
    timestamp: str
    videos: list[VideoData]
    summary: str = ""

    def to_dict(self):
        return {
            "topic": self.topic,
            "timestamp": self.timestamp,
            "videos": [
                {
                    "video_id": v.video_id,
                    "title": v.title,
                    "channel": v.channel,
                    "channel_id": v.channel_id,
                    "description": v.description,
                    "published_at": v.published_at,
                    "view_count": v.view_count,
                    "like_count": v.like_count,
                    "comment_count": v.comment_count,
                    "subscriber_count": v.subscriber_count,
                    "transcript": v.transcript[:2000],  # Limit transcript size
                    "top_comments": v.top_comments[:10],
                }
                for v in self.videos
            ],
        }

    def save(self, date_dir: Path):
        filepath = date_dir / f"research_{self.topic.replace(' ', '_')}_{self.timestamp}.json"
        filepath.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Research saved to {filepath}")
        return filepath


class YouTubeResearcher:
    def __init__(self, config: Config):
        self.config = config
        self.youtube = build("youtube", "v3", developerKey=config.youtube_api_key)

    def search_videos(self, topic: str, max_results: int = None) -> list[dict]:
        """Search YouTube for videos on a topic."""
        # Fetch more candidates to account for filtering
        max_results = max_results or (
            self.config.max_search_results * self.config.search_candidate_multiplier
        )
        # YouTube API cap is 50 per request
        max_results = min(max_results, 50)
        logger.info(f"Searching YouTube for: '{topic}' (fetching {max_results} candidates)")

        request = self.youtube.search().list(
            q=topic,
            part="snippet",
            type="video",
            order="relevance",
            maxResults=max_results,
            relevanceLanguage=self.config.language,
        )
        response = request.execute()

        results = []
        for item in response.get("items", []):
            results.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "channel_id": item["snippet"]["channelId"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
            })

        logger.info(f"Found {len(results)} candidates")
        return results

    def get_video_stats(self, video_ids: list[str]) -> dict:
        """Get statistics for multiple videos."""
        request = self.youtube.videos().list(
            part="statistics",
            id=",".join(video_ids),
        )
        response = request.execute()

        stats = {}
        for item in response.get("items", []):
            s = item["statistics"]
            stats[item["id"]] = {
                "view_count": int(s.get("viewCount", 0)),
                "like_count": int(s.get("likeCount", 0)),
                "comment_count": int(s.get("commentCount", 0)),
            }
        return stats

    def get_channel_stats(self, channel_ids: list[str]) -> dict:
        """Get subscriber counts for multiple channels (batch, max 50)."""
        # Deduplicate and batch in groups of 50
        unique_ids = list(set(channel_ids))
        stats = {}
        for i in range(0, len(unique_ids), 50):
            batch = unique_ids[i:i + 50]
            request = self.youtube.channels().list(
                part="statistics",
                id=",".join(batch),
            )
            response = request.execute()
            for item in response.get("items", []):
                s = item["statistics"]
                stats[item["id"]] = {
                    "subscriber_count": int(s.get("subscriberCount", 0)),
                }
        return stats

    def get_transcript(self, video_id: str) -> str:
        """Get video transcript/captions."""
        try:
            transcript_api = YouTubeTranscriptApi()
            transcript = transcript_api.fetch(video_id, languages=[self.config.language])
            return " ".join(entry.text for entry in transcript if getattr(entry, "text", "").strip())
        except Exception as e:
            logger.warning(f"Could not get transcript for {video_id}: {e}")
            return ""

    def get_comments(self, video_id: str, max_results: int = 20) -> list[str]:
        """Get top comments for a video."""
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                order="relevance",
                maxResults=max_results,
            )
            response = request.execute()

            comments = []
            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
            return comments
        except Exception as e:
            logger.warning(f"Could not get comments for {video_id}: {e}")
            return []

    def research_topic(self, topic: str) -> ResearchResult:
        """Full research pipeline: search -> filter by views & subscribers -> transcripts -> comments."""
        logger.info(f"=== Starting research on: '{topic}' ===")
        logger.info(
            f"  Quality filters: views >= {self.config.min_view_count:,} | "
            f"subscribers >= {self.config.min_subscriber_count:,}"
        )

        # Step 1: Search videos (fetch extra candidates for filtering)
        search_results = self.search_videos(topic)
        if not search_results:
            logger.warning("No videos found")
            return ResearchResult(topic=topic, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"), videos=[])

        # Step 2: Get video statistics and filter by view count
        video_ids = [v["video_id"] for v in search_results]
        stats = self.get_video_stats(video_ids)

        view_filtered = [
            r for r in search_results
            if stats.get(r["video_id"], {}).get("view_count", 0) >= self.config.min_view_count
        ]
        logger.info(
            f"  After view filter (>= {self.config.min_view_count:,}): "
            f"{len(view_filtered)}/{len(search_results)} videos"
        )

        if not view_filtered:
            logger.warning("No videos passed the view count filter")
            return ResearchResult(topic=topic, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"), videos=[])

        # Step 3: Get channel statistics and filter by subscriber count
        channel_ids = [r["channel_id"] for r in view_filtered]
        channel_stats = self.get_channel_stats(channel_ids)

        quality_results = [
            r for r in view_filtered
            if channel_stats.get(r["channel_id"], {}).get("subscriber_count", 0)
            >= self.config.min_subscriber_count
        ]
        logger.info(
            f"  After subscriber filter (>= {self.config.min_subscriber_count:,}): "
            f"{len(quality_results)}/{len(view_filtered)} videos"
        )

        if not quality_results:
            logger.warning("No videos passed the subscriber count filter")
            return ResearchResult(topic=topic, timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"), videos=[])

        # Limit to max_search_results after filtering
        quality_results = quality_results[: self.config.max_search_results]

        # Step 4: Fetch transcripts and comments only for quality videos
        videos = []
        for result in quality_results:
            vid = result["video_id"]
            video_stats = stats.get(vid, {})
            sub_count = channel_stats.get(result["channel_id"], {}).get("subscriber_count", 0)

            logger.info(
                f"  Processing: {result['title'][:55]}... "
                f"[{video_stats.get('view_count', 0):,} views | {sub_count:,} subs]"
            )
            transcript = self.get_transcript(vid)
            comments = self.get_comments(vid)

            videos.append(VideoData(
                video_id=vid,
                title=result["title"],
                channel=result["channel"],
                channel_id=result["channel_id"],
                description=result["description"],
                published_at=result["published_at"],
                view_count=video_stats.get("view_count", 0),
                like_count=video_stats.get("like_count", 0),
                comment_count=video_stats.get("comment_count", 0),
                subscriber_count=sub_count,
                transcript=transcript,
                top_comments=comments,
            ))

        # Sort by view count (most popular first)
        videos.sort(key=lambda v: v.view_count, reverse=True)

        research = ResearchResult(
            topic=topic,
            timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
            videos=videos,
        )

        # Save research data
        research.save(self.config.today_dir("research"))

        logger.info(f"=== Research complete: {len(videos)} quality videos analyzed ===")
        return research
