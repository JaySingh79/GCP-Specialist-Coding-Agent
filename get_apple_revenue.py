import urllib.request
import json

url = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=financialData,incomeStatementHistoryQuarterly"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=2)[:1000])
except Exception as e:
    print("Error:", e)
