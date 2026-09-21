import os
import subprocess

def run_python_test_last_failed(working_dir, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not in the working directory"
    
    if not os.path.isfile(abs_file):
        return f"Error - {dir} is not a file"
    try:
        res = subprocess.run(["uv", "run", "pytest" "--last-failed"], cwd=abs_dir, capture_output=True, text=True)
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
        return f"Error executing tests"
    
    
def run_python_test(working_dir, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not in the working directory"
    
    if not os.path.isfile(abs_file):
        return f"Error - {dir} is not a file"
    try:
        res = subprocess.run(["uv", "run", "pytest"], cwd=abs_dir, capture_output=True, text=True)
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
        return f"Error executing tests"