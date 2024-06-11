import openai
from config.settings import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def summarize_text(text):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente útil que proporciona resúmenes detallados en español."},
            {"role": "user", "content": f"Por favor, resume el siguiente texto en español y en primera persona y sobretodo teniendo en cuenta que será una entrada de un blog y lo que mas me interesa es el SEO. El resumen debe ser muy detallado y cubrir todos los aspectos importantes mencionados en el texto original: {text}"}
        ],
        max_tokens=4000
    )
    summary = response.choices[0].message.content.strip()
    return summary




