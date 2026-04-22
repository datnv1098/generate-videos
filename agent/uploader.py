"""YouTube Upload Module - Upload videos to YouTube using OAuth2."""

import logging
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import Config
from .synthesizer import VideoScript

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",  # needed to list channels
]


class YouTubeUploader:
    def __init__(self, config: Config):
        self.config = config
        self.credentials = None
        self.youtube = None

    def authenticate(self):
        """Authenticate with YouTube API using OAuth2."""
        token_path = Path("token.pickle")

        # Load saved credentials
        if token_path.exists():
            with open(token_path, "rb") as f:
                self.credentials = pickle.load(f)

        # Refresh or get new credentials
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                logger.info("Refreshing OAuth2 token...")
                self.credentials.refresh(Request())
            else:
                if not Path(self.config.client_secrets_file).exists():
                    raise FileNotFoundError(
                        f"OAuth2 client secrets file not found: {self.config.client_secrets_file}\n"
                        "Download it from Google Cloud Console -> APIs & Services -> Credentials\n"
                        "Create an OAuth 2.0 Client ID (Desktop App) and download the JSON file."
                    )

                logger.info("Starting OAuth2 flow (browser will open)...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.client_secrets_file, SCOPES
                )
                self.credentials = flow.run_local_server(port=0)

            # Save credentials
            with open(token_path, "wb") as f:
                pickle.dump(self.credentials, f)
            logger.info("OAuth2 credentials saved")

        self.youtube = build("youtube", "v3", credentials=self.credentials)
        logger.info("YouTube API authenticated successfully")

    def list_channels(self) -> list[dict]:
        """List all YouTube channels associated with the authenticated account."""
        if not self.youtube:
            self.authenticate()

        response = self.youtube.channels().list(
            part="snippet,statistics",
            mine=True,
            maxResults=50,
        ).execute()

        channels = []
        for item in response.get("items", []):
            channels.append({
                "id": item["id"],
                "title": item["snippet"]["title"],
                "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                "video_count": int(item["statistics"].get("videoCount", 0)),
            })
        return channels

    def print_channels(self):
        """Print all channels to console for user to identify the right one."""
        channels = self.list_channels()
        print("\n" + "=" * 50)
        print("  YOUR YOUTUBE CHANNELS")
        print("=" * 50)
        for i, ch in enumerate(channels, 1):
            print(f"  [{i}] {ch['title']}")
            print(f"      Channel ID  : {ch['id']}")
            print(f"      Subscribers : {ch['subscriber_count']:,}")
            print(f"      Videos      : {ch['video_count']:,}")
            print()
        print(f"  To set a specific channel, add to .env:")
        print(f"  YOUTUBE_CHANNEL_ID=<channel_id_above>")
        print("=" * 50 + "\n")
        return channels

    def upload(self, video_path: Path, script: VideoScript, privacy: str = "private") -> str:
        """Upload a video to YouTube.

        Args:
            video_path: Path to the video file
            script: VideoScript with metadata
            privacy: 'private', 'unlisted', or 'public'

        Returns:
            The uploaded video ID
        """
        if not self.youtube:
            self.authenticate()

        # Show which channel will be used
        if self.config.youtube_channel_id:
            logger.info(f"Uploading to channel ID: {self.config.youtube_channel_id}")
        else:
            logger.info("No YOUTUBE_CHANNEL_ID set - uploading to default channel")
            logger.info("Run 'python main.py --list-channels' to see all your channels")

        logger.info(f"Uploading video: '{script.title}'")

        body = {
            "snippet": {
                "title": script.title[:100],
                "description": script.description[:5000],
                "tags": script.tags[:30],
                "categoryId": "22",  # People & Blogs (safe default)
                "defaultLanguage": self.config.language,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=10 * 1024 * 1024,  # 10MB chunks
        )

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        # Execute upload with progress tracking
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.info(f"  Upload progress: {progress}%")

        video_id = response["id"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"Upload complete! Video URL: {video_url}")

        return video_id
