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

    # --- 문서 군집화 대시보드(업무명=03.문서 군집화) ---
    # 원본(정찬성/ipynb/data/topics, Opinosis 51개 리뷰 문서)은 루트 .gitignore가
    # "정찬성/ipynb/data" 전체를 배포 제외 대상으로 막아둬(§운영오류1과 동일한 함정)
    # Render에 배포되지 않는다. creditcard_sample.csv와 같은 방식으로 semi-backend/data/
    # 밑에 51개 원본 그대로(828KB, 용량 문제 없음) 복사해 git 배포 가능하게 만든 경로가 기본값.
    doc_clustering_topics_dir: str = "data/doc_clustering_topics"


@lru_cache
def get_settings() -> Settings:
    return Settings()
