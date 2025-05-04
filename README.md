# YouTube Transcript Fetcher

Este es un proyecto conjunto entre Crashbit y Astrotivissa. El objetivo principal de este proyecto es obtener y procesar transcripciones de vídeos de YouTube.

## Descripción

El proyecto está escrito en Python y utiliza la API de YouTube Transcript para obtener las transcripciones de los vídeos de YouTube. El programa toma una lista de identificadores de vídeos de YouTube de un archivo JSON (`processed_videos.json`) y obtiene las transcripciones correspondientes.

## Funcionalidades

1. **Obtener transcripciones**: La función `get_video_transcript` en `src/youtube_transcript.py` toma un `video_id` como entrada y obtiene la transcripción del vídeo correspondiente.

2. **Ver nuevos vídeos**: La función `watch_new_videos` en `src/video_watcher.py` se encarga de procesar nuevos vídeos.

## Cómo usar

Para usar este proyecto, necesitarás tener Python y pip instalados en tu sistema. Una vez que los tengas, puedes clonar este repositorio y ejecutar `src/main.py`.

## Contribuciones

Este proyecto es un esfuerzo conjunto entre Crashbit y Astrotivissa. Agradecemos cualquier contribución que pueda ayudar a mejorar este proyecto.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.

# Astrotivissa Blogpost Automation

Automatitza la creació d'entrades de blog a WordPress a partir de vídeos nous d'un canal de YouTube. El procés inclou:
- Detecció de vídeos nous (tipus "review").
- Extracció de la transcripció.
- Resum amb Gemini.
- Publicació automàtica a WordPress.

## Configuració

1. **Variables d'entorn** (posa-les a `.env`):
   - `YOUTUBE_API_KEY`
   - `CHANNEL_ID`
   - `GEMINI_API_KEY`
   - `WORDPRESS_API_URL`
   - `WORDPRESS_USERNAME`
   - `WORDPRESS_PASSWORD`

2. **Instal·lació**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Execució**
   ```bash
   python -m src.main
   ```

## Persistència
Els vídeos processats es guarden a `data/processed_videos.json` amb informació detallada (ID, títol, data, estat).

## Docker

### Exemple docker-compose.yml
```yaml
version: '3.8'
services:
  blogpost:
    build: .
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

## Troubleshooting
- **No es processen vídeos nous:** Comprova que les API keys i variables d'entorn són correctes.
- **Quota excedida:** El sistema reintenta automàticament amb espera exponencial.
- **Problemes d'autenticació a WordPress:** Revisa usuari/contrasenya i permisos de l'usuari.

## Extensió
- Modularitat: la lògica de YouTube, Gemini i WordPress està separada per facilitar el manteniment.
- Fàcil d'afegir nous processaments o notificacions.

## Tests
Executa els tests amb:
```bash
pytest tests/
```

## Seguretat
- No posis mai secrets al Dockerfile ni al codi font.
- Utilitza fitxers `.env` i no els comparteixis públicament.