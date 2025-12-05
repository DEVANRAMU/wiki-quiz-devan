import requests
from bs4 import BeautifulSoup
import re

def is_wikipedia_url(url: str) -> bool:
    return "wikipedia.org" in url.lower()

def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }
    )
    response.raise_for_status()
    return response.text

from bs4 import BeautifulSoup
import re

def extract_preview(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # Extract the <title>
    title = soup.find("h1", {"id": "firstHeading"})
    title_text = title.get_text(strip=True) if title else "Untitled"

    # Extract first meaningful paragraph
    paragraphs = soup.select("div.mw-parser-output > p")

    summary = ""
    for p in paragraphs:
        text = p.get_text(strip=True)

        # Skip empty & irrelevant paragraphs
        if (
            not text 
            or len(text) < 50           # skip very short lines
            or text.lower().startswith(("redirects here", "coordinates"))
        ):
            continue

        summary = text
        break

    return {
        "title": title_text,
        "summary": summary
    }

