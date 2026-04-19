import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router, prefix="/api/v1")

if _FRONTEND_BUILD.exists():
    app.mount("/_app", StaticFiles(directory=str(_FRONTEND_BUILD / "_app")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = _FRONTEND_BUILD / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_FRONTEND_BUILD / "index.html"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Acerola RAG")
    parser.add_argument("--dev", action="store_true", help="Habilita reload automático")
    args = parser.parse_args()

    # Resolve o módulo correto dependendo de como o script foi invocado
    _module = f"{__package__ + '.' if __package__ else ''}main:app"

    uvicorn.run(
        _module,
        host=settings.api_host,
        port=settings.api_port,
        reload=args.dev,
    )
