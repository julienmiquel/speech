# PhD-Level Research Analysis: STT Pipeline Architecture

## Critique Théorique de l'Architecture du Pipeline STT

Le pipeline STT (Speech-to-Text) examiné dans ce dépôt repose sur un assemblage pragmatique de modèles génératifs de pointe (Google Gemini 1.5 Pro/Flash) et d'interfaces de reconnaissance vocale dédiées (Google Cloud Speech v1/v2, modèles Chirp USM). L'architecture est fondamentalement orientée autour d'un traitement hybride combinant des heuristiques locales de pré-traitement du signal et des appels distants vers des API Cloud.

### 1. Stratégies de Segmentation Temporelle (Chunking)

La gestion de la fenêtre de contexte limitée (aussi bien pour les STT traditionnels que pour l'ingestion d'audio dans les LLMs) est un problème ouvert. Ce dépôt implémente trois heuristiques principales pour la segmentation de séquences temporelles.

#### Technique A : Découpage par Silences Actifs (Energy-based VAD)
Utilisation de `pydub.silence.detect_nonsilent` avec un algorithme de diminution récursive du seuil (`min_silence_len`).

*   **Avantages :**
    *   Préserve l'intégrité lexicale et sémantique : les segments ne coupent pas les mots ou les phrases en plein milieu, minimisant la corruption phonétique aux frontières de découpage.
    *   Améliore potentiellement les scores de "Semantic Textual Similarity" (STS) en fournissant au modèle un flux de pensée naturel.
*   **Inconvénients :**
    *   **Complexité Temporelle:** L'algorithme actuel emploie une boucle `while` ré-évaluant l'intégralité du fichier audio (`myaudio`) en réduisant itérativement `min_silence_len` de 100ms si un segment excède 59 secondes. Cette complexité ($O(K \cdot N)$, où $K$ est le nombre d'itérations) est très inefficace.
    *   **Sensibilité au Bruit (Noise Robustness):** Le seuillage basé sur l'énergie (`dBFS-20`) est reconnu comme sous-optimal dans des conditions non-stationnaires (SNR bas), entraînant un sur-découpage ou un sous-découpage sévère comparé aux VAD neuronaux (ex: WebRTC VAD, CNN-based VAD).

#### Technique B : Découpage Strict (Time-based Hard Split)
Découpage "aveugle" par fenêtres fixes (ex: incréments stricts de 59 secondes).

*   **Avantages :**
    *   **Latence et Complexité $O(1)$ par chunk :** La segmentation est instantanée et hautement prédictible, essentielle pour des architectures de streaming strictes où le budget temporel est contraint.
    *   Consommation mémoire constante.
*   **Inconvénients :**
    *   **Dégradation du WER (Word Error Rate):** Tronque inévitablement des mots ou phonèmes aux limites du chunk. Ces coupures nettes génèrent des artefacts acoustiques qui désorientent les décodeurs CTC (Connectionist Temporal Classification) ou les mécanismes d'attention des LLM, provoquant des hallucinations locales ou des suppressions (Deletions).

#### Technique C : Streaming gRPC (Cloud Speech v2)
Délégation de l'état temporel à l'API Cloud (impliqué par l'utilisation de `cloud_speech.AutoDetectDecodingConfig` et des reconnaisseurs gérés).

*   **Avantages :** Résout intrinsèquement le problème du découpage en streamant le flux audio en continu. Le back-end gère la mémoire contextuelle.
*   **Inconvénients :** Dépendance forte au réseau (jitter/packet loss affectant la transcription) et opacité de l'algorithme de bufferisation côté serveur.

### 2. Évaluation de la Précision : Métriques Orthogonales

Le dépôt intègre un framework d'évaluation sophistiqué combinant des métriques exactes et des métriques latentes, géré via les librairies HuggingFace `evaluate`, `jiwer` et `sequence-evaluate` (via un module `SeqEval`).

#### Métrique 1 : Word Error Rate (WER) via `jiwer`
*   **Avantages :** Standard "Gold" de l'industrie ASR. Mesure stricte des distance de Levenshtein (Insertions, Deletions, Substitutions) sur la séquence de mots. Essentiel pour auditer la justesse acoustique absolue.
*   **Inconvénients :** Ne capture pas la qualité sémantique. Une erreur de ponctuation ou un synonyme parfait pénalise le WER de la même manière qu'un contresens majeur.

#### Métrique 2 : Semantic Textual Similarity (STS) via `sequence-evaluate`
*   **Avantages :** Utilise des embeddings vectoriels (ex: Sentence Transformers) pour calculer la distance cosinus entre la vérité terrain et la prédiction. Ceci est crucial lors de l'utilisation de LLMs (Gemini) comme STT, car les LLMs ont tendance à reformuler légèrement ou à corriger grammaticalement l'audio source. Le STS permet de valider si l'information a été transmise, même si le WER est moyen.
*   **Inconvénients :** Computationnellement coûteux à évaluer (nécessite l'inférence d'un modèle d'embedding additionnel). Moins adapté pour des cas d'usage stricts (ex: juridique, médical) où la transcription verbatim est requise.

### 3. Écarts par rapport à l'État de l'Art et Recommandations

L'architecture actuelle dévie des pipelines STT End-to-End (E2E) modernes sur deux axes majeurs :
1.  **Diarisation Manquante :** Bien que mentionnée conceptuellement, l'architecture ne démontre pas l'utilisation de modèles de clustering de locuteurs (ex: Spectral Clustering sur des vecteurs d-vector/x-vector). Confier la reconnaissance du locuteur uniquement au LLM est source d'instabilité.
2.  **Gestion de la Concurrence :** Le pipeline de traitement est synchrone (une boucle `for` attend la résolution de chaque appel API). L'introduction d'I/O asynchrones (`asyncio` avec Vertex AI Async Client) multiplierait le débit par le nombre de workers, transformant un processus batch en un système hautement concurrent adapté au traitement de larges corpus audio.
