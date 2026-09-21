import subprocess
import os
from pathlib import Path

def try_python_func():

    abs_dir = Path(__file__).resolve().parents[0]
    print(abs_dir)
    try: 
        print("start")
        res = subprocess.run(["python", "-m" ,"__init__"], cwd=abs_dir, capture_output=True, text=True)
        final = f"""
        Std Err: \n{res.stderr}\n
        Std Out: \n{res.stdout}\n
        """
        
        if res.stderr == "" and res.stdout == "":
            return f"Error - did not produce any output"
        
        elif res.returncode != 0:
            final+= f"program exited with code {res.returncode}"
            
        return final
            
    except Exception as e:
        return f"Error executing the file {e}"
    
    
print(try_python_func())



