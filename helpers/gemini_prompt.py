import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = client.chats.create(
    model="gemini-3.5-flash-lite"
)

def generate_verse(length, mood):
    prompt = f"Give me {length} word of a poem in a {mood} mood. No punctuation at the end."
    return chat.send_message(prompt).text

# Agents call generate_verse when a line is needed. Running it here
# would call the API on import.