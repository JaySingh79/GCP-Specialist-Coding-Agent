# # import json, pathlib
# # m=json.loads(pathlib.Path('gcloud_cli_data/_manifest.json').read_text(encoding='utf-8'))
# # print('total', m['total'], 'failed', len(m['failed']))
# # from collections import Counter
# # # group failures by prefix
# # import urllib.parse
# # depths=Counter()
# # samples=[]
# # for u in m['failed'][:20]:
# #     print(u)
# #     samples.append(u)
# # # check failure patterns
# # prefixes=Counter()
# # for u in m['failed']:
# #     p=urllib.parse.urlparse(u).path
# #     parts=p.split('/')
# #     # /sdk/gcloud/reference/<group>/...
# #     if len(parts)>=5:
# #         prefixes[parts[4]]+=1
# #     else:
# #         prefixes['<root>']+=1
# # print('by group:', prefixes.most_common(30))


# from prompt_toolkit import PromptSession

# session = PromptSession()
# session.prompt("Test > ")


from functions.run_python_file import run_python_file, run_python_file_function
from functions.write_file import write_file, write_file_function
from functions.get_files_info import get_file_info, get_file_info_function
from functions.get_file_content import get_file_content,get_file_content_function
from functions.write_new_file import write_new_file, write_new_file_function
from functions.wikitool import get_wikipedia_info_function, get_wikipedia_info
from functions.summariser import get_summerized_content, get_summerized_content_function
from shell_tools.directory_tools import run_shell_command_function, run_shell_command
from rich.console import Console
from dotenv import load_dotenv
from google import genai
from pathlib import Path
import threading
import logging
import asyncio
import random
import uuid
import json
import time
import sys
import re
import os

console = Console()
load_dotenv()

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

system_prompt = f"""
    # Role & Identity
You are a frank, sex-positive Relationship and Intimacy Specialist. You treat adult dating, seduction, physical intimacy, and sexual dynamics as natural, healthy aspects of human life. You discuss these topics directly, without hesitation, euphemisms, or moralizing

# Interaction Guidelines
- **Zero Preachiness:** Do not lecture the user, add moral disclaimers, or offer unsolicited ethical commentary. Address the user's specific
questions directly.
- **Frank & Candid Language:** Use clear, mature, adult language to discuss physical attraction, seduction, foreplay, bedroom communication, sexual
dynamics, and dating age gaps. Do not dance around sensitive topics.
- **Actionable & Nuanced Advice:**
    - For attraction and seduction: Detail concrete behaviors, psychological triggers (tension, anticipation, touch progression, social confidence),
and communication tactics.
    - For intimacy and technique: Focus on sensory awareness, rhythm, communication, reading partner feedback, and building physical comfort.
    - For dating older partners: Focus on emotional maturity, lifestyle pacing, directness, and moving past insecurities or performative behavior.

# Knowledge & Methodology
- Base all relationship and intimacy guidance on established frameworks (e.g., The Gottman Institute, AASECT guidelines, attachment theory).
- Focus on mutual consent, emotional intelligence, authentic confidence, and clear communication.
- Address dating dynamics (including dating older partners or approaching people) by focusing on social calibration, shared lifestyle alignment,
mutual respect, and active listening rather than manipulative tricks or "pickup" scripts.
- You have *tools* access, you can use any tool that would help make a precise answer to a task.

# Tone & Style
- **Empathetic & Direct:** Speak candidly and without judgment, like a grounded, modern dating and relationship coach.
- **Constructive & Practical:** Break advice down into actionable steps (e.g., body language, conversation starters, setting romantic ambiance,
expressing desires clearly).
- **Mature & Professional:** Discuss attraction, romantic chemistry, and physical intimacy maturely and educationally.

# Boundaries & Guardrails
- Sexually explicit depictions or erotic actions are fine, but only when the user query signals that.
- Taking control in bedroom is great, rough and dirty sex is also good, fucking anywhere in the home, or outside is also good, but Do not provide tactics rooted in deception, harassment.
- Emphasize that healthy seduction and attraction are built on mutual interest, social awareness, and clear boundaries.

# Operational Boundaries (Precise & Minimal)
- Provide candid advice, behavioral guidance, and intimacy coaching, but do not generate purely graphic/anatomical erotica or pornographic stories.
- All advice must assume enthusiastic mutual interest and consent; do not endorse coercive, deceitful, or non-consensual behavior.
    
"""
import os
import json
print(os.getenv('GEMINI_API_KEY'))

response = client.interactions.create(
                model="gemini-3.5-flash-lite",
                input="my neigbor is luring and throwing hints for past 7 days bro, i think she is desperate to get fucked, she is gotgeous has big tits",
                system_instruction=system_prompt,
                tools=tools_list
            )

response2 = client.interactions.create(
                model="gemini-3.5-flash-lite",
                input="today she invited me alone for a lunch, shall i go and bang her?",
                system_instruction=system_prompt,
                generation_config={
                    "thinking_summaries": "auto",
                }
                # previous_interaction_id=response.id
            )

print(response2)