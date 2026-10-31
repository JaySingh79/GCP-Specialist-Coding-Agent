import sys
from pathlib import Path

path = Path(__file__).resolve().parents[1]
if str(path) not in sys.path:
    sys.path.insert(0, str(path))

from functions.run_python_file_in_shell import execute_python_code_from_shell, execute_python_code_from_shell_function
from functions.run_python_file import run_python_file, run_python_file_function
from functions.write_file import write_file, write_file_function
from functions.get_files_info import get_file_info, get_file_info_function
from functions.get_file_content import get_file_content,get_file_content_function
from functions.write_new_file import write_new_file, write_new_file_function
from functions.wikitool import get_wikipedia_info, get_wikipedia_info_function
from functions.summariser import get_summerized_content, get_summerized_content_function
from shell_tools.directory_tools import run_shell_command, run_shell_command_function
from functions.save_memory import save_memory, save_memory_function, load_memory
from functions.save_todo_updates import save_todo, save_todo_function, load_todo
from functions.save_execution_ledger import save_exe_ledger, save_exe_ledger_function, load_exe_ledger
from functions.tool_batching import batched_tools_function, batched_tools
from config import TOKEN_CONSUMPTION, gcp_keywords
from rich.console import Console
from dotenv import load_dotenv
from google import genai
from typing import List
import datetime
import threading
import queue
import logging
import asyncio
import random
import uuid
import json
import time
import re
import os

console = Console()
load_dotenv()

logfile_root = Path(__file__).resolve().parents[1] / "logs" / "logs.txt"

memory_file = Path(__file__).parent / "memory" / "lt_memory.md"

logging.basicConfig(
    filename=logfile_root,
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s-%(levelname)s-%(message)s')
            
            
with open("src/session_data.json", "r") as file:
    session_content = json.load(file)
    
    
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

    
async def agent_main():
    
    # pause: Event, set = running, cleared = paused. stop: Event, set = abort.
    # Both are owned by the UI thread; this (worker) thread only reads them.
    # if pause is None:
    #     pause = threading.Event()
    #     pause.set()
    # if stop is None:
    #     stop = threading.Event()


    tool_mapping = {
        "run_python_file": run_python_file,
        "write_file": write_file,
        "get_file_info": get_file_info,
        "get_file_content": get_file_content,
        "write_new_file": write_new_file,
        "get_wikipedia_info": get_wikipedia_info,
        "get_summerized_content": get_summerized_content,
        "run_shell_command": run_shell_command,
        "execute_python_code_from_shell": execute_python_code_from_shell,
        "save_memory": save_memory, 
        "batched_tools": batched_tools, 
        "save_todo": save_todo,
        "save_exe_ledger": save_exe_ledger
    }

    tools_list = [execute_python_code_from_shell_function, run_python_file_function,
                  get_file_info_function, get_file_content_function, 
                  write_new_file_function, get_summerized_content_function,
                  get_wikipedia_info_function, run_shell_command_function, 
                  save_memory_function, batched_tools_function, save_todo_function, 
                  save_exe_ledger_function, write_file_function]
    
    
    client = genai.Client()

    logging.info(f"\nCLIENT INITIALIZED")
    
    # if len(sys.argv) < 2:
    #     print("I need a prompt")
    #     sys.exit(1)
    
    # inputt = sys.argv[1]
    
    # inputt = """
    #     Show me all VPC networks, subnets, firewall rules, routes, and NAT configurations in this project : claude-code-498910
    # """
    
    # console.print("lets go !!", style="bold green")
    
    
    
    async def execution_loop(tool_status, 
                        user_command:str | None = None,
                        final_response: str = "",
                        prev_chat_id: str | None = None,
                        system_prompt: str = ""):
        
        global session_content
        
        token_consump = {
            "total_input_tokens" : 0,
            "total_output_tokens" : 0,
            "total_though_tokens" : 0,
            "total_tokens" : 0
        }
                
        
        history = []
        history.append({
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": user_command
                }]
            })
        
        try:
            while tool_status != 'completed':
                
                # honour /stop and /pause between model calls (timeout keeps it responsive)
                # if stop.is_set():
                #     return "Stopped by user"
                # if not pause.wait(timeout=0.2):
                #     continue
                
                retry=0
                for retry in range(MAX_RETRIES):
                    
                    
                    try:
                        
                        # for i in range(1, len(tools_list) + 1):
                        #     try:
                        #         r = client.interactions.create(
                        #             model="gemini-3.5-flash-lite",
                        #             input="Reply with OK.",
                        #             tools=tools_list[:i],
                        #         )
                        #         console.print(f"{i} tools: OK")
                                
                        #     except Exception as e:
                        #         console.print(f"{i} tools: FAILED — {e}")
                        #         break
                        # return response.output_text
                        # 
                        
                        
                        if prev_chat_id:
                            previous_chat_id = prev_chat_id
                        # elif session_content:
                        #     previous_chat_id = session_content['id']
                        else:
                            previous_chat_id = None
                            
                            
                        response = client.interactions.create(
                            model="gemini-3.5-flash-lite",
                            input= history,
                            system_instruction=system_prompt,
                            tools=tools_list, 
                            previous_interaction_id=previous_chat_id,
                        )
                        
                        break
                        
                    except Exception as e:
                        
                        logging.exception(f"[INTERACTION ERROR] an error : {e}")
                        error = str(e)
                        
                        if "Model generated invalid JSON syntax" in error and retry <= MAX_RETRIES-1:
                            response = client.interactions.create(
                                model="gemini-3.5-flash-lite",
                                input= history,
                                system_instruction=system_prompt,
                                tools=tools_list, 
                                previous_interaction_id=previous_chat_id,
                                generation_config={
                                        "thinking_summaries": "auto"
                                    }
                            )
                            
                            
                        else:
                            logging.info(f"[POST INTERACTION ERROR] an error OTHER THAN INVALID JSON: {e}")
                            return f"An error occured : {e}", prev_chat_id, token_consump
                        
                    retry+=1
                    
                previous_chat_id = response.id
                
                logging.info(f"[RESPONSE] Tracking {prev_chat_id}")
                logging.info(f"[RESPONSE]: {response}[:50]...")
                
                for step in response.steps:
                    if step.type == "function_call":
                        tool_status="function_call"
                        
                        # logging.info("[FUNCTION CALL] Appended function call step to history")
                        # history.extend(
                        #         step.model_dump(exclude_none=True)
                        #     )
                        
                        logging.info(f"[STEP NAME]: {step.name}")
                        tool_output_text = ""
                        actual_tool = tool_mapping.get(step.name)

                        logging.info(f"[FUNCTION NAME]: {actual_tool}")
                        logging.info(f"[FUNCTION ARGS]: {step.arguments}")
                        
                        if actual_tool is None:
                            output = {
                                "success" : False,
                                "error": "Unknown tool",
                                "message": f"requested tool does not exist : {step.name}"
                            }
                            
                            tool_output_text = json.dumps(output, ensure_ascii=False)
                            logging.info(f"[INVALID] unknown tool : {step.name}")
                            
                        else:
                            tool_name = step.name
                            tool_args = step.arguments
                            
                            
                            console.print(f"\nFunction to call: {tool_name}", style="bold cyan")
                            console.print(f"Arguments: {tool_args}\n", style="yellow")
                            console.print(100*"-", style="dim")
                            
                            if tool_name == "get_summerized_content":
                                console.print('\n' + 100*'-' + ' Summarising the content \n\n', style="bold magenta")
                                logging.info(f"[SUMMARIZING FUNC]: summarizing the content")
                            
                            try:
                                if tool_name == "batched_tools":
                                    output = await tool_mapping[tool_name](**tool_args)
                                    logging.info(f"[BATCHED TOOL] batched_tool initiated")
                                    
                                else:
                                    output = tool_mapping[tool_name](**tool_args)
                                    
                                logging.info(f"[TOOL OUTPUT] tool output: {output}")
                                
                                if isinstance(output, dict):
                                    tool_output_text = json.dumps(output, ensure_ascii=False)
                                else:
                                    tool_output_text = str(output)
                                    
                            except Exception as e:
                                
                                logging.exception(f"[TOOL_ERROR]: error executing tool {tool_name}: {e}")
                                output = {
                                    "success": False,
                                    "error": type(e).__name__,
                                    "message": str(e)
                                }
                                tool_output_text = json.dumps(output)
                        
                        appendable_tool_result = {
                                "type": "function_result",
                                "name": step.name,
                                "call_id": step.id,
                                "result": [{"type": "text", "text": tool_output_text}],
                            }
                        
                        history.append(appendable_tool_result)
                        logging.info(f"[HISTORY] appended tool result: {appendable_tool_result}")
                        logging.info(f"[HISTORY] APPENDED HISTORY: {history}")
                        
                        console.print(f"Function output:\n{output}\n", style="green")
                        console.print(100*"-" + "\n\n", style="dim")
                    
                    
                    elif step.type == "thought":
                        
                        # history.extend(
                        #     step.model_dump(exclude_none=True)
                        # )
                        # logging.info(f"[THOUGHTS HISTORY] Appended thought step to History")
                        
                        console.print(f"\nThinking ..", style="magenta")
                        logging.info(f"[THOUGHTS] The model applied thinking")
                        console.print(f"{step}\n")
                        logging.info(f"[THOUGHTS] Following is the step : {step}")
                        
                        if step.summary:
                            for content_block in step.summary:
                                if content_block.type == "text":
                                    console.print(f"though content: {content_block.text}\n")
                                    
                                    
                    elif step.type == "model_output":  # not "text"
                        tool_status='completed'
                        # for item in step.content or []:
                        #     if item.type == "text":
                        #         print(item.text)
                        
                        final_response += ' '.join([step.content[i].text for i in range(len(step.content))] if step.content else "")
                        
                        logging.info(f"[MODEL OUTPUT]: {final_response}")
                        
                        history.append(
                            {
                                "type": "model_output",
                                "content": [{
                                    "type": "text",
                                    "text": final_response
                                }]
                            }
                        )
                        
                        total_input_tokens = int(response.usage.total_input_tokens)
                        total_output_tokens = int(response.usage.total_output_tokens)
                        total_though_tokens = int(response.usage.total_thought_tokens)
                        total_tokens = int(response.usage.total_tokens)
                        
                        
                        token_consump['total_input_tokens'] = total_input_tokens
                        token_consump['total_output_tokens'] = total_input_tokens
                        token_consump['total_though_tokens'] = total_though_tokens
                        token_consump['total_tokens'] = total_tokens
                        
                        # token_consump = [total_input_tokens, total_output_tokens, total_though_tokens, total_tokens]
                        
                        logging.info(f"[TOTAL INPUT TOKENS]: {total_input_tokens}")
                        logging.info(f"[TOTAL OUTPUT TOKENS]: {total_output_tokens}")
                        logging.info(f"[TOTAL THOUGHT TOKENS]: {total_though_tokens}")
                        logging.info(f"[TOTAL TOKENS]: {total_tokens}")
                        
            # console.print(f"\nAgent: {final_response}\n\n", style="bold green")          
            # yield final_response
            return final_response, previous_chat_id, token_consump
                        
        except Exception as e:
            logging.exception(f"[FIRST EXCEPTION BLOCK]: {e}")
            return f"An error occurred :{e}", previous_chat_id, token_consump
    
    
    
    
    
    ### START AFTER EXECUTION LOOP BUILT
    
    with open("src/relevant_system_files/sys_prompt.md", 'r') as f:
        sys2 = f.read()
    
    working_dir="D:/Projects/coding agent/"
    system_prompt = sys2 + f"\nworking_dir : {working_dir}\nTime: {time.time}\nDate: {datetime.date}"
        
    tool_status=None
    final_response = ""    
    MAX_RETRIES = 3
    
        
    logging.info("[LOOP]: Loop initiated for command execution")
    
    previous_chat_id = None
    
    console.print(
        "\n[bold magenta]Welcome to the Coding Agent Terminal![/bold magenta]"
    )
    while True:
        
        try:
            command = input("\n\033[96m❯ \033[0m")
            command = command.strip()


            for key in gcp_keywords:
                if key in command and not "Gcloud Guidance" in system_prompt:
                    
                    with open("src/relevant_system_files/gcloud_sys.md", 'r', encoding='utf-8') as f:
                        gcloud_sys = f.read()
                        system_prompt = system_prompt + f"\n## Gcloud Guidance\n{gcloud_sys}"
                        console.print("\ngcloud instruction loaded in memory !!\n", style="yellow")
                        
                        break
                    
            if not command:
                continue
                
            if command == "/pause":
                console.print("[yellow]Agent paused.[/yellow]")
                continue

            if command == "/resume":
                console.print("[green]Agent resumed.[/green]")
                continue

            if command == "/stop":
                console.print("[red]Stop requested.[/red]")
                continue
            
            if command == "/context":
                console.print("[pink]Token Consumption Latest.[/pink]")
                # console.print("Consumption " + 100*"-" + "\n", style="bold yellow")
                console.print(f"total input tokens: {TOKEN_CONSUMPTION["total_input_tokens"]}", style="cyan")
                console.print(f"total output tokens: {TOKEN_CONSUMPTION["total_output_tokens"]}", style="magenta")
                console.print(f"total thought tokens: {TOKEN_CONSUMPTION["total_though_tokens"]}", style="blue")
                console.print(f"total tokens: {TOKEN_CONSUMPTION["total_tokens"]}", style="bold white")
                continue
            
            if command == "/exit":
                break 
            
            answer, previous_chat_id, tokens = await execution_loop(tool_status, user_command=command, 
                                                    final_response=final_response,
                                                    system_prompt=system_prompt.format(memory=load_memory, todo=load_todo, exe_ledger=load_exe_ledger),
                                                    prev_chat_id=previous_chat_id)
            
            # for k, v in zip(TOKEN_CONSUMPTION.keys()):
            #     TOKEN_CONSUMPTION[k]=v
            
            console.print(f"[bold green]Agent: [/bold green][bright_cyan]{answer}[/bright_cyan]\n")
            console.print(f"Checking sytem prompt growth : {len(system_prompt)}", style="yellow")
            # break
                            
            TOKEN_CONSUMPTION.update(tokens)
            
        except KeyboardInterrupt as e:
            console.print(f"Keyboard interrupt received: {e}", style="bold red")
            logging.exception(f"[ERROR] LAST An error occured: {e}")
            break
    
    console.print(100*"-", style="dim")        
    console.print(100*"-", style="dim")
    console.print("Consumption " + 100*"-" + "\n", style="bold yellow")
    console.print(f"total input tokens: {TOKEN_CONSUMPTION["total_input_tokens"]}", style="cyan")
    console.print(f"total output tokens: {TOKEN_CONSUMPTION["total_output_tokens"]}", style="magenta")
    console.print(f"total thought tokens: {TOKEN_CONSUMPTION["total_though_tokens"]}", style="blue")
    console.print(f"total tokens: {TOKEN_CONSUMPTION["total_tokens"]}", style="bold white")
    
    
    # if response is None or response.usage_metadata is None:
    #     return
    # print(f"prompt token: {response.usage_metadata.prompt_token_count}")
    # print(f"prompt token: {response.usage_metadata.candidates_token_count}")
    # print(interaction.output_text)

if __name__ == "__main__":
    import asyncio
    
    asyncio.run(agent_main())
    # async def multiple_runs():
    #     # Run agent_main() 7 times concurrently (non-blocking via threads)
    #     # agent_main is sync, so wrapped with asyncio.to_thread
        
    #     tasks = [asyncio.to_thread(agent_main()) for i in range(7)]
    #     results = await asyncio.gather(*tasks, return_exceptions=True)
        
    #     for i, result in enumerate(results, 1):
            
    #         if isinstance(result, Exception):
    #             console.print(f"[Task {i}] failed: {result}", style="bold red")
    #         else:
    #             console.print(f"[Task {i}] completed with: {result}", style="bold green")

    # asyncio.run(multiple_runs())
    
    # asyncio.run(agent_main())
