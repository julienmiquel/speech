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

Lancer l'application complète (FastAPI + Streamlit) :

```bash
./run.sh
```

L'interface sera accessible dans votre navigateur (par défaut sur `http://localhost:8501`) et l'API sur `http://localhost:8000`.
# Article-to-Speech : Générateur Audio pour Articles de Presse

Article-to-Speech est une application Streamlit puissante qui automatise l'extraction de texte à partir d'URL d'articles de presse (média en ligne) et les synthétise en fichiers audio (podcasts, flash infos, brèves) à l'aide des modèles de pointe d'Intelligence Artificielle de Google (Gemini et Cloud TTS).

## Fonctionnalités Principales

- **Extraction Intelligente de Texte** : Utilise Gemini 2.5 Flash pour analyser la structure de la page HTML, extraire le contenu narratif principal et écarter les menus, publicités et éléments superflus.
- **Analyse Sémantique et Structuration** : Découpe l'article extrait en un dialogue structuré (Narrateur Principal vs Reporter secondaire) pour rendre l'écoute plus dynamique.
- **Recherche de Prononciation Automatisée** : Analyse le texte pour identifier les noms propres, marques (ex: Shein, Temu) ou termes techniques et utilise Gemini couplé à Google Search pour générer la prononciation exacte en **Alphabet Phonétique International (IPA)**.
- **Dictionnaire Phonétique Hybride** : Gère automatiquement un dictionnaire pour imposer la prononciation de mots complexes grâce à l'API Cloud TTS `CustomPronunciations` pour l'IPA, et un remplacement Regex pour les règles phonétiques basiques (ex: tirets/majuscules).
- **Architecture de Synthèse Modulaire (Factory Pattern)** : Support de plusieurs fournisseurs et moteurs de rendu :
  - **Google Cloud Text-to-Speech** : Idéal pour les gros volumes de production continus, gère le Multi-Speaker, et évite nativement la limitation de 4000 octets via un système de "chunking" asynchrone intelligent.
  - **Vertex AI (Gemini TTS)** : Support des configurations de voix avancées et pré-générations expérimentales.
- **Sauvegarde Distante & Cache** : Tous les textes extraits sont mis en cache. Application configurable pour basculer facilement de `local` à `remote` (Google Cloud Storage / Firebase) pour les assets et les prompts.

## Architecture & Installation

Le projet repose sur **Python 3.13** et nécessite un environnement virtuel.

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
./run.sh
# Le script lance à la fois le backend FastAPI (port 8000) et le frontend Streamlit (port 8501).
```

### Configuration Globale (`.env`)

L'application est entièrement paramétrable via un fichier `.env` à la racine :

```env
APP_MODE=local                # local ou remote
TTS_PROVIDER=cloud            # 'cloud' (Google Cloud TTS) ou 'vertex' (Vertex AI)
LOCATION=europe-west1         # Région Google Cloud (ex: europe-west1, us-central1)
GOOGLE_CLOUD_PROJECT=...      # ID de votre projet Google Cloud
```

## Structure du Projet

- `app.py` : Le point d'entrée principal (interface utilisateur Streamlit).
- `gemini_url_to_audio.py` : Le moteur backend gérant l'orchestration LLM, le parsing, le cache et l'architecture "Factory" du TTS.
- `prompts.py` : Fichier de configuration isolant l'ensemble des instructions systèmes (Prompts) données à Gemini pour l'extraction et la génération.
- `phonetic_dictionary_guide.md` : Guide technique dédié à l'explication des subtilités du moteur phonétique et de la différence entre Cloud TTS (IPA) et Regex.
- `assets/` : Répertoire de stockage local des audios `.wav` générés et des métadonnées `.json`.
- `brain/` : Répertoire des artefacts et logs d'Antigravity (l'assistant IA du projet).

## Cas d'usage & Démos

L'interface de l'application permet : 
1. **Atelier "Générateur"** : Collez n'importe quelle URL pour automatiser toute la chaîne (Extraction -> Prononciation -> Structure -> Audio).
2. **Atelier "Playground"** : Saisissez du texte brut arbitraire pour tester directement des voix et ajuster des balises (`[pause]`, `<speak>`).
3. **Playground "Audio"** : Laboratoire pour tester les voix mono-locuteur, l'ajustement du pitch, l'Auto-tune et la vitesse de locution.
