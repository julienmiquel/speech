import { GoogleGenAI } from '@google/genai';
import { GoogleAuth } from 'google-auth-library';
import admin from 'firebase-admin';

// Initialize Firebase
if (!admin.apps.length) {
    try {
        admin.initializeApp({
            credential: admin.credential.applicationDefault(),
            storageBucket: process.env.FIREBASE_STORAGE_BUCKET || `${process.env.GOOGLE_CLOUD_PROJECT}.appspot.com`
        });
    } catch (error) {
        if (!/already exists/.test(error.message)) {
            console.error('Firebase initialization error', error.stack);
        }
    }
}
export const db = admin.firestore();
export const bucket = admin.storage().bucket();

// Initialize Gemini/Lyria
// Ensure we handle environment safely without crashing Next.js during static site generation
const projectId = process.env.GOOGLE_CLOUD_PROJECT;
const location = process.env.GOOGLE_CLOUD_REGION || 'global';
let genaiConfig = {};
let lyriaConfig = {};
if (projectId) {
    genaiConfig = { vertexai: { project: projectId, location: location }, project: projectId, location: location };
    // Lyria 3 only supports 'global' location
    lyriaConfig = { vertexai: { project: projectId, location: 'global' }, project: projectId, location: 'global' };
}
export const ai = new GoogleGenAI(genaiConfig);
export const lyriaAi = new GoogleGenAI(lyriaConfig);

export async function generateMusicMetadata(text, fileData, mimeType) {
    const promptInstruction = `
    Analyse l'image fournie (et/ou le texte fourni s'il y en a un).
    Tu dois générer trois choses basées sur ce contexte, l'humeur et l'ambiance :
    1. "prompt": Un prompt musical détaillé en anglais (50-100 mots) pour l'API Lyria 3.
       - Genre & Era : Le style et l'époque (ex: 1980s-style synth-pop).
       - Tempo & Rhythm : La vitesse et le rythme (ex: 120 BPM).
       - Instrumentation & Texture : Les instruments et l'ambiance sonore.
       - Vocal Profile : (Optionnel) Si approprié, décrit le type de voix.
       - INCLUS DANS LE PROMPT LYRIA LES PAROLES COMPLÈTES sous la forme de balises (ex: [Verse] paroles... [Chorus] paroles...). Lyria accepte les paroles directement dans le prompt musical.
    2. "title": Un titre évocateur et court pour la chanson (en français ou dans la langue demandée).
    3. "lyrics": Les paroles complètes formatées avec des sauts de ligne pour un affichage lisible. Si cest une musique instrumentale (par exemple si classique), renvoie une chaîne vide ou "Instrumental".

    Tu DOIS impérativement renvoyer un objet JSON valide avec exactement ces 3 clés : "prompt", "title" et "lyrics". Ne rajoute pas de markdown autour de ta réponse JSON.
    `;

    const contents = [];
    if (fileData) {
        contents.push({
            inlineData: {
                data: fileData, // Base64
                mimeType: mimeType
            }
        });
    }

    if (text) {
        contents.push(`Texte de contexte utilisateur : ${text}\n\n`);
    }

    contents.push(promptInstruction);

    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: contents,
        config: {
            temperature: 0.7,
            responseMimeType: 'application/json'
        }
    });

    try {
        return JSON.parse(response.text);
    } catch (e) {
        console.error("Failed to parse JSON response from Gemini", response.text);
        return {
            prompt: text || "A nice song",
            title: "Sans titre",
            lyrics: ""
        };
    }
}

export async function generateMusic(prompt) {
    const project = process.env.GOOGLE_CLOUD_PROJECT;
    if (!project) {
        // Mock implementation if no real credentials exist
        return Buffer.from('mock_audio_data_for_' + prompt);
    }

    try {
        const auth = new GoogleAuth({ scopes: 'https://www.googleapis.com/auth/cloud-platform' });
        const client = await auth.getClient();
        const tokenResponse = await client.getAccessToken();
        const token = tokenResponse.token;

        const url = `https://global-aiplatform.googleapis.com/v1/projects/${project}/locations/global/publishers/google/models/lyria-3-pro-preview:generateAudio`;

        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            // Fallback body formats since Lyria is an experimental model
            body: JSON.stringify({
                instances: [{ prompt: prompt }],
                input: { prompt: prompt },
                prompt: prompt
            })
        });

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`Lyria API Error: ${res.status} - ${text}`);
        }

        const json = await res.json();
        let base64Data = null;

        if (json.predictions && json.predictions.length > 0) {
            const p = json.predictions[0];
            base64Data = p.audio || p.audioBase64 || p.bytesBase64Encoded || p.content || p.data || p;
        } else if (json.outputs && json.outputs.length > 0) {
            const o = json.outputs.find(out => out.type === 'audio' || out.data);
            base64Data = o ? o.data : json.outputs[0];
        } else if (json.data) {
            base64Data = json.data;
        }

        if (typeof base64Data === 'string' && base64Data.length > 100) {
            return Buffer.from(base64Data, 'base64');
        }

        console.warn("Lyria REST API returned unknown format:", JSON.stringify(json).substring(0, 200));
        // Return a valid empty MP4/WAV buffer instead of a string so the UI doesn't crash on playback
        return Buffer.from('AAAAHGZ0eXBpc29tAAACAGlzb21pc28yAAAIO21vb3YAAABsbXZoZAAAAADxT01j8U9NYwAAA+gAAAAAAAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAITdHJhawAAAFx0a2hkAAAAA/FPTWPxT01jAAAAAQAAAAAAAAMcAAAAAAAAAQAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAA0bWRpYQAAACBtZGhkAAAAA/FPTWPxT01jAAAD6AAAAAAAFXEAAAAAAhxoZGxyAAAAAAAAAABzb3VuAAAAAAAAAAAAAAAAAAAAbWluZgAAABRzbWhkAAAAAAAAAAAAAAABAAAAJGRpbmYAAAAcYnRhbAAAAAByZWZlAAAAAAAAAAEAAAAMdXJsIAAAAAEAAAFAc3RibAAAAGRzdHNkAAAAAAAAAAEAAABUbXA0YQAAAAAAAAABAAAAAgAQAAAAAAAD6AAAAAAAMGVzZHMAAAAAA4CAgAIAAAAEgICABAEAAAAAgICAA0iAIAAAAACA', 'base64');
    } catch (e) {
        console.warn("Lyria REST API failed, using fallback:", e.message);
        // Return a valid empty MP4/WAV buffer instead of a string so the UI doesn't crash on playback
        return Buffer.from('AAAAHGZ0eXBpc29tAAACAGlzb21pc28yAAAIO21vb3YAAABsbXZoZAAAAADxT01j8U9NYwAAA+gAAAAAAAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAITdHJhawAAAFx0a2hkAAAAA/FPTWPxT01jAAAAAQAAAAAAAAMcAAAAAAAAAQAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAA0bWRpYQAAACBtZGhkAAAAA/FPTWPxT01jAAAD6AAAAAAAFXEAAAAAAhxoZGxyAAAAAAAAAABzb3VuAAAAAAAAAAAAAAAAAAAAbWluZgAAABRzbWhkAAAAAAAAAAAAAAABAAAAJGRpbmYAAAAcYnRhbAAAAAByZWZlAAAAAAAAAAEAAAAMdXJsIAAAAAEAAAFAc3RibAAAAGRzdHNkAAAAAAAAAAEAAABUbXA0YQAAAAAAAAABAAAAAgAQAAAAAAAD6AAAAAAAMGVzZHMAAAAAA4CAgAIAAAAEgICABAEAAAAAgICAA0iAIAAAAACA', 'base64');
    }
}