import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {    
    "Authorization": f"Bearer {os.getenv("HF_TOKEN")}",
    'Content-Type': 'application/json',
}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

response = query({
    "messages": [
        {
            "role": "user",
            "content": "Give me a long list of commands to execute a db migration from MongoDB to BigQuery?"
        }
    ],
    "model": "Qwen/Qwen3-Coder-Next:novita"
})

output = response["choices"][0]["message"]['content']
print(output)