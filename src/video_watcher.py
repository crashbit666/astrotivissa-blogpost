import requests
import json
import os
import logging
from config.settings import YOUTUBE_API_KEY, CHANNEL_ID
import time

# Configuració del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Comprovació de variables crítiques
if not YOUTUBE_API_KEY or not CHANNEL_ID:
    logging.critical("Falten YOUTUBE_API_KEY o CHANNEL_ID a la configuració. Revisa el fitxer .env o config/settings.py.")
    exit(1)

NUM_VIDEOS_TO_PROCESS = int(os.getenv('NUM_VIDEOS_TO_PROCESS', 5))
BLOG_CATEGORY_ID = int(os.getenv('BLOG_CATEGORY_ID', 283))

def request_with_retries(url, max_retries=5):
    retries = 0
    while retries < max_retries:
        response = requests.get(url)
        if response.status_code == 429:
            wait = 2 ** retries
            logging.warning(f"Quota excedida (429). Esperant {wait} segons abans de reintentar...")
            time.sleep(wait)
            retries += 1
        else:
            return response
    logging.error(f"Massa intents fallits per quota a {url}")
    return response

def fetch_latest_videos(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults={NUM_VIDEOS_TO_PROCESS}&order=date&type=video&key={api_key}"
    response = request_with_retries(url)
    if not response.ok:
        logging.error(f"Error a fetch_latest_videos: {response.status_code} - {response.text}")
        return []
    videos = response.json().get('items', [])
    return videos


def fetch_all_videos(channel_id, api_key):
    videos = []
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=50&order=date&type=video&key={api_key}"
    next_page_token = ""

    while True:
        response = request_with_retries(f"{url}&pageToken={next_page_token}")
        if not response.ok:
            logging.error(f"Error a fetch_all_videos: {response.status_code} - {response.text}")
            break
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
    response = request_with_retries(url)
    if not response.ok:
        logging.error(f"Error a fetch_video_tags: {response.status_code} - {response.text}")
        return []
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
                logging.warning(f"No s'ha pogut llegir el fitxer {filepath}, es reinicialitza la llista de vídeos processats.")
                return []
    return []


def save_processed_videos(filepath, videos):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath, 'w') as file:
        json.dump(videos, file, indent=2)


def get_last_processed_date(processed_videos):
    if not processed_videos:
        return None
    # Assumeix que els vídeos estan ordenats per data ascendent
    return processed_videos[-1]["processed_at"]


def get_unprocessed_videos(latest_videos, processed_videos):
    processed_ids = {v["video_id"] for v in processed_videos}
    return [video for video in latest_videos if 'videoId' in video['id'] and video['id']['videoId'] not in processed_ids]


def notify(message, level="info"):
    # Notificació per consola
    if level == "info":
        logging.info(f"NOTIFICACIÓ: {message}")
    elif level == "error":
        logging.error(f"NOTIFICACIÓ: {message}")
    # Aquí pots afegir integració amb email, Telegram, etc.
    # Exemple:
    # if level == "error":
    #     send_telegram_alert(message)


def watch_new_videos():
    processed_videos_path = os.path.join('data', 'processed_videos.json')
    processed_videos = load_processed_videos(processed_videos_path)
    last_processed_date = get_last_processed_date(processed_videos)
    all_videos = fetch_all_videos(CHANNEL_ID, YOUTUBE_API_KEY)

    # Filtra només vídeos posteriors a l'últim processat
    if last_processed_date:
        from dateutil import parser
        last_dt = parser.isoparse(last_processed_date)
        all_videos = [v for v in all_videos if parser.isoparse(v['snippet']['publishedAt']) > last_dt]

    new_review_videos = [video for video in get_unprocessed_videos(all_videos, processed_videos) if is_review_video(video)]

    for video in new_review_videos:
        video_id = video['id']['videoId']
        try:
            logging.info(f"Processant nou vídeo: {video['snippet']['title']} (ID: {video_id})")
            thumbnail_url = video['snippet']['thumbnails']['high']['url']
            result = process_new_video(video_id, video['snippet']['title'], thumbnail_url)
            processed_videos.append({
                "video_id": video_id,
                "title": video['snippet']['title'],
                "processed_at": video['snippet']['publishedAt'],
                "status": "published" if result else "error"
            })
            save_processed_videos(processed_videos_path, processed_videos)
            if result:
                notify(f"Publicada nova entrada per vídeo: {video['snippet']['title']}")
        except Exception as e:
            logging.error(f"Error processant el vídeo {video_id}: {e}")
            notify(f"Error greu processant el vídeo {video_id}: {e}", level="error")


def process_new_video(video_id, blog_title, thumbnail_url):
    from src.youtube_transcript import get_video_transcript
    from src.text_summary_gemini import summarize_text_gemini
    from src.blog_post import create_blog_post

    # Obtain video transcript
    transcript = get_video_transcript(video_id)
    if transcript == "No transcript available":
        logging.warning(f"Transcript no disponible pel vídeo {video_id}. Es salta.")
        return

    logging.info(f"Transcript pel vídeo {video_id}: {transcript[:100]}...")  # Print the first 100 characters of the transcript

    # Generate a summary of the video content
    summary = summarize_text_gemini(transcript)
    logging.info(f"Resum pel vídeo {video_id}: {summary}")

    # Afegeix secció 'Veure també' amb altres vídeos
    altres_videos = [v for v in fetch_latest_videos(CHANNEL_ID, YOUTUBE_API_KEY) if v['id']['videoId'] != video_id][:3]
    veure_tambe = "\n\n<b>Veure també:</b><ul>" + "".join([
        f'<li><a href="https://www.youtube.com/watch?v={v["id"]["videoId"]}">{v["snippet"]["title"]}</a></li>' for v in altres_videos
    ]) + "</ul>"
    summary += veure_tambe

    # Create a new blog post with review category
    video_url = f"https://www.youtube.com/watch?v={video_id}"  # Create the video URL
    try:
        post_response = create_blog_post(blog_title, thumbnail_url, video_url, summary, BLOG_CATEGORY_ID)
        logging.info(f"Entrada de blog creada pel vídeo {video_id}: {post_response}")
        return post_response
    except Exception as e:
        logging.error(f"Error creant l'entrada de blog pel vídeo {video_id}: {e}")
        return None


if __name__ == "__main__":
    watch_new_videos()

    # Test manual: comprova que fetch_latest_videos retorna vídeos
    print("Test: fetch_latest_videos")
    videos = fetch_latest_videos(CHANNEL_ID, YOUTUBE_API_KEY)
    print(f"S'han trobat {len(videos)} vídeos.")
    if videos:
        print(f"Primer vídeo: {videos[0]['snippet']['title']}")

    if __name__ == "__test__":
        def test_get_unprocessed_videos():
            latest = [
                {"id": {"videoId": "1"}},
                {"id": {"videoId": "2"}},
                {"id": {"videoId": "3"}},
            ]
            processed = [
                {"video_id": "1", "title": "A", "processed_at": "2024-01-01T00:00:00", "status": "published"}
            ]
            result = get_unprocessed_videos(latest, processed)
            assert len(result) == 2
            assert result[0]["id"]["videoId"] == "2"
            assert result[1]["id"]["videoId"] == "3"
        test_get_unprocessed_videos()
        print("Test get_unprocessed_videos passat!")
