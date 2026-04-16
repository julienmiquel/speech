const request = require('supertest');
const app = require('./server');

jest.mock('@google/genai', () => {
    return {
        GoogleGenAI: jest.fn().mockImplementation(() => ({
            models: {
                generateContent: jest.fn().mockResolvedValue({
                    text: JSON.stringify({
                        prompt: "1980s synth-pop, 120 BPM, heavy bassline, female vocals",
                        title: "Synth Dreams",
                        lyrics: "[Verse] Hello world"
                    })
                })
            },
            interactions: {
                create: jest.fn().mockResolvedValue({
                    outputs: [{ type: 'audio', data: Buffer.from('fake_audio').toString('base64') }]
                })
            }
        }))
    };
});

jest.mock('firebase-admin', () => {
    const firestoreMock = {
        collection: jest.fn().mockReturnThis(),
        doc: jest.fn().mockReturnThis(),
        set: jest.fn().mockResolvedValue(true),
        where: jest.fn().mockReturnThis(),
        orderBy: jest.fn().mockReturnThis(),
        limit: jest.fn().mockReturnThis(),
        get: jest.fn().mockResolvedValue({
            forEach: jest.fn()
        })
    };
    const bucketMock = {
        file: jest.fn().mockReturnValue({
            save: jest.fn().mockResolvedValue(true),
            publicUrl: jest.fn().mockReturnValue('http://fake-url.com/file')
        })
    };

    return {
        initializeApp: jest.fn(),
        credential: { applicationDefault: jest.fn() },
        firestore: Object.assign(jest.fn(() => firestoreMock), { FieldValue: { serverTimestamp: jest.fn() } }),
        storage: jest.fn(() => ({ bucket: jest.fn(() => bucketMock) }))
    };
});

describe('Node.js Lyria Journal API', () => {
    it('should render the index page', async () => {
        const res = await request(app).get('/');
        expect(res.statusCode).toEqual(200);
        expect(res.text).toContain("Capturez l'instant");
    });

    it('should handle /generate with text only', async () => {
        const res = await request(app)
            .post('/generate')
            .field('mood_text', 'Happy day');

        expect(res.statusCode).toEqual(200);
        expect(res.text).toContain('générée et publiée');
    });
});
