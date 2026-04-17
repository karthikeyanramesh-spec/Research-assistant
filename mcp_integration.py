
from mcp import Tool
import requests
import os 
from dotenv import load_dotenv
from scrapping import scraper_agent
from maincrew import run_crew
from modeselection import build_query

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
def serper_search_func(input: dict):
    query = input["query"]
    mode = input["mode"]

    search_query = build_query(query, mode)

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"q": search_query}, headers=headers)
    data = response.json()

    return [item["link"] for item in data.get("organic", [])]

def scraper_func(input: dict):
    urls = input["urls"]
    return scraper_agent(urls)

def crewai_func(input: dict):
    return run_crew({
        "query": input["query"],
        "mode": input["mode"],
        "data": input["data"]
    })

serper_tool = Tool(
    name="serper",
    description="Search URLs using Serper API",
    func=serper_search_func,
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "mode": {"type": "string"}
        },
        "required": ["query", "mode"]
    }
)

scrape_tool = Tool(
    name="scrape",
    description="Scrape URLs using Playwright",
    func=scraper_func,
    inputSchema={
        "type": "object",
        "properties": {
            "urls": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["urls"]
    }
)

generate_tool = Tool(
    name="generate",
    description="Generate answer using CrewAI",
    func=crewai_func,
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "mode": {"type": "string"},
            "data": {"type": "array"}
        },
        "required": ["query", "mode", "data"]
    }
)


tools = {
    "serper": serper_tool,
    "scrape": scrape_tool,
    "generate": generate_tool
}