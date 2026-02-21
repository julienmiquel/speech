# ASR Metrics

Librairie d'outils et de notebooks pour le calcul de métriques d'évaluation des systèmes de reconnaissance vocale (ASR).

## Métriques Principales

*   **WER (Word Error Rate)** : La mesure standard de performance ASR.
    *   Formule : `(Substitutions + Insertions + Deletions) / Nombre total de mots dans la référence`
*   **Normalisation** : Prétraitement essentiel pour éviter de compter des erreurs dues uniquement au formatage (ex: "10" vs "dix", majuscules/minuscules, ponctuation).

## Contenu

*   `ASR_metrics.ipynb` : Notebook démontrant l'utilisation des librairies `jiwer`, `werpy`, `evaluate` et `seq_eval` pour calculer le WER et normaliser les textes.

## Bibliothèques Python

*   `jiwer` : Calcul rapide et flexible du WER.
*   `werpy` : Outil simplifié pour le calcul du WER sur des listes.
*   `evaluate` (Hugging Face) : Interface standardisée pour diverses métriques NLP.
