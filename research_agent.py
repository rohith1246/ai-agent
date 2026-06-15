import os
import logging
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def search_web(query: str) -> str:
    """Search DuckDuckGo and return formatted results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return "No results found."

        output = ""
        for i, r in enumerate(results):
            output += f"Result {i+1}:\n"
            output += f"Title: {r['title']}\n"
            output += f"URL: {r.get('href', 'N/A')}\n"
            output += f"Summary: {r['body']}\n\n"

        logger.info(f"Search returned {len(results)} results for: {query}")
        return output

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search error: {str(e)}"


def get_sources(query: str) -> list[dict]:
    """Return structured source list for citations."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return [
            {"title": r["title"], "url": r.get("href", "#"), "snippet": r["body"]}
            for r in results
        ]
    except Exception as e:
        logger.error(f"Source fetch failed: {e}")
        return []


def write_report(topic: str, search_results: str) -> str:
    """Synthesize search results into a structured report via Groq."""
    prompt = f"""You are a professional research analyst.

Based on the following search results about "{topic}", write a detailed research report.

Search Results:
{search_results}

Write the report with exactly these sections:

## Overview
## Key Facts
## Latest Developments
## Conclusion

Be clear, detailed, and professional. Use bullet points where appropriate."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    logger.info(f"Report generated for: {topic}")
    return response.choices[0].message.content


def save_report(topic: str, report: str) -> str:
    """Save report to the reports/ directory. Returns filename (not full path)."""
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in topic)
    filename = safe_name.lower().replace(" ", "-") + "-report.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Research Report: {topic}\n")
        f.write("=" * 50 + "\n\n")
        f.write(report)

    logger.info(f"Report saved: {filepath}")
    return filename


def research_agent(topic: str) -> dict:
    """Full pipeline: search → synthesize → save. Returns report data."""
    logger.info(f"Starting research: {topic}")

    search_results = search_web(topic)
    sources = get_sources(topic)
    report = write_report(topic, search_results)
    filename = save_report(topic, report)

    return {
        "report": report,
        "filename": filename,
        "sources": sources,
    }