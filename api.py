from pathlib import Path
import traceback
import uuid
from fastapi import (
    FastAPI,
    UploadFile,
    BackgroundTasks,
    HTTPException,
    File,
    Body,
)
from web.models import ExtractorConfig, JobResponse, JobStatus
from web.job_store import JobStore
from core.service import extract_from_config

app = FastAPI()

job_store = JobStore()

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def save_upload_file(upload_file: UploadFile) -> Path:
    file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{upload_file.filename}"
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path


async def process_file(job_id: str, file_path: Path, config: ExtractorConfig):
    try:
        job_store.update_job(job_id, JobStatus.PROCESSING)

        result = extract_from_config(
            file_path=file_path,
            config=config,
        )

        if hasattr(result, "model_dump"):
            result = result.model_dump()

        job_store.update_job(job_id, JobStatus.COMPLETED, result=result)
    except Exception as e:
        error_details = f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        job_store.update_job(job_id, JobStatus.FAILED, error=error_details)
    finally:
        file_path.unlink(missing_ok=True)


@app.post("/extract")
async def extract_file(
    background_tasks: BackgroundTasks,
    config: str = Body(...),
    file: UploadFile = File(...),
) -> JobResponse:
    if not job_store.can_accept_job():
        raise HTTPException(
            status_code=429,
            detail=f"Maximum number of concurrent jobs ({job_store.max_active_jobs}) reached. Please try again later.",
        )

    if config:
        config = ExtractorConfig.model_validate_json(config)

    try:
        job_id = job_store.create_job()
        file_path = save_upload_file(file)

        background_tasks.add_task(process_file, job_id, file_path, config)

        return job_store.get_job(job_id)
    except Exception as e:
        error_details = (
            f"File processing error: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        )
        if "job_id" in locals():
            job_store.update_job(job_id, JobStatus.FAILED, error=error_details)
        raise HTTPException(status_code=500, detail=error_details)


@app.get("/status/{job_id}")
async def get_status(job_id: str) -> JobResponse:
    job = job_store.get_job(job_id)
    if job is None:
        return JobResponse(
            job_id=job_id, status=JobStatus.FAILED, error="Job not found"
        )
    return job
