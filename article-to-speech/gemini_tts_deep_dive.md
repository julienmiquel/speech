# Gemini TTS API: The Deep Dive

> **Ce guide est conçu pour les développeurs souhaitant exploiter 100% des capacités vocal de Gemini (modèles `gemini-2.5-pro` / `gemini-2.5-flash`), y compris les fonctionnalités cachées et les techniques de "prompt engineering" audio.**

---

## 1. La Philosophie "Audio-First"

Contrairement aux API TTS classiques (Google Cloud TTS, AWS Polly) qui sont paramétriques (`rate=1.2`, `pitch=-2.0`), Gemini est un modèle **génératif multimodal**.

Cela signifie que **le contrôle se fait par le contexte et le prompt**, pas par des curseurs.
- **Tu veux qu'il parle vite ?** Dis-lui qu'il est pressé.
- **Tu veux qu'il chuchote ?** Mets-le en situation de secret.

---

## 2. Structure Complète de Configuration

Voici l'objet de configuration maximal qu'il est possible de passer à `client.models.generate_content`.

```python
from google.genai import types

config = types.GenerateContentConfig(
    # 1. Activation du TTS
    response_modalities=["AUDIO"], 

    # 2. Métadonnées Temporelles (Sous-titres / Lip-sync)
    audio_timestamp=True, 

    # 3. Configuration Vocale (L'un OU l'autre)
    speech_config=types.SpeechConfig(
        # --- OPTION A : Voix Unique (Standard) ---
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Aoede"
            )
        ),
        
        # --- OU OPTION B : Voix Clonnée (Deep) ---
        # voice_config=types.VoiceConfig(
        #     replicated_voice_config=types.ReplicatedVoiceConfig(
        #         voice_sample_audio=b"...", # Bytes du fichier WAV
        #         mime_type="audio/wav"
        #     )
        # ),

        # --- OU OPTION C : Multi-Locuteurs (Natif) ---
        # multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
        #     speaker_voice_configs=[
        #         types.SpeakerVoiceConfig(
        #             speaker="Narrateur",
        #             voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Fenrir"))
        #         ),
        #         types.SpeakerVoiceConfig(
        #             speaker="Alice",
        #             voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore"))
        #         )
        #     ]
        # ),

        # 4. Langue (Accent/Prononciation)
        language_code="fr-FR" 
    ),

    # 5. Directives de Style (Le "vrai" contrôle prosodique)
    system_instruction="""
    Tu es un lecteur de livres audio professionnel.
    Ton ton est calme, posé et captivant.
    Marque des pauses claires après chaque phrase.
    """
)
```

---

## 3. Le "Hack" de la Prosodie (Prompt Engineering Audio)

Puisqu'il n'y a pas de paramètres `speed` ou `emotion`, vous devez les simuler via le `system_instruction` ou le prompt utilisateur.

### Technique A : Le Directeur de Plateau
Donnez des instructions de scène explicites avant le texte.

**Prompt :**
```text
(Context: Breaking News, High Urgency, Fast Pace)
Flash Spécial : Une tempête approche de la côte...
```

### Technique B : Les Tags Vocaux (Markup Tags) - OFFICIEL
Documentés officiellement par Google, ces tags entre crochets agissent selon 4 modes :

**1. Sons Non-Verbaux (Mode 1)**
Le tag est remplacé par un son, il n'est pas lu.
- `[laughing]` : Rire
- `[sigh]` : Soupir
- `[uhm]` : Hésitation

**2. Modificateurs de Style (Mode 2)**
Le tag modifie la façon de dire la suite, sans être lu.
- `[whispering]` : Chuchotement
- `[shouting]` : Cri
- `[sarcasm]` : Ton sarcastique
- `[robotic]` : Voix robotique
- `[extremely fast]` : Débit très rapide

**3. Pauses et Rythme (Mode 4)**
Contrôle explicite du timing.
- `[short pause]` : Courte pause
- `[medium pause]` : Pause moyenne
- `[long pause]` : Longue pause

**⚠ Attention (Mode 3 - Vocalized)**: Certains tags comme `[scared]`, `[curious]` ou `[bored]` risquent d'être **lus à haute voix** par le modèle au lieu d'être joués. Pour ces émotions, privilégiez le *System Prompt* (Technique A).

### Technique C : La Ponctuation Rythmique
Utilisez la ponctuation pour forcer le rythme.
- `...` = Pause moyenne
- `—` = Changement de ton ou interruption
- `\n\n` = Pause longue (paragraphe)

---

## 4. Catalogue des Voix (Liste Complète)

Ces noms sont à passer dans `voice_name`.

| Nom | Genre | Style / Personnalité | Usage Recommandé |
| :--- | :--- | :--- | :--- |
| **Aoede** | Femme | Professionnelle, Claire, Posée | News, Documentaires, Assistants |
| **Fenrir** | Homme | Profond, Autoritaire, "Radio" | Narration épique, Thriller, News |
| **Charon** | Homme | Grave, Calme, Rassurant | Méditation, Histoires du soir |
| **Kore** | Femme | Douce, Apaisante, Maternelle | Bien-être, Histoires pour enfants |
| **Puck** | Homme | Énergique, Enjoué, Rapide | Gaming, Tutos dynamiques, Pubs |
| **Zephyr** | Femme | Légère, Aérienne, Douce | Poésie, Nature, Romance |
| **Léda** | Femme | Équilibrée, Standard | Usage général |
| **Orus** | Homme | Équilibré, Standard | Usage général |
| **Achernar** | Femme | Aiguë, Pétillante | Personnages jeunes |
| **Achird** | Homme | Jeune, Dynamique | Ados, Tech |
| **Algenib** | Homme | Baryton, Profond | Personnages imposants |

> **Astuce** : Combinez `Fenrir` (Narrateur) et `Aoede` (Journaliste) pour un rendu très pro.

---

## 5. Multi-Speaker : L'Arme Secrète

Pour créer une conversation réaliste sans générer X fichiers audio séparés.

**Scénario : Interview**

```python
contents = """
Journaliste: Bonjour Monsieur le Président.
Président: Bonjour à vous.
Journaliste: La situation est-elle sous contrôle ?
Président: [hésitant] Eh bien... c'est complexe.
"""

# Config
# Speaker "Journaliste" -> Aoede
# Speaker "Président" -> Fenrir
```

Le modèle va automatiquement :
1. Détecter les tours de parole basés sur les noms définis dans `speaker_voice_configs`.
2. Changer de voix instantanément.
3. Gérer les interruptions ou les chevauchements légers si le prompt le suggère.

---

## 6. Voice Cloning (ReplicatedVoiceConfig)

**Statut : Expérimental / Restricted**

Permet de cloner une voix avec quelques secondes d'audio.

**Contraintes Techniques :**
- **Format :** WAV (PCM 16-bit recommandé) ou MP3.
- **Taille :** Idéalement < 5MB pour la latence.
- **Qualité :** L'échantillon doit être propre, sans bruit de fond.

```python
types.ReplicatedVoiceConfig(
    voice_sample_audio=open("ma_voix.wav", "rb").read(),
    mime_type="audio/wav"
)
```

---

## 7. Récupération des Timestamps Audio

Si `audio_timestamp=True`, la réponse contient une liste de `TimeSegment` mappant texte et temps.

**Structure de la réponse (JSON-like) :**
```json
"voice_metadata": [
    {"start_offset": "0s", "end_offset": "0.5s", "word": "Bonjour"},
    {"start_offset": "0.5s", "end_offset": "0.8s", "word": ","},
    {"start_offset": "0.9s", "end_offset": "1.2s", "word": "ceci"}
]
```
*Note : La structure exacte peut varier légèrement selon la version de l'API (`video_metadata` ou `voice_metadata`).*

---

## 8. Limitations & Best Practices

1. **Longueur** : Gemini a une fenêtre de contexte énorme, mais pour l'audio, évitez de générer plus de 5-10 minutes d'un coup pour éviter les timeouts HTTP. Découpez les longs textes.
2. **Hallucinations Sonores** : Parfois, le modèle peut "rire" ou faire des bruits de bouche si le texte est ambigu. Le `strict_mode` via prompt ("Do not add sound effects") aide.
3. **Langues** : Si le texte est en FR mais `language_code="en-US"`, il lira le français avec un fort accent américain. Toujours matcher la langue.

---

## 9. Structure de la Réponse Audio (`AudioChunk`)

L'inspection de l'API confirme que la réponse audio est encapsulée dans des objets `AudioChunk` (via `part.inline_data`).

**Champs détectés dans `AudioChunk` :**
- `data` (`bytes`) : Les données audio brutes (PCM/WAV).
- `mime_type` (`str`) : Le type MIME (ex: `audio/pcm`, `audio/wav`).
- `source_metadata` : Métadonnées sur la source (si mixage ou multi-source).

> **Confirmation Finale** : L'inspection complète du SDK (`inspect_broad.py`) confirme qu'il n'existe **AUCUNE** classe cachée pour régler le débit (`rate`), la hauteur (`pitch`) ou le volume. Tout repose définitivement sur le **Prompt Engineering** et les **Markup Tags**.
