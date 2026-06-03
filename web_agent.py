
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Groq client ready")
print("DuckDuckGo ready")
print("All imports loaded")


def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "No results found."

        output = ""

        for r in results:
            output += f"Title: {r['title']}\n"
            output += f"Summary: {r['body']}\n\n"

        return output

    except Exception as e:
        return f"Search error: {str(e)}"

print("Web search tool built")


#results = search_web("latest OpenAI announcements")
#print(results)

def calculate(expression):
    try:
        result = eval(expression)
        return f"Result: {result}"

    except Exception as e:
        return f"Calculation error: {str(e)}"

print("Calculator tool built")

#print(calculate("125 * 4 + 200"))
#print(calculate("2 ** 10"))
#print(calculate("(500 - 200) / 3"))
#print(calculate("999 * 365"))



def read_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read()

        return content

    except FileNotFoundError:
        return f"File '{filename}' not found."

    except Exception as e:
        return f"File read error: {str(e)}"

print("File reader tool built")

with open("notes.txt", "w") as f:
    f.write("My AI Agent Course Notes\n")
    f.write("Day 1 - Setup Python and VS Code\n")
    f.write("Day 2 - Connected to Groq API\n")
    f.write("Day 3 - Built memory and chat loop\n")
    f.write("Day 4 - Building tools today!\n")

#print("File created. Reading now...\n")

#print(read_file("notes.txt"))

def run_tool(agent_reply):
    if "search_web(" in agent_reply:
        try:
            query = agent_reply.split('search_web("')[1].split('"')[0]
            print(f"Searching: {query}")
            return search_web(query)

        except:
            return None

    elif "calculate(" in agent_reply:
        try:
            expression = agent_reply.split('calculate("')[1].split('"')[0]
            print(f"Calculating: {expression}")
            return calculate(expression)

        except:
            return None

    elif "read_file(" in agent_reply:
        try:
            filename = agent_reply.split('read_file("')[1].split('"')[0]
            print(f"Reading: {filename}")
            return read_file(filename)

        except:
            return None

    return None

print("Tool router ready")


memory = []

system_prompt = """
You are a helpful AI assistant named Rohi.

You have access to these tools:

- search_web("query") — search the internet
- calculate("expression") — solve math
- read_file("filename") — read a file

When a tool is needed, respond ONLY with the tool call.

Example:

search_web("latest AI news")

calculate("125 * 4")

read_file("notes.txt")

For normal questions, answer directly.
"""

def chat(user_input):
    memory.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *memory
        ]
    )

    reply = response.choices[0].message.content

    memory.append({"role": "assistant", "content": reply})

    return reply

print("Agent ready with all tools connected")


# ==========================================
# Tool Test 1 — Web Search
# ==========================================

print("=== Tool Test 1: Web Search ===")

reply = chat("Search for the latest news about Groq AI")
tool_result = run_tool(reply)

if tool_result:
    final = chat(f"Tool result: {tool_result}. Summarize in 3 bullet points.")
    print("Rohi:", final)
else:
    print("Rohi:", reply)


# ==========================================
# Tool Test 2 — Calculator
# ==========================================

print("\n=== Tool Test 2: Calculator ===")

reply = chat("Calculate 999 multiplied by 365")
tool_result = run_tool(reply)

if tool_result:
    final = chat(f"Tool result: {tool_result}. Give the user a clear answer.")
    print("Rohi:", final)
else:
    print("Rohi:", reply)


# ==========================================
# Tool Test 3 — File Reader
# ==========================================

print("\n=== Tool Test 3: File Reader ===")

reply = chat("Read the file notes.txt and summarize it")
tool_result = run_tool(reply)

if tool_result:
    final = chat(f"Tool result: {tool_result}. Summarize for the user.")
    print("Rohi:", final)
else:
    print("Rohi:", reply)