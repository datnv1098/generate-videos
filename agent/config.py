import logging
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    # API Keys
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # YouTube OAuth2
    client_secrets_file: str = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
    youtube_channel_id: str = ""  # Set via --channel-id CLI arg only

    # Agent settings
    language: str = os.getenv("DEFAULT_LANGUAGE", "en")
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))

    # Quality filters
    min_view_count: int = int(os.getenv("MIN_VIEW_COUNT", "100000"))
    min_subscriber_count: int = int(os.getenv("MIN_SUBSCRIBER_COUNT", "10000"))
    # Fetch more candidates initially so we have enough after filtering
    search_candidate_multiplier: int = 3
    video_width: int = 1920
    video_height: int = 1080
    tts_voice: str = os.getenv("TTS_VOICE", "en-US-AriaNeural")

    # LLM settings
    openai_model: str = "gpt-4o"
    max_tokens: int = 4096

    # Paths
    output_dir: Path = field(default_factory=lambda: Path("output"))

    def __post_init__(self):
        if self.language.lower() != "en":
            logger.warning("DEFAULT_LANGUAGE=%s is not supported for this pipeline. Falling back to English.", self.language)
            self.language = "en"

        if not self.tts_voice.lower().startswith("en-"):
            logger.warning("TTS_VOICE=%s is not an English voice. Falling back to en-US-AriaNeural.", self.tts_voice)
            self.tts_voice = "en-US-AriaNeural"

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def today_dir(self, subdir: str) -> Path:
        """Return output/<subdir>/YYYY-MM-DD/, creating it if needed."""
        path = self.output_dir / subdir / date.today().isoformat()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate(self):
        errors = []
        if not self.youtube_api_key:
            errors.append("YOUTUBE_API_KEY is not set")
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is not set")
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
