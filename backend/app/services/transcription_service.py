import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


def ms_to_time_format(milliseconds: int) -> str:
    """
    Convert milliseconds to a readable time format (HH:MM:SS or MM:SS).
    """
    # Calculate total seconds
    total_seconds = milliseconds / 1000

    # Extract hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Format the time string
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def create_conversation_transcript(
    transcription_json: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Creates a transcript of a multi-turn conversation, preserving the turn-taking structure.
    """
    if "phrases" not in transcription_json:
        logger.error("No phrases found in the transcription JSON")
        return []

    conversation = []
    current_speaker = None
    current_turn = None

    # Sort phrases by their timestamp to ensure chronological order
    phrases = sorted(
        transcription_json["phrases"], key=lambda x: x["offsetMilliseconds"]
    )

    for phrase in phrases:
        if "speaker" not in phrase:
            continue

        speaker_id = phrase["speaker"]
        start_time_ms = phrase["offsetMilliseconds"]
        end_time_ms = start_time_ms + phrase["durationMilliseconds"]

        # If this is a new speaker or the first phrase
        if speaker_id != current_speaker:
            # Save the previous turn if it exists
            if current_turn is not None:
                # Join the text into a single string
                current_turn["text"] = " ".join(current_turn["text"])
                conversation.append(current_turn)

            # Start a new turn
            current_turn = {
                "speaker_id": speaker_id,
                "start_time_ms": start_time_ms,
                "end_time_ms": end_time_ms,
                "start_time": ms_to_time_format(start_time_ms),
                "end_time": ms_to_time_format(end_time_ms),
                "text": [phrase["text"]],
                "confidence": phrase.get("confidence", 0),
            }
            current_speaker = speaker_id
        else:
            # Continue the current turn
            current_turn["text"].append(phrase["text"])
            current_turn["end_time_ms"] = end_time_ms
            current_turn["end_time"] = ms_to_time_format(end_time_ms)

            # Update confidence (use average)
            if "confidence" in phrase:
                current_turn["confidence"] = (
                    current_turn["confidence"] + phrase["confidence"]
                ) / 2

    # Add the last turn
    if current_turn is not None:
        # Join the text into a single string
        current_turn["text"] = " ".join(current_turn["text"])
        conversation.append(current_turn)

    return conversation


def format_transcript_as_string(transcript: List[Dict[str, Any]]) -> str:
    """
    Format the conversation transcript as a human-readable string.
    """
    formatted_transcript = []

    for turn in transcript:
        speaker_id = turn["speaker_id"]
        text = turn["text"]
        formatted_line = f'speaker {speaker_id}: "{text}"'
        formatted_transcript.append(formatted_line)

    # Join all lines with newlines
    return "\n".join(formatted_transcript)


def process_transcript_file(transcription_result: Dict, output_file: str) -> str:
    """
    Process a transcription file and create a formatted conversation transcript.
    """
    # Create the conversation transcript
    transcript = create_conversation_transcript(transcription_result)

    # Create the string transcript
    transcript_string = format_transcript_as_string(transcript)

    # Save the transcript to a file
    with open(output_file, "w") as json_file:
        json.dump(transcript, json_file, indent=4)

    logger.info(f"Conversation transcript saved to {output_file}")
    return transcript_string


def transcribe_audio_with_diarization(audio_file_path: str, job_id: str) -> str:
    """
    Transcribe an audio file with speaker diarization using Azure Speech Service.
    """
    # Create output file path
    output_file = os.path.join(settings.RESULTS_DIR, f"{job_id}_transcript.json")

    # Get settings from config
    service_region = settings.AZURE_SERVICE_REGION
    subscription_key = settings.AZURE_SUBSCRIPTION_KEY

    # Default parameters
    locales = ["en-US", "th-TH"]
    max_speakers = 2
    api_version = "2024-11-15"

    # API endpoint URL
    url = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version={api_version}"

    # Request headers
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}

    # JSON definition for transcription parameters as a string
    definition_str = json.dumps(
        {
            "locales": locales,
            "diarization": {"maxSpeakers": max_speakers, "enabled": True},
        }
    )

    try:
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Prepare the multipart form data
            files = {"audio": audio_file, "definition": (None, definition_str)}

            # Make the POST request
            logger.info(
                f"Sending request to Azure Speech Service to transcribe {audio_file_path}..."
            )
            response = requests.post(url, headers=headers, files=files)

        # Check the response
        if response.status_code == 200:
            logger.info("Transcription successful")
            transcription_result = response.json()

            # Process the transcript and save to file
            transcript_string = process_transcript_file(
                transcription_result, output_file
            )
            return transcript_string
        else:
            error_msg = f"Transcription error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise Exception(f"Failed to transcribe audio: {str(e)}")
