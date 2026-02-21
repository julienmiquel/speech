# STT Benchmark

Outils et scripts pour évaluer et comparer la qualité des modèles de transcription (ASR).

## Objectifs

*   Comparer les performances des modèles Gemini (1.5 Pro, Flash, etc.) et Google Speech-to-Text.
*   Mesurer la précision via le WER (Word Error Rate).
*   Évaluer la similarité sémantique (Semantic Textual Similarity) pour aller au-delà de la simple correspondance mot à mot.

## Contenu

*   `STT benchmark gemini ASR.ipynb` : Benchmark spécifique aux modèles Gemini via Vertex AI.
*   `STT benchmark google speech.ipynb` : Benchmark pour l'API Google Cloud Speech-to-Text (STT V1/V2).

## Métriques Utilisées

*   **WER (Word Error Rate)** : Taux d'erreur standard (Insertions, Deletions, Substitutions).
*   **Semantic Similarity** : Mesure de la proximité du sens entre la transcription et la vérité terrain (Ground Truth).

## Utilisation

Les notebooks nécessitent un dataset de test (fichiers audio + transcriptions de référence) stocké sur Google Cloud Storage (GCS).
