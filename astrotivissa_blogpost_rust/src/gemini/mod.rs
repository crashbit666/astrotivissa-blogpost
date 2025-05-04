// gemini/mod.rs
// Lògica relacionada amb la API de Gemini: resum de textos, etc. 
use serde_json::json;

/// Fa un resum detallat del text utilizando Gemini
pub async fn summarize_text_gemini(api_key: &str, text: &str) -> Result<String, reqwest::Error> {
    let url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";
    let client = reqwest::Client::new();
    let body = json!({
        "contents": [{
            "role": "user",
            "parts": [{
                "text": format!(
                    "Resume el siguiente texto en español, en primera persona, pensando en SEO y como si fuera una entrada de blog. El resumen debe ser muy detallado y cubrir todos los aspectos importantes del texto original: {}",
                    text
                )
            }]
        }]
    });
    let resp = client
        .post(url)
        .query(&[("key", api_key)])
        .json(&body)
        .send()
        .await?;
    let json: serde_json::Value = resp.json().await?;
    Ok(json["candidates"][0]["content"]["parts"][0]["text"]
        .as_str()
        .unwrap_or("")
        .to_string())
} 