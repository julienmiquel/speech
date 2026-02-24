# Prompting Affective Speech in Gemini TTS

*![][image1] Applied AI Engineering: 1P Multimodal x Evaluations Workstream*

# A Practical Guide to Prompting Affective Speech in Gemini TTS

[Hussain Chinoy](mailto:ghchinoy@google.com) Aug 31, 2025  
Contributors [Sandeep Gupta](mailto:sandeepngupta@google.com) [Haris Ioannou](mailto:harisi@google.com)

This guide provides best practices and a glossary of validated markup for generating expressive speech with Google's Gemini Text-to-Speech models. This is the output of a collaborative, iterative discovery process.

This document is currently the basis of the official documentation [https://cloud.google.com/text-to-speech/docs/gemini-tts\#prompting\_tips](https://cloud.google.com/text-to-speech/docs/gemini-tts#prompting_tips)

---

## The Three Pillars of Affective Speech

To achieve nuanced and reliable results, it is crucial to align three key levers that influence the model's performance:

1. **The Style Prompt:** This is the primary driver of the overall emotional tone and delivery. It sets the general context for the entire speech segment (e.g., "You are angry and yelling," "You are telling a secret in a hushed tone").  
     
2. **The Text Content:** The semantic content of the phrase you are synthesizing is a powerful signal. An evocative phrase that is emotionally consistent with the style prompt will produce much more reliable results than a neutral one.  
     
3. **The Markup Tag:** Bracketed tags like `[sigh]` or `[robotic]` are best used for injecting a specific, localized *action* or *style modification*, not for setting the overall tone.

---

## Markup Glossary & Behavior

We have discovered that bracketed tags operate in at least three distinct modes. Understanding the mode of a tag is key to using it effectively.

### Mode 1: Non-Speech Sound

*The markup is replaced by an audible, non-speech vocalization. The tag itself is not spoken.*

- **`[sigh]`**, **`[laughing]`**, **`[uhm]`**  
  - **Reliability:** High.  
  - **Guidance:** Excellent for adding realistic, human-like hesitations and reactions. The emotional quality of the speech that *follows* the sound is highly dependent on the style prompt. For `[laughing]`, a generic prompt may result in a laugh of shock, while a specific prompt (e.g., "...react with an amused laugh") can create a laugh of amusement.

### Mode 2: Modifier

*The markup is not spoken, but modifies the delivery of the subsequent speech. The scope of the modification can vary.*

- **`[sarcasm]`**  
    
  - **Reliability:** High.  
  - **Guidance:** This tag successfully imparts a sarcastic tone on the subsequent phrase. This is a key finding, as it shows that even abstract concepts or nouns can function as powerful modifiers.


- **`[robotic]`**  
    
  - **Reliability:** Medium.  
  - **Guidance:** This tag makes the subsequent speech sound robotic. Our testing shows this effect can extend across an entire phrase, not just a single word. The style prompt (`Say in a robotic way`) is still recommended to support the effect.


- **`[extremely fast]`**, **`[shouting]`**, **`[whispering]`**  
    
  - **Reliability:** High / Medium (for `[whispering]`).  
  - **Guidance:** These are reliable for controlling speed and volume. However, for effects like `[whispering]`, the best results are achieved when the style prompt is also explicit (e.g., "...whispering as quietly as you possibly can").

### Mode 3: Vocalized Markup

*The markup tag itself is spoken as a word, while the overall tone of the sentence is influenced by the style prompt. This behavior seems to apply to many emotional adjectives.*

- **`[sleepy]`**, **`[curious]`**, **`[surprised]`**, **`[bored]`**, **`[scared]`**, **`[drama]`**  
  - **Reliability:** High for producing the overall tone, but the vocalization of the tag itself is likely an undesired side effect for most use cases.  
  - **Guidance:** Using an evocative phrase is critical for this category. When we used `[scared]` with the phrase "I just heard a window break downstairs," the result was genuinely scared. When used with a neutral phrase, the result was described as "spooky." This shows the model uses the text content to resolve ambiguity.

---

## Key Prompting Strategies: Aligning the Three Pillars

To get the best results from Gemini TTS, you must align the **Style Prompt**, the **Text Content**, and the **Markup Tag**. When these three elements contradict each other, the model will struggle. 

### Poor vs. Better Prompting Examples

**Example 1: The "Amused" Reaction**
- ❌ **Poor Prompt Alignment**: 
  - *Prompt*: "Read the text."
  - *Text*: "`[laughing]` The dog died."
  - *Result*: The model will sound confused or create a forced, inappropriate sound because the text content is sad, the prompt is neutral, but the markup implies amusement.
- ✅ **Better Prompt Alignment**:
  - *Prompt*: "Read the text while reacting with genuine amusement."
  - *Text*: "`[laughing]` I can't believe he actually wore that hat!"
  - *Result*: A natural, cohesive laugh followed by a genuinely amused tone.

**Example 2: The "Whispered Secret"**
- ❌ **Poor Prompt Alignment**: 
  - *Prompt*: "You are giving a speech to a massive crowd."
  - *Text*: "`[whispering]` The meeting is at midnight."
  - *Result*: The model might output a loud "stage whisper" that sounds artificial because the prompt context contradicts the markup tag.
- ✅ **Better Prompt Alignment**:
  - *Prompt*: "You are hiding in a closet and whispering a secret to a friend as quietly as possible."
  - *Text*: "`[whispering]` The meeting is at midnight. Don't tell anyone."
  - *Result*: A convincing, hushed whisper.

---

## Practical Examples of Stage Directions

When generating audiobooks or journalistic content, you often need to insert pauses, hesitations, or tonal shifts. Here is how to combine natural punctuation pacing with affective tags:

1. **Creating a Heavy Pause:** Use ellipses and physical cues immediately after.
   - *Text:* "I looked everywhere for the keys... `[sigh]` They were in my pocket the whole time."
2. **Conveying Doubt or Hesitation:** Use the hesitation non-speech sound inline.
   - *Text:* "I think the suspect went... `[uhm]`... maybe down the alleyway."
3. **Simulating Cynicism or Sarcasm:** Use the modifier tag and descriptive text.
   - *Prompt:* "Read the text with dripping sarcasm and disdain."
   - *Text:* "Oh, great. `[sarcasm]` Another meeting to plan the next meeting."
4. **Sudden Change in Volume:** Use modifier tags on specific phrases.
   - *Text:* "The librarian leaned in closely. `[whispering]` If you look in section four... `[shouting]` but don't touch the red book!"

---

# Markup Reliability Summary

This document categorizes the validated markup tags based on their observed reliability during testing. This can be used to guide future test creation and to quickly select the best tag for a desired effect.

---

## High Reliability

*These tags consistently produce the intended effect, especially when used with a well-aligned style prompt and text content.*

### `[sigh]`, `[laughing]`, `[uhm]`

- **Mode of Operation:** Non-Speech Sound. The markup is replaced with an audible, non-speech vocalization (a sigh, a laugh, a hesitation sound).  
- **Guidance:** The emotional quality of the speech that *follows* the sound is highly dependent on the style prompt. For `[laughing]`, a generic prompt may result in a laugh of shock, while a specific prompt can create a laugh of amusement.

### `[extremely fast]`

- **Mode of Operation:** Modifier for Subsequent Word/Phrase.  
- **Guidance:** Reliably increases the words-per-minute rate of the speech.

### `[shouting]`

- **Mode of Operation:** Modifier for Subsequent Word/Phrase.  
- **Guidance:** Reliably increases volume and intensity to sound like a shout or yell.

### `[sleepy]`, `[curious]`, `[surprised]`

- **Mode of Operation:** Vocalized Markup. The markup tag itself is spoken as a word, while the overall tone of the sentence is influenced by the style prompt.  
- **Guidance:** While the vocalization of the tag may be an undesired side effect, the overall *tone* is produced with high reliability.

---

## Medium Reliability

*These tags work, but may require more specific prompting or produce nuanced results that don't perfectly match the user's intent.*

### `[whispering]`

- **Mode of Operation:** Modifier for Subsequent Word/Phrase.  
- **Guidance:** Creates a "whispery" or breathy quality, but requires an explicit prompt to also lower the volume. The result is often a "stage whisper" rather than a true, quiet whisper.

### `[robotic]`

- **Mode of Operation:** Modifier for Subsequent Word/Phrase.  
- **Guidance:** The modifying effect can be inconsistent in its scope. In some tests, it affected only a single word; in others, it affected the entire phrase.

---

## Low Reliability

*These tags are the most inconsistent. They may produce related but incorrect emotions, or their effect may be highly dependent on context that is difficult to control.*

### `[crying]`, `[bored]`, `[scared]`

- **Mode of Operation:** Modifier for Subsequent Word/Phrase.  
- **Caveat:** These tags can produce related but incorrect emotions (e.g., `[bored]` sounding sarcastic, `[scared]` sounding spooky). Their effectiveness is likely highly dependent on using an evocative phrase in the text itself, rather than a neutral test phrase. Further testing with better text content is needed to improve their reliability.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABkAAAAaCAYAAABCfffNAAADH0lEQVR4Xu2U+09TZxyH/YOWaMJM4JfWTGcpYEtPKe1poRXEBoca75KICPEyBbxH3WbmFhVhi7d4CypGUHRekIvIpazlZkvBihjScnHZnr3nII2irrCftsRP8uRzfnjzffJ+3+TMmfM5/8tcmfs1V+ctRumbGj21yQZuLtBTFZ/I9LOzzvUvdVQJlK5LSeWu3sAjOY37plRq9Uu4JYQ3EhKpitP9O9m5OC23xQCFmgQ9jyWJh8ZUmlzp1NskHkkmOjdmY97+UuW2ODN9xj/mcsICftMmc0+TxH2ltUk0y1Ya08y0uu20ZFsJluZHBVMoZ6fP+mSua3Q8XmSg/h3anHZaM2w8k9Px5Gaglbs+kChMn/XReM/No3phCk/1Ek16U7S9OS48WQ46nDIdDvmTkhmJvBfi8F2eT50+jTaDhVbDZCt0uZfiy3Hyu5D1rMlCKg69Nzx+nZkVJSOxJZ2/fkH3NQ0NRhuNRises4xHkulU20ZPbjbd7iy6ljnR2rvfk9jKZeQzcmxJoCqeQHUig3cstMtiuN2Oz/EhfSuz6M11kbIpqArSdwpOyrjPu2NLBqu1hGp0DNUaGXmSx9izfLqXifUsz1R78jtDbf+GbPpWu5B3vWRpaQjL4RUU1RTHloRqFjN818DIAyvheiev72Qy7tlLb579o/g3u5A2d/HNoRCGwq380Hw8tmS4ThFYiAhBuGE5keZVRFo2EG4s5I/+S/SuTadvnUBtK4FCB4ECB+u/e0FJ+TCnveWxJZOCTCLvCEbbChjz7GLC+z1/DT3geb4kMEe7f7uVghMD7Dg9SIW/MrZESeRJjhCsJPJ0SrCDcd8+xjv28+fQPfxFRvzbDNEOllmEIMiRiy9mJlASacp7K9iiCiZ8ZUz0HGW8vUys7AqBb5MI7E4WPcnA4VQOnB3ghK9i5hIl4YaN4sHFDbxlvOk5wlj7PsJNRbzxX6B/vy5K6EcTrypslP4Smp1gKqMtQtKxV6AIisXKflYlA8cWEjz2FUNnTIROLWFP5Qx+JbESaS5mtP2gKhj8SSvQ8Oq8iZLKWbzB5/yn8je+KckJVer0HAAAAABJRU5ErkJggg==>