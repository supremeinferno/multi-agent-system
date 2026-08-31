from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


@tool
def tavily_search(query: str) -> list:
    """Search the web using Tavily and return titles, URLs, and snippets."""

    try:
        response = tavily.search(
            query=query,
            max_results=5
        )

        return [
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": " ".join(
                    result.get("content", "").split()[:100]
                )
            }
            for result in response.get("results", [])
        ]

    except Exception as e:
        return [
            {
                "title": "Search Error",
                "url": "",
                "snippet": f"Unable to perform web search: {str(e)}"
            }
        ]


@tool
def scrape_webpage(url: str) -> str:
    """Scrape readable text from a webpage safely."""

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            },
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for element in soup([
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "aside",
            "form",
            "noscript"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if not text:
            return "No readable text could be extracted from this webpage."

        return text[:15000]

    except requests.exceptions.Timeout:
        return (
            "Unable to scrape this webpage because "
            "the request timed out."
        )

    except requests.exceptions.ConnectionError:
        return (
            "Unable to connect to this webpage. "
            "The website may be unreachable."
        )

    except requests.exceptions.HTTPError as e:
        return (
            f"Unable to scrape this webpage because "
            f"the website returned an HTTP error: {e}"
        )

    except requests.exceptions.RequestException as e:
        return (
            f"Unable to scrape this webpage: {str(e)}"
        )

    except Exception as e:
        return (
            f"Unexpected error while scraping webpage: {str(e)}"
        )