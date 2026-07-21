from crewai.tools import tool
from tavily import TavilyClient
from scrapegraph_py import ScrapeGraphAI, FetchConfig
from .pydantic_schemes import SearchResult
from helpers import get_settings


setting = get_settings()

search_client = TavilyClient(api_key=setting.TAVILY_API_KEY)
scraping_client = ScrapeGraphAI(api_key=setting.SCRAPGRAPH_API_KEY)

@tool
def search_engine_tool(query: str, no_websites: int=2, chunks_per_website: int=2):
    """Useful for search-based queries. Use this to find current information about any query related pages using a search engine"""
    
    return search_client.search(
        query=query,
        max_results=no_websites,
        search_depth='advanced',
        chunks_per_source=chunks_per_website
    )
    
@tool
def web_scraping_tool(page_url: str):
    
    """ An AI Tool to help an agent to scrape a web page to get text chunks that are relevant to user's query """
    
    details = scraping_client.extract(
        "Extract ```json\n" + SearchResult.schema_json() + "```\n From the web page",
        url=page_url,
        fetch_config=FetchConfig(stealth=True),
    )
    
    return {
        "page_url": page_url,
        "details": details
    }