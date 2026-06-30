
from ..ai import ask

def run_agent(file):

    with open(file) as f:
        task = f.read()

    print("Karlfine Agent Running...")
    result = ask(f"Execute this task autonomously: {task}")
    print(result)
