import streamlit as st
import json
import os
import scrapetube
import utils
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NotTranslatable, TranscriptsDisabled, VideoUnavailable, InvalidVideoId,
    NoTranscriptAvailable, NoTranscriptFound, TooManyRequests
)

# Define base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.getenv('RAW_DATA_DIR', os.path.join(BASE_DIR, 'raw_data'))

def extract_title(video_info):
    """Extracts the title from the nested video info dictionary."""
    try:
        title_parts = video_info.get('title', {}).get('runs', [{}])
        title = title_parts[0].get('text', 'No title available')
        return title
    except (AttributeError, IndexError, KeyError):
        return 'No title available'

def get_transcripts(video_ids):
    transcripts = {}
    for video_id in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcripts[video_id] = transcript
        except (VideoUnavailable, TranscriptsDisabled, NotTranslatable, InvalidVideoId, NoTranscriptAvailable, NoTranscriptFound, TooManyRequests) as e:
            transcripts[video_id] = f"Error: {e}"
        except Exception as e:
            transcripts[video_id] = f"Error: {e}"
    return transcripts

def main():
    st.title("YouTube Video Transcripts Processor")

    # Step 1: Prompt for Username and Content Type
    st.sidebar.header("YouTube Channel Details")
    username = st.sidebar.text_input("YouTube Channel Username")
    content_type = st.sidebar.selectbox("Content Type", ["videos", "shorts"])

    if st.sidebar.button("Fetch Videos"):
        if username:
            with st.spinner("Fetching video data..."):
                try:
                    videos = scrapetube.get_channel(channel_username=username, content_type=content_type)
                except Exception as e:
                    st.error(f"Error fetching video data: {e}")
                    return

                video_links = {}
                video_ids = []

                for video in videos:
                    video_id = video.get('videoId')
                    video_title = extract_title(video)

                    if not isinstance(video_title, str):
                        video_title = 'No title available'

                    video_link = f"https://www.youtube.com/watch?v={video_id}"

                    video_links[video_title] = {
                        "link": video_link,
                        "videoId": video_id,
                        "transcript": None
                    }
                    video_ids.append(video_id)

                with st.spinner("Fetching transcripts..."):
                    transcripts = get_transcripts(video_ids)

                for video_title, video_info in video_links.items():
                    video_id = video_info.get('videoId')
                    if video_id:
                        transcript = transcripts.get(video_id)
                        video_links[video_title]["transcript"] = transcript

                json_file_path = os.path.join(RAW_DATA_DIR, 'video_links_with_transcripts.json')
                try:
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(video_links, json_file, indent=4, ensure_ascii=False)
                    st.success("Data successfully saved. Now you can process the transcripts.")
                except IOError as e:
                    st.error(f"Error writing JSON file: {e}")
                    return

                # Display the data
                st.json(video_links)
                st.session_state.json_file_path = json_file_path
        else:
            st.error("Please enter a valid YouTube channel username.")

    if 'json_file_path' in st.session_state:
        # Step 2: Process Transcripts
        st.header("Process Transcripts")
        if st.button("Process Transcripts"):
            json_file_path = st.session_state.json_file_path
            output_text_file = os.path.join(RAW_DATA_DIR, 'output_transcripts.txt')

            result = utils.process_transcripts(open(json_file_path).read(), output_text_file)

            if result == "Processing complete":
                st.success("Transcripts processed successfully.")
                st.markdown(f"[Download the file](./{output_text_file})")
            else:
                st.error(result)

if __name__ == "__main__":
    main()
