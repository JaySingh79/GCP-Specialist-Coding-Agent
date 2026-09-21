import os
import subprocess

from functions.get_files_info import get_file_info

def run_python_file(working_dir, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not in the working directory"
    
    if not os.path.isfile(abs_file):
        return f"Error - {dir} is not a file"

    try:
            
        res = subprocess.run(["python", abs_file], cwd=abs_dir, capture_output=True, text=True)
        final = f"""
            {res.stderr}
            {res.stdout}
        """
        if res.stderr == "" and res.stdout == "":
            return f"Error - {abs_file} did not produce any output"
        
        elif res.returncode != 0:
            final+= f"program exited with code {res.returncode}"
            
        return final
        
    except Exception as e:
        return f"Error executing the file {abs_file}"


    
    
run_python_file_function = {
    "type": "function",
    "name": "run_python_file",
    "description": "Runs a Python file.",
    "parameters": {
        "type": "object",
        "properties": {
            "working_dir": {
                "type": "string",
                "description": "The working directory.",
            },
            "dir": {
                "type": "string",
                "description": "The file path, e.g. ./src/main.py",
            },
        },
        "required": ["working_dir", "dir"],
    },
}


def run_python_file_as_module(working_dir, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not in the working directory"
    
    if not os.path.isfile(abs_file):
        return f"Error - {dir} is not a file"
    try:
        abs_file = abs_file.replace('.py', '')
        res = subprocess.run(["python","-m", abs_file], cwd=abs_dir, capture_output=True, text=True)
        final = f"""
            {res.stderr}
            {res.stdout}
        """
        if res.stderr == "" and res.stdout == "":
            return f"Error - {abs_file} did not produce any output"
        
        elif res.returncode != 0:
            final+= f"program exited with code {res.returncode}"
            
        return final
        
    except Exception as e:
        return f"Error executing the file {abs_file} : {e}"
    
    
    
run_python_file_as_module_function = {
    "type": "function",
    "name": "run_python_file_as_module",
    "description": "Runs a Python file as module.",
    "parameters": {
        "type": "object",
        "properties": {
            "working_dir": {
                "type": "string",
                "description": "The working directory.",
            },
            "dir": {
                "type": "string",
                "description": "The file path, e.g. ./src/main.py",
            },
        },
        "required": ["working_dir", "dir"],
    },
}