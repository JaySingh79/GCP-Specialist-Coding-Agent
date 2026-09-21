import sys
from pathlib import Path

path = Path(__file__).resolve().parents[0]
if str(path) not in sys.path:
    sys.path.insert(0, str(path))
    

print(path, sys.

# sys.path.append(__file__)