MAX_CHAR=10_000
MAX_CODE_CHAR=1_000

test_code = """

import os

def write_file(working_dir, dir, file_content):
    abs_dir = os.path.realpath(working_dir)
    abs_file = os.path.realpath(os.path.join(abs_dir, dir))
    try:
        if os.path.commonpath((abs_dir, abs_file)) != abs_dir:
            return f"Error {dir} is outside the working directory"
    except ValueError:
        return f"Error {dir} is outside the working directory"

    try:
        parent_dir = os.path.dirname(abs_file)
        os.makedirs(parent_dir, exist_ok=True)
        with open(abs_file, "w", encoding="utf-8") as f:
            f.write(file_content)
    except Exception as e:
        return f"Could not write to file {abs_file}: {e}"

    return f"Successfully wrote the content to {abs_file}"
    
        
        
write_file_function = {
    "type": "function",
    "name": "write_file",
    "description": "Writes content to a file.",
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
            "file_content": {
                "type": "string",
                "description": "contents to put in 'dir'",
            },
        },
        "required": ["working_dir", "dir", "file_content"],
    },
}
"""

print(len(test_code))