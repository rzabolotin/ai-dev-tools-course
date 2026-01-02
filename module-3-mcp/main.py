from fastmcp import FastMCP
import requests

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def fetch_web_content(url: str) -> str:
    """Fetch web page content as markdown using r.jina.ai

    Args:
        url: The URL of the web page to fetch

    Returns:
        The content of the web page in markdown format
    """
    jina_url = f"https://r.jina.ai/{url}"
    response = requests.get(jina_url)
    response.raise_for_status()
    return response.text

@mcp.tool
def web_fetch(url: str) -> str:
    """Fetch web page content as markdown using r.jina.ai

    Args:
        url: The URL of the web page to fetch

    Returns:
        The content of the web page in markdown format
    """
    return fetch_web_content(url)

if __name__ == "__main__":
    mcp.run()