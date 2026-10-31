from pathlib import Path
from datetime import datetime

todo_file = Path(__file__).resolve().parents[1] / "src" / "memory" / "todo.md"

def save_todo(content: str):
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(todo_file, "a") as f:
        f.write(f"UPDATE AT {timestamp}\n\n- {content}\n")
            
    return "content saved in todo"

def load_todo():
    if todo_file.is_file():
        return todo_file.read_text(encoding="utf-8").strip()
        
    return "nothing in todo yet"


save_todo_function = {
    "type": "function",
    "name": "save_todo",
    "description": """
                Use this tool when you to save todo plan.
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