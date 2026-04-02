import { POST } from '../app/api/generate/route';

jest.mock('../lib/genai', () => ({
    db: {
        collection: jest.fn().mockReturnThis(),
        doc: jest.fn().mockReturnThis(),
        set: jest.fn().mockResolvedValue(true)
    },
    bucket: {
        file: jest.fn().mockReturnValue({
            save: jest.fn().mockResolvedValue(true),
            publicUrl: jest.fn().mockReturnValue('http://fake-url.com/file')
        })
    },
    generateMusicMetadata: jest.fn().mockResolvedValue({
        prompt: "1980s synth-pop",
        title: "Test Song",
        lyrics: "Test Lyrics"
    }),
    generateMusic: jest.fn().mockResolvedValue(Buffer.from('fake_audio'))
}));

jest.mock('firebase-admin', () => ({
    apps: ['mock'],
    firestore: {
        FieldValue: { serverTimestamp: jest.fn() }
    }
}));

jest.mock('uuid', () => ({
    v4: jest.fn(() => '1234-5678')
}));

describe('/api/generate', () => {
    it('returns error if no input provided', async () => {
        const req = {
            formData: async () => {
                const map = new Map();
                map.getAll = () => [];
                return map;
            }
        };

        const response = await POST(req);
        const data = await response.json();

        expect(response.status).toBe(400);
        expect(data.error).toBe('Veuillez fournir un texte ou une image');
    });

    it('processes successfully with text', async () => {
        const req = {
            formData: async () => {
                const map = new Map();
                map.set('mood_text', 'Happy day');
                map.getAll = () => [];
                return map;
            }
        };

        const response = await POST(req);
        const data = await response.json();

        expect(response.status).toBe(200);
        expect(data.success).toBe(true);
        expect(data.message).toContain('générée et publiée');
    });
});