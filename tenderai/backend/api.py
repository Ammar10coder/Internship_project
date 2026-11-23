from pathlib import Path
from contextlib import asynccontextmanager
from typing import Literal
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from .documents import extract_pdf
from .scoring import classify
from .storage import Store

ROOT = Path(__file__).resolve().parents[1]


class Tender(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1, max_length=20000)


def create_app(database=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.store = Store(database or ROOT / "data" / "tenders.db")
        yield

    app = FastAPI(title="TenderAI", lifespan=lifespan)

    @app.post("/api/extract")
    async def extract(file: UploadFile = File(...)):
        data = await file.read(5_000_001)
        if len(data) > 5_000_000:
            raise HTTPException(413, "Use a PDF under 5 MB.")
        try:
            return {"text": await run_in_threadpool(extract_pdf, data)}
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.post("/api/tenders", status_code=201)
    def screen(item: Tender):
        title, body = item.title.strip(), item.description.strip()
        if not title or not body:
            raise HTTPException(422, "Enter a title and a scope of work.")
        return app.state.store.save(title, body, classify(body))

    @app.get("/api/tenders")
    def history(decision: Literal["", "GO", "NO-GO"] = ""):
        return app.state.store.history(decision)

    from . import portal

    @app.get("/api/portal")
    def portal_cache():
        return portal.cached()

    @app.post("/api/portal/refresh")
    def refresh_portal():
        try:
            return portal.refresh()
        except (OSError, ValueError) as exc:
            raise HTTPException(503, "CPPP could not be refreshed. Previous results are still available.") from exc

    app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True))
    return app


app = create_app()
