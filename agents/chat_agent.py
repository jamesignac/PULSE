from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import datetime
from datetime import datetime, timedelta
import os

load_dotenv('.env')

def create_chat_agent(profession: str, specialty: str = None):
    # Define credible healthcare news sources
    HEALTHCARE_DOMAINS = [
        "medscape.com",
        "modernhealthcare.com", 
        "healthaffairs.org",
        "beckershospitalreview.com",
        "theatlantic.com",
        "kffhealthnews.org",
        "healthcaredive.com",
        "statnews.com",
        "bmj.com",
        "medicalnewstoday.com",
        "cdc.gov",
        "who.int",
        "nih.gov",
        "fda.gov",
        "nature.com",
        "thelancet.com",
        "jamanetwork.com",
        "nejm.org",
        "fiercehealthcare.com",
        "biopharmadive.com"
    ]
    
    # Date context
    today = datetime.now().strftime("%Y-%m-%d")
    date_note = f"Current date: {today}. Focus on recent news from the past 7 days when relevant."

    # Initialize LLM with moderate temperature for conversational responses
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
        top_p=0.9
    )

    # Create Tavily search tool for healthcare news
    search_tool = TavilySearch(
        max_results=5, 
        topic="news",
        time_range="week",
        search_depth="advanced",
        include_domains=HEALTHCARE_DOMAINS,
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )

    # Enhanced prompt for conversational agent with search capabilities and memory
    prompt = f"""You are a specialized healthcare AI assistant for {profession}s{f" specializing in {specialty}" if specialty else ""}. {date_note}

    You can help users by:
    1. Answering questions about healthcare topics
    2. Searching for recent news and articles when users ask about current events
    3. Providing context and analysis on healthcare developments
    4. Engaging in back-and-forth conversation about healthcare topics
    5. Remembering previous conversation context to provide more relevant responses

    SEARCH GUIDELINES:
    - Use the search tool when users ask about recent news, current events, or want to learn about specific topics
    - Only search from credible healthcare sources: {', '.join(HEALTHCARE_DOMAINS[:10])}...
    - Always cite your sources with URLs when providing information from searches
    - If no recent news is found, suggest alternative search terms or topics

    CONVERSATION STYLE:
    - Be conversational and engaging
    - Ask follow-up questions to better understand user needs
    - Provide context and explain complex topics clearly
    - Encourage users to explore topics further
    - Reference previous parts of the conversation when relevant
    - Build on topics discussed earlier in the conversation

    RESPONSE FORMAT:
    - For general questions: Provide direct, helpful answers
    - For news searches: Include source citations and URLs
    - For complex topics: Break down information into digestible parts
    - Always be ready to search for more information if the user requests it
    - Use conversation history to provide more personalized and contextual responses

    MEMORY GUIDELINES:
    - Remember what topics have been discussed previously
    - Reference earlier questions or interests when relevant
    - Build upon previous conversations rather than starting fresh each time
    - Maintain context about the user's profession and specialty throughout the conversation

    Remember: You have access to real-time search capabilities and conversation memory. Use them to provide the most helpful and personalized responses possible.
    """

    # Create memory saver for conversation history
    memory = MemorySaver()

    # Create the agent with search capabilities and memory
    agent = create_react_agent(
        llm, 
        tools=[search_tool], 
        prompt=prompt,
        checkpointer=memory
    )
    
    return agent
