import subprocess
import os
from config import MAX_CHAR
import re

def execute_python_code_from_shell(working_dir, code:str):
    short=False
    if len(code)<MAX_CHAR:
        short=True
        
    if "'''" in code:
        pass    
    else:
        text = re.sub(r"""["']""", "'''", code)
    try:
        subprocess.run(["python", "-c", code], cwd=working_dir, capture_output=True, shell=True)
        
    except Exception as e:
        if short:
            return f"Error occured while executing the script {code} : \ne"
        else:
            return f"Error occured while executing the script : \ne"
        
        
execute_python_code_from_shell_function = {
    "type": "function",
    "name": "execute_python_code_from_shell",
    "description": "Runs a Python code from shell",
    "parameters": {
        "type": "object",
        "properties": {
            "working_dir": {
                "type": "string",
                "description": "The working directory.",
            },
            "code": {
                "type": "string",
                "description": "The actual code to test/run",
            },
        },
        "required": ["working_dir", "code"],
    },
}