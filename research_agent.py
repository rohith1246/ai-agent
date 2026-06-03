from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Groq client ready")
print("DuckDuckGo ready")
print("Ready to build Research Agent")

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return "No results found."

        output = ""

        for i, r in enumerate(results):
            output += f"Result {i+1}:\n"
            output += f"Title: {r['title']}\n"
            output += f"Summary: {r['body']}\n\n"

        return output

    except Exception as e:
        return f"Search error: {str(e)}"

print("Search tool ready")

#test_results = search_web("Python programming language")

#print(test_results)


def write_report(topic, search_results):
    prompt = f"""
You are a research assistant.

Based on the following search results about "{topic}", write a detailed research report.

Search Results:
{search_results}

Write the report with exactly these sections:

1. Overview
2. Key Facts
3. Latest Developments
4. Conclusion

Be clear, detailed, and beginner friendly.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

print("Report writer ready")

def save_report(topic, report):
    filename = topic.lower().replace(" ", "-") + "-report.txt"

    with open(filename, "w") as f:
        f.write(f"Research Report: {topic}\n")
        f.write("=" * 50 + "\n\n")
        f.write(report)

    print(f"Report saved to {filename}")
    return filename

print("Save function ready")


def research_agent(topic):
    print(f"\nSearching the web for: {topic}")

    search_results = search_web(topic)
    print("Search complete")

    print("Writing report...")
    report = write_report(topic, search_results)
    print("Report written")

    print("Saving to file...")
    filename = save_report(topic, report)

    print("\n" + "=" * 50)
    print("REPORT PREVIEW (first 600 chars)")
    print("=" * 50)

    print(report[:600])
    print("\n...")

    print(f"\nFull report saved to: {filename}")


#print("Research agent ready")

#topic = input("Enter a topic for research: ")

#research_agent(topic)

import os

report_files = [f for f in os.listdir(".") if f.endswith("-report.txt")]

#print(f"You have generated {len(report_files)} research reports today:\n")
for f in report_files:
    size = os.path.getsize(f)
    #print(f"📄 {f} ({size} bytes)")