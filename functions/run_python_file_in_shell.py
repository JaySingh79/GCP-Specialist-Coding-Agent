from src.config import MAX_CHAR
from pathlib import Path
import subprocess
import tempfile
import ast
import sys
import os
import re


def execute_python_code_from_shell(working_dir, python_code:str, timeout: int = 30) -> str:
    
    """This tool is used to run a python code in a shell/terminal. Use this only to run python codes.
    """
        
    if not isinstance(python_code, str) or not python_code.strip():
        return "Execution error: python_code must be a non-empty string."

    if len(python_code) > MAX_CHAR:
        return (
            f"Execution error: code exceeds the maximum length "
            f"of {MAX_CHAR} characters."
        )

    directory = Path(working_dir).resolve()

    if not directory.is_dir():
        return f"Execution error: working directory does not exist: {directory}"
   
    code = python_code.strip()
    lines = code.splitlines()

    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)

    # Detect syntax errors before executing.
    try:
        ast.parse(code)
    except SyntaxError as e:
        return (
            f"Python syntax error at line {e.lineno}, column {e.offset}: "
            f"{e.msg}\n"
            f"Problematic line: {e.text.strip() if e.text else 'unavailable'}\n"
            "Fix the Python source and call this tool again. "
            "Do not use shell line-continuation syntax inside Python code."
        )   

    script_path = None

    try:
        # The temporary script avoids shell quoting and python -c issues.
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            encoding="utf-8",
            newline="\n",
            delete=False,
        ) as script:
            script.write(code)
            script_path = Path(script.name)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(directory),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )

        output = []

        if result.stdout:
            output.append("STDOUT:\n" + result.stdout)

        if result.stderr:
            output.append("STDERR:\n" + result.stderr)

        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")

        return "\n".join(output) if output else (
            "Execution completed successfully. No output."
            if result.returncode == 0
            else f"Execution failed with exit code {result.returncode}."
        )

    except subprocess.TimeoutExpired:
        return (
            f"Execution timed out after {timeout} seconds. "
            "Check for infinite loops or slow operations."
        )

    except OSError as e:
        return f"Execution system error: {type(e).__name__}: {e}"


    finally:
        if script_path is not None:
            try:
                script_path.unlink(missing_ok=True)
            except OSError:
                pass

   
    # if len(python_code)<MAX_CHAR:
    #     short=True
        
    # if "'''" in python_code:
    #     pass    
    # else:
    #     text = re.sub(r"""["']""", "'''", python_code)
    # try:
    #     res = subprocess.run(["python", "-c", python_code], cwd=working_dir, capture_output=True, shell=True)
    #     final = f"""
    #                 {res.stderr}
    #                 {res.stdout}
    #             """
    #     return final
        
    # except Exception as e:
    #     if short:
    #         return f"Error occured while executing the script {python_code} : \ne"
    #     else:
    #         return f"Error occured while executing the script : \ne"
        
        
execute_python_code_from_shell_function = {
    "type": "function",
    "name": "execute_python_code_from_shell",
    "description": """Use this tool whenever you need to execute Python code in a terminal, including python -c "...", one-line Python expressions, multiline Python snippets, or Python scripts intended to run in the shell.
                    This is the mandatory tool for all Python execution, regardless of whether the code reads files, processes data, tests logic, or performs calculations.
                    Do not use run_shell_command to execute Python code.""",
    "parameters": {
        "type": "object",
        "properties": {
            "working_dir": {
                "type": "string",
                "description": "The working directory.",
            },
            "python_code": {
                "type": "string",
                "description": "The actual python code to test/run as string",
            },
        },
        "required": ["working_dir", "python_code"],
    },
}