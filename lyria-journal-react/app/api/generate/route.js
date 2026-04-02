import { NextResponse } from 'next/server';
import { db, bucket, generateMusicMetadata, generateMusic } from '../../../lib/genai';
import admin from 'firebase-admin';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request) {
    try {
        const formData = await request.formData();

        const moodText = formData.get('mood_text') || '';
        const genres = formData.getAll('genres') || [];
        const genresText = genres.length > 0 ? genres.join(', ') : '';
        const fullMoodText = `${moodText} ${genresText ? 'Genres souhaités: ' + genresText : ''}`.trim();

        const imageFile = formData.get('image');
        let fileData = null;
        let mimeType = null;
        let imageBufferForUpload = null;

        if (imageFile && imageFile.size > 0) {
            const arrayBuffer = await imageFile.arrayBuffer();
            imageBufferForUpload = Buffer.from(arrayBuffer);
            fileData = imageBufferForUpload.toString('base64');
            mimeType = imageFile.type;
        }

        if (!fullMoodText && !fileData) {
            return NextResponse.json({ error: "Veuillez fournir un texte ou une image" }, { status: 400 });
        }

        // 1. Generate Metadata
        const metadata = await generateMusicMetadata(fullMoodText, fileData, mimeType);

        // 2. Generate Music
        const audioBuffer = await generateMusic(metadata.prompt);

        if (!audioBuffer) {
            return NextResponse.json({ error: "Echec de génération audio par Lyria" }, { status: 500 });
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
        if (imageBufferForUpload) {
            const imagePath = `lyria_images/${timestamp}_${id}.jpg`;
            const imageFileObj = bucket.file(imagePath);
            await imageFileObj.save(imageBufferForUpload, {
                contentType: mimeType,
                public: true
            });
            imageUrl = imageFileObj.publicUrl();
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
            user_id: "anonymous", // Simplified for this project
            likes_count: 0,
            views_count: 0,
            listens_count: 0
        });

        return NextResponse.json({
            success: true,
            message: `Musique "${metadata.title}" générée et publiée !`,
            data: { title: metadata.title, url: audioUrl }
        });

    } catch (e) {
        console.error(e);
        return NextResponse.json({ error: `Erreur interne: ${e.message}` }, { status: 500 });
    }
}
