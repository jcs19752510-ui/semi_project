from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    field_encryption_key: str = ""

    session_cookie_name: str = "semi_session"
    session_ttl_seconds: int = 3600

    santander_csv_path: str = "../santander-customer-satisfaction/train.csv"
    creditcard_csv_path: str = "../ipynb/data/creditcard.csv"


@lru_cache
def get_settings() -> Settings:
    return Settings()
