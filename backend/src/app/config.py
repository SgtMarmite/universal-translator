from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_chat_model_deployment_name: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"

    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    max_file_size_mb: int = 50
    file_ttl_seconds: int = 3600
    redis_url: str = "redis://redis:6379/0"
    session_secret: str = "change-me-to-a-random-string"
    data_dir: str = "/data"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
