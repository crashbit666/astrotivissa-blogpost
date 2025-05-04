// models.rs
// Definició d'estructures centrals: Video, ProcessedVideo, etc. 

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Video {
    pub id: String,
    pub title: String,
    pub published_at: String,
    pub thumbnail_url: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProcessedVideo {
    pub video_id: String,
    pub title: String,
    pub processed_at: String,
    pub status: String,
} 