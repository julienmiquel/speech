import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def generate_rss():
    if not firebase_admin._apps:
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        except Exception as e:
            return f"<!-- Failed to initialize Firebase: {e} -->\n<error>Failed to initialize Firebase</error>"

    try:
        db = firestore.client()
        entries = db.collection('lyria_journal').where('is_public', '==', True).order_by('created_at', direction=firestore.Query.DESCENDING).limit(10).stream()

        rss_items = ""
        for entry in entries:
            data = entry.to_dict()
            title = data.get('title')
            if not title:
                title = data.get('mood_text', 'Musique Lyria')
            if not title:
                title = "Musique Lyria"
            url = data.get('audio_url', '')
            date_str = data.get('created_at').strftime('%a, %d %b %Y %H:%M:%S GMT') if data.get('created_at') else ''
            desc = data.get('lyrics', '')
            if not desc:
                desc = data.get('prompt', 'Généré par Lyria Journal')

            rss_items += f"""
        <item>
            <title><![CDATA[{title}]]></title>
            <link>{url}</link>
            <description><![CDATA[{desc}]]></description>
            <pubDate>{date_str}</pubDate>
            <enclosure url="{url}" type="audio/mp4" />
        </item>
"""

        rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>Lyria Journal Radio</title>
        <link>https://lyria-journal.example.com</link>
        <description>Les 10 dernières créations musicales de la communauté Lyria Journal</description>
{rss_items}
    </channel>
</rss>
"""
        return rss
    except Exception as e:
        return f"<error>{str(e)}</error>"

if __name__ == "__main__":
    print(generate_rss())
