from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    max_file_size_mb: int = 50
    file_ttl_seconds: int = 3600
    session_secret: str = "change-me-to-a-random-string"
    data_dir: str = "/data"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
