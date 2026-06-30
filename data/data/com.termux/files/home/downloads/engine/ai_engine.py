from ai.tgpt_bridge import ask_online

def run_ai(input_data):
    response = ask_online(input_data)
    if not response:
        return "Offline fallback not configured yet."
    return response
