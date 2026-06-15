# AI Research Agent

> Autonomous AI agent that searches the web, synthesizes findings, and delivers structured research reports in seconds.

**Built by [Rohith Builds Labs](https://rohith-builds-labs.onrender.com) · [Live Demo →](https://ai-research-agent-0765.onrender.com/)**

---

## What it does

You give it a topic. It searches the web, reads the results, and writes a structured research report — Overview, Key Facts, Latest Developments, Conclusion — with cited sources. No copy-pasting. No manual searching. One click.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| AI Model | Groq API — LLaMA 3.3 70B |
| Search | DuckDuckGo Search API |
| Deployment | Render |

---

## Features

- **Autonomous research pipeline** — search → synthesize → report in one step
- **Source citations** — every report links back to its web sources
- **Structured reports** — consistent sections every time (Overview, Key Facts, Latest Developments, Conclusion)
- **Download as .txt** — export any report locally
- **Clean dark UI** — built for focus, not distraction

---

## Project Structure

```
ai-research-agent/
├── app.py                 # Flask routes
├── research_agent.py      # Core agent: search, synthesize, save
├── templates/
│   └── index.html         # Frontend UI
├── reports/               # Generated reports (auto-created)
├── .env                   # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/rohith1246/ai-agent.git
cd ai-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

**4. Run**
```bash
python app.py
```

Open `http://localhost:5000`

---

## Requirements

```
flask
groq
duckduckgo-search
python-dotenv
```

---

## How it works

```
User submits topic
       ↓
DuckDuckGo searches top 5 results
       ↓
URLs + snippets collected
       ↓
Groq LLaMA 3.3 70B synthesizes findings
       ↓
Structured report returned + saved
```

---

## API

**POST** `/research`

```bash
curl -X POST https://your-app.onrender.com/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Quantum computing 2025"}'
```

Response:
```json
{
  "success": true,
  "report": "## Overview\n...",
  "filename": "quantum-computing-2025-report.txt",
  "sources": [
    {
      "title": "IBM Quantum roadmap",
      "url": "https://...",
      "snippet": "..."
    }
  ]
}
```

**GET** `/download/<filename>`

Downloads the saved report as a `.txt` file.

---

## Deployment (Render)

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variable: `GROQ_API_KEY`
6. Deploy

---

## Roadmap

- [x] Web search via DuckDuckGo
- [x] Groq LLM synthesis
- [x] Source citations
- [x] Report download
- [ ] Research history (PostgreSQL)
- [ ] PDF export
- [ ] Multiple research modes (Quick / Deep / Expert)
- [ ] Public API with key authentication
- [ ] Multi-source search (Google, Bing, DDG)

---

## Part of Rohith Builds Labs

This project is one of several AI engineering products built under **Rohith Builds Labs** — a personal lab focused on production-grade AI applications.

[View all projects →](https://rohith-builds-labs.onrender.com)

---

## License

MIT