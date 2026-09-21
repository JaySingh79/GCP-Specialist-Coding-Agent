import ast

with open("risk_commands.json", 'r') as f:
    restrict_commands = f.read()
    
print(type(eval(restrict_commands)))