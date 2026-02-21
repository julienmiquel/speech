# Media Utils

Collection d'utilitaires pour le traitement de fichiers audio et vidéo.

## Fonctionnalités

*   **Conversion Audio vers Vidéo** : Transforme un fichier audio (MP3) en fichier vidéo (MP4) avec un fond statique (par exemple blanc). Utile pour télécharger des audios sur des plateformes vidéo ou pour utiliser des API nécessitant un flux vidéo.
*   **Conversion MP3 vers WAV** : Convertit des fichiers MP3 en format WAV (16kHz ou mono) pour le traitement par des modèles ASR (Speech-to-Text).

## Contenu

*   `audio-to-video.ipynb` : Notebook Jupyter contenant les scripts de conversion utilisant `moviepy` et `pydub`.

## Pré-requis

*   Python 3
*   Bibliothèques : `moviepy`, `pydub`, `ffmpeg`

## Installation

```bash
pip install moviepy pydub ffmpeg-python
```

(Nécessite également l'installation de FFmpeg sur le système).
