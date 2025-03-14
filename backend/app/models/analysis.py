from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
from ..schemas.analysis import ProcessingStatus


class AnalysisJob:
    """In-memory storage for job tracking"""

    def __init__(self, filename: str):
        self.job_id: str = str(uuid.uuid4())
        self.filename: str = filename
        self.original_filename: str = filename
        self.status: ProcessingStatus = ProcessingStatus.PENDING
        self.created_at: datetime = datetime.now()
        self.updated_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.video_path: Optional[str] = None
        self.audio_path: Optional[str] = None
        self.transcript: Optional[str] = None
        self.transcript_json_path: Optional[str] = None
        self.analysis_result: Optional[Dict[str, Any]] = None
        self.current_step: Optional[str] = None
        self.progress: float = 0.0
        self.error: Optional[str] = None

    def update_status(
        self,
        status: ProcessingStatus,
        step: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.status = status
        if step:
            self.current_step = step
        if error:
            self.error = error
        self.updated_at = datetime.now()
        if status == ProcessingStatus.COMPLETED:
            self.completed_at = datetime.now()
            self.progress = 1.0

    def update_progress(self, progress: float):
        self.progress = progress
        self.updated_at = datetime.now()


# Simple in-memory database to store analysis jobs
class AnalysisJobDB:
    def __init__(self):
        self.jobs: Dict[str, AnalysisJob] = {}

    def create_job(self, filename: str) -> AnalysisJob:
        job = AnalysisJob(filename)
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[AnalysisJob]:
        return list(self.jobs.values())


# Create a singleton instance
job_db = AnalysisJobDB()
