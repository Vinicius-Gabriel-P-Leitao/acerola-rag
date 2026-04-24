import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

logger = logging.getLogger(__name__)

class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


@dataclass
class IngestionJob:
    filename: str
    file_path: Path
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: JobStatus = JobStatus.PENDING
    error: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str | None = None


_queue: asyncio.Queue[IngestionJob] = asyncio.Queue()
_jobs: dict[str, IngestionJob] = {}
# Aumentado para 4 workers para processamento paralelo
_executor = ThreadPoolExecutor(max_workers=4)


def enqueue(job: IngestionJob) -> None:
    logger.info(f"Enfileirando trabalho: {job.filename} (ID: {job.job_id})")
    _jobs[job.job_id] = job
    _queue.put_nowait(job)


def get_job(job_id: str) -> IngestionJob | None:
    return _jobs.get(job_id)


def all_jobs() -> list[IngestionJob]:
    return list(_jobs.values())


def queue_size() -> int:
    return _queue.qsize()


def _process_job(job: IngestionJob) -> None:
    from backend.rag.engine import refresh_engine
    from backend.rag.pipeline import ingest_file

    logger.info(f"Iniciando processamento: {job.filename} (ID: {job.job_id})")

    # Silenciamento radical da pypdf
    logging.getLogger("pypdf").setLevel(logging.ERROR)

    try:
        ingest_file(job.file_path)
        refresh_engine()
        job.file_path.unlink(missing_ok=True)
        logger.info(f"Processamento concluído: {job.filename} (ID: {job.job_id})")
    except Exception as e:
        logger.error(f"Erro ao processar {job.filename}: {e}")
        raise


async def worker() -> None:
    loop = asyncio.get_event_loop()
    while True:
        job = await _queue.get()
        job.status = JobStatus.PROCESSING
        try:
            await loop.run_in_executor(_executor, _process_job, job)
            job.status = JobStatus.DONE
        except Exception as exc:
            job.status = JobStatus.ERROR
            job.error = str(exc)
        finally:
            job.finished_at = datetime.now(UTC).isoformat()
            _queue.task_done()

