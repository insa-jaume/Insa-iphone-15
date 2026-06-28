"""Configuración central de la aplicación (cargada desde variables de entorno)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Prestador del servicio
    provider_name: str = "Jaume Insa Pérez"
    provider_nif: str = "21693936Z"
    provider_email: str = "contacto@example.es"
    provider_phone: str = ""
    provider_address: str = "España"
    site_name: str = "Alertas Oficiales"
    site_url: str = "http://localhost:8000"

    # App
    secret_key: str = "dev-insecure-secret-change-me"
    debug: bool = False
    price_eur: str = "5"

    # DB
    database_url: str = "postgresql+psycopg2://alertas:alertas@db:5432/alertas"

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Alertas Oficiales <alertas@example.es>"
    smtp_starttls: bool = True

    # Ingesta
    ingest_start_date: str = "2010-01-01"
    ingest_request_delay: float = 0.4
    ingest_daily_hour: int = 6

    @property
    def stripe_enabled(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_price_id)

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_host)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
