from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv('.env')
def create_news_agent(profession: str, specialty: str = None):
    
    SCIENCE_DOMAINS = [
        "pubmed.ncbi.nlm.nih.gov",
        "sciencedirect.com",
        "nature.com",
        "thelancet.com",
        "nejm.org",
        "https://www.medscape.com/", 
        "jamanetwork.com",
        "science.org",
        "cell.com",
        "bmj.com",
        "springer.com"
    ]
    # Date context
    today = datetime.now().strftime("%Y-%m-%d")
    date_note = f"Current date: {today}. Only consider research published in the last 7 days."

    # Initialize LLM with low temperature for factual responses
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1,
        top_p=0.9
    )

    search_tool = TavilySearch(max_results = 5, 
                        topic = "news",
                        time_range = "week",
                        search_depth = "advanced",
                        include_domains = SCIENCE_DOMAINS,
                        tavily_api_key=os.getenv("TAVILY_API_KEY"))


    prompt = f""" 
    You are a research assistant helping to find relevant information and updates for a {profession} who specializes in {specialty}. The current date is {today}. You will search for recent articles and studies from the past week related to this field, and return the top 3 relevant findings.

    Use the tools provided to you each time you search for an article and need to create the report. DO not use anything else other than the tools provided when conducting your research.

    SOURCE REQUIREMENTS:
    - Use only the sources from {SCIENCE_DOMAINS}
    - Never use news articles or non-peer-reviewed content

    RULES:
    1. ALWAYS cite sources with exact publication dates and URLs
    2. NEVER invent or extrapolate beyond the provided data
    3. If no results exist, state this explicitly

    RESPONSE FORMAT:

    === [Short Descriptive Title] ===
    • Source: [Journal Name] ([YYYY-MM-DD])
    • Link: [Full URL]
    • Study Type: [RCT/Meta-analysis/etc.]
    • Key Findings: [6-8 sentences]
    • Impact: [2-3 sentences on clinical relevance]

    If no results:
    === No Recent Findings ===
    • Last query: [attempted query]
    • Date range: Past 7 days
    • Suggested alternative queries: [1-2 suggestions]

    """
    agent = create_react_agent(llm, tools=[search_tool], prompt=prompt)

    return agent
