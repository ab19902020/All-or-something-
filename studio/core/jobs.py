from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
import traceback
import uuid
from typing import Any, Callable


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Job:
    id: str
    kind: str
    project_id: str
    status: str = "queued"
    message: str = "Queued"
    progress: float = 0.0
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    result: Any = None
    error: str | None = None

    def public(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "project_id": self.project_id,
            "status": self.status,
            "message": self.message,
            "progress": self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error,
        }


class JobManager:
    def __init__(self, workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max(1, workers), thread_name_prefix="urs")
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()

    def submit(self, kind: str, project_id: str, fn: Callable[[], Any]) -> Job:
        job = Job(id=uuid.uuid4().hex, kind=kind, project_id=project_id)
        with self.lock:
            self.jobs[job.id] = job

        def run():
            self._update(job.id, status="running", message="Working", progress=0.1)
            try:
                result = fn()
                self._update(job.id, status="done", message="Complete", progress=1.0, result=result)
            except Exception as exc:
                self._update(
                    job.id,
                    status="failed",
                    message=str(exc),
                    progress=1.0,
                    error="".join(traceback.format_exception_only(type(exc), exc)).strip(),
                )

        self.executor.submit(run)
        return job

    def _update(self, job_id: str, **values) -> None:
        with self.lock:
            job = self.jobs[job_id]
            for key, value in values.items():
                setattr(job, key, value)
            job.updated_at = _now()

    def get(self, job_id: str) -> Job | None:
        with self.lock:
            return self.jobs.get(job_id)

    def recent(self, project_id: str | None = None, limit: int = 30) -> list[dict]:
        with self.lock:
            jobs = list(self.jobs.values())
        if project_id:
            jobs = [j for j in jobs if j.project_id == project_id]
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return [j.public() for j in jobs[:limit]]
