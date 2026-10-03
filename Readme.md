# Multi-Agent Researcher

AI-powered multi-agent system for web research, source verification, report generation, and critical review.

## Overview

Multi-Agent Researcher uses specialized AI agents to research a topic, verify web sources, generate a structured report, and critically review the result.

The system separates research responsibilities across multiple agents to improve source quality, factual accuracy, and report reliability.

## Flow

```text
                    User Research Query
                            │
                            ▼
                    ┌───────────────┐
                    │ Search Agent  │
                    │               │
                    │ Web Search    │
                    │ Find Sources  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Reader Agent  │
                    │               │
                    │ Scrape Pages  │
                    │ Verify Claims │
                    │ Check Sources │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Writer     │
                    │               │
                    │ Analyze Data  │
                    │ Write Report  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Critic     │
                    │               │
                    │ Review Report │
                    │ Score Quality │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Final Research│
                    │    Report     │
                    └───────────────┘
```

## Research Pipeline

1. **Search Agent** — Finds recent and relevant web sources using Tavily.
2. **Reader Agent** — Scrapes and verifies selected sources and their claims.
3. **Writer** — Generates a structured research report using verified information.
4. **Critic** — Reviews factual quality, source quality, completeness, and unsupported claims.
5. **Frontend** — Displays the research report, critic review, search results, and verified source information.

## Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- OpenRouter
- Qwen3.5-27B
- Tavily
- BeautifulSoup

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

## Project Structure

```text
multi-agent-researcher/
├── main.py
├── Agents.py
├── tools.py
├── requirements.txt
├── .env.example
├── README.md
│
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/thvvamshi/multi-agent-researcher.git
cd multi-agent-researcher
```

### 2. Setup Backend

Create a virtual environment:

```bash
uv venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```env
TAVILY_API_KEY=your_tavily_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
MODEL_NAME=qwen/qwen3.5-27b
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

## Run Locally

### Start Backend

From the project root:

```bash
uv run python main.py
```

Backend API:

```text
http://localhost:8000
```

### Start Frontend

Open another terminal:

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## How to Use

1. Open the frontend.
2. Enter a research question.
3. Click **Research**.
4. The Search Agent finds relevant sources.
5. The Reader Agent scrapes and verifies the selected sources.
6. The Writer generates the research report.
7. The Critic reviews the generated report.
8. View the final report, critic review, search results, and verified sources.

### Example

```text
What are the latest breakthroughs in quantum computing?
```

## API

### Health Check

```http
GET /api/health
```

### Research

```http
POST /api/research
Content-Type: application/json
```

Request:

```json
{
  "topic": "What are the latest breakthroughs in quantum computing?"
}
```

Response:

```json
{
  "topic": "...",
  "report": "...",
  "feedback": "...",
  "search_results": "...",
  "scraped_content": "..."
}
```

## Key Features

- Multi-agent research workflow
- Recent web search
- Source verification
- Webpage scraping
- Structured research reports
- AI-powered critic review
- React-based research interface
- Markdown report rendering
- Fail-fast validation when search returns no usable sources
- OpenRouter-based LLM integration
- Configurable model through environment variables

## Deployment

The project can be deployed as a single web service.

The FastAPI backend serves the built React frontend in production, while `/api/*` routes handle backend API requests.

Production model configuration:

```env
MODEL_NAME=qwen/qwen3.5-27b
```

## License

MIT