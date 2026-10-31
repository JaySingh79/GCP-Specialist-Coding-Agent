from pathlib import Path
from datetime import datetime

exe_file = Path(__file__).resolve().parents[1] / "src" / "memory" / "execution_ledger.md"

def save_exe_ledger(content: str):
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(exe_file, "a") as f:
        f.write(f"UPDATE AT {timestamp}\n\n- {content}\n")
            
    return "content saved in execution ledger"

def load_exe_ledger():
    if exe_file.is_file():
        return exe_file.read_text(encoding="utf-8").strip()
        
    return "nothing in execution ledger yet"


save_exe_ledger_function = {
    "type": "function",
    "name": "save_exe_ledger",
    "description": """
                Use this tool to save the execution status.
            """,
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The content to be saved in todo file.",
            }
        },
        "required": ["content"],
    },
}