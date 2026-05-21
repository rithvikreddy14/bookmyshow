import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Settings:
    # Database Settings
    DATABASE_URL: str = os.environ["DATABASE_URL"]

    # JWT Security Settings
    SECRET_KEY: str = os.environ["SECRET_KEY"]

    # Optional settings with defaults
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
    )


settings = Settings()