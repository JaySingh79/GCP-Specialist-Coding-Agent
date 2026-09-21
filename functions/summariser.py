import requests
from dotenv import load_dotenv
import os

load_dotenv()

# {
#   "id": "resp_1234567890",
#   "object": "response",
#   "created_at": 1234567890,
#   "model": "openai/o4-mini",
#   "output": [
#     {
#       "type": "message",
#       "id": "msg_abc123",
#       "status": "completed",
#       "role": "assistant",
#       "content": [
#         {
#           "type": "output_text",
#           "text": "The meaning of life is a philosophical question that has been pondered for centuries...",
#           "annotations": []
#         }
#       ]
#     }
#   ],
#   "usage": {
#     "input_tokens": 12,
#     "output_tokens": 45,
#     "total_tokens": 57
#   },
#   "status": "completed"
# }


def get_summerized_content(input_content):


    url = "https://openrouter.ai/api/v1/chat/completions"
    url_responses = "https://openrouter.ai/api/v1/responses"
    
    # headers = {
    # "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    # "Content-Type": "application/json"
    # }

    # payload = {
    # "model": "openai/gpt-3.5-turbo",
    # "messages": [{"role": "user", "content": content}],
    # "stream": True
    # }
    
    content = f"""
        ## Role
        You are an expert English PHD.
        
        ## Task
        You goal is to best summarise the below <content> in strictly less that 200 words.
        
        ## Instructions
        Do not add any other words like "here is your summary", "provided below is short version..", etc.
        Only return the summarised version of <content>
    
        ## Input
        content:
        {input_content}
    """
    

    try:        
        response = requests.post(
                url_responses,
                headers={
                    'Authorization': f'Bearer {os.getenv('OPENROUTER_API_KEY')}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'openai/gpt-oss-20b',
                    'input': content,
                    'max_output_tokens': 2000,
                },
                
            )

    except Exception as e:
        return f"An error occured while processing : {e}"
    
    
    result = response.json()
    # with open('testing.json', 'w') as f:
    #     f.write(json.dumps(result))
        
    # response = requests.post(url, headers=headers, json=payload, stream=True)
    return result['output'][1]['content'][0]['text']
    # return result


# print(summerize_content(inpit_bro))

get_summerized_content_function = {
    "type": "function",
    "name": "get_summerized_content",
    "description": "Summarises the input content.",
    "parameters": {
        "type": "object",
        "properties": {
            "input_content": {
                "type": "string",
                "description": "The input content to be summarised.",
            }
        },
        "required": ["input_content"],
    },
}