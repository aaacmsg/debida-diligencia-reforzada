from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Diligencia Reforzada EDD"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/diligencia_db"

    # Security
    secret_key: str = "diligencia-reforsada-dev-secret-key-2026-not-for-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # File Upload
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"
    allowed_extensions: list = ["pdf", "png", "jpg", "jpeg"]

    # PEP Data (datosabiertos.gob.pa)
    datos_abiertos_base_url: str = "https://www.datosabiertos.gob.pa/api/3"
    datos_abiertos_download_base: str = "https://monitoreo.antai.gob.pa/api/designations/download"

    # Scoring Weights
    score_pais_peso: float = 0.25
    score_cargo_peso: float = 0.30
    score_sector_peso: float = 0.15
    score_vinculos_peso: float = 0.20
    score_origen_fondos_peso: float = 0.10

    # Thresholds
    fuzzy_match_threshold: int = 85
    beneficiario_final_porcentaje_min: float = 10.0

    # Risk Thresholds
    riesgo_bajo_max: int = 35
    riesgo_medio_max: int = 65

    # Retention
    retention_years: int = 5

    # Redis (Celery / cache)
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
