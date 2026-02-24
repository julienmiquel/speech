# Article : Plongée technique dans les capacités TTS (Text-to-Speech) du projet

Ce document présente une analyse détaillée de toutes les fonctionnalités Text-to-Speech implémentées dans le projet **Article-to-Speech**, piloté par les technologies de Google Cloud et Vertex AI. L'objectif de la plateforme est de transformer la lecture classique d'articles de presse en une expérience audio dynamique, professionnelle et multi-voix.

---

## 1. Moteurs de Synthèse : L'Architecture Factory

Pour garantir flexibilité et évolutivité face aux limites des différentes API Google, l'application repose sur un design pattern **Factory** (`TTSFactory` dans `gemini_url_to_audio.py`). Le système peut basculer d'un fournisseur ("Provider") à un autre de manière transparente pour l'interface utilisateur, selon la variable d'environnement `TTS_PROVIDER`.

### A. Le Provider : `CloudTTSProvider` (Google Cloud Text-to-Speech)
Implémentation s'appuyant sur l'API native Google Cloud (bibliothèque `google-cloud-texttospeech`).
- **Fiabilité Industrielle** : Conçu pour les scénarios de production denses nécessitant de la prévisibilité financière et opérationnelle.
- **Dépassement de la limite de 4000 octets** : Les modèles de synthèse Google sont structurellement limités à des envois de 4000 caractères par paquet. Le `CloudTTSProvider` implémente un algorithme de *Chunking Inteligente* qui découpe le long texte d'un article en morceaux sûrs (~3500 caractères), envoie les requêtes en asynchrone fluide, puis recoud ensemble les "frames" audio binaires de façon imperceptible pour générer un méga-fichier `.wav` de plusieurs minutes.
- **Formats supportés** : `VoiceSelectionParams` pour les modèles classiques mono-locuteur, et l'objet structuré `MultiSpeakerMarkup` qui concatène les dialogues entre deux locuteurs différents.

### B. Le Provider : `VertexTTSProvider` (Gemini & Vertex AI)
Implémentation s'appuyant sur l'écosystème IA générative Gemini (bibliothèque `google-genai`).
- **Prérogatives Expérimentales** : Principalement utilisé pour interroger des modèles Early Access Program (EAP) tels que `gemini-2.5-flash-tts-eap` (souvent exclusifs à `us-central1`).
- **Clonage de voix (Voice Cloning)** : Ce provider est le seul capable d'exécuter la fonction expérimentale `synthesize_replicated_voice()` qui copie le timbre d'une voix à partir d'un fichier audio en entrée et applique ce timbre à un nouveau texte généré (*zero-shot voice replication*).

---

## 2. Le Dictionnaire Phonétique Hybride (Gestion des 400)

La prononciation de noms propres, acronymes et marques étrangères (ex: "Shein", "Retailleau", "SaaS") est critique dans un podcast d'actualité. 
Les API classiques ont tendance à inventer ou franciser nativement tous les mots étrangers. 

Pour forcer la main au modèle, nous combinons **deux approches distinctes et automatisées** :

### L'approche API "Premium" : Alphabet Phonétique International (IPA)
L'API Cloud TTS accepte une liste d'exceptions via le paramètre `CustomPronunciations` couplé à la constante `PHONETIC_ENCODING_IPA`. Si le dictionnaire généré fournit une chaine IPA stricte (tout en minuscules avec les bons symboles, ex: `fijɔ̃` pour Fillon), ce terme est encapsulé binairement lors de la transmission et le moteur ajuste la forme d'onde sans toucher aux lettres.
**Avantage** : Rendu sonore extrêmement pur sans hachure.

### L'approche "Legacy" : Remplacement Regex (Pseudo-Phonétique)
Cependant l'API Cloud TTS *crashe* (Erreur 400 "Invalid Phrases") si on lui fournit des tirets, des virgules, ou des majuscules dans l'instruction de phonème (ex: `Fi-yon` ou `Chi-ine`).
Dans ce cas, l'implémentation filtre conditionnellement ces mots non-IPA. Elle les retire de la requête `CustomPronunciations` et applique à la place une substitution basique `Regex string replace` (ex: remplace le mot "Shein" par l'orthographe "Chi-ine" directement dans la chaine de texte envoyée au modèle).
**Avantage** : Rétrocompatibilité avec les prononciations définies artisanalement par les humains.

### Génération de l'IPA par Gemini
Afin de fluidifier ce pipeline, lorsqu'un utilisateur importe un nouvel article, l'application délègue à **Gemini 2.5 Flash** (couplé à l'outil `Google Search`) l'identification des termes ambigus et génère automatiquement pour chaque nom propre le rendu IPA strict (ex : `ʃi.in`). La requête générée trace nativement ce qui a été soumis dans le JSON d'historisation `applied_ipa_phonemes`.

---

## 3. L'Architecture Multi-Speaker (Dialogue)

L'une des plus-values produit de l'application est la capacité de convertir un article linéaire et chronologique en format interactif de 2 locuteurs :
1. **L'Anchor (Le Présentateur)** : Ton autoritaire, stable, formel, pour porter l'intrigue et lire le fil d'une dépêche.
2. **Le Reporter / L'Expert** : Ton conversationnel et dynamique. Il est utilisé (via l'algorithme d'Analyse du Parseur) pour reprendre en vocal les citations ou "encarts" pertinents de l'article (*sidebars* au milieu du HTML).

### Format MultiSpeakerMarkup de Cloud TTS
La méthode `synthesize_multi_speaker` itère sur chaque structure JSON (Speaker "R" ou "S") fournie par Gemini après extraction HTML. 
Le texte est segmenté en **Turns** (les tours de prise de parole). Cloud TTS impose que ces *Turns* soient packagés dans des lots de maximum 4000 caractères au format binaire. Plutôt que de synthétiser 50 micro-fichiers WAV, l'algorithme "Batch" les prises de paroles et insère au besoin un délai structurel (`delay_seconds`) entre les phrases pour simuler le silence narratif naturel.

---

## Conclusion
Le projet maîtrise toute la chaîne de bout en bout :
- De l'URL web brute à une structure JSON de données nettoyées.
- De l'ingénierie LLM pour extraire les cas critiques de phonétique et simuler un Google Search.
- D'un pattern de développement distribué (`TTSProvider Interface`) qui adresse les limites techniques strictes des endpoints Cloud API pour garantir qu'aucune ressource ne dépasse en longueur.
