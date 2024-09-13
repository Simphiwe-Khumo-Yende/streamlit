import json
import os
from datetime import timedelta
from streamlit.logger import get_logger
import requests



# Initialize the logger
logger = get_logger(__name__)

def format_timestamp(seconds):
    """Formats timestamp into HH:MM:SS without milliseconds."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def process_transcripts(json_file_content, output_file_path):
    # Ensure the directory for the output file exists
    output_dir = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger.info("Starting transcript processing...")

    # Check if the JSON content is valid
    try:
        data = json.loads(json_file_content)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON content: {e}")
        return "Error decoding JSON content"

    formatted_texts = []

    for title, details in data.items():
        link = details.get('link', 'No link available')
        transcript = details.get('transcript', None)

        if transcript == "Transcript not available":
            formatted_texts.append(f"Title: {title}")
            formatted_texts.append(f"Link: {link}")
            formatted_texts.append("\nTranscript not available.\n")
            logger.info(f"Processed {title} - Transcript not available.")
            continue

        if not isinstance(transcript, list):
            formatted_texts.append(f"Title: {title}")
            formatted_texts.append(f"Link: {link}")
            formatted_texts.append("\nTranscript not available.\n")
            logger.info(f"Processed {title} - Transcript not available.")
            logger.error(f"Transcript for {title} is not in expected list format.")
            continue
        
        formatted_texts.append(f"Title: {title}")
        formatted_texts.append(f"Link: {link}\n")
        
        last_time = 0
        current_text = []

        for entry in transcript:
            if not isinstance(entry, dict) or 'start' not in entry or 'text' not in entry:
                formatted_texts.append(f"Unexpected entry format: {entry}")
                logger.error(f"Unexpected entry format for {title}: {entry}")
                continue

            start = entry.get('start', 0)
            text = entry.get('text', '')

            start_time = format_timestamp(start)
            
            if start > last_time + 60:
                if current_text:
                    formatted_texts.append(f"(Start: {format_timestamp(last_time)})")
                    formatted_texts.append(" ".join(current_text))
                    formatted_texts.append("")
                current_text = []
                last_time = start
            
            current_text.append(text)
        
        if current_text:
            formatted_texts.append(f"(Start: {format_timestamp(last_time)})")
            formatted_texts.append(" ".join(current_text))
            formatted_texts.append("")

        logger.info(f"Processed transcript for {title}.")

    # Write to file with error handling
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write("\n".join(formatted_texts))
            file.flush()  # Ensure all data is written to disk
        logger.info(f"Formatted text has been written to {output_file_path}")

        # Debug: Verify file content
        with open(output_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Content of the file:\n{content}")

    except IOError as e:
        logger.error(f"Error writing to output file: {e}")
        return "Error writing to output file"

    return "Processing complete"
