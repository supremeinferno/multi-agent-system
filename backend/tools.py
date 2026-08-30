from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def tavily_search(query: str) -> list:
    """Search the web using Tavily and return titles, URLs, and snippets."""

    response = tavily.search(
        query=query,
        max_results=5
    )

    return [
        {
            "title": result["title"],
            "url": result["url"],
            "snippet": " ".join(result.get("content", "").split()[:100])
        }
        for result in response["results"]
    ]


@tool
def scrape_webpage(url: str) -> str:
    """Scrape readable text from a webpage."""

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup([
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "form"
    ]):
        element.decompose()

    return soup.get_text(separator=" ", strip=True)