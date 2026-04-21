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

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


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
