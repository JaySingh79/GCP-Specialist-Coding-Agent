import os 

MAX_CHARS = 10000

def get_file_content(working_dir, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not a file"
    
    if not os.path.isfile(abs_file):
        return f"Error - {dir} is not a file"
    
    try:
        with open(abs_file, 'r') as f:
            file_content = f.read(MAX_CHARS)
            if len(file_content) >= MAX_CHARS:
                file_content += f"\n[file] truncated to {MAX_CHARS} characters"
                
        return file_content
    
    except Exception as e:
        return f"Exception reading file: {e}"
    
    
get_file_content_function = {
    "type": "function",
    "name": "get_file_content",
    "description": "Gets the content of a file.",
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