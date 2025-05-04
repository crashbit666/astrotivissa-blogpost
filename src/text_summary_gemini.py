import os
import requests

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def summarize_text_gemini(text):
    """
    Fa un resum detallat del text utilitzant Gemini, en castellà, en primera persona i pensant en SEO per a una entrada de blog.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY no està definida a les variables d'entorn.")

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Resume el siguiente texto en español, en primera persona, pensando en SEO y como si fuera una entrada de blog. "
                            "El resumen debe ser muy detallado y cubrir todos los aspectos importantes del texto original: " + text
                        )
                    }
                ]
            }
        ]
    }
    params = {"key": GEMINI_API_KEY}
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    response.raise_for_status()
    result = response.json()
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Resposta inesperada de Gemini: {result}")

"""
Mòdul per resumir textos utilitzant Gemini.
""" 