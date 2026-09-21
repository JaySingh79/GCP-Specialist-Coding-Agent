import os

def write_new_file(working_dir, file_name_dir:str, file_content):
    abs_dir = os.path.realpath(working_dir)
    abs_file = os.path.realpath(os.path.join(abs_dir, file_name_dir))
    
    try:
        if os.path.commonpath((abs_dir, abs_file)) != abs_dir:
            return f"Error {dir} is outside the working directory"
    except ValueError:
        return f"Error {dir} is outside the working directory"

    try:
        if os.path.exists(abs_file):
            return f"File with name {file_name} already exists at {abs_file}"
        parent_dir = os.path.dirname(abs_file)
        os.makedirs(parent_dir, exist_ok=True)
        with open(abs_file, "x", encoding="utf-8") as f:
            f.write(file_content)
    except Exception as e:
        return f"Could not write to file {abs_file}: {e}"

    return f"Successfully wrote the content to {abs_file}"
    
        
        
write_new_file_function = {
    "type": "function",
    "name": "write_new_file",
    "description": "Writes content to a file.",
    "parameters": {
        "type": "object",
        "properties": {
            "working_dir": {
                "type": "string",
                "description": "The working directory.",
            },
            "file_name_dir": {
                "type": "string",
                "description": "The new file path, e.g. ./src/main.py",
            },
            "file_content": {
                "type": "string",
                "description": "the content to write in new file",
            },
        },
        "required": ["working_dir", "file_name_dir", "file_content"],
    },
}