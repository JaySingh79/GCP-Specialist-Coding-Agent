import os

def get_file_info(working_dir, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not a file"
    
    final_response = ""
    contents = os.listdir()
    for content in contents:
        content_path = os.path.join(abs_dir, content)
        isdir = os.path.isdir(content_path)
        size = os.path.getsize(content_path)
        final_response += f"- {content}: file size={size} bytes, is_dir={isdir}"
    
    return final_response



get_file_info_function = {
    "type": "function",
    "name": "get_file_info",
    "description": "Gets information about files in a directory.",
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