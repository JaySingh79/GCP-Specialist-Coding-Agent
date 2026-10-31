import threading
import time
from rich.console import Console
from rich.prompt import Prompt
from queue import Queue, Empty
from src.main import history, agent_main


console = Console() 

class TerminalController:
    def __init__(self):
        self.running = True
        self.commands = Queue()

    def listen(self):
        """Continuously listen for terminal input."""

        console.print("\n[bold green]Listening bro..[/bold green]!\n")
        while self.running:
            
            try:
                command = Prompt.ask("[bold cyan]You > [/bold cyan]")

                if command.strip() == "/exit":
                    self.running = False
                    self.commands.put("/exit")
                    break

                # Ignore empty Enter
                if command.strip():
                    self.commands.put(command)

            except (EOFError, KeyboardInterrupt):
                self.running = False
                self.commands.put("/exit")
                break


def run_agent(controller: TerminalController):
    """Your actual coding-agent loop."""

    while controller.running:

        # ------------------------------------------------
        # 1. Check whether user sent a command
        # ------------------------------------------------

        try:
            command = controller.commands.get_nowait()
            if command == "/exit":
                break

            console.print(f"\n[bold purple]Recieved command : {command}[/bold purple]")
            console.print("\n[bold red]Agent working..[/bold red]")
            # Handle command here
            try:
                agent_main(command)
                
            except Exception as e:
                print(f'Some error occured : \n{e}')
            
        except Empty:
            pass

        # ------------------------------------------------
        # 2. Do agent work
        # ------------------------------------------------

        # Example agent operation
        time.sleep(2)

    console.print("\n[bold red]Agent stopped.[/bold red]")


def main():
    controller = TerminalController()

    # Input listener runs independently
    listener = threading.Thread(
        target=controller.listen,
        daemon=True
    )

    listener.start()

    # Main agent loop
    run_agent(controller)


if __name__ == "__main__":
    main()