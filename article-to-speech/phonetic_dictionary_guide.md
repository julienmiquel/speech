# Guide d'utilisation : Dictionnaires Phonétiques et Cloud TTS

L'application supporte désormais une gestion avancée des prononciations via l'API **Google Cloud Text-to-Speech**, avec un système de fallback intelligent pour préserver la rétrocompatibilité avec Vertex AI et les anciennes méthodes.

## 1. Le problème initial
Google Cloud TTS supporte le paramètre natif `CustomPronunciations` pour forcer la prononciation exacte de certains mots (noms propres, marques, sigles). Cependant, cette API est très stricte :
- Elle **exige** que la prononciation soit au format **IPA (Alphabet Phonétique International)** via `PHONETIC_ENCODING_IPA`.
- Elle **rejette (Erreur 400)** tout mot comportant des tirets ou des majuscules dans la prononciation (ex: `Fi-yon`, `Sass`, etc.).
- Elle **rejette (Erreur 400)** les dictionnaires contenant des doublons insensibles à la casse (ex: `Fast-fashion` et `fast-fashion`).

## 2. La solution implémentée : Le Dictionnaire Hybride
Pour vous permettre d'utiliser Cloud TTS sans avoir à convertir manuellement tout votre ancien dictionnaire (qui utilisait des remplacements textuels comme `Fi-yon`), nous avons mis en place un **système de partitionnement hybride** dans `gemini_url_to_audio.py` (`CloudTTSProvider`).

### A) Les vrais termes IPA (Envoyés à l'API Cloud TTS)
Si une prononciation de votre dictionnaire ne contient ni tirets ni majuscules (ex: `fijɔ̃` pour Fillon, `ʃi.in` pour Shein), elle est reconnue comme du **vrai IPA**.
- Ces termes sont extraits et envoyés **nativement** dans la configuration `CustomPronunciations` de l'API Google Cloud TTS. C'est la méthode la plus optimisée et naturelle pour la voix.

### B) Les "Pseudo-Phonétiques" (Remplacement textuel via Regex)
Si une prononciation contient des majuscules ou des tirets (ex: `Chi-ine`, `Ré-ta-yo`, `Faste-fa-chion`), elle est considérée comme un "pseudo-phonème" hérité.
- Ces termes sont **exclus** de la requête API pour éviter le crash.
- Ils sont à la place appliqués **directement sur le texte** sous forme de remplacement textuel Regex (ex: "François Fillon" -> "François Fi-yon") avant d'être envoyés à l'API.

## 3. Déduplication Intelligente
L'API Cloud TTS plantait s'il y avait des mots en double, même avec une casse différente.
Le générateur filtre désormais les mots en double de manière insensible à la casse (`lowercase`). Si `Fast-fashion` et `fast-fashion` existent, seul le premier est conservé pour l'API.

## 4. Extraction Automatisée via Gemini
L'étape de "Recherche de prononciations (Google Search)" depuis l'interface Streamlit a été mise à jour !
Désormais, **Gemini génère strictement de l'IPA** au lieu d'approximations françaises.
- **Avant** : `{"term": "Fillon", "guide": "Fi-yon"}`
- **Maintenant** : `{"term": "Fillon", "guide": "fijɔ̃"}`

Quand vous ajoutez de nouveaux mots via l'interface de recherche, vous alimentez directement le moteur `CustomPronunciations` de Cloud TTS de manière optimale.

## 5. Résumé pour l'utilisateur
Vous n'avez **rien** à changer dans vos habitudes !
1. Les anciens mots avec `-` ou des majuscules continueront de fonctionner en mode dégradé (Remplacement texte).
2. Les générateurs vont progressivement insérer du vrai IPA dans votre dictionnaire pour une prononciation parfaite via Cloud TTS.
3. Les erreurs 400 pour doublons de casse `Aa` vs `aa` sont filtrées silencieusement.
