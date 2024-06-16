import requests
import json
import os
from config.settings import YOUTUBE_API_KEY, CHANNEL_ID


def fetch_latest_videos(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=5&order=date&type=video&key={api_key}"
    response = requests.get(url)
    videos = response.json().get('items', [])
    return videos


def fetch_all_videos(channel_id, api_key):
    videos = []
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=50&order=date&type=video&key={api_key}"
    next_page_token = ""

    while True:
        response = requests.get(f"{url}&pageToken={next_page_token}")
        result = response.json()
        videos.extend(result.get('items', []))

        next_page_token = result.get('nextPageToken')
        if not next_page_token:
            break

    # Reverse the list of videos to get the latest videos first
    videos.reverse()

    return videos


def fetch_video_tags(video_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    response = requests.get(url)
    video_info = response.json().get('items', [])
    if video_info:
        return video_info[0]['snippet'].get('tags', [])
    return []


def is_review_video(video):
    if 'id' in video and 'videoId' in video['id']:
        video_id = video['id']['videoId']
        tags = fetch_video_tags(video_id, YOUTUBE_API_KEY)
        return 'review' in tags
    return False


def load_processed_videos(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []


def save_processed_videos(filepath, videos):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath, 'w') as file:
        json.dump(videos, file)


def get_unprocessed_videos(latest_videos, processed_videos):
    return [video for video in latest_videos if 'videoId' in video['id'] and video['id']['videoId'] not in processed_videos]


def watch_new_videos():
    processed_videos_path = os.path.join('data', 'processed_videos.json')
    processed_videos = load_processed_videos(processed_videos_path)
    all_videos = fetch_all_videos(CHANNEL_ID, YOUTUBE_API_KEY)  # Call the fetch_all_videos function

    new_review_videos = [video for video in get_unprocessed_videos(all_videos, processed_videos) if is_review_video(video)]

    for video in new_review_videos:
        video_id = video['id']['videoId']
        try:
            print(f"Processing new video: {video['snippet']['title']} (ID: {video_id})")
            thumbnail_url = video['snippet']['thumbnails']['high']['url']
            process_new_video(video_id, video['snippet']['title'], thumbnail_url)
            processed_videos.append(video_id)
            save_processed_videos(processed_videos_path, processed_videos)
        except Exception as e:
            print(f"Error processing video {video_id}: {e}")


def process_new_video(video_id, blog_title, thumbnail_url):
    from src.youtube_transcript import get_video_transcript
    from src.text_summary import summarize_text
    from src.blog_post import create_blog_post

    # Obtain video transcript
    transcript = get_video_transcript(video_id)
    if transcript == "No transcript available":
        print(f"Transcript not available for video {video_id}. Skipping.")
        return

    print(f"Transcript for video {video_id}: {transcript[:100]}...")  # Print the first 100 characters of the transcript

    # Generate a summary of the video content
    summary = summarize_text(transcript)
    print(f"Summary for video {video_id}: {summary}")

    # Not used, only for testing purposes
    # content_with_image = f'[et_pb_image text_orientation="center" src="{thumbnail_url}" _builder_version="4.9.10"][/et_pb_image]\n\n<div style="color: #ffffff;">{summary}</div>'

    # Create a new blog post with review category
    category_id = 283  # Review category ID
    video_url = f"https://www.youtube.com/watch?v={video_id}"  # Create the video URL
    post_response = create_blog_post(blog_title, thumbnail_url, video_url, summary, category_id)
    print(f"Blog post created for video {video_id}: {post_response}")

    return post_response


if __name__ == "__main__":
    watch_new_videos()
