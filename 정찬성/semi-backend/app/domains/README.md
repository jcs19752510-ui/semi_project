# domains/

도메인별 수직 분할(vertical slice) 구조를 따른다. 각 도메인은 아래 4개 파일을 갖는다.

```
domains/<도메인명>/
├── models.py    # SQLAlchemy Mapped 모델
├── schemas.py   # Pydantic 요청/응답 스키마
├── crud.py      # DB 조회/조작 함수
└── router.py    # FastAPI APIRouter
```

`app/main.py`에서 각 도메인의 `router`를 `include_router()`로 등록한다.

다음 단계(A-1 로그인 등)부터 이 규칙대로 도메인을 하나씩 추가한다.

## 예외: `dataviz/`

DB 테이블이 아니라 캐글 CSV 원본을 그대로 읽는 데이터 탐색 대시보드라
`models.py`가 없다. 대신 `crud.py`가 `get_dataframe()`을 FastAPI `Depends`로
노출해 테스트에서 `app.dependency_overrides`로 표본 DataFrame으로 갈아끼울
수 있게 했다 — DB 세션을 `Depends(get_db)`로 주입하는 것과 같은 목적이다.
