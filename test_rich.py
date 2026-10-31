from rich import print

from time import sleep
from rich.console import Console
from rich.markdown import Markdown

print("Hello, [bold green]Geeks[/bold green]!")
console = Console()
with open("life copy.md") as readme:
    markdown = Markdown(readme.read())
console.print(markdown)