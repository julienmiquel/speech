import { NextResponse } from 'next/server';
import { db } from '../../../lib/genai';

export async function GET(request) {
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
                created_at: data.created_at ? data.created_at.toDate().toISOString() : new Date().toISOString()
            });
        });

        return NextResponse.json({ success: true, entries });
    } catch (e) {
        console.error(e);
        return NextResponse.json({ error: "Erreur d'accès à la base de données." }, { status: 500 });
    }
}