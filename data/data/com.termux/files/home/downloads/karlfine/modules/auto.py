
from ..ai import ask_ai

def run_auto(file):
    with open(file) as f:
        task = f.read()

    print("Running autonomous task...")
    result = ask_ai(task)
    print(result)
