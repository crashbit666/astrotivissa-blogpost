from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound


def get_video_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([t['text'] for t in transcript_list])
        return transcript
    except NoTranscriptFound:
        return "No transcript available"
    except Exception as e:
        print(f"An error occurred while fetching the transcript for video {video_id}: {e}")
        return "No transcript available"


if __name__ == "__main__":
    print("Testing get_video_transcript function:")


"""
Mòdul per obtenir la transcripció d'un vídeo de YouTube.
"""
