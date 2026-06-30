
from rich.console import Console
from prompt_toolkit import prompt
from .ai import ask_ai

console = Console()

def main():
    console.print("[bold cyan]Karlfine AI Terminal[/bold cyan]")
    console.print("Type 'exit' to quit\n")

    while True:
        user = prompt("You > ")

        if user.lower() in ["exit","quit"]:
            break

        response = ask_ai(user)
        console.print(f"[green]Karlfine >[/green] {response}")

if __name__ == "__main__":
    main()
