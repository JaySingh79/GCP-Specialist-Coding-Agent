import threading
import time
from queue import Queue, Empty
from main import history, agent_main


class TerminalController:
    def __init__(self):
        self.running = True
        self.commands = Queue()

    def listen(self):
        """Continuously listen for terminal input."""
        while self.running:
            try:
                command = input()

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

            print(f"Received command: {command}")

            # Handle command here
            agent_main(command)

        except Empty:
            pass

        # ------------------------------------------------
        # 2. Do agent work
        # ------------------------------------------------

        print("Agent working...")

        # Example agent operation
        time.sleep(2)

    print("Agent stopped.")


def main():
    controller = TerminalController()

    # Input listener runs independently
    listener = threading.Thread(
        target=controller.listen,
        daemon=True
    )

    listener.start()

    print("Agent started.")
    print("Press Enter to continue.")
    print("Type /exit to stop.")

    # Main agent loop
    run_agent(controller)


if __name__ == "__main__":
    main()