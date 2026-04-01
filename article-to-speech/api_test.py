import requests

API_URL = "https://article-to-speech-api-59602385614.europe-west9.run.app"
print("Testing /extract...")
r = requests.post(f"{API_URL}/extract", json={"url": "https://www.lemonde.fr/planete/article/2026/03/23/l-exemple-de-vancouver_61655_3244.html", "method": "bs4"})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(f"Text snippet: {r.json().get('text', '')[:100]}...")
