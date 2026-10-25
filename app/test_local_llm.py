import ollama


print("Starting local LLM test...")

response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Local LLM connection successful."
        }
    ],
)

print("Response received:")
print(response["message"]["content"])