from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from Agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


app = FastAPI(
    title="Multi-Agent AI Researcher",
    description=(
        "Multi-agent AI system for web research, "
        "source verification and report generation."
    ),
    version="1.0.0",
)


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    topic: str
    report: str
    feedback: str
    search_results: str
    scraped_content: str


def run_research_pipeline(topic: str) -> dict:
    state = {}

    current_date = date.today().strftime("%B %d, %Y")

    # STEP 1 - SEARCH
    print("\n" + "=" * 50)
    print("STEP 1 - Search Agent is working...")
    print("=" * 50)

    search_result = build_search_agent().invoke({
        "messages": [
            (
                "user",
                f"""
Research topic:
{topic}

Current date:
{current_date}

Find recent, reliable and detailed information about this topic.

If the topic asks for recent, latest, new, today, this week,
this month, or similar time-sensitive information:

- Prioritize the newest available sources.
- Prefer sources published within the last few weeks or months.
- Check publication dates carefully.
- Never assume a fixed year.
- Do not use old information when newer reliable information
  is available.
- Use older sources only when they provide useful background.
- Prefer primary sources when available.

IMPORTANT:

Return direct URLs to the specific articles, papers or webpages
containing the information.

Do not return:

- generic homepages
- category pages
- search pages
- tag pages
- generic news landing pages

Only use URLs returned by the search tool.

For every source provide:

- Title
- Direct URL
- Short factual summary
- Publication date if available
- Source type
"""
            )
        ]
    })

    state["search_results"] = search_result["messages"][-1].content

    print("\nSEARCH RESULTS:\n")
    print(state["search_results"])


    # STEP 2 - READER / VERIFICATION
    print("\n" + "=" * 50)
    print("STEP 2 - Reader Agent is verifying sources...")
    print("=" * 50)

    reader_result = build_reader_agent().invoke({
        "messages": [
            (
                "user",
                f"""
Topic:
{topic}

Current date:
{current_date}

Search results:
{state["search_results"]}

Select up to 3 of the most relevant and reliable URLs.

Prioritize:

1. Official announcements / primary sources
2. Original research papers
3. Universities / research institutions
4. Reputable news organizations
5. Industry publications
6. Reliable secondary sources

For EACH selected URL:

1. Use the web_scrap tool.
2. Read the webpage content.
3. Verify that the URL is the correct article or source.
4. Verify the important claims from the Search Agent.
5. Verify the actual publication date.
6. Check important numbers, names and dates.
7. Extract only facts directly supported by the webpage.
8. Preserve uncertainty in the original source.
9. Mark the source VERIFIED, PARTIALLY VERIFIED or REJECTED.

IMPORTANT:

Do not treat a search-result summary as verified evidence.

If a webpage does not support an important claim:

- do not repeat that claim as fact
- mark the claim as unverified
- explain the problem

Do not invent information.

Do not use URLs that were not provided by the Search Agent.

Do not modify URLs.

For numerical claims:

- Check whether numbers are internally consistent.
- For sports results, verify that scores match the stated
  winning margin.
- If the source appears inconsistent, flag the issue.
- Do not silently invent a correction.

Return:

SOURCE:
Title:
URL:
Verification:
Actual Date:
Source Type:

IMPORTANT FINDINGS:
- ...

VERIFIED FACTS:
- ...

CLAIMS NOT VERIFIED:
- ...

VERIFICATION NOTES:
- ...

Then provide:

VERIFIED SOURCES:
- ...

PARTIALLY VERIFIED SOURCES:
- ...

REJECTED SOURCES:
- ...
"""
            )
        ]
    })

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\nSCRAPED CONTENT:\n")
    print(state["scraped_content"])


    # STEP 3 - WRITER
    print("\n" + "=" * 50)
    print("STEP 3 - Writer is drafting the report...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n"
        f"{state['search_results']}\n\n"
        f"VERIFIED RESEARCH:\n"
        f"{state['scraped_content']}\n"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "current_date": current_date,
        "research": research_combined,
    })

    print("\nFINAL REPORT:\n")
    print(state["report"])


    # STEP 4 - CRITIC
    print("\n" + "=" * 50)
    print("STEP 4 - Critic is reviewing the report...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"],
        "research": state["scraped_content"],
    })

    print("\nCRITIC REPORT:\n")
    print(state["feedback"])


    return state

# API
@app.get("/api/health")
def health():
    return {
        "message": "Multi-Agent AI Researcher API is running",
        "status": "healthy",
    }


@app.get("/")
def root():
    if FRONTEND_DIST.exists():
        return FileResponse(FRONTEND_DIST / "index.html")

    return {
        "message": "Multi-Agent AI Researcher API is running",
        "status": "healthy",
    }


@app.post("/api/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    topic = request.topic.strip()

    if not topic:
        raise HTTPException(
            status_code=400,
            detail="Research topic cannot be empty.",
        )

    try:
        result = run_research_pipeline(topic)

        return ResearchResponse(
            topic=topic,
            report=result["report"],
            feedback=result["feedback"],
            search_results=result["search_results"],
            scraped_content=result["scraped_content"],
        )

    except Exception as e:
        import traceback

        print("\n" + "=" * 50)
        print("FULL ERROR")
        print("=" * 50)
    
        print(f"\nERROR TYPE: {type(e).__name__}")
        print(f"ERROR: {str(e)}")
    
        print("\nFULL TRACEBACK:")
        traceback.print_exc()
    
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {str(e)}",
        )


# FRONTEND STATIC FILES
if FRONTEND_DIST.exists():

    app.mount(
        "/assets",
        StaticFiles(
            directory=FRONTEND_DIST / "assets"
        ),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):

        if full_path.startswith("api/"):
            raise HTTPException(
                status_code=404,
                detail="API endpoint not found.",
            )

        requested_file = FRONTEND_DIST / full_path

        if requested_file.is_file():
            return FileResponse(requested_file)

        return FileResponse(
            FRONTEND_DIST / "index.html"
        )


# LOCAL SERVER
if __name__ == "__main__":
    import os
    import uvicorn

    port = int(
        os.environ.get("PORT", 8000)
    )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )