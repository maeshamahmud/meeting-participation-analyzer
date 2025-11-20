from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    recall_api_key: str
    recall_region: str  # e.g. "us-west-2"

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # ignore env vars we don't have fields for
    )


settings = Settings()
