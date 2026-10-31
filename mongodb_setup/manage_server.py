"""
Helper utility to start, stop, and check the status of the local MongoDB server (`mongod.exe`)
as a fully detached Windows background process so CLI commands return immediately.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from rich.console import Console

BASE_DIR = Path(__file__).resolve().parent.parent / "mongodb_env"
MONGOD_EXE = BASE_DIR / "bin" / "mongod.exe"
MONGOD_CFG = BASE_DIR / "mongod.cfg"
MONGO_URI = "mongodb://127.0.0.1:27017/"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_NO_WINDOW = 0x08000000

console = Console()


def is_running() -> bool:
    try:
        with MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500) as client:
            res = client.admin.command("ping")
            return res.get("ok") == 1.0
    except PyMongoError:
        return False


def start_server() -> None:
    if is_running():
        console.print("[green]MongoDB server is already running on 127.0.0.1:27017.[/green]")
        return

    if not MONGOD_EXE.exists():
        raise FileNotFoundError(f"mongod.exe not found at {MONGOD_EXE}")

    # Use WMI process creation to cleanly break out of parent Job Objects / subshells
    cmd_line = f'"{MONGOD_EXE}" --config "{MONGOD_CFG}"'
    ps_cmd = (
        f"Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
        f"-Arguments @{{CommandLine = '{cmd_line}'}} | Out-Null"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        check=True,
        capture_output=True,
    )

    for _ in range(20):
        if is_running():
            console.print("[bold green]MongoDB server started in detached mode (127.0.0.1:27017).[/bold green]")
            return
        time.sleep(0.5)

    raise RuntimeError("Timed out waiting for MongoDB server to accept connections on 127.0.0.1:27017.")


def stop_server() -> None:
    if not is_running():
        console.print("[yellow]MongoDB server is not currently running.[/yellow]")
        return

    try:
        with MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000) as client:
            client.admin.command("shutdown", 1)
    except PyMongoError:
        # shutdown command closes the socket immediately, which raises an expected AutoReconnect/ConnectionFailure
        pass

    for _ in range(10):
        if not is_running():
            console.print("[bold yellow]MongoDB server stopped cleanly.[/bold yellow]")
            return
        time.sleep(0.5)


def status_server() -> None:
    if is_running():
        with MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000) as client:
            info = client.server_info()
            dbs = client.list_database_names()
        console.print(
            f"[bold green]ONLINE[/bold green] | MongoDB v{info.get('version')} | "
            f"URI: {MONGO_URI} | Databases: {', '.join(dbs)}"
        )
    else:
        console.print("[bold red]OFFLINE[/bold red] | No MongoDB server responding on 127.0.0.1:27017.")


if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action == "start":
        start_server()
    elif action == "stop":
        stop_server()
    elif action == "status":
        status_server()
    else:
        console.print(f"[red]Unknown command: {action}. Use 'start', 'stop', or 'status'.[/red]")
        sys.exit(1)
