from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoUploadResponse(BaseModel):
    job_id: str
    filename: str
    status: ProcessingStatus
    message: str
    created_at: datetime


class TranscriptionItem(BaseModel):
    speaker_id: str
    start_time: str
    end_time: str
    text: str
    confidence: Optional[float] = None


class AnalysisRequest(BaseModel):
    job_id: str


class AnalysisResponse(BaseModel):
    job_id: str
    status: ProcessingStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    filename: str
    transcript: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: ProcessingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    filename: str
    current_step: Optional[str] = None
    progress: Optional[float] = None
    error: Optional[str] = None
