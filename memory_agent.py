from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Groq client ready")
print("Ready to build memory")

system_prompt = """
You are a helpful AI assistant named Rohi.
You are friendly, concise, and always answer clearly.
You remember everything the user tells you in this conversation.
When you do not know something, you say so honestly.
"""

print("System prompt set")
print("Agent name: Rohi")
print("Personality: Friendly and concise")


example_memory = [
    {"role": "user", "content": "My name is Rohith"},
    {"role": "assistant", "content": "Nice to meet you Rohith! How can I help you today?"},
    {"role": "user", "content": "What is my name?"},
    {"role": "assistant", "content": "Your name is Rohith, you just told me!"}
]

print("Memory contains", len(example_memory), "messages")
print()

for msg in example_memory:
    print(f"{msg['role'].upper()}: {msg['content']}")
    

memory = []

def chat(user_input):
    # Add user message to memory
    memory.append({"role": "user", "content": user_input})

    # Send full memory to Groq every time
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *memory
        ]
    )

    reply = response.choices[0].message.content

    # Add agent reply to memory
    memory.append({"role": "assistant", "content": reply})

    return reply

print("Memory initialized")
print("Chat function ready")

question1 = "Hi! My name is Rohith and I am building an AI agent."
print("You:", question1)

reply1 = chat(question1)
print("Rohi:", reply1)

print()

# Message 2
question2 = "What is my name and what am I building?"
print("You:", question2)

reply2 = chat(question2)
print("Rohi:", reply2)

print()
print("Memory now has", len(memory), "messages stored")

print("=== MEMORY CONTENTS ===")
print()

for i, msg in enumerate(memory):
    print(f"Message {i+1} — {msg['role'].upper()}")
    print(msg['content'])
    print("-" * 40)  
    
    
def save_memory():
    with open("memory.json", "w") as f:
        json.dump(memory, f, indent=2)

    print(f"Memory saved to memory.json ({len(memory)} messages)")

save_memory()


def load_memory():
    global memory

    try:
        with open("memory.json", "r") as f:
            memory = json.load(f)

        print(f"Memory loaded — {len(memory)} messages restored")

    except FileNotFoundError:
        print("No saved memory found. Starting fresh.")

load_memory()


# Reset memory for a fresh conversation
memory = []

print("Rohi is ready. Type 'quit' to exit and save.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        save_memory()
        print("Rohi: Goodbye! See you next time.")
        break

    if not user_input.strip():
        continue

    reply = chat(user_input)
    print(f"Rohi: {reply}\n")