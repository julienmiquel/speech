# L400 Pitch Deck Outline : Deep-Dive Engineering STT

## Titre: Mécaniques Bas-Niveau, Quotas et Métriques Latentes

### Slide 1 : Gestion Fine de la Mémoire et de l'Encodage Audio
*   **Message Clé :** Extraction "à la volée" des propriétés du signal pour prévenir les erreurs de transcodage.
*   **Points Clés :**
    *   Lecture directe des attributs de l'objet `AudioSegment` (`channels`, `frame_rate`) pour une construction 100% dynamique du `RecognitionConfig` de l'API Google Cloud.
    *   Export mémoire avec casting strict : `sound[start:stop].export(buffer, format="wav")` garantissant la transmission PCM Linéaire requise par les moteurs Speech.
    *   **Avantage :** Élimine le risque de mismatch de sample-rate entre l'audio source et la configuration STT, une cause majeure d'erreurs 400 Bad Request silencieuses.
    *   **Inconvénient (Goulot d'étranglement) :** Le chargement initial `AudioSegment.from_mp3(file)` décompresse *l'intégralité* du fichier en RAM. Un podcast de 3h causera un OOM (Out Of Memory) sur une instance de calcul standard.

### Slide 2 : Limitation des Taux de Requêtes et Programmation Synchrone
*   **Message Clé :** Tolérance aux pannes implémentée, mais bridée par un modèle d'exécution bloquant.
*   **Points Clés :**
    *   Le code s'appuie sur `@retry.Retry(timeout=3000.0)` pour envelopper les appels réseau (Vertex AI/Speech API) et mitiger les quotas API (ex: erreurs 429 Too Many Requests).
    *   **Problème d'Architecture (Inconvénient) :** La boucle de traitement des chunks audio (`for (start, stop) in speak_sequences:`) est strictement synchrone. Le processus attend la fin de l'inférence du segment N avant d'envoyer le segment N+1.
    *   **Solution (Avantage d'une future refonte) :** Remplacer cette boucle par un `ThreadPoolExecutor` ou `asyncio.gather`. En parallélisant l'envoi des segments, le temps total d'exécution (Wall-clock time) chuterait de $O(N)$ à $O(1)$, contraint uniquement par le quota réseau simultané autorisé par GCP.

### Slide 3 : Évaluation NLP Avancée : Levenshtein vs Cosine Similarity
*   **Message Clé :** Un framework de benchmarking qui comprend les forces et les faiblesses des LLMs face aux systèmes ASR purs.
*   **Points Clés :**
    *   **La limite du WER (`jiwer` / `evaluate`) :** Calcul de la distance d'édition stricte. Un LLM comme Gemini est conçu pour "nettoyer" le langage (suppression des tics de langage "euh", correction grammaticale). Le WER pénalise lourdement ce comportement pourtant désiré.
    *   **Le correctif `sequence-evaluate` (`SeqEval`) :** Introduction du calcul de `semantic_textual_similarity`. Le texte généré et la vérité terrain sont projetés dans un espace vectoriel dense (via HuggingFace sentence-transformers).
    *   **Avantage :** Permet de prouver mathématiquement que la perte de précision (augmentation du WER) observée avec Gemini est en réalité un "Nettoyage Linguistique" (maintien d'un score de similarité sémantique élevé).
    *   **Inconvénient :** La normalisation et le nettoyage pré-évaluation (`cleanup = True`) sont minimaux. Une étape de NLP supplémentaire (lower-casing, regex-removal des ponctuations) est souvent requise pour stabiliser les scores des evaluateurs.
