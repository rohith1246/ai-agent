print("Hello, World!")
try:
    import groq
    print("groq is ready")
except ImportError:
    print("groq not installed")

try:
    import dotenv
    print("python-dotenv is ready")
except ImportError:
    print("python-dotenv not installed")

try:
    from duckduckgo_search import DDGS
    print("duckduckgo-search is ready")
except ImportError:
    print("duckduckgo-search not installed")

try:
    import flask
    print("flask is ready")
except ImportError:
    print("flask not installed")

print("\nAll libraries ready! You are set for Day 2.")


from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if api_key:
    print("API key loaded successfully")
    print(f"Key starts with: {api_key[:8]}...")
else:
    print("API key not found. Check your .env file.")
    
    
    
from groq import Groq

client = Groq(api_key=api_key)

print("Groq client ready")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello and tell me what you can do in 3 bullet points."}
    ]
)

print(response.choices[0].message.content)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "What is 2 + 2?"}
    ]
)

print("Model used:", response.model)
print("Tokens used:", response.usage.total_tokens)
print("Response:", response.choices[0].message.content)

def ask(question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

print("Q1:", ask("What is Python in one sentence?"))
print()
print("Q2:", ask("What is an API in one sentence?"))
print()
print("Q3:", ask("What is Groq in one sentence?"))
