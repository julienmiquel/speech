import Link from 'next/link';
import './globals.css';

export default function Layout({ children }) {
    return (
        <html lang="fr">
        <body>
        <div className="bg-gray-100 font-sans text-gray-900 min-h-screen">
            <nav className="bg-white shadow mb-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex space-x-8 items-center">
                            <Link href="/" className="text-xl font-bold text-gray-800">Lyria Journal 🎵</Link>
                            <div className="hidden md:flex space-x-4">
                                <Link href="/" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">Créer</Link>
                                <Link href="/gallery" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">Galerie Publique</Link>
                                <Link href="/radio" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">Radio Lyria</Link>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
            <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pb-10">
                {children}
            </main>
        </div>
        </body>
        </html>
    );
}