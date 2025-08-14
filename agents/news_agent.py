from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv 
import os
import datetime
from datetime import datetime, timedelta

load_dotenv('.env')

def create_news_agent(profession: str, specialty: str = None):
    # Calculate date range (past 7 days)
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    date_range_note = f"Focus ONLY on news published between {week_ago} and {today}. The current date is {today}."

    credible_sources_note = """
    When searching for healthcare news, ONLY retrieve information from these credible, reputable sources 
    and ignore blogs, unverified websites, or social media:

    1. Medscape
    2. Modern Healthcare
    3. Health Affairs
    4. Becker’s Hospital Review
    5. Fierce Healthcare
    6. Kaiser Health News (KFF Health News)
    7. Healthcare Dive
    8. STAT News
    9. The BMJ
    10. Medical News Today
    11. CDC Newsroom
    12. WHO Newsroom
    13. NIH News Releases
    14. FDA News
    15. Nature Medicine
    16. The Lancet
    17. JAMA News
    18. NEJM News
    19. Fierce Pharma
    20. BioPharma Dive

    Always verify that the source of the article matches one of the above before including it in your summary.
    If no relevant news is found from these sources in the past 7 days, clearly state that no recent credible news is available.
    """
    specialty_note = f"Specialty focus: {specialty}" if specialty else ""

    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )
    
    # Initialize tools
    tool = TavilySearchResults(
        api_key=os.getenv("TAVILY_API_KEY"),
        search_type="news",
        max_results=5,
        language="en"
    )
    tools = [tool]
    
    # Proper ReAct prompt template with all required variables
    template = """You are a healthcare news specialist AI assisting {profession}s. {specialty_note}
{date_range_note}

Your task is to find and analyze recent medical news and research, focusing on:
- Clinical relevance
- Practice implications
- Evidence quality

{credible_sources_note}

You have access to these tools:
{tools}

Use this format exactly (do NOT use code blocks or triple backticks):

Question: The healthcare news query to answer
Thought: Consider what information is needed
Action: <tool name from [{tool_names}]>
Action Input: <input for the tool, as a JSON string if needed>
Observation: The tool's result
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have the information needed
Final Answer: Concise summary with key points and sources

Return AT MOST only 3-5 summaries, each no more than 200 words.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
    
    
    prompt = PromptTemplate.from_template(template).partial(
        profession=profession,
        date_range_note=date_range_note,
        credible_sources_note=credible_sources_note,
        specialty_note=specialty_note,
        tools="\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
        tool_names=", ".join([tool.name for tool in tools])
    )
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)