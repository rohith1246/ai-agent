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

DEPTH_CONFIG = {
    "quick":  {"max_results": 3,  "label": "Quick",  "detail": "concise and focused"},
    "deep":   {"max_results": 8,  "label": "Deep",   "detail": "detailed and thorough"},
    "expert": {"max_results": 12, "label": "Expert", "detail": "comprehensive, cite specific statistics and data points, include multiple perspectives"},
}


def search_web(query: str, max_results: int = 5) -> str:
    """Search DuckDuckGo and return formatted results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

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


def get_sources(query: str, max_results: int = 5) -> list[dict]:
    """Return structured source list for citations."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {"title": r["title"], "url": r.get("href", "#"), "snippet": r["body"]}
            for r in results
        ]
    except Exception as e:
        logger.error(f"Source fetch failed: {e}")
        return []


def write_report(topic: str, search_results: str, depth: str = "quick") -> str:
    """Synthesize search results into a structured report via Groq."""
    detail = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["quick"])["detail"]

    prompt = f"""You are a professional research analyst.

Based on the following search results about "{topic}", write a {detail} research report.

Search Results:
{search_results}

Write the report with exactly these sections using ## headings:

## Overview
## Key Facts
## Latest Developments
## Conclusion

Be professional. Use bullet points under Key Facts and Latest Developments."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    logger.info(f"Report generated for: {topic} [{depth}]")
    return response.choices[0].message.content


def save_report(topic: str, report: str) -> str:
    """Save report to the reports/ directory. Returns filename only."""
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in topic)
    filename = safe_name.lower().replace(" ", "-") + "-report.txt"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Research Report: {topic}\n")
        f.write("=" * 50 + "\n\n")
        f.write(report)

    logger.info(f"Report saved: {filepath}")
    return filename


def research_agent(topic: str, depth: str = "quick") -> dict:
    """Full pipeline: search → synthesize → save. Returns report data."""
    config = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["quick"])
    max_results = config["max_results"]

    logger.info(f"Starting research: {topic} [{depth}, {max_results} results]")

    search_results = search_web(topic, max_results=max_results)
    sources = get_sources(topic, max_results=max_results)
    report = write_report(topic, search_results, depth)
    filename = save_report(topic, report)

    return {
        "report": report,
        "filename": filename,
        "sources": sources,
        "depth": depth,
    }