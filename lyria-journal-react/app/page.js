'use client';
import { useState } from 'react';

export default function Home() {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        setError('');

        const formData = new FormData(e.target);

        try {
            const res = await fetch('/api/generate', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                setMessage(data.message);
                e.target.reset();
            } else {
                setError(data.error || "Une erreur est survenue");
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const genres = ["Joyeux", "Mélancolique", "Chanson française", "Chanson en anglais", "Pop rock", "Hard rock", "Heavy metal", "Hip-hop", "Slam", "Électro", "Jazz", "Musique classique"];

    return (
        <div>
            <h1 className="text-2xl font-bold mb-2">Capturez votre Daily Mood</h1>
            <p className="text-gray-600 mb-6">Votre journal intime musical et visuel.</p>

            {message && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
                    {message}
                </div>
            )}
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="image">
                        Image (Optionnel)
                    </label>
                    <input type="file" name="image" id="image" accept="image/png, image/jpeg, image/jpg" className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
                </div>

                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="mood_text">
                        Ajoutez un court texte ou légende (Optionnel)
                    </label>
                    <input className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="mood_text" name="mood_text" type="text" placeholder="ex: Matinée difficile" />
                </div>

                <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-bold mb-2">
                        Genres musicaux (Optionnel)
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                        {genres.map(genre => (
                            <label key={genre} className="inline-flex items-center">
                                <input type="checkbox" name="genres" value={genre} className="form-checkbox text-blue-600" />
                                <span className="ml-2 text-sm text-gray-700">{genre}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button disabled={loading} className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full ${loading ? 'opacity-50 cursor-not-allowed' : ''}`} type="submit">
                        {loading ? 'Création en cours...' : 'Générer ma musique avec Lyria'}
                    </button>
                </div>
            </form>
        </div>
    );
}