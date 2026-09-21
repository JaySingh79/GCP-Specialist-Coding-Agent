from tavily import TavilyClient
from dotenv import load_dotenv
from typing import Literal
from google import genai
import json
import os 

load_dotenv()

def get_web_results(query:str):
    
    tavily_client = TavilyClient()
    response = tavily_client.search(query, max_results=8)

    result = {'response': response}
    with open('testin.json', 'w') as f:
        f.write(json.dumps(result))

    # print(response)
    return response['results']


    
get_web_results_function = {
    "type": "function",
    "name": "get_web_results",
    "description": "Gets the content of a file.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The topic/personality/object that you need information about.",
            }
        },
        "required": ["query"],
    },
}


# print(get_web_results("Who is Hannibal Lectar"))


def crawl_webpage(url: str, instruction: str):
    
    print(f"\n\nCrawling {url}\n\n", 100*"-")
    tavily_client = TavilyClient()
    try:
        
        response = tavily_client.crawl(url, instructions=instruction)
        result = {'response': response}
        with open('crawl_testing.json', 'w') as f:
            f.write(json.dumps(result))
        
        text_content = [content['raw_content'] for content in response['results'] if content['raw_content']]
        return text_content
    
    except Exception as e:
        return f" An error occured while processing: {e}"
    
        # print(response)
    
    ## ranking
    
    
    
def reranker(text_content: list):
    
    system_prompt = f"""
        ## Identity
        You are worlds most powerfull reranker model.
        
        ## Task
        You have to rank the <input> list of content pieces as per highest relevance. Return top 3 results.

        ## Input
        input: 
        
    """
    
    client = genai.Client()
    
    response = client.interactions.create(
                model="gemini-3.5-flash-lite",
                input=f"{text_content}",
                system_instruction=system_prompt,
            )
    
crawl_webpage_function = {
    "type": "function",
    "name": "crawl_webpage",
    "description": "Gets the content of a file.",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The url to be crawled",
            },
            "instructions": {
                "type": "string",
                "description": "Some necessary instructions to get precise crawled results.",
            },
        },
        "required": ["url", "instructions"],
    },
}


import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://stackoverflow.com/questions/76105489/problems-deploying-cloud-functions-on-gcp",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())

# print(crawl_webpage(url="", instruction="all relvant information"))