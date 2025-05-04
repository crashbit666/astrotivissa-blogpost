// youtube/mod.rs
// Lògica relacionada amb la API de YouTube: obtenció de vídeos, tags, etc. 

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct YoutubeVideo {
    pub id: String,
    pub title: String,
    pub published_at: String,
    pub thumbnail_url: String,
}

#[derive(Debug, Deserialize)]
struct YoutubeApiResponse {
    items: Vec<YoutubeApiItem>,
    #[serde(default, rename = "nextPageToken")]
    next_page_token: Option<String>,
}

#[derive(Debug, Deserialize)]
struct YoutubeApiItem {
    id: YoutubeApiId,
    snippet: YoutubeApiSnippet,
}

#[derive(Debug, Deserialize)]
struct YoutubeApiId {
    #[serde(rename = "videoId")]
    video_id: String,
}

#[derive(Debug, Deserialize)]
struct YoutubeApiSnippet {
    title: String,
    #[serde(rename = "publishedAt")]
    published_at: String,
    thumbnails: YoutubeApiThumbnails,
}

#[derive(Debug, Deserialize)]
struct YoutubeApiThumbnails {
    high: YoutubeApiThumbnail,
}

#[derive(Debug, Deserialize)]
struct YoutubeApiThumbnail {
    url: String,
}

#[derive(Debug, Deserialize)]
struct YoutubeVideoDetailsResponse {
    items: Vec<YoutubeVideoDetailsItem>,
}

#[derive(Debug, Deserialize)]
struct YoutubeVideoDetailsItem {
    snippet: YoutubeVideoDetailsSnippet,
}

#[derive(Debug, Deserialize)]
struct YoutubeVideoDetailsSnippet {
    #[serde(default)]
    tags: Vec<String>,
}

/// Obté els últims vídeos d'un canal de YouTube
pub async fn fetch_latest_videos(channel_id: &str, api_key: &str, max_results: u32) -> Result<Vec<YoutubeVideo>, reqwest::Error> {
    let all = fetch_all_videos(channel_id, api_key).await?;
    Ok(all.into_iter().take(max_results as usize).collect())
}

/// Obté tots els vídeos d'un canal de YouTube (paginació)
pub async fn fetch_all_videos(channel_id: &str, api_key: &str) -> Result<Vec<YoutubeVideo>, reqwest::Error> {
    let mut videos = Vec::new();
    let mut page_token = String::new();
    loop {
        let url = format!(
            "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={}&maxResults=50&order=date&type=video&key={}&pageToken={}",
            channel_id, api_key, page_token
        );
        let resp = reqwest::get(&url).await?.json::<YoutubeApiResponse>().await?;
        for item in resp.items {
            videos.push(YoutubeVideo {
                id: item.id.video_id,
                title: item.snippet.title,
                published_at: item.snippet.published_at,
                thumbnail_url: item.snippet.thumbnails.high.url,
            });
        }
        if let Some(token) = resp.next_page_token {
            page_token = token;
        } else {
            break;
        }
    }
    Ok(videos)
}

/// Obté les tags d'un vídeo de YouTube
pub async fn fetch_video_tags(video_id: &str, api_key: &str) -> Result<Vec<String>, reqwest::Error> {
    let url = format!(
        "https://www.googleapis.com/youtube/v3/videos?part=snippet&id={}&key={}",
        video_id, api_key
    );
    let resp = reqwest::get(&url).await?.json::<YoutubeVideoDetailsResponse>().await?;
    if let Some(item) = resp.items.get(0) {
        Ok(item.snippet.tags.clone())
    } else {
        Ok(vec![])
    }
}

/// Comprova si un vídeo és de tipus "review" segons les seves tags
pub async fn is_review_video(video: &YoutubeVideo, api_key: &str) -> Result<bool, reqwest::Error> {
    let tags = fetch_video_tags(&video.id, api_key).await?;
    Ok(tags.iter().any(|tag| tag.to_lowercase() == "review"))
} 