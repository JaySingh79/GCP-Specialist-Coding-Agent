import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'SampleCompany AdminContact@sampledomain.com'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        gaap = data['facts']['us-gaap']
        if 'RevenueFromContractWithCustomerExcludingAssessedTax' in gaap:
            revs = gaap['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD']
            # Filter for entries where form is 10-Q or 10-K and sort by filed date
            revs = sorted(revs, key=lambda x: (x.get('filed', ''), x.get('end', '')), reverse=True)
            for entry in revs:
                if entry.get('form') in ['10-Q', '10-K']:
                    # Check if it's a quarterly span (roughly 80-100 days)
                    start = entry.get('start')
                    end = entry.get('end')
                    val = entry.get('val')
                    form = entry.get('form')
                    filed = entry.get('filed')
                    if start:
                        print(f"Form: {form}, Filed: {filed}, Start: {start}, End: {end}, Val: {val}")
except Exception as e:
    print(f"Error: {e}")
