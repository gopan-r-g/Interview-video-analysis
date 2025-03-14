import os
import shutil
from fastapi import UploadFile
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def save_uploaded_file(
    file: UploadFile, destination_folder: Path, filename: Optional[str] = None
) -> str:
    """
    Save an uploaded file to the destination folder.

    Parameters:
    -----------
    file : UploadFile
        The uploaded file
    destination_folder : Path
        The folder to save the file to
    filename : Optional[str]
        Optional custom filename, if None the original filename is used

    Returns:
    --------
    str
        The full path to the saved file
    """
    # Make sure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Determine the filename
    if filename:
        dest_filename = filename
    else:
        dest_filename = file.filename

    # Full path to destination
    file_path = os.path.join(destination_folder, dest_filename)

    try:
        # Create a buffer to store the file
        with open(file_path, "wb") as buffer:
            # Copy the uploaded file to the buffer
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File saved successfully: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise Exception(f"Failed to save uploaded file: {str(e)}")

    finally:
        # Always close the file to prevent resource leaks
        file.file.close()


def is_video_file(filename: str) -> bool:
    """
    Check if a file is a video file based on extension.

    Parameters:
    -----------
    filename : str
        The filename to check

    Returns:
    --------
    bool
        True if the file has a video extension, False otherwise
    """
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
    _, ext = os.path.splitext(filename.lower())
    return ext in video_extensions
