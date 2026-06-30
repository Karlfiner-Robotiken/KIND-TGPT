import subprocess

def ask_online(prompt):
    try:
        result = subprocess.check_output(["tgpt", prompt])
        return result.decode()
    except:
        return None
