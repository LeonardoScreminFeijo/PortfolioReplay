from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cache_ttl_hours: int = 24
    cache_dir: str = ".cache"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
