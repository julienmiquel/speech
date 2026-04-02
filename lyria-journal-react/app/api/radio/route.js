import { NextResponse } from 'next/server';
import { db } from '../../../lib/genai';

export async function GET(request) {
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

        return NextResponse.json({ success: true, playlist_items: entries });
    } catch (e) {
        console.error(e);
        return NextResponse.json({ error: "Erreur d'accès à la base de données." }, { status: 500 });
    }
}