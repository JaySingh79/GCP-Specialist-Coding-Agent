import urllib.request
import json

url = "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=3mo&interval=1d"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        meta = data['chart']['result'][0]['meta']
        print(f"Symbol: {meta.get('symbol')}")
        print(f"Regular Market Price: {meta.get('regularMarketPrice')}")
        print(f"Currency: {meta.get('currency')}")
except Exception as e:
    print(f"Error: {e}")
