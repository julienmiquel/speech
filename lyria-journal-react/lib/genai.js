import { GoogleGenAI } from '@google/genai';
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
const location = process.env.GOOGLE_CLOUD_REGION || 'europe-west1';
let genaiConfig = {};
if (projectId) {
    genaiConfig = { vertexai: { project: projectId, location: location }, project: projectId, location: location };
}
export const ai = new GoogleGenAI(genaiConfig);

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
    const response = await ai.interactions.create({
        model: 'lyria-3-pro-preview',
        input: prompt
    });

    if (response && response.outputs && response.outputs.length > 0) {
        const audioOutput = response.outputs.find(o => o.type === 'audio');
        if (audioOutput && audioOutput.data) {
            return Buffer.from(audioOutput.data, 'base64');
        }
    }
    return null;
}