// persistence/mod.rs
// Lògica relacionada amb la persistència local: lectura/escriptura de fitxers JSON, etc. 

use serde::{Deserialize, Serialize};
use std::fs;
use std::io::{self, Write};

#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessedVideo {
    pub video_id: String,
    pub title: String,
    pub processed_at: String,
    pub status: String,
}

/// Llegeix la llista de vídeos processats des d'un fitxer JSON
pub fn load_processed_videos(path: &str) -> io::Result<Vec<ProcessedVideo>> {
    let data = fs::read_to_string(path)?;
    let videos: Vec<ProcessedVideo> = serde_json::from_str(&data)?;
    Ok(videos)
}

/// Desa la llista de vídeos processats a un fitxer JSON
pub fn save_processed_videos(path: &str, videos: &[ProcessedVideo]) -> io::Result<()> {
    let data = serde_json::to_string_pretty(videos)?;
    let mut file = fs::File::create(path)?;
    file.write_all(data.as_bytes())?;
    Ok(())
}

/// Afegeix un vídeo processat i desa la llista
pub fn add_processed_video(path: &str, video: ProcessedVideo) -> io::Result<()> {
    let mut videos = load_processed_videos(path).unwrap_or_default();
    videos.push(video);
    save_processed_videos(path, &videos)
} 