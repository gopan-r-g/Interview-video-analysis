import os
from pathlib import Path
from moviepy import VideoFileClip
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def extract_audio_from_video(video_path: str, job_id: str) -> str:
    """
    Extract audio from video file.

    Parameters:
    -----------
    video_path : str
        Path to the video file
    job_id : str
        Job ID for uniquely naming the audio file

    Returns:
    --------
    str
        Path to the extracted audio file
    """
    try:
        # Generate audio filename
        audio_filename = f"{job_id}_audio.wav"
        audio_path = os.path.join(settings.AUDIO_UPLOAD_DIR, audio_filename)

        logger.info(f"Extracting audio from video {video_path} to {audio_path}")

        # Load the video file
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)

        # Close the clips
        audio_clip.close()
        video_clip.close()

        logger.info(f"Audio extraction completed: {audio_path}")
        return audio_path

    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        raise Exception(f"Failed to extract audio from video: {str(e)}")
