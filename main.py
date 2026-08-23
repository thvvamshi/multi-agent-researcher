from datetime import date

from Agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain
)


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # Current date - automatically updates every day/year
    current_date = date.today().strftime("%B %d, %Y")


    # STEP 1 - SEARCH
    # This is for terminal use better UI
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
or similar time-sensitive information:

- Prioritize the newest available sources.
- Prefer sources published within the last few weeks or months.
- Check publication dates carefully.
- Do not use old information when newer information is available.
- Use older sources only when they provide useful background.
- Prefer primary sources when available.

IMPORTANT:

Return direct URLs to the specific articles or webpages
containing the information.

Do not return:
- generic homepages
- category pages
- search pages
- tag pages
- generic news landing pages

Only use URLs returned by the search tool.
"""
            )
        ]
    })

    state["search_results"] = search_result["messages"][-1].content

    print("\nSEARCH RESULTS:\n")
    print(state["search_results"])


    # STEP 2 - READER
    print("\n" + "=" * 50)
    print("STEP 2 - Reader Agent is scraping top resources...")
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

Select the 3 most relevant and reliable URLs.

Prioritize sources in this order:

1. Official announcements / primary sources
2. Reputable news organizations
3. Industry publications
4. Reliable secondary sources

For EACH selected URL:

1. Use the web_scrap tool.
2. Read the scraped webpage.
3. Verify that the webpage actually supports the information
   provided by the Search Agent.
4. Extract facts directly relevant to the research topic.
5. Identify important findings.
6. Check publication dates and important details.
7. Include the source title and URL.
8. Mark the source as VERIFIED or REJECTED.

If a URL is a generic homepage or does not contain the
information described by the Search Agent, reject it.

Do not invent information.
Do not use URLs that were not provided by the Search Agent.
Do not treat an unverified search summary as a confirmed fact.
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
        f"DETAILED SCRAPED CONTENT:\n"
        f"{state['scraped_content']}\n"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFINAL REPORT:\n")
    print(state["report"])


    # STEP 4 - CRITIC
    print("\n" + "=" * 50)
    print("STEP 4 - Critic is reviewing the report...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCRITIC REPORT:\n")
    print(state["feedback"])


    return state


# RUN
if __name__ == "__main__":

    topic = input("\nEnter the research topic: ")

    result = run_research_pipeline(topic)