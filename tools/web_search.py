import json
from typing import List, Dict, Optional

from duckduckgo_search import DDGS
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


def ddg_text_search(
    query: str,
    query_count: int = 3,
    region: str = "wt-wt",
    time_limit: Optional[str] = None,
) -> str:
    """
    Perform a DuckDuckGo text search with enhanced parameters.

    Args:
        query: Search query string
        query_count: Number of results to return (3-10)
        region: Region code for search results (e.g., "us-en", "uk-en")
        time_limit: Time filter ("d" for day, "w" for week, "m" for month, "y" for year)
    """
    try:
        results: List[Dict[str, str]] = DDGS().text(
            keywords=query,
            region=region,
            safesearch="strict",
            timelimit=time_limit,
            max_results=query_count,
        )
        return json.dumps(
            {"status": "success", "query": query, "results": results}, indent=2
        )
    except Exception as e:
        return json.dumps(
            {"status": "error", "message": str(e), "query": query}, indent=2
        )


class DDGTextSearchInput(BaseModel):
    query: str = Field(description="The search query to use for the text search")
    query_count: int = Field(
        default=3,
        description="The number of search results to return (3-10)",
        ge=3,
        le=10,
    )
    region: str = Field(
        default="wt-wt",
        description="Region code for search results (e.g., 'us-en', 'uk-en', 'wt-wt' for worldwide)",
    )
    time_limit: Optional[str] = Field(
        default=None,
        description="Time filter for results: 'd' (day), 'w' (week), 'm' (month), 'y' (year)",
    )


class DDGTextSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = """Performs web searches using DuckDuckGo's search engine.
    Useful for finding current information about topics, news, or general knowledge.
    Returns results in JSON format with title, link, and snippet for each result.
    Can filter by region and time limit."""
    args_schema: type[BaseModel] = DDGTextSearchInput

    def _run(
        self,
        query: str,
        query_count: int = 3,
        region: str = "wt-wt",
        time_limit: Optional[str] = None,
    ) -> str:
        return ddg_text_search(
            query=query, query_count=query_count, region=region, time_limit=time_limit
        )
