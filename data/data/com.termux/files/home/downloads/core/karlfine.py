import os

def think(prompt):
    return os.popen(f"~/karlfine/llama.cpp/main -m ~/karlfine/models/tiny.gguf -p '{prompt}' -n 120").read()

print("KARLFINE OFFLINE AI READY")

while True:
    q = input("You: ")
    if q == "exit":
        break
    print("Karlfine:", think(q))
