
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are Karlfine, a conscious AI assistant."},
            {"role":"user","content":prompt}
        ]
    )
    return response.choices[0].message.content
