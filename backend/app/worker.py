from celery import Celery
import os
from app.models.analysis import job_db, ProcessingStatus
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Get Redis URL from environment or use default
redis_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery("video_analysis", broker=redis_url, backend=redis_url)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)


# Define the video processing task
@celery_app.task(bind=True, name="process_video")
def process_video_task(self, job_id: str, video_path: str, filename: str):
    """Process a video in a separate worker process"""
    logger.info(f"Starting processing for job {job_id}")

    # Import here to avoid circular imports
    from app.services.analysis_service import process_video_job_sync

    try:
        # Update task ID in job
        job = job_db.get_job(job_id)
        if job:
            job.celery_task_id = self.request.id

        # Process the video
        process_video_job_sync(job_id)

        logger.info(f"Completed processing for job {job_id}")
        return {"status": "success", "job_id": job_id}

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")

        # Update job status in case of error
        job = job_db.get_job(job_id)
        if job:
            job.update_status(ProcessingStatus.FAILED, error=str(e))

        # Raise exception to mark task as failed
        raise
