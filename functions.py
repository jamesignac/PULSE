import re
from langchain_core.messages import AIMessage
import streamlit as st


### STREAMLIT HELPER FUNCTIONS ###
def extract_ai_contents(agent_output: dict) -> list[str]:
    """
    Extracts all AIMessage contents from agent output.
    
    Args:
        agent_output (dict): The dictionary containing 'messages'
    
    Returns:
        List[str]: A list of AIMessage contents
    """
    contents = []
    for msg in agent_output.get("messages", []):
        if isinstance(msg, AIMessage):   # when using LangChain objects
            if msg.content:
                contents.append(msg.content)
        elif isinstance(msg, dict):  # in case it's serialized to dicts
            if msg.get("type") == "ai" or "AIMessage" in str(type(msg)):
                if msg.get("content"):
                    contents.append(msg["content"])
    return contents

def display_results(raw_results: list[str]):
    """
    Pretty-print agent results in Streamlit using expanders and formatting.
    Strips leading === and puts each subheader on a new line.
    """
    if not raw_results:
        st.warning("No results found.")
        return

    # Join results into one string and split on "===" headers
    text = "\n".join(raw_results)
    sections = [sec.strip() for sec in text.split("=== ") if sec.strip()]

    for sec in sections:
        # First line is the title, rest is the body
        lines = sec.split("\n")
        title = lines[0].replace("===", "").strip() if lines else "Untitled"
        body = "\n".join(lines[1:]).strip()

        # Put each subheader on a new line with bold + icons
        body = re.sub(r"• Source:", "\n\n**📖 Source:**", body)
        body = re.sub(r"• Link:", "\n\n**🔗 Link:**", body)
        body = re.sub(r"• Study Type:", "\n\n**🧪 Study Type:**", body)
        body = re.sub(r"• Key Findings:", "\n\n**📝 Key Findings:**", body)
        body = re.sub(r"• Impact:", "\n\n**💡 Impact:**", body)

        with st.expander(title, expanded=True):
            st.markdown(body)
