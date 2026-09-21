from functions.run_python_file import run_python_file, run_python_file_function
from functions.write_file import write_file, write_file_function
from functions.get_files_info import get_file_info, get_file_info_function
from functions.get_file_content import get_file_content,get_file_content_function
from functions.write_new_file import write_new_file, write_new_file_function
from functions.wikitool import get_wikipedia_info_function, get_wikipedia_info
from functions.summariser import get_summerized_content, get_summerized_content_function
from shell_tools.directory_tools import run_shell_command_function, run_shell_command
from dotenv import load_dotenv
from google import genai
import random
import uuid
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
        
# print(f'\n\n{response}\n\n')

# with open("response.json", "w", encoding="utf-8") as f:
#     json.dump(response, f, ensure_ascii=False, indent=4)


# TRANSCRIPT FORMAT
# {
#     "type": "user_input",
#     "content": {
#         "type": "text",
#         "text": inputt
#     }
# }
    
# print(response.output_text)
# print(f"model name : {response.}")

# config = types.GenerateContentConfig(
#     max_output_tokens=2048,
#     temperature=0.2
# )
history = []
load_dotenv()
    
def agent_main(inputt):
    
    total_input_tokens = ''
    total_output_tokens = ''
    total_though_tokens = ''
    total_tokens = ''
    
    tool_mapping = {
        "run_python_file": run_python_file,
        "write_file": write_file,
        "get_file_info": get_file_info,
        "get_file_content": get_file_content,
        "write_new_file": write_new_file,
        "get_wikipedia_info": get_wikipedia_info,
        "get_summerized_content": get_summerized_content,
        "run_shell_command": run_shell_command
    }

    tools_list = [run_python_file_function, write_file_function, 
                  get_file_info_function, get_file_content_function, 
                  write_new_file_function, get_summerized_content_function,
                  get_wikipedia_info_function, run_shell_command_function]
    
    
    
    client = genai.Client()

    # if len(sys.argv) < 2:
    #     print("I need a prompt")
    #     sys.exit(1)
        
    # inputt = sys.argv[1]
    
    # inputt = """
    #     Show me all VPC networks, subnets, firewall rules, routes, and NAT configurations in this project : claude-code-498910
    # """

    working_dir="D:/Projects/coding agent/"
    system_prompt = f"""
        ## Identity
        You are an expert coding assistant that solves user programming, planning bug fixes related questions.
        
        ## Rules
        - Justify every command run, code written, file edited, and steps taken to reach solution, in the final response.
        - If executing a shell commmand follow Powershell rules strictly, not bash, zsh, etc.
        Strictly:
        - Do not execute unnecessary tools
        - Do not write irrelevant code
        - Do not create irrelevant files
        - Do not do anything except for what user has asked
        - Make sure the all the commands you ran, code files you created pass the test
        
        ## Knowledge
        You are currently inside a coding project directory.
        
        ## Execution Flow
        - Understand the user query
        - Break it into multile tasks for better understanding.
        - write benchmark evaluation cases for your solution
        - Write clean code
        - Execute through tool calls
        - Test the results
        - Loop iterateratively untill you have the final answer
        
        # CWD : {working_dir}
    """
    
    
    history.append({
        "type": "user_input",
        "content": [{
            "type": "text",
            "text": inputt
        }]
    })
    tool_status=None
    final_response = ""
    print("lets go !!")
    
    
    try:
            
        while tool_status != 'completed':
        
            response = client.interactions.create(
                model="gemini-3.5-flash-lite",
                input=history,
                system_instruction=system_prompt,
                tools=tools_list
            )
            
            for step in response.steps:
                if step.type == "function_call":
                    tool_status="function_call"
                    
                    actual_tool = tool_mapping.get(step.name)
                    
                    if actual_tool is None:
                        output = {
                            "success" : False,
                            "error": "Unknown tool",
                            "message": f"requested tool does not exist : {step.name}"
                        }
                    else:
                        tool_name = step.name
                        tool_args = step.arguments
                        
                        
                        print(f"\nFunction to call: {tool_name}")
                        print(f"Arguments: {tool_args}\n")
                        print(100*"-")
                        
                        if tool_name == "get_summerized_content":
                            print('\n',100*'-', 'Summarising the content', '\n\n')
                        
                        try:
                            output = tool_mapping[tool_name](**tool_args)
                            
                            try:
                                tool_output_text = json.dumps(output)
                            except TypeError as e:
                                output = {
                                    "success": False,
                                    "error": "SerializationError",
                                    "message": f"Tool returned not json serializable object:\nActual output: {output}"
                                }
                        except Exception as e:
                            output = {
                                "success": False,
                                "error": type(e).__name__,
                                "message": str(e)
                            }
                            
                    history.append({
                        "type": "function_result",
                        "name": step.name,
                        "call_id": step.id,
                        "result": [{"type": "text", "text": tool_output_text}],
                    })
                    print(f"Function output: {output}\n")
                    print(100*"-", '\n\n')
                
                elif step.type == "model_output":  # not "text"
                    tool_status='completed'
                    # for item in step.content or []:
                    #     if item.type == "text":
                    #         print(item.text)
                    
                    final_response += ' '.join([step.content[i].text for i in range(len(step.content))] if step.content else "")
                    history.append({
                        "type": "model_output",
                        "content": {
                            "type": "text",
                            "text": final_response
                        }
                    })
                    
                    total_input_tokens = response.usage.total_input_tokens
                    total_output_tokens = response.usage.total_output_tokens
                    total_though_tokens = response.usage.total_thought_tokens
                    total_tokens = response.usage.total_tokens
                    
    except Exception as e:
        return f"An error occurred :{e}"    
        
    print(100*"-")
    print(f"Final response:\n{final_response}\n\n")
    print("Consumption",100*"-",'\n')
    print(f"total input tokens: {total_input_tokens}")
    print(f"total output tokens: {total_output_tokens}")
    print(f"total thought tokens: {total_though_tokens}")
    print(f"total tokens: {total_tokens}")
    
    return 0
    # if response is None or response.usage_metadata is None:
    #     return
    # print(f"prompt token: {response.usage_metadata.prompt_token_count}")
    # print(f"prompt token: {response.usage_metadata.candidates_token_count}")
    # print(interaction.output_text)

# if __name__ == "__main__":
#     agent_main()
