import os

def make_changes(working_dir, changes, dir='.'):
    
    abs_dir = os.path.abspath(working_dir)
    abs_file = os.path.abspath(os.path.join(working_dir, dir))
    if not abs_file.startswith(abs_dir):
        return f"Error {dir} is not a file"
    
    if not os.path.isfile(abs_file):
        return f"Error - {dir} is not a file"
    
    with open(abs_file, 'w') as f:
        content = f.write(changes)
        