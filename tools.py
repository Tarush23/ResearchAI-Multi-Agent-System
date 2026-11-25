from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """
    Search the web for relevant information on a topic.
    Returns titles, URLs and short content snippets.
    Use simple plain-text queries without quotation marks.
    """

    try:
        results = tavily.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )

        out = []

        for r in results["results"]:
            out.append(
                f"Title: {r['title']}\n"
                f"URL: {r['url']}\n"
                f"Snippet: {r['content'][:500]}\n"
            )
            
        if out : 
            return "\n----\n".join(out)
        else : return "No results found."

    except Exception as e:
        return f"Web search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """
    Extract readable text from a specific webpage.
    Accepts a single valid HTTP or HTTPS URL.
    Use this tool to read relevant webpages found using web_search.
    """

    try:
        if not url.startswith(("https://", "http://")):
            return "Invalid URL."

        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup([
            "script", "style", "nav", "footer",
            "header", "aside", "noscript"
        ]):
            tag.decompose()

        main_content = (
            soup.find("article")
            or soup.find("main")
            or soup.body
            or soup
        )

        text = main_content.get_text(
            separator=" ",
            strip=True
        )

        if not text:
            return "No readable content found."

        return f"Source: {url}\nContent: {text[:2000]}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"