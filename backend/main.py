import asyncio
import logging
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ── Logging setup ─────────────────────────────────────────────────────────────

def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-8s  %(name)s — %(message)s",
        force=True,
    )

    # Silencia libs verbosas que poluem o console
    for _noisy in (
        "httpx", "httpcore",
        "llama_index", "llama_index.core",
        "openai", "openai._base_client",
        "google", "google.auth",
        "urllib3", "multipart",
    ):
        logging.getLogger(_noisy).setLevel(logging.WARNING)

    _thread_log = logging.getLogger("acerola.thread")

    def _thread_excepthook(args: threading.ExceptHookArgs) -> None:
        exc = args.exc_value
        tname = args.thread.name if args.thread else "thread"
        ename = type(exc).__name__ if exc else "UnknownError"
        emsg = str(exc) if exc else ""

        # Erros de API conhecidos: mostra só o essencial, sem traceback
        _api_errs = ("RateLimitError", "AuthenticationError", "APIConnectionError",
                     "APIError", "ResourceExhausted")
        if any(k in ename for k in _api_errs) or "429" in emsg:
            short = emsg.split("\n")[0][:300]
            _thread_log.warning("(%s) %s: %s", tname, ename, short)
            return

        # Outros erros: traceback condensado (últimos 3 frames)
        import traceback as _tb
        frames = _tb.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
        condensed = "".join(frames[-3:]) if len(frames) > 3 else "".join(frames)
        _thread_log.error("(%s) %s\n%s", tname, ename, condensed.rstrip())

    threading.excepthook = _thread_excepthook


_setup_logging()

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.api import ingestion_queue as iq
from backend.api.dtos import ErrorResponse
from backend.api.routes import router
from backend.config import settings

_FRONTEND_BUILD = Path(__file__).parent.parent / "frontend" / "build"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.api.routes import load_persisted_settings
    from backend.history import manager as hist

    load_persisted_settings()
    hist.init(Path(__file__).parent / "data" / "history.db")
    task = asyncio.create_task(iq.worker())
    yield
    task.cancel()


app = FastAPI(title="Acerola RAG", version="0.1.0", lifespan=lifespan)

_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=str(exc.detail),
                code=f"HTTP_{exc.status_code}"
            ).model_dump()
        )

    logging.getLogger("acerola").error("Unhandled error on %s: %s", request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Erro interno do servidor",
            code="INTERNAL_SERVER_ERROR",
            detail=f"{type(exc).__name__}: {exc}"
        ).model_dump()
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=str(exc.detail),
            code=f"HTTP_{exc.status_code}"
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Erro de validação nos dados enviados",
            code="VALIDATION_ERROR",
            detail=exc.errors()
        ).model_dump()
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
