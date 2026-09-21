import urllib.request
import json

def get_wikipedia_info(query: str):
    try:
        # Format the query for the Wikipedia API URL
        encoded_query = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded_query}&prop=extracts&exintro=True&explaintext=True&format=json&formatversion=2"

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MyWikipediaApp/1.0 (sriya13121@gmail.com)"}
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data['query']['pages'][0]['extract']
    
    except Exception as e:
        return f"An error occured while querying for {query}: {str(e)}"
    
    
get_wikipedia_info_function = {
    "type": "function",
    "name": "get_wikipedia_info",
    "description": "Gets wikipedia information regarding the query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The topic/thing/being for which the information is needed",
            }
        },
        "required": ["query"],
    },
}
