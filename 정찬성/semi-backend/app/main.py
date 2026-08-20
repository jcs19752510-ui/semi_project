from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.domains.dataviz.router import router as dataviz_router

app = FastAPI(title="SEMI Backend", version="0.1.0")

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# 다음 도메인부터는 여기서 계속 등록한다.
# from app.domains.<도메인명>.router import router as <도메인명>_router
# app.include_router(<도메인명>_router)
app.include_router(dataviz_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
