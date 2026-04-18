import asyncio
import subprocess
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from backend.api import ingestion_queue as iq
from backend.api.routes import router
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.api.routes import load_persisted_settings
    load_persisted_settings()
    task = asyncio.create_task(iq.worker())
    yield
    task.cancel()


app = FastAPI(title="Acerola RAG", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")


def _start_streamlit() -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "backend/ui/streamlit_app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true",
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Acerola RAG")
    parser.add_argument("--dev", action="store_true", help="Habilita reload automático da API")
    parser.add_argument("--api-only", action="store_true", help="Sobe só a FastAPI (sem UI)")
    args = parser.parse_args()

    ui_proc = None if args.api_only else _start_streamlit()

    try:
        uvicorn.run(
            "backend.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=args.dev,
        )
    finally:
        if ui_proc:
            ui_proc.terminate()
