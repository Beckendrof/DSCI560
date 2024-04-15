import re
import os
import cv2
import yt_dlp as youtube_dl
from difflib import SequenceMatcher
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

def save_frame_as_image(frame, output_path):
    cv2.imwrite(output_path, frame)

def extract_frame_from_youtube(video_url, start_time, output_path):
    try:
        start_time = float(start_time) 

        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            for format in formats:
                try:
                    format['filesize'] = int(format.get('filesize', 0))
                except:
                    format['filesize'] = 0
            best_format = max(formats, key=lambda x: x.get('filesize', 0))

        cap = cv2.VideoCapture(best_format['url'])

        if not cap.isOpened():
            print("Error: Could not open the video stream.")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(start_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if ret:
            save_frame_as_image(frame, output_path)
        else:
            print("Error: Could not read frame.")

        cap.release()

    except Exception as e:
        print("Error:", e)


def find_best_timestamp(transcript, query, start, duration, chunk_length=100):
    chunks = [transcript[i:i+chunk_length] for i in range(0, len(transcript), chunk_length)]
    best_score = 0.4
    best_timestamp = None

    total_duration = duration * len(chunks)  # Total duration of the video in seconds

    for index, chunk in enumerate(chunks):
        score = SequenceMatcher(None, query.lower(), chunk.lower()).ratio()
        if score > best_score:
            chunk_start_time = start + (index * chunk_length / len(transcript)) * total_duration
            chunk_midpoint = chunk_start_time + (chunk_length / 2) * total_duration / len(transcript)
            best_timestamp = chunk_midpoint

    return (best_timestamp)

def search_videos(query):
    try:
        ydl_opts = {
            'format': 'best',  # Choose the best quality format
            'quiet': True,     # Suppress console output
            'extract_flat': True,  # Extract only the direct video URL
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                # Search for videos matching the query
                search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in search_results:
                    # Get the link of the first video in the search results
                    first_video_link = search_results['entries'][0]['url']
                    return first_video_link
            except youtube_dl.utils.DownloadError as e:
                print("Error:", e)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        return None

def extract_timestamp(video_id, query):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        best_timestamp = None

        for transcript in transcript_list:
            translated_transcript = transcript.translate('en').fetch()
            
            for segment in translated_transcript:
                text = segment['text']
                start = segment['start']
                duration = segment['duration']
                end = start + duration
                
                if query:
                    best_timestamp = find_best_timestamp(text, query, start, duration)
                    return best_timestamp
        return None
    except:
        print("Subtitles are disabled...")
        return None

def get_frame(query):
    query = query[:300]  

    video = search_videos(query)

    if video:
        video_id = video.split("v=")[1]

        best_timestamp = extract_timestamp(video_id, query)
        if best_timestamp:
            extract_frame_from_youtube(f"https://www.youtube.com/watch?v={video_id}", best_timestamp, f"conversation_images/{query}.jpg")
            return best_timestamp, video_id
        else:
            print("No transcripts available for this video.")
            return None, None
    else:
        print("No videos found for the given query.")
        return None, None
