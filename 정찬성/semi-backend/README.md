# semi-backend

`../1. 기술 스택/1. 기술 스택(신규).md`에 명시된 스택으로 구성한 1단계(기반 구조)다.
도메인 로직(로그인, 메뉴 등)은 아직 없다 — `app/domains/README.md` 참고.

## 스택

| 구성요소 | 버전 |
|---|---|
| Python | 3.12+ |
| FastAPI | 0.139.0 |
| Pydantic | 2.13.4 |
| SQLAlchemy | 2.0.51 |
| Alembic | 1.19.1 |
| psycopg | 3.3.4 |
| pwdlib[argon2] | 0.3.0 |
| cryptography | 50.0.0 |
| Uvicorn | 0.50.0 |
| PostgreSQL | 16 (Docker) |

## 실행 순서

```bash
# 1) 가상환경 + 의존성
python -m venv .venv
.venv\Scripts\activate        # (bash: source .venv/bin/activate)
pip install -e ".[dev]"

# 2) 환경변수
copy .env.example .env        # (bash: cp .env.example .env)
# .env 안의 FIELD_ENCRYPTION_KEY를 아래 명령으로 발급해 채워 넣는다
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 3) PostgreSQL 16 기동
docker compose up -d
# 이 개발 환경은 5432가 이미 다른 컨테이너(toyo-db)에 점유되어 있어
# .env에서 POSTGRES_PORT=5555 / DATABASE_URL 포트도 5555로 맞춰뒀다.
# 다른 환경에서 5432가 비어 있으면 .env.example 기본값(5432)을 그대로 써도 된다.

# 4) 마이그레이션 (도메인이 추가되면)
alembic upgrade head

# 5) 서버 실행
uvicorn app.main:app --reload
# http://127.0.0.1:8000/health
# http://127.0.0.1:8000/docs

# 6) 테스트
pytest
```

## 새 도메인 추가 시

1. `app/domains/<도메인명>/{models,schemas,crud,router}.py` 생성
2. `alembic/env.py`에 해당 `models` import 추가(autogenerate가 인식하도록)
3. `alembic revision --autogenerate -m "add <도메인명>"` → `alembic upgrade head`
4. `app/main.py`에 `include_router()` 등록
