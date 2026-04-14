# L300 Pitch Deck Outline : Architecture Système STT

## Titre: Architecture de Transcription Multi-Modèles Haute Flexibilité

### Slide 1 : Unification Multi-Fournisseurs
*   **Message Clé :** Un pipeline agnostique intégrant de manière transparente les LLM génératifs et les API Speech "Legacy".
*   **Points Clés :**
    *   Design Pattern de type "Adaptateur" unifiant `google-cloud-speech` (v1/v2) et `google-genai` (Vertex AI).
    *   Prise en charge native d'une large gamme de modèles : Google Chirp (USM), Gemini 1.5 Flash/Pro, et STT traditionnels (Long/Short).
    *   **Avantage :** Évite le "Vendor Lock-in" interne et permet de basculer d'un modèle à l'autre via de simples dictionnaires (`models_dic`, `models_v2`) selon les besoins coûts/performances.
    *   **Inconvénient :** La maintenance s'alourdit en raison des différences de formatage requises par chaque API (ex: gestion des Prompts pour Gemini vs Configuration d'AutoDecoding pour Speech v2).

### Slide 2 : Stratégies d'Ingestion et Scalabilité
*   **Message Clé :** Gestion adaptative des payloads pour contourner les limitations d'infrastructure et de quotas.
*   **Points Clés :**
    *   **In-Memory Processing :** Utilisation de `io.BytesIO()` pour traiter les chunks audio sans générer de coûteuses écritures sur disque dur (I/O disk).
    *   **Fallback Cloud Storage (GCS) :** Pour les gros volumes, l'architecture bascule sur `write_file_to_gcs` et utilise les opérations asynchrones (`long_running_recognize`) des APIs cloud.
    *   **Avantage :** Hautement résilient, capable de traiter aussi bien des micro-requêtes en streaming mémoire que d'ingérer des podcasts de 3 heures de façon asynchrone.
    *   **Inconvénient :** La logique de "fallback" (bascule local/cloud) complexifie le flux d'exécution et rend le débogage de la latence de bout en bout plus difficile.

### Slide 3 : Observabilité et Framework d'Évaluation de la Qualité (BigQuery)
*   **Message Clé :** Le pipeline n'est pas qu'un outil d'exécution, c'est un moteur d'amélioration continue piloté par les données.
*   **Points Clés :**
    *   Intégration d'un sous-système de "Benchmark" dédié (module `evaluator`).
    *   Évaluation systématique bidimensionnelle : Taux d'Erreur Strict (WER) et Préservation du Sens (Semantic Textual Similarity).
    *   Télémétrie automatisée : Insertion des prédictions, vérités terrains (ground truths) et métriques vers **Google BigQuery** (`save_results_df_bq`).
    *   **Avantage :** Permet aux directions techniques de construire des dashboards BI temps réel pour valider le ROI des modèles d'IA.
    *   **Inconvénient :** L'évaluation sémantique est intensive en calcul (utilisation de modèles HuggingFace Sentence Transformers locaux) et ralentit fortement le processus de CI/CD et de test.
