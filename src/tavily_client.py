import os
from tavily import TavilyClient
from typing import List, Dict

class TavilySearch:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not set")
        self.client = TavilyClient(api_key=self.api_key)

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        # returns list of dict with title, url, snippet
        resp = self.client.search(query=query, max_results=max_results)
        out = []
        # Tavily-python client structures may vary; adapt if needed
        for r in resp.get("results", []):
            out.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "snippet": r.get("snippet") or r.get("description")
            })
        # Fallback: if direct results are returned as a list
        if not out and isinstance(resp, list):
            for r in resp:
                out.append({"title": r.get("title"), "url": r.get("url"), "snippet": r.get("snippet", "")})
        return out