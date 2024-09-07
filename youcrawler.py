import streamlit as st
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NotTranslatable, TranscriptsDisabled, VideoUnavailable, InvalidVideoId,
    NoTranscriptAvailable, NoTranscriptFound, TooManyRequests
)
import json
import os
from utils import process_transcripts

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

            # Save the video links with transcripts to a JSON file
            json_file_path = 'video_links_with_transcripts.json'
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(video_links, json_file, indent=4, ensure_ascii=False)

            # Button to process transcripts
            if st.button("Process Transcripts"):
                output_file_path = 'output_transcripts.txt'
                process_transcripts(json_file_path, output_file_path)
                
                if os.path.exists(output_file_path):
                    # Provide download link for the processed file
                    with open(output_file_path, 'r', encoding='utf-8') as file:
                        processed_text = file.read()
                    st.download_button(
                        label="Download",
                        data=processed_text,
                        file_name='output_transcripts.txt',
                        mime='text/plain'
                    )
                else:
                    st.error("Failed to process transcripts.")

if __name__ == "__main__":
    main()
