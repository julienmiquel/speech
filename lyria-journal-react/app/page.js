'use client';
import { useState, useEffect } from 'react';

export default function Home() {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [idToken, setIdToken] = useState('');
    const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

    useEffect(() => {
        if (googleClientId && typeof window !== 'undefined' && window.google) {
            window.google.accounts.id.initialize({
                client_id: googleClientId,
                callback: (response) => {
                    setIdToken(response.credential);
                }
            });
            window.google.accounts.id.renderButton(
                document.getElementById('googleSignInBtn'),
                { theme: 'outline', size: 'large', text: 'signin_with', shape: 'rectangular' }
            );
        }
    }, [googleClientId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        setError('');

        const formData = new FormData(e.target);
        if (idToken) {
            formData.append('id_token', idToken);
        }

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

    const genres = [
        "Joyeux", "Mélancolique", "Chanson française", "Chanson en anglais",
        "Pop rock", "Hard rock", "Heavy metal", "Hip-hop", "Slam", "Électro",
        "Jazz", "Musique classique", "Jumpstyle", "Synthwave", "Reggae",
        "Lo-Fi Hip Hop", "Country", "Dubstep"
    ];

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-2xl font-bold tracking-tight text-gray-900">Capturez l'instant</h2>
                <p className="text-sm text-gray-500 mt-1">Votre journal musical et visuel.</p>
            </div>

            {message && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-2xl mb-6 text-sm font-medium">
                    {message}
                </div>
            )}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-2xl mb-6 text-sm font-medium">
                    {error}
                </div>
            )}

            {googleClientId && !idToken && (
                <div className="mb-6 flex justify-center">
                    <div id="googleSignInBtn"></div>
                </div>
            )}

            <form onSubmit={handleSubmit} className={`bg-white shadow-sm ring-1 ring-gray-100 rounded-3xl p-5 mb-4 ${googleClientId && !idToken ? 'opacity-50 pointer-events-none' : ''}`}>

                <div className="mb-5">
                    <label className="block text-sm font-semibold text-gray-700 mb-2" htmlFor="image">
                        Photo (Optionnel)
                    </label>
                    <div className="relative group">
                        <input type="file" name="image" id="image" accept="image/png, image/jpeg, image/jpg" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" />
                        <div className="w-full flex items-center justify-center px-4 py-4 border-2 border-dashed border-gray-200 rounded-2xl bg-gray-50 group-hover:bg-gray-100 transition-colors">
                            <div className="text-center">
                                <svg className="mx-auto h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <span className="mt-2 block text-xs font-medium text-gray-600">Appuyez pour choisir</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mb-5">
                    <label className="block text-sm font-semibold text-gray-700 mb-2" htmlFor="mood_text">
                        Mood du jour
                    </label>
                    <textarea
                        className="w-full bg-gray-50 border border-gray-200 text-gray-800 text-sm rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent block p-3 transition duration-150 ease-in-out resize-none"
                        id="mood_text"
                        name="mood_text"
                        rows={3}
                        placeholder="ex: Matinée difficile, besoin d'énergie..."
                    ></textarea>
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                        Genres musicaux
                    </label>
                    <div className="flex flex-wrap gap-2">
                        {genres.map(genre => (
                            <label key={genre} className="cursor-pointer">
                                <input type="checkbox" name="genres" value={genre} className="peer sr-only" />
                                <div className="rounded-full px-4 py-1.5 text-xs font-medium bg-gray-100 text-gray-600 peer-checked:bg-blue-600 peer-checked:text-white transition-all duration-200">
                                    {genre}
                                </div>
                            </label>
                        ))}
                    </div>
                </div>

                <button
                    disabled={loading || (googleClientId && !idToken)}
                    className={`w-full text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 font-semibold rounded-2xl text-sm px-5 py-3.5 text-center transition-all duration-200 shadow-sm active:scale-95 ${loading || (googleClientId && !idToken) ? 'opacity-70 cursor-not-allowed scale-95' : ''}`}
                    type="submit"
                >
                    {loading ? 'Création en cours...' : 'Générer avec Lyria'}
                </button>
            </form>
        </div>
    );
}
