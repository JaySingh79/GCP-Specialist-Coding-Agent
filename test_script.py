import urllib.request
import json

try:
    url = "https://api.duckduckgo.com/?q=OpenAI+revenue+growth+quarterly&format=json"
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode())
    print("OpenAI DDG Abstract:", data.get("AbstractText"))
    for r in data.get("RelatedTopics", [])[:3]:
        print("-", r.get("Text"))
except Exception as e:
    print("Error:", e)
