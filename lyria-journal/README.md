# Lyria Journal 🎵

Lyria Journal est une application sociale et musicale basée sur l'IA (Streamlit). Elle permet de capturer son "humeur quotidienne" via une photo ou un texte, génère un prompt musical détaillé avec **Gemini 2.5 Flash**, puis utilise l'API **Lyria 3** pour composer un aperçu musical (clip de 30 secondes). Les créations peuvent être conservées dans une galerie privée ou publiées pour la communauté.

## Fonctionnalités Principales
- **Photo to Music** : Prenez une photo pour générer la musique de l'instant.
- **Lyria Prompting Best Practices** : Utilisation d'instructions strictes pour Gemini afin d'orchestrer la génération via Lyria.
- **Galeries** : Stockage Firebase pour gérer les galeries privées et publiques.

## Installation Locale

1. Assurez-vous d'avoir Python 3.11+.
2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Configurez vos variables d'environnement (si vous n'utilisez pas GCP par défaut) :
   ```bash
   export GOOGLE_API_KEY="votre-cle-gemini"
   export GOOGLE_CLOUD_PROJECT="votre-projet-gcp"
   export FIREBASE_STORAGE_BUCKET="votre-bucket.appspot.com"
   ```
4. Lancez l'application Streamlit :
   ```bash
   streamlit run app.py
   ```

## Configuration Firebase (Pré-requis)

Pour le stockage des pistes audio et métadonnées, ce projet s'appuie sur :
- **Firebase Cloud Storage** pour les `.mp4` audios et images.
- **Cloud Firestore** pour les données (prompts, dates, etc.).

Vous devez avoir initialisé Firebase et Firestore dans votre projet Google Cloud.

**Notes importantes pour Firebase :**
1. **Firestore Indexes :** L'application effectue des requêtes triées sur Firestore (ex: `where('is_public', '==', True).order_by('created_at', descending=True)`). Lors de la première exécution de ces requêtes, Firestore renverra une erreur contenant un lien direct pour créer l'index composite nécessaire. Cliquez sur ce lien pour générer l'index.
2. **Permissions Storage :** Pour que les fichiers audio soient lisibles par tous, assurez-vous que votre bucket Cloud Storage autorise l'accès public en lecture (rôle `Lecteur des objets en l'espace de stockage` attribué à `allUsers`).

## Déploiement sur Cloud Run

Vous pouvez déployer cette application directement sur Cloud Run grâce au script fourni. Il utilisera `gcloud run deploy` avec les sources du répertoire courant.

1. Connectez-vous à GCP :
   ```bash
   gcloud auth login
   gcloud config set project VOTRE_PROJET_ID
   ```
2. Lancez le déploiement :
   ```bash
   ./deploy.sh
   ```

## Tests

Pour lancer les tests unitaires :
```bash
PYTHONPATH=. pytest tests/
```
