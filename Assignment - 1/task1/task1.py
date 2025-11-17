
import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from ddgs import DDGS
import os
import dotenv
dotenv.load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

logfire.configure()
logfire.instrument_pydantic_ai()

class ResearchOutput(BaseModel):
    summary: str = Field(description="A concise summary of the research findings")
    key_facts: list[str] = Field(description="A list of 3-5 key facts extracted from the research")
    sources: list[str] = Field(description="List of source URLs or references used")

research_agent = Agent(
    'google-gla:gemini-2.5-flash',
    output_type=ResearchOutput,
    instructions=(
        "You are a research agent specialized in gathering and summarizing information. "
        "Use the web_search tool to fetch relevant data from the internet. "
        "Always cite sources and structure your output according to the schema."
    ),
)

@research_agent.tool
def web_search(ctx: RunContext, query: str) -> str:
    """Perform a web search for the given query and return a string with the top results."""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5) 
        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}\n")
    return "\n".join(formatted_results)

if __name__ == "__main__":
    print("Research Agent (type 'exit' to quit)")
    while True:
        query = input("Enter your research query: ")
        if query.strip().lower() == 'exit':
            print("Exiting.")
            break
        print(f"Running research agent for query: {query}")
        result = research_agent.run_sync(query)
        print("Research Output:")
        print(result.output)