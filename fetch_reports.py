import urllib.request
import json

url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=Paytm+annual+report&format=json"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for item in data.get('query', {}).get('search', []):
            print(item['title'], ':', item.get('snippet', ''))
except Exception as e:
    print("Error:", e)
