from functions.get_file_content import get_file_content
from functions.get_files_info import get_file_info
from functions.write_file import write_file
from functions.run_python_file import run_python_file

def main():
    
    working_dir = "agent_building"
    # print(get_file_info(working_dir, 'agent_debugging.py'))
    # print(get_file_info(working_dir, 'data'))
    # print(get_file_info(working_dir, 'functions/get_file_info.py'))
    # print(write_file(working_dir, 'sample-2kb.txt', 'This is a test file content'))
    # print(write_file(working_dir, 'subdir/sample-2kb.txt', 'This is a test file content'))
    print(run_python_file(working_dir, dir='agent_building/main.py'))

    
if __name__ == '__main__':
    main()