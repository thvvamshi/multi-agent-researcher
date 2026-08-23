import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
from rich import print


load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def search(query:str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    result = tavily.search(query=query,max_results=5)

    out = []
    for r in result["results"]:
        out.append(f"Title :{r["title"]}\nUrl : {r["url"]}\nContent: {r["content"][:500]}")
    return "\n---\n".join(out)


@tool
def web_scrap(url: str)-> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        res = requests.get(url,timeout=10,headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text,"html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ",strip=True)
        return text[:3000]
    except Exception as e:
        return f"couldn't scrape URL : {str(e)}"
