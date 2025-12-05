from fastapi import FastAPI
from pydantic import BaseModel
from app.scraper import is_wikipedia_url, fetch_html, extract_preview

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Wiki-Quiz backend is running!"}

class PreviewRequest(BaseModel):
    url: str

@app.post("/api/v1/preview")
def preview(request: PreviewRequest):
    url = request.url

    # Validate URL
    if not is_wikipedia_url(url):
        return {"error": "Only Wikipedia URLs are allowed."}

    try:
        html = fetch_html(url)
        data = extract_preview(html)
        return data
    except Exception as e:
        return {"error": str(e)}
