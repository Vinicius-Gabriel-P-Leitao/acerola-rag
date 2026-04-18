from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.api.ingestion_queue import IngestionJob, JobStatus, _process_job


def _make_job(exists: bool = True) -> IngestionJob:
    path = MagicMock(spec=Path)
    path.unlink = MagicMock()
    return IngestionJob(filename="test.pdf", file_path=path)


def test_process_job_deletes_file_after_success():
    job = _make_job()
    with patch("backend.rag.pipeline.ingest_file"), \
         patch("backend.rag.engine.refresh_engine"):
        _process_job(job)

    job.file_path.unlink.assert_called_once_with(missing_ok=True)


def test_process_job_does_not_delete_on_error():
    job = _make_job()

    with patch("backend.rag.pipeline.ingest_file", side_effect=RuntimeError("boom")), \
         patch("backend.rag.engine.refresh_engine"):
        try:
            _process_job(job)
        except RuntimeError:
            pass

    job.file_path.unlink.assert_not_called()


def test_job_status_starts_as_pending():
    job = IngestionJob(filename="a.pdf", file_path=Path("a.pdf"))
    assert job.status == JobStatus.PENDING


def test_job_has_unique_ids():
    j1 = IngestionJob(filename="a.pdf", file_path=Path("a.pdf"))
    j2 = IngestionJob(filename="b.pdf", file_path=Path("b.pdf"))
    assert j1.job_id != j2.job_id
