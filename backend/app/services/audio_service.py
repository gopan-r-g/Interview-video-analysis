import os
from pathlib import Path
from moviepy import VideoFileClip
from app.config import settings
import logging
import subprocess

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


def extract_audio_from_video_with_ffmpeg(video_path: str, job_id: str) -> str:
    """
    Extract audio from video file and compress if needed to stay under size limits.

    Parameters:
    -----------
    video_path : str
        Path to the video file
    job_id : str
        Job ID for uniquely naming the audio file

    Returns:
    --------
    str
        Path to the extracted (and possibly compressed) audio file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(settings.AUDIO_UPLOAD_DIR, exist_ok=True)

        # Generate audio filename
        audio_filename = f"{job_id}_audio.wav"
        audio_path = os.path.join(settings.AUDIO_UPLOAD_DIR, audio_filename)

        # Initial extraction with moderate quality
        logger.info(f"Extracting audio from video {video_path} to {audio_path}")

        # Extract audio with ffmpeg using a subprocess
        extract_command = [
            "ffmpeg",
            "-i",
            video_path,  # Input file
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",  # PCM format
            "-ar",
            "22050",  # Improved from 16kHz to 22.05kHz (better quality)
            "-ac",
            "2",  # Stereo instead of mono for better spatial quality
            "-q:a",
            "3",  # Audio quality setting (lower is better, 3 is good)
            "-y",  # Overwrite output file if exists
            audio_path,
        ]
        # Run the extraction
        subprocess.run(extract_command, check=True, capture_output=True, text=True)
        logger.info(f"Initial audio extraction completed: {audio_path}")

        # Check file size
        file_size = os.path.getsize(audio_path)
        max_size = settings.AUDIO_MAX_SIZE_MB  # 300 MB (Azure limit)
        logger.info(f"Audio file size: {file_size / (1024 * 1024):.2f} MB")

        # If file is too large, compress it
        if file_size > max_size:
            logger.warning(
                f"Audio file exceeds 300MB limit ({file_size / (1024 * 1024):.2f} MB). Compressing..."
            )

            # Create compressed filename
            compressed_filename = f"{job_id}_audio_compressed.wav"
            compressed_path = os.path.join(
                settings.AUDIO_UPLOAD_DIR, compressed_filename
            )

            # Compression options - stronger compression
            compress_command = [
                "ffmpeg",
                "-i",
                audio_path,  # Input file
                "-ar",
                "16000",  # Lower sample rate
                "-ac",
                "1",  # Mono
                "-acodec",
                "pcm_s16le",  # PCM format
                "-y",  # Overwrite output if exists
                compressed_path,
            ]

            # Try first level of compression
            subprocess.run(compress_command, check=True, capture_output=True, text=True)
            compressed_size = os.path.getsize(compressed_path)

            logger.info(
                f"Compressed audio file size: {compressed_size / (1024 * 1024):.2f} MB"
            )

            # If still too large, try more aggressive compression
            if compressed_size > max_size:
                logger.warning(
                    "First compression not sufficient, trying MP3 compression..."
                )
                mp3_filename = f"{job_id}_audio_compressed.mp3"
                mp3_path = os.path.join(settings.AUDIO_UPLOAD_DIR, mp3_filename)

                mp3_command = [
                    "ffmpeg",
                    "-i",
                    audio_path,  # Input file
                    "-ar",
                    "8000",  # Low sample rate
                    "-ac",
                    "1",  # Mono
                    "-codec:a",
                    "libmp3lame",  # MP3 codec
                    "-b:a",
                    "32k",  # Very low bitrate
                    "-y",  # Overwrite output if exists
                    mp3_path,
                ]

                # Run MP3 compression
                subprocess.run(mp3_command, check=True, capture_output=True, text=True)
                mp3_size = os.path.getsize(mp3_path)

                logger.info(
                    f"MP3 compressed audio file size: {mp3_size / (1024 * 1024):.2f} MB"
                )

                # Convert back to WAV for compatibility
                if mp3_size < max_size:
                    final_command = [
                        "ffmpeg",
                        "-i",
                        mp3_path,  # Input file
                        "-acodec",
                        "pcm_s16le",  # PCM format
                        "-y",  # Overwrite output if exists
                        compressed_path,
                    ]

                    subprocess.run(
                        final_command, check=True, capture_output=True, text=True
                    )

                    # Clean up mp3 temporary file
                    os.remove(mp3_path)
                    # Use the compressed file
                    audio_path = compressed_path
                else:
                    # If still too large, we have to truncate the audio
                    logger.warning(
                        "File still too large after compression. Truncating audio..."
                    )

                    # Calculate duration to keep under limit (rough estimate)
                    # Target size: 290MB to stay under 300MB limit with some margin
                    target_size = 290 * 1024 * 1024
                    ratio = target_size / file_size

                    # Get duration of original file
                    duration_command = [
                        "ffprobe",
                        "-i",
                        audio_path,
                        "-show_entries",
                        "format=duration",
                        "-v",
                        "quiet",
                        "-of",
                        "csv=p=0",
                    ]

                    result = subprocess.run(
                        duration_command, check=True, capture_output=True, text=True
                    )
                    duration = float(result.stdout.strip())

                    # Calculate new duration
                    new_duration = duration * ratio
                    logger.info(
                        f"Truncating {duration} seconds to {new_duration} seconds"
                    )

                    truncate_command = [
                        "ffmpeg",
                        "-i",
                        audio_path,
                        "-t",
                        str(new_duration),  # Limit duration
                        "-acodec",
                        "pcm_s16le",
                        "-y",
                        compressed_path,
                    ]

                    subprocess.run(
                        truncate_command, check=True, capture_output=True, text=True
                    )

                    # Use the truncated file
                    audio_path = compressed_path
            else:
                # First compression was sufficient
                audio_path = compressed_path

        return audio_path

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        raise Exception(f"Failed to extract/compress audio: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise Exception(f"Failed to process audio: {str(e)}")
