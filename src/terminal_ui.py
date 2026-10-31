import sys
from pathlib import Path
import asyncio
import threading

path = Path(__file__).resolve().parents[1]
if str(path) not in sys.path:
    sys.path.insert(0, str(path))

from main import agent_main
from rich.console import Console
from rich.panel import Panel

console = Console()

console.print(
    "\n[bold magenta]Welcome to the Coding Agent Terminal![/bold magenta]"
)

class AgentTerminal:
    def __init__(self):
        self.running = True
        self.pause = threading.Event()
        self.pause.set()
        self.stop = threading.Event()
        self.worker = None

    async def get_input(self, func, *args, **kwargs):
        while self.running:
            try:
                command = input("\n\033[96m❯ \033[0m")
                command = command.strip()

                if not command:
                    continue

                if command == "/pause":
                    self.pause.clear()
                    console.print("[yellow]Agent paused.[/yellow]")
                    continue

                if command == "/resume":
                    self.pause.set()
                    console.print("[green]Agent resumed.[/green]")
                    continue

                if command == "/stop":
                    self.stop.set()
                    console.print("[red]Stop requested.[/red]")
                    continue

                if command == "/exit":
                    self.stop.set()
                    self.running = False
                    break 

                # Avoid overlapping agent executions.
                if self.worker and not self.worker.done():
                    console.print(
                        "[yellow]Agent is busy. Wait for it to finish.[/yellow]"
                    )
                    continue

                self.stop.clear()
                self.pause.set()

                self.worker = asyncio.create_task(
                    asyncio.to_thread(func, command, *args, **kwargs)
                )

                await self.worker
            except (EOFError, KeyboardInterrupt):
                self.stop.set()
                self.running = False
                break

        # if self.worker and not self.worker.done():
        #     await self.worker

        console.print("[bold red]Agent stopped.[/bold red]")

    def process_command(self, command):
        # console.print(
        #     Panel(
        #         command,
        #         title="[cyan]User instruction[/cyan]",
        #         expand=False,
        #         padding=(0, 1),
        #     ),
        #     width=min(console.width - 4, 80),
        # )

        try:
            response = agent_main(command, self.pause, self.stop)

            # Handle generator-based agent functions.
            # if hasattr(response, "__next__"):
            #     response = list(response)

            console.print(
                f"[bold green]Agent:[/bold green] {response}"
            )

        except Exception as exc:
            console.print(f"[bold red]Agent error:[/bold red] {exc}")


if __name__ == "__main__":
    terminal = AgentTerminal()
    asyncio.run(terminal.get_input())