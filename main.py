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


# FastAPI app setup
app = FastAPI(
    title="Multi-Agent AI Researcher",
    description=(
        "Multi-agent AI system for web research, "
        "source verification and report generation."
    ),
    version="1.0.0",
)


# Frontend build directory
# React/Vite creates the production build inside frontend/dist
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


# CORS setup
# Allow frontend and API communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class ResearchRequest(BaseModel):
    topic: str


# Response model
class ResearchResponse(BaseModel):
    topic: str
    report: str
    feedback: str
    search_results: str
    scraped_content: str


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # Current date - automatically updates every day/year
    current_date = date.today().strftime("%B %d, %Y")


    # STEP 1 - SEARCH
    # Search for recent and reliable sources
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


    # STEP 2 - READER
    # Scrape and independently verify the selected sources
    print("\n" + "=" * 50)
    print("STEP 2 - Reader Agent is verifying sources...")
    print("=" * 50)

    reader_result = build_reader_agent().invoke({
        "messages": [
            (
                "user",
                f"""
Research topic:
{topic}

Current date:
{current_date}

The Search Agent found these sources:

{state["search_results"]}

Select up to 3 of the most relevant and reliable URLs.

Prioritize sources in this order:

1. Official announcements / primary sources
2. Original research papers
3. Universities / research institutions
4. Reputable news organizations
5. Industry publications
6. Reliable secondary sources

For EACH selected URL:

1. Use the web_scrap tool.
2. Read the complete available webpage.
3. Verify that the URL is the correct article or source.
4. Verify the actual publication date.
5. Verify the important claims from the Search Agent.
6. Extract only facts directly supported by the webpage.
7. Check important numbers, names and dates.
8. Preserve uncertainty in the original source.
9. Mark the source VERIFIED, PARTIALLY VERIFIED or REJECTED.

IMPORTANT:

Do not treat a search-result summary as verified evidence.

If a webpage does not support an important claim:

- do not repeat that claim as fact
- mark the claim as unverified
- explain the problem in verification notes

Do not invent information.

Do not use URLs that were not provided by the Search Agent.

Do not modify URLs.

Return a final list of:

VERIFIED SOURCES
PARTIALLY VERIFIED SOURCES
REJECTED SOURCES
"""
            )
        ]
    })

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\nSCRAPED CONTENT:\n")
    print(state["scraped_content"])


    # STEP 3 - WRITER
    # Generate the final report only from verified research
    print("\n" + "=" * 50)
    print("STEP 3 - Writer is drafting the report...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n"
        f"{state['search_results']}\n\n"
        f"DETAILED VERIFIED RESEARCH:\n"
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
    # Review the final report for factual and source quality
    print("\n" + "=" * 50)
    print("STEP 4 - Critic is reviewing the report...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"],
    })

    print("\nCRITIC REPORT:\n")
    print(state["feedback"])


    # Return complete pipeline state
    return state


# API health check
@app.get("/api/health")
def health():

    return {
        "message": "Multi-Agent AI Researcher API is running",
        "status": "healthy",
    }


# Serve React application
@app.get("/")
def root():

    # Serve React application in production
    if FRONTEND_DIST.exists():

        return FileResponse(
            FRONTEND_DIST / "index.html"
        )

    return {
        "message": "Multi-Agent AI Researcher API is running",
        "status": "healthy",
    }


# Research API endpoint
@app.post(
    "/api/research",
    response_model=ResearchResponse,
)
def research(request: ResearchRequest):

    # Validate topic
    topic = request.topic.strip()

    if not topic:

        raise HTTPException(
            status_code=400,
            detail="Research topic cannot be empty.",
        )


    try:

        # Run research pipeline
        result = run_research_pipeline(topic)


        # Return research result
        return ResearchResponse(
            topic=topic,
            report=result["report"],
            feedback=result["feedback"],
            search_results=result["search_results"],
            scraped_content=result["scraped_content"],
        )


    except Exception as e:

        # Print backend error for debugging
        print(f"\nERROR: {str(e)}")


        # Return API error
        raise HTTPException(
            status_code=500,
            detail=f"Research pipeline failed: {str(e)}",
        )


# Serve React static assets
# This route is used only when the frontend has been built
if FRONTEND_DIST.exists():

    # Serve Vite generated assets
    app.mount(
        "/assets",
        StaticFiles(
            directory=FRONTEND_DIST / "assets"
        ),
        name="assets",
    )


    # Serve React application routes
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):

        # Do not intercept API routes
        if full_path.startswith("api/"):

            raise HTTPException(
                status_code=404,
                detail="API endpoint not found.",
            )


        # Requested frontend file
        requested_file = FRONTEND_DIST / full_path


        # Serve the file if it exists
        if requested_file.is_file():

            return FileResponse(
                requested_file
            )


        # React handles client-side routes
        return FileResponse(
            FRONTEND_DIST / "index.html"
        )


# RUN
if __name__ == "__main__":

    import os
    import uvicorn

    # Use Render's PORT in production
    # Fall back to 8000 for local development
    port = int(
        os.environ.get("PORT", 8000)
    )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )