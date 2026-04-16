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

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-64">
            <p className="text-gray-500 font-medium">Chargement de la radio...</p>
        </div>
    );

    const currentTrack = playlist[currentIndex];

    return (
        <div className="flex flex-col items-center justify-center w-full min-h-[calc(100vh-140px)]">
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-2xl w-full text-sm font-medium mb-6">
                    {error}
                </div>
            )}

            <div className="w-full flex flex-col items-center">
                {playlist.length > 0 ? (
                    <>
                        <div className="relative w-64 h-64 mb-10 rounded-3xl bg-gray-100 overflow-hidden album-art-shadow">
                            {currentTrack.image ? (
                                <img src={currentTrack.image} className="absolute inset-0 w-full h-full object-cover transition-opacity duration-500" alt="Track Cover" />
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-indigo-50 to-blue-50 text-indigo-200">
                                    <svg className="w-24 h-24" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"></path></svg>
                                </div>
                            )}
                        </div>

                        <h3 className="text-2xl font-bold tracking-tight text-gray-900 text-center line-clamp-2 mb-2 w-full px-4">
                            {currentTrack.title || "Sans titre"}
                        </h3>
                        <p className="text-sm font-medium text-gray-500 uppercase tracking-widest mb-10">Lyria Radio</p>

                        <audio
                            ref={playerRef}
                            controls
                            autoPlay
                            className="w-full mb-8 h-10 hide-scroll"
                            src={currentTrack.url}
                            onEnded={playNext}
                        >
                            Votre navigateur ne supporte pas l'élément audio.
                        </audio>

                        <button onClick={playNext} className="flex items-center justify-center w-16 h-16 rounded-full bg-white text-gray-800 shadow-sm ring-1 ring-gray-200 hover:bg-gray-50 hover:scale-105 active:scale-95 transition-all duration-200">
                            <svg className="w-6 h-6 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                        </button>
                    </>
                ) : (
                    <div className="flex flex-col items-center justify-center h-64 text-center">
                        <h3 className="text-xl font-semibold mb-4 text-gray-800">Pas assez de pistes pour lancer la radio.</h3>
                    </div>
                )}
            </div>
        </div>
    );
}
