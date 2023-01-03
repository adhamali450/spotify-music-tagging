from rich.console import Console

console = Console()


def show_progress(action, message):
    with console.status(f"[bold green]{message}") as status:
        action()


def log(message):
    console.log(message)
