import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Video Interview Analysis API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for analyzing interview videos"

    # Azure Speech Service settings
    AZURE_SUBSCRIPTION_KEY: str = os.getenv("AZURE_SUBSCRIPTION_KEY", "")
    AZURE_SERVICE_REGION: str = os.getenv("AZURE_SERVICE_REGION", "southeastasia")

    # Gemini API settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_ID: str = os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-exp")

    # File paths
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    VIDEO_UPLOAD_DIR: Path = UPLOAD_DIR / "videos"
    AUDIO_UPLOAD_DIR: Path = UPLOAD_DIR / "audio"
    RESULTS_DIR: Path = BASE_DIR / "results"

    # File size limits
    MAX_UPLOAD_SIZE_MB: int = 1024 * 1024 * 500

    # Create necessary directories
    @property
    def setup_directories(self):
        self.VIDEO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        return True


settings = Settings()
settings.setup_directories
