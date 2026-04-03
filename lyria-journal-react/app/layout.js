'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './globals.css';

export default function Layout({ children }) {
    const pathname = usePathname();

    return (
        <html lang="fr">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <script src="https://accounts.google.com/gsi/client" async defer></script>
        </head>
        <body className="bg-gray-50 text-gray-900 pb-20 selection:bg-blue-100">
            {/* Sticky Header */}
            <header className="glass-nav fixed top-0 w-full z-50 h-14 flex items-center justify-center">
                <h1 className="text-lg font-bold tracking-tight text-gray-800">
                    {pathname === '/' && <>Lyria Journal <span className="text-xl">🎵</span></>}
                    {pathname === '/gallery' && <>Galerie Publique <span className="text-xl">✨</span></>}
                    {pathname === '/radio' && <>Radio Lyria <span className="text-xl">📻</span></>}
                </h1>
            </header>

            {/* Main Content (constrained for mobile) */}
            <main className="max-w-md mx-auto pt-20 pb-6 px-4">
                {children}
            </main>

            {/* Bottom Navigation */}
            <nav className="glass-bottom fixed bottom-0 w-full pb-safe z-50">
                <div className="flex justify-around items-center h-16 max-w-md mx-auto px-6">
                    <Link href="/" className={`flex flex-col items-center justify-center w-16 transition-colors ${pathname === '/' ? 'text-blue-600' : 'text-gray-400 hover:text-gray-900'}`}>
                        <svg className="w-6 h-6 mb-1" fill={pathname === '/' ? 'currentColor' : 'none'} stroke={pathname === '/' ? 'none' : 'currentColor'} viewBox="0 0 24 24">
                            {pathname === '/' ? (
                                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                            )}
                        </svg>
                        <span className={`text-[10px] ${pathname === '/' ? 'font-semibold' : 'font-medium'}`}>Créer</span>
                    </Link>

                    <Link href="/gallery" className={`flex flex-col items-center justify-center w-16 transition-colors ${pathname === '/gallery' ? 'text-blue-600' : 'text-gray-400 hover:text-gray-900'}`}>
                        <svg className="w-6 h-6 mb-1" fill={pathname === '/gallery' ? 'currentColor' : 'none'} stroke={pathname === '/gallery' ? 'none' : 'currentColor'} viewBox={pathname === '/gallery' ? '0 0 20 20' : '0 0 24 24'}>
                            {pathname === '/gallery' ? (
                                <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"></path>
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            )}
                        </svg>
                        <span className={`text-[10px] ${pathname === '/gallery' ? 'font-semibold' : 'font-medium'}`}>Galerie</span>
                    </Link>

                    <Link href="/radio" className={`flex flex-col items-center justify-center w-16 transition-colors ${pathname === '/radio' ? 'text-blue-600' : 'text-gray-400 hover:text-gray-900'}`}>
                        <svg className="w-6 h-6 mb-1" fill={pathname === '/radio' ? 'currentColor' : 'none'} stroke={pathname === '/radio' ? 'none' : 'currentColor'} viewBox={pathname === '/radio' ? '0 0 20 20' : '0 0 24 24'}>
                            {pathname === '/radio' ? (
                                <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.28l8-1.6V11.114A4.369 4.369 0 0015 11c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z"></path>
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
                            )}
                        </svg>
                        <span className={`text-[10px] ${pathname === '/radio' ? 'font-semibold' : 'font-medium'}`}>Radio</span>
                    </Link>
                </div>
            </nav>
        </body>
        </html>
    );
}
