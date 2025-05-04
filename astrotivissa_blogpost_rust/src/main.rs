// mod models;

use dotenv::dotenv;
use std::env;
use log::{info, error};

use astrotivissa_blogpost_rust::youtube::{fetch_all_videos, is_review_video, YoutubeVideo};
use astrotivissa_blogpost_rust::gemini::summarize_text_gemini;
use astrotivissa_blogpost_rust::wordpress::{get_jwt_token, create_blog_post};
use astrotivissa_blogpost_rust::persistence::{add_processed_video, load_processed_videos, ProcessedVideo};

use youtube_transcript::{YoutubeBuilder, TranscriptCore};

async fn get_video_transcript(video_id: &str) -> String {
    let link = format!("https://www.youtube.com/watch?v={}", video_id);
    let youtube_builder = YoutubeBuilder::default();
    let youtube_loader = youtube_builder.build();
    let transcript_result = youtube_loader.transcript(&link).await;
    match transcript_result {
        Ok(transcript) => {
            let transcripts = &transcript.transcripts;
            transcripts
                .iter()
                .map(|t: &TranscriptCore| t.text.clone())
                .collect::<Vec<String>>()
                .join(" ")
        }
        Err(e) => {
            error!("Error obtenint la transcripció: {}", e);
            "No transcript available".to_string()
        }
    }
}

#[tokio::main]
async fn main() {
    dotenv().ok();
    env_logger::init();
    info!("Astrotivissa Blogpost Rust iniciat");

    // Carrega variables d'entorn
    let youtube_api_key = env::var("YOUTUBE_API_KEY").expect("Falta YOUTUBE_API_KEY");
    let channel_id = env::var("CHANNEL_ID").expect("Falta CHANNEL_ID");
    let gemini_api_key = env::var("GEMINI_API_KEY").unwrap_or_default();
    let wordpress_api_url = env::var("WORDPRESS_API_URL").unwrap_or_default();
    let wordpress_username = env::var("WORDPRESS_USERNAME").unwrap_or_default();
    let wordpress_password = env::var("WORDPRESS_PASSWORD").unwrap_or_default();

    // 1. Obtenir tots els vídeos
    let videos: Vec<YoutubeVideo> = fetch_all_videos(&channel_id, &youtube_api_key).await.unwrap_or_default();
    info!("S'han trobat {} vídeos", videos.len());

    // 2. Carregar vídeos processats
    let processed_videos = load_processed_videos("data/processed_videos.json").unwrap_or_default();
    let processed_ids: Vec<String> = processed_videos.iter().map(|v| v.video_id.clone()).collect();

    // 3. Filtrar vídeos de tipus review i no processats
    let mut review_videos = vec![];
    for video in &videos {
        if is_review_video(video, &youtube_api_key).await.unwrap_or(false)
            && !processed_ids.contains(&video.id)
        {
            review_videos.push(video.clone());
        }
    }
    info!("Vídeos de tipus review i no processats: {}", review_videos.len());

    // 4. Per cada vídeo nou:
    for video in review_videos {
        // 4.1. Obtenir transcripció
        let transcript = get_video_transcript(&video.id).await;
        // 4.2. Resumir amb Gemini
        let resum = summarize_text_gemini(&gemini_api_key, &transcript).await.unwrap_or_default();
        // 4.3. Publicar a WordPress
        let jwt = get_jwt_token(&wordpress_api_url, &wordpress_username, &wordpress_password).await.unwrap_or_default();
        let _ = create_blog_post(&wordpress_api_url, &jwt, &video.title, &resum, 283).await;
        // 4.4. Desa com a processat
        let processed = ProcessedVideo {
            video_id: video.id.clone(),
            title: video.title.clone(),
            processed_at: video.published_at.clone(),
            status: "published".to_string(),
        };
        let _ = add_processed_video("data/processed_videos.json", processed);
    }
}
