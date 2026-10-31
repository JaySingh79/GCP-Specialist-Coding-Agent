import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console
from rich.panel import Panel

console = Console()

async def main():
    session = PromptSession("❯ ")

    while True:
        with patch_stdout():
            text = await session.prompt_async()

        with patch_stdout():
            console.print(Panel(text, title="[cyan]User instruction[/cyan]"))

asyncio.run(main())