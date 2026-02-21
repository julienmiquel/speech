# Gemini Speech-to-Text (STT)

Expérimentations et exemples d'utilisation des modèles Google Gemini pour la transcription automatique de la parole (ASR).

## Fonctionnalités

*   **Transcription Longue Durée** : Stratégies de découpage (chunking) pour traiter des fichiers audio dépassant la limite de tokens des modèles.
    *   Découpage par silences (Voice Activity Detection implicite).
    *   Découpage strict (time-based).
*   **Diarisation** : Identification des locuteurs dans la transcription.
*   **Timestamps** : Récupération des horodatages pour chaque segment ou mot.
*   **Comparaison de Modèles** : Scripts pour tester différentes versions de Gemini (Pro, Flash).

## Contenu

*   `STT gemini ASR examples.ipynb` : Notebook principal démontrant l'utilisation de l'API Vertex AI pour la transcription, avec gestion des fichiers locaux et GCS.

## Pré-requis

*   Compte Google Cloud Platform.
*   Accès à Vertex AI.
*   Bibliothèques Python : `google-cloud-aiplatform`, `pydub`, `pandas`.
