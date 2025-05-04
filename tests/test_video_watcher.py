import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from video_watcher import get_unprocessed_videos

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