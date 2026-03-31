from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="КАК У ТЕБЯ ДЕЛА ТУПОЙ УШЛËПОК?"
)
print(response.text)
print("NPTHING")