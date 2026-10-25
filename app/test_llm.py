import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("API key loaded:", bool(api_key))
print("API key prefix:", api_key[:7] if api_key else "None")

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-5.6",
    input="Reply with exactly: LLM connection successful."
)

print(response.output_text)