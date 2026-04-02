'use client';
import { useState, useEffect } from 'react';

export default function Gallery() {
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetch('/api/gallery')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    setEntries(data.entries);
                } else {
                    setError(data.error || "Erreur lors du chargement");
                }
            })
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <p>Chargement...</p>;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6">Galerie Publique</h1>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                    {error}
                </div>
            )}

            {entries.length === 0 ? (
                <p className="text-gray-600">Aucune création publique trouvée.</p>
            ) : (
                <div className="space-y-6">
                    {entries.map(entry => (
                        <div key={entry.id} className="bg-white shadow rounded-lg p-6 flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-6">
                            {entry.image_url && (
                                <div className="flex-shrink-0">
                                    <img className="h-32 w-32 object-cover rounded-md mx-auto sm:mx-0" src={entry.image_url} alt="Mood image" />
                                </div>
                            )}
                            <div className="flex-1 min-w-0">
                                <h2 className="text-xl font-semibold mb-1 truncate">🎵 {entry.title || 'Sans titre'}</h2>
                                <p className="text-sm text-gray-500 mb-2">Posté le: {new Date(entry.created_at).toLocaleString()}</p>

                                {entry.mood_text && (
                                    <p className="text-gray-700 mb-2"><strong>Contexte:</strong> {entry.mood_text}</p>
                                )}

                                <audio controls className="w-full mt-4">
                                    <source src={entry.audio_url} type="audio/mp4" />
                                    Votre navigateur ne supporte pas l'élément audio.
                                </audio>

                                {entry.lyrics && (
                                    <details className="mt-4">
                                        <summary className="cursor-pointer text-blue-600 hover:underline">📝 Paroles</summary>
                                        <div className="mt-2 bg-gray-50 p-4 rounded text-sm text-gray-700 whitespace-pre-wrap">{entry.lyrics}</div>
                                    </details>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}