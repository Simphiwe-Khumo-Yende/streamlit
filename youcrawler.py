import streamlit as st
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NotTranslatable, TranscriptsDisabled, VideoUnavailable, InvalidVideoId,
    NoTranscriptAvailable, NoTranscriptFound, TooManyRequests
)
import os

# Function to extract title
def extract_title(video_info):
    try:
        title_parts = video_info.get('title', {}).get('runs', [{}])
        title = title_parts[0].get('text', 'No title available')
        return title
    except (AttributeError, IndexError, KeyError):
        return 'No title available'

# Function to fetch transcripts
def get_transcripts(video_ids):
    transcripts = {}
    total_videos = len(video_ids)
    with st.spinner("Fetching transcripts..."):
        # Initialize progress bar
        progress_bar = st.progress(0)
        
        for idx, video_id in enumerate(video_ids):
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcripts[video_id] = transcript
            except (VideoUnavailable, TranscriptsDisabled, NotTranslatable, InvalidVideoId,
                    NoTranscriptAvailable, NoTranscriptFound, TooManyRequests) as e:
                transcripts[video_id] = f"Error: {e}"
            except Exception as e:
                transcripts[video_id] = f"Unexpected Error: {e}"
            
            # Update progress bar
            progress = (idx + 1) / total_videos
            progress_bar.progress(progress)

    return transcripts

# Function to process transcripts and generate a file
def process_transcripts(video_links, file_path):
    formatted_texts = []
    
    for title, details in video_links.items():
        link = details.get('link', 'No link available')
        transcript = details.get('transcript', None)
        
        if transcript == "Transcript not available":
            formatted_texts.append(f"Title: {title}")
            formatted_texts.append(f"Link: {link}")
            formatted_texts.append("\nTranscript not available.\n")
            continue

        if isinstance(transcript, str):
            continue
        
        formatted_texts.append(f"Title: {title}")
        formatted_texts.append(f"Link: {link}\n")
        
        last_time = 0
        current_text = []

        for entry in transcript:
            if not isinstance(entry, dict) or 'start' not in entry or 'text' not in entry:
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

    # Write the formatted text to the specified file path
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(formatted_texts))

# Function to format timestamp
def format_timestamp(seconds):
    """Formats timestamp into HH:MM:SS without milliseconds."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Streamlit interface
def main():
    st.title("YouCrawler")

    # Input for user
    username = st.text_input("YouTube Channel Username")
    content_type = st.selectbox("Content Type", ["videos", "streams"])
    
    if st.button("Fetch Data"):
        if username:
            st.write("Fetching video data...")
            videos = scrapetube.get_channel(channel_username=username, content_type=content_type)

            video_links = {}
            video_ids = []

            for video in videos:
                video_id = video.get('videoId')
                video_title = extract_title(video)
                video_link = f"https://www.youtube.com/watch?v={video_id}"

                video_links[video_title] = {
                    "link": video_link,
                    "videoId": video_id,
                    "transcript": None
                }
                video_ids.append(video_id)

            # Fetch transcripts and show progress
            transcripts = get_transcripts(video_ids)

            # Update video_links with transcripts
            for video_title, video_info in video_links.items():
                video_id = video_info.get('videoId')
                if video_id:
                    transcript = transcripts.get(video_id)
                    video_links[video_title]["transcript"] = transcript

            # Define the path for the formatted text file
            file_path = 'output_transcripts.txt'
            
            # Process transcripts and generate the file
            process_transcripts(video_links, file_path)
            
            # Provide download link for the processed file
            with open(file_path, 'r', encoding='utf-8') as file:
                processed_text = file.read()
                
            st.download_button(
                label="Download Processed Transcripts",
                data=processed_text,
                file_name='output_transcripts.txt',
                mime='text/plain'
            )

if __name__ == "__main__":
    main()
