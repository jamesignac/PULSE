from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import datetime
from datetime import datetime, timedelta
import os

load_dotenv('.env')

def create_chat_agent(profession: str, specialty: str = None):
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
    # Enhanced prompt template with proper variable handling
    template = """You are a specialized healthcare AI assistant for {profession}s. {specialty_note}. {date_range_note} 
    
    {credible_sources_note}

    Your task is to assist users by providing accurate, relevant information based on their queries about healthcare news and its implications related to their profession.
    
    Current conversation:
    {history}
    Human: {input}
    AI Assistant:"""
    
    specialty_note = f"Specialty: {specialty}" if specialty else ""
    
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=template
    ).partial(
        profession=profession,
        specialty_note=specialty_note, 
        date_range_note=date_range_note,
        credible_sources_note=credible_sources_note
    )
    
    # Configure Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5,
    )
    
    memory = ConversationBufferMemory()
    return ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )