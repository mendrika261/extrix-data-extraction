from datetime import datetime, timedelta, timezone
import uuid
from typing import Dict, Any
from web.models import JobStatus, JobResponse


class JobStore:
    _instance = None
    _jobs: Dict[str, JobResponse] = {}
    _max_active_jobs = 5
    _retention_period = timedelta(minutes=5)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def cleanup_old_jobs(self):
        now = datetime.now(timezone.utc)
        completed_statuses = [JobStatus.COMPLETED, JobStatus.FAILED]

        self._jobs = {
            job_id: job
            for job_id, job in self._jobs.items()
            if not job.fetched
            or job.status not in completed_statuses
            or (now - job.created_at) < self._retention_period
        }

    def create_job(self) -> str:
        self.cleanup_old_jobs()

        job_id = str(uuid.uuid4())
        self._jobs[job_id] = JobResponse(job_id=job_id, status=JobStatus.PENDING)
        return job_id

    def get_job(self, job_id: str) -> JobResponse:
        job = self._jobs.get(job_id)
        if job and job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            job.fetched = True
        return job

    def update_job(
        self, job_id: str, status: JobStatus, result: Any = None, error: str = None
    ):
        if job_id in self._jobs:
            self._jobs[job_id].status = status
            if result is not None:
                self._jobs[job_id].result = result
            if error is not None:
                self._jobs[job_id].error = error

    def count_active_jobs(self) -> int:
        return sum(
            1
            for job in self._jobs.values()
            if job.status in [JobStatus.PENDING, JobStatus.PROCESSING]
        )

    def can_accept_job(self) -> bool:
        return self.count_active_jobs() < self._max_active_jobs

    @property
    def max_active_jobs(self) -> int:
        return self._max_active_jobs

    @max_active_jobs.setter
    def max_active_jobs(self, value: int):
        if value < 1:
            raise ValueError("Maximum active jobs must be at least 1")
        self._max_active_jobs = value

    @property
    def retention_period(self) -> timedelta:
        return self._retention_period

    @retention_period.setter
    def retention_period(self, value: timedelta):
        if value < timedelta(minutes=5):
            raise ValueError("Retention period must be at least 5 minutes")
        self._retention_period = value
