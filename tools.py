import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
from rich import print


load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def search(query: str) -> str:
    """Search the web for recent and reliable information on a topic.
    Returns titles, URLs and concise snippets.
    """

    query = query.strip()

    # Prevent invalid Tavily queries containing only site: operators.
    words = query.split()

    non_site_terms = [
        word
        for word in words
        if not word.lower().startswith("site:")
    ]

    if not non_site_terms:
        return (
            "Invalid search query. The query contained only site: "
            "operators. Please retry with actual topic keywords."
        )

    try:
        result = tavily.search(
            query=query,
            max_results=5,
        )

        out = []

        for r in result.get("results", []):
            out.append(
                f"Title: {r.get('title', 'No title')}\n"
                f"URL: {r.get('url', 'No URL')}\n"
                f"Content: {r.get('content', '')[:250]}"
            )

        if not out:
            return "No relevant search results were found."

        return "\n---\n".join(out)

    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def web_scrap(url: str) -> str:
    """Scrape and return clean text content from a given URL
    for deeper reading.
    """

    try:
        res = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        res.raise_for_status()

        soup = BeautifulSoup(
            res.text,
            "html.parser",
        )

        for tag in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        return text[:5000]

    except Exception as e:
        return f"Couldn't scrape URL: {str(e)}"