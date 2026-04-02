const express = require('express');
const multer = require('multer');
const path = require('path');
const { GoogleGenAI } = require('@google/genai');
const admin = require('firebase-admin');
const { v4: uuidv4 } = require('uuid');

require('dotenv').config();

const app = express();
const port = process.env.PORT || 8080;

// Init Firebase
try {
    const defaultApp = admin.initializeApp({
        credential: admin.credential.applicationDefault(),
        storageBucket: process.env.FIREBASE_STORAGE_BUCKET || `${process.env.GOOGLE_CLOUD_PROJECT}.appspot.com`
    });
} catch (error) {
    if (!/already exists/.test(error.message)) {
        console.error('Firebase initialization error', error.stack);
    }
}
const db = admin.firestore();
const bucket = admin.storage().bucket();

// Init Gemini/Lyria
const ai = new GoogleGenAI({}); // pass empty object to prevent SDK crash

// Setup EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Setup multer for in-memory upload
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

async function generateMusicMetadata(text, file) {
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
    if (file) {
        const base64Data = file.buffer.toString('base64');
        contents.push({
            inlineData: {
                data: base64Data,
                mimeType: file.mimetype
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

async function generateMusic(prompt) {
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

// Routes
app.get('/', (req, res) => {
    res.render('index', { message: null, error: null });
});

app.post('/generate', upload.single('image'), async (req, res) => {
    try {
        const moodText = req.body.mood_text || '';
        const genres = req.body.genres ? (Array.isArray(req.body.genres) ? req.body.genres.join(', ') : req.body.genres) : '';
        const fullMoodText = `${moodText} ${genres ? 'Genres souhaités: ' + genres : ''}`.trim();

        if (!fullMoodText && !req.file) {
            return res.render('index', { message: null, error: "Veuillez fournir un texte ou une image" });
        }

        // 1. Generate Metadata
        const metadata = await generateMusicMetadata(fullMoodText, req.file);

        // 2. Generate Music
        const audioBuffer = await generateMusic(metadata.prompt);

        if (!audioBuffer) {
            return res.render('index', { message: null, error: "Echec de génération audio par Lyria" });
        }

        // 3. Save to Firebase
        const timestamp = Date.now().toString();
        const id = uuidv4();

        const audioPath = `lyria_audio/${timestamp}_${id}.mp4`;
        const audioFile = bucket.file(audioPath);
        await audioFile.save(audioBuffer, {
            contentType: 'audio/mp4',
            public: true
        });
        const audioUrl = audioFile.publicUrl();

        let imageUrl = null;
        if (req.file) {
            const imagePath = `lyria_images/${timestamp}_${id}.jpg`;
            const imageFile = bucket.file(imagePath);
            await imageFile.save(req.file.buffer, {
                contentType: req.file.mimetype,
                public: true
            });
            imageUrl = imageFile.publicUrl();
        }

        const docRef = db.collection('lyria_journal').doc(timestamp);
        await docRef.set({
            prompt: metadata.prompt,
            mood_text: fullMoodText,
            title: metadata.title,
            lyrics: metadata.lyrics,
            audio_url: audioUrl,
            image_url: imageUrl,
            created_at: admin.firestore.FieldValue.serverTimestamp(),
            is_public: true,
            user_id: "anonymous",
            likes_count: 0,
            views_count: 0,
            listens_count: 0
        });

        res.render('index', { message: `Musique "${metadata.title}" générée et publiée !`, error: null });

    } catch (e) {
        console.error(e);
        res.render('index', { message: null, error: `Erreur: ${e.message}` });
    }
});

app.get('/gallery', async (req, res) => {
    try {
        const snapshot = await db.collection('lyria_journal')
            .where('is_public', '==', true)
            .orderBy('created_at', 'desc')
            .limit(20)
            .get();

        const entries = [];
        snapshot.forEach(doc => {
            const data = doc.data();
            entries.push({
                id: doc.id,
                ...data,
                created_at: data.created_at ? data.created_at.toDate() : new Date()
            });
        });

        res.render('gallery', { entries });
    } catch (e) {
        console.error(e);
        res.render('gallery', { entries: [], error: "Erreur d'accès à la base de données." });
    }
});

app.get('/radio', async (req, res) => {
    try {
        const snapshot = await db.collection('lyria_journal')
            .where('is_public', '==', true)
            .orderBy('created_at', 'desc')
            .limit(10)
            .get();

        const entries = [];
        snapshot.forEach(doc => {
            const data = doc.data();
            if (data.audio_url) {
                entries.push({
                    title: data.title || data.mood_text || "Sans titre",
                    url: data.audio_url,
                    image: data.image_url || ""
                });
            }
        });

        res.render('radio', { playlist_items: JSON.stringify(entries) });
    } catch (e) {
        console.error(e);
        res.render('radio', { playlist_items: '[]', error: "Erreur d'accès à la base de données." });
    }
});

if (require.main === module) {
    app.listen(port, "0.0.0.0", () => {
        console.log(`Server listening on port ${port}`);
    });
}

module.exports = app;