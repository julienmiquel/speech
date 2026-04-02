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

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-64">
            <p className="text-gray-500 font-medium">Chargement de la galerie...</p>
        </div>
    );

    return (
        <div>
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-2xl mb-6 text-sm font-medium">
                    {error}
                </div>
            )}

            {entries.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                    <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                    <p className="text-gray-500 font-medium">Aucune création publique trouvée.</p>
                </div>
            ) : (
                <div className="space-y-5 pb-10">
                    {entries.map(entry => (
                        <article key={entry.id} className="bg-white shadow-sm ring-1 ring-gray-100 rounded-3xl overflow-hidden">
                            {entry.image_url && (
                                <div className="w-full aspect-[4/3] bg-gray-100 relative">
                                    <img className="absolute inset-0 w-full h-full object-cover" src={entry.image_url} loading="lazy" alt="Mood image" />
                                </div>
                            )}
                            <div className="p-5">
                                <h2 className="text-lg font-bold text-gray-900 mb-1 leading-tight">{entry.title || 'Sans titre'}</h2>
                                <p className="text-[11px] text-gray-400 font-medium uppercase tracking-wider mb-3">
                                    {new Date(entry.created_at).toLocaleDateString('fr-FR', {day: 'numeric', month: 'short', year: 'numeric'})}
                                </p>

                                {entry.mood_text && (
                                    <p className="text-sm text-gray-600 mb-4 leading-relaxed line-clamp-3">{entry.mood_text}</p>
                                )}

                                <audio controls className="w-full h-10 mt-2 mb-2 rounded-full bg-gray-50 hide-scroll">
                                    <source src={entry.audio_url} type="audio/mp4" />
                                    Votre navigateur ne supporte pas l'élément audio.
                                </audio>

                                {entry.lyrics && (
                                    <details className="mt-3 group">
                                        <summary className="cursor-pointer text-sm font-semibold text-indigo-600 flex items-center outline-none">
                                            <svg className="w-4 h-4 mr-1 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
                                            Paroles
                                        </summary>
                                        <div className="mt-3 bg-gray-50 p-4 rounded-2xl text-[13px] leading-relaxed text-gray-600 font-mono whitespace-pre-wrap">{entry.lyrics}</div>
                                    </details>
                                )}
                            </div>
                        </article>
                    ))}
                </div>
            )}
        </div>
    );
}
