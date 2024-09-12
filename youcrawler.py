import streamlit as st
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NotTranslatable, TranscriptsDisabled, VideoUnavailable, InvalidVideoId,
    NoTranscriptAvailable, NoTranscriptFound, TooManyRequests
)
import json
import tempfile
import re
import time
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

# Function to fetch transcripts with retry logic
def get_transcripts(video_ids):
    transcripts = {}
    total_videos = len(video_ids)
    with st.spinner("Fetching transcripts..."):
        progress_bar = st.progress(0)
        for idx, video_id in enumerate(video_ids):
            attempt = 0
            while attempt < 3:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    transcripts[video_id] = transcript
                    break
                except TooManyRequests as e:
                    attempt += 1
                    wait_time = 2 ** attempt
                    st.warning(f"Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except (VideoUnavailable, TranscriptsDisabled, NotTranslatable, InvalidVideoId,
                        NoTranscriptAvailable, NoTranscriptFound) as e:
                    transcripts[video_id] = f"Error: {e}"
                    break
                except Exception as e:
                    transcripts[video_id] = f"Unexpected Error: {e}"
                    break

            progress = (idx + 1) / total_videos
            progress_bar.progress(progress)

    return transcripts

# Function to extract video IDs from URLs
def extract_video_ids_from_urls(urls):
    video_ids = []
    for url in urls:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            video_ids.append(match.group(1))
    return video_ids

# Streamlit interface
def main():
    st.title("YouCrawler")

    option = st.selectbox("Choose Input Method", ["YouTube Channel Username", "Custom Video URLs"])

    video_links = {}

    if option == "YouTube Channel Username":
        username = st.text_input("YouTube Channel Username")
        content_type = st.selectbox("Content Type", ["videos", "streams"])

        if st.button("Fetch Data"):
            if username:
                st.write("Fetching video data...")
                videos = scrapetube.get_channel(channel_username=username, content_type=content_type)

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

                transcripts = get_transcripts(video_ids)

                for video_title, video_info in video_links.items():
                    video_id = video_info.get('videoId')
                    if video_id:
                        transcript = transcripts.get(video_id)
                        video_links[video_title]["transcript"] = transcript

    elif option == "Custom Video URLs":
        urls_input = st.text_area("Paste Video URLs (one per line)")
        urls = urls_input.splitlines()

        unique_urls = list(set(urls))

        if st.button("Fetch Transcripts"):
            if unique_urls:
                video_ids = extract_video_ids_from_urls(unique_urls)

                for url, video_id in zip(unique_urls, video_ids):
                    video_link = f"https://www.youtube.com/watch?v={video_id}"
                    video_links[video_link] = {
                        "link": video_link,
                        "videoId": video_id,
                        "transcript": None
                    }

                transcripts = get_transcripts(video_ids)

                for video_link, video_info in video_links.items():
                    video_id = video_info.get('videoId')
                    if video_id:
                        transcript = transcripts.get(video_id)
                        video_links[video_link]["transcript"] = transcript

    if video_links:
        json_content = json.dumps(video_links, ensure_ascii=False, indent=4)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as temp_file:
            output_file_path = temp_file.name
            result = process_transcripts(json_content, output_file_path)

        if result == "Processing complete":
            with open(output_file_path, 'r', encoding='utf-8') as file:
                processed_text = file.read()

            st.download_button(
                label="Download Processed Transcripts",
                data=processed_text,
                file_name='output_transcripts.txt',
                mime='text/plain'
            )
            
            # Delete the temporary file after download
            os.remove(output_file_path)
        else:
            st.error(f"Error in processing: {result}")

if __name__ == "__main__":
    main()
