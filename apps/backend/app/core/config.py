from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-2024-08-06"

    class Config:
        env_file = ".env"


settings = Settings()
