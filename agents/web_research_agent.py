from functions.wikitool import get_wikipedia_info, get_wikipedia_info_function
from functions.summariser import get_summerized_content, get_summerized_content_function
from functions.web_search import get_web_results_function, crawl_webpage_function, crawl_webpage, get_web_results
from dotenv import load_dotenv
from google.genai import types
from google import genai
from enum import Enum
from datetime import date
import sys
import json



# response = client.interactions.create(...)
# response.id            # str, for previous_interaction_id chaining
# response.status        # e.g. completed
# response.output_text   # str, SDK-derived: concatenated text from last model_output. "" if none.
# response.usage.total_input_tokens
# response.usage.total_output_tokens
# response.usage.total_thought_tokens
# response.usage.total_tokens
# response.model_dump()  # full dict for inspection / json.dump


# 3. How to parse each
# for step in response.steps or []:
#     if step.type == "model_output":  # not "text"
#         for item in step.content or []:
#             if item.type == "text":
#                 print(item.text)

#     elif step.type == "thought":
#         for s in step.summary or []:
#             if s.type == "text":
#                 print(s.text)

#     elif step.type == "function_call":
#         print(step.id, step.name, step.arguments)  # arguments is dict
# Schema verified locally:
# - FunctionCallStep: arguments: dict, id: str, name: str, type='function_call'
# - ModelOutputStep: content: list[TextContent|ImageContent...], type='model_output'
# - ThoughtStep: summary: list[TextContent...], signature, type='thought'
# - Usage: total_input/output/thought/tokens, etc.

load_dotenv()

date = date.today()
total_input_tokens = ''
total_output_tokens = ''
total_thought_tokens = ''
total_tokens = ''
    
def main():
    
    tool_mapping = {
        "get_wikipedia_info": get_wikipedia_info,
        "get_summerized_content": get_summerized_content,
        "crawl_webpage": crawl_webpage, 
        "get_web_results": get_web_results
    }

    tools_list = [get_summerized_content_function, get_wikipedia_info_function, get_web_results_function, crawl_webpage_function]
    
    client = genai.Client()

    inputt = "i want to build a GCP expert agent that can migrate an entire MongoDB database of size more than 2TB all alone to BigQuery. Give me the detailed technical flow"
    
    thoughts = ""
    final_response = ""
    
    system_prompt = f"""
            You are a research assistant conducting research on the user's input topic. For context, today's date is {date}.

            <Task>
            Your job is to use tools to gather information about the user's input topic.
            You can use any of the tools provided to you to find resources that can help answer the research question. You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.
            </Task>

            <Available Tools>
            You have access to two main tools:
            1. "get_wikipedia_info": get_wikipedia_info,
            2. "get_summerized_content": get_summerized_content,
            3. "crawl_webpage": crawl_webpage, 
            4. "get_web_results": get_web_results

            <Instructions>
            Think like a human researcher with limited time. Follow these steps:

            1. **Read the question carefully** - What specific information does the user need?
            2. **Start with broader searches** - Use broad, comprehensive queries first
            3. **After each search, pause and assess** - Do I have enough to answer? What's still missing?
            4. **Execute narrower searches as you gather information** - Fill in the gaps
            5. **Stop when you can answer confidently** - Don't keep searching for perfection
            </Instructions>

            <Hard Limits>
            **Tool Call Budgets** (Prevent excessive searching):
            - **Simple queries**: Use 2-3 search tool calls maximum
            - **Complex queries**: Use up to 6 search tool calls maximum
            - **Always stop**: After 6 search tool calls if you cannot find the right sources

            **Stop Immediately When**:
            - You can answer the user's question comprehensively
            - You have 3+ relevant examples/sources for the question
            - Your last 2 searches returned similar information
            </Hard Limits>

            <Show Your Thinking>
            After each search tool call, use think_tool to analyze the results:
            - What key information did I find?
            - What's missing?
            - Do I have enough to answer the question comprehensively?
            - Should I search more or provide my answer?
            </Show Your Thinking>
        
        """


    history = []    
    tool_status=None
    print("Lets begin !!")
    while tool_status != 'completed':
        
        if history == []:
            history.append({
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": inputt
                }]
            })
        response = client.interactions.create(
            model="gemini-3.5-flash-lite",
            input=history,
            system_instruction=system_prompt,
            tools=tools_list
        )
        
        for step in response.steps:
            
            if step.type == "thought":
                print("\nThought summary:\n", 100*"-")
                if step.summary:
                    thoughts = ' '.join([step.content[i].text for i in range(len(step.summary))] if step.content else "")
                    
                history.append({
                    "type": "thought",
                    "content": {
                        "type": "text",
                        "text": thoughts
                    }
                })
                
                print(f"thoughts:{thoughts}\n",100*'-')
                
            if step.type == "function_call":
                tool_status="function_call"
                tool_name = step.name
                tool_args = step.arguments
                
                print(f"\n\nFUNCTIONS TO CALL: {tool_name}")
                print(f"ARGUMENTS: {tool_args}")
                print(100*"-", '\n\n')
                
                if tool_name == "get_summerized_content":
                    print('\n\n','SUMMARISING THE CONTENT')
                
                output = tool_mapping[tool_name](**tool_args)
                history.append({
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(output)}],
                })
                print(f"FUNCTION OUTPUT:\n", 100*"-")
                print(f"{output}")
                print(100*'-', '\n\n')
            
            elif step.type == "model_output":  # not "text"
                tool_status='completed'
                        
                history.append({
                    "type": "model_output",
                    "content": {
                        "type": "text",
                        "text": ' '.join([step.content[i].text for i in range(len(step.content))] if step.content else "")
                    }
                })
                
                total_input_tokens = response.usage.total_input_tokens
                total_output_tokens = response.usage.total_input_tokens
                total_thought_tokens = response.usage.total_input_tokens
                total_tokens = response.usage.total_input_tokens

                final_response += ' '.join([step.content[i].text for i in range(len(step.content))] if step.content else "")


    print(f"FINAL RESPONSE:\n{final_response}", '\n\n')   
    print("CONSUMPTIONS:\n")             
    print(f"total input tokens: {total_input_tokens}")
    print(f"total output tokens: {total_output_tokens}")
    print(f"total thought tokens: {total_thought_tokens}")
    print(f"total tokens: {total_tokens}\n\n")
    return 0
            
if __name__ == "__main__":
    main()
