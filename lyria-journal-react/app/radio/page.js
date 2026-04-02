'use client';
import { useState, useEffect, useRef } from 'react';

export default function Radio() {
    const [playlist, setPlaylist] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const playerRef = useRef(null);

    useEffect(() => {
        fetch('/api/radio')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    setPlaylist(data.playlist_items);
                } else {
                    setError(data.error || "Erreur lors du chargement");
                }
            })
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (playlist.length > 0 && playerRef.current) {
            playerRef.current.play().catch(e => console.log("Auto-play prevented", e));
        }
    }, [currentIndex, playlist]);

    const playNext = () => {
        if (playlist.length === 0) return;
        setCurrentIndex((prevIndex) => (prevIndex + 1) % playlist.length);
    };

    if (loading) return <p>Chargement...</p>;

    const currentTrack = playlist[currentIndex];

    return (
        <div>
            <h1 className="text-2xl font-bold mb-6 text-center">Radio Lyria 📻</h1>
            <p className="text-center text-gray-600 mb-8">Écoutez les 10 dernières créations à la suite.</p>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                    {error}
                </div>
            )}

            <div className="bg-white p-6 rounded-lg shadow-lg text-center">
                {playlist.length > 0 ? (
                    <>
                        <h3 className="text-xl font-semibold mb-4 text-gray-800">Lecture : {currentTrack.title}</h3>
                        {currentTrack.image && (
                            <img src={currentTrack.image} className="max-h-48 mx-auto mb-4 rounded-lg" alt="Track Cover" />
                        )}
                        <audio
                            ref={playerRef}
                            controls
                            autoPlay
                            className="w-full mb-4"
                            src={currentTrack.url}
                            onEnded={playNext}
                        >
                            Votre navigateur ne supporte pas l'élément audio.
                        </audio>
                        <div>
                            <button onClick={playNext} className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out">
                                Passer à la suivante ⏭️
                            </button>
                        </div>
                    </>
                ) : (
                    <h3 className="text-xl font-semibold mb-4 text-gray-800">Pas assez de pistes pour lancer la radio.</h3>
                )}
            </div>
        </div>
    );
}