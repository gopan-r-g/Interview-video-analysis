import os
import json
import time
import pathlib
import re
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from app.config import settings
from app.models.analysis import job_db, ProcessingStatus
from app.services.audio_service import extract_audio_from_video
from app.services.transcription_service import transcribe_audio_with_diarization
from app.utils.prompts import (
    VIDEO_ANALYSIS_SYSTEM_PROMPT,
    VIDEO_ANALYSIS_USER_PROMPT,
    SCORING_SYSTEM_PROMPT,
    SCORING_USER_PROMPT,
)
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
# Create a thread pool executor
thread_pool = ThreadPoolExecutor()


def extract_json_from_markdown(markdown_string: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from a markdown code block string.
    """
    # Remove markdown code block indicators and newlines
    json_string = markdown_string.strip()
    json_string = re.sub(r"^```json\n", "", json_string)
    json_string = re.sub(r"\n```$", "", json_string)

    # Replace escaped newlines with actual newlines
    json_string = json_string.replace("\\n", "\n")

    # Replace escaped quotes with actual quotes
    json_string = json_string.replace("\\'", "'")

    try:
        # Parse the JSON string into a Python dictionary
        json_obj = json.loads(json_string)
        return json_obj
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from markdown: {str(e)}")
        logger.error(f"JSON string: {json_string}")
        raise Exception(f"Failed to parse analysis result: {str(e)}")


def analyze_body_language(video_path: str, transcript: str) -> Dict[str, Any]:
    """
    Analyze body language using Gemini AI.
    """
    # Initialize Gemini client
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model_id = settings.GEMINI_MODEL_ID

    try:
        # Upload the file using the API
        file_upload = client.files.upload(file=pathlib.Path(video_path))

        # Wait for video to be processed
        while file_upload.state == "PROCESSING":
            logger.info("Waiting for video to be processed by Gemini AI.")
            time.sleep(10)
            file_upload = client.files.get(name=file_upload.name)

        if file_upload.state == "FAILED":
            raise ValueError(f"Video processing failed with state: {file_upload.state}")

        logger.info(f"Video processing complete: {file_upload.uri}")

        # Define system and user prompts
        system_prompt = VIDEO_ANALYSIS_SYSTEM_PROMPT

        user_prompt = VIDEO_ANALYSIS_USER_PROMPT.format(transcript=transcript)

        # Send request to Gemini
        response = client.models.generate_content(
            model=model_id,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=file_upload.uri, mime_type=file_upload.mime_type
                        ),
                    ],
                ),
                user_prompt,
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
            ),
        )

        # Extract JSON from response
        return extract_json_from_markdown(response.text)

    except Exception as e:
        logger.error(f"Error analyzing body language: {str(e)}")
        raise Exception(f"Failed to analyze video: {str(e)}")


def score_candidate(transcript: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score the candidate based on the transcript and analysis result.
    """
    # Initialize Gemini client
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    model_id = settings.GEMINI_MODEL_ID

    try:
        # Define scoring system prompt
        scoring_system_prompt = SCORING_SYSTEM_PROMPT

        # Define scoring user prompt
        scoring_user_prompt = SCORING_USER_PROMPT.format(
            transcript=transcript,
            video_and_audio_analysis_report=json.dumps(analysis_result, indent=2),
        )

        # Send request to Gemini
        response = client.models.generate_content(
            model=model_id,
            contents=[scoring_user_prompt],
            config=types.GenerateContentConfig(
                system_instruction=scoring_system_prompt,
                temperature=0.0,
            ),
        )

        # Extract JSON from response
        return extract_json_from_markdown(response.text)

    except Exception as e:
        logger.error(f"Error scoring candidate: {str(e)}")
        raise Exception(f"Failed to score candidate: {str(e)}")


async def process_video_job(job_id: str):
    """
    Process a video job asynchronously.
    """
    job = job_db.get_job(job_id)
    if not job:
        logger.error(f"Job not found: {job_id}")
        return

    try:
        # Update job status to processing
        job.update_status(ProcessingStatus.PROCESSING, "Starting video processing")

        # Step 1: Extract audio from video - Run in thread pool
        job.update_status(ProcessingStatus.PROCESSING, "Extracting audio from video")
        job.update_progress(0.1)
        audio_path = await asyncio.get_event_loop().run_in_executor(
            thread_pool, extract_audio_from_video, job.video_path, job_id
        )
        job.audio_path = audio_path
        job.update_progress(0.2)

        # Step 2: Transcribe audio with speaker diarization - Run in thread pool
        job.update_status(ProcessingStatus.PROCESSING, "Transcribing audio")
        job.update_progress(0.3)
        transcript = await asyncio.get_event_loop().run_in_executor(
            thread_pool, transcribe_audio_with_diarization, audio_path, job_id
        )
        job.transcript = transcript
        job.transcript_json_path = os.path.join(
            settings.RESULTS_DIR, f"{job_id}_transcript.json"
        )
        job.update_progress(0.5)

        # Step 3: Analyze body language - Run in thread pool
        job.update_status(ProcessingStatus.PROCESSING, "Analyzing body language")
        job.update_progress(0.6)
        analysis_result = await asyncio.get_event_loop().run_in_executor(
            thread_pool, analyze_body_language, job.video_path, transcript
        )
        job.update_progress(0.8)

        # Step 4: Score candidate - Run in thread pool
        job.update_status(ProcessingStatus.PROCESSING, "Scoring candidate")
        job.update_progress(0.9)
        scoring_result = await asyncio.get_event_loop().run_in_executor(
            thread_pool, score_candidate, transcript, analysis_result
        )

        # Combine results
        final_result = {
            "body_language_analysis": analysis_result,
            "candidate_score": scoring_result,
        }
        print("#" * 20)
        print(final_result)
        print("#" * 20)

        # Save results to a file
        results_path = os.path.join(settings.RESULTS_DIR, f"{job_id}_results.json")
        with open(results_path, "w") as f:
            json.dump(final_result, f, indent=4)

        # Update job with final result
        job.analysis_result = final_result
        job.update_status(ProcessingStatus.COMPLETED)

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        error_message = str(e)
        logger.error(f"Error processing job {job_id}: {error_message}")
        job.update_status(ProcessingStatus.FAILED, error=error_message)
