from fastapi import (
    APIRouter,
    UploadFile,
    File,
    BackgroundTasks,
    HTTPException,
    Depends,
    Form,
    Body,
    Query,
)
from fastapi.responses import JSONResponse, FileResponse
import os
from typing import Optional, List
import asyncio
import logging
from datetime import datetime
import json

from app.schemas.analysis import (
    VideoUploadResponse,
    AnalysisResponse,
    JobStatusResponse,
)
from app.models.analysis import job_db, ProcessingStatus
from app.services.analysis_service import process_video_job
from app.utils.file_utils import save_uploaded_file, is_video_file
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["analysis"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
):
    """
    Upload a video file for analysis.
    """
    try:
        logger.info(f"Uploading video: {file.filename}")
        # Validate video file
        if not is_video_file(file.filename):
            raise HTTPException(status_code=400, detail="Not a valid video file")

        # Create a new job
        job = job_db.create_job(file.filename)

        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        video_filename = f"{job.job_id}{file_extension}"

        # Save the uploaded file
        video_path = await save_uploaded_file(
            file, settings.VIDEO_UPLOAD_DIR, video_filename
        )
        job.video_path = video_path

        # Launch truly asynchronous background processing task
        asyncio.create_task(process_video_job(job.job_id))

        logger.info(f"Video uploaded successfully: {job.job_id}")

        return VideoUploadResponse(
            job_id=job.job_id,
            filename=file.filename,
            status=job.status,
            message="Video uploaded successfully. Processing has been started.",
            created_at=job.created_at,
        )

    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a job.
    """
    job = job_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        filename=job.original_filename,
        current_step=job.current_step,
        progress=job.progress,
        error=job.error,
    )


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs():
    """
    List all jobs.
    """
    jobs = job_db.list_jobs()
    return [
        JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            filename=job.original_filename,
            current_step=job.current_step,
            progress=job.progress,
            error=job.error,
        )
        for job in jobs
    ]


@router.get("/results/{job_id}", response_model=AnalysisResponse)
async def get_job_results(job_id: str):
    """
    Get the results of a completed job.
    """
    job = job_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == ProcessingStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"Job failed: {job.error}")

    if job.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not completed yet")

    return AnalysisResponse(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
        filename=job.original_filename,
        transcript=job.transcript,
        analysis_result=job.analysis_result,
        error=job.error,
    )


@router.get("/videos/{job_id}")
async def get_video(job_id: str):
    """
    Get the uploaded video file with proper range support.
    """
    job = job_db.get_job(job_id)
    if not job or not job.video_path:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check if the file exists on disk
    if not os.path.exists(job.video_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    # Get file extension and size
    file_extension = os.path.splitext(job.video_path)[1].lower()
    file_size = os.path.getsize(job.video_path)

    # Determine proper MIME type
    content_type = "video/mp4"  # Default
    if file_extension == ".avi":
        content_type = "video/x-msvideo"
    elif file_extension == ".mov":
        content_type = "video/quicktime"
    elif file_extension == ".webm":
        content_type = "video/webm"

    # Use simpler FileResponse which handles ranges automatically
    return FileResponse(
        job.video_path, media_type=content_type, filename=job.original_filename
    )
