from pathlib import Path
from datetime import datetime

memory_file = Path(__file__).resolve().parents[1] / "src" / "memory" / "lt_memory.md"

def save_memory(content: str):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(memory_file, "a") as f:
        f.write(f"UPDATED at {timestamp}\n\n- {content}\n")
            
    return "content saved in memory"

def load_memory():
    if memory_file.is_file():
        return memory_file.read_text(encoding="utf-8").strip()
        
    return "nothing in memory yet"


save_memory_function = {
    "type": "function",
    "name": "save_memory",
    "description": """
                Use this tool when you want to save some content in memory.
            """,
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The content to be saved in memory.",
            }
        },
        "required": ["content"],
    },
}