# Synthèse Gemini TTS pour Le Figaro

Ce document présente une synthèse technique et pratique pour l'intégration de Gemini TTS 2.5 PRO dans le projet "Article-to-Speech" avec Le Figaro.

---

## 1. Questions & Réponses : Prononciation et Prompting

### Gestion de la Prononciation (Noms Propres & Termes Techniques)
**Question :** Comment garantir la bonne prononciation de noms comme "François Fillon" ou de termes techniques ?
**Réponse :** Gemini TTS 2.5 PRO ne supporte **pas le SSML** standard (donc pas de balise `<phoneme>`). Le contrôle se fait exclusivement via le **Prompt en Langage Naturel**.
*   **Méthode :** Fournir des instructions explicites dans le prompt système ou utilisateur.
*   **Exemple :** "Tu es un présentateur de journal télévisé. Fais attention à la prononciation des noms propres. Par exemple, 'Fillon' se prononce 'Fi-yon'."

**Exemple de Payload JSON pour la Prononciation :**
```json
{
  "input": {
    "prompt": "Tu es un expert technique. L'acronyme 'SLA' doit être épelé S-L-A. 'SaaS' se prononce 'Sass'.",
    "text": "Nous devons respecter le SLA pour notre offre SaaS."
  },
  "voice": {
    "languageCode": "fr-FR",
    "model_name": "gemini-2.5-pro-tts",
    "name": "Kore"
  }
}
```

### Intégration et Mixage Audio
**Question :** Peut-on mixer des jingles ou fonds sonores directement ?
**Réponse :** Non. Gemini TTS génère uniquement la piste vocale.
*   **Contrainte :** Pas de balise `<audio>` SSML supportée.
*   **Solution :** Le mixage doit être réalisé en **post-production** en combinant le fichier audio généré par l'API avec les autres pistes sonores.

### Cohérence de la Voix ("Side")
**Question :** Comment éviter que la voix change (problème de "Side") ?
**Réponse :** La cohérence est assurée par l'utilisation constante du paramètre `voice.name` (Speaker ID).
*   **Note :** Le terme "Side" évoqué en atelier semble être spécifique à l'application de démonstration fournie (peut-être une variable de configuration locale), et non un paramètre de l'API Gemini.

### Qualité et Coûts
**Question :** Quid de la qualité "robotique" et des coupures vs anciens systèmes ?
**Réponse :** Gemini 2.5 PRO est conçu pour une prosodie naturelle et émotionnelle, corrigeant les défauts robotiques.
*   **Modèles :** `gemini-2.5-pro-tts` (Haute Qualité) vs `gemini-2.5-flash-tts` (Latence/Coût optimisé).

---

## 2. Guide de Prompting Affectif (Best Practices)

Pour obtenir un discours expressif, alignez ces trois piliers :
1.  **Le Style Prompt** : Définit le ton global (ex: "Tu es en colère").
2.  **Le Contenu du Texte** : Le sens des mots doit porter l'émotion.
3.  **Les Balises (Markup Tags)** : Pour des actions localisées.

### Glossaire des Tags Validés

#### Haute Fiabilité (High Reliability)
Ces tags fonctionnent de manière cohérente pour ajouter de l'humanité ou modifier le débit.

| Tag | Effet | Exemple d'Usage |
| :--- | :--- | :--- |
| `[sigh]` | Ajoute un soupir audible | "Je suis fatigué. `[sigh]` C'était une longue journée." |
| `[laughing]` | Ajoute un rire | "C'est très drôle ! `[laughing]`" (Le type de rire dépend du prompt global) |
| `[uhm]` | Ajoute une hésitation | "Je ne suis pas sûr... `[uhm]` peut-être demain." |
| `[extremely fast]` | Accélère le débit vocal | "`[extremely fast]` Vite, nous n'avons plus de temps !" |
| `[shouting]` | Augmente le volume/intensité | "`[shouting]` Attention !" |

#### Fiabilité Moyenne (Medium Reliability)
*   **`[whispering]`** : Produit souvent un "chuchotement de scène" (assez fort pour être entendu au théâtre).
*   **`[robotic]`** : Donne un ton robotique, mais la portée (mot ou phrase) peut varier.

#### Fiabilité Basse / Contextuelle
*   **`[crying]`, `[bored]`, `[scared]`** : Résultats très dépendants du texte. "Je suis effrayé `[scared]`" marchera mieux que "Bonjour `[scared]`".

### Stratégies Clés
*   **Alignement Sémantique :** Ne demandez pas un ton joyeux sur un texte triste.
*   **Simplicité :** Un prompt clair ("Dis-le avec tristesse") vaut mieux qu'une liste complexe d'adjectifs contradictoires.

### Exemples de Prompts pour les Cas Figaro
Voici des modèles de prompts conçus pour répondre aux difficultés spécifiques rencontrées :

#### 1. Gestion de la Prononciation (Noms Propres)
*Objectif : Corriger "François Fillon" ou autres noms.*
> **Prompt :** "Tu es un journaliste politique expérimenté. Ton élocution est parfaite. Attention aux noms propres : 'François Fillon' se prononce 'Fi-yon', 'Jean-Luc Mélenchon' se prononce 'Mé-lan-chon'. Adopte un ton neutre et informatif."

#### 2. Termes Techniques & Acronymes
*Objectif : Bien prononcer "SaaS", "SLA", "RSE".*
> **Prompt :** "Tu lis une chronique économique. Prononce les acronymes suivants ainsi : 'SaaS' se dit 'Sass', 'RSE' s'épelle R-S-E, 'B2B' se dit 'Bi-tou-bi'. Le reste du texte doit être lu avec expertise et clarté."

#### 3. Éviter le Ton "Robotique"
*Objectif : Rendre la voix plus vivante et engagée.*
> **Prompt :** "Tu es un conteur passionné. Ne sois jamais monotone ou robotique. Varie ton intonation pour capter l'attention de l'auditeur. Marque de légères pauses pour souligner les points importants. Ton ton doit être chaleureux et captivant."

#### 4. Incitation au "Nettoyage" de Contenu (Infographies)
*Note : Le prompt TTS ne peut pas "voir" l'image, mais si le texte contient des descriptions d'infographies, on peut guider la lecture.*
> **Prompt (si le texte inclut une description) :** "Tu organises ta lecture pour l'audio. Si tu rencontres une description d'infographie commençant par 'Graphique :', change légèrement de ton pour indiquer qu'il s'agit d'une description visuelle, plus descriptive et plus lente."

---

## 3. Next Steps (Actions Requises)

1.  **Valider les Voix Françaises :** Confirmer la liste exacte des `voice.name` disponibles pour `fr-FR` sur Gemini TTS 2.5 PRO.
2.  **Bibliothèque de Prompts :** Créer des exemples de prompts standardisés pour les cas récurrents du Figaro (titres, citations, noms politiques).
3.  **Correction Démo Streamlit :**
    *   Fixer les problèmes d'environnement (VENV, dépendances).
    *   Résoudre le bug de la boucle "Watch".
    *   Clarifier la config régionale ("Europe Prestin").
4.  **Custom Voice (Chirp 3) :** Initier le processus d'allowlisting pour "Instant Custom Voice" si le clonage est prioritaire.
5.  **Stratégie Contenus Enrichis :** Définir éditorialement le traitement des infographies (description par Gemini LLM ?) et vidéos.
