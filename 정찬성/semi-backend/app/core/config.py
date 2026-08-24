from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    field_encryption_key: str = ""

    session_cookie_name: str = "semi_session"
    session_ttl_seconds: int = 3600

    santander_csv_path: str = "../santander-customer-satisfaction/train.csv"
    # 원본(ipynb/data/creditcard.csv, 284,807행·144MB)은 .gitignore 대상이고 GitHub
    # 파일당 100MB 제한도 넘어 배포가 안 된다(§운영오류1·2 장애 원인). ml.py의 대용량
    # 학습 상한(MAX_TRAIN_ROWS=80,000)과 동일한 random_state=42 계층화 표본을 미리 뽑아
    # git으로 배포 가능한 semi-backend/data/creditcard_sample.csv를 기본값으로 쓴다.
    creditcard_csv_path: str = "data/creditcard_sample.csv"


@lru_cache
def get_settings() -> Settings:
    return Settings()
