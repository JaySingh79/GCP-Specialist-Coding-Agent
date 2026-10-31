import urllib.request
import xml.etree.ElementTree as ET

url = 'https://news.google.com/rss/search?q=India+tax+changes+news+2025&hl=en-IN&gl=IN&ceid=IN:en'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    xml_data = urllib.request.urlopen(req).read()
    root = ET.fromstring(xml_data)
    items = root.findall('.//item')[:8]
    for i, item in enumerate(items, 1):
        title = item.find('title').text if item.find('title') is not None else 'No title'
        link = item.find('link').text if item.find('link') is not None else 'No link'
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No date'
        print(f"{i}. {title}")
        print(f"   Date: {pub_date}")
        print(f"   Link: {link}\n")
except Exception as e:
    print("Error fetching news:", e)
