# Gemini TTS Factory

Application interactive basée sur Streamlit pour transformer des articles (depuis une URL ou du texte brut) en fichiers audio de haute qualité, utilisant les capacités de Google Gemini et Google Cloud Text-to-Speech.

## Fonctionnalités

*   **Extraction de Contenu** : Récupération automatique du texte d'articles à partir d'URLs (supporte BeautifulSoup et Gemini pour le parsing intelligent).
*   **Recherche de Prononciation** : Utilisation de Google Search et Gemini pour identifier et suggérer la prononciation correcte des noms propres et termes techniques.
*   **Gestion de Dictionnaire** : Interface pour ajouter, modifier et supprimer des règles de prononciation personnalisées.
*   **Structuration Intelligente** : Analyse du texte par Gemini pour ajouter des pauses, des didascalies (émotions) et attribuer les locuteurs (Speaker 1 / Speaker 2).
*   **Synthèse Vocale (TTS)** : Génération audio multi-locuteurs via Google Cloud TTS (modèles Vertex AI, Journey, etc.). Supporte le clonage de voix (expérimental).
*   **Historique** : Sauvegarde et relecture des fichiers audio générés.

## Pré-requis

*   Python 3.10+
*   Un projet Google Cloud avec les API activées (Vertex AI, Text-to-Speech).
*   Authentification configurée (ex: `gcloud auth application-default login`).

## Installation

```bash
cd article-to-speech
pip install -r requirements.txt
```

## Utilisation

Lancer l'application Streamlit :

```bash
streamlit run app.py
```

L'interface sera accessible dans votre navigateur (par défaut sur `http://localhost:8501`).
