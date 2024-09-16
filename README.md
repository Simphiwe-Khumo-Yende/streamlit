# YouCrawler

YouCrawler is a web-based tool that allows users to scrape video transcripts from specific YouTube channels or custom video URLs. The app is built using Streamlit and utilizes YouTube's API for fetching video transcripts. Users can input a YouTube channel username or provide custom video URLs, and the tool retrieves and processes the transcripts.

## Features

- Fetch video transcripts from a YouTube channel (by username) or custom video URLs.
- Retry mechanism for handling rate limits and errors during transcript fetching.
- Bulk transcript extraction for entire channels or multiple videos.
- Auto-cleanup for temporary files used in transcript processing.
- Download processed transcripts directly from the web interface.
  
## Tech Stack

- **Frontend**: Streamlit for the user interface.
- **Backend**: Python for scraping and processing transcripts.
- **APIs**: YouTube Transcript API, ScrapeTube for fetching video data.
- **File Handling**: Temporary file generation with auto-deletion to optimize resource usage.

## Prerequisites

- Python 3.x
- Streamlit
- YouTube Transcript API
- ScrapeTube
- Requests

Install dependencies using `pip`:

```bash
pip install streamlit scrapetube youtube-transcript-api
```

## Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:Simphiwe-Khumo-Yende/streamlit.git
   cd streamlit
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app locally:
   ```bash
   streamlit run youcrawler.py
   ```

## Usage

### Fetching Transcripts by YouTube Channel

- Enter the YouTube channel username in the input box.
- Select the type of content (videos/streams).
- Click the "Fetch Data" button to start scraping transcripts for the channel’s videos.

### Fetching Transcripts by Custom Video URLs

- Paste one or more YouTube video URLs into the text area.
- Click the "Fetch Transcripts" button to retrieve and process transcripts.

### Download Processed Transcripts

Once the transcripts are processed, a download button will be available to download the results as a plain text file.

## Error Handling

- The app includes retry logic for rate limits and common transcript-fetching errors (e.g., video unavailable, no transcript available, etc.).
- Any failed video URLs are displayed in a separate section for review.

## Logging

YouCrawler uses Streamlit's built-in logger for tracking important events such as temporary file creation, transcript fetching issues, and process completion.

## License

This project is licensed under the MIT License.

## Repository

- [GitHub Repository](git@github.com:Simphiwe-Khumo-Yende/streamlit.git)
