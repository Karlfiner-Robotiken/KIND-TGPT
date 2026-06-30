
import json
import os

MEMORY_FILE = "memory.json"

def save(entry):
    if not os.path.exists(MEMORY_FILE):
        data=[]
    else:
        with open(MEMORY_FILE) as f:
            data=json.load(f)

    data.append(entry)

    with open(MEMORY_FILE,"w") as f:
        json.dump(data,f)
