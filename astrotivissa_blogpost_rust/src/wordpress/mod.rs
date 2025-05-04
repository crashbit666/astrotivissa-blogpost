// wordpress/mod.rs
// Lògica relacionada amb la API de WordPress: autenticació, publicació, etc. 
use serde_json::json;
use anyhow::{Result, anyhow};

/// Obté un token JWT per autenticar-se a WordPress
pub async fn get_jwt_token(api_url: &str, username: &str, password: &str) -> Result<String> {
    let token_url = api_url.replace("/wp/v2/posts", "/jwt-auth/v1/token");
    let client = reqwest::Client::new();
    let body = json!({
        "username": username,
        "password": password
    });
    let resp = client
        .post(&token_url)
        .json(&body)
        .send()
        .await?;
    let json: serde_json::Value = resp.json().await?;
    Ok(json["token"].as_str().unwrap_or("").to_string())
}

/// Publica una nova entrada al blog de WordPress
pub async fn create_blog_post(
    api_url: &str,
    jwt_token: &str,
    title: &str,
    content: &str,
    category_id: u32,
) -> Result<()> {
    let client = reqwest::Client::new();
    let divi_content = format!(
        "[et_pb_section bb_built=\"1\" _builder_version=\"4.9.10\" background_color=\"transparent\"]\
            [et_pb_row]\
                [et_pb_column type=\"4_4\"]\
                    [et_pb_text _builder_version=\"4.9.10\" text_orientation=\"center\" text_text_color=\"#ffffff\"]\
                        <h1 style=\"color: #ffffff;\">{}</h1>\
                    [/et_pb_text]\
                    [et_pb_text _builder_version=\"4.9.10\" text_text_color=\"#ffffff\"]\
                        {}\
                    [/et_pb_text]\
                [/et_pb_column]\
            [/et_pb_row]\
        [/et_pb_section]",
        title, content
    );
    let body = json!({
        "title": title,
        "content": divi_content,
        "categories": [category_id],
        "status": "publish"
    });
    let resp = client
        .post(api_url)
        .bearer_auth(jwt_token)
        .json(&body)
        .send()
        .await?;
    if resp.status().is_success() {
        Ok(())
    } else {
        Err(anyhow!("Error publicant a WordPress: {}", resp.text().await.unwrap_or_default()))
    }
} 