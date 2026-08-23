# Multi-Agent Researcher

AI-powered multi-agent system for web research, source verification, and report generation.

## Overview

Multi-Agent Researcher uses specialized AI agents to research a topic, verify web sources, generate a structured report, and critically review the result.

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

1. **Search Agent** — Finds recent and relevant web sources.
2. **Reader Agent** — Scrapes and verifies selected sources.
3. **Writer** — Generates a structured research report using verified information.
4. **Critic** — Reviews factual quality, source quality, completeness, and unsupported claims.
5. **Frontend** — Displays the research progress, report, critic review, and sources.

## Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- Mistral AI
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
MISTRAL_API_KEY=your_mistral_api_key
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
4. The system searches and verifies sources.
5. The Writer generates the research report.
6. The Critic reviews the report.
7. View the final report, critic review, and sources.

### Example

```text
What are the latest breakthroughs in quantum computing?
```

## API

### Health Check

```http
GET /
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

## License

MIT