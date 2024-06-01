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