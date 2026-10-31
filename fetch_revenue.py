import urllib.request
import json

url = "https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=financialData,incomeStatementHistory"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)
