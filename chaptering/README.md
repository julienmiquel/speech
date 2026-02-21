# Audio Chaptering

Expérimentation pour la génération automatique de chapitres à partir de transcriptions audio.

## Objectif

Utiliser les capacités de compréhension contextuelle des modèles Gemini pour segmenter une transcription audio longue (podcast, interview, réunion) en chapitres logiques, chacun avec un titre et un résumé.

## Contenu

*   `STT gemini chaptering.ipynb` : Notebook explorant l'utilisation de prompts spécifiques pour la segmentation thématique post-transcription.

## Approche

1.  **Transcription** : Conversion de l'audio en texte via Gemini (STT).
2.  **Segmentation** : Analyse du texte pour identifier les changements de sujets.
3.  **Titrage** : Génération de titres pertinents pour chaque segment identifié.
