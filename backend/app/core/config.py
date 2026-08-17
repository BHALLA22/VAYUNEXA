"""
FILE: backend/app/core/config.py

PURPOSE:
Loads configuration from environment variables via .env into
one typed Settings object.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database ---
    database_url: str = "postgresql://vayunexa:vayunexa_dev_password@localhost:5432/vayunexa"

    # --- Security ---
    api_token: str = "dev-token-change-me"
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:5173,http://127.0.0.1:5173"
    )

    # --- Weather provider ---
    weather_api_provider: str = "open-meteo"
    weather_api_key: str = ""
    weather_lat: float = 29.6856
    weather_lon: float = 76.9905

    # --- AI model artifacts ---
    ai_model_path: str = "../ai/models/energy_model.joblib"
    ai_metrics_path: str = "../ai/models/metrics.json"

    # --- Prototype physical constants ---
    servo_energy_mw_per_degree: float = 5.0

    # --- Misc ---
    environment: str = "development"
    backend_port: int = 8000

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Cached so settings are parsed once per process."""
    return Settings()


settings = get_settings()

