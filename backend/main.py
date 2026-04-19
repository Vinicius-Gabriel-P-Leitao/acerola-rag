import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import ingestion_queue as iq
from backend.api.routes import router
from backend.config import settings

_FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "build"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.api.routes import load_persisted_settings
    load_persisted_settings()
    task = asyncio.create_task(iq.worker())
    yield
    task.cancel()


app = FastAPI(title="Acerola RAG", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")

if _FRONTEND_BUILD.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_BUILD), html=True), name="spa")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Acerola RAG")
    parser.add_argument("--dev", action="store_true", help="Habilita reload automático")
    args = parser.parse_args()

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=args.dev,
    )
