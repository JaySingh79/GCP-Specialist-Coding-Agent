import subprocess
import json

with open("risk_commands.json", 'r') as f:
    restrict_commands = eval(f.read())

def run_shell_command(command: str, timeout:int=30):
    
    if not command:
        return f"Empty string is not a command"
        
    print(f"running shell..\n{command}")
    command_list = command.split()
    
    if command_list[0] == 'gcloud':
        if command in restrict_commands['gcloud']:
            return f"Blocked command : agent tried to access restricted command {command}"
    else:
        if command in restrict_commands['powershell']:
            return f"Blocked command : agent tried to access restricted command {command}"            

    try:
        response = subprocess.run(
            command_list,
            capture_output=True,
            shell=True,
            text=True,
            timeout=timeout
        )
        if response.stderr == "" and response.stdout == "":
            return f"Error - {command} did not produce any output"
                
        elif response.returncode != 0:
            return f"program exited with code {response.returncode}"
        
        return {
            "Status Code": response.returncode,
            "stdout": response.stdout,
            "stderr": response.stderr,
        }
        
    except Exception as e:
        return f"Error executing the file {command}: {e}"

run_shell_command_function = {
    "type": "function",
    "name": "run_shell_command",
    "description": "Execute shell/bash/powershell/terminal commands.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to be executed. If executing a shell commmand follow powershell rules",
            },
            "timeout": {
                "type": "integer",
                "description": "TTL for the executed command until output arrives, mostly between 10 to 300s based on the type of command being executed, ex. npm install might take few minues",
            }
        },
        "required": ["command", "timeout"],
    },
}