from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    recall_api_key: str
    recall_api_base_url: AnyHttpUrl = "https://api.recall.ai"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

