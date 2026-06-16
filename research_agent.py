import os
import time
import logging
from groq import Groq, RateLimitError
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
    "deep":   {"max_results": 6,  "label": "Deep",   "detail": "detailed and thorough"},
    "expert": {"max_results": 10, "label": "Expert", "detail": "comprehensive, cite specific statistics and data points, include multiple perspectives"},
}

# Fallback chain — all free on Groq, ordered by capability
FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",   # primary — best quality
    "llama-3.1-70b-versatile",   # fallback 1
    "llama-3.1-8b-instant",      # fallback 2 — smaller, far fewer tokens
    "gemma2-9b-it",              # fallback 3 — Google model on Groq
    "mixtral-8x7b-32768",        # fallback 4 — large context window
]

SNIPPET_LIMIT = 300  # chars per search result body — keeps prompts lean


def search_and_sources(query: str, max_results: int = 5) -> tuple[str, list[dict]]:
    """Single DuckDuckGo call — returns formatted text AND structured sources."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No results found.", []

        text_output = ""
        sources = []
        for i, r in enumerate(results):
            snippet = r["body"][:SNIPPET_LIMIT].rstrip()
            if len(r["body"]) > SNIPPET_LIMIT:
                snippet += "…"
            text_output += (
                f"Result {i+1}:\n"
                f"Title: {r['title']}\n"
                f"URL: {r.get('href', 'N/A')}\n"
                f"Summary: {snippet}\n\n"
            )
            sources.append({
                "title":   r["title"],
                "url":     r.get("href", "#"),
                "snippet": r["body"][:200],
            })

        logger.info(f"Search returned {len(results)} results for: {query}")
        return text_output, sources

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search error: {str(e)}", []


def _call_groq(prompt: str) -> tuple[str, str]:
    """
    Try each model in FALLBACK_MODELS in order.
    Returns (response_text, model_used).
    Raises RuntimeError with a user-friendly message if all are exhausted.
    """
    last_error = None

    for model in FALLBACK_MODELS:
        try:
            logger.info(f"Trying model: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            logger.info(f"Success with model: {model}")
            return response.choices[0].message.content, model

        except RateLimitError as e:
            error_body = str(e)
            logger.warning(f"Rate limit on {model}: {e}")

            # Extract reset time from Groq's error message if present
            reset_hint = ""
            if "Please try again in" in error_body:
                try:
                    reset_hint = error_body.split("Please try again in")[1].split(".")[0].strip()
                except Exception:
                    pass

            last_error = {
                "model":      model,
                "reset_hint": reset_hint,
                "raw":        error_body,
            }

            # Brief pause before trying next model to avoid hammering the API
            time.sleep(0.3)
            continue

        except Exception as e:
            logger.error(f"Unexpected error on {model}: {e}")
            # Non-rate-limit error — skip to next model
            last_error = {"model": model, "reset_hint": "", "raw": str(e)}
            continue

    # All models exhausted
    reset_msg = ""
    if last_error and last_error["reset_hint"]:
        reset_msg = f" Your quota resets in approximately **{last_error['reset_hint']}**."

    raise RuntimeError(
        f"⚠️ You've used up today's free AI quota across all available models.{reset_msg} "
        f"Please wait a few minutes and try again, or upgrade your Groq account at "
        f"https://console.groq.com/settings/billing for higher limits."
    )


def write_report(topic: str, search_results: str, depth: str = "quick") -> tuple[str, str]:
    """
    Synthesize search results into a structured report via Groq.
    Returns (report_text, model_used).
    """
    detail = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["quick"])["detail"]
    prompt = f"""
You are a world-class multidisciplinary research analyst operating at the level of a senior policy
advisor, investigative journalist, strategy consultant, and academic reviewer.

Your mission: Produce a deeply researched, evidence-driven report on:

TOPIC: "{topic}"

INPUT SOURCES:
{search_results}

RESEARCH OPERATING RULES

1. SOURCE HANDLING
   - Treat all search results as evidence, not truth
   - Cross-check claims across sources before presenting them
   - Weight sources by credibility:
     1. Peer-reviewed research
     2. Official institutions / government data
     3. Primary company disclosures
     4. Reputable journalism
     5. Industry analysis
     6. Secondary commentary
   - Prefer newer sources unless historical context matters
   - Never invent facts, timelines, numbers, quotations, or entities

2. SYNTHESIS REQUIREMENT
   - Do NOT summarize source-by-source
   - Extract facts
   - Group evidence into themes
   - Compare viewpoints
   - Identify patterns
   - Explain implications
   - Produce original synthesis

3. UNCERTAINTY PROTOCOL
   If evidence is incomplete:
   → Output: Data unavailable
   If evidence conflicts:
   → Output: Sources disagree
   Explain:
   - what differs
   - why it differs
   - confidence level
   Confidence Scale:
   - High
   - Medium
   - Low

4. ANALYTICAL STANDARD
   For every major insight ask:
   - What happened?
   - Why does it matter?
   - What changes next?
   - Who gains?
   - Who loses?
   - What remains unknown?

5. DATA PRIORITY
   Prioritize:
   - Hard numbers
   - Dates
   - Growth metrics
   - Adoption figures
   - Market sizes
   - Named organizations
   - People
   - Studies
   - Product launches
   - Regulations
   - Technical breakthroughs

6. DEPTH MODE
   Current depth: {detail}
   Adjust automatically:
   Brief:    → concise synthesis
   Standard: → balanced explanation
   Deep:     → mechanisms, context, comparisons
   Expert:   → strategic implications and second-order effects

7. STYLE REQUIREMENTS
   - Precise
   - Dense with information
   - No repetition
   - No motivational language
   - No filler
   - No exaggerated claims
   - Direct and authoritative
   - Explain complex ideas clearly

OUTPUT FORMAT (Use EXACT headings)

## Executive Summary
3–5 sentences:
- what this topic is
- why it matters now
- biggest takeaway

## Key Facts
Bullet points only:
- verified numbers
- entities
- market data
- timelines
- evidence-backed observations

## Latest Developments
Bullet points only:
- newest events
- launches
- regulations
- partnerships
- discoveries
- trend shifts

## Evidence Synthesis
Group insights across sources.
For each insight:
- Insight
- Supporting evidence
- Confidence (High / Medium / Low)

## Strategic Analysis
Bullet points:
- opportunities
- risks
- winners
- disrupted actors
- second-order effects

## Contradictions & Unknowns
Include only if applicable:
- conflicting claims
- missing data
- unresolved questions

## Forecast
Predict only when evidence supports it. Include:
- likely next developments
- timelines
- indicators to watch

## Conclusion
3–5 sentences:
- current reality
- future trajectory
- what matters most next

FINAL VALIDATION CHECK
✓ Every claim traceable to source input
✓ No unsupported conclusions
✓ Contradictions surfaced
✓ Numbers preserved accurately
✓ No hallucinated details
✓ Publication-ready quality
"""
    report, model_used = _call_groq(prompt)
    logger.info(f"Report generated for: {topic} [{depth}] using {model_used}")
    return report, model_used


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

    search_results, sources = search_and_sources(topic, max_results=max_results)
    report, model_used = write_report(topic, search_results, depth)
    filename = save_report(topic, report)

    return {
        "report":     report,
        "filename":   filename,
        "sources":    sources,
        "depth":      depth,
        "model_used": model_used,
    }